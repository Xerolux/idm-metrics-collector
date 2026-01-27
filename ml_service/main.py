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
import copy

# Use joblib for safer model serialization (no arbitrary code execution)
# pickle is still needed for community model loading
import pickle

try:
    import joblib

    USE_JOBLIB = True
except ImportError:
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
from .utils.crypto import load_encrypted_model

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
COMMUNITY_MODEL_PATH = os.environ.get(
    "COMMUNITY_MODEL_PATH", "/app/data/community_model.enc"
)
ENABLE_ALERTS = os.environ.get("ENABLE_ALERTS", "true").lower() == "true"
ALERT_COOLDOWN = int(os.environ.get("ALERT_COOLDOWN", "3600"))  # 1 hour between alerts
WARMUP_UPDATES = int(
    os.environ.get("WARMUP_UPDATES", "120")
)  # Default 1 hour (30s * 120)
ALARM_CONSECUTIVE_HITS = int(os.environ.get("ALARM_CONSECUTIVE_HITS", "3"))
IDM_LOGGER_URL = os.environ.get("IDM_LOGGER_URL", "http://idm-logger:5000")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY")

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
last_model_save = time.time()

# Modes: heating, cooling, water, standby. (Defrost is excluded/skipped)
MODES = ["heating", "cooling", "water", "standby"]


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


class HeatpumpContext:
    """Holds the ML state for a single heatpump."""

    def __init__(self, hp_id):
        self.hp_id = hp_id
        self.models = {mode: create_pipeline() for mode in MODES}
        self.last_data_points = {}
        self.consecutive_anomalies = 0
        self.current_mode = "unknown"
        self.last_score = 0.0
        self.model_trained = False
        self.update_counter = 0
        self.last_alert_time = 0

    def restore_models(self, saved_models: dict):
        """Restore models from saved dictionary."""
        if all(k in saved_models for k in MODES):
            self.models = saved_models
            self.model_trained = True
            logger.info(f"[{self.hp_id}] Restored models from persistence.")
        else:
            logger.warning(
                f"[{self.hp_id}] Saved model state incomplete. Starting fresh."
            )


# Contexts
contexts = {}  # type: dict[str, HeatpumpContext]
saved_state_cache = {}  # type: dict[str, dict]


# Flask health check app
health_app = Flask(__name__)


