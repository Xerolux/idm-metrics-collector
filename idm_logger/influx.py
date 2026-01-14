import logging
import datetime
import time
import os
from .config import config

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds, exponential backoff


class InfluxWriter:
    def __init__(self):
        self.conf = config.get("influx")
        self.client = None
        self._connected = False
        self._last_error = None
        self._setup_with_retry()

    def _setup_with_retry(self):
        """Setup InfluxDB connection with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                self._setup()
                if self._connected:
                    logger.info("InfluxDB v3 connected successfully")
                    return
            except Exception as e:
                self._last_error = str(e)

                # Auto-Recovery for 401 Unauthorized
                if "401" in str(e) or "unauthorized" in str(e).lower():
                    logger.warning("InfluxDB authentication failed (401). Checking for environment token...")
                    # Check all supported variable names, prioritizing the standard v3 token
                    env_token = (
                        os.environ.get("INFLUXDB3_AUTH_TOKEN") or
                        os.environ.get("INFLUX_TOKEN") or
                        os.environ.get("INFLUXDB_TOKEN")
                    )

                    if env_token:
                        current_token = self.conf.get("token")
                        if env_token != current_token:
                            logger.info("Found different token in environment, updating configuration...")
                            # Update config object in memory
                            self.conf["token"] = env_token
                            # Update persistent storage via config object
                            config.data["influx"]["token"] = env_token
                            config.save()
                        else:
                            logger.warning("Environment token matches current token. Token might be invalid.")
                    else:
                        logger.warning("No token found in environment variables.")

                delay = RETRY_DELAY_BASE ** (attempt + 1)
                logger.warning(
                    f"InfluxDB connection attempt {attempt + 1}/{MAX_RETRIES} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(delay)

        logger.error(f"Failed to connect to InfluxDB after {MAX_RETRIES} attempts")

    def _setup(self):
        """Initialize InfluxDB v3 client."""
        self._connected = False

        from influxdb_client_3 import InfluxDBClient3

        host = self.conf.get("url", "http://localhost:8181")
        token = self.conf.get("token", "")
        database = self.conf.get("database", "idm")

        if not token:
            logger.warning("InfluxDB token not configured")
            return

        try:
            flight_client_options = {
                "disable_server_verification": True,
                "tls_root_certs": None
            }

            self.client = InfluxDBClient3(
                host=host,  # Pass full URL with http:// scheme
                token=token,
                database=database,
                org="",  # InfluxDB v3 doesn't use org
                write_client_options={"disable_tls": True},
                flight_client_options=flight_client_options
            )

            # Test connection by attempting a simple query
            try:
                # Try to query the database to verify connection
                self.client.query("SELECT * FROM idm_heatpump LIMIT 1")
                self._connected = True
            except Exception as e:
                # If query fails due to no data/empty table, that's ok - connection works
                error_str = str(e).lower()
                if "no such table" in error_str or "not found" in error_str or "list index out of range" in error_str:
                    self._connected = True
                else:
                    raise

        except Exception as e:
            raise ConnectionError(f"InfluxDB v3 connection failed: {e}")

    def is_connected(self) -> bool:
        """Return current connection status."""
        return self._connected

    def get_status(self) -> dict:
        """Get detailed status information."""
        return {
            "connected": self._connected,
            "version": 3,
            "url": self.conf.get("url", ""),
            "database": self.conf.get("database", ""),
            "last_error": self._last_error
        }

    def reconnect(self):
        """Attempt to reconnect to InfluxDB."""
        logger.info("Attempting to reconnect to InfluxDB...")
        self._close()
        self._setup_with_retry()

    def _close(self):
        """Close existing connection."""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                # Ignore errors during cleanup, but log for debugging
                logger.debug(f"Error closing InfluxDB connection (non-critical): {e}")
        self.client = None
        self._connected = False

    def write(self, measurements: dict) -> bool:
        """Write measurements to InfluxDB v3 with error handling and retry."""
        if not measurements:
            return True

        if not self.client:
            # Try to reconnect if not connected
            if not self._connected:
                self.reconnect()
            if not self.client:
                return False

        for attempt in range(MAX_RETRIES):
            try:
                success = self._write_internal(measurements)
                if success:
                    return True
            except Exception as e:
                self._last_error = str(e)
                delay = RETRY_DELAY_BASE ** attempt
                logger.warning(
                    f"InfluxDB write attempt {attempt + 1}/{MAX_RETRIES} failed: {e}"
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(delay)
                else:
                    logger.error(f"InfluxDB write failed after {MAX_RETRIES} attempts")
                    self._connected = False

        return False

    def _write_internal(self, measurements: dict) -> bool:
        """Internal write method without retry logic."""
        from influxdb_client_3 import Point

        timestamp = datetime.datetime.utcnow()
        p = Point("idm_heatpump").time(timestamp)

        has_fields = False
        for key, value in measurements.items():
            # Skip string representation fields
            if key.endswith("_str"):
                continue
            # Convert booleans to int
            if isinstance(value, bool):
                value = int(value)
            # Only write numeric values
            if isinstance(value, (int, float)):
                p.field(key, value)
                has_fields = True

        if has_fields:
            self.client.write(record=p)
            return True
        return False

    def query(self, sql_query: str) -> list:
        """Execute a SQL query (InfluxDB v3)."""
        if not self.client:
            logger.warning("InfluxDB client not connected")
            return []

        try:
            # Query returns a pyarrow Table
            table = self.client.query(query=sql_query)
            # Convert to list of dicts
            results = []
            if table:
                df = table.to_pandas()
                results = df.to_dict('records')
            return results
        except Exception as e:
            logger.error(f"InfluxDB query failed: {e}")
            return []

    def delete_all_data(self) -> bool:
        """Delete all data from the database."""
        try:
            if not self.client:
                return False

            # InfluxDB v3 uses SQL for deletes
            sql = "DELETE FROM idm_heatpump"
            self.client.query(sql)
            logger.info("Deleted all data (v3)")
            return True

        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            return False

        return False

    def __del__(self):
        """Cleanup on destruction."""
        self._close()
