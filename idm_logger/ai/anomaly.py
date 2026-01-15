import json
import logging
import os
import threading
from typing import Dict, Any

from ..config import DATA_DIR
from .models import RollingWindowStats, IsolationForestModel

logger = logging.getLogger(__name__)

ANOMALY_STATE_FILE = os.path.join(DATA_DIR, "anomaly_state.json")


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
        """Load learned state from disk."""
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
                except Exception as e:
                    logger.error(f"Failed to load anomaly detection state: {e}")

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
        # This is model dependent, for now just return empty or summary
        return {}


anomaly_detector = AnomalyDetector()
