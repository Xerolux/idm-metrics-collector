import os
import time
import logging
import requests
import schedule
import pickle
import threading
from datetime import datetime
from river import anomaly
from river import preprocessing
from river import compose
from flask import Flask, jsonify
import sys

# Add parent directory to path to import idm_logger modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from idm_logger.sensor_addresses import (
    COMMON_SENSORS,
    BINARY_SENSOR_ADDRESSES,
    heating_circuit_sensors,
    zone_sensors,
    HeatingCircuit,
)

# Configuration
METRICS_URL = os.environ.get("METRICS_URL", "http://victoriametrics:8428")
MEASUREMENT_NAME = os.environ.get("MEASUREMENT_NAME", "idm_heatpump")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 30))

# ML Configuration
ANOMALY_THRESHOLD = float(os.environ.get("ANOMALY_THRESHOLD", "0.7"))
MIN_DATA_RATIO = float(os.environ.get("MIN_DATA_RATIO", "0.8"))
MODEL_N_TREES = int(os.environ.get("MODEL_N_TREES", "25"))
MODEL_HEIGHT = int(os.environ.get("MODEL_HEIGHT", "15"))
MODEL_WINDOW_SIZE = int(os.environ.get("MODEL_WINDOW_SIZE", "250"))
MODEL_SAVE_INTERVAL = int(os.environ.get("MODEL_SAVE_INTERVAL", "300"))  # Save every 5 minutes
MODEL_PATH = os.environ.get("MODEL_PATH", "/app/data/model_state.pkl")
ENABLE_ALERTS = os.environ.get("ENABLE_ALERTS", "true").lower() == "true"
ALERT_COOLDOWN = int(os.environ.get("ALERT_COOLDOWN", "3600"))  # 1 hour between alerts
IDM_LOGGER_URL = os.environ.get("IDM_LOGGER_URL", "http://idm-logger:5000")

# Circuit and Zone configuration
ML_CIRCUITS = os.environ.get("ML_CIRCUITS", "A").split(",")
ML_ZONES = [int(z.strip()) for z in os.environ.get("ML_ZONES", "").split(",") if z.strip()]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ml-service")

# Global state
start_time = time.time()
last_score = 0.0
model_trained = False
last_alert_time = 0
update_counter = 0
last_model_save = time.time()

# Flask health check app
health_app = Flask(__name__)

@health_app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "model_state": "trained" if model_trained else "learning",
        "last_score": last_score,
        "features_count": len(get_all_readable_sensors()),
        "uptime_seconds": int(time.time() - start_time),
        "update_interval": UPDATE_INTERVAL,
        "anomaly_threshold": ANOMALY_THRESHOLD,
        "updates_processed": update_counter
    }), 200

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

# Initialize River Model
logger.info(f"Initializing model with: n_trees={MODEL_N_TREES}, height={MODEL_HEIGHT}, window_size={MODEL_WINDOW_SIZE}")
model = compose.Pipeline(
    preprocessing.StandardScaler(),
    anomaly.HalfSpaceTrees(
        n_trees=MODEL_N_TREES,
        height=MODEL_HEIGHT,
        window_size=MODEL_WINDOW_SIZE,
        seed=42
    )
)

