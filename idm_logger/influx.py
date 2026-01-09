import logging
import datetime
import time
from .config import config

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds, exponential backoff


class InfluxWriter:
    def __init__(self):
        self.conf = config.get("influx")
        self.version = self.conf.get("version", 2)
        self.client = None
        self.write_api = None
        self.bucket = None
        self._connected = False
        self._last_error = None
        self._setup_with_retry()

    def _setup_with_retry(self):
        """Setup InfluxDB connection with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                self._setup()
                if self._connected:
                    logger.info(f"InfluxDB v{self.version} connected successfully")
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
        """Initialize InfluxDB client."""
        self._connected = False

        if self.version == 2:
            from influxdb_client import InfluxDBClient
            from influxdb_client.client.write_api import SYNCHRONOUS

            url = self.conf.get("url", "http://localhost:8086")
            token = self.conf.get("token", "")
            org = self.conf.get("org", "")

            if not token:
                logger.warning("InfluxDB token not configured")
                return

            self.client = InfluxDBClient(
                url=url,
                token=token,
                org=org,
                timeout=10000  # 10 second timeout
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.bucket = self.conf.get("bucket", "idm")

            # Verify connection with health check
            if self._health_check():
                self._connected = True

        elif self.version == 1:
            from influxdb import InfluxDBClient as InfluxDBClientV1
            from urllib.parse import urlparse

            # Parse URL if host not directly provided
            if "host" in self.conf:
                host = self.conf["host"]
                port = self.conf.get("port", 8086)
            elif "url" in self.conf:
                u = urlparse(self.conf["url"])
                host = u.hostname
                port = u.port if u.port else 8086
            else:
                host = "localhost"
                port = 8086

            self.client = InfluxDBClientV1(
                host=host,
                port=port,
                username=self.conf.get("username", ""),
                password=self.conf.get("password", ""),
                database=self.conf.get("database", "idm"),
                timeout=10
            )

            # Verify connection
            try:
                self.client.ping()
                self._connected = True
            except Exception as e:
                raise ConnectionError(f"InfluxDB v1 ping failed: {e}")

    def _health_check(self) -> bool:
        """Check InfluxDB v2 health status."""
        if not self.client:
            return False

        try:
            health = self.client.health()
            if health.status == "pass":
                return True
            else:
                logger.warning(f"InfluxDB health check: {health.status} - {health.message}")
                return False
        except Exception as e:
            logger.warning(f"InfluxDB health check failed: {e}")
            return False

    def is_connected(self) -> bool:
        """Return current connection status."""
        return self._connected

    def get_status(self) -> dict:
        """Get detailed status information."""
        return {
            "connected": self._connected,
            "version": self.version,
            "url": self.conf.get("url", ""),
            "bucket": self.conf.get("bucket", "") if self.version == 2 else self.conf.get("database", ""),
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
                if self.version == 2 and self.write_api:
                    self.write_api.close()
                self.client.close()
            except Exception:
                pass
        self.client = None
        self.write_api = None
        self._connected = False

    def write(self, measurements: dict) -> bool:
        """Write measurements to InfluxDB with error handling and retry."""
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
        if self.version == 2:
            from influxdb_client import Point

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
                self.write_api.write(bucket=self.bucket, record=p)
                return True
            return False

        elif self.version == 1:
            timestamp = datetime.datetime.utcnow().isoformat() + "Z"

            fields = {}
            for key, value in measurements.items():
                if key.endswith("_str"):
                    continue
                if isinstance(value, bool):
                    value = int(value)
                if isinstance(value, (int, float)):
                    fields[key] = value

            if fields:
                json_body = [{
                    "measurement": "idm_heatpump",
                    "time": timestamp,
                    "fields": fields
                }]
                self.client.write_points(json_body)
                return True
            return False

        return False

    def query(self, flux_query: str) -> list:
        """Execute a Flux query (InfluxDB v2 only)."""
        if self.version != 2 or not self.client:
            logger.warning("Query only supported for InfluxDB v2")
            return []

        try:
            query_api = self.client.query_api()
            tables = query_api.query(flux_query)
            results = []
            for table in tables:
                for record in table.records:
                    results.append(record.values)
            return results
        except Exception as e:
            logger.error(f"InfluxDB query failed: {e}")
            return []

    def __del__(self):
        """Cleanup on destruction."""
        self._close()
