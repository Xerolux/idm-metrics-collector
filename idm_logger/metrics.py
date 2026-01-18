# SPDX-License-Identifier: MIT
import logging
import requests
import os
import queue
import threading
import time
from typing import List
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

        # Add timestamp to measurements to preserve time when queuing
        # We use a copy to avoid modifying the passed dict which might be used elsewhere
        queued_measurements = measurements.copy()
        queued_measurements['_timestamp'] = time.time()

        try:
            self.queue.put_nowait(queued_measurements)
            return True
        except queue.Full:
            logger.warning("Metrics queue full, dropping data")
            return False

    def _worker(self):
        """Worker thread to process metrics queue."""
        while not self.stop_event.is_set():
            batch = []
            try:
                # Wait for data with timeout to allow checking stop_event
                # Block for up to 1s to get the first item
                item = self.queue.get(timeout=1.0)
                batch.append(item)

                # Try to get more items immediately to fill the batch
                # Limit batch size to avoid huge payloads (e.g., 50 items)
                while len(batch) < 50:
                    try:
                        item = self.queue.get_nowait()
                        batch.append(item)
                    except queue.Empty:
                        break
            except queue.Empty:
                continue

            try:
                self._send_data(batch)
            except Exception as e:
                logger.error(f"Error in metrics worker: {e}")
            finally:
                # Mark all tasks as done
                for _ in batch:
                    self.queue.task_done()

    def _send_data(self, batch: List[dict]) -> bool:
        """Internal method to send data to VictoriaMetrics (executed in worker thread)."""
        # Construct Line Protocol
        # measurement field1=val1,field2=val2 timestamp

        measurement = "idm_heatpump"
        lines = []

        for measurements in batch:
            fields = []
            timestamp = measurements.pop('_timestamp', None)

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
                line = f"{measurement} {field_str}"

                # Add timestamp if present (convert seconds to nanoseconds)
                if timestamp:
                    line += f" {int(timestamp * 1e9)}"

                lines.append(line)

        if not lines:
            return False

        payload = "\n".join(lines)

        try:
            # VictoriaMetrics /write endpoint
            # Use session for connection pooling
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

    def get_status(self) -> dict:
        return {
            "connected": self._connected,
            "type": "VictoriaMetrics",
            "url": self.url,
            "queue_size": self.queue.qsize()
        }

    def stop(self):
        """Stop the worker thread."""
        self.stop_event.set()
        self.worker_thread.join(timeout=2.0)
