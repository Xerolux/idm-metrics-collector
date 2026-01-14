import logging
import requests
import os
from .config import config

logger = logging.getLogger(__name__)

class MetricsWriter:
    def __init__(self):
        self.url = os.environ.get("METRICS_URL", config.get("metrics.url", "http://victoriametrics:8428/write"))
        self._connected = True # HTTP is stateless
        self.session = requests.Session()
        logger.info(f"MetricsWriter initialized with URL: {self.url}")

    def is_connected(self) -> bool:
        return self._connected

    def write(self, measurements: dict) -> bool:
        if not measurements:
            return True

        # Construct Influx Line Protocol
        # measurement field1=val1,field2=val2
        # We omit timestamp to let VictoriaMetrics assign the current server time

        measurement = "idm_heatpump"
        fields = []

        for key, value in measurements.items():
            # Skip string representation fields
            if key.endswith("_str"):
                continue
            # Convert booleans to int
            if isinstance(value, bool):
                value = int(value)
            # Only write numeric values
            if isinstance(value, (int, float)):
                fields.append(f"{key}={value}")

        if not fields:
            return False

        field_str = ",".join(fields)
        line = f"{measurement} {field_str}"

        try:
            # VictoriaMetrics /write endpoint
            # Use session for connection pooling
            response = self.session.post(self.url, data=line, timeout=5)
            if response.status_code in (200, 204):
                return True
            else:
                logger.error(f"Failed to write metrics: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception writing metrics: {e}")
            return False

    def get_status(self) -> dict:
        return {
            "connected": self._connected,
            "type": "VictoriaMetrics",
            "url": self.url
        }