@health_app.route("/health")
def health():
    """Health check endpoint for monitoring."""
    hp_summaries = {}
    for hp_id, ctx in contexts.items():
        hp_summaries[hp_id] = {
            "model_state": "trained" if ctx.model_trained else "learning",
            "current_mode": ctx.current_mode,
            "last_score": ctx.last_score,
            "updates_processed": ctx.update_counter,
        }

    return jsonify(
        {
            "status": "healthy",
            "heatpumps": hp_summaries,
            "uptime_seconds": int(time.time() - start_time),
            "update_interval": UPDATE_INTERVAL,
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


def save_model_state():
    """Save model state to disk for persistence across restarts."""
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        # Structure: {hp_id: {mode: pipeline}}
        export_data = {}
        for hp_id, ctx in contexts.items():
            export_data[hp_id] = ctx.models

        if USE_JOBLIB:
            joblib.dump(export_data, MODEL_PATH)
        else:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(export_data, f)
        logger.info(f"Model state saved to {MODEL_PATH} ({len(contexts)} contexts)")
        return True
    except Exception as e:
        logger.error(f"Failed to save model state: {e}")
        return False


def load_model_state():
    """Load model state from disk if available."""
    global saved_state_cache

    # 1. Check for Community Model (Encrypted) - acts as default seed
    if os.path.exists(COMMUNITY_MODEL_PATH):
        try:
            community_model = load_encrypted_model(COMMUNITY_MODEL_PATH)
            if community_model:
                saved_state_cache["community"] = community_model
                logger.info("Loaded community model template (encrypted)")
        except Exception as e:
            logger.error(f"Failed to load community model: {e}")

    # 2. Check for Local Model
    try:
        if os.path.exists(MODEL_PATH):
            if USE_JOBLIB:
                loaded = joblib.load(MODEL_PATH)
            else:
                with open(MODEL_PATH, "rb") as f:
                    loaded = pickle.load(f)

            if isinstance(loaded, dict):
                # Check format: Version 1 (Mode -> Model) or Version 2 (HP -> Mode -> Model)
                # Heuristic: keys are modes or HP IDs?
                # Modes are 'heating', 'cooling' etc. HP IDs are usually 'hp-...' or numbers.
                keys = list(loaded.keys())
                if keys and keys[0] in MODES:
                    # Version 1 (Single HP Legacy)
                    logger.info("Detected legacy model state (single device).")
                    saved_state_cache["default"] = loaded
                else:
                    # Version 2 (Multi HP)
                    saved_state_cache = loaded
                    logger.info(
                        f"Multi-device model state loaded ({len(saved_state_cache)} devices)"
                    )
            else:
                logger.warning("Invalid model state format.")

            return True
        else:
            logger.info("No saved model state found.")
            return False
    except Exception as e:
        logger.error(f"Failed to load model state: {e}")
        return False


def get_context(hp_id: str) -> HeatpumpContext:
    """Get or create a context for a heatpump."""
    if hp_id not in contexts:
        logger.info(f"New heatpump detected: {hp_id}")
        ctx = HeatpumpContext(hp_id)
        # Try to restore
        if hp_id in saved_state_cache:
            ctx.restore_models(saved_state_cache[hp_id])
        elif "default" in saved_state_cache:
            # Try to migrate legacy default to first seen HP?
            logger.info(f"[{hp_id}] seeding with legacy model state")
            ctx.restore_models(saved_state_cache["default"])
        elif "community" in saved_state_cache:
            # Seed with community model if no local history
            logger.info(f"[{hp_id}] seeding with community model template")
            # Deep copy to ensure independence
            ctx.restore_models(copy.deepcopy(saved_state_cache["community"]))

        contexts[hp_id] = ctx

    return contexts[hp_id]


def determine_mode(data: dict) -> str:
    """Determine the operating mode based on status_heat_pump."""
    status_raw = data.get("status_heat_pump", 0)
    try:
        status_val = int(status_raw)
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


def enrich_features(ctx: HeatpumpContext, data: dict) -> dict:
    """Add temporal and computed features for better anomaly detection."""
    now = datetime.now()

    # Temporal features
    data["hour_of_day"] = now.hour
    data["day_of_week"] = now.weekday()
    data["is_weekend"] = 1 if now.weekday() >= 5 else 0

    # Delta features
    for key, value in list(data.items()):
        if isinstance(value, (int, float)) and key in ctx.last_data_points:
            data[f"{key}_delta"] = value - ctx.last_data_points[key]
        ctx.last_data_points[key] = value

    # Computed features
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


def fetch_latest_data() -> dict:
    """
    Fetch the latest values from VictoriaMetrics.
    Returns: Dict[hp_id, Dict[sensor, value]]
    """
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"
    data_by_hp = {}

    # Query regex to match all relevant metrics
    regex = "|".join([f"{MEASUREMENT_NAME}_{s}" for s in SENSORS])
    # Match any metric starting with regex
    query = f'{{__name__=~"{regex}"}}'

    try:
        response = requests.get(query_url, params={"query": query}, timeout=10)
        if response.status_code != 200:
            logger.error(
                f"Failed to fetch data: {response.status_code} {response.text}"
            )
            return {}

        json_data = response.json()
        if json_data.get("status") != "success":
            return {}

        results = json_data.get("data", {}).get("result", [])

        for result in results:
            metric = result.get("metric", {})
            metric_name = metric.get("__name__", "")

            # Identify Heatpump ID
            hp_id = metric.get("heatpump_id", "default")

            # Extract sensor name
            sensor_name = metric_name.replace(f"{MEASUREMENT_NAME}_", "")

            if "value" in result:
                val = result["value"][1]
                try:
                    val_float = float(val)
                    if hp_id not in data_by_hp:
                        data_by_hp[hp_id] = {}
                    data_by_hp[hp_id][sensor_name] = val_float
                except (ValueError, TypeError):
                    pass

        return data_by_hp

    except Exception as e:
        logger.error(f"Exception fetching data: {e}")
        return {}


def write_metrics(
    ctx: HeatpumpContext,
    score: float,
    is_anomaly: bool,
    features_count: int,
    processing_time: float,
    mode: str,
):
    """Write anomaly metrics to VictoriaMetrics."""
    write_url = f"{METRICS_URL.rstrip('/')}/write"

    # Escape hp_id for label
    hp_label = ctx.hp_id.replace('"', '\\"')

    lines = [
        f'idm_anomaly_score{{heatpump_id="{hp_label}",mode="{mode}"}} {score}',
        f'idm_anomaly_flag{{heatpump_id="{hp_label}",mode="{mode}"}} {1 if is_anomaly else 0}',
        f'idm_ml_features_count{{heatpump_id="{hp_label}",mode="{mode}"}} {features_count}',
        f'idm_ml_processing_time_ms{{heatpump_id="{hp_label}",mode="{mode}"}} {processing_time * 1000}',
        f'idm_ml_model_updates{{heatpump_id="{hp_label}",mode="{mode}"}} 1',
    ]

    data = "\n".join(lines)

    try:
        response = requests.post(write_url, data=data, timeout=5)
        if response.status_code not in (200, 204):
            logger.error(f"Failed to write metrics: {response.status_code}")
    except Exception as e:
        logger.error(f"Exception writing metrics: {e}")


def get_top_features(model, data, n=3):
    """Identify top contributing features based on Z-score deviation."""
    try:
        if "StandardScaler" not in model.steps:
            return []
        scaler = model["StandardScaler"]
        if not hasattr(scaler, "means"):
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
        contributions.sort(key=lambda x: x["score"], reverse=True)
        return contributions[:n]
    except Exception:
        return []


def send_anomaly_alert(
    ctx: HeatpumpContext, score: float, data: dict, mode: str, top_features: list
):
    """Send anomaly alert to IDM Logger."""
    if not ENABLE_ALERTS:
        return

    if time.time() - ctx.last_alert_time < ALERT_COOLDOWN:
        return

    feature_msg = ""
    if top_features:
        feature_msg = "\n\nAuffällige Werte:\n" + "\n".join(
            [
                f"- {f['feature']}: {f['value']:.2f} (Avg: {f['mean']:.2f}, Z: {f['score']:.1f})"
                for f in top_features
            ]
        )

    try:
        alert_url = f"{IDM_LOGGER_URL}/api/internal/ml_alert"
        payload = {
            "type": "anomaly",
            "heatpump_id": ctx.hp_id,
            "score": round(score, 4),
            "threshold": ANOMALY_THRESHOLD,
            "sensor_count": len(data),
            "timestamp": int(time.time()),
            "message": f"⚠️ Anomalie erkannt! ({ctx.hp_id} / {mode})\nScore: {score:.2f} (Limit: {ANOMALY_THRESHOLD}){feature_msg}",
            "data": {
                "mode": mode,
                "top_features": top_features,
                "heatpump_id": ctx.hp_id,
            },
        }

        headers = {}
        if INTERNAL_API_KEY:
            headers["X-Internal-Secret"] = INTERNAL_API_KEY

        requests.post(alert_url, json=payload, headers=headers, timeout=5)
        ctx.last_alert_time = time.time()
        logger.info(f"[{ctx.hp_id}] Anomaly alert sent (score: {score:.4f})")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")


def process_heatpump(hp_id: str, data: dict):
    """Process data for a single heatpump."""
    ctx = get_context(hp_id)

    min_features = int(len(SENSORS) * MIN_DATA_RATIO)
    if len(data) < min_features:
        logger.warning(
            f"[{hp_id}] Low data availability: {len(data)}/{len(SENSORS)} sensors ({len(data)/len(SENSORS)*100:.1f}%). "
            f"Minimum required: {MIN_DATA_RATIO*100:.0f}%. Proceeding anyway."
        )

    start = time.time()
    data = enrich_features(ctx, data)
    mode = determine_mode(data)
    ctx.current_mode = mode

    if mode == "defrost":
        return

    if mode not in ctx.models:
        mode = "standby"

    active_model = ctx.models[mode]
    score = active_model.score_one(data)
    active_model.learn_one(data)

    if not ctx.model_trained:
        if ctx.update_counter > WARMUP_UPDATES:
            ctx.model_trained = True
            logger.info(f"[{hp_id}] Model training phase completed")

    is_anomaly = score > ANOMALY_THRESHOLD

    if is_anomaly:
        ctx.consecutive_anomalies += 1
    else:
        ctx.consecutive_anomalies = 0

    processing_time = time.time() - start

    logger.info(
        f"[{hp_id}] Mode: {mode} | Score: {score:.4f} | Anomaly: {is_anomaly} ({ctx.consecutive_anomalies}/{ALARM_CONSECUTIVE_HITS})"
    )

    write_metrics(ctx, score, is_anomaly, len(data), processing_time, mode)

    if is_anomaly and ctx.model_trained:
        if ctx.consecutive_anomalies >= ALARM_CONSECUTIVE_HITS:
            top_features = get_top_features(active_model, data)
            send_anomaly_alert(ctx, score, data, mode, top_features)

    ctx.last_score = score
    ctx.update_counter += 1


def job():
    """Main job loop."""
    global last_model_save

    try:
        all_data = fetch_latest_data()

        if not all_data:
            logger.debug("No data fetched.")
            return

        for hp_id, data in all_data.items():
            try:
                process_heatpump(hp_id, data)
            except Exception as e:
                logger.error(f"Error processing {hp_id}: {e}")

        # Periodic save
        if time.time() - last_model_save > MODEL_SAVE_INTERVAL:
            save_model_state()
            last_model_save = time.time()

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)


def wait_for_connection():
    """Wait for VictoriaMetrics."""
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"
    logger.info(f"Connecting to VictoriaMetrics at {METRICS_URL}...")
    while True:
        try:
            response = requests.get(query_url, params={"query": "up"}, timeout=5)
            if response.status_code == 200:
                logger.info("Connected.")
                return
        except Exception:
            pass
        time.sleep(5)


def main():
    logger.info("=" * 60)
    logger.info("Starting IDM ML Service (Multi-Heatpump)")
    logger.info("=" * 60)

    load_model_state()
    wait_for_connection()

    logger.info("Starting health check server...")
    threading.Thread(
        target=lambda: health_app.run(host="0.0.0.0", port=8080, debug=False),
        daemon=True,
    ).start()

    logger.info("Running initial processing...")
    job()

    schedule.every(UPDATE_INTERVAL).seconds.do(job)
    schedule.every(MODEL_SAVE_INTERVAL).seconds.do(save_model_state)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        save_model_state()
        logger.info("Stopped")


if __name__ == "__main__":
    main()