def save_model_state():
    """Save model state to disk for persistence across restarts."""
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Model state saved to {MODEL_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to save model state: {e}")
        return False

def load_model_state():
    """Load model state from disk if available."""
    global model, model_trained
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            model_trained = True
            logger.info(f"Model state loaded from {MODEL_PATH}")
            return True
        else:
            logger.info("No saved model state found, starting fresh")
            return False
    except Exception as e:
        logger.error(f"Failed to load model state: {e}")
        return False

def enrich_features(data: dict) -> dict:
    """Add temporal and computed features for better anomaly detection."""
    now = datetime.now()

    # Temporal features
    data['hour_of_day'] = now.hour
    data['day_of_week'] = now.weekday()
    data['is_weekend'] = 1 if now.weekday() >= 5 else 0

    # Computed features (if sensors available)
    try:
        # Temperature difference (common in heat pumps)
        if 'flow_temp' in data and 'return_temp' in data:
            data['temp_diff'] = data['flow_temp'] - data['return_temp']

        # Efficiency approximation
        if 'power_consumption' in data and 'heating_power' in data:
            if data['power_consumption'] > 0:
                data['efficiency'] = data['heating_power'] / data['power_consumption']
    except Exception as e:
        logger.debug(f"Feature engineering error: {e}")

    return data

def fetch_latest_data():
    """
    Fetch the latest values for the selected sensors from VictoriaMetrics.
    """
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"
    data_point = {}

    # Query regex to match all relevant metrics
    regex = "|".join([f"{MEASUREMENT_NAME}_{s}" for s in SENSORS])
    query = f"{{__name__=~\"{regex}\"}}"

    try:
        response = requests.get(query_url, params={"query": query}, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to fetch data from {query_url}: {response.status_code} {response.text}")
            return None

        json_data = response.json()
        if json_data.get("status") != "success":
            logger.error(f"Query returned error status: {json_data}")
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

        return data_point

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching data from {query_url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Exception fetching data: {e}")
        return None

def write_metrics(score: float, is_anomaly: bool, features_count: int, processing_time: float):
    """
    Write anomaly and ML performance metrics to VictoriaMetrics.
    """
    write_url = f"{METRICS_URL.rstrip('/')}/write"

    lines = [
        f"idm_anomaly_score value={score}",
        f"idm_anomaly_flag value={1 if is_anomaly else 0}",
        f"idm_ml_features_count value={features_count}",
        f"idm_ml_processing_time_ms value={processing_time * 1000}",
        f"idm_ml_model_updates value=1"  # Counter
    ]

    data = "\n".join(lines)

    try:
        response = requests.post(write_url, data=data, timeout=5)
        if response.status_code not in (200, 204):
            logger.error(f"Failed to write metrics to {write_url}: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Exception writing metrics: {e}")

def send_anomaly_alert(score: float, data: dict):
    """Send anomaly alert to IDM Logger notification system."""
    global last_alert_time

    if not ENABLE_ALERTS:
        return

    # Check cooldown
    if time.time() - last_alert_time < ALERT_COOLDOWN:
        logger.debug("Alert cooldown active, skipping notification")
        return

    try:
        alert_url = f"{IDM_LOGGER_URL}/api/internal/ml_alert"
        payload = {
            "type": "anomaly",
            "score": round(score, 4),
            "threshold": ANOMALY_THRESHOLD,
            "sensor_count": len(data),
            "timestamp": int(time.time()),
            "message": f"⚠️ Anomalie erkannt! Score: {score:.2f} (Schwellwert: {ANOMALY_THRESHOLD})"
        }

        response = requests.post(alert_url, json=payload, timeout=5)
        if response.status_code in (200, 201):
            logger.info(f"Anomaly alert sent successfully (score: {score:.4f})")
            last_alert_time = time.time()
        else:
            logger.warning(f"Alert endpoint returned {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send anomaly alert: {e}")

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
            logger.warning(f"Insufficient data fetched ({len(data)}/{len(SENSORS)} sensors, need {min_features}). Skipping.")
            return

        # Enrich with temporal and computed features
        data = enrich_features(data)

        # Update model
        score = model.score_one(data)
        model.learn_one(data)

        if not model_trained and update_counter > 10:
            model_trained = True
            logger.info("Model training phase completed")

        # Determine anomaly flag
        is_anomaly = score > ANOMALY_THRESHOLD

        processing_time = time.time() - start

        logger.info(f"Score: {score:.4f} | Anomaly: {is_anomaly} | Features: {len(data)} | Time: {processing_time*1000:.1f}ms")

        # Write metrics
        write_metrics(score, is_anomaly, len(data), processing_time)

        # Send alert if anomaly detected
        if is_anomaly and model_trained:
            send_anomaly_alert(score, data)

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
    """
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"

    logger.info(f"Attempting to connect to VictoriaMetrics at {METRICS_URL}...")

    while True:
        try:
            response = requests.get(query_url, params={"query": "up"}, timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to VictoriaMetrics.")
                return
            else:
                logger.warning(f"VictoriaMetrics reachable but returned {response.status_code}. Retrying in 5s...")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection refused to {METRICS_URL}. VictoriaMetrics might be starting up. Retrying in 5s...")
        except Exception as e:
            logger.error(f"Unexpected error connecting to {METRICS_URL}: {e}. Retrying in 5s...")

        time.sleep(5)

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
    logger.info(f"Model: n_trees={MODEL_N_TREES}, height={MODEL_HEIGHT}, window={MODEL_WINDOW_SIZE}")
    logger.info(f"Alerts: {'Enabled' if ENABLE_ALERTS else 'Disabled'}")
    logger.info("=" * 60)

    # Load model state if available
    load_model_state()

    # Wait for DB connection
    wait_for_connection()

    # Start health check server in background thread
    logger.info("Starting health check server on port 8080...")
    threading.Thread(target=lambda: health_app.run(host='0.0.0.0', port=8080, debug=False), daemon=True).start()

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
