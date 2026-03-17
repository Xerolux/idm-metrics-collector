# Xerolux 2026
# SPDX-License-Identifier: MIT
import base64
import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from cryptography.fernet import Fernet

from .telemetry_config import model_download_config, telemetry_client_config
from .http_client import HttpClient

logger = logging.getLogger(__name__)

ML_SERVICE_UPLOAD_URL = os.environ.get(
    "ML_SERVICE_UPLOAD_URL", "http://idm-ml-service:8080/model/upload"
)


@dataclass
class ModelVerificationResult:
    valid: bool
    decrypted_data: Optional[bytes] = None
    error_message: str = ""


@dataclass
class ModelCheckResult:
    eligible: bool
    model_available: bool
    update_available: bool
    role: str = "guest"
    is_admin: bool = False
    is_banned: bool = False
    server_stats: Optional[Dict[str, Any]] = None
    reason: str = ""
    reason_de: str = ""


class ModelDownloader:
    """Handles model download, verification, and installation."""

    def __init__(self, http_client: Optional[HttpClient] = None):
        self.http_client = http_client or HttpClient()
        self._manual_downloads_today = 0
        self._last_manual_download = 0

    def check_rate_limit(self, manual: bool) -> Tuple[bool, str]:
        """Check if manual download is allowed."""
        if not manual:
            return True, ""

        if (
            self._manual_downloads_today
            >= model_download_config.max_manual_downloads_per_day
        ):
            return (
                False,
                f"Tägliches Limit für manuelle Downloads erreicht ({model_download_config.max_manual_downloads_per_day}/Tag).",
            )

        return True, ""

    def increment_download_count(self) -> None:
        """Increment the manual download counter."""
        self._manual_downloads_today += 1
        self._last_manual_download = int(time.time())

    def reset_daily_counter(self) -> None:
        """Reset the daily download counter."""
        from datetime import datetime

        last_date = datetime.fromtimestamp(self._last_manual_download).date()
        if last_date < datetime.now().date():
            self._manual_downloads_today = 0

    def verify_hash(self, content: bytes, expected_hash: str) -> bool:
        """Verify SHA256 hash of content."""
        if not expected_hash:
            logger.warning("No hash provided for verification")
            return True

        actual_hash = hashlib.sha256(content).hexdigest()
        return hmac.compare_digest(expected_hash.lower(), actual_hash.lower())

    def verify_timestamp(self, timestamp: Optional[float]) -> Tuple[bool, str]:
        """Verify model timestamp is valid (not too old, not from future)."""
        if not timestamp:
            logger.warning(
                "No timestamp in model metadata - replay protection unavailable"
            )
            return True, ""

        age_hours = (time.time() - timestamp) / 3600

        if age_hours > model_download_config.model_max_age_days * 24:
            logger.warning(
                f"Model is very old ({int(age_hours / 24)} days). "
                "This could indicate a replay attack or outdated model."
            )

        if age_hours < -24:
            return False, f"Model timestamp is in the future! Possible replay attack."

        logger.info(f"Model age: {int(age_hours / 24)} days - timestamp valid")
        return True, ""

    def verify_signature(
        self,
        payload_b64: str,
        metadata: Dict[str, Any],
        signature: str,
        key: bytes,
    ) -> bool:
        """Verify HMAC signature of the model payload."""
        metadata_json = json.dumps(metadata, sort_keys=True)
        msg = f"{payload_b64}.{metadata_json}".encode("utf-8")
        expected_sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature)

    def verify_and_decrypt(
        self,
        envelope: Dict[str, Any],
        encryption_key: Optional[bytes] = None,
    ) -> ModelVerificationResult:
        """Verify and decrypt a model envelope."""
        try:
            envelope_version = envelope.get("version", "1.0")
            if (
                envelope_version
                not in model_download_config.supported_envelope_versions
            ):
                return ModelVerificationResult(
                    valid=False,
                    error_message=f"Nicht unterstützte Modell-Version: {envelope_version}",
                )

            logger.info(f"Model version {envelope_version} is compatible")

            payload_b64 = envelope.get("payload", "")
            metadata = envelope.get("metadata", {})
            signature = envelope.get("signature", "")

            if not all([payload_b64, signature]):
                return ModelVerificationResult(
                    valid=False,
                    error_message="Fehlende payload oder signatur im Modell",
                )

            timestamp_valid, timestamp_error = self.verify_timestamp(
                metadata.get("timestamp")
            )
            if not timestamp_valid:
                return ModelVerificationResult(
                    valid=False, error_message=timestamp_error
                )

            key = encryption_key or telemetry_client_config.get_default_encryption_key()
            if isinstance(key, str):
                key = key.encode("utf-8")

            if not self.verify_signature(payload_b64, metadata, signature, key):
                return ModelVerificationResult(
                    valid=False,
                    error_message="Ungültige Signatur des Modells! Download abgebrochen.",
                )

            logger.info("Model signature verified successfully")

            f = Fernet(key)
            encrypted_data = base64.b64decode(payload_b64)
            decrypted_data = f.decrypt(encrypted_data)

            return ModelVerificationResult(valid=True, decrypted_data=decrypted_data)

        except Exception as e:
            logger.error(f"Model verification failed: {e}")
            return ModelVerificationResult(valid=False, error_message=str(e))

    def upload_to_ml_service(
        self,
        decrypted_data: bytes,
        internal_api_key: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Upload decrypted model to ML service."""
        try:
            logger.info("Uploading model to ML Service...")
            files = {"file": ("model_state.pkl", decrypted_data)}

            headers = {}
            if internal_api_key:
                headers["X-Internal-Secret"] = internal_api_key

            response = self.http_client.post(
                ML_SERVICE_UPLOAD_URL,
                files=files,
                headers=headers,
            )

            if response.status_code == 200:
                logger.info("Model installed successfully.")
                return True, ""
            else:
                return False, f"ML Service Upload failed: {response.text}"

        except Exception as e:
            logger.error(f"Failed to upload model to ML service: {e}")
            return False, str(e)

    def check_model_availability(
        self,
        server_url: str,
        installation_id: str,
        hp_model: str,
    ) -> ModelCheckResult:
        """Check model availability on the server."""
        try:
            check_url = f"{server_url}/api/v1/model/check"
            params = {"installation_id": installation_id, "model": hp_model}

            response = self.http_client.get(check_url, params=params)
            response.raise_for_status()
            status = response.json()

            return ModelCheckResult(
                eligible=status.get("eligible", False),
                model_available=status.get("model_available", False),
                update_available=status.get("update_available", False),
                role=status.get("role", "guest"),
                is_admin=status.get("is_admin", False),
                is_banned=status.get("is_banned", False),
                server_stats=status.get("server_stats"),
                reason=status.get("reason", ""),
                reason_de=status.get("reason_de", ""),
            )

        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return ModelCheckResult(
                eligible=False,
                model_available=False,
                update_available=False,
                reason=str(e),
            )

    def download_model(
        self,
        server_url: str,
        installation_id: str,
        hp_model: str,
        auth_token: str,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[bytes], str]:
        """Download model from server. Returns (envelope, raw_content, error)."""
        try:
            download_url = f"{server_url}/api/v1/model/download"
            params = {"installation_id": installation_id, "model": hp_model}
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

            response = self.http_client.get(
                download_url,
                params=params,
                headers=headers,
            )
            response.raise_for_status()

            raw_content = response.content

            expected_hash = response.headers.get("X-Model-Hash", "").strip()
            if expected_hash and not self.verify_hash(raw_content, expected_hash):
                return (
                    None,
                    raw_content,
                    (
                        f"Hash-Verifizierung fehlgeschlagen! "
                        f"Erwartet: {expected_hash[:16]}..., "
                        f"Erhalten: {hashlib.sha256(raw_content).hexdigest()[:16]}... "
                        f"- Modell könnte manipuliert sein!"
                    ),
                )

            if expected_hash:
                logger.info("Model hash verified successfully")

            envelope = response.json()
            return envelope, raw_content, ""

        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return None, None, str(e)


model_downloader = ModelDownloader()
