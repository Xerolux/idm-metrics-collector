import os
from dataclasses import dataclass, field
from typing import Dict, Optional

import redis


def _get_encryption_key() -> bytes:
    key = os.environ.get(
        "TELEMETRY_ENCRYPTION_KEY", "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="
    )
    return key.encode() if isinstance(key, str) else key


@dataclass
class ServerConfig:
    vm_write_url: str = field(
        default_factory=lambda: os.environ.get(
            "VM_WRITE_URL", "http://victoriametrics:8428/write"
        )
    )
    vm_query_url: str = field(
        default_factory=lambda: os.environ.get(
            "VM_QUERY_URL", "http://victoriametrics:8428/api/v1/query"
        )
    )
    auth_token: str = field(
        default_factory=lambda: os.environ.get(
            "AUTH_TOKEN", "change-me-to-something-secure"
        )
    )
    model_dir: str = field(
        default_factory=lambda: os.environ.get("MODEL_DIR", "/app/models")
    )
    min_installations: int = field(
        default_factory=lambda: int(os.environ.get("MIN_INSTALLATIONS", "5"))
    )
    min_data_points: int = field(
        default_factory=lambda: int(os.environ.get("MIN_DATA_POINTS", "10000"))
    )
    max_payload_size: int = field(
        default_factory=lambda: int(
            os.environ.get("MAX_PAYLOAD_SIZE", str(10 * 1024 * 1024))
        )
    )


@dataclass
class RateLimitConfig:
    window: int = field(
        default_factory=lambda: int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
    )
    max_entries: int = field(
        default_factory=lambda: int(os.environ.get("MAX_RATE_LIMIT_ENTRIES", "10000"))
    )
    limits: Dict[str, int] = field(
        default_factory=lambda: {
            "default": int(os.environ.get("RATE_LIMIT_DEFAULT", "100")),
            "submit": int(os.environ.get("RATE_LIMIT_SUBMIT", "60")),
            "status": int(os.environ.get("RATE_LIMIT_STATUS", "30")),
            "model": int(os.environ.get("RATE_LIMIT_MODEL", "10")),
            "admin": int(os.environ.get("RATE_LIMIT_ADMIN", "20")),
        }
    )

    def get_limit(self, endpoint_type: str) -> int:
        return self.limits.get(endpoint_type, self.limits["default"])


@dataclass
class CacheConfig:
    hash_ttl: int = field(
        default_factory=lambda: int(os.environ.get("HASH_CACHE_TTL", "3600"))
    )
    pool_stats_ttl: int = field(
        default_factory=lambda: int(os.environ.get("POOL_STATS_CACHE_TTL", "60"))
    )
    community_avg_ttl: int = field(
        default_factory=lambda: int(os.environ.get("COMMUNITY_AVG_CACHE_TTL", "300"))
    )
    contribution_rank_ttl: int = field(
        default_factory=lambda: int(
            os.environ.get("CONTRIBUTION_RANK_CACHE_TTL", "300")
        )
    )


@dataclass
class SecurityConfig:
    default_ban_duration: int = field(
        default_factory=lambda: int(os.environ.get("DEFAULT_BAN_DURATION", "3600"))
    )
    encryption_key: bytes = field(default_factory=lambda: _get_encryption_key())
    redis_url: Optional[str] = field(
        default_factory=lambda: os.environ.get("REDIS_URL", "")
    )
    use_redis: bool = field(init=False)

    def __post_init__(self):
        try:
            self.redis_client = (
                redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                if self.redis_url
                else None
            )
            self.redis_client.ping()
            self.use_redis = True
        except Exception:
            self.redis_client = None
            self.use_redis = False


config = ServerConfig()
rate_limit_config = RateLimitConfig()
cache_config = CacheConfig()
security_config = SecurityConfig()
