# SPDX-License-Identifier: MIT
import logging
import requests
import threading
import time
import os
from pathlib import Path
from .config import config

logger = logging.getLogger(__name__)

# Use DATA_DIR environment variable or current directory
DATA_DIR = os.environ.get("DATA_DIR", ".")
MODEL_PATH = os.path.join(DATA_DIR, "community_model.enc")


class ModelUpdater:
    def __init__(self, config_instance):
        self.config = config_instance
        self._thread = None
        self._running = False
        self._check_interval = 24 * 3600  # Check every 24 hours
        self._last_check = 0

    def start(self):
        """Start the background updater."""
        if not self.config.get("share_data", True):
            logger.info("Data sharing disabled. Model updates disabled.")
            return

        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
        logger.info("Model updater started")

    def stop(self):
        """Stop the background updater."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _worker_loop(self):
        # Wait a bit after startup before first check
        time.sleep(60)

        while self._running:
            try:
                if self.config.get("share_data", True):
                    self._check_and_download()
            except Exception as e:
                logger.error(f"Model update check failed: {e}")

            # Sleep in chunks to allow stopping
            for _ in range(self._check_interval // 10):
                if not self._running:
                    break
                time.sleep(10)

    def trigger_check(self):
        """Manually trigger an update check."""
        threading.Thread(target=self._check_and_download, daemon=True).start()

    def _check_and_download(self):
        # Determine endpoint (production or dummy)
        # Using the same logic as TelemetryManager implicitly via config if we wanted,
        # but here we need to query the server URL.
        # We assume the default endpoint domain from TelemetryManager or similar.
        # Ideally this should be in config too.
        # For now, we derive it from the hardcoded default in telemetry.py or config if set.

        # NOTE: In a real implementation, the base URL should be centralized.
        # Assuming https://collector.xerolux.de based on previous steps.
        base_url = "https://collector.xerolux.de"

        # Override with env if set (for testing)
        if os.environ.get("TELEMETRY_ENDPOINT"):
            # telemetry endpoint is /api/v1/submit, we need base
            base_url = os.environ.get("TELEMETRY_ENDPOINT").rsplit("/api/", 1)[0]

        installation_id = self.config.get("installation_id")

        # 1. Check Eligibility
        check_url = f"{base_url}/api/v1/model/check"
        try:
            logger.debug(f"Checking model eligibility at {check_url}...")
            # Headers
            headers = {}
            token = self.config.get("telemetry_auth_token")
            if token:
                headers["Authorization"] = f"Bearer {token}"

            response = requests.get(
                check_url,
                params={"installation_id": installation_id},
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("eligible"):
                    # 2. Download Model if eligible
                    # TODO: In future, check version/hash to avoid redownloading same file
                    self._download_model(base_url, headers)
                else:
                    logger.info(
                        "Not eligible for community model updates yet (need more data contribution)."
                    )
            elif response.status_code == 404:
                # Endpoint might not exist on dummy server
                pass
            else:
                logger.warning(f"Model check returned {response.status_code}")

        except requests.RequestException as e:
            logger.warning(f"Could not contact model server: {e}")

    def _download_model(self, base_url, headers):
        download_url = f"{base_url}/api/v1/model/download"
        local_path = Path(MODEL_PATH)
        temp_path = local_path.with_suffix(".tmp")

        logger.info(f"Downloading community model from {download_url}...")
        try:
            with requests.get(
                download_url, headers=headers, stream=True, timeout=60
            ) as r:
                r.raise_for_status()
                with open(temp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Move into place (Atomic)
            if temp_path.exists() and temp_path.stat().st_size > 0:
                os.replace(temp_path, local_path)
                logger.info(f"Community model updated successfully: {local_path}")
            else:
                logger.error("Downloaded model file is empty")

        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            if temp_path.exists():
                os.remove(temp_path)


# Global instance
model_updater = ModelUpdater(config)
