# Xerolux 2026
# SPDX-License-Identifier: MIT
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TelemetryClientConfig:
    server_url: str = field(
        default_factory=lambda: os.environ.get(
            "TELEMETRY_SERVER_URL", "https://collector.xerolux.de"
        )
    )
    auth_token: Optional[str] = field(default=None)
    encryption_key: Optional[bytes] = field(default=None)
    installation_id: Optional[str] = field(default=None)
    hp_model: Optional[str] = field(default=None)

    enabled: bool = field(
        default_factory=lambda: os.environ.get("TELEMETRY_ENABLED", "true").lower()
        in ("true", "1", "yes")
    )

    submit_hours: int = field(
        default_factory=lambda: int(os.environ.get("TELEMETRY_SUBMIT_HOURS", "24"))
    )

    @staticmethod
    def get_default_encryption_key() -> bytes:
        return b"gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="

    @staticmethod
    def get_shared_auth_token() -> str:
        return "COMMUNITY-CONTRIBUTOR-TOKEN-2026"


@dataclass
class RetryConfig:
    max_retries: int = field(
        default_factory=lambda: int(os.environ.get("TELEMETRY_MAX_RETRIES", "3"))
    )
    base_delay: float = field(
        default_factory=lambda: float(
            os.environ.get("TELEMETRY_RETRY_BASE_DELAY", "2.0")
        )
    )
    max_delay: float = field(
        default_factory=lambda: float(
            os.environ.get("TELEMETRY_RETRY_MAX_DELAY", "30.0")
        )
    )
    retryable_status_codes: tuple = field(default_factory=lambda: (502, 503, 504))


@dataclass
class BatchConfig:
    max_payload_mb: float = field(
        default_factory=lambda: float(os.environ.get("TELEMETRY_MAX_PAYLOAD_MB", "0.9"))
    )
    max_batch_size: int = field(
        default_factory=lambda: int(os.environ.get("TELEMETRY_MAX_BATCH_SIZE", "1000"))
    )
    min_batch_size: int = field(
        default_factory=lambda: int(os.environ.get("TELEMETRY_MIN_BATCH_SIZE", "100"))
    )
    overhead_bytes: int = field(default_factory=lambda: 500)


@dataclass
class ModelDownloadConfig:
    max_manual_downloads_per_day: int = field(
        default_factory=lambda: int(
            os.environ.get("TELEMETRY_MAX_MANUAL_DOWNLOADS", "3")
        )
    )
    model_max_age_days: int = field(
        default_factory=lambda: int(
            os.environ.get("TELEMETRY_MODEL_MAX_AGE_DAYS", "90")
        )
    )
    supported_envelope_versions: tuple = field(default_factory=lambda: ("1.0", "2.0"))


telemetry_client_config = TelemetryClientConfig()
retry_config = RetryConfig()
batch_config = BatchConfig()
model_download_config = ModelDownloadConfig()
