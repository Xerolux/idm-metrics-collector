# Xerolux 2026
# SPDX-License-Identifier: MIT
import math
import os
import sys
import time
import logging
import schedule
import threading
import uuid
import pickle

import torch

try:
    import joblib

    USE_JOBLIB = True
except ImportError:
    USE_JOBLIB = False
    logging.warning("joblib not available, falling back to pickle (less secure)")

from flask import Flask, jsonify, request
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_service.config import config
from ml_service.models import create_model

try:
    from idm_logger.sensor_addresses import (
        COMMON_SENSORS,
        BINARY_SENSOR_ADDRESSES,
        heating_circuit_sensors,
        zone_sensors,
        HeatingCircuit,
    )
    from idm_logger.const import HeatPumpStatus
except ImportError:
    logging.warning("Could not import idm_logger modules, using stubs")
    COMMON_SENSORS = []
    BINARY_SENSOR_ADDRESSES = {}
    HeatPumpStatus = None
    HeatingCircuit = None

    def heating_circuit_sensors(x):
        return []

    def zone_sensors(x):
        return []


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ml-service")

MODES = ["heating", "cooling", "water", "standby"]

http_session = requests.Session()
start_time = time.time()
last_score = 0.0
model_trained = False
last_alert_time = 0
update_counter = 0
last_model_save = time.time()
current_mode = "unknown"
last_mode = "unknown"
last_data_points = {}
consecutive_anomalies = {}
model_lock = threading.Lock()
state_lock = threading.RLock()
_save_threads = []

connection_stats = {
    "metrics_connected": False,
    "metrics_last_success": None,
    "metrics_consecutive_failures": 0,
    "alert_last_success": None,
    "alert_consecutive_failures": 0,
    "total_fetch_errors": 0,
    "total_write_errors": 0,
    "total_alert_errors": 0,
}


def get_all_readable_sensors():
    sensors = []

    for sensor in COMMON_SENSORS:
        if sensor.read_supported:
            sensors.append(sensor.name)

    for sensor_name, sensor in BINARY_SENSOR_ADDRESSES.items():
        if sensor.read_supported:
            sensors.append(sensor.name)

    for circuit_name in config.ml_circuits:
        try:
            circuit_enum = HeatingCircuit[circuit_name.upper().strip()]
            circuit_sensors = heating_circuit_sensors(circuit_enum)
            for sensor in circuit_sensors:
                if sensor.read_supported:
                    sensors.append(sensor.name)
        except (KeyError, AttributeError):
            logger.warning(f"Invalid heating circuit: {circuit_name}")

    for zone_id in config.ml_zones:
        try:
            zone_sensor_list = zone_sensors(zone_id)
            for sensor in zone_sensor_list:
                if sensor.read_supported:
                    sensors.append(sensor.name)
        except Exception as e:
            logger.warning(f"Invalid zone {zone_id}: {e}")

    seen = set()
    unique_sensors = []
    for sensor in sensors:
        if sensor not in seen:
            seen.add(sensor)
            unique_sensors.append(sensor)

    return unique_sensors


SENSORS = get_all_readable_sensors()
if "status_heat_pump" not in SENSORS:
    SENSORS.append("status_heat_pump")

logger.info(
    f"Initializing Autoencoder models with: hidden={config.ae_hidden_dim}, "
    f"latent={config.ae_latent_dim}, lr={config.ae_learning_rate}"
)
models = {mode: create_model() for mode in MODES}

health_app = Flask(__name__)


