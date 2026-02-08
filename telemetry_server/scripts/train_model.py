#!/usr/bin/env python3
# Xerolux 2026
"""
Community Model Training Script for IDM Telemetry Server.

This script fetches telemetry data from VictoriaMetrics and trains
a PyTorch Autoencoder anomaly detection model that can be distributed to
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
import os
import math
from datetime import datetime, timedelta
from typing import Generator, Dict, Any

import requests
import torch
import torch.nn as nn

# Configuration
VM_EXPORT_URL = os.environ.get("VM_EXPORT_URL", "http://localhost:8428/api/v1/export")
VM_QUERY_URL = os.environ.get(
    "VM_QUERY_URL", "http://localhost:8428/api/v1/query_range"
)

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

# Autoencoder hyperparameters
AE_HIDDEN_DIM = int(os.environ.get("AE_HIDDEN_DIM", "32"))
AE_LATENT_DIM = int(os.environ.get("AE_LATENT_DIM", "8"))
AE_LEARNING_RATE = float(os.environ.get("AE_LEARNING_RATE", "0.001"))
AE_EPOCHS = int(os.environ.get("AE_EPOCHS", "50"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("train_model")


class Autoencoder(nn.Module):
    """Simple feedforward autoencoder for anomaly detection."""

    def __init__(self, input_dim, hidden_dim=AE_HIDDEN_DIM, latent_dim=AE_LATENT_DIM):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


class OnlineStandardScaler:
    """Standard scaler for batch training data."""

    def __init__(self):
        self.n = 0
        self.means = {}
        self.m2 = {}
        self.vars = {}

    def partial_fit(self, data: dict):
        """Update running statistics with a single sample."""
        self.n += 1
        for key, value in data.items():
            if not isinstance(value, (int, float)):
                continue
            if key not in self.means:
                self.means[key] = 0.0
                self.m2[key] = 0.0
                self.vars[key] = 0.0
            delta = value - self.means[key]
            self.means[key] += delta / self.n
            delta2 = value - self.means[key]
            self.m2[key] += delta * delta2
            self.vars[key] = self.m2[key] / self.n if self.n > 1 else 0.0

    def transform(self, data: dict, feature_order: list) -> list:
        """Scale features using running stats."""
        result = []
        for key in feature_order:
            value = data.get(key, 0.0)
            if not isinstance(value, (int, float)):
                value = 0.0
            mean = self.means.get(key, 0.0)
            var = self.vars.get(key, 0.0)
            std = var**0.5
            if std > 1e-6:
                result.append((value - mean) / std)
            else:
                result.append(0.0)
        return result


class AutoencoderModel:
    """
    Wrapper providing streaming interface around PyTorch Autoencoder.
    Compatible with the ml_service runtime.
    """

    def __init__(
        self,
        hidden_dim=AE_HIDDEN_DIM,
        latent_dim=AE_LATENT_DIM,
        learning_rate=AE_LEARNING_RATE,
        train_steps=3,
        ema_alpha=0.01,
    ):
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.train_steps = train_steps
        self.ema_alpha = ema_alpha

        self.scaler = OnlineStandardScaler()
        self.feature_order = []
        self.net = None
        self.optimizer = None
        self.criterion = nn.MSELoss()
        self.ema_loss = None
        self.ema_loss_sq = None
        self.steps = {}

    def _ensure_net(self, input_dim):
        if self.net is None:
            self.net = Autoencoder(input_dim, self.hidden_dim, self.latent_dim)
            self.net.train()
            self.optimizer = torch.optim.Adam(
                self.net.parameters(), lr=self.learning_rate
            )

    def _prepare_input(self, data: dict) -> torch.Tensor:
        numeric_data = {
            k: v
            for k, v in data.items()
            if isinstance(v, (int, float))
            and not (isinstance(v, float) and math.isnan(v))
        }
        if not self.feature_order:
            self.feature_order = sorted(numeric_data.keys())
        scaled = self.scaler.transform(numeric_data, self.feature_order)
        return torch.tensor([scaled], dtype=torch.float32)

    def score_one(self, data: dict) -> float:
        if not self.feature_order:
            return 0.0
        self._ensure_net(len(self.feature_order))
        self.net.eval()
        with torch.no_grad():
            x = self._prepare_input(data)
            x_hat = self.net(x)
            mse = torch.mean((x - x_hat) ** 2).item()
        if self.ema_loss is None:
            return 0.0
        ema_var = self.ema_loss_sq - self.ema_loss**2
        ema_std = max(ema_var, 0.0) ** 0.5
        if ema_std < 1e-8:
            score = min(mse / (self.ema_loss + 1e-8), 1.0)
        else:
            z = (mse - self.ema_loss) / ema_std
            score = 1.0 / (1.0 + math.exp(-z))
        return float(score)

    def learn_one(self, data: dict):
        self.scaler.partial_fit(data)
        if not self.feature_order:
            numeric_data = {
                k: v
                for k, v in data.items()
                if isinstance(v, (int, float))
                and not (isinstance(v, float) and math.isnan(v))
            }
            self.feature_order = sorted(numeric_data.keys())
        self._ensure_net(len(self.feature_order))
        self.net.train()
        x = self._prepare_input(data)
        for _ in range(self.train_steps):
            self.optimizer.zero_grad()
            x_hat = self.net(x)
            loss = self.criterion(x_hat, x)
            loss.backward()
            self.optimizer.step()
        mse = loss.item()
        if self.ema_loss is None:
            self.ema_loss = mse
            self.ema_loss_sq = mse**2
        else:
            self.ema_loss = (1 - self.ema_alpha) * self.ema_loss + self.ema_alpha * mse
            self.ema_loss_sq = (
                1 - self.ema_alpha
            ) * self.ema_loss_sq + self.ema_alpha * (mse**2)


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
        # Count data points (across all metrics for this model)
        safe_model = model_name.replace(" ", "_")
        query = f'count({{__name__=~"heatpump_metrics_.*", model="{safe_model}"}})'
        response = requests.get(
            VM_QUERY_URL.replace("query_range", "query"),
            params={"query": query},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["total_points"] = int(
                    float(data["data"]["result"][0]["value"][1])
                )

        # Count installations
        query = f'count(count by (installation_id) ({{__name__=~"heatpump_metrics_.*", model="{safe_model}"}}))'
        response = requests.get(
            VM_QUERY_URL.replace("query_range", "query"),
            params={"query": query},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["installations"] = int(
                    float(data["data"]["result"][0]["value"][1])
                )

        logger.info(
            f"Data stats for {model_name}: {stats['total_points']} points from {stats['installations']} installations"
        )

    except Exception as e:
        logger.error(f"Error fetching data stats: {e}")

    return stats


def stream_training_data(
    model_name: str, lookback_days: int = 30
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
        "match[]": f'{{__name__=~"heatpump_metrics_.*", model="{safe_model}"}}',
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
        for line in response.iter_lines():
            if not line:
                continue

            try:
                series = json.loads(line)
                metric_info = series.get("metric", {})
                values = series.get("values", [])
                timestamps = series.get("timestamps", [])

                # Extract field name from metric
                field_name = metric_info.get("__name__", "").replace(
                    "heatpump_metrics_", ""
                )

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
                            "installation_id": metric_info.get(
                                "installation_id", "unknown"
                            ),
                        }

            except json.JSONDecodeError:
                continue

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")


def aggregate_to_samples(
    data_stream: Generator[Dict[str, Any], None, None], window_seconds: int = 60
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
    Train a PyTorch Autoencoder anomaly detection model on community data.

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

    # Setup PyTorch Autoencoder model
    model = AutoencoderModel(
        hidden_dim=AE_HIDDEN_DIM,
        latent_dim=AE_LATENT_DIM,
        learning_rate=AE_LEARNING_RATE,
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
                # Learn from the sample
                model.learn_one(features)
                samples_processed += 1

                if samples_processed % 1000 == 0:
                    logger.info(f"Processed {samples_processed} samples...")

        except Exception as e:
            errors += 1
            if errors <= 10:
                logger.warning(f"Error processing sample: {e}")

    logger.info(
        f"Training complete. Processed {samples_processed} samples with {errors} errors."
    )

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
        "architecture": "pytorch_autoencoder",
        "hidden_dim": AE_HIDDEN_DIM,
        "latent_dim": AE_LATENT_DIM,
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
        help="Heat pump model name (e.g., 'AERO_SLM', 'Navigator_2.0')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="model.pkl",
        help="Output file path (default: model.pkl)",
    )
    parser.add_argument(
        "--min-points",
        type=int,
        default=DEFAULT_MIN_POINTS,
        help=f"Minimum data points required (default: {DEFAULT_MIN_POINTS})",
    )
    parser.add_argument(
        "--min-installations",
        type=int,
        default=DEFAULT_MIN_INSTALLATIONS,
        help=f"Minimum installations required (default: {DEFAULT_MIN_INSTALLATIONS})",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=30,
        help="Days of data to use for training (default: 30)",
    )
    parser.add_argument(
        "--vm-url",
        type=str,
        default="http://localhost:8428",
        help="VictoriaMetrics base URL",
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
