# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
import requests
import os
import queue
import threading
import time
from typing import List, Union, Dict
from .config import config

logger = logging.getLogger(__name__)


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
                    except Exception as e:
                        logger.warning(
                            f"Error flushing metrics after worker error: {e}"
                        )
                    batch = []

        # Flush remaining items on exit
        if batch:
            try:
                self._send_data(batch)
            except Exception as e:
                logger.error(f"Error flushing metrics on exit: {e}")

    def _escape_tag(self, value):
        """Escape special characters for InfluxDB line protocol tags."""
        if not value:
            return "unknown"
        s = str(value)
        s = s.replace("\\", "\\\\").replace("\n", "\\n")
        s = s.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")
        return s

    def _send_data(self, data: Union[Dict, List[Dict]]) -> bool:
        """Internal method to send data to VictoriaMetrics (executed in worker thread)."""
        # data can be a single dict (legacy call) or a list of dicts (batch)

        items = data if isinstance(data, list) else [data]
        lines = []

        # Prepare tags from config
        inst_id = self._escape_tag(config.get("installation_id"))
        model = self._escape_tag(config.get("hp_model"))
        manufacturer = self._escape_tag(config.get("hp_manufacturer", "IDM"))

        tags = f",installation_id={inst_id},model={model},manufacturer={manufacturer}"

        for measurements in items:
            measurement_name = "idm_heatpump"
            fields = []

            for key, value in measurements.items():
                # Skip string representation fields
                if key.endswith("_str"):
                    continue
                # Convert booleans to int
                if isinstance(value, bool):
                    value = int(value)
                # Only write numeric values
                if isinstance(value, (int, float)):
                    fields.append(f"{key}={value}")

            if fields:
                field_str = ",".join(fields)
                # Timestamp is handled by VictoriaMetrics on ingestion
                lines.append(f"{measurement_name}{tags} {field_str}")

        if not lines:
            return False

        payload = "\n".join(lines)

        try:
            url = str(self.url)
            response = self.session.post(url, data=payload, timeout=5)
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

    def get_status(self) -> dict:
        return {
            "connected": self._connected,
            "type": "VictoriaMetrics",
            "url": self.url,
            "queue_size": self.queue.qsize(),
        }

    def stop(self):
        """Stop the worker thread and flush remaining data."""
        self.stop_event.set()
        self.worker_thread.join(timeout=10.0)
        if self.worker_thread.is_alive():
            logger.warning(
                "Metrics worker thread did not stop gracefully, some data may be lost"
            )
