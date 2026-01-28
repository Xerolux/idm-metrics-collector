# SPDX-License-Identifier: MIT
import os
import time
import logging
import requests
import schedule
import threading
from datetime import datetime
from river import anomaly
from river import preprocessing
from river import compose
from flask import Flask, jsonify
import sys

# Use joblib for safer model serialization (no arbitrary code execution)
try:
    import joblib

    USE_JOBLIB = True
except ImportError:
    import pickle

    USE_JOBLIB = False
    logging.warning("joblib not available, falling back to pickle (less secure)")

# Add parent directory to path to import idm_logger modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from idm_logger.sensor_addresses import (
    COMMON_SENSORS,
    BINARY_SENSOR_ADDRESSES,
    heating_circuit_sensors,
    zone_sensors,
    HeatingCircuit,
)
from idm_logger.const import HeatPumpStatus

# Configuration
METRICS_URL = os.environ.get("METRICS_URL", "http://victoriametrics:8428")
MEASUREMENT_NAME = os.environ.get("MEASUREMENT_NAME", "idm_heatpump")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 30))

# ML Configuration
ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD", "0.7"))
MIN_DATA_RATIO = float(os.environ.get("MIN_DATA_RATIO", "0.1"))
MODEL_N_TREES = int(os.environ.get("MODEL_N_TREES", "25"))
MODEL_HEIGHT = int(os.environ.get("MODEL_HEIGHT", "15"))
MODEL_WINDOW_SIZE = int(os.environ.get("MODEL_WINDOW_SIZE", "250"))
MODEL_SAVE_INTERVAL = int(
    os.environ.get("MODEL_SAVE_INTERVAL", "300")
)  # Save every 5 minutes
MODEL_PATH = os.environ.get("MODEL_PATH", "/app/data/model_state.pkl")
ENABLE_ALERTS = os.environ.get("ENABLE_ALERTS", "true").lower() == "true"
ALERT_COOLDOWN = int(os.environ.get("ALERT_COOLDOWN", "3600"))  # 1 hour between alerts
WARMUP_UPDATES = int(
    os.environ.get("WARMUP_UPDATES", "120")
)  # Default 1 hour (30s * 120)
ALARM_CONSECUTIVE_HITS = int(os.environ.get("ALARM_CONSECUTIVE_HITS", "3"))
IDM_LOGGER_URL = os.environ.get("IDM_LOGGER_URL", "http://idm-logger:5000")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY")

# Connection retry configuration
RETRY_BASE_DELAY = float(os.environ.get("RETRY_BASE_DELAY", "1.0"))
RETRY_MAX_DELAY = float(os.environ.get("RETRY_MAX_DELAY", "60.0"))
RETRY_MULTIPLIER = float(os.environ.get("RETRY_MULTIPLIER", "2.0"))
RETRY_MAX_ATTEMPTS = int(os.environ.get("RETRY_MAX_ATTEMPTS", "3"))

# Circuit and Zone configuration
ML_CIRCUITS = os.environ.get("ML_CIRCUITS", "A").split(",")
ML_ZONES = [
    int(z.strip()) for z in os.environ.get("ML_ZONES", "").split(",") if z.strip()
]

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ml-service")

# Global state
start_time = time.time()
last_score = 0.0
model_trained = False  # Main trained flag (true if ANY model is trained)
last_alert_time = 0
update_counter = 0
last_model_save = time.time()
current_mode = "unknown"
last_data_points = {}  # Store previous values for delta calculation
consecutive_anomalies = 0

# Connection health tracking
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

# Flask health check app
health_app = Flask(__name__)


@health_app.route("/health")
def health():
    """Health check endpoint for monitoring."""
    # Determine overall health status
    is_healthy = connection_stats["metrics_connected"] or update_counter > 0
    status = "healthy" if is_healthy else "degraded"

    return jsonify(
        {
            "status": status,
            "model_state": "trained" if model_trained else "learning",
            "current_mode": current_mode,
            "last_score": last_score,
            "features_count": len(get_all_readable_sensors()),
            "uptime_seconds": int(time.time() - start_time),
            "update_interval": UPDATE_INTERVAL,
            "anomaly_threshold": ANOMALY_THRESHOLD,
            "updates_processed": update_counter,
            "connection": {
                "metrics_connected": connection_stats["metrics_connected"],
                "metrics_failures": connection_stats["metrics_consecutive_failures"],
                "total_errors": connection_stats["total_fetch_errors"]
                + connection_stats["total_write_errors"],
            },
        }
    ), 200


