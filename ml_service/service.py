import logging
import os
import pickle
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from .config import config
from .models import AutoencoderModel, create_model

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ml-service")

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from idm_logger.sensor_addresses import (
        COMMON_SENSORS,
        BINARY_SENSOR_ADDRESSES,
        HeatingCircuit,
        heating_circuit_sensors,
        zone_sensors,
    )
    from idm_logger.const import HeatPumpStatus
except ImportError:
    logger.warning("Could not import idm_logger modules, using defaults")
    COMMON_SENSORS = []
    BINARY_SENSOR_ADDRESSES = {}
    HeatPumpStatus = None
    HeatingCircuit = None

    def heating_circuit_sensors(x):
        return []

    def zone_sensors(x):
        return []


@dataclass
class ConnectionState:
    metrics_connected: bool = False
    metrics_last_success: Optional[float] = None
    metrics_consecutive_failures: int = 0
    alert_last_success: Optional[float] = None
    alert_consecutive_failures: int = 0
    total_fetch_errors: int = 0
    total_write_errors: int = 0
    total_alert_errors: int = 0


@dataclass
class ServiceState:
    start_time: float = field(default_factory=time.time)
    last_score: float = 0.0
    model_trained: bool = False
    last_alert_time: float = 0.0
    update_counter: int = 0
    last_model_save: float = field(default_factory=time.time)
    current_mode: str = "unknown"
    last_mode: str = "unknown"
    last_data_points: Dict[str, float] = field(default_factory=dict)
    consecutive_anomalies: Dict[str, int] = field(default_factory=dict)
    connection: ConnectionState = field(default_factory=ConnectionState)


