# Xerolux 2026
# SPDX-License-Identifier: MIT
import os
import time
import logging
import requests
import json
import threading
import base64
import hmac
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime
from .config import config
from .update_manager import get_current_version

logger = logging.getLogger(__name__)

# Default encryption key for community models (shared public key)
# In a real scenario, this might be rotated or fetched securely.
DEFAULT_ENCRYPTION_KEY = b"gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="

# Hardcoded Shared Auth Token for Community Server
# This allows clients to submit data without needing to configure a token manually.
SHARED_AUTH_TOKEN = "COMMUNITY-CONTRIBUTOR-TOKEN-2026"

# Service URLs
ML_SERVICE_UPLOAD_URL = os.environ.get(
    "ML_SERVICE_UPLOAD_URL", "http://idm-ml-service:8080/model/upload"
)


class TelemetryManager:
    def __init__(self):
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        # Rate limiting state
        self.manual_downloads_today = 0
        self.last_manual_download = 0

        # Admin State
        self.is_admin = False
        self.server_stats = None
        self.role = "guest"
        self.is_banned = False

        # Load state from config
        self._load_state()

    def _load_state(self):
        telemetry_config = config.get("telemetry", {})
        self.manual_downloads_today = telemetry_config.get("manual_downloads_today", 0)
        self.last_manual_download = telemetry_config.get("last_manual_download", 0)
        self.is_admin = telemetry_config.get("is_admin", False)
        self.role = telemetry_config.get("role", "guest")
        self.is_banned = telemetry_config.get("is_banned", False)
        self.server_stats = telemetry_config.get("server_stats", None)

        # Reset counter if it's a new day
        last_date = datetime.fromtimestamp(self.last_manual_download).date()
        if last_date < datetime.now().date():
            self.manual_downloads_today = 0
            self._save_state()

    def _save_state(self):
        config.set("telemetry.manual_downloads_today", self.manual_downloads_today)
        config.set("telemetry.last_manual_download", self.last_manual_download)
        config.set("telemetry.is_admin", self.is_admin)
        config.set("telemetry.role", self.role)
        config.set("telemetry.is_banned", self.is_banned)
        if self.server_stats:
            config.set("telemetry.server_stats", self.server_stats)
        config.save()

    def retrieve_credentials(self):
        """
        Retrieve per-installation credentials from the server.

        If no per-installation token is stored locally, requests new credentials
        from the server using the global SHARED_AUTH_TOKEN.

        Returns:
            True if credentials are available (existing or newly retrieved),
            False if retrieval failed.
        """
        # Check if we already have a per-installation token
        existing_token = config.get("telemetry.auth_token")
        if existing_token and existing_token != SHARED_AUTH_TOKEN:
            logger.debug("Per-installation token already configured")
            return True

        installation_id = config.get("installation_id")
        if not installation_id:
            logger.warning("Cannot retrieve credentials: no installation_id configured")
            return False

        server_url = config.get("telemetry.server_url", "https://collector.xerolux.de")

        # Retry configuration for transient errors (503, network issues)
        max_retries = 3
        base_delay = 2.0  # seconds

        headers = {
            "Authorization": f"Bearer {SHARED_AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        last_error = None
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    logger.info(
                        "Retrieving per-installation credentials from server..."
                    )
                else:
                    logger.debug(
                        f"Credential retrieval retry attempt {attempt + 1}/{max_retries}"
                    )

                response = requests.post(
                    f"{server_url}/api/v1/credentials/retrieve",
                    params={"installation_id": installation_id},
                    headers=headers,
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()

                    # Store credentials in config
                    auth_token = data.get("auth_token")
                    encryption_key = data.get("encryption_key")

                    if auth_token:
                        config.set("telemetry.auth_token", auth_token)
                        logger.info("Per-installation auth token stored")

                    if encryption_key:
                        config.set("telemetry.encryption_key", encryption_key)
                        logger.info("Per-installation encryption key stored")

                    config.save()

                    is_new = data.get("is_new", True)
                    if is_new:
                        logger.info("New installation registered with telemetry server")
                    else:
                        logger.info("Credentials retrieved for existing installation")

                    return True
                elif response.status_code in (502, 503, 504):
                    # Transient server errors - retry with backoff
                    last_error = f"{response.status_code} - {response.text}"
                    if attempt < max_retries - 1:
                        delay = base_delay * (2**attempt)
                        logger.debug(
                            f"Server temporarily unavailable ({response.status_code}), retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        continue
                else:
                    # Non-retryable error
                    logger.warning(
                        f"Failed to retrieve credentials: {response.status_code} - {response.text}"
                    )
                    return False

            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    logger.debug(f"Network error, retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
                    continue
            except Exception as e:
                logger.error(f"Unexpected error retrieving credentials: {e}")
                return False

        # All retries exhausted
        logger.warning(
            f"Failed to retrieve credentials after {max_retries} attempts: {last_error}"
        )
        return False

    def start(self, scheduler=None):
        """
        Start the telemetry manager.
        The `scheduler` argument is kept for compatibility but ignored if it's the custom Modbus scheduler.
        Telemetry uses its own internal thread/scheduler for background tasks.
        """
        if self.running:
            return

        self.running = True

        # Try to retrieve per-installation credentials (non-blocking, fails silently)
        # This migrates from shared token to per-installation token
        if config.get("telemetry.enabled", True):
            try:
                self.retrieve_credentials()
            except Exception as e:
                logger.debug(f"Credential retrieval skipped: {e}")

        # Start internal loop thread
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Telemetry Manager started")

    def _run_loop(self):
        """Internal loop to check for scheduled tasks."""
        # Use simple schedule library if available, or manual loop
        import schedule

        # Schedule jobs
        # Run submission every 24 hours (e.g., at 02:00)
        schedule.every().day.at("02:00").do(self.submit_data_job)

        # Run model check every 24 hours (e.g., at 04:00)
        schedule.every().day.at("04:00").do(self.check_model_job)

        logger.info("Telemetry jobs scheduled")

        while self.running:
            try:
                schedule.run_pending()
                # Use a shorter sleep to check stop condition more frequently
                for _ in range(
                    60
                ):  # Sleep for 60 seconds total, but check every second
                    if not self.running:
                        break
                    time.sleep(1)
                if not self.running:
                    break
            except Exception as e:
                logger.error(f"Telemetry loop error: {e}")
                # Also check running flag during error recovery sleep
                for _ in range(60):
                    if not self.running:
                        break
                    time.sleep(1)
                if not self.running:
                    break

    def stop(self):
        self.running = False

    def get_status(self):
        """Return current telemetry status."""
        telemetry_config = config.get("telemetry", {})

        # Check if using per-installation token
        auth_token = telemetry_config.get("auth_token")
        has_per_installation_token = bool(
            auth_token and auth_token != SHARED_AUTH_TOKEN
        )
        has_encryption_key = bool(telemetry_config.get("encryption_key"))

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
            "has_encryption_key": has_encryption_key,
        }

    def submit_data_job(self):
        """Scheduled job to submit data."""
        if not config.get("telemetry.enabled", True):
            return

        try:
            logger.info("Starting daily telemetry submission...")
            self.submit_data(hours=24)
        except Exception as e:
            logger.error(f"Telemetry submission job failed: {e}")

    def check_model_job(self):
        """Scheduled job to check and update model."""
        if not config.get("telemetry.enabled", True):
            return

        try:
            logger.info("Starting daily model update check...")
            self.download_and_install_model(manual=False)
        except Exception as e:
            logger.error(f"Model check job failed: {e}")

    def submit_data(self, hours=24):
        """
        Query VictoriaMetrics for data and submit to server.
        """
        server_url = config.get("telemetry.server_url", "https://collector.xerolux.de")
        # Use user config token if available, else shared token
        auth_token = config.get("telemetry.auth_token") or SHARED_AUTH_TOKEN

        if not auth_token:
            logger.warning("Telemetry: No auth token configured. Skipping submission.")
            return False

        # 1. Fetch data from VictoriaMetrics
        metrics_url = config.get("metrics.url", "http://victoriametrics:8428/write")
        base_url = metrics_url.replace("/write", "").replace("/api/v1/write", "")
        query_url = f"{base_url}/api/v1/export"

        # Time range
        end_ts = int(time.time())
        start_ts = end_ts - (hours * 3600)

        # Use export API to get raw data points for idm_heatpump metrics
        params = {
            "match[]": '{__name__=~"idm_heatpump_.*"}',
            "start": start_ts,
            "end": end_ts,
        }

        # Note: export API returns JSON stream (one object per line)
        try:
            logger.debug(f"Querying metrics from {query_url}")
            response = requests.get(query_url, params=params, stream=True, timeout=60)

            if response.status_code != 200:
                logger.error(f"Failed to query metrics: {response.status_code}")
                return False

            measurement_map = {}  # timestamp -> {metric: value}

            # Process stream
            count = 0
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    # format: {"metric":{"__name__":"...","tag":"..."},"values":[v1...],"timestamps":[t1...]}
                    # OR format: {"metric":..., "value":..., "timestamps":...} depending on version/flags?
                    # VM export API usually returns: {"metric":{"__name__":"name", ...}, "values":[...], "timestamps":[...]}

                    metric_name = (
                        record.get("metric", {})
                        .get("__name__", "")
                        .replace("idm_heatpump_", "")
                    )
                    values = record.get("values", [])
                    timestamps = record.get("timestamps", [])

                    if not metric_name:
                        continue

                    for t, v in zip(timestamps, values):
                        # t is usually ms in VM export? Check VM docs.
                        # VM export returns timestamps in milliseconds usually.
                        ts_sec = t / 1000.0

                        # Group by timestamp (bucket to nearest second to align)
                        ts_key = int(ts_sec)

                        if ts_key not in measurement_map:
                            measurement_map[ts_key] = {"timestamp": ts_sec}

                        measurement_map[ts_key][metric_name] = v
                        count += 1

                except Exception:
                    continue

            logger.info(
                f"Processed {count} data points into {len(measurement_map)} records."
            )

            if not measurement_map:
                logger.warning("No data found to submit.")
                return False

            # Convert map to list
            payload_data = list(measurement_map.values())

            # Dynamic batch size calculation based on payload size
            # Server seems to have strict limit (likely 1MB Nginx default), so we use 0.9MB
            MAX_PAYLOAD_MB = 0.9
            MAX_BATCH_SIZE = 1000
            MIN_BATCH_SIZE = 100

            # Estimate average record size from sample
            if len(payload_data) > 0:
                # Use first 10 records or all if less
                sample_size = min(10, len(payload_data))
                sample_json = json.dumps(payload_data[:sample_size])
                avg_record_bytes = len(sample_json.encode("utf-8")) / sample_size

                # Add overhead for payload wrapper (installation_id, model, etc.)
                overhead_bytes = 500

                # Calculate optimal batch size
                optimal_batch = int(
                    ((MAX_PAYLOAD_MB * 1024 * 1024) - overhead_bytes) / avg_record_bytes
                )

                # Clamp to min/max bounds
                BATCH_SIZE = max(MIN_BATCH_SIZE, min(MAX_BATCH_SIZE, optimal_batch))

                logger.info(
                    f"Dynamic batch size: {BATCH_SIZE} records "
                    f"(avg record size: {int(avg_record_bytes)} bytes, "
                    f"total records: {len(payload_data)})"
                )
            else:
                BATCH_SIZE = 200  # Fallback

            total_batches = (len(payload_data) + BATCH_SIZE - 1) // BATCH_SIZE

            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json",
            }

            success_count = 0

            for i in range(0, len(payload_data), BATCH_SIZE):
                batch = payload_data[i : i + BATCH_SIZE]

                payload = {
                    "installation_id": config.get("installation_id"),
                    "heatpump_model": config.get("hp_model", "Unknown"),
                    "version": get_current_version(),
                    "data": batch,
                }

                try:
                    res = requests.post(
                        f"{server_url}/api/v1/submit",
                        json=payload,
                        headers=headers,
                        timeout=30,
                    )
                    if res.status_code in (200, 204):
                        success_count += 1
                    else:
                        logger.error(
                            f"Submit batch {i // BATCH_SIZE + 1} failed: {res.status_code} - {res.text}"
                        )
                except Exception as e:
                    logger.error(f"Submit batch {i // BATCH_SIZE + 1} error: {e}")

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

        except Exception as e:
            logger.error(f"Telemetry submission failed: {e}")
            return False

    def download_and_install_model(self, manual=False):
        """
        Check for model update, download if available, install to ML service.
        """
        # Rate limit check for manual
        if manual:
            if self.manual_downloads_today >= 3:
                logger.warning("Manual download limit reached.")
                raise Exception(
                    "Tägliches Limit für manuelle Downloads erreicht (3/Tag)."
                )

        server_url = config.get("telemetry.server_url", "https://collector.xerolux.de")
        installation_id = config.get("installation_id")
        hp_model = config.get("hp_model")

        # 1. Check eligibility
        try:
            check_url = f"{server_url}/api/v1/model/check"
            params = {"installation_id": installation_id, "model": hp_model}

            resp = requests.get(check_url, params=params, timeout=10)
            resp.raise_for_status()
            status = resp.json()

            config.set("telemetry.last_model_check", int(time.time()))

            # Update Status (Role, Admin, Ban)
            self.role = status.get("role", "guest")
            self.is_banned = status.get("is_banned", False)

            if status.get("is_admin"):
                self.is_admin = True
                self.server_stats = status.get("server_stats")
            else:
                self.is_admin = False
                self.server_stats = None

            self._save_state()

            if not status.get("eligible"):
                msg = status.get("reason_de", status.get("reason", "Nicht berechtigt"))
                logger.info(f"Model check: Not eligible - {msg}")
                if manual:
                    raise Exception(msg)
                return False

            if not status.get("model_available"):
                msg = status.get(
                    "reason_de", status.get("reason", "Kein Modell verfügbar")
                )
                logger.info(f"Model check: {msg}")
                if manual:
                    raise Exception(msg)
                return False

            if not status.get("update_available") and not manual:
                logger.info("Model check: No update needed.")
                return True

            # 2. Download Model
            logger.info("Downloading community model...")
            # Use user config token if available, else shared token
            auth_token = config.get("telemetry.auth_token") or SHARED_AUTH_TOKEN
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

            download_url = f"{server_url}/api/v1/model/download"
            resp = requests.get(
                download_url, params=params, headers=headers, timeout=60
            )
            resp.raise_for_status()

            # 3. Integrity Verification (BEFORE parsing/decryption)
            raw_content = resp.content

            # Verify SHA256 hash if provided
            expected_hash = resp.headers.get("X-Model-Hash", "").strip()
            if expected_hash:
                actual_hash = hashlib.sha256(raw_content).hexdigest()
                if not hmac.compare_digest(expected_hash.lower(), actual_hash.lower()):
                    raise Exception(
                        f"Hash-Verifizierung fehlgeschlagen! Erwartet: {expected_hash[:16]}..., "
                        f"Erhalten: {actual_hash[:16]}... - Modell könnte manipuliert sein!"
                    )
                logger.info("Model hash verified successfully")
            else:
                logger.warning(
                    "No X-Model-Hash header found - hash verification skipped"
                )

            # Parse JSON envelope
            envelope = resp.json()

            # Version compatibility check
            envelope_version = envelope.get("version", "1.0")
            supported_versions = ["1.0", "2.0"]
            if envelope_version not in supported_versions:
                raise Exception(
                    f"Nicht unterstützte Modell-Version: {envelope_version}. "
                    f"Unterstützte Versionen: {', '.join(supported_versions)}"
                )
            logger.info(f"Model version {envelope_version} is compatible")

            # Verify signature
            key = config.get("telemetry.encryption_key")
            if not key:
                key = DEFAULT_ENCRYPTION_KEY

            # Ensure key is bytes
            if isinstance(key, str):
                key = key.encode("utf-8")

            payload_b64 = envelope["payload"]
            metadata = envelope["metadata"]
            signature = envelope["signature"]

            # Timestamp verification (prevent replay attacks)
            model_timestamp = metadata.get("timestamp")
            if model_timestamp:
                age_hours = (time.time() - model_timestamp) / 3600
                # Models older than 90 days are suspicious
                if age_hours > 90 * 24:
                    logger.warning(
                        f"Model is very old ({int(age_hours / 24)} days). "
                        "This could indicate a replay attack or outdated model."
                    )
                # Models from the future are definitely suspicious
                if age_hours < -24:
                    raise Exception(
                        f"Model timestamp is in the future! Possible replay attack. "
                        f"Model timestamp: {model_timestamp}, Current time: {time.time()}"
                    )
                logger.info(f"Model age: {int(age_hours / 24)} days - timestamp valid")
            else:
                logger.warning(
                    "No timestamp in model metadata - replay protection unavailable"
                )

            # Reconstruct message to sign
            metadata_json = json.dumps(metadata, sort_keys=True)
            msg = f"{payload_b64}.{metadata_json}".encode("utf-8")

            expected_sig = hmac.new(key, msg, hashlib.sha256).hexdigest()

            if not hmac.compare_digest(expected_sig, signature):
                raise Exception("Ungültige Signatur des Modells! Download abgebrochen.")

            logger.info("Model signature verified successfully")

            # Decrypt
            f = Fernet(key)
            encrypted_data = base64.b64decode(payload_b64)
            decrypted_data = f.decrypt(encrypted_data)

            # 4. Upload to ML Service
            logger.info("Uploading model to ML Service...")
            files = {"file": ("model_state.pkl", decrypted_data)}

            # Add internal secret header if configured
            ml_headers = {}
            internal_key = config.get("internal_api_key")
            if internal_key:
                ml_headers["X-Internal-Secret"] = internal_key

            upload_resp = requests.post(
                ML_SERVICE_UPLOAD_URL, files=files, headers=ml_headers, timeout=30
            )

            if upload_resp.status_code == 200:
                logger.info("Model installed successfully.")
                if manual:
                    self.manual_downloads_today += 1
                    self.last_manual_download = int(time.time())
                    self._save_state()
                return True
            else:
                raise Exception(f"ML Service Upload failed: {upload_resp.text}")

        except Exception as e:
            logger.error(f"Model update failed: {e}")
            if manual:
                raise e
            return False


telemetry_manager = TelemetryManager()
