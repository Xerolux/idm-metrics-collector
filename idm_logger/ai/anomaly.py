import json
import logging
import os
import threading
import requests
from urllib.parse import urlparse, urlunparse, urljoin
from typing import Dict, Any

from ..config import DATA_DIR, config
from .models import RollingWindowStats, IsolationForestModel

logger = logging.getLogger(__name__)

ANOMALY_STATE_FILE = os.path.join(DATA_DIR, "anomaly_state.json")
DEFAULT_MEASUREMENT = "idm_heatpump"

class AnomalyDetector:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_model_type = "rolling"
        self.models = {
            "rolling": RollingWindowStats(window_size=20160), # Approx 14 days at 1 min interval
            "isolation_forest": IsolationForestModel(buffer_size=5000)
        }
        self.load()

    def set_model_type(self, model_type: str):
        """Switch the active model strategy."""
        with self.lock:
            if model_type not in self.models:
                logger.warning(f"Unknown model type '{model_type}', using 'rolling'")
                model_type = "rolling"

            if model_type != self.current_model_type:
                logger.info(f"Switching anomaly detection model to: {model_type}")
                self.current_model_type = model_type

    def load(self):
        """Load learned state from disk or fetch from DB if missing."""
        loaded_from_file = False
        with self.lock:
            if os.path.exists(ANOMALY_STATE_FILE):
                try:
                    with open(ANOMALY_STATE_FILE, "r") as f:
                        data = json.load(f)

                    # Load state for all models found in file
                    if "models" in data:
                         for m_name, m_state in data["models"].items():
                             if m_name in self.models:
                                 self.models[m_name].load_state(m_state)

                    # Backwards compatibility with old simple file format
                    # If "models" key missing, it might be the old Welford state.
                    # We largely discard it or could try to migrate, but easier to restart learning.
                    if "models" not in data and data:
                        logger.info("Old anomaly state format detected. Starting fresh.")

                    logger.info("Loaded anomaly detection state.")
                    loaded_from_file = True
                except Exception as e:
                    logger.error(f"Failed to load anomaly detection state: {e}")

        # If we didn't load from file (or it was empty/corrupt), try fetching from DB
        # We do this outside the lock to avoid blocking too long, but update() locks internally
        if not loaded_from_file:
            logger.info("No anomaly state found on disk. Attempting to fetch history from database...")
            if self.fetch_history_from_db():
                self.save()

    def save(self):
        """Save learned state to disk."""
        with self.lock:
            try:
                state = {
                    "models": {
                        name: model.save_state()
                        for name, model in self.models.items()
                    }
                }
                with open(ANOMALY_STATE_FILE, "w") as f:
                    json.dump(state, f)
            except Exception as e:
                logger.error(f"Failed to save anomaly detection state: {e}")

    def fetch_history_from_db(self) -> bool:
        """
        Fetches historical data from VictoriaMetrics/InfluxDB to pre-fill the models.
        Returns True if successful and data was added.
        """
        metrics_url = config.get("metrics.url", "http://victoriametrics:8428/write")

        # Robustly construct query URL
        try:
            parsed = urlparse(metrics_url)
            # Replace path ending in /write with /query or just use /query if path is empty/different
            # VictoriaMetrics/Influx v1 API uses /query on the same port/host
            # If the user put a path like /api/v1/write, we want /api/v1/query?
            # Standard VM is just /write and /query.

            # Use rstrip to remove trailing slash from path for consistent handling
            path = parsed.path.rstrip("/")
            if path.endswith("/write"):
                path = path[:-6] + "/query"
            else:
                 # Fallback: assuming the user provided the base URL or the write endpoint
                 # If they provided http://vm:8428, we want http://vm:8428/query
                 # If they provided http://vm:8428/foo, maybe http://vm:8428/foo/query?
                 # Let's assume standard behavior: replace last segment or append.
                 path = path + "/query"

            query_url = urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))

        except Exception as e:
            logger.error(f"Failed to parse metrics URL '{metrics_url}': {e}")
            return False

        measurement = config.get("metrics.measurement", DEFAULT_MEASUREMENT)
        db_name = config.get("metrics.db", "prometheus")

        # Query: Get last 25000 points. We order by time DESC to get the NEWEST,
        # but we need to feed them in chronological order (ASC), so we'll reverse in python.
        query = f"SELECT * FROM {measurement} ORDER BY time DESC LIMIT 25000"

        try:
            logger.info(f"Querying history from {query_url}...")
            response = requests.get(query_url, params={"q": query, "db": db_name}, timeout=30)

            if response.status_code != 200:
                logger.warning(f"Failed to fetch history: {response.status_code} {response.text}")
                return False

            data = response.json()

            # Parse InfluxDB 1.x JSON response format
            # { "results": [ { "series": [ { "name": "...", "columns": [...], "values": [...] } ] } ] }

            if "results" not in data or not data["results"]:
                logger.info("No history data found in DB.")
                return False

            result = data["results"][0]
            if "series" not in result or not result["series"]:
                logger.info("No series found in history data.")
                return False

            series = result["series"][0]
            columns = series.get("columns", [])
            values = series.get("values", [])

            if not values:
                logger.info("Empty values in history data.")
                return False

            # Reverse to process from oldest to newest
            values.reverse()

            logger.info(f"Processing {len(values)} historical data points...")

            count = 0
            # Map column names to indices
            col_map = {name: i for i, name in enumerate(columns)}

            # Batch update to reduce locking overhead?
            # Current update() takes a single dict.
            # We will just loop. It's 25000 ops, should be fast enough in memory (seconds).

            for row in values:
                point_data = {}
                for col_name, idx in col_map.items():
                    if col_name == "time":
                        continue
                    val = row[idx]
                    if val is not None:
                         point_data[col_name] = val

                if point_data:
                    self.update(point_data)
                    count += 1

            logger.info(f"Successfully loaded {count} historical data points.")
            return True

        except Exception as e:
            logger.error(f"Error fetching history from DB: {e}")
            return False

    def update(self, data: Dict[str, Any]):
        """
        Update the model with new data.
        We update ALL models regardless of which one is active,
        so switching doesn't lose history.
        """
        with self.lock:
            numeric_data = {}
            for sensor, value in data.items():
                try:
                    numeric_data[sensor] = float(value)
                except (ValueError, TypeError):
                    continue

            for model in self.models.values():
                model.update(numeric_data)

    def detect(self, data: Dict[str, Any], sigma: float = 3.0) -> Dict[str, Any]:
        """
        Detect anomalies using the currently active model.
        """
        with self.lock:
            numeric_data = {}
            for sensor, value in data.items():
                try:
                    numeric_data[sensor] = float(value)
                except (ValueError, TypeError):
                    continue

            model = self.models[self.current_model_type]
            return model.detect(numeric_data, sigma)

    def get_stats(self):
        """Return current statistics for debugging/UI."""
        with self.lock:
            if self.current_model_type in self.models:
                return self.models[self.current_model_type].get_stats()
            return {"error": "No model active"}


anomaly_detector = AnomalyDetector()
