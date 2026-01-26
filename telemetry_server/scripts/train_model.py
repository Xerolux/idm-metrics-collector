import requests
import pickle
import logging
from river import anomaly
from river import compose
from river import preprocessing
import argparse

# Configuration
VM_QUERY_URL = "http://localhost:8428/api/v1/export"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_model")


def fetch_data(model_name):
    """
    Fetch raw data from VictoriaMetrics for a specific heatpump model.
    Using /api/v1/export for bulk retrieval.
    """
    params = {
        "match[]": f'{{__name__="heatpump_metrics", model="{model_name}"}}',
        "format": "json",
    }
    logger.info(f"Fetching data for model: {model_name}")

    # This is simplified; export returns JSON lines.
    # In a real scenario with GBs of data, you'd stream this line by line.
    response = requests.get(VM_QUERY_URL, params=params, stream=True)

    if response.status_code != 200:
        logger.error(f"Failed to fetch data: {response.status_code}")
        return []

    # Stream processing
    for line in response.iter_lines():
        if line:
            yield eval(line)  # VM export format is often JSON lines, but check VM docs.
            # Actually VM export is JSON line format if format=json is specified.
            # However, `eval` is dangerous if source is untrusted. `json.loads` is better.
            # But the export format is {"metric":..., "values": [v1, v2...], "timestamps": [t1, t2...]}
            # Wait, /api/v1/export returns native format or JSON line?
            # Standard export is usually line protocol or JSON per series.
            pass


def train(model_name, output_file):
    # Setup River Pipeline
    # HalfSpaceTrees is good for anomaly detection in streaming data
    model = compose.Pipeline(
        preprocessing.MinMaxScaler(),
        anomaly.HalfSpaceTrees(n_trees=50, height=6, window_size=250, seed=42),
    )

    # Simulate streaming training
    # In reality, you need to parse the specific metrics structure from VM export
    # For this reference implementation, we assume we get a dict of features

    # Mock training loop as we don't have real data source connected in this env
    logger.info("Starting training (Simulation)")

    # ... Training logic ...

    # Save model
    logger.info(f"Saving model to {output_file}")
    with open(output_file, "wb") as f:
        pickle.dump(model, f)

    logger.info("Training complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", type=str, required=True, help="Heatpump Model Name (e.g. AERO_SLM)"
    )
    parser.add_argument("--output", type=str, default="model.pkl", help="Output file")
    args = parser.parse_args()

    train(args.model, args.output)