def get_all_readable_sensors():
    """Get all sensors that are readable (read_supported=True)."""
    sensors = []

    # Add common sensors
    for sensor in COMMON_SENSORS:
        if sensor.read_supported:
            sensors.append(sensor.name)

    # Add binary sensors
    for sensor_name, sensor in BINARY_SENSOR_ADDRESSES.items():
        if sensor.read_supported:
            sensors.append(sensor.name)

    # Add heating circuit sensors for configured circuits
    for circuit_name in ML_CIRCUITS:
        try:
            circuit_enum = HeatingCircuit[circuit_name.upper().strip()]
            circuit_sensors = heating_circuit_sensors(circuit_enum)
            for sensor in circuit_sensors:
                if sensor.read_supported:
                    sensors.append(sensor.name)
        except KeyError:
            logger.warning(f"Invalid heating circuit: {circuit_name}")

    # Add zone sensors for configured zones
    for zone_id in ML_ZONES:
        try:
            zone_sensor_list = zone_sensors(zone_id)
            for sensor in zone_sensor_list:
                if sensor.read_supported:
                    sensors.append(sensor.name)
        except Exception as e:
            logger.warning(f"Invalid zone {zone_id}: {e}")

    # Remove duplicates while preserving order
    seen = set()
    unique_sensors = []
    for sensor in sensors:
        if sensor not in seen:
            seen.add(sensor)
            unique_sensors.append(sensor)

    return unique_sensors


SENSORS = get_all_readable_sensors()

# Ensure status_heat_pump is in SENSORS if not already
if "status_heat_pump" not in SENSORS:
    SENSORS.append("status_heat_pump")


def create_pipeline():
    """Create a new River anomaly detection pipeline."""
    return compose.Pipeline(
        preprocessing.StandardScaler(),
        anomaly.HalfSpaceTrees(
            n_trees=MODEL_N_TREES,
            height=MODEL_HEIGHT,
            window_size=MODEL_WINDOW_SIZE,
            seed=42,
        ),
    )


# Initialize River Models (one per mode)
logger.info(
    f"Initializing models with: n_trees={MODEL_N_TREES}, height={MODEL_HEIGHT}, window_size={MODEL_WINDOW_SIZE}"
)

# Modes: heating, cooling, water, standby. (Defrost is excluded/skipped)
MODES = ["heating", "cooling", "water", "standby"]
models = {mode: create_pipeline() for mode in MODES}


def save_model_state():
    """Save model state to disk for persistence across restarts."""
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        if USE_JOBLIB:
            joblib.dump(models, MODEL_PATH)
        else:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(models, f)
        logger.info(f"Model state saved to {MODEL_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to save model state: {e}")
        return False


def load_model_state():
    """Load model state from disk if available."""
    global models, model_trained
    try:
        if os.path.exists(MODEL_PATH):
            if USE_JOBLIB:
                loaded = joblib.load(MODEL_PATH)
            else:
                with open(MODEL_PATH, "rb") as f:
                    loaded = pickle.load(f)

            if isinstance(loaded, dict) and all(k in loaded for k in MODES):
                models = loaded
                logger.info(f"Multi-mode model state loaded from {MODEL_PATH}")
            else:
                logger.warning(
                    "Legacy model state found (single model). Starting fresh with multi-mode models."
                )
                # We could try to migrate, but a generic model is bad for specific modes.
                # Better to start fresh.

            # Assume if we loaded something valid, we have some training.
            # Realistically, we should check per model, but this flag is for global health.
            model_trained = True
            return True
        else:
            logger.info("No saved model state found, starting fresh")
            return False
    except Exception as e:
        logger.error(f"Failed to load model state: {e}")
        return False