class MLService:
    def __init__(self):
        self.config = config
        self.state = ServiceState()
        self.models: Dict[str, AutoencoderModel] = {}
        self.model_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._initialize_models()
        self._initialize_sensors()

    def _initialize_models(self) -> None:
        for mode in self.config.modes:
            self.models[mode] = create_model()
        logger.info(
            f"Initialized Autoencoder models: hidden={self.config.ae_hidden_dim}, "
            f"latent={self.config.ae_latent_dim}, lr={self.config.ae_learning_rate}"
        )

    def _initialize_sensors(self) -> None:
        self.sensors = self._get_all_readable_sensors()
        if "status_heat_pump" not in self.sensors:
            self.sensors.append("status_heat_pump")
        logger.info(f"Monitoring {len(self.sensors)} sensors")

    def _get_all_readable_sensors(self) -> List[str]:
        sensors = []

        for sensor in COMMON_SENSORS:
            if getattr(sensor, "read_supported", True):
                sensors.append(sensor.name)

        for sensor_name, sensor in BINARY_SENSOR_ADDRESSES.items():
            if getattr(sensor, "read_supported", True):
                sensors.append(sensor.name)

        for circuit_name in self.config.ml_circuits:
            try:
                if HeatingCircuit:
                    circuit_enum = HeatingCircuit[circuit_name.upper().strip()]
                    for sensor in heating_circuit_sensors(circuit_enum):
                        if getattr(sensor, "read_supported", True):
                            sensors.append(sensor.name)
            except (KeyError, AttributeError):
                logger.warning(f"Invalid heating circuit: {circuit_name}")

        for zone_id in self.config.ml_zones:
            try:
                for sensor in zone_sensors(zone_id):
                    if getattr(sensor, "read_supported", True):
                        sensors.append(sensor.name)
            except Exception as e:
                logger.warning(f"Invalid zone {zone_id}: {e}")

        seen = set()
        return [s for s in sensors if not (s in seen or seen.add(s))]

    def determine_mode(self, data: Dict[str, Any]) -> str:
        status_raw = data.get("status_heat_pump", 0)
        try:
            status_val = int(status_raw)
            if HeatPumpStatus:
                if status_val & HeatPumpStatus.DEFROSTING.value:
                    return "defrost"
                if status_val & HeatPumpStatus.WATER.value:
                    return "water"
                if status_val & HeatPumpStatus.COOLING.value:
                    return "cooling"
                if status_val & HeatPumpStatus.HEATING.value:
                    return "heating"
        except (ValueError, TypeError):
            pass
        return "standby"

    def enrich_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now()
        data["hour_of_day"] = now.hour
        data["day_of_week"] = now.weekday()
        data["is_weekend"] = 1 if now.weekday() >= 5 else 0

        for key, value in list(data.items()):
            if isinstance(value, (int, float)) and key in self.state.last_data_points:
                data[f"{key}_delta"] = value - self.state.last_data_points[key]
            if isinstance(value, (int, float)):
                self.state.last_data_points[key] = value

        stale_keys = [k for k in self.state.last_data_points if k not in data]
        for k in stale_keys:
            del self.state.last_data_points[k]

        try:
            flow_temp = data.get("temp_heat_pump_flow") or data.get(
                "temp_flow_current_circuit_a"
            )
            return_temp = data.get("temp_heat_pump_return") or data.get(
                "temp_return_current_circuit_a"
            )
            if flow_temp is not None and return_temp is not None:
                data["temp_spread"] = flow_temp - return_temp

            power_thermal = data.get("power_thermal")
            power_electrical = data.get("power_current")
            if (
                power_thermal is not None
                and power_electrical is not None
                and power_electrical > 0.2
            ):
                data["cop_instant"] = power_thermal / power_electrical
            else:
                data["cop_instant"] = 0.0
        except Exception as e:
            logger.debug(f"Feature engineering error: {e}")

        return data

    def fetch_data(self) -> Optional[Dict[str, Any]]:
        query_url = f"{self.config.metrics_url.rstrip('/')}/api/v1/query"
        regex = "|".join([f"{self.config.measurement_name}_{s}" for s in self.sensors])
        query = f'{{__name__=~"{regex}"}}'

        delay = self.config.retry_base_delay
        for attempt in range(self.config.retry_max_attempts):
            try:
                response = requests.post(query_url, data={"query": query}, timeout=10)
                if response.status_code != 200:
                    if attempt < self.config.retry_max_attempts - 1:
                        time.sleep(delay)
                        delay = min(
                            delay * self.config.retry_multiplier,
                            self.config.retry_max_delay,
                        )
                        continue
                    self.state.connection.total_fetch_errors += 1
                    self.state.connection.metrics_consecutive_failures += 1
                    return None

                json_data = response.json()
                if json_data.get("status") != "success":
                    self.state.connection.total_fetch_errors += 1
                    return None

                data_point = {}
                for result in json_data.get("data", {}).get("result", []):
                    metric_name = result["metric"].get("__name__", "")
                    sensor_name = metric_name.replace(
                        f"{self.config.measurement_name}_", ""
                    )
                    if "value" in result:
                        try:
                            data_point[sensor_name] = float(result["value"][1])
                        except (ValueError, TypeError):
                            pass

                self.state.connection.metrics_connected = True
                self.state.connection.metrics_last_success = time.time()
                self.state.connection.metrics_consecutive_failures = 0
                return data_point

            except requests.exceptions.ConnectionError:
                if attempt < self.config.retry_max_attempts - 1:
                    time.sleep(delay)
                    delay = min(
                        delay * self.config.retry_multiplier,
                        self.config.retry_max_delay,
                    )
                    continue
                self.state.connection.metrics_connected = False
                self.state.connection.metrics_consecutive_failures += 1
                self.state.connection.total_fetch_errors += 1
                return None
            except Exception as e:
                logger.error(f"Fetch error: {e}")
                self.state.connection.total_fetch_errors += 1
                return None

        return None

    def write_metrics(
        self,
        score: float,
        is_anomaly: bool,
        features_count: int,
        processing_time: float,
        mode: str,
    ) -> bool:
        write_url = f"{self.config.metrics_url.rstrip('/')}/write"
        lines = [
            f"idm_anomaly_score,mode={mode} value={score}",
            f"idm_anomaly_flag,mode={mode} value={1 if is_anomaly else 0}",
            f"idm_ml_features_count,mode={mode} value={features_count}",
            f"idm_ml_processing_time_ms,mode={mode} value={processing_time * 1000}",
            f"idm_ml_model_updates,mode={mode} value=1",
        ]

        delay = self.config.retry_base_delay
        for attempt in range(self.config.retry_max_attempts):
            try:
                response = requests.post(write_url, data="\n".join(lines), timeout=5)
                if response.status_code in (200, 204):
                    return True
                if attempt < self.config.retry_max_attempts - 1:
                    time.sleep(delay)
                    delay = min(
                        delay * self.config.retry_multiplier,
                        self.config.retry_max_delay,
                    )
                    continue
                self.state.connection.total_write_errors += 1
            except requests.exceptions.ConnectionError:
                if attempt < self.config.retry_max_attempts - 1:
                    time.sleep(delay)
                    delay = min(
                        delay * self.config.retry_multiplier,
                        self.config.retry_max_delay,
                    )
                    continue
                self.state.connection.total_write_errors += 1
            except Exception as e:
                logger.error(f"Write error: {e}")
                self.state.connection.total_write_errors += 1
                return False
        return False

    def send_alert(
        self,
        score: float,
        data: Dict[str, Any],
        mode: str,
        top_features: List[Dict[str, Any]],
    ) -> bool:
        if not self.config.enable_alerts:
            return False

        if time.time() - self.state.last_alert_time < self.config.alert_cooldown:
            logger.debug("Alert cooldown active")
            return False

        feature_msg = ""
        if top_features:
            feature_msg = "\n\nAuffällige Werte:\n" + "\n".join(
                f"- {f['feature']}: {f['value']:.2f} (Avg: {f['mean']:.2f}, Z: {f['score']:.1f})"
                for f in top_features
            )

        alert_url = f"{self.config.idm_logger_url}/api/internal/ml_alert"
        payload = {
            "type": "anomaly",
            "score": round(score, 4),
            "threshold": self.config.anomaly_threshold,
            "sensor_count": len(data),
            "timestamp": int(time.time()),
            "message": f"Anomalie erkannt! ({mode})\nScore: {score:.2f} (Limit: {self.config.anomaly_threshold}){feature_msg}",
            "data": {"mode": mode, "top_features": top_features},
        }

        headers = {}
        if self.config.internal_api_key:
            headers["X-Internal-Secret"] = self.config.internal_api_key

        delay = self.config.retry_base_delay
        for attempt in range(self.config.retry_max_attempts):
            try:
                response = requests.post(
                    alert_url, json=payload, headers=headers, timeout=5
                )
                if response.status_code in (200, 201):
                    logger.info(f"Alert sent (score: {score:.4f})")
                    self.state.last_alert_time = time.time()
                    self.state.connection.alert_last_success = time.time()
                    self.state.connection.alert_consecutive_failures = 0
                    return True
                if attempt < self.config.retry_max_attempts - 1:
                    time.sleep(delay)
                    delay = min(
                        delay * self.config.retry_multiplier,
                        self.config.retry_max_delay,
                    )
                    continue
                self.state.connection.alert_consecutive_failures += 1
                self.state.connection.total_alert_errors += 1
            except requests.exceptions.ConnectionError:
                if attempt < self.config.retry_max_attempts - 1:
                    time.sleep(delay)
                    delay = min(
                        delay * self.config.retry_multiplier,
                        self.config.retry_max_delay,
                    )
                    continue
                self.state.connection.alert_consecutive_failures += 1
                self.state.connection.total_alert_errors += 1
            except Exception as e:
                logger.error(f"Alert error: {e}")
                self.state.connection.total_alert_errors += 1
                return False
        return False

    def fetch_remote_config(self) -> None:
        url = f"{self.config.idm_logger_url}/api/internal/ml_config"
        headers = {}
        if self.config.internal_api_key:
            headers["X-Internal-Secret"] = self.config.internal_api_key

        try:
            response = requests.get(url, headers=headers, timeout=2)
            if response.status_code == 200:
                data = response.json()
                new_threshold = data.get("threshold")
                if new_threshold is not None:
                    self.config.update_threshold(float(new_threshold))
        except Exception as e:
            logger.debug(f"Config fetch error: {e}")

    def save_model_state(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.config.model_path), exist_ok=True)

            with self.model_lock:
                serialized = pickle.dumps(self.models)

            def _save_worker(data, path):
                temp_path = f"{path}.{uuid.uuid4()}.tmp"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(data)
                    os.replace(temp_path, path)
                    logger.info(f"Model saved to {path}")
                except Exception as e:
                    logger.error(f"Save error: {e}")
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass

            threading.Thread(
                target=_save_worker,
                args=(serialized, self.config.model_path),
                daemon=False,
            ).start()
            return True
        except Exception as e:
            logger.error(f"Save initiation failed: {e}")
            return False

    def load_model_state(self) -> bool:
        try:
            if not os.path.exists(self.config.model_path):
                logger.info("No saved model found, starting fresh")
                return False

            with self.model_lock:
                with open(self.config.model_path, "rb") as f:
                    loaded = pickle.load(f)

                if isinstance(loaded, dict):
                    for mode, state in loaded.items():
                        if mode in self.models and hasattr(state, "get"):
                            self.models[mode].load_state(state)
                        elif mode in self.models and hasattr(state, "sample_count"):
                            self.models[mode] = state
                    self.state.model_trained = True
                    logger.info(f"Model loaded from {self.config.model_path}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Load error: {e}")
            return False

    def process(self) -> None:
        self.fetch_remote_config()
        start = time.time()

        try:
            data = self.fetch_data()
            if not data:
                logger.debug("No data fetched")
                return

            min_features = int(len(self.sensors) * self.config.min_data_ratio)
            if len(data) < min_features:
                logger.warning(f"Low data ({len(data)}/{len(self.sensors)} sensors)")

            data = self.enrich_features(data)
            mode = self.determine_mode(data)
            self.state.current_mode = mode

            if mode == "defrost":
                logger.info("Defrost mode - skipping")
                return

            if mode not in self.models:
                logger.warning(f"Unknown mode '{mode}', using standby")
                mode = "standby"

            with self.model_lock:
                active_model = self.models[mode]
                score = active_model.score_one(data)
                active_model.learn_one(data)

            if (
                not self.state.model_trained
                and self.state.update_counter > self.config.warmup_updates
            ):
                self.state.model_trained = True
                logger.info(
                    f"Training completed (Updates > {self.config.warmup_updates})"
                )

            is_anomaly = score > self.config.anomaly_threshold

            if mode != self.state.last_mode:
                self.state.consecutive_anomalies[mode] = 0
                self.state.last_mode = mode

            if is_anomaly:
                self.state.consecutive_anomalies[mode] = (
                    self.state.consecutive_anomalies.get(mode, 0) + 1
                )
            else:
                self.state.consecutive_anomalies[mode] = 0

            mode_consecutive = self.state.consecutive_anomalies.get(mode, 0)
            processing_time = time.time() - start

            logger.info(
                f"Mode: {mode} | Score: {score:.4f} | Anomaly: {is_anomaly} "
                f"({mode_consecutive}/{self.config.alarm_consecutive_hits}) | Features: {len(data)}"
            )

            self.write_metrics(score, is_anomaly, len(data), processing_time, mode)

            if is_anomaly and self.state.model_trained:
                if mode_consecutive >= self.config.alarm_consecutive_hits:
                    top_features = active_model.get_top_features(data)
                    self.send_alert(score, data, mode, top_features)
                else:
                    logger.info(
                        f"Anomaly suppressed ({mode_consecutive}/{self.config.alarm_consecutive_hits})"
                    )

            self.state.last_score = score
            self.state.update_counter += 1

            if (
                time.time() - self.state.last_model_save
                > self.config.model_save_interval
            ):
                self.save_model_state()
                self.state.last_model_save = time.time()

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)

    def wait_for_connection(self) -> None:
        query_url = f"{self.config.metrics_url.rstrip('/')}/api/v1/query"
        delay = self.config.retry_base_delay
        attempt = 0

        logger.info(f"Connecting to VictoriaMetrics at {self.config.metrics_url}...")

        while True:
            attempt += 1
            try:
                response = requests.get(query_url, params={"query": "up"}, timeout=5)
                if response.status_code == 200:
                    logger.info(f"Connected after {attempt} attempt(s)")
                    self.state.connection.metrics_connected = True
                    return
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                logger.error(f"Connection error: {e}")

            logger.warning(f"Retrying in {delay:.1f}s...")
            time.sleep(delay)
            delay = min(
                delay * self.config.retry_multiplier, self.config.retry_max_delay
            )

    def get_health_status(self) -> Dict[str, Any]:
        is_healthy = (
            self.state.connection.metrics_connected or self.state.update_counter > 0
        )
        model_stats = {}

        with self.model_lock:
            for mode, model in self.models.items():
                model_stats[mode] = {
                    "samples": model.sample_count,
                    "features": len(model.feature_order) if model.feature_order else 0,
                    "ema_loss": round(model.ema_loss, 6) if model.ema_loss else None,
                    "consecutive_anomalies": self.state.consecutive_anomalies.get(
                        mode, 0
                    ),
                }

        return {
            "status": "healthy" if is_healthy else "degraded",
            "model_state": "trained" if self.state.model_trained else "learning",
            "current_mode": self.state.current_mode,
            "last_score": self.state.last_score,
            "features_count": len(self.sensors),
            "uptime_seconds": int(time.time() - self.state.start_time),
            "update_interval": self.config.update_interval,
            "anomaly_threshold": self.config.anomaly_threshold,
            "updates_processed": self.state.update_counter,
            "models": model_stats,
            "connection": {
                "metrics_connected": self.state.connection.metrics_connected,
                "metrics_failures": self.state.connection.metrics_consecutive_failures,
                "total_errors": self.state.connection.total_fetch_errors
                + self.state.connection.total_write_errors,
            },
        }
