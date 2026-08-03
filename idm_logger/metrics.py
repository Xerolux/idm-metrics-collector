# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
import os
import queue
import threading
import time

import requests

from .config import config

logger = logging.getLogger(__name__)


class MetricsWriter:
    def __init__(self):
        self.url = os.environ.get(
            "METRICS_URL",
            config.get("metrics.url", "http://victoriametrics:8428/write"),
        )
        self._connected = True
        self.session = requests.Session()

        self.queue = queue.Queue(maxsize=2000)
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        self._cached_tags = None
        self._cached_tags_config = None

        logger.info(f"MetricsWriter initialized with URL: {self.url} (Async)")

    def _get_tags(self):
        current_config = (
            config.get("installation_id"),
            config.get("hp_model"),
            config.get("hp_manufacturer", "IDM"),
        )
        if self._cached_tags_config != current_config:
            inst_id = self._escape_tag(current_config[0])
            model = self._escape_tag(current_config[1])
            manufacturer = self._escape_tag(current_config[2])
            self._cached_tags = (
                f",installation_id={inst_id},model={model},manufacturer={manufacturer}"
            )
            self._cached_tags_config = current_config
        return self._cached_tags

    def is_connected(self) -> bool:
        return self._connected

    def write(self, measurements: dict) -> bool:
        if not measurements:
            return True

        try:
            self.queue.put_nowait(measurements)
            return True
        except queue.Full:
            try:
                self.queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.queue.put_nowait(measurements)
                logger.warning("Metrics queue full, dropped oldest item")
                return True
            except queue.Full:
                logger.warning("Metrics queue full after eviction, dropping data")
                return False

    def _worker(self):
        batch = []
        last_send = time.time()
        BATCH_SIZE = 50
        BATCH_TIMEOUT = 1.0
        MAX_RETRIES = 3
        RETRY_BASE_DELAY = 0.5

        while not self.stop_event.is_set():
            try:
                now = time.time()
                if batch:
                    timeout = max(0, BATCH_TIMEOUT - (now - last_send))
                else:
                    timeout = 1.0

                measurements = self.queue.get(timeout=timeout)
                if measurements is None:
                    self.queue.task_done()
                    break
                batch.append(measurements)
                self.queue.task_done()

                if len(batch) >= BATCH_SIZE:
                    self._send_with_retry(batch, MAX_RETRIES, RETRY_BASE_DELAY)
                    batch = []
                    last_send = time.time()

            except queue.Empty:
                if batch:
                    self._send_with_retry(batch, MAX_RETRIES, RETRY_BASE_DELAY)
                    batch = []
                    last_send = time.time()
                continue
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error in metrics worker: {e}")
                if batch:
                    try:
                        self._send_with_retry(batch, MAX_RETRIES, RETRY_BASE_DELAY)
                    except Exception as e:  # noqa: BLE001
                        logger.warning(
                            f"Error flushing metrics after worker error: {e}"
                        )
                    batch = []

        if batch:
            try:
                self._send_with_retry(batch, MAX_RETRIES, RETRY_BASE_DELAY)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error flushing metrics on exit: {e}")

    def _send_with_retry(self, data, max_retries=3, base_delay=0.5):
        for attempt in range(max_retries):
            if self._send_data(data):
                return True
            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt)
                logger.debug(
                    f"Metrics send retry {attempt + 1}/{max_retries} in {delay:.1f}s"
                )
                time.sleep(delay)
        logger.error(f"Failed to send metrics after {max_retries} attempts")
        return False

    def _escape_tag(self, value):
        if not value:
            return "unknown"
        s = str(value)
        s = s.replace("\\", "\\\\").replace("\n", "\\n")
        s = s.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")
        return s

    def _send_data(self, data: dict | list[dict]) -> bool:
        items = data if isinstance(data, list) else [data]
        lines = []

        # ⚡ Bolt: Pre-calculate common string prefix outside the loop
        prefix = f"idm_heatpump{self._get_tags()} "

        # ⚡ Bolt: Memoize key formatting to avoid redundant string allocations
        key_cache = getattr(self, "_key_cache", {})

        for measurements in items:
            fields = []

            for key, value in measurements.items():
                if key.endswith("_str"):
                    continue

                # Bolt: convert bools to 1/0, format others as strings. Keep isinstance for robustness against sub-types
                if isinstance(value, bool):
                    val_str = "1" if value else "0"
                elif isinstance(value, (int, float)):
                    val_str = str(value)
                else:
                    continue

                # Use cache for key string to avoid repeated allocations
                if key not in key_cache:
                    key_cache[key] = f"{key}="
                fields.append(f"{key_cache[key]}{val_str}")

            if fields:
                field_str = ",".join(fields)
                lines.append(prefix + field_str)

        self._key_cache = key_cache

        if not lines:
            return False

        payload = "\n".join(lines)

        try:
            url = str(self.url)
            response = self.session.post(url, data=payload, timeout=5)
            if response.status_code in (200, 204):
                self._connected = True
                return True
            else:
                logger.error(
                    f"Failed to write metrics: {response.status_code} {response.text}"
                )
                self._connected = False
                return False
        except Exception as e:  # noqa: BLE001
            logger.error(f"Exception writing metrics: {e}")
            self._connected = False
            return False

    def get_status(self) -> dict:
        return {
            "connected": self._connected,
            "type": "VictoriaMetrics",
            "url": self.url,
            "queue_size": self.queue.qsize(),
        }

    def stop(self):
        self.stop_event.set()
        try:
            self.queue.put_nowait(None)
        except queue.Full:
            pass
        self.worker_thread.join(timeout=10.0)
        if self.worker_thread.is_alive():
            logger.warning(
                "Metrics worker thread did not stop gracefully, some data may be lost"
            )
        self.session.close()
