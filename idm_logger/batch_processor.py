# Xerolux 2026
# SPDX-License-Identifier: MIT
import json
import logging
from typing import Dict, List, Any, Iterator
from dataclasses import dataclass

from .telemetry_config import batch_config

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    success_count: int
    total_batches: int
    failed: bool = False
    error_message: str = ""


class DataBatcher:
    """Handles batching of telemetry data for submission."""

    def __init__(
        self,
        max_payload_mb: float = None,
        max_batch_size: int = None,
        min_batch_size: int = None,
    ):
        self.max_payload_mb = max_payload_mb or batch_config.max_payload_mb
        self.max_batch_size = max_batch_size or batch_config.max_batch_size
        self.min_batch_size = min_batch_size or batch_config.min_batch_size

    def calculate_optimal_batch_size(self, sample_data: List[Dict[str, Any]]) -> int:
        """Calculate optimal batch size based on sample data."""
        if not sample_data:
            return self.min_batch_size

        sample_size = min(10, len(sample_data))
        sample_json = json.dumps(sample_data[:sample_size])
        avg_record_bytes = len(sample_json.encode("utf-8")) / sample_size

        max_bytes = (self.max_payload_mb * 1024 * 1024) - batch_config.overhead_bytes
        optimal_batch = int(max_bytes / avg_record_bytes)

        return max(self.min_batch_size, min(self.max_batch_size, optimal_batch))

    def create_batches(
        self,
        data: List[Dict[str, Any]],
        batch_size: int = None,
    ) -> Iterator[List[Dict[str, Any]]]:
        """Create batches from data."""
        if not data:
            return

        size = batch_size or self.calculate_optimal_batch_size(data)

        for i in range(0, len(data), size):
            yield data[i : i + size]

    def prepare_submission_payload(
        self,
        batch: List[Dict[str, Any]],
        installation_id: str,
        hp_model: str,
        version: str,
    ) -> Dict[str, Any]:
        """Create a submission payload from a batch."""
        return {
            "installation_id": installation_id,
            "heatpump_model": hp_model,
            "version": version,
            "data": batch,
        }


class MetricsAggregator:
    """Aggregates metrics from VictoriaMetrics export format."""

    def __init__(self):
        self.measurements: Dict[int, Dict[str, Any]] = {}
        self._count: int = 0

    def add_record(self, record: Dict[str, Any]) -> None:
        """Add a record from VictoriaMetrics export."""
        metric_name = (
            record.get("metric", {}).get("__name__", "").replace("idm_heatpump_", "")
        )
        values = record.get("values", [])
        timestamps = record.get("timestamps", [])

        if not metric_name:
            return

        for t, v in zip(timestamps, values):
            ts_sec = t / 1000.0
            ts_key = int(ts_sec)

            if ts_key not in self.measurements:
                self.measurements[ts_key] = {"timestamp": ts_sec}

            self.measurements[ts_key][metric_name] = v
            self._count += 1

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert aggregated measurements to list."""
        return list(self.measurements.values())

    def count(self) -> int:
        """Return count of data points processed."""
        return self._count

    def clear(self) -> None:
        """Clear all aggregated data."""
        self.measurements.clear()
        self._count = 0