@health_app.route("/health")
def health():
    with state_lock:
        _update_counter = update_counter
        _model_trained = model_trained
        _current_mode = current_mode
        _last_score = last_score
        _consecutive_anomalies = dict(consecutive_anomalies)

    is_healthy = connection_stats["metrics_connected"] or _update_counter > 0
    status = "healthy" if is_healthy else "degraded"

    model_stats = {}
    with model_lock:
        for mode, model in models.items():
            model_stats[mode] = {
                "samples": getattr(model, "sample_count", 0),
                "features": len(model.feature_order) if model.feature_order else 0,
                "ema_loss": round(model.ema_loss, 6) if model.ema_loss else None,
                "consecutive_anomalies": _consecutive_anomalies.get(mode, 0),
            }

    return jsonify(
        {
            "status": status,
            "model_state": "trained" if _model_trained else "learning",
            "current_mode": _current_mode,
            "last_score": _last_score,
            "features_count": len(SENSORS),
            "uptime_seconds": int(time.time() - start_time),
            "update_interval": config.update_interval,
            "anomaly_threshold": config.anomaly_threshold,
            "updates_processed": _update_counter,
            "models": model_stats,
            "connection": {
                "metrics_connected": connection_stats["metrics_connected"],
                "metrics_failures": connection_stats["metrics_consecutive_failures"],
                "total_errors": connection_stats["total_fetch_errors"]
                + connection_stats["total_write_errors"],
            },
        }
    ), 200


@health_app.route("/model/upload", methods=["POST"])
def upload_model():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        logger.info("Receiving new model file via API...")

        temp_path = config.model_path + ".tmp"
        file.save(temp_path)
        os.replace(temp_path, config.model_path)

        if load_model_state():
            return jsonify(
                {"success": True, "message": "Model updated and reloaded"}
            ), 200
        else:
            return jsonify({"error": "Failed to load uploaded model"}), 500

    except Exception as e:
        logger.error(f"Model upload failed: {e}")
        return jsonify({"error": str(e)}), 500


