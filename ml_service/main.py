import os
import time
import logging
import requests
import schedule
from river import anomaly
from river import preprocessing
from river import compose

# Configuration
# Default to "http://victoriametrics:8428"
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
    # Use /api/v1/query (Prometheus API) to fetch instant values
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

def write_anomaly_score(score: float, is_anomaly: bool):
    """
    Write the anomaly score back to VictoriaMetrics via InfluxDB line protocol.
    """
    # Use /write for InfluxDB line protocol
    write_url = f"{METRICS_URL.rstrip('/')}/write"

    lines = [
        f"idm_anomaly_score value={score}",
        f"idm_anomaly_flag value={1 if is_anomaly else 0}"
    ]

    data = "\n".join(lines)

    try:
        response = requests.post(write_url, data=data, timeout=5)
        if response.status_code not in (200, 204):
            logger.error(f"Failed to write metrics to {write_url}: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Exception writing metrics: {e}")

def job():
    """
    Main job loop.
    """
    try:
        data = fetch_latest_data()

        if not data:
            logger.debug("No data fetched. Waiting for next cycle.")
            return

        if len(data) < len(SENSORS) / 2:
            logger.warning(f"Insufficient data fetched ({len(data)}/{len(SENSORS)} sensors). Skipping step.")
            return

        # Update model
        score = model.score_one(data)
        model.learn_one(data)

        # Determine anomaly flag
        is_anomaly = score > 0.7

        logger.info(f"Score: {score:.4f} | Anomaly: {is_anomaly} | Features: {len(data)}")

        write_anomaly_score(score, is_anomaly)

    except Exception as e:
        logger.error(f"Job failed: {e}")

def wait_for_connection():
    """
    Wait for VictoriaMetrics to be reachable.
    """
    # Check both query and write endpoints
    query_url = f"{METRICS_URL.rstrip('/')}/api/v1/query"

    logger.info(f"Attempting to connect to VictoriaMetrics at {METRICS_URL}...")

    while True:
        try:
            # Simple health check query
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
    logger.info("Starting IDM ML Service (River/HalfSpaceTrees)...")
    logger.info(f"Python 3.12 | typing_extensions verified")
    logger.info(f"Targeting Metrics URL: {METRICS_URL}")
    logger.info(f"Monitoring {len(SENSORS)} sensors.")

    # Wait for DB connection before starting schedule
    wait_for_connection()

    # Run once immediately
    job()

    # Schedule
    schedule.every(UPDATE_INTERVAL).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