def determine_mode(data: dict) -> str:
    """Determine the operating mode based on status_heat_pump."""
    status_raw = data.get("status_heat_pump", 0)
    try:
        status_val = int(status_raw)
        # Use bitwise operations on integer directly to avoid Enum validation errors
        # on combined flags (e.g., HEATING | DEFROSTING)

        if status_val & HeatPumpStatus.DEFROSTING.value:
            return "defrost"
        if status_val & HeatPumpStatus.WATER.value:
            return "water"
        if status_val & HeatPumpStatus.COOLING.value:
            return "cooling"
        if status_val & HeatPumpStatus.HEATING.value:
            return "heating"

        # Default to standby
        return "standby"
    except (ValueError, TypeError):
        return "standby"


def enrich_features(data: dict) -> dict:
    """Add temporal and computed features for better anomaly detection."""
    global last_data_points
    now = datetime.now()

    # Temporal features
    data["hour_of_day"] = now.hour
    data["day_of_week"] = now.weekday()
    data["is_weekend"] = 1 if now.weekday() >= 5 else 0

    # Delta features (Rate of change)
    # We track deltas for all float sensors
    # Use list(data.items()) to allow modifying data during iteration
    for key, value in list(data.items()):
        if isinstance(value, (int, float)) and key in last_data_points:
            # Calculate delta per minute (approx, assuming 30s interval)
            # Just raw delta is fine as interval is constant-ish
            data[f"{key}_delta"] = value - last_data_points[key]

        # Update last value
        last_data_points[key] = value

    # Computed features (if sensors available)
    try:
        # Temperature difference (Spread)
        # Try to find flow/return temps. Names vary by circuit but IDM usually has common ones.
        flow_temp = data.get("temp_heat_pump_flow") or data.get(
            "temp_flow_current_circuit_a"
        )
        return_temp = data.get("temp_heat_pump_return") or data.get(
            "temp_return_current_circuit_a"
        )  # Note: return might not be per circuit

        if flow_temp is not None and return_temp is not None:
            data["temp_spread"] = flow_temp - return_temp

        # Efficiency approximation (COP)
        # power_thermal = Heat Output, power_current = Electrical Input
        power_thermal = data.get("power_thermal")
        power_electrical = data.get("power_current")

        if power_thermal is not None and power_electrical is not None:
            if (
                power_electrical > 0.2
            ):  # Ignore very low power to avoid noise/division by zero
                data["cop_instant"] = power_thermal / power_electrical
            else:
                data["cop_instant"] = 0.0

    except Exception as e:
        logger.debug(f"Feature engineering error: {e}")

    return data


