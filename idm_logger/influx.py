import logging
import datetime
import time
from .config import config

# Import at top level as it is a core dependency now
try:
    from influxdb_client_3 import InfluxDBClient3, Point, WriteOptions
except ImportError:
    # Fallback/logging if not installed, though it should be
    InfluxDBClient3 = None
    Point = None
    WriteOptions = None

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds, exponential backoff


class InfluxWriter:
    def __init__(self):
        self.conf = config.get("influx")
        self.client = None
        self.bucket = None
        self._connected = False
        self._last_error = None
        self._setup_with_retry()

    def _setup_with_retry(self):
        """Setup InfluxDB connection with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                self._setup()
                # InfluxDB 3 client doesn't explicitly connect until first request,
                # but we assume success if no exception during init.
                # We can try a dummy query or health check if API allows.
                self._connected = True
                logger.info(f"InfluxDB 3 client initialized")
                return
            except Exception as e:
                self._last_error = str(e)
                delay = RETRY_DELAY_BASE ** (attempt + 1)
                logger.warning(
                    f"InfluxDB connection attempt {attempt + 1}/{MAX_RETRIES} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(delay)

        logger.error(f"Failed to connect to InfluxDB after {MAX_RETRIES} attempts")

    def _setup(self):
        """Initialize InfluxDB 3 client."""
        self._connected = False

        if InfluxDBClient3 is None:
            raise ImportError("influxdb3-python not installed")

        # User's v3 Core configuration uses port 8181
        url = self.conf.get("url", "http://localhost:8181")
        token = self.conf.get("token", "")
        org = self.conf.get("org", "")
        bucket = self.conf.get("bucket", "idm")

        if not token and not url: # Minimal check
             pass

        # InfluxDB 3 client expects full URL with protocol
        # The influxdb3-python library uses 'host' parameter for the full URL
        self.bucket = bucket
        self.client = InfluxDBClient3(
            host=url,
            token=token,
            org=org,
            database=bucket
        )

    def is_connected(self) -> bool:
        """Return current connection status."""
        return self._connected

    def get_status(self) -> dict:
        """Get detailed status information."""
        return {
            "connected": self._connected,
            "version": 3,
            "url": self.conf.get("url", ""),
            "bucket": self.conf.get("bucket", ""),
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
            except Exception:
                pass
        self.client = None
        self._connected = False

    def write(self, measurements: dict) -> bool:
        """Write measurements to InfluxDB with error handling and retry."""
        if not measurements:
            return True

        if not self.client:
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
                    # Don't mark disconnected immediately on write failure for v3 as it might be transient
                    # But if persistent, maybe?
                    # For now, keep connected state unless re-init needed.

        return False

    def _write_internal(self, measurements: dict) -> bool:
        """Internal write method using InfluxDB 3 Line Protocol or Point."""
        if Point is None:
             return False

        # Create a point
        # Measurement name matches what we used in v2: "idm_heatpump"
        p = Point("idm_heatpump")

        # Add timestamp in nanoseconds for InfluxDB 3
        import time as time_module
        p = p.time(int(time_module.time() * 1e9))

        has_fields = False
        for key, value in measurements.items():
            # Skip string representation fields
            if key.endswith("_str"):
                continue
            # Convert booleans to int
            if isinstance(value, bool):
                value = int(value)
            # Only write numeric values as fields
            if isinstance(value, (int, float)):
                p = p.field(key, value)
                has_fields = True

        if has_fields:
            # write() method accepts Point objects or line protocol strings
            # database parameter is already set during client initialization
            self.client.write(record=p, database=self.bucket)
            return True

        return False

    def query(self, query: str, language: str = "sql") -> list:
        """Execute a query (default SQL). Returns list of dicts or values."""
        if not self.client:
            return []

        try:
            # query() returns a PyArrow Table (default) or Pandas DataFrame
            # We want simple list of dicts for compatibility with app usage if any.
            # But wait, app doesn't use query() results except maybe for debugging?
            # Actually, nothing uses query() return value in the python code we grepped.
            # But let's implement it to return list of rows (dicts) just in case.

            table = self.client.query(query=query, language=language)
            # Convert PyArrow table to list of dicts
            return table.to_pylist()
        except Exception as e:
            logger.error(f"InfluxDB query failed: {e}")
            return []

    def delete_all_data(self) -> bool:
        """Delete all data from the database (bucket)."""
        if not self.client:
            return False

        try:
            # InfluxDB 3 (IOx) supports standard SQL.
            # "DROP TABLE idm_heatpump" is the standard way to clear a measurement.
            self.client.query(query="DROP TABLE idm_heatpump", language="sql")
            logger.info("Deleted all data (DROP TABLE idm_heatpump)")
            return True
        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            return False

    def __del__(self):
        """Cleanup on destruction."""
        self._close()
