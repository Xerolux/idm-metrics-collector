import os
import time
import logging
import requests
import schedule
from river import anomaly
from river import preprocessing
from river import compose

# Configuration
METRICS_URL = os.environ.get("METRICS_URL", "http://victoriametrics:8428")
MEASUREMENT_NAME = os.environ.get("MEASUREMENT_NAME", "idm_heatpump")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 60))

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ml-service")

# Selected Sensors (MVP)
SENSORS = [
    "temp_flow_current_circuit_a",
    "temp_heat_pump_return",
    "power_current",
    "temp_water_heater_top",
    "temp_outside",
    "temp_heat_storage",
    "temp_cold_storage",
    "state_compressor_1"
]

# Initialize River Model
# StandardScaler to normalize features + HalfSpaceTrees for anomaly detection
model = compose.Pipeline(
    preprocessing.StandardScaler(),
    anomaly.HalfSpaceTrees(
        n_trees=25,
        height=15,
        window_size=250,
        seed=42
    )
)

def fetch_latest_data():
    """
    Fetch the latest values for the selected sensors from VictoriaMetrics.
    """
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"
    data_point = {}

    # We need to query each sensor or use a regex selector if possible.
    # To be robust, we query the last value for each sensor.
    # A single query like '{__name__=~"idm_heatpump_.*"}' could work, but let's be specific.

    # Construct a query that selects our specific metrics
    # VM supports PromQL. Metric names are typically "idm_heatpump_{sensor_name}"
    # We can try to fetch them all in one go using a regex match on __name__ if we know the prefix.
    # query: {__name__=~"idm_heatpump_.*"}

    # However, to filter exactly our SENSORS list:
    regex = "|".join([f"{MEASUREMENT_NAME}_{s}" for s in SENSORS])
    query = f"{{__name__=~\"{regex}\"}}"

    try:
        response = requests.get(query_url, params={"query": query}, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to fetch data: {response.status_code} {response.text}")
            return None

        json_data = response.json()
        if json_data.get("status") != "success":
            logger.error(f"Query failed: {json_data}")
            return None

        results = json_data.get("data", {}).get("result", [])

        for result in results:
            metric_name = result["metric"].get("__name__", "")
            # Extract sensor name by removing prefix
            sensor_name = metric_name.replace(f"{MEASUREMENT_NAME}_", "")

            # Get the value (last element of value array is timestamp, value)
            # PromQL instant query returns [timestamp, "value"]
            if "value" in result:
                val = result["value"][1]
                try:
                    data_point[sensor_name] = float(val)
                except (ValueError, TypeError):
                    pass

        return data_point

    except Exception as e:
        logger.error(f"Exception fetching data: {e}")
        return None

def write_anomaly_score(score: float, is_anomaly: bool):
    """
    Write the anomaly score back to VictoriaMetrics via InfluxDB line protocol.
    """
    write_url = f"{METRICS_URL.rstrip('/')}/write"

    # Line protocol: measurement field=value
    # idm_anomaly_score value=0.123
    # idm_anomaly_flag value=0

    lines = [
        f"idm_anomaly_score value={score}",
        f"idm_anomaly_flag value={1 if is_anomaly else 0}"
    ]

    data = "\n".join(lines)

    try:
        response = requests.post(write_url, data=data, timeout=5)
        if response.status_code not in (200, 204):
            logger.error(f"Failed to write metrics: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Exception writing metrics: {e}")

def job():
    """
    Main job loop.
    """
    try:
        data = fetch_latest_data()

        # We need a complete vector?
        # River handles missing data reasonably well in some models, but StandardScaler might complain if features change.
        # Ideally we want all sensors. If some are missing, we might skip or impute.
        # For MVP, let's just proceed with what we have if we have at least >50% of sensors.

        if not data or len(data) < len(SENSORS) / 2:
            logger.warning(f"Insufficient data fetched ({len(data) if data else 0}/{len(SENSORS)} sensors). Skipping step.")
            return

        # Score first, then learn
        score = model.score_one(data)
        model.learn_one(data)

        # Threshold for flag (simple static threshold for now, usually 0.5 - 1.0 for HST)
        # HST score is between 0 and 1.
        # 0.5 is a common starting threshold, but user suggested user-defined alerting in Grafana.
        # We'll just output the flag based on a reasonable default (e.g., > 0.7).
        is_anomaly = score > 0.7

        logger.info(f"Score: {score:.4f} | Anomaly: {is_anomaly} | Features: {len(data)}")

        write_anomaly_score(score, is_anomaly)

    except Exception as e:
        logger.error(f"Job failed: {e}")

def main():
    logger.info("Starting IDM ML Service (River/HalfSpaceTrees)...")
    logger.info(f"Monitoring {len(SENSORS)} sensors.")

    # Run once immediately
    job()

    # Schedule
    schedule.every(UPDATE_INTERVAL).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
