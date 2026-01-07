import logging
import datetime
from .config import config

logger = logging.getLogger(__name__)

class InfluxWriter:
    def __init__(self):
        self.conf = config.get("influx")
        self.version = self.conf.get("version", 2)
        self.client = None
        self.setup()

    def setup(self):
        try:
            if self.version == 2:
                from influxdb_client import InfluxDBClient
                from influxdb_client.client.write_api import SYNCHRONOUS

                self.client = InfluxDBClient(
                    url=self.conf["url"],
                    token=self.conf["token"],
                    org=self.conf["org"]
                )
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                self.bucket = self.conf["bucket"]

            elif self.version == 1:
                from influxdb import InfluxDBClient
                self.client = InfluxDBClient(
                    host=self.conf["host"],
                    port=self.conf.get("port", 8086),
                    username=self.conf["username"],
                    password=self.conf["password"],
                    database=self.conf["database"]
                )
                if "host" not in self.conf and "url" in self.conf:
                     from urllib.parse import urlparse
                     u = urlparse(self.conf["url"])
                     self.client = InfluxDBClient(
                        host=u.hostname,
                        port=u.port if u.port else 8086,
                        username=self.conf["username"],
                        password=self.conf["password"],
                        database=self.conf["database"]
                     )

        except ImportError as e:
            logger.error(f"InfluxDB library not installed for version {self.version}: {e}")
        except Exception as e:
            logger.error(f"Failed to setup InfluxDB client: {e}")

    def write(self, measurements):
        if not self.client:
            return

        try:
            if self.version == 2:
                from influxdb_client import Point

                # Optimized: One point with many fields
                timestamp = datetime.datetime.utcnow()
                p = Point("idm_heatpump").time(timestamp)

                has_fields = False
                for key, value in measurements.items():
                    if key.endswith("_str"):
                        continue
                    if isinstance(value, bool):
                        value = int(value)

                    if isinstance(value, (int, float)):
                        p.field(key, value)
                        has_fields = True

                if has_fields:
                    self.write_api.write(bucket=self.bucket, record=p)

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

        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")
