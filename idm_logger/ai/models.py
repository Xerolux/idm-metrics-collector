from abc import ABC, abstractmethod
import collections
import logging
import time
import numpy as np
from typing import Dict, Any
try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class BaseAnomalyModel(ABC):
    """Abstract base class for anomaly detection strategies."""

    @abstractmethod
    def update(self, data: Dict[str, float]):
        """Update model with new data point."""
        pass

    @abstractmethod
    def detect(self, data: Dict[str, float], sensitivity: float) -> Dict[str, Any]:
        """Detect anomalies in the current data point."""
        pass

    @abstractmethod
    def save_state(self) -> Dict[str, Any]:
        """Return state for persistence."""
        pass

    @abstractmethod
    def load_state(self, state: Dict[str, Any]):
        """Load state from persistence."""
        pass


class RollingWindowStats(BaseAnomalyModel):
    """
    Detects anomalies using a rolling window of Z-Scores.
    Adapts to changes over time by only keeping recent history.
    """
    def __init__(self, window_size: int = 2000):
        self.window_size = window_size
        self.history: Dict[str, collections.deque] = {}
        # We cache stats to avoid recomputing mean/std on every read if needed,
        # but for accuracy on every step, we recompute or use Welford's if we wanted pure streaming.
        # With deque and numpy, recomputing on window is fast enough for 2000 points.

    def get_stats(self) -> Dict[str, Any]:
        return {
            "model_type": "RollingWindow",
            "sensors_monitored": len(self.history),
            "data_points_total": sum(len(h) for h in self.history.values()),
            "window_size": self.window_size
        }

    def update(self, data: Dict[str, float]):
        for sensor, value in data.items():
            if sensor not in self.history:
                self.history[sensor] = collections.deque(maxlen=self.window_size)
            self.history[sensor].append(value)

    def detect(self, data: Dict[str, float], sensitivity: float) -> Dict[str, Any]:
        anomalies = {}
        for sensor, value in data.items():
            if sensor not in self.history:
                continue

            history = self.history[sensor]
            if len(history) < 20: # Minimum samples
                continue

            # Calculate stats on current window
            # Using numpy for speed
            vals = np.array(history)
            mean = np.mean(vals)
            std = np.std(vals)

            if std == 0:
                continue

            z_score = (value - mean) / std

            if abs(z_score) > sensitivity:
                anomalies[sensor] = {
                    "value": value,
                    "mean": float(mean),
                    "std_dev": float(std),
                    "z_score": float(z_score),
                    "model": "RollingWindow"
                }
        return anomalies

    def save_state(self) -> Dict[str, Any]:
        # Convert deques to lists for JSON serialization
        return {k: list(v) for k, v in self.history.items()}

    def load_state(self, state: Dict[str, Any]):
        self.history = {}
        for k, v in state.items():
            self.history[k] = collections.deque(v, maxlen=self.window_size)


class IsolationForestModel(BaseAnomalyModel):
    """
    Uses Scikit-Learn Isolation Forest for anomaly detection.
    Requires batch training.
    """
    def __init__(self, buffer_size: int = 5000):
        if not SKLEARN_AVAILABLE:
            logger.error("Scikit-learn not available. IsolationForestModel will fail.")

        self.buffer_size = buffer_size
        self.history: Dict[str, collections.deque] = {}
        self.models: Dict[str, Any] = {} # sensor -> trained model
        self.last_train_time = 0
        self.needs_retraining = False
        self.training_count = 0

    def update(self, data: Dict[str, float]):
        for sensor, value in data.items():
            if sensor not in self.history:
                self.history[sensor] = collections.deque(maxlen=self.buffer_size)
            self.history[sensor].append(value)

        # Trigger retraining periodically?
        # For simplicity, we train on first detection or if we have enough new data.
        # In a real app, we might do this in a background thread.
        # Here we just flag it, or train on the fly if model doesn't exist.

    def _train(self, sensor: str):
        if not SKLEARN_AVAILABLE:
            return

        data = np.array(self.history[sensor]).reshape(-1, 1)
        if len(data) < 50: # Need reasonable amount of data
            return

        logger.info(f"Training Isolation Forest for sensor '{sensor}' with {len(data)} points...")
        self.last_train_time = time.time()

        clf = IsolationForest(contamination=0.01, random_state=42)
        clf.fit(data)
        self.models[sensor] = clf
        self.training_count += 1
        logger.info(f"Training complete for {sensor}.")

    def detect(self, data: Dict[str, float], sensitivity: float) -> Dict[str, Any]:
        """
        Sensitivity in IsolationForest is somewhat fixed by contamination parameter during training,
        but we can look at decision_function scores.
        """
        if not SKLEARN_AVAILABLE:
            return {}

        anomalies = {}
        for sensor, value in data.items():
            # Ensure we have a model
            if sensor not in self.models:
                self._train(sensor)

            if sensor not in self.models:
                continue # Training failed or not enough data

            clf = self.models[sensor]

            # Predict returns -1 for anomaly, 1 for normal
            # We want to use the score to handle sensitivity manually if possible,
            # but standard usage is predict.
            # score_samples returns anomaly score. Lower = more abnormal.

            x = np.array([[value]])
            score = clf.decision_function(x)[0]

            # Configurable threshold is tricky with IF.
            # Usually score < 0 is anomaly.
            # We can scale "sensitivity" to shift the threshold.
            # E.g. sensitivity 3.0 (high) -> strictly < -0.1
            # sensitivity 1.0 (low) -> < 0

            # Let's map sensitivity 1-10 to a threshold adjustment.
            # Default 0.
            threshold = 0.0

            if score < threshold:
                 # Calculate stats for the message (mean/std of history) for context
                 vals = np.array(self.history[sensor])
                 mean = np.mean(vals)

                 anomalies[sensor] = {
                    "value": value,
                    "mean": float(mean), # Context only
                    "z_score": float(score), # Using score as proxy for severity
                    "model": "IsolationForest"
                }

        return anomalies

    def save_state(self) -> Dict[str, Any]:
        # We only save the history to retrain on reload.
        # Pickling models is unsafe/heavy for this simple JSON store.
        return {k: list(v) for k, v in self.history.items()}

    def load_state(self, state: Dict[str, Any]):
        self.history = {}
        for k, v in state.items():
            self.history[k] = collections.deque(v, maxlen=self.buffer_size)
        # Models will be retrained on first detect

    def get_stats(self) -> Dict[str, Any]:
        """Return statistics about the model."""
        stats = {
            "model_type": "IsolationForest",
            "sensors_monitored": len(self.history),
            "models_trained": len(self.models),
            "data_points_total": sum(len(h) for h in self.history.values()),
            "last_train_time": self.last_train_time,
            "last_train_relative": f"{int(time.time() - self.last_train_time)}s ago" if self.last_train_time > 0 else "never",
            "training_count": self.training_count
        }
        return stats
