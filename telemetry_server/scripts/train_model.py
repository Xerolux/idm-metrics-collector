#!/usr/bin/env python3
"""
Community Model Training Script for IDM Telemetry Server.

This script fetches telemetry data from VictoriaMetrics and trains
a River-based anomaly detection model that can be distributed to
eligible community members.

Usage:
    python train_model.py --model "AERO_SLM" --output model.pkl
    python train_model.py --model "AERO_SLM" --output model.pkl --min-points 5000
"""

import json
import pickle
import logging
import argparse
import sys
from datetime import datetime, timedelta
from typing import Generator, Dict, Any, Optional

import requests
from river import anomaly
from river import compose
from river import preprocessing

# Configuration
VM_EXPORT_URL = "http://localhost:8428/api/v1/export"
VM_QUERY_URL = "http://localhost:8428/api/v1/query_range"

# Minimum data requirements
DEFAULT_MIN_POINTS = 5000
DEFAULT_MIN_INSTALLATIONS = 3

# Features to use for training (common heat pump metrics)
TRAINING_FEATURES = [
    "temp_outdoor",
    "temp_flow",
    "temp_return",
    "temp_hot_water",
    "power_current",
    "power_compressor",
    "cop_current",
    "pressure_high",
    "pressure_low",
    "fan_speed",
    "compressor_frequency",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("train_model")


def fetch_data_stats(model_name: str) -> Dict[str, Any]:
    """
    Get statistics about available data for a model.
    """
    stats = {
        "total_points": 0,
        "installations": 0,
        "time_range_days": 0,
        "available_fields": set(),
    }

    try:
        # Count data points
        safe_model = model_name.replace(" ", "_")
        query = f'count(heatpump_metrics{{model="{safe_model}"}})'
        response = requests.get(
            VM_QUERY_URL.replace("query_range", "query"),
            params={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["total_points"] = int(float(data["data"]["result"][0]["value"][1]))

        # Count installations
        query = f'count(count by (installation_id) (heatpump_metrics{{model="{safe_model}"}}))'
        response = requests.get(
            VM_QUERY_URL.replace("query_range", "query"),
            params={"query": query},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["installations"] = int(float(data["data"]["result"][0]["value"][1]))

        logger.info(f"Data stats for {model_name}: {stats['total_points']} points from {stats['installations']} installations")

    except Exception as e:
        logger.error(f"Error fetching data stats: {e}")

    return stats


def stream_training_data(
    model_name: str,
    lookback_days: int = 30
) -> Generator[Dict[str, float], None, None]:
    """
    Stream training data from VictoriaMetrics.
    Uses the export API for efficient bulk retrieval.
    """
    safe_model = model_name.replace(" ", "_")
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=lookback_days)

    # Export format for VictoriaMetrics
    params = {
        "match[]": f'heatpump_metrics{{model="{safe_model}"}}',
        "start": int(start_time.timestamp()),
        "end": int(end_time.timestamp()),
    }

    logger.info(f"Fetching data from {start_time} to {end_time}")

    try:
        response = requests.get(VM_EXPORT_URL, params=params, stream=True, timeout=300)

        if response.status_code != 200:
            logger.error(f"Export failed: {response.status_code} - {response.text}")
            return

        # VictoriaMetrics export returns JSON lines
        # Each line is a series: {"metric": {...}, "values": [...], "timestamps": [...]}
        for line in response.iter_lines():
            if not line:
                continue

            try:
                series = json.loads(line)
                metric_info = series.get("metric", {})
                values = series.get("values", [])
                timestamps = series.get("timestamps", [])

                # Extract field name from metric
                field_name = metric_info.get("__name__", "").replace("heatpump_metrics_", "")

                # Skip if not a training feature
                if field_name not in TRAINING_FEATURES:
                    continue

                # Yield individual data points
                for val, ts in zip(values, timestamps):
                    if isinstance(val, (int, float)) and not (val != val):  # Skip NaN
                        yield {
                            "field": field_name,
                            "value": float(val),
                            "timestamp": ts,
                            "installation_id": metric_info.get("installation_id", "unknown"),
                        }

            except json.JSONDecodeError:
                continue

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")


def aggregate_to_samples(
    data_stream: Generator[Dict[str, Any], None, None],
    window_seconds: int = 60
) -> Generator[Dict[str, float], None, None]:
    """
    Aggregate streaming data points into feature vectors.
    Groups data by installation_id and time window.
    """
    current_window = {}
    current_window_start = None

    for point in data_stream:
        ts = point["timestamp"]
        window_start = (ts // window_seconds) * window_seconds

        if current_window_start is None:
            current_window_start = window_start

        # New window - yield previous if complete
        if window_start != current_window_start:
            if len(current_window) >= 3:  # Minimum features
                yield current_window
            current_window = {}
            current_window_start = window_start

        # Add to current window
        field = point["field"]
        current_window[field] = point["value"]

    # Yield final window
    if len(current_window) >= 3:
        yield current_window


def train_model(
    model_name: str,
    output_file: str,
    min_points: int = DEFAULT_MIN_POINTS,
    min_installations: int = DEFAULT_MIN_INSTALLATIONS,
    lookback_days: int = 30,
) -> bool:
    """
    Train a River anomaly detection model on community data.

    Returns True if training was successful.
    """
    logger.info(f"Starting training for model: {model_name}")

    # Check data availability
    stats = fetch_data_stats(model_name)

    if stats["total_points"] < min_points:
        logger.warning(
            f"Insufficient data: {stats['total_points']}/{min_points} points. "
            "Waiting for more contributions."
        )
        return False

    if stats["installations"] < min_installations:
        logger.warning(
            f"Insufficient installations: {stats['installations']}/{min_installations}. "
            "Need more diverse data sources."
        )
        return False

    # Setup River Pipeline
    # HalfSpaceTrees is good for anomaly detection in streaming data
    model = compose.Pipeline(
        preprocessing.MinMaxScaler(),
        anomaly.HalfSpaceTrees(
            n_trees=50,
            height=6,
            window_size=250,
            seed=42
        ),
    )

    # Training loop
    logger.info("Starting streaming training...")
    samples_processed = 0
    errors = 0

    data_stream = stream_training_data(model_name, lookback_days)
    sample_stream = aggregate_to_samples(data_stream)

    for sample in sample_stream:
        try:
            # Filter to only training features that exist
            features = {k: v for k, v in sample.items() if k in TRAINING_FEATURES}

            if len(features) >= 3:  # Minimum features required
                # Learn from the sample (anomaly score is computed internally)
                model.learn_one(features)
                samples_processed += 1

                if samples_processed % 1000 == 0:
                    logger.info(f"Processed {samples_processed} samples...")

        except Exception as e:
            errors += 1
            if errors <= 10:
                logger.warning(f"Error processing sample: {e}")

    logger.info(f"Training complete. Processed {samples_processed} samples with {errors} errors.")

    if samples_processed < 100:
        logger.error("Too few samples processed. Model may be unreliable.")
        return False

    # Save model
    logger.info(f"Saving model to {output_file}")
    with open(output_file, "wb") as f:
        pickle.dump(model, f)

    # Save metadata
    metadata = {
        "model_name": model_name,
        "trained_at": datetime.utcnow().isoformat(),
        "samples_processed": samples_processed,
        "data_points": stats["total_points"],
        "installations": stats["installations"],
        "lookback_days": lookback_days,
        "features": TRAINING_FEATURES,
    }
    metadata_file = output_file.replace(".pkl", "_metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Training complete. Metadata saved to {metadata_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Train community anomaly detection model"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Heat pump model name (e.g., 'AERO_SLM', 'Navigator_2.0')"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="model.pkl",
        help="Output file path (default: model.pkl)"
    )
    parser.add_argument(
        "--min-points",
        type=int,
        default=DEFAULT_MIN_POINTS,
        help=f"Minimum data points required (default: {DEFAULT_MIN_POINTS})"
    )
    parser.add_argument(
        "--min-installations",
        type=int,
        default=DEFAULT_MIN_INSTALLATIONS,
        help=f"Minimum installations required (default: {DEFAULT_MIN_INSTALLATIONS})"
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=30,
        help="Days of data to use for training (default: 30)"
    )
    parser.add_argument(
        "--vm-url",
        type=str,
        default="http://localhost:8428",
        help="VictoriaMetrics base URL"
    )

    args = parser.parse_args()

    # Override URLs if provided
    global VM_EXPORT_URL, VM_QUERY_URL
    VM_EXPORT_URL = f"{args.vm_url}/api/v1/export"
    VM_QUERY_URL = f"{args.vm_url}/api/v1/query_range"

    success = train_model(
        model_name=args.model,
        output_file=args.output,
        min_points=args.min_points,
        min_installations=args.min_installations,
        lookback_days=args.lookback_days,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
