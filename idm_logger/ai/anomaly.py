import json
import logging
import math
import os
import threading
from typing import Dict, Any

from ..config import DATA_DIR

logger = logging.getLogger(__name__)

ANOMALY_STATE_FILE = os.path.join(DATA_DIR, "anomaly_state.json")


class AnomalyDetector:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {}  # {sensor_name: {n, mean, m2}}
        self.load()

    def load(self):
        """Load learned state from disk."""
        with self.lock:
            if os.path.exists(ANOMALY_STATE_FILE):
                try:
                    with open(ANOMALY_STATE_FILE, "r") as f:
                        self.state = json.load(f)
                    logger.info(
                        f"Loaded anomaly detection model for {len(self.state)} sensors"
                    )
                except Exception as e:
                    logger.error(f"Failed to load anomaly detection state: {e}")
                    self.state = {}

    def save(self):
        """Save learned state to disk."""
        with self.lock:
            try:
                with open(ANOMALY_STATE_FILE, "w") as f:
                    json.dump(self.state, f)
            except Exception as e:
                logger.error(f"Failed to save anomaly detection state: {e}")

    def update(self, data: Dict[str, Any]):
        """
        Update the model with new data (Online Learning).
        Uses Welford's algorithm for running mean and variance.
        """
        with self.lock:
            updated = False
            for sensor, value in data.items():
                # Only learn from numeric values
                try:
                    x = float(value)
                except (ValueError, TypeError):
                    continue

                if sensor not in self.state:
                    self.state[sensor] = {"n": 0, "mean": 0.0, "m2": 0.0}

                stats = self.state[sensor]
                stats["n"] += 1

                # Welford's algorithm
                delta = x - stats["mean"]
                stats["mean"] += delta / stats["n"]
                delta2 = x - stats["mean"]
                stats["m2"] += delta * delta2

                updated = True

            # if updated and stats["n"] % 10 == 0:  # Save periodically (every 10 updates per sensor roughly)
            #    pass # Don't save every update, maybe handle in main loop or shutdown

    def detect(self, data: Dict[str, Any], sigma: float = 3.0) -> Dict[str, Any]:
        """
        Detect anomalies in current data based on learned model.
        Returns a dict of {sensor: {value, mean, std_dev, z_score}} for anomalies.
        """
        anomalies = {}
        with self.lock:
            for sensor, value in data.items():
                if sensor not in self.state:
                    continue

                stats = self.state[sensor]
                if (
                    stats["n"] < 10
                ):  # Need minimum samples to be statistically significant
                    continue

                try:
                    x = float(value)
                except (ValueError, TypeError):
                    continue

                variance = stats["m2"] / (stats["n"] - 1) if stats["n"] > 1 else 0
                std_dev = math.sqrt(variance)

                if std_dev == 0:
                    continue

                z_score = (x - stats["mean"]) / std_dev

                if abs(z_score) > sigma:
                    anomalies[sensor] = {
                        "value": x,
                        "mean": stats["mean"],
                        "std_dev": std_dev,
                        "z_score": z_score,
                    }
        return anomalies

    def get_stats(self):
        """Return current statistics for debugging/UI."""
        with self.lock:
            return self.state.copy()


anomaly_detector = AnomalyDetector()