def _save_worker(serialized_data, filepath):
    temp_path = f"{filepath}.{uuid.uuid4()}.tmp"
    try:
        with open(temp_path, "wb") as f:
            f.write(serialized_data)
        os.replace(temp_path, filepath)
        logger.info(f"Model state saved to {filepath} (background)")
    except Exception as e:
        logger.error(f"Failed to save model state in background: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def save_model_state(wait=False):
    try:
        os.makedirs(os.path.dirname(config.model_path), exist_ok=True)

        with model_lock:
            state = {mode: model.get_state() for mode, model in models.items()}
            serialized = pickle.dumps(state)

        if wait:
            _save_worker(serialized, config.model_path)
        else:
            thread = threading.Thread(
                target=_save_worker, args=(serialized, config.model_path), daemon=False
            )
            thread.start()
            global _save_threads
            with model_lock:
                _save_threads.append(thread)
            _cleanup_save_threads()

        return True
    except Exception as e:
        logger.error(f"Failed to initiate model save: {e}")
        return False


def _cleanup_save_threads():
    global _save_threads
    with model_lock:
        _save_threads = [t for t in _save_threads if t.is_alive()]


def wait_for_saves(timeout=30):
    global _save_threads
    start = time.time()
    while _save_threads:
        with model_lock:
            active_threads = _save_threads[:]
        if not active_threads:
            break
        for thread in active_threads:
            remaining = timeout - (time.time() - start)
            if remaining <= 0:
                logger.warning(
                    f"Timeout waiting for {len(active_threads)} save threads"
                )
                return
            thread.join(timeout=min(1, remaining))
        _cleanup_save_threads()


def load_model_state():
    global models, model_trained
    try:
        if not os.path.exists(config.model_path):
            logger.info("No saved model state found, starting fresh")
            return False

        with model_lock:
            if USE_JOBLIB:
                loaded = joblib.load(config.model_path)
            else:
                with open(config.model_path, "rb") as f:
                    loaded = pickle.load(f)

            if isinstance(loaded, dict):
                first_val = next(iter(loaded.values()), None)
                if isinstance(first_val, dict) and "net_state" in first_val:
                    for mode in MODES:
                        if mode in loaded:
                            models[mode].load_state(loaded[mode])
                    logger.info(
                        f"Model state loaded (get_state format) from {config.model_path}"
                    )
                elif hasattr(first_val, "sample_count"):
                    models = loaded
                    for mode, model in models.items():
                        if hasattr(model, "sample_count") and model.sample_count < 100:
                            model.sample_count = 100
                    logger.info(
                        f"Legacy pickle model state loaded from {config.model_path}"
                    )

            for mode, model in models.items():
                if hasattr(model, "sample_count") and model.sample_count < 100:
                    model.sample_count = 100

            model_trained = True
        return True
    except Exception as e:
        logger.error(f"Failed to load model state: {e}")
        return False


def determine_mode(data):
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
        return "standby"
    except (ValueError, TypeError):
        return "standby"


ENGINEERED_SUFFIXES = frozenset(("_delta", "_sin", "_cos", "_spread", "_instant"))
ENGINEERED_KEYS = frozenset(
    (
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "hour_sin",
        "hour_cos",
        "temp_spread",
        "cop_instant",
    )
)


def enrich_features(data):
    global last_data_points
    now = time.localtime()

    data["hour_of_day"] = now.tm_hour
    data["day_of_week"] = now.tm_wday
    data["is_weekend"] = 1 if now.tm_wday >= 5 else 0

    hour_rad = now.tm_hour * 2 * math.pi / 24
    data["hour_sin"] = math.sin(hour_rad)
    data["hour_cos"] = math.cos(hour_rad)

    original_keys = {k for k in data if isinstance(data[k], (int, float))}
    for key in original_keys:
        if key in ENGINEERED_KEYS:
            continue
        if any(key.endswith(s) for s in ENGINEERED_SUFFIXES):
            continue
        if key in last_data_points:
            data[f"{key}_delta"] = data[key] - last_data_points[key]
        last_data_points[key] = data[key]

    stale_keys = [
        k
        for k in last_data_points
        if k not in data
        and k not in ENGINEERED_KEYS
        and not any(k.endswith(s) for s in ENGINEERED_SUFFIXES)
    ]
    for k in stale_keys:
        del last_data_points[k]

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

        if power_thermal is not None and power_electrical is not None:
            if power_electrical > 0.2:
                data["cop_instant"] = power_thermal / power_electrical
            else:
                data["cop_instant"] = 0.0

    except Exception as e:
        logger.debug(f"Feature engineering error: {e}")

    return data


def fetch_latest_data():
    query_url = f"{config.metrics_url.rstrip('/')}/api/v1/query"
    data_point = {}

    regex = "|".join([f"{config.measurement_name}_{s}" for s in SENSORS])
    query = f'{{__name__=~"{regex}"}}'

    delay = config.retry_base_delay
    last_error = None

    for attempt in range(config.retry_max_attempts):
        try:
            response = http_session.post(query_url, data={"query": query}, timeout=10)
            if response.status_code != 200:
                last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                if attempt < config.retry_max_attempts - 1:
                    logger.debug(f"Fetch attempt {attempt + 1} failed: {last_error}")
                    time.sleep(delay)
                    delay = min(delay * config.retry_multiplier, config.retry_max_delay)
                    continue
                logger.error(
                    f"Failed to fetch data after {config.retry_max_attempts} attempts: {last_error}"
                )
                connection_stats["total_fetch_errors"] += 1
                connection_stats["metrics_consecutive_failures"] += 1
                return None

            json_data = response.json()
            if json_data.get("status") != "success":
                logger.error(f"Query returned error status: {json_data}")
                connection_stats["total_fetch_errors"] += 1
                return None

            results = json_data.get("data", {}).get("result", [])

            for result in results:
                metric_name = result["metric"].get("__name__", "")
                sensor_name = metric_name.replace(f"{config.measurement_name}_", "")

                if "value" in result:
                    val = result["value"][1]
                    try:
                        data_point[sensor_name] = float(val)
                    except (ValueError, TypeError):
                        pass

            connection_stats["metrics_connected"] = True
            connection_stats["metrics_last_success"] = time.time()
            connection_stats["metrics_consecutive_failures"] = 0
            return data_point

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            if attempt < config.retry_max_attempts - 1:
                logger.debug(
                    f"Connection error on attempt {attempt + 1}, retrying in {delay:.1f}s"
                )
                time.sleep(delay)
                delay = min(delay * config.retry_multiplier, config.retry_max_delay)
                continue
            logger.error(
                f"Connection error after {config.retry_max_attempts} attempts: {e}"
            )
            connection_stats["metrics_connected"] = False
            connection_stats["metrics_consecutive_failures"] += 1
            connection_stats["total_fetch_errors"] += 1
            return None
        except Exception as e:
            logger.error(f"Exception fetching data: {e}")
            connection_stats["total_fetch_errors"] += 1
            return None

    return None


def write_metrics(score, is_anomaly, features_count, processing_time, mode):
    write_url = f"{config.metrics_url.rstrip('/')}/write"

    lines = [
        f"idm_anomaly_score,mode={mode} value={score}",
        f"idm_anomaly_flag,mode={mode} value={1 if is_anomaly else 0}",
        f"idm_ml_features_count,mode={mode} value={features_count}",
        f"idm_ml_processing_time_ms,mode={mode} value={processing_time * 1000}",
        f"idm_ml_model_updates,mode={mode} value=1",
    ]

    data = "\n".join(lines)
    delay = config.retry_base_delay

    for attempt in range(config.retry_max_attempts):
        try:
            response = http_session.post(write_url, data=data, timeout=5)
            if response.status_code in (200, 204):
                return
            if attempt < config.retry_max_attempts - 1:
                logger.debug(
                    f"Write attempt {attempt + 1} failed with {response.status_code}"
                )
                time.sleep(delay)
                delay = min(delay * config.retry_multiplier, config.retry_max_delay)
                continue
            logger.error(
                f"Failed to write metrics after {config.retry_max_attempts} attempts: {response.status_code}"
            )
            connection_stats["total_write_errors"] += 1
        except requests.exceptions.RequestException:
            if attempt < config.retry_max_attempts - 1:
                time.sleep(delay)
                delay = min(delay * config.retry_multiplier, config.retry_max_delay)
                continue
            logger.error(
                f"Connection error writing metrics after {config.retry_max_attempts} attempts"
            )
            connection_stats["total_write_errors"] += 1
        except Exception as e:
            logger.error(f"Exception writing metrics: {e}")
            connection_stats["total_write_errors"] += 1
            return


def get_top_features(model, data, n=3):
    try:
        return model.get_top_features(data, n=n)
    except Exception as e:
        logger.debug(f"Error extracting features: {e}")
        return []


def send_anomaly_alert(score, data, mode, top_features):
    global last_alert_time

    if not config.enable_alerts:
        return

    if time.time() - last_alert_time < config.alert_cooldown:
        logger.debug("Alert cooldown active, skipping notification")
        return

    feature_msg = ""
    if top_features:
        feature_msg = "\n\nAuffällige Werte:\n" + "\n".join(
            [
                f"- {f['feature']}: {f['value']:.2f} (Avg: {f['mean']:.2f}, Z: {f.get('z_score', f['score']):.1f})"
                for f in top_features
            ]
        )

    alert_url = f"{config.idm_logger_url}/api/internal/ml_alert"
    payload = {
        "type": "anomaly",
        "score": round(score, 4),
        "threshold": config.anomaly_threshold,
        "sensor_count": len(data),
        "timestamp": int(time.time()),
        "message": f"Anomalie erkannt! ({mode})\nScore: {score:.2f} (Limit: {config.anomaly_threshold}){feature_msg}",
        "data": {"mode": mode, "top_features": top_features},
    }

    headers = {}
    if config.internal_api_key:
        headers["X-Internal-Secret"] = config.internal_api_key

    delay = config.retry_base_delay

    for attempt in range(config.retry_max_attempts):
        try:
            response = http_session.post(
                alert_url, json=payload, headers=headers, timeout=5
            )
            if response.status_code in (200, 201):
                logger.info(f"Anomaly alert sent successfully (score: {score:.4f})")
                last_alert_time = time.time()
                connection_stats["alert_last_success"] = time.time()
                connection_stats["alert_consecutive_failures"] = 0
                return
            if attempt < config.retry_max_attempts - 1:
                logger.debug(
                    f"Alert attempt {attempt + 1} failed with {response.status_code}"
                )
                time.sleep(delay)
                delay = min(delay * config.retry_multiplier, config.retry_max_delay)
                continue
            logger.warning(
                f"Alert endpoint returned {response.status_code} after {config.retry_max_attempts} attempts"
            )
            connection_stats["alert_consecutive_failures"] += 1
            connection_stats["total_alert_errors"] += 1
        except requests.exceptions.RequestException:
            if attempt < config.retry_max_attempts - 1:
                time.sleep(delay)
                delay = min(delay * config.retry_multiplier, config.retry_max_delay)
                continue
            logger.error(
                f"Connection error sending alert after {config.retry_max_attempts} attempts"
            )
            connection_stats["alert_consecutive_failures"] += 1
            connection_stats["total_alert_errors"] += 1
        except Exception as e:
            logger.error(f"Failed to send anomaly alert: {e}")
            connection_stats["total_alert_errors"] += 1
            return


def fetch_remote_config():
    url = f"{config.idm_logger_url}/api/internal/ml_config"
    headers = {}
    if config.internal_api_key:
        headers["X-Internal-Secret"] = config.internal_api_key

    try:
        response = http_session.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            new_threshold = data.get("threshold")
            if new_threshold is not None:
                new_threshold = float(new_threshold)
                if config.update_threshold(new_threshold):
                    logger.info(
                        f"Updated ANOMALY_THRESHOLD to {new_threshold} (Sensitivity: {data.get('sensitivity')})"
                    )
    except Exception as e:
        logger.debug(f"Failed to fetch remote config: {e}")


def job():
    global last_score, model_trained, update_counter, last_model_save

    fetch_remote_config()

    start = time.time()

    try:
        data = fetch_latest_data()

        if not data:
            logger.debug("No data fetched. Waiting for next cycle.")
            return

        min_features = int(len(SENSORS) * config.min_data_ratio)
        if len(data) < min_features:
            missing_sensors = sorted(list(set(SENSORS) - set(data.keys())))
            logger.warning(
                f"Low data availability ({len(data)}/{len(SENSORS)} sensors, target {min_features}). Proceeding anyway to maintain data flow."
            )
            if missing_sensors:
                logger.debug(
                    f"Missing sensors (first 10): {', '.join(missing_sensors[:10])}..."
                )

        data = enrich_features(data)

        mode = determine_mode(data)
        with state_lock:
            global current_mode
            current_mode = mode

        if mode == "defrost":
            logger.info(
                "Defrost mode detected - skipping anomaly detection to avoid false positives."
            )
            return

        if mode not in models:
            logger.warning(f"Unknown mode '{mode}' detected. Using standby model.")
            mode = "standby"

        with model_lock:
            active_model = models[mode]

            score = active_model.score_one(data)
            active_model.learn_one(data)

        with state_lock:
            if not model_trained:
                if update_counter > config.warmup_updates:
                    model_trained = True
                    logger.info(
                        f"Model training phase completed (Updates > {config.warmup_updates})"
                    )

            is_anomaly = score > config.anomaly_threshold

            global consecutive_anomalies, last_mode
            if mode != last_mode:
                consecutive_anomalies[mode] = 0
                last_mode = mode
            if is_anomaly:
                consecutive_anomalies[mode] = consecutive_anomalies.get(mode, 0) + 1
            else:
                consecutive_anomalies[mode] = 0

            mode_consecutive = consecutive_anomalies.get(mode, 0)
            _model_trained = model_trained

        processing_time = time.time() - start

        logger.info(
            f"Mode: {mode} | Score: {score:.4f} | Anomaly: {is_anomaly} ({mode_consecutive}/{config.alarm_consecutive_hits}) | Features: {len(data)}"
        )

        write_metrics(score, is_anomaly, len(data), processing_time, mode)

        if is_anomaly and _model_trained:
            if mode_consecutive >= config.alarm_consecutive_hits:
                top_features = get_top_features(active_model, data)
                send_anomaly_alert(score, data, mode, top_features)
            else:
                logger.info(
                    f"Anomaly suppressed (Debounce {mode_consecutive}/{config.alarm_consecutive_hits})"
                )

        with state_lock:
            last_score = score
            update_counter += 1

        if time.time() - last_model_save > config.model_save_interval:
            save_model_state()
            last_model_save = time.time()

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)