def fetch_latest_data():
    """
    Fetch the latest values for the selected sensors from VictoriaMetrics.
    Uses exponential backoff retry on transient failures.
    """
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"
    data_point = {}

    # Query regex to match all relevant metrics
    regex = "|".join([f"{MEASUREMENT_NAME}_{s}" for s in SENSORS])
    query = f'{{__name__=~"{regex}"}}'

    delay = RETRY_BASE_DELAY
    last_error = None

    for attempt in range(RETRY_MAX_ATTEMPTS):
        try:
            response = requests.get(query_url, params={"query": query}, timeout=10)
            if response.status_code != 200:
                last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                if attempt < RETRY_MAX_ATTEMPTS - 1:
                    logger.debug(f"Fetch attempt {attempt + 1} failed: {last_error}")
                    time.sleep(delay)
                    delay = min(delay * RETRY_MULTIPLIER, RETRY_MAX_DELAY)
                    continue
                logger.error(
                    f"Failed to fetch data after {RETRY_MAX_ATTEMPTS} attempts: {last_error}"
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
                # Extract sensor name by removing prefix
                sensor_name = metric_name.replace(f"{MEASUREMENT_NAME}_", "")

                if "value" in result:
                    # PromQL instant query value is [timestamp, "value"]
                    val = result["value"][1]
                    try:
                        data_point[sensor_name] = float(val)
                    except (ValueError, TypeError):
                        pass

            # Success - update connection stats
            connection_stats["metrics_connected"] = True
            connection_stats["metrics_last_success"] = time.time()
            connection_stats["metrics_consecutive_failures"] = 0
            return data_point

        except requests.exceptions.ConnectionError as e:
            last_error = str(e)
            if attempt < RETRY_MAX_ATTEMPTS - 1:
                logger.debug(
                    f"Connection error on attempt {attempt + 1}, retrying in {delay:.1f}s"
                )
                time.sleep(delay)
                delay = min(delay * RETRY_MULTIPLIER, RETRY_MAX_DELAY)
                continue
            logger.error(f"Connection error after {RETRY_MAX_ATTEMPTS} attempts: {e}")
            connection_stats["metrics_connected"] = False
            connection_stats["metrics_consecutive_failures"] += 1
            connection_stats["total_fetch_errors"] += 1
            return None
        except Exception as e:
            logger.error(f"Exception fetching data: {e}")
            connection_stats["total_fetch_errors"] += 1
            return None

    return None


def write_metrics(
    score: float,
    is_anomaly: bool,
    features_count: int,
    processing_time: float,
    mode: str,
):
    """
    Write anomaly and ML performance metrics to VictoriaMetrics.
    Uses retry logic for transient failures.
    """
    write_url = f"{METRICS_URL.rstrip('/')}/write"

    lines = [
        f"idm_anomaly_score,mode={mode} value={score}",
        f"idm_anomaly_flag,mode={mode} value={1 if is_anomaly else 0}",
        f"idm_ml_features_count,mode={mode} value={features_count}",
        f"idm_ml_processing_time_ms,mode={mode} value={processing_time * 1000}",
        f"idm_ml_model_updates,mode={mode} value=1",  # Counter
    ]

    data = "\n".join(lines)
    delay = RETRY_BASE_DELAY

    for attempt in range(RETRY_MAX_ATTEMPTS):
        try:
            response = requests.post(write_url, data=data, timeout=5)
            if response.status_code in (200, 204):
                return  # Success
            if attempt < RETRY_MAX_ATTEMPTS - 1:
                logger.debug(
                    f"Write attempt {attempt + 1} failed with {response.status_code}"
                )
                time.sleep(delay)
                delay = min(delay * RETRY_MULTIPLIER, RETRY_MAX_DELAY)
                continue
            logger.error(
                f"Failed to write metrics after {RETRY_MAX_ATTEMPTS} attempts: {response.status_code}"
            )
            connection_stats["total_write_errors"] += 1
        except requests.exceptions.ConnectionError:
            if attempt < RETRY_MAX_ATTEMPTS - 1:
                time.sleep(delay)
                delay = min(delay * RETRY_MULTIPLIER, RETRY_MAX_DELAY)
                continue
            logger.error(
                f"Connection error writing metrics after {RETRY_MAX_ATTEMPTS} attempts"
            )
            connection_stats["total_write_errors"] += 1
        except Exception as e:
            logger.error(f"Exception writing metrics: {e}")
            connection_stats["total_write_errors"] += 1
            return


def get_top_features(model, data, n=3):
    """Identify top contributing features based on Z-score deviation."""
    try:
        # Access scaler from pipeline
        if "StandardScaler" not in model.steps:
            return []

        scaler = model["StandardScaler"]
        # Check if scaler has stats
        if not hasattr(scaler, "means") or not hasattr(scaler, "vars"):
            return []

        contributions = []
        for key, value in data.items():
            if isinstance(value, (int, float)) and key in scaler.means:
                mean = scaler.means[key]
                var = scaler.vars[key]
                std = var**0.5
                if std > 1e-6:
                    z_score = abs(value - mean) / std
                    contributions.append(
                        {
                            "feature": key,
                            "score": float(z_score),
                            "value": float(value),
                            "mean": float(mean),
                        }
                    )

        # Sort by Z-score descending
        contributions.sort(key=lambda x: x["score"], reverse=True)
        return contributions[:n]
    except Exception as e:
        logger.debug(f"Error extracting features: {e}")
        return []


def send_anomaly_alert(score: float, data: dict, mode: str, top_features: list):
    """
    Send anomaly alert to IDM Logger notification system.
    Uses retry logic for transient failures.
    """
    global last_alert_time

    if not ENABLE_ALERTS:
        return

    # Check cooldown
    if time.time() - last_alert_time < ALERT_COOLDOWN:
        logger.debug("Alert cooldown active, skipping notification")
        return

    feature_msg = ""
    if top_features:
        feature_msg = "\n\nAuffällige Werte:\n" + "\n".join(
            [
                f"- {f['feature']}: {f['value']:.2f} (Avg: {f['mean']:.2f}, Z: {f['score']:.1f})"
                for f in top_features
            ]
        )

    alert_url = f"{IDM_LOGGER_URL}/api/internal/ml_alert"
    payload = {
        "type": "anomaly",
        "score": round(score, 4),
        "threshold": ANOMALY_THRESHOLD,
        "sensor_count": len(data),
        "timestamp": int(time.time()),
        "message": f"Anomalie erkannt! ({mode})\nScore: {score:.2f} (Limit: {ANOMALY_THRESHOLD}){feature_msg}",
        "data": {"mode": mode, "top_features": top_features},
    }

    headers = {}
    if INTERNAL_API_KEY:
        headers["X-Internal-Secret"] = INTERNAL_API_KEY

    delay = RETRY_BASE_DELAY

    for attempt in range(RETRY_MAX_ATTEMPTS):
        try:
            response = requests.post(
                alert_url, json=payload, headers=headers, timeout=5
            )
            if response.status_code in (200, 201):
                logger.info(f"Anomaly alert sent successfully (score: {score:.4f})")
                last_alert_time = time.time()
                connection_stats["alert_last_success"] = time.time()
                connection_stats["alert_consecutive_failures"] = 0
                return
            if attempt < RETRY_MAX_ATTEMPTS - 1:
                logger.debug(
                    f"Alert attempt {attempt + 1} failed with {response.status_code}"
                )
                time.sleep(delay)
                delay = min(delay * RETRY_MULTIPLIER, RETRY_MAX_DELAY)
                continue
            logger.warning(
                f"Alert endpoint returned {response.status_code} after {RETRY_MAX_ATTEMPTS} attempts"
            )
            connection_stats["alert_consecutive_failures"] += 1
            connection_stats["total_alert_errors"] += 1
        except requests.exceptions.ConnectionError:
            if attempt < RETRY_MAX_ATTEMPTS - 1:
                time.sleep(delay)
                delay = min(delay * RETRY_MULTIPLIER, RETRY_MAX_DELAY)
                continue
            logger.error(
                f"Connection error sending alert after {RETRY_MAX_ATTEMPTS} attempts"
            )
            connection_stats["alert_consecutive_failures"] += 1
            connection_stats["total_alert_errors"] += 1
        except Exception as e:
            logger.error(f"Failed to send anomaly alert: {e}")
            connection_stats["total_alert_errors"] += 1
            return


def job():
    """
    Main job loop - fetch data, process with model, detect anomalies.
    """
    global last_score, model_trained, update_counter, last_model_save

    start = time.time()

    try:
        data = fetch_latest_data()

        if not data:
            logger.debug("No data fetched. Waiting for next cycle.")
            return

        min_features = int(len(SENSORS) * MIN_DATA_RATIO)
        if len(data) < min_features:
            missing_sensors = sorted(list(set(SENSORS) - set(data.keys())))
            logger.warning(
                f"Low data availability ({len(data)}/{len(SENSORS)} sensors, target {min_features}). Proceeding anyway to maintain data flow."
            )
            if missing_sensors:
                logger.debug(
                    f"Missing sensors (first 10): {', '.join(missing_sensors[:10])}..."
                )
            # We do NOT return here anymore, to ensure graphs are not empty.
            # River can handle sparse data (though accuracy might suffer).

        # Enrich with temporal and computed features
        data = enrich_features(data)

        # Determine mode
        mode = determine_mode(data)
        global current_mode
        current_mode = mode

        # Skip processing for defrost mode (user suggestion)
        if mode == "defrost":
            logger.info(
                "Defrost mode detected - skipping anomaly detection to avoid false positives."
            )
            return

        if mode not in models:
            logger.warning(f"Unknown mode '{mode}' detected. Using standby model.")
            mode = "standby"

        active_model = models[mode]

        # Update model
        score = active_model.score_one(data)
        active_model.learn_one(data)

        # Warm-up Logic
        if not model_trained:
            if update_counter > WARMUP_UPDATES:
                model_trained = True
                logger.info(
                    f"Model training phase completed (Updates > {WARMUP_UPDATES})"
                )
            else:
                # During warmup, we don't count anomalies
                pass

        # Determine anomaly flag and Debounce
        is_anomaly = score > ANOMALY_THRESHOLD

        global consecutive_anomalies
        if is_anomaly:
            consecutive_anomalies += 1
        else:
            consecutive_anomalies = 0

        processing_time = time.time() - start

        logger.info(
            f"Mode: {mode} | Score: {score:.4f} | Anomaly: {is_anomaly} ({consecutive_anomalies}/{ALARM_CONSECUTIVE_HITS}) | Features: {len(data)}"
        )

        # Write metrics
        write_metrics(score, is_anomaly, len(data), processing_time, mode)

        # Send alert if anomaly detected AND confirmed (debounce) AND warmed up
        if is_anomaly and model_trained:
            if consecutive_anomalies >= ALARM_CONSECUTIVE_HITS:
                top_features = get_top_features(active_model, data)
                send_anomaly_alert(score, data, mode, top_features)
                # Reset counter to avoid spamming every cycle after trigger?
                # Or keep it high? If we reset, we might alert again in 3 cycles.
                # Usually better to let cooldown handle the frequency limit.
                # But to prevent "flickering" alarm states, we keep counting.
                # The send_anomaly_alert has cooldown.
            else:
                logger.info(
                    f"Anomaly suppressed (Debounce {consecutive_anomalies}/{ALARM_CONSECUTIVE_HITS})"
                )

        last_score = score
        update_counter += 1

        # Periodic model save
        if time.time() - last_model_save > MODEL_SAVE_INTERVAL:
            save_model_state()
            last_model_save = time.time()

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)


