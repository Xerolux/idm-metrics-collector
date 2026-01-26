# SPDX-License-Identifier: MIT
import logging
import requests
import threading
import time
import os
from .config import config
from .update_manager import get_current_version

logger = logging.getLogger(__name__)

# Default telemetry endpoint
DEFAULT_ENDPOINT = "https://collector.xerolux.de/api/v1/submit"


class TelemetryManager:
    def __init__(self, config_instance):
        self.config = config_instance
        # Always prefer Environment Variable, but allow user to use default if not set
        # The user SHOULD set TELEMETRY_ENDPOINT in docker-compose
        self.endpoint = os.environ.get("TELEMETRY_ENDPOINT", DEFAULT_ENDPOINT)
        self._buffer = []
        self._lock = threading.Lock()
        self._last_send = 0
        self._send_interval = 300  # Send every 5 minutes to avoid spamming
        self._worker_thread = None
        self._running = False

    def start(self):
        """Start the background worker."""
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        logger.info("Telemetry manager started")

    def stop(self):
        """Stop the background worker."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=2)

    def submit_data(self, sensor_data):
        """Submit sensor data to be sent."""
        if not self.config.get("share_data", True):
            return

        # Basic filtering or processing could go here
        # We only want to send if we have a model selected
        if not self.config.get("heatpump_model"):
            return

        with self._lock:
            # Add timestamp if not present
            if "timestamp" not in sensor_data:
                sensor_data["timestamp"] = time.time()
            self._buffer.append(sensor_data)

    def _worker_loop(self):
        while self._running:
            time.sleep(10)  # Check every 10 seconds

            if not self.config.get("share_data", True):
                with self._lock:
                    self._buffer.clear()  # Clear buffer if sharing is disabled
                continue

            now = time.time()
            if now - self._last_send >= self._send_interval:
                self._flush_buffer()

    def _flush_buffer(self):
        with self._lock:
            if not self._buffer:
                return
            data_to_send = list(self._buffer)
            self._buffer.clear()

        try:
            payload = {
                "installation_id": self.config.get("installation_id"),
                "heatpump_model": self.config.get("heatpump_model"),
                "version": get_current_version(),
                "data": data_to_send,
            }

            # Use a short timeout to not block anything
            # In a real scenario, we might want to retry, but for telemetry fire-and-forget is often okay
            # or we handle retries more robustly.

            # Check for legacy dummy endpoint to avoid spamming
            if "example.com" in self.endpoint:
                logger.debug(
                    f"Telemetry (Simulation): Would send {len(data_to_send)} records to {self.endpoint}"
                )
            else:
                # Add Authorization Header if token is configured
                headers = {}
                token = self.config.get("telemetry_auth_token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"

                response = requests.post(
                    self.endpoint, json=payload, headers=headers, timeout=10
                )

                if response.status_code == 200:
                    logger.debug(
                        f"Telemetry sent successfully: {len(data_to_send)} records"
                    )
                else:
                    logger.warning(f"Telemetry send failed: {response.status_code}")

            self._last_send = time.time()

        except Exception as e:
            logger.error(f"Error sending telemetry: {e}")


# Global instance
telemetry_manager = TelemetryManager(config)