def wait_for_connection():
    query_url = f"{config.metrics_url.rstrip('/')}/api/v1/query"
    delay = config.retry_base_delay
    attempt = 0

    logger.info(f"Attempting to connect to VictoriaMetrics at {config.metrics_url}...")

    while True:
        attempt += 1
        try:
            response = http_session.get(query_url, params={"query": "up"}, timeout=5)
            if response.status_code == 200:
                logger.info(
                    f"Successfully connected to VictoriaMetrics after {attempt} attempt(s)."
                )
                connection_stats["metrics_connected"] = True
                return
            else:
                logger.warning(
                    f"VictoriaMetrics reachable but returned {response.status_code}. Retrying in {delay:.1f}s..."
                )
        except requests.exceptions.RequestException:
            logger.warning(
                f"Connection refused to {config.metrics_url}. VictoriaMetrics might be starting up. Retrying in {delay:.1f}s..."
            )
        except Exception as e:
            logger.error(
                f"Unexpected error connecting to {config.metrics_url}: {e}. Retrying in {delay:.1f}s..."
            )

        time.sleep(delay)
        delay = min(delay * config.retry_multiplier, config.retry_max_delay)


def main():
    logger.info("=" * 60)
    logger.info("Starting IDM ML Service (PyTorch/Autoencoder)")
    logger.info("=" * 60)
    logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor}")
    logger.info(f"PyTorch {torch.__version__}")
    logger.info(f"Metrics URL: {config.metrics_url}")
    logger.info(f"Update Interval: {config.update_interval}s")
    logger.info(f"Anomaly Threshold: {config.anomaly_threshold}")
    logger.info(f"Min Data Ratio: {config.min_data_ratio}")
    logger.info(f"Monitoring {len(SENSORS)} sensors")
    logger.info(f"Circuits: {', '.join(config.ml_circuits)}")
    if config.ml_zones:
        logger.info(f"Zones: {', '.join(map(str, config.ml_zones))}")
    logger.info(
        f"Autoencoder: hidden={config.ae_hidden_dim}, latent={config.ae_latent_dim}, lr={config.ae_learning_rate}"
    )
    logger.info(f"Alerts: {'Enabled' if config.enable_alerts else 'Disabled'}")
    logger.info("=" * 60)

    load_model_state()
    wait_for_connection()

    logger.info("Starting health check server on port 8080...")
    threading.Thread(
        target=lambda: health_app.run(host="0.0.0.0", port=8080, debug=False),
        daemon=True,
    ).start()

    logger.info("Running initial processing...")
    job()

    schedule.every(config.update_interval).seconds.do(job)
    schedule.every(config.model_save_interval).seconds.do(save_model_state)

    logger.info(f"Scheduler started. Processing every {config.update_interval}s")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        save_model_state(wait=True)
        wait_for_saves(timeout=30)
        logger.info("ML Service stopped")


if __name__ == "__main__":
    main()