def wait_for_connection():
    """
    Wait for VictoriaMetrics to be reachable.
    Uses exponential backoff to avoid overwhelming the service during startup.
    """
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"
    delay = RETRY_BASE_DELAY
    attempt = 0

    logger.info(f"Attempting to connect to VictoriaMetrics at {METRICS_URL}...")

    while True:
        attempt += 1
        try:
            response = requests.get(query_url, params={"query": "up"}, timeout=5)
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
        except requests.exceptions.ConnectionError:
            logger.warning(
                f"Connection refused to {METRICS_URL}. VictoriaMetrics might be starting up. Retrying in {delay:.1f}s..."
            )
        except Exception as e:
            logger.error(
                f"Unexpected error connecting to {METRICS_URL}: {e}. Retrying in {delay:.1f}s..."
            )

        time.sleep(delay)
        delay = min(delay * RETRY_MULTIPLIER, RETRY_MAX_DELAY)


def main():
    logger.info("=" * 60)
    logger.info("Starting IDM ML Service (River/HalfSpaceTrees)")
    logger.info("=" * 60)
    logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor}")
    logger.info(f"Metrics URL: {METRICS_URL}")
    logger.info(f"Update Interval: {UPDATE_INTERVAL}s")
    logger.info(f"Anomaly Threshold: {ANOMALY_THRESHOLD}")
    logger.info(f"Min Data Ratio: {MIN_DATA_RATIO}")
    logger.info(f"Monitoring {len(SENSORS)} sensors")
    logger.info(f"Circuits: {', '.join(ML_CIRCUITS)}")
    if ML_ZONES:
        logger.info(f"Zones: {', '.join(map(str, ML_ZONES))}")
    logger.info(
        f"Model: n_trees={MODEL_N_TREES}, height={MODEL_HEIGHT}, window={MODEL_WINDOW_SIZE}"
    )
    logger.info(f"Alerts: {'Enabled' if ENABLE_ALERTS else 'Disabled'}")
    logger.info("=" * 60)

    # Load model state if available
    load_model_state()

    # Wait for DB connection
    wait_for_connection()

    # Start health check server in background thread
    logger.info("Starting health check server on port 8080...")
    threading.Thread(
        target=lambda: health_app.run(host="0.0.0.0", port=8080, debug=False),
        daemon=True,
    ).start()

    # Run once immediately
    logger.info("Running initial processing...")
    job()

    # Schedule periodic updates
    schedule.every(UPDATE_INTERVAL).seconds.do(job)

    # Schedule periodic model saves
    schedule.every(MODEL_SAVE_INTERVAL).seconds.do(save_model_state)

    logger.info(f"Scheduler started. Processing every {UPDATE_INTERVAL}s")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        # Save model on exit
        save_model_state()
        logger.info("ML Service stopped")


if __name__ == "__main__":
    main()
