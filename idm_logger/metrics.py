# SPDX-License-Identifier: MIT
"""
Metrics writer for VictoriaMetrics time-series database.

Supports multi-heatpump labeling with heatpump_id, manufacturer, and model tags.

Metric format:
    idm_heatpump_<sensor_name>{heatpump_id="hp-001",manufacturer="idm",model="navigator_2_0"} <value>

For backwards compatibility, metrics without labels are also supported.
"""

import logging
import requests
import os
import queue
import threading
import time
import re
from typing import Any, Dict, List, Optional, Union
from .config import config

logger = logging.getLogger(__name__)

# Valid characters for metric names and labels
METRIC_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class MetricsWriter:
    def __init__(self):
        self.url = os.environ.get(
            "METRICS_URL",
            config.get("metrics.url", "http://victoriametrics:8428/write"),
        )
        self._connected = True  # HTTP is stateless
        self.session = requests.Session()

        # Async queue for metrics to avoid blocking main loop
        self.queue = queue.Queue(maxsize=1000)
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        logger.info(f"MetricsWriter initialized with URL: {self.url} (Async)")

    def is_connected(self) -> bool:
        return self._connected

    def write(self, measurements: dict) -> bool:
        if not measurements:
            return True

        try:
            self.queue.put_nowait(measurements)
            return True
        except queue.Full:
            logger.warning("Metrics queue full, dropping data")
            return False

    def _worker(self):
        """Worker thread to process metrics queue with batching."""
        batch = []
        last_send = time.time()
        BATCH_SIZE = 50
        BATCH_TIMEOUT = 1.0

        while not self.stop_event.is_set():
            try:
                # Calculate timeout dynamically
                now = time.time()
                if batch:
                    # If we have items, wait only the remaining time of the 1s window
                    timeout = max(0, BATCH_TIMEOUT - (now - last_send))
                else:
                    # If empty, wait up to 1s (or until an item arrives)
                    timeout = 1.0

                measurements = self.queue.get(timeout=timeout)
                batch.append(measurements)
                self.queue.task_done()

                # If batch is full, send immediately
                if len(batch) >= BATCH_SIZE:
                    self._send_data(batch)
                    batch = []
                    last_send = time.time()

            except queue.Empty:
                # Timeout expired (or queue empty for >1s)
                # If we have data pending, send it now
                if batch:
                    self._send_data(batch)
                    batch = []
                    last_send = time.time()
                continue
            except Exception as e:
                logger.error(f"Error in metrics worker: {e}")
                # Try to flush what we have if possible, otherwise drop
                if batch:
                    try:
                        self._send_data(batch)
                    except Exception:
                        pass
                    batch = []

        # Flush remaining items on exit
        if batch:
            try:
                self._send_data(batch)
            except Exception as e:
                logger.error(f"Error flushing metrics on exit: {e}")

    def write_heatpump(
        self,
        heatpump_id: str,
        manufacturer: str,
        model: str,
        measurements: Dict[str, Any],
        heatpump_name: Optional[str] = None,
    ) -> bool:
        """
        Write metrics for a specific heatpump with labels.

        Args:
            heatpump_id: Unique heatpump identifier
            manufacturer: Manufacturer ID (e.g., "idm")
            model: Model ID (e.g., "navigator_2_0")
            measurements: Dict of sensor_id -> value
            heatpump_name: Optional display name

        Returns:
            True if queued successfully
        """
        if not measurements:
            return True

        # Wrap measurements with metadata
        labeled_data = {
            "_heatpump_id": heatpump_id,
            "_manufacturer": manufacturer,
            "_model": model,
            "_name": heatpump_name or heatpump_id,
            **measurements,
        }

        try:
            self.queue.put_nowait(labeled_data)
            return True
        except queue.Full:
            logger.warning(f"Metrics queue full for {heatpump_id}, dropping data")
            return False

    def write_all_heatpumps(
        self, all_values: Dict[str, Dict[str, Any]], configs: Dict[str, dict]
    ) -> bool:
        """
        Write metrics for all heatpumps at once.

        Args:
            all_values: Dict mapping heatpump_id to sensor values
            configs: Dict mapping heatpump_id to config

        Returns:
            True if all queued successfully
        """
        success = True
        for hp_id, values in all_values.items():
            hp_config = configs.get(hp_id, {})
            result = self.write_heatpump(
                heatpump_id=hp_id,
                manufacturer=hp_config.get("manufacturer", "unknown"),
                model=hp_config.get("model", "unknown"),
                measurements=values,
                heatpump_name=hp_config.get("name"),
            )
            if not result:
                success = False
        return success

    def _send_data(self, data: Union[Dict, List[Dict]]) -> bool:
        """Internal method to send data to VictoriaMetrics (executed in worker thread)."""
        # data can be a single dict (legacy call) or a list of dicts (batch)

        items = data if isinstance(data, list) else [data]
        lines = []

        for measurements in items:
            # Check for heatpump metadata (new format)
            heatpump_id = measurements.pop("_heatpump_id", None)
            manufacturer = measurements.pop("_manufacturer", None)
            model = measurements.pop("_model", None)
            hp_name = measurements.pop("_name", None)

            # Build labels if we have metadata
            if heatpump_id:
                labels = self._build_labels(heatpump_id, manufacturer, model, hp_name)
            else:
                labels = ""

            for key, value in measurements.items():
                # Skip string representation fields
                if key.endswith("_str"):
                    continue

                # Handle dict values (enum with value/text)
                if isinstance(value, dict):
                    value = value.get("value", 0)

                # Convert booleans to int
                if isinstance(value, bool):
                    value = int(value)

                # Only write numeric values
                if isinstance(value, (int, float)):
                    # Sanitize metric name
                    metric_name = self._sanitize_metric_name(key)
                    full_name = f"idm_heatpump_{metric_name}"

                    # InfluxDB line protocol format: name{labels} value [timestamp]
                    if labels:
                        lines.append(f"{full_name}{labels} {value}")
                    else:
                        # Legacy format without labels
                        lines.append(f"idm_heatpump {key}={value}")

        if not lines:
            return False

        payload = "\n".join(lines)

        try:
            # VictoriaMetrics /write endpoint
            response = self.session.post(self.url, data=payload, timeout=5)
            if response.status_code in (200, 204):
                return True
            else:
                logger.error(
                    f"Failed to write metrics: {response.status_code} {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Exception writing metrics: {e}")
            return False

    def _build_labels(
        self,
        heatpump_id: str,
        manufacturer: Optional[str],
        model: Optional[str],
        name: Optional[str],
    ) -> str:
        """Build label string for metrics."""
        labels = [f'heatpump_id="{self._escape_label(heatpump_id)}"']

        if manufacturer:
            labels.append(f'manufacturer="{self._escape_label(manufacturer)}"')
        if model:
            labels.append(f'model="{self._escape_label(model)}"')
        if name:
            labels.append(f'name="{self._escape_label(name)}"')

        return "{" + ",".join(labels) + "}"

    def _sanitize_metric_name(self, name: str) -> str:
        """Sanitize a metric name to be valid."""
        # Replace invalid characters with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        # Ensure starts with letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = "_" + sanitized
        return sanitized

    def _escape_label(self, value: str) -> str:
        """Escape special characters in label values."""
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    def get_status(self) -> dict:
        return {
            "connected": self._connected,
            "type": "VictoriaMetrics",
            "url": self.url,
            "queue_size": self.queue.qsize(),
        }

    def stop(self):
        """Stop the worker thread."""
        self.stop_event.set()
        self.worker_thread.join(timeout=2.0)
