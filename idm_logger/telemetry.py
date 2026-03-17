# Xerolux 2026
# SPDX-License-Identifier: MIT
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional

from .config import config
from .update_manager import get_current_version
from .telemetry_config import (
    telemetry_client_config,
)
from .http_client import HttpClient
from .batch_processor import DataBatcher, MetricsAggregator
from .model_downloader import (
    ModelDownloader,
    ModelCheckResult,
)

logger = logging.getLogger(__name__)


class TelemetryManager:
    """Manages telemetry submission and model downloads."""

    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        self.http_client = HttpClient()
        self.batcher = DataBatcher()
        self.model_downloader = ModelDownloader(self.http_client)

        self._load_state()

    def _load_state(self) -> None:
        """Load state from config."""
        telemetry_config = config.get("telemetry", {})

        self.manual_downloads_today = telemetry_config.get("manual_downloads_today", 0)
        self.last_manual_download = telemetry_config.get("last_manual_download", 0)
        self.is_admin = telemetry_config.get("is_admin", False)
        self.role = telemetry_config.get("role", "guest")
        self.is_banned = telemetry_config.get("is_banned", False)
        self.server_stats = telemetry_config.get("server_stats", None)

        self._reset_daily_counter_if_needed()

    def _reset_daily_counter_if_needed(self) -> None:
        """Reset counter if it's a new day."""
        if self.last_manual_download > 0:
            last_date = datetime.fromtimestamp(self.last_manual_download).date()
            if last_date < datetime.now().date():
                self.manual_downloads_today = 0
                self._save_state()

    def _save_state(self) -> None:
        """Save state to config."""
        config.set("telemetry.manual_downloads_today", self.manual_downloads_today)
        config.set("telemetry.last_manual_download", self.last_manual_download)
        config.set("telemetry.is_admin", self.is_admin)
        config.set("telemetry.role", self.role)
        config.set("telemetry.is_banned", self.is_banned)
        if self.server_stats:
            config.set("telemetry.server_stats", self.server_stats)
        config.save()

    def _get_auth_token(self) -> str:
        """Get auth token from config or use shared token."""
        token = config.get("telemetry.auth_token")
        return token or telemetry_client_config.get_shared_auth_token()

    def _get_encryption_key(self) -> bytes:
        """Get encryption key from config or use default."""
        key = config.get("telemetry.encryption_key")
        if not key:
            return telemetry_client_config.get_default_encryption_key()
        return key.encode("utf-8") if isinstance(key, str) else key

    def retrieve_credentials(self) -> bool:
        """
        Retrieve per-installation credentials from the server.
        Returns True if credentials are available.
        """
        existing_token = config.get("telemetry.auth_token")
        if (
            existing_token
            and existing_token != telemetry_client_config.get_shared_auth_token()
        ):
            logger.debug("Per-installation token already configured")
            return True

        installation_id = config.get("installation_id")
        if not installation_id:
            logger.warning("Cannot retrieve credentials: no installation_id configured")
            return False

        server_url = config.get(
            "telemetry.server_url", telemetry_client_config.server_url
        )

        try:
            logger.info("Retrieving per-installation credentials from server...")

            response = self.http_client.post(
                f"{server_url}/api/v1/credentials/retrieve",
                params={"installation_id": installation_id},
                headers={
                    "Authorization": f"Bearer {telemetry_client_config.get_shared_auth_token()}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                data = response.json()

                auth_token = data.get("auth_token")
                encryption_key = data.get("encryption_key")

                if auth_token:
                    config.set("telemetry.auth_token", auth_token)
                    logger.info("Per-installation auth token stored")

                if encryption_key:
                    config.set("telemetry.encryption_key", encryption_key)
                    logger.info("Per-installation encryption key stored")

                config.save()

                if data.get("is_new", True):
                    logger.info("New installation registered with telemetry server")
                else:
                    logger.info("Credentials retrieved for existing installation")

                return True

            logger.warning(f"Failed to retrieve credentials: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error retrieving credentials: {e}")
            return False

    def start(self, scheduler=None) -> None:
        """Start the telemetry manager."""
        if self.running:
            return

        self.running = True

        if config.get("telemetry.enabled", True):
            try:
                self.retrieve_credentials()
            except Exception as e:
                logger.debug(f"Credential retrieval skipped: {e}")

        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Telemetry Manager started")

    def _run_loop(self) -> None:
        """Internal loop to check for scheduled tasks."""
        import schedule

        schedule.every().day.at("02:00").do(self.submit_data_job)
        schedule.every().day.at("04:00").do(self.check_model_job)

        logger.info("Telemetry jobs scheduled")

        while self.running:
            try:
                schedule.run_pending()
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Telemetry loop error: {e}")
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)

    def stop(self) -> None:
        """Stop the telemetry manager."""
        self.running = False
        self.http_client.close()

    def get_status(self) -> Dict[str, Any]:
        """Return current telemetry status."""
        telemetry_config = config.get("telemetry", {})

        auth_token = telemetry_config.get("auth_token")
        has_per_installation_token = bool(
            auth_token and auth_token != telemetry_client_config.get_shared_auth_token()
        )

        return {
            "enabled": telemetry_config.get("enabled", True),
            "installation_id": config.get("installation_id"),
            "server_url": telemetry_config.get("server_url"),
            "last_submission": telemetry_config.get("last_submission"),
            "last_model_check": telemetry_config.get("last_model_check"),
            "manual_downloads_today": self.manual_downloads_today,
            "version": get_current_version(),
            "is_admin": self.is_admin,
            "role": self.role,
            "is_banned": self.is_banned,
            "server_stats": self.server_stats,
            "has_per_installation_token": has_per_installation_token,
            "has_encryption_key": bool(telemetry_config.get("encryption_key")),
        }

    def submit_data_job(self) -> None:
        """Scheduled job to submit data."""
        if not config.get("telemetry.enabled", True):
            return

        try:
            logger.info("Starting daily telemetry submission...")
            self.submit_data(hours=24)
        except Exception as e:
            logger.error(f"Telemetry submission job failed: {e}")

    def check_model_job(self) -> None:
        """Scheduled job to check and update model."""
        if not config.get("telemetry.enabled", True):
            return

        try:
            logger.info("Starting daily model update check...")
            self.download_and_install_model(manual=False)
        except Exception as e:
            logger.error(f"Model check job failed: {e}")

    def submit_data(self, hours: int = 24) -> bool:
        """Query VictoriaMetrics for data and submit to server."""
        server_url = config.get(
            "telemetry.server_url", telemetry_client_config.server_url
        )
        auth_token = self._get_auth_token()

        if not auth_token:
            logger.warning("Telemetry: No auth token configured. Skipping submission.")
            return False

        metrics_url = config.get("metrics.url", "http://victoriametrics:8428/write")
        base_url = metrics_url.replace("/write", "").replace("/api/v1/write", "")
        query_url = f"{base_url}/api/v1/export"

        end_ts = int(time.time())
        start_ts = end_ts - (hours * 3600)

        params = {
            "match[]": '{__name__=~"idm_heatpump_.*"}',
            "start": start_ts,
            "end": end_ts,
        }

        try:
            logger.debug(f"Querying metrics from {query_url}")
            response = self.http_client.get(
                query_url, params=params, stream=True, timeout=60
            )

            if response.status_code != 200:
                logger.error(f"Failed to query metrics: {response.status_code}")
                return False

            aggregator = MetricsAggregator()

            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    aggregator.add_record(record)
                except Exception:
                    continue

            payload_data = aggregator.to_list()

            logger.info(
                f"Processed {aggregator.count()} data points into {len(payload_data)} records."
            )

            if not payload_data:
                logger.warning("No data found to submit.")
                return False

            return self._submit_batches(server_url, auth_token, payload_data)

        except Exception as e:
            logger.error(f"Telemetry submission failed: {e}")
            return False

    def _submit_batches(
        self,
        server_url: str,
        auth_token: str,
        payload_data: list,
    ) -> bool:
        """Submit data in batches to the server."""
        batch_size = self.batcher.calculate_optimal_batch_size(payload_data)

        logger.info(
            f"Dynamic batch size: {batch_size} records, total records: {len(payload_data)}"
        )

        total_batches = (len(payload_data) + batch_size - 1) // batch_size
        success_count = 0
        current_token = auth_token

        for i, batch in enumerate(
            self.batcher.create_batches(payload_data, batch_size)
        ):
            payload = self.batcher.prepare_submission_payload(
                batch,
                config.get("installation_id"),
                config.get("hp_model", "Unknown"),
                get_current_version(),
            )

            headers = {
                "Authorization": f"Bearer {current_token}",
                "Content-Type": "application/json",
            }

            try:
                res = self.http_client.post(
                    f"{server_url}/api/v1/submit",
                    json=payload,
                    headers=headers,
                )

                if res.status_code in (200, 204):
                    success_count += 1
                elif res.status_code == 403:
                    logger.warning(
                        "Token expired or invalid (403). Attempting to refresh..."
                    )

                    config.set("telemetry.auth_token", None)

                    if self.retrieve_credentials():
                        new_token = config.get("telemetry.auth_token")
                        if new_token:
                            current_token = new_token
                            headers["Authorization"] = f"Bearer {new_token}"

                            retry_res = self.http_client.post(
                                f"{server_url}/api/v1/submit",
                                json=payload,
                                headers=headers,
                            )

                            if retry_res.status_code in (200, 204):
                                success_count += 1
                                logger.info("Batch retry successful with new token.")
                            else:
                                logger.error(
                                    f"Submit batch retry failed: {retry_res.status_code}"
                                )
                                return False
                    else:
                        logger.error(
                            "Failed to refresh credentials. Aborting submission."
                        )
                        return False
                else:
                    logger.error(
                        f"Submit batch {i + 1} failed: {res.status_code} - {res.text}"
                    )

            except Exception as e:
                logger.error(f"Submit batch {i + 1} error: {e}")

        if success_count == total_batches:
            config.set("telemetry.last_submission", int(time.time()))
            config.save()
            logger.info("Telemetry submission completed successfully.")
            return True
        else:
            logger.warning(
                f"Telemetry submission partially failed ({success_count}/{total_batches} batches)."
            )
            return False

    def download_and_install_model(self, manual: bool = False) -> bool:
        """Check for model update, download if available, install to ML service."""
        allowed, error_msg = self.model_downloader.check_rate_limit(manual)
        if not allowed:
            raise Exception(error_msg)

        self.model_downloader.reset_daily_counter()

        server_url = config.get(
            "telemetry.server_url", telemetry_client_config.server_url
        )
        installation_id = config.get("installation_id")
        hp_model = config.get("hp_model")

        check_result = self.model_downloader.check_model_availability(
            server_url, installation_id, hp_model
        )

        config.set("telemetry.last_model_check", int(time.time()))

        self._update_status_from_check(check_result)

        if not check_result.eligible:
            msg = check_result.reason_de or check_result.reason or "Nicht berechtigt"
            logger.info(f"Model check: Not eligible - {msg}")
            if manual:
                raise Exception(msg)
            return False

        if not check_result.model_available:
            msg = (
                check_result.reason_de or check_result.reason or "Kein Modell verfügbar"
            )
            logger.info(f"Model check: {msg}")
            if manual:
                raise Exception(msg)
            return False

        if not check_result.update_available and not manual:
            logger.info("Model check: No update needed.")
            return True

        auth_token = self._get_auth_token()
        encryption_key = self._get_encryption_key()

        envelope, raw_content, error = self.model_downloader.download_model(
            server_url, installation_id, hp_model, auth_token
        )

        if error:
            logger.error(f"Model download failed: {error}")
            if manual:
                raise Exception(error)
            return False

        if not envelope:
            logger.error("Model download failed: No envelope received")
            return False

        verify_result = self.model_downloader.verify_and_decrypt(
            envelope, encryption_key
        )

        if not verify_result.valid:
            error = verify_result.error_message
            logger.error(f"Model verification failed: {error}")
            if manual:
                raise Exception(error)
            return False

        internal_api_key = config.get("internal_api_key")
        upload_success, upload_error = self.model_downloader.upload_to_ml_service(
            verify_result.decrypted_data, internal_api_key
        )

        if upload_success:
            logger.info("Model installed successfully.")
            if manual:
                self.model_downloader.increment_download_count()
                self.manual_downloads_today = (
                    self.model_downloader._manual_downloads_today
                )
                self.last_manual_download = self.model_downloader._last_manual_download
                self._save_state()
            return True
        else:
            if manual:
                raise Exception(upload_error)
            return False

    def _update_status_from_check(self, result: ModelCheckResult) -> None:
        """Update internal state from model check result."""
        self.role = result.role
        self.is_banned = result.is_banned

        if result.is_admin:
            self.is_admin = True
            self.server_stats = result.server_stats
        else:
            self.is_admin = False
            self.server_stats = None

        self._save_state()


telemetry_manager = TelemetryManager()
