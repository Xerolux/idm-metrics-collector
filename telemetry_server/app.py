# Xerolux 2026
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Depends, Request, status
from fastapi.responses import (
    FileResponse,
    PlainTextResponse,
    ORJSONResponse,
    JSONResponse,
    Response,
)
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urlparse
import os
import httpx
import time
import asyncio
import csv
import io
import threading

from datetime import timedelta, datetime, timezone
import hashlib
import re
import uuid
import json
import base64
import hmac
import tempfile
from cryptography.fernet import Fernet
from pathlib import Path
from analysis import get_community_averages
import structlog
import orjson
import redis
from audit_log import (
    audit_logger,
    log_model_delete,
    log_model_download,
    log_training_trigger,
)
from token_manager import (
    token_manager,
    generate_token,
    validate_token as validate_installation_token,
    token_exists,
    get_encryption_key,
    has_encryption_key,
)
from permissions import (
    permission_manager,
    has_permission,
    is_admin,
    PERMISSIONS,
)
from installation_manager import (
    installation_manager,
    InstallationRole,
    BanType,
    check_upload_allowed,
    check_download_allowed,
    ROLE_DESCRIPTIONS,
    ROLE_FEATURES,
)
from training_queue import training_queue
from config import config, rate_limit_config, cache_config, security_config
from security import (
    mask_ip,
    mask_id,
    validate_installation_id as _validate_installation_id,
    validate_model_name as _validate_model_name,
    get_client_ip,
)
from rate_limit import rate_limiter
from cache import (
    file_hash_cache,
    pool_stats_cache,
    community_avg_cache,
    contribution_rank_cache,
)
from storage_paths import resolve_storage_dir

# Setup Structured Logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger("telemetry-server")

raw_admin_ids = os.environ.get("ADMIN_INSTALLATION_IDS", "")
ADMIN_IDS = {x.strip().lower() for x in raw_admin_ids.split(",") if x.strip()}

logger.info("loaded_admin_ids", count=len(ADMIN_IDS))
if not ADMIN_IDS and raw_admin_ids:
    logger.warning(
        "admin_ids_empty_but_set",
        message="ADMIN_INSTALLATION_IDS was present but parsed to empty list. Check delimiters.",
    )

VM_WRITE_URL = config.vm_write_url
VM_QUERY_URL = config.vm_query_url
AUTH_TOKEN = config.auth_token
ADMIN_AUTH_TOKEN = os.environ.get("ADMIN_AUTH_TOKEN", "").strip()
STRICT_ADMIN_AUTH = os.environ.get("STRICT_ADMIN_AUTH", "true").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)
MODEL_DIR = str(resolve_storage_dir("MODEL_DIR", config.model_dir, "models"))
MIN_INSTALLATIONS_FOR_MODEL = config.min_installations
MIN_DATA_POINTS_FOR_MODEL = config.min_data_points
MAX_PAYLOAD_SIZE = config.max_payload_size

RATE_LIMIT_WINDOW = rate_limit_config.window
MAX_RATE_LIMIT_ENTRIES = rate_limit_config.max_entries
RATE_LIMITS = rate_limit_config.limits

ADMIN_RUNTIME_SETTINGS: Dict[str, Any] = {
    "admin_rate_limit": int(RATE_LIMITS.get("admin", 20)),
    "max_training_queue": int(os.environ.get("MAX_TRAINING_QUEUE", "10")),
    "max_parallel_training": int(os.environ.get("MAX_PARALLEL_TRAINING", "1")),
    "min_installations": MIN_INSTALLATIONS_FOR_MODEL,
    "min_data_points": MIN_DATA_POINTS_FOR_MODEL,
}

PERMISSION_PRESETS: Dict[str, List[str]] = {
    "viewer": ["admin:view"],
    "ops": ["admin:view", "admin:models", "admin:training"],
    "user_admin": ["admin:view", "admin:users"],
    "ml_admin": ["admin:view", "admin:training", "admin:models"],
    "full": ["admin:full"],
}

DEFAULT_INSTALLATION_SETTINGS: Dict[str, Any] = {
    "telemetry_policy": {
        "upload_interval_seconds": 60,
        "sampling_ratio": 1.0,
        "pii_masking_level": "standard",
    },
    "alert_tuning": {
        "anomaly_threshold": 0.7,
        "cooldown_seconds": 300,
        "consecutive_hits": 3,
    },
    "feature_flags": {
        "next_gen_ai": False,
        "new_dashboard": False,
        "beta_training": False,
    },
}

_admin_rl_lock = threading.Lock()
_admin_rl_store: Dict[str, List[float]] = {}

DEFAULT_BAN_DURATION = security_config.default_ban_duration
DEFAULT_ENCRYPTION_KEY = security_config.encryption_key
USE_REDIS = security_config.use_redis
_redis_client = security_config.redis_client
REDIS_URL = security_config.redis_url
REDIS_AVAILABLE = security_config.use_redis
_encryption_key_str = os.environ.get("TELEMETRY_ENCRYPTION_KEY")
if not _encryption_key_str:
    _encryption_key_str = "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="
    logger.warning(
        "Using default encryption key - set TELEMETRY_ENCRYPTION_KEY environment variable for production"
    )

_INSECURE_TOKENS = {
    "",
    "change-me-to-something-secure",
    "changeme",
    "admin",
    "password",
}


def _is_strong_secret(token: Optional[str]) -> bool:
    if not token:
        return False
    t = token.strip()
    if len(t) < 24:
        return False
    return t.lower() not in _INSECURE_TOKENS


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return None
    return token or None


HASH_CACHE_TTL = cache_config.hash_ttl
POOL_STATS_CACHE_TTL = cache_config.pool_stats_ttl
COMMUNITY_AVG_CACHE_TTL = cache_config.community_avg_ttl

MAX_BANNED_IPS = 10000


_banned_ips: Dict[str, Tuple[float, int]] = {}


def run_sync(func, *args):
    return asyncio.to_thread(func, *args)


async def _cleanup_task():
    """Background task to clean up expired caches and bans."""
    while True:
        await asyncio.sleep(300)
        try:
            await asyncio.to_thread(audit_logger.cleanup_old_logs)
            await asyncio.to_thread(training_queue.cleanup_old_tasks, max_age_days=30)
            file_hash_cache.cleanup_expired()
            community_avg_cache.cleanup_expired()

            now = time.time()
            expired_bans = [
                ip for ip, (bt, dur) in list(_banned_ips.items()) if now - bt >= dur
            ]
            for ip in expired_bans:
                del _banned_ips[ip]
            if len(_banned_ips) > MAX_BANNED_IPS:
                sorted_bans = sorted(_banned_ips.items(), key=lambda x: x[1][0])
                for ip, _ in sorted_bans[: len(_banned_ips) - MAX_BANNED_IPS]:
                    del _banned_ips[ip]
        except Exception as e:
            logger.error("cleanup_error", error=str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    global _redis_client

    if AUTH_TOKEN == "change-me-to-something-secure":
        logger.critical(
            "insecure_configuration",
            message="AUTH_TOKEN is using default value! Security is compromised.",
        )

    default_key_str = "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="
    if _encryption_key_str == default_key_str:
        logger.critical(
            "insecure_configuration",
            message="TELEMETRY_ENCRYPTION_KEY is using default value! Models are not secure.",
        )

    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    logger.info("http_client_initialized")

    if USE_REDIS:
        try:
            _redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            _redis_client.ping()
            safe_url = REDIS_URL
            try:
                parsed = urlparse(REDIS_URL)
                if parsed.password:
                    user_part = parsed.username if parsed.username is not None else ""
                    host_part = parsed.hostname if parsed.hostname else ""
                    port_part = f":{parsed.port}" if parsed.port else ""
                    safe_netloc = f"{user_part}:***@{host_part}{port_part}"
                    safe_url = parsed._replace(netloc=safe_netloc).geturl()
            except Exception:
                safe_url = "redis://***"
            logger.info("redis_connected", url=safe_url)
        except Exception as e:
            logger.warning(
                "redis_connection_failed", error=str(e), fallback="in_memory"
            )
            _redis_client = None
    else:
        if REDIS_AVAILABLE:
            logger.info(
                "redis_not_configured",
                hint="Set REDIS_URL environment variable to enable persistent rate limiting",
            )
        else:
            logger.info(
                "redis_not_available",
                hint="Install redis package to enable persistent rate limiting",
            )

    cleanup_handle = asyncio.create_task(_cleanup_task())
    logger.info("background_tasks_started")

    yield

    cleanup_handle.cancel()
    try:
        await cleanup_handle
    except asyncio.CancelledError:
        pass

    if hasattr(app.state, "http_client"):
        await app.state.http_client.aclose()
        logger.info("http_client_closed")

    if _redis_client:
        try:
            _redis_client.close()
            logger.info("redis_closed")
        except Exception as e:
            logger.warning("redis_close_error", error=str(e))


app = FastAPI(
    title="IDM Telemetry Server",
    version="1.0.6",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return PlainTextResponse(
        "Service Unavailable", status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )


# Obfuscate Root URL
@app.get("/")
async def root():
    return PlainTextResponse(
        "Service Unavailable", status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )


def _check_rate_limit_override(
    client_ip: str, endpoint_type: str, limit: int
) -> Tuple[bool, Dict[str, str]]:
    now = time.time()
    key = f"{client_ip}:{endpoint_type}"
    with _admin_rl_lock:
        timestamps = _admin_rl_store.get(key, [])
        timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(timestamps) >= limit:
            reset = int((max(timestamps) if timestamps else now) + RATE_LIMIT_WINDOW)
            _admin_rl_store[key] = timestamps
            return False, {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset),
                "Retry-After": str(RATE_LIMIT_WINDOW),
            }

        timestamps.append(now)
        _admin_rl_store[key] = timestamps
        remaining = max(0, limit - len(timestamps))
        reset = int(max(timestamps) + RATE_LIMIT_WINDOW)
        return True, {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
        }


def check_rate_limit(
    client_ip: str, endpoint_type: str = "default", override_limit: Optional[int] = None
) -> Tuple[bool, Dict[str, str]]:
    if override_limit and endpoint_type == "admin":
        allowed, headers = _check_rate_limit_override(
            client_ip, endpoint_type, max(1, int(override_limit))
        )
    else:
        allowed, headers = rate_limiter.check(client_ip, endpoint_type)
    if not allowed:
        logger.warning(
            "rate_limit_exceeded",
            ip=mask_ip(client_ip),
            endpoint=endpoint_type,
        )
    return allowed, headers


async def check_ip_ban(client_ip: str) -> bool:
    """Check if IP is banned. Supports Redis for persistence (falls back to in-memory)."""
    ban_key = f"ban:{client_ip}"
    now = time.time()

    # Use Redis if available
    if _redis_client:
        try:
            # Get ban data from Redis
            ban_data = _redis_client.get(ban_key)
            if ban_data:
                ban_info = json.loads(ban_data)
                ban_time = ban_info["ban_time"]
                duration = ban_info["duration"]
                if now - ban_time < duration:
                    logger.warning(
                        "ip_ban_check_redis", ip=mask_ip(client_ip), banned=True
                    )
                    return True  # Still banned
                else:
                    # Ban expired, remove from Redis
                    _redis_client.delete(ban_key)
            return False

        except Exception as e:
            logger.warning(
                "redis_ip_ban_check_failed", error=str(e), fallback="in_memory"
            )
            # Fall through to in-memory implementation

    # In-memory IP ban check (fallback)
    if client_ip in _banned_ips:
        ban_time, duration = _banned_ips[client_ip]
        if now - ban_time < duration:
            logger.warning("ip_ban_check_memory", ip=mask_ip(client_ip), banned=True)
            return True  # Still banned
        else:
            del _banned_ips[client_ip]  # Ban expired
    return False


def ban_ip(client_ip: str, duration: Optional[int] = None) -> None:
    """Ban an IP for duration seconds. Supports Redis for persistence (falls back to in-memory)."""
    if duration is None:
        duration = DEFAULT_BAN_DURATION

    ban_time = time.time()
    ban_key = f"ban:{client_ip}"
    ban_data = json.dumps({"ban_time": ban_time, "duration": duration})

    # Use Redis if available
    if _redis_client:
        try:
            # Store ban in Redis with TTL
            _redis_client.setex(ban_key, duration, ban_data)
            logger.warning(
                "ip_banned_redis",
                ip=mask_ip(client_ip),
                duration=duration,
                backend="redis",
            )
            return

        except Exception as e:
            logger.warning("redis_ip_ban_failed", error=str(e), fallback="in_memory")
            # Fall through to in-memory implementation

    # In-memory IP ban (fallback)
    _banned_ips[client_ip] = (ban_time, duration)
    logger.warning(
        "ip_banned_memory",
        ip=mask_ip(client_ip),
        duration=duration,
        backend="memory",
    )


async def get_file_hash(filepath: str) -> Optional[str]:
    return await file_hash_cache.get(filepath)


def validate_installation_id(installation_id: str) -> str:
    try:
        _validate_installation_id(installation_id)
        return installation_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def validate_model_name(model_name: Optional[str]) -> Optional[str]:
    try:
        return _validate_model_name(model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def resolve_model_file(model_name: str) -> Path:
    """Resolve model file path safely under MODEL_DIR."""
    normalized = validate_model_name(model_name)
    if not normalized:
        raise HTTPException(status_code=400, detail="Invalid model name")

    model_dir = Path(MODEL_DIR).resolve()
    for candidate in model_dir.glob("*.enc"):
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.stem == normalized and resolved.is_file():
            return resolved
    raise HTTPException(status_code=404, detail="Model not found")


async def get_data_pool_stats(request: Request) -> Dict[str, Any]:
    """
    Get current data pool statistics from VictoriaMetrics with caching.
    Used for cold start feedback.
    """
    cached_stats = await pool_stats_cache.get()
    if cached_stats:
        return cached_stats

    stats = {
        "total_installations": 0,
        "total_data_points": 0,
        "models_available": [],
        "data_sufficient": False,
        "message": "",
        "message_de": "",
    }

    try:
        client = request.app.state.http_client

        # Count unique installations (last 30 days)
        query_installations = 'count(count by (installation_id) (count_over_time({__name__=~"heatpump_metrics_.*", installation_id!=""}[30d])))'
        # Count total data points (last 30 days)
        query_points = 'sum(count_over_time({__name__=~"heatpump_metrics_.*"}[30d]))'

        # Check which models are available
        model_dir = Path(MODEL_DIR)

        def _list_models():
            if model_dir.exists():
                return [f.stem.replace("_", " ") for f in model_dir.glob("*.enc")]
            return []

        # Run all queries and model listing in parallel
        results = await asyncio.gather(
            client.get(VM_QUERY_URL, params={"query": query_installations}),
            client.get(VM_QUERY_URL, params={"query": query_points}),
            asyncio.to_thread(_list_models),
        )

        resp_installations, resp_points, models_available = results

        if resp_installations.status_code == 200:
            data = resp_installations.json()
            if (
                data.get("status") == "success"
                and data["data"]["result"]
                and data["data"]["result"][0].get("value")
                and len(data["data"]["result"][0]["value"]) > 1
            ):
                stats["total_installations"] = int(
                    data["data"]["result"][0]["value"][1]
                )

        if resp_points.status_code == 200:
            data = resp_points.json()
            if (
                data.get("status") == "success"
                and data["data"]["result"]
                and data["data"]["result"][0].get("value")
                and len(data["data"]["result"][0]["value"]) > 1
            ):
                stats["total_data_points"] = int(
                    float(data["data"]["result"][0]["value"][1])
                )

        stats["models_available"] = models_available

        # Determine if data is sufficient
        stats["data_sufficient"] = stats[
            "total_installations"
        ] >= ADMIN_RUNTIME_SETTINGS.get(
            "min_installations", MIN_INSTALLATIONS_FOR_MODEL
        ) and stats["total_data_points"] >= ADMIN_RUNTIME_SETTINGS.get(
            "min_data_points", MIN_DATA_POINTS_FOR_MODEL
        )

        # Generate user-friendly messages
        if stats["data_sufficient"]:
            stats["message"] = "Data pool is ready. Community models are available."
            stats["message_de"] = (
                "Datenpool ist bereit. Community-Modelle sind verfügbar."
            )
        else:
            needed_installations = max(
                0, MIN_INSTALLATIONS_FOR_MODEL - stats["total_installations"]
            )
            needed_points = max(
                0, MIN_DATA_POINTS_FOR_MODEL - stats["total_data_points"]
            )
            stats["message"] = (
                f"Building data pool. Need {needed_installations} more installations "
                f"and ~{needed_points:,} more data points. Data is being collected - thank you for contributing!"
            )
            stats["message_de"] = (
                f"Datenpool wird aufgebaut. Benötigt noch {needed_installations} Installationen "
                f"und ~{needed_points:,} Datenpunkte. Daten werden gesammelt - vielen Dank für Ihre Beiträge!"
            )

    except Exception as e:
        logger.error("data_pool_stats_error", error=str(e))
        stats["message"] = "Data pool status temporarily unavailable."
        stats["message_de"] = "Datenpool-Status vorübergehend nicht verfügbar."

    await pool_stats_cache.set(stats)

    return stats


class TelemetryPayload(BaseModel):
    installation_id: str
    heatpump_model: str
    version: str
    data: List[Dict[str, Any]]

    @validator("installation_id")
    def validate_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("installation_id must be a valid UUID")

    @validator("heatpump_model")
    def validate_model(cls, v):
        if not re.match(r"^[a-zA-Z0-9_\-\. \(\)]+$", v):
            raise ValueError("heatpump_model contains invalid characters")
        return v

    @validator("data")
    def validate_data_size(cls, v):
        """Validate payload size to prevent DoS."""
        import sys

        size = sys.getsizeof(v)
        if size > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload too large (max {MAX_PAYLOAD_SIZE} bytes)")
        return v


class RuntimeLimitsUpdate(BaseModel):
    admin_rate_limit: Optional[int] = None
    max_training_queue: Optional[int] = None
    max_parallel_training: Optional[int] = None
    min_installations: Optional[int] = None
    min_data_points: Optional[int] = None


class PermissionPresetApply(BaseModel):
    target_admin_id: str
    preset: str
    merge: bool = False


class InstallationSettingsUpdate(BaseModel):
    telemetry_policy: Optional[Dict[str, Any]] = None
    alert_tuning: Optional[Dict[str, Any]] = None
    feature_flags: Optional[Dict[str, bool]] = None


async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify global AUTH_TOKEN (for admin endpoints)."""
    if not AUTH_TOKEN or AUTH_TOKEN == "change-me-to-something-secure":
        raise HTTPException(
            status_code=503,
            detail="Server is not properly configured. Set a strong AUTH_TOKEN.",
        )

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Token")


async def verify_token_with_fallback(
    installation_id: str, authorization: Optional[str] = Header(None)
):
    """
    Verify token with fallback to global token for backward compatibility.

    1. Try per-installation token first (if exists)
    2. Fallback to global AUTH_TOKEN (for migration)
    3. Auto-register installation if using global token

    This allows seamless migration from shared token to per-installation tokens.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")

    # Try per-installation token first
    if token_exists(installation_id):
        if validate_installation_token(installation_id, token):
            logger.debug(
                "token_validated",
                installation_id=installation_id,
                type="per_installation",
            )
            return
        # Per-installation token exists but doesn't match
        # Still allow global token as fallback (client may not have received per-installation token yet)
        if AUTH_TOKEN and token == AUTH_TOKEN:
            logger.debug(
                "global_token_fallback",
                installation_id=installation_id,
                reason="per_installation_token_exists_but_client_using_global",
            )
            return
        # Neither per-installation nor global token matched
        logger.warning("token_mismatch", installation_id=installation_id)
        raise HTTPException(
            status_code=403, detail="Invalid Token for this installation"
        )

    # No per-installation token exists yet - check global token
    if AUTH_TOKEN and token == AUTH_TOKEN:
        logger.info(
            "global_token_used", installation_id=installation_id, migrating=True
        )
        # Auto-register this installation with unique token AND encryption key
        try:
            generate_token(
                installation_id,
                metadata={"migrated_from_global": True},
                with_encryption_key=True,
            )
            # Result is tuple of (token, encryption_key)
            logger.info(
                "installation_auto_registered",
                installation_id=installation_id,
                has_encryption_key=True,
            )
            # Note: Client doesn't know about the new credentials yet, but on next model check it will be notified
        except Exception as e:
            logger.error(
                "auto_registration_failed",
                installation_id=installation_id,
                error=str(e),
            )
        return

    # Neither per-installation nor global token worked
    raise HTTPException(status_code=403, detail="Invalid Token")


@app.post("/api/v1/register")
async def register_installation(
    installation_id: str,
    heatpump_model: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    """
    Register a new installation and receive a unique authentication token.

    This endpoint allows installations to register and receive their own unique token,
    replacing the shared COMMUNITY-CONTRIBUTOR-TOKEN.

    Args:
        installation_id: Unique installation identifier
        heatpump_model: Optional heat pump model name
        authorization: Must provide global AUTH_TOKEN for initial registration

    Returns:
        {
            "installation_id": "...",
            "auth_token": "unique-token-for-this-installation",
            "registered_at": "2026-02-02T..."
        }
    """
    validate_installation_id(installation_id)

    # Registration requires global AUTH_TOKEN (for security)
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AUTH_TOKEN:
        raise HTTPException(
            status_code=403, detail="Invalid global token for registration"
        )

    # Check if already registered
    if token_exists(installation_id):
        logger.warning("registration_duplicate", installation_id=installation_id)
        raise HTTPException(
            status_code=409,
            detail="Installation already registered. Use /api/v1/token/refresh to get a new token.",
        )

    # Generate new token AND encryption key
    try:
        result = generate_token(
            installation_id,
            metadata={"heatpump_model": heatpump_model} if heatpump_model else {},
            with_encryption_key=True,  # Generate encryption key alongside token
        )

        # Unpack result (tuple of token, encryption_key)
        new_token, encryption_key = result

        logger.info(
            "installation_registered",
            installation_id=installation_id,
            has_encryption_key=True,
        )

        return {
            "installation_id": installation_id,
            "auth_token": new_token,
            "encryption_key": encryption_key,  # NEW: Per-installation encryption key
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "message": "Credentials generated successfully. Store these securely - they won't be shown again!",
            "security_note": "Your personal encryption key provides additional security. Future model downloads will use per-installation encryption.",
        }
    except Exception as e:
        logger.error(
            "registration_failed", installation_id=installation_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/api/v1/credentials/retrieve")
async def retrieve_credentials(
    installation_id: str,
    authorization: Optional[str] = Header(None),
):
    """
    Retrieve (or regenerate) credentials for an installation.

    This endpoint allows clients to get their per-installation credentials.
    - For new installations: Creates new credentials
    - For existing installations: Regenerates credentials (invalidates old token)

    Requires global AUTH_TOKEN for authentication.

    Args:
        installation_id: Unique installation identifier
        authorization: Must provide global AUTH_TOKEN

    Returns:
        {
            "installation_id": "...",
            "auth_token": "unique-token-for-this-installation",
            "encryption_key": "base64-encoded-key",
            "is_new": true/false,
            "retrieved_at": "2026-02-02T..."
        }
    """
    validate_installation_id(installation_id)

    # Verify token with fallback
    await verify_token_with_fallback(installation_id, authorization)

    is_new = not token_exists(installation_id)

    # Generate new credentials (overwrites existing if present)
    try:
        result = generate_token(
            installation_id,
            metadata={"retrieved_via_api": True, "was_new": is_new},
            with_encryption_key=True,
        )

        new_token, encryption_key = result

        logger.info(
            "credentials_retrieved",
            installation_id=installation_id,
            is_new=is_new,
        )

        return {
            "installation_id": installation_id,
            "auth_token": new_token,
            "encryption_key": encryption_key,
            "is_new": is_new,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "message": "Store these credentials securely - they won't be shown again!",
        }
    except Exception as e:
        logger.error(
            "credential_retrieval_failed", installation_id=installation_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail="Credential retrieval failed")


def _process_telemetry_batch(
    installation_id: str, heatpump_model: str, version: str, data: list
) -> list[str]:
    """
    Synchronously format a batch of telemetry records into Influx Line Protocol.
    This CPU-intensive task is designed to be offloaded to a background thread.
    """

    def _escape_tag_value(value: Any) -> str:
        text = str(value)
        return (
            text.replace("\\", "\\\\")
            .replace(",", "\\,")
            .replace("=", "\\=")
            .replace(" ", "\\ ")
        )

    def _escape_field_key(key: Any) -> str:
        text = str(key)
        return (
            text.replace("\\", "\\\\")
            .replace(",", "\\,")
            .replace("=", "\\=")
            .replace(" ", "\\ ")
        )

    def _escape_string_field(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    lines = []
    # Pre-calculate static tags once per batch.
    prefix = (
        "heatpump_metrics,"
        f"installation_id={_escape_tag_value(installation_id)},"
        f"model={_escape_tag_value(heatpump_model)},"
        f"version={_escape_tag_value(version)} "
    )

    # Memoize escaped keys to avoid redundant string parsing allocations in the hot loop
    _key_cache = {}

    for record in data:
        timestamp = record.get("timestamp")
        if not timestamp:
            continue

        ts_ns = int(timestamp * 1e9)
        fields = []
        for key, value in record.items():
            if key == "timestamp":
                continue

            if key not in _key_cache:
                _key_cache[key] = _escape_field_key(key)
            field_key = _key_cache[key]

            if isinstance(value, bool):
                fields.append(f"{field_key}={'True' if value else 'False'}")
            elif isinstance(value, (int, float)):
                fields.append(f"{field_key}={value}")
            elif isinstance(value, str):
                fields.append(f'{field_key}="{_escape_string_field(value)}"')

        if fields:
            line = f"{prefix}{','.join(fields)} {ts_ns}"
            lines.append(line)

    return lines


@app.post("/api/v1/submit")
async def submit_telemetry(
    payload: TelemetryPayload,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """
    Ingest telemetry data and forward to VictoriaMetrics.

    Uses per-installation tokens with fallback to global token for migration.
    """
    # Verify token (per-installation with fallback)
    await verify_token_with_fallback(payload.installation_id, authorization)

    # Check installation ban status
    upload_allowed, ban_reason = check_upload_allowed(payload.installation_id)
    if not upload_allowed:
        logger.warning(
            "submit_installation_banned",
            installation_id=payload.installation_id,
            reason=ban_reason,
        )
        return JSONResponse(
            {"detail": f"Upload blocked: {ban_reason}"},
            status_code=403,
            headers={"Content-Type": "application/json"},
        )

    # Prefer X-Forwarded-For if behind proxy, else fallback to direct connection
    raw_ip = get_client_ip(request)

    client_ip = mask_ip(raw_ip)

    # Check IP ban
    if await check_ip_ban(raw_ip):
        logger.warning(
            "submit_banned_ip", ip=client_ip, installation_id=payload.installation_id
        )
        return JSONResponse(
            {"detail": "Access denied"},
            status_code=403,
            headers={"Content-Type": "application/json"},
        )

    # Rate limiting with headers (endpoint-specific for submit)
    allowed, rate_limit_headers = check_rate_limit(raw_ip, "submit")
    if not allowed:
        logger.warning(
            "rate_limit_exceeded", ip=client_ip, installation_id=payload.installation_id
        )
        return JSONResponse(
            {"detail": "Too many requests. Please try again later."},
            status_code=429,
            headers=rate_limit_headers,
        )

    try:
        # Offload synchronous formatting to a thread pool to avoid blocking the event loop
        lines = await asyncio.to_thread(
            _process_telemetry_batch,
            payload.installation_id,
            payload.heatpump_model,
            payload.version,
            payload.data,
        )

        if lines:
            # Batch write to VictoriaMetrics using pooled client
            data = "\n".join(lines)
            client = request.app.state.http_client
            # Use content=data for raw body to avoid form-encoding overhead/issues
            response = await client.post(VM_WRITE_URL, content=data)

            if response.status_code != 204:  # VM returns 204 on success
                logger.error(
                    "vm_write_failed",
                    status=response.status_code,
                    response=response.text[:200],
                )
                raise HTTPException(status_code=502, detail="Database Write Failed")

            logger.info(
                "telemetry_ingested",
                installation_id=payload.installation_id,
                points=len(lines),
                ip=client_ip,
            )

            # Track business metrics
            if PROMETHEUS_AVAILABLE:
                data_submissions_total.labels(
                    heatpump_model=payload.heatpump_model
                ).inc()
                data_points_submitted_total.inc(len(lines))

        return JSONResponse(
            {"status": "success", "processed": len(lines)}, headers=rate_limit_headers
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("telemetry_processing_error", ip=client_ip, error=str(e))
        raise HTTPException(status_code=500, detail="Telemetry processing failed")


@app.get("/health")
async def health(request: Request):
    """Detailed health check endpoint."""
    health_status = {"status": "healthy", "checks": {}, "timestamp": time.time()}

    # Check VictoriaMetrics
    try:
        client = request.app.state.http_client
        response = await client.get(f"{VM_QUERY_URL}?query=up", timeout=2)
        health_status["checks"]["victoriametrics"] = (
            "up" if response.status_code == 200 else "down"
        )
        if response.status_code != 200:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["victoriametrics"] = "unreachable"
        health_status["status"] = "degraded"
        logger.warning("health_check_vm_failed", error=str(e))

    # Check Model Directory
    model_dir = Path(MODEL_DIR)
    health_status["checks"]["model_dir"] = (
        "accessible" if model_dir.exists() else "missing"
    )
    if not model_dir.exists():
        health_status["status"] = "degraded"

    # Check memory usage
    try:
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()
        health_status["checks"]["memory_mb"] = round(memory_info.rss / 1024 / 1024, 2)
    except ImportError:
        pass  # psutil not available, skip
    except Exception as e:
        logger.warning("health_check_memory_failed", error=str(e))

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/api/v1/status")
async def server_status(request: Request, auth: None = Depends(verify_token)):
    """
    Get server statistics (Internal/Admin only).
    """
    try:
        client = request.app.state.http_client
        # Count unique installations (approximate)
        query = 'count(count by (installation_id) (count_over_time({__name__=~"heatpump_metrics_.*", installation_id!=""}[30d])))'
        response = await client.get(VM_QUERY_URL, params={"query": query})
        installations = 0
        if response.status_code == 200:
            data = response.json()
            if (
                data.get("status") == "success"
                and data["data"]["result"]
                and data["data"]["result"][0].get("value")
                and len(data["data"]["result"][0]["value"]) > 1
            ):
                installations = int(data["data"]["result"][0]["value"][1])

        return {
            "status": "online",
            "active_installations_30d": installations,
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error("status_check_failed", error=str(e))
        return {"status": "error", "message": "status check failed"}


@app.get("/api/v1/model/check")
async def check_eligibility(
    request: Request,
    installation_id: str,
    model: Optional[str] = None,
    current_hash: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    """
    Check if an installation ID is eligible for community models.
    Returns eligibility status, model hash (if available), and data pool info.

    Args:
        installation_id: Unique installation identifier
        model: Optional heat pump model name for model-specific checks
        current_hash: Optional current model hash to check if update needed
    """
    # Validation
    validate_installation_id(installation_id)
    model = validate_model_name(model)  # Returns normalized/validated name or None

    # Require valid token for this installation to avoid ID probing.
    # For admin installations we also allow the dedicated admin token.
    bearer_token = _extract_bearer_token(authorization)
    is_admin_candidate = (
        installation_id.lower() in ADMIN_IDS
        or installation_manager.has_role_or_higher(
            installation_id, InstallationRole.ADMIN
        )
    )
    admin_token_ok = bool(
        bearer_token
        and _is_strong_secret(ADMIN_AUTH_TOKEN)
        and bearer_token == ADMIN_AUTH_TOKEN
        and is_admin_candidate
    )
    if not admin_token_ok:
        await verify_token_with_fallback(installation_id, authorization)

    try:
        result = {
            "eligible": False,
            "reason": "",
            "reason_de": "",
            "model_hash": None,
            "model_metadata": None,
            "model_available": False,
            "update_available": False,
            "data_pool": await get_data_pool_stats(request),
        }

        # Check if Admin (Legacy Env + New Role System)
        role = installation_manager.get_role(installation_id)
        is_banned_check = installation_manager.is_banned(installation_id)
        active_bans = installation_manager.get_active_bans(installation_id)

        is_admin_check = (
            installation_id.lower() in ADMIN_IDS
            or installation_manager.has_role_or_higher(
                installation_id, InstallationRole.ADMIN
            )
        )

        logger.info(
            "eligibility_check",
            installation_id=mask_id(installation_id),
            is_admin=is_admin_check,
            role=role.value,
        )

        # Add role and ban info to response
        result["role"] = role.value
        result["is_banned"] = is_banned_check
        result["active_bans"] = active_bans

        is_admin_authorized = False
        if is_admin_check:
            try:
                await verify_admin(authorization, installation_id)
                is_admin_authorized = True
            except HTTPException:
                # Do not expose admin-only server stats without dedicated admin auth.
                is_admin_authorized = False

        if is_admin_authorized:
            result["is_admin"] = True
            logger.info("admin_access_verified", installation_id=installation_id)
            # Fetch server stats for admins
            try:

                def _get_admin_models():
                    models = []
                    m_dir = Path(MODEL_DIR)
                    if m_dir.exists():
                        for mf in m_dir.glob("*.enc"):
                            models.append(
                                {
                                    "name": mf.stem.replace("_", " "),
                                    "size": mf.stat().st_size,
                                    "modified": mf.stat().st_mtime,
                                }
                            )
                    return models

                result["server_stats"] = {
                    "models": await run_sync(_get_admin_models),
                    "active_installations": result["data_pool"]["total_installations"],
                    "total_points": result["data_pool"]["total_data_points"],
                }
            except Exception as e:
                logger.error("admin_stats_error", error=str(e))

        # Check if data pool has enough data
        if not result["data_pool"]["data_sufficient"]:
            result["reason"] = (
                "Community model not yet available - data pool is still growing. "
                "Your data contributions help build the model. Please check back later."
            )
            result["reason_de"] = (
                "Community-Modell noch nicht verfügbar - Datenpool wird noch aufgebaut. "
                "Ihre Datenbeiträge helfen beim Aufbau des Modells. Bitte später erneut prüfen."
            )
            return result

        # Query: Check if this ID appears in the last 30 days
        query = f'last_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{installation_id}"}}[30d])'
        client = request.app.state.http_client
        response = await client.get(VM_QUERY_URL, params={"query": query})

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                result["eligible"] = True
        else:
            logger.warning(
                "vm_eligibility_check_failed",
                status=response.status_code,
                response=response.text[:200],
                installation_id=installation_id,
            )

        if not result["eligible"]:
            result["reason"] = (
                "No data contribution found in the last 30 days. "
                "Enable data sharing to become eligible for community models."
            )
            result["reason_de"] = (
                "Kein Datenbeitrag in den letzten 30 Tagen gefunden. "
                "Aktivieren Sie die Datenfreigabe, um für Community-Modelle berechtigt zu werden."
            )
            return result

        # Check for model availability and hash
        model_dir = Path(MODEL_DIR)
        model_file = None
        metadata_file = None

        if model:
            # Look for model-specific file (model is already validated and normalized)
            try:
                model_file = resolve_model_file(model)
            except HTTPException:
                # Fall back to generic model
                model_file = (model_dir / "community_model.enc").resolve()
            metadata_file = (model_dir / f"{model_file.stem}_metadata.json").resolve()
        else:
            model_file = (model_dir / "community_model.enc").resolve()
            metadata_file = (model_dir / "community_model_metadata.json").resolve()

        # Helper to check existence asynchronously
        exists = await run_sync(model_file.exists) if model_file else False

        if exists:
            result["model_available"] = True
            result["model_hash"] = await get_file_hash(str(model_file))

            # Load metadata if available
            meta_exists = (
                await run_sync(metadata_file.exists) if metadata_file else False
            )
            if meta_exists:
                try:

                    def _load_json(path):
                        with open(path, "r") as f:
                            return json.load(f)

                    result["model_metadata"] = await run_sync(
                        _load_json, str(metadata_file)
                    )
                except Exception as e:
                    logger.warning(
                        "metadata_load_failed", file=str(metadata_file), error=str(e)
                    )

            # Check if update is needed
            if current_hash and result["model_hash"]:
                result["update_available"] = current_hash != result["model_hash"]
            else:
                result["update_available"] = True

            result["reason"] = "Eligible for community model."
            result["reason_de"] = "Berechtigt für Community-Modell."
        else:
            result["reason"] = (
                "Eligible but no model available for your heat pump yet. "
                "Models are created when enough data is collected."
            )
            result["reason_de"] = (
                "Berechtigt, aber noch kein Modell für Ihre Wärmepumpe verfügbar. "
                "Modelle werden erstellt, wenn genügend Daten gesammelt wurden."
            )

        # Add token information (for per-installation token migration)
        result["has_personal_token"] = token_exists(installation_id)
        if result["has_personal_token"]:
            token_info = token_manager.get_token_info(installation_id)
            result["token_info"] = {
                "created_at": token_info.get("created_at") if token_info else None,
                "last_used": token_info.get("last_used") if token_info else None,
                "message": "You have a personal authentication token. Make sure to use it instead of the shared token.",
            }

        # Add encryption key information (for per-installation encryption)
        result["has_personal_encryption_key"] = has_encryption_key(installation_id)
        if result["has_personal_encryption_key"]:
            result["encryption_key_info"] = {
                "message": "You have a personal encryption key for enhanced security. This will be used for future model encryption.",
                "note": "Currently using shared encryption for backward compatibility. Migration to per-installation encryption is planned.",
            }

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "eligibility_check_failed", installation_id=installation_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail="Check failed")


@app.get("/api/v1/model/download")
async def download_model(
    request: Request,
    installation_id: str,
    model: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    """
    Download the community model file.
    Only available to eligible installations (data contributors).

    Args:
        installation_id: Unique installation identifier (for eligibility check)
        model: Optional heat pump model name for model-specific downloads
    """
    # Validation
    validate_installation_id(installation_id)

    # Verify token (per-installation with fallback)
    await verify_token_with_fallback(installation_id, authorization)
    model = validate_model_name(model)  # Returns normalized/validated name or None

    # Check installation ban status
    download_allowed, ban_reason = check_download_allowed(installation_id)
    if not download_allowed:
        logger.warning(
            "model_download_installation_banned",
            installation_id=installation_id,
            reason=ban_reason,
        )
        raise HTTPException(
            status_code=403,
            detail=f"Download blocked: {ban_reason}",
        )

    try:
        # Verify eligibility first
        query = f'last_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{installation_id}"}}[30d])'
        client = request.app.state.http_client
        response = await client.get(VM_QUERY_URL, params={"query": query})

        eligible = False
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                eligible = True

        if not eligible:
            logger.warning(
                "model_download_not_eligible", installation_id=installation_id
            )
            raise HTTPException(
                status_code=403,
                detail="Not eligible. Contribute data for 30 days to access community models.",
            )

        # Find model file
        model_dir = Path(MODEL_DIR)
        model_file = None

        if model:
            # Model is already validated and normalized
            try:
                model_file = resolve_model_file(model)
            except HTTPException:
                model_file = (model_dir / "community_model.enc").resolve()
        else:
            model_file = (model_dir / "community_model.enc").resolve()

        if not model_file.exists():
            logger.warning(
                "model_download_not_found", installation_id=installation_id, model=model
            )
            raise HTTPException(
                status_code=404,
                detail="No model available yet. The community model is still being trained.",
            )

        logger.info(
            "model_download",
            installation_id=installation_id,
            model_file=model_file.name,
        )

        # Track download in Prometheus
        if PROMETHEUS_AVAILABLE:
            model_downloads_total.labels(model=model_file.stem).inc()

        # Log download in audit log
        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = (
            forwarded.split(",")[0].strip()
            if forwarded
            else (request.client.host if request.client else "unknown")
        )
        log_model_download(
            installation_id=installation_id,
            ip_address=client_ip,
            model_name=model_file.stem,
            success=True,
        )

        # Check if installation has personal encryption key
        personal_key = get_encryption_key(installation_id)

        if personal_key:
            # Re-encrypt model with personal key for enhanced security
            logger.info(
                "model_reencrypt_personal",
                installation_id=installation_id,
                model=model_file.stem,
            )

            try:
                # Read encrypted model file (JSON envelope)
                def _read_and_reencrypt():
                    with open(model_file, "r", encoding="utf-8") as f:
                        envelope = json.load(f)

                    # Decrypt with shared key
                    shared_fernet = Fernet(DEFAULT_ENCRYPTION_KEY)
                    encrypted_data = base64.b64decode(envelope["payload"])
                    model_data = shared_fernet.decrypt(encrypted_data)

                    # Encrypt with personal key
                    personal_fernet = Fernet(personal_key)
                    personal_encrypted = personal_fernet.encrypt(model_data)

                    # Create new envelope with personal encryption
                    new_envelope = {
                        "version": envelope.get("version", "2.0"),
                        "metadata": envelope["metadata"].copy(),
                        "payload": base64.b64encode(personal_encrypted).decode("utf-8"),
                        "encryption": "per-installation",  # Mark as personally encrypted
                    }

                    # Add installation info to metadata
                    new_envelope["metadata"]["encrypted_for"] = installation_id
                    new_envelope["metadata"]["encryption_type"] = "per-installation"

                    # Create signature with personal key
                    metadata_json = json.dumps(new_envelope["metadata"], sort_keys=True)
                    msg = f"{new_envelope['payload']}.{metadata_json}".encode("utf-8")
                    signature = hmac.new(personal_key, msg, hashlib.sha256).hexdigest()
                    new_envelope["signature"] = signature

                    return new_envelope

                # Execute re-encryption in thread pool (I/O intensive)
                new_envelope = await asyncio.to_thread(_read_and_reencrypt)

                # Write to temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".enc", delete=False, encoding="utf-8"
                )
                try:
                    json.dump(new_envelope, temp_file, indent=2)
                    temp_file.close()

                    # Return personally encrypted model
                    response = FileResponse(
                        path=temp_file.name,
                        filename=model_file.name,
                        media_type="application/octet-stream",
                        headers={
                            "X-Model-Hash": await get_file_hash(str(model_file)) or "",
                            "X-Model-Name": model_file.stem,
                            "X-Encryption-Type": "per-installation",
                            "X-Encrypted-For": installation_id,
                            "Content-Disposition": f'attachment; filename="{model_file.name}"',
                        },
                    )

                    # Clean up temp file after response
                    response.background = None  # Temp file will be cleaned up by OS

                    logger.info(
                        "model_download_personal_encryption",
                        installation_id=installation_id,
                        model=model_file.stem,
                    )

                    return response

                except Exception as e:
                    # Clean up temp file on error
                    try:
                        os.unlink(temp_file.name)
                    except Exception:
                        pass
                    raise e

            except Exception as e:
                logger.error(
                    "personal_encryption_failed",
                    installation_id=installation_id,
                    error=str(e),
                    fallback_to_shared=True,
                )
                # Fall through to shared encryption on error

        # Return model with shared encryption (default/fallback)
        return FileResponse(
            path=str(model_file),
            filename=model_file.name,
            media_type="application/octet-stream",
            headers={
                "X-Model-Hash": await get_file_hash(str(model_file)) or "",
                "X-Model-Name": model_file.stem,
                "X-Encryption-Type": "shared",
                "Content-Disposition": f'attachment; filename="{model_file.name}"',
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "model_download_failed", installation_id=installation_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail="Download failed")


@app.get("/api/v1/pool/status")
async def data_pool_status(request: Request):
    """
    Get the current status of the data pool.
    Public endpoint - no authentication required.
    Useful for displaying cold start information to users.
    """
    stats = await get_data_pool_stats(request)
    stats["timestamp"] = time.time()
    return stats


@app.get("/api/v1/models")
async def list_available_models(request: Request, auth: None = Depends(verify_token)):
    """
    List all available community models.
    Admin endpoint.
    """
    models = []
    model_dir = Path(MODEL_DIR)

    if model_dir.exists():

        async def _get_model_info(model_file):
            return {
                "name": model_file.stem.replace("_", " "),
                "filename": model_file.name,
                "size_bytes": model_file.stat().st_size,
                "hash": await get_file_hash(str(model_file)),
                "modified": model_file.stat().st_mtime,
            }

        tasks = [_get_model_info(f) for f in model_dir.glob("*.enc")]
        if tasks:
            models = await asyncio.gather(*tasks)

    return {
        "models": models,
        "total": len(models),
        "model_dir": str(model_dir),
    }


@app.get("/api/v1/community/averages")
async def community_averages(
    request: Request,
    model: str,
    metrics: Optional[str] = None,
    auth: None = Depends(verify_token),
):
    """
    Get aggregated community statistics.
    Requires authentication (token).
    Results are cached for 5 minutes to reduce VictoriaMetrics load.
    """
    # Validate Inputs
    validate_model_name(model)

    if not metrics:
        # Default metrics
        metric_list = ["cop_current", "temp_outdoor"]
    else:
        metric_list = [m.strip() for m in metrics.split(",") if m.strip()]
        # Validate metric names to prevent injection (simple alphanumeric + underscore)
        for m in metric_list:
            if not re.match(r"^[a-zA-Z0-9_]+$", m):
                raise HTTPException(status_code=400, detail=f"Invalid metric name: {m}")

    # Create cache key from model and sorted metrics
    cache_key = f"{model}:{','.join(sorted(metric_list))}"

    cached = community_avg_cache.get(cache_key)
    if cached:
        logger.info(
            "community_averages_cache_hit", model=model, metrics=len(metric_list)
        )
        if PROMETHEUS_AVAILABLE:
            cache_hits_total.labels(cache_type="community_averages").inc()
        return cached[0]

    logger.info("community_averages_cache_miss", model=model, metrics=len(metric_list))
    if PROMETHEUS_AVAILABLE:
        cache_misses_total.labels(cache_type="community_averages").inc()
    result = await get_community_averages(
        model, metric_list, client=request.app.state.http_client
    )

    if "error" in result:
        logger.error("community_averages_failed", error=result.get("error"))
        raise HTTPException(status_code=500, detail="Community averages unavailable")

    await community_avg_cache.set(cache_key, result)

    return result


# ==================== ADMIN ENDPOINTS ====================


def _merge_installation_settings(
    existing_metadata: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    merged = json.loads(json.dumps(DEFAULT_INSTALLATION_SETTINGS))
    meta = existing_metadata or {}
    for key in ("telemetry_policy", "alert_tuning", "feature_flags"):
        if isinstance(meta.get(key), dict):
            merged[key].update(meta[key])
    return merged


def _sanitize_installation_settings(
    payload: InstallationSettingsUpdate,
) -> Dict[str, Any]:
    updates: Dict[str, Any] = {}

    if payload.telemetry_policy is not None:
        pol = payload.telemetry_policy
        interval = int(pol.get("upload_interval_seconds", 60))
        sampling = float(pol.get("sampling_ratio", 1.0))
        masking = str(pol.get("pii_masking_level", "standard")).lower()
        if interval < 10 or interval > 86400:
            raise HTTPException(
                status_code=400, detail="upload_interval_seconds must be 10..86400"
            )
        if sampling <= 0 or sampling > 1.0:
            raise HTTPException(
                status_code=400, detail="sampling_ratio must be >0 and <=1.0"
            )
        if masking not in {"low", "standard", "high"}:
            raise HTTPException(
                status_code=400, detail="pii_masking_level must be low|standard|high"
            )
        updates["telemetry_policy"] = {
            "upload_interval_seconds": interval,
            "sampling_ratio": sampling,
            "pii_masking_level": masking,
        }

    if payload.alert_tuning is not None:
        tune = payload.alert_tuning
        threshold = float(tune.get("anomaly_threshold", 0.7))
        cooldown = int(tune.get("cooldown_seconds", 300))
        consecutive = int(tune.get("consecutive_hits", 3))
        if threshold <= 0 or threshold > 1.0:
            raise HTTPException(
                status_code=400, detail="anomaly_threshold must be >0 and <=1.0"
            )
        if cooldown < 0 or cooldown > 86400:
            raise HTTPException(
                status_code=400, detail="cooldown_seconds must be 0..86400"
            )
        if consecutive < 1 or consecutive > 20:
            raise HTTPException(
                status_code=400, detail="consecutive_hits must be 1..20"
            )
        updates["alert_tuning"] = {
            "anomaly_threshold": threshold,
            "cooldown_seconds": cooldown,
            "consecutive_hits": consecutive,
        }

    if payload.feature_flags is not None:
        ff = payload.feature_flags
        updates["feature_flags"] = {
            "next_gen_ai": bool(ff.get("next_gen_ai", False)),
            "new_dashboard": bool(ff.get("new_dashboard", False)),
            "beta_training": bool(ff.get("beta_training", False)),
        }

    return updates


async def verify_admin(
    authorization: Optional[str] = Header(None), installation_id: Optional[str] = None
):
    """
    Verify admin access (token + admin ID).
    Uses dedicated ADMIN_AUTH_TOKEN in strict mode.
    Returns installation_id for use in permission checks.
    """
    # Verify dedicated admin token
    if STRICT_ADMIN_AUTH:
        if not _is_strong_secret(ADMIN_AUTH_TOKEN):
            logger.error(
                "admin_auth_misconfigured",
                strict=True,
                reason="ADMIN_AUTH_TOKEN is missing or weak",
            )
            raise HTTPException(
                status_code=503,
                detail="Admin API disabled: ADMIN_AUTH_TOKEN is missing or weak",
            )
        expected_token = ADMIN_AUTH_TOKEN
    else:
        # Backward compatibility mode only (not recommended for public deployments)
        expected_token = ADMIN_AUTH_TOKEN or AUTH_TOKEN
        if not _is_strong_secret(expected_token):
            logger.warning(
                "admin_auth_weak_token_fallback",
                strict=False,
                reason="Using weak admin token fallback",
            )

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")

    # Verify admin ID
    if not installation_id:
        raise HTTPException(
            status_code=401, detail="Missing installation_id for admin check"
        )
    try:
        _validate_installation_id(installation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    normalized_id = installation_id.lower()

    # Token is valid if it matches expected_token (global admin token) OR if it is a valid per-installation token
    token_is_valid = False
    if scheme.lower() == "bearer":
        if token == expected_token:
            token_is_valid = True
        elif token_exists(normalized_id) and validate_installation_token(
            normalized_id, token
        ):
            token_is_valid = True

    if not token_is_valid:
        raise HTTPException(status_code=403, detail="Invalid Admin Token")

    # Check using new permission system
    if not (is_admin(normalized_id) or normalized_id in ADMIN_IDS):
        logger.warning("unauthorized_admin_access", installation_id=normalized_id)
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    return normalized_id  # Return for use in endpoints


async def check_admin_rate_limit(request: Request) -> None:
    """Check rate limit for admin endpoints."""
    forwarded = request.headers.get("X-Forwarded-For")
    raw_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else "unknown")
    )

    allowed, rate_limit_headers = check_rate_limit(
        raw_ip, "admin", override_limit=ADMIN_RUNTIME_SETTINGS["admin_rate_limit"]
    )
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many admin requests. Please try again later.",
            headers=rate_limit_headers,
        )


@app.get("/api/v1/admin/models")
async def admin_list_models(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: List all models with details. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    # Check permission
    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    model_dir = Path(MODEL_DIR)

    async def _get_model_details(model_file):
        stat = await run_sync(model_file.stat)

        # Get download count from Prometheus counter
        download_count = 0
        if PROMETHEUS_AVAILABLE:
            try:
                # Get the counter value for this specific model
                metric_value = model_downloads_total.labels(
                    model=model_file.stem
                )._value.get()
                download_count = int(metric_value) if metric_value else 0
            except Exception:
                download_count = 0

        return {
            "name": model_file.stem.replace("_", " "),
            "filename": model_file.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "modified": stat.st_mtime,
            "modified_formatted": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)
            ),
            "hash": await get_file_hash(str(model_file)),
            "download_count": download_count,
        }

    models = []
    exists = await run_sync(model_dir.exists)
    if exists:
        model_files = await run_sync(lambda: list(model_dir.glob("*.enc")))
        if model_files:
            models = await asyncio.gather(
                *[_get_model_details(mf) for mf in model_files]
            )

    return {
        "models": sorted(models, key=lambda x: x["modified"], reverse=True),
        "total": len(models),
    }


@app.delete("/api/v1/admin/models/{model_name}")
async def admin_delete_model(
    model_name: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Delete a model file. Requires admin:models permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:models"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:models"
        )

    client_ip = get_client_ip(request)

    model_file = resolve_model_file(model_name)

    try:
        file_hash = (
            await asyncio.to_thread(file_hash_cache.get, str(model_file)) or "unknown"
        )
    except Exception:
        file_hash = "unknown"

    try:
        await asyncio.to_thread(os.remove, model_file)

        logger.info(
            "model_deleted",
            admin_id=admin_id,
            model_name=model_name,
            file_hash=file_hash[:12],
            ip=client_ip,
        )

        log_model_delete(
            admin_id=admin_id,
            ip_address=client_ip,
            model_name=model_name,
            success=True,
            metadata={"file_hash": file_hash[:12] if file_hash else "unknown"},
        )

        if PROMETHEUS_AVAILABLE:
            model_downloads_total.labels(model=model_name).inc()

        return {"success": True, "message": f"Model {model_name} deleted successfully"}

    except Exception as e:
        logger.error("model_delete_failed", error=str(e), model_name=model_name)
        log_model_delete(
            admin_id=admin_id,
            ip_address=client_ip,
            model_name=model_name,
            success=False,
            metadata={"error": "delete_failed"},
        )
        raise HTTPException(status_code=500, detail="Failed to delete model")


@app.post("/api/v1/admin/models/trigger-training")
async def admin_trigger_training(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    target_model: Optional[str] = None,
    target_installation_id: Optional[str] = None,
    min_points: Optional[int] = None,
    min_installations: Optional[int] = None,
    lookback_days: Optional[int] = None,
    dry_run: bool = False,
):
    """Admin: Trigger manual model training. Requires admin:training permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:training"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:training"
        )

    client_ip = get_client_ip(request)
    normalized_target_model = validate_model_name(target_model)
    if target_installation_id:
        target_installation_id = validate_installation_id(target_installation_id)

    try:
        script_args = []
        if normalized_target_model:
            script_args.extend(["--target-model", normalized_target_model])
        if target_installation_id:
            # Single-device training: explicitly allow one installation as source.
            script_args.extend(
                [
                    "--target-installation-id",
                    target_installation_id,
                    "--min-installations",
                    "1",
                ]
            )

        if min_points is not None:
            if min_points < 100 or min_points > 10_000_000:
                raise HTTPException(
                    status_code=400, detail="min_points must be 100..10000000"
                )
            script_args.extend(["--min-points", str(int(min_points))])
        if min_installations is not None:
            if min_installations < 1 or min_installations > 1000:
                raise HTTPException(
                    status_code=400, detail="min_installations must be 1..1000"
                )
            script_args.extend(["--min-installations", str(int(min_installations))])
        if lookback_days is not None:
            if lookback_days < 1 or lookback_days > 365:
                raise HTTPException(
                    status_code=400, detail="lookback_days must be 1..365"
                )
            script_args.extend(["--lookback-days", str(int(lookback_days))])

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": "Training request is valid. No job was queued.",
                "args": script_args,
                "target_model": normalized_target_model,
                "target_installation_id": target_installation_id,
            }

        task_id = await training_queue.enqueue_training(
            triggered_by=admin_id,
            script_path="/app/scripts/train_models.py",
            script_args=script_args,
            target_model=normalized_target_model,
            target_installation_id=target_installation_id,
            max_queued_tasks=ADMIN_RUNTIME_SETTINGS["max_training_queue"],
            max_parallel_tasks=ADMIN_RUNTIME_SETTINGS["max_parallel_training"],
        )

        logger.info("admin_training_queued", admin_id=admin_id, task_id=task_id)

        log_training_trigger(
            admin_id=admin_id,
            ip_address=client_ip,
            success=True,
            metadata={
                "task_id": task_id,
                "status": "queued",
                "target_model": normalized_target_model,
                "target_installation_id": target_installation_id,
            },
        )

        return {
            "success": True,
            "message": "Training queued successfully. Use task_id to check progress.",
            "task_id": task_id,
            "status": "queued",
            "target_model": normalized_target_model,
            "target_installation_id": target_installation_id,
            "check_status_url": f"/api/v1/admin/training/status/{task_id}",
        }

    except ValueError as e:
        logger.warning("training_already_running", admin_id=admin_id, error=str(e))

        log_training_trigger(
            admin_id=admin_id,
            ip_address=client_ip,
            success=False,
            metadata={"error": "already_running", "reason": "already_running"},
        )

        raise HTTPException(status_code=409, detail=str(e))

    except Exception as e:
        logger.error("admin_training_trigger_failed", error=str(e))

        log_training_trigger(
            admin_id=admin_id,
            ip_address=client_ip,
            success=False,
            metadata={"error": str(e)},
        )

        raise HTTPException(status_code=500, detail="Failed to trigger training")


@app.get("/api/v1/admin/training/status/{task_id}")
async def admin_get_training_status(
    task_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get training task status. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    try:
        task_status = training_queue.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=404, detail=f"Training task {task_id} not found"
            )

        return {"task_id": task_id, **task_status}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_training_status_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get training status")


@app.get("/api/v1/admin/training/history")
async def admin_get_training_history(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    limit: int = 20,
):
    """Admin: Get recent training history. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    try:
        limit = min(limit, 100)

        tasks = training_queue.get_recent_tasks(limit=limit)

        return {
            "tasks": tasks,
            "count": len(tasks),
            "limit": limit,
        }

    except Exception as e:
        logger.error("get_training_history_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get training history")


@app.get("/api/v1/admin/training/current")
async def admin_get_current_training(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get currently running training task. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    try:
        current_task = training_queue.get_current_task()

        if not current_task:
            return {"running": False, "message": "No training task currently running"}

        return {"running": True, **current_task}

    except Exception as e:
        logger.error("get_current_training_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get current training")


@app.post("/api/v1/admin/training/cancel/{task_id}")
async def admin_cancel_training(
    task_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Cancel a running training task. Requires admin:training permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:training"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:training"
        )

    try:
        cancelled = await training_queue.cancel_training(task_id)

        if not cancelled:
            raise HTTPException(
                status_code=400,
                detail="Task not found, not running, or already completed",
            )

        logger.info("admin_training_cancelled", admin_id=admin_id, task_id=task_id)

        return {
            "success": True,
            "message": f"Training task {task_id} cancelled",
            "task_id": task_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("cancel_training_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel training")


@app.get("/api/v1/admin/installations")
async def admin_list_installations(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    limit: int = 100,
):
    """Admin: List all active installations with stats."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    try:
        client = request.app.state.http_client

        list_query = 'count by (installation_id) ({__name__=~"heatpump_metrics_.*"})'

        time_query = 'max(tlast_over_time({__name__=~"heatpump_metrics_.*"}[30d])) by (installation_id)'

        list_response, time_response = await asyncio.gather(
            client.get(VM_QUERY_URL, params={"query": list_query}),
            client.get(VM_QUERY_URL, params={"query": time_query}),
        )

        installation_times = {}
        if time_response.status_code == 200:
            data = orjson.loads(time_response.content)
            if data.get("status") == "success":
                for result in data["data"]["result"]:
                    inst_id = result["metric"].get("installation_id", "unknown")
                    ts = float(result["value"][1]) if result.get("value") else 0
                    installation_times[inst_id] = ts

        installations = []
        if list_response.status_code == 200:
            data = orjson.loads(list_response.content)
            if data.get("status") == "success":
                for result in data["data"]["result"]:
                    inst_id = result["metric"].get("installation_id", "unknown")
                    count = int(result["value"][1]) if result.get("value") else 0

                    last_seen = installation_times.get(inst_id)
                    info = installation_manager.get_installation(inst_id) or {}
                    role = info.get("effective_role", "guest")
                    is_banned = bool(info.get("is_banned", False))

                    installations.append(
                        {
                            "installation_id": inst_id,
                            "data_points": count,
                            "last_seen": last_seen,
                            "last_seen_formatted": (
                                time.strftime(
                                    "%Y-%m-%d %H:%M:%S", time.localtime(last_seen)
                                )
                                if last_seen
                                else "Unknown"
                            ),
                            "is_admin": inst_id.lower() in ADMIN_IDS,
                            "role": role,
                            "is_banned": is_banned,
                        }
                    )

        installations.sort(key=lambda x: x.get("last_seen") or 0, reverse=True)

        return {
            "installations": installations[:limit],
            "total": len(installations),
            "showing": min(len(installations), limit),
        }
    except Exception as e:
        logger.error("admin_installations_list_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list installations")


@app.get("/api/v1/admin/installations/{target_id}/details")
async def admin_installation_details(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get detailed information about a specific installation."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    validate_installation_id(target_id)

    try:
        client = request.app.state.http_client

        metrics_query = (
            f'{{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}'
        )

        timestamps_query = f'count_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[30d])'

        first_seen_query = f'min_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[30d])'

        last_seen_query = f'last_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[30d])'

        all_installations_query = (
            "group by(installation_id) (count by (installation_id))"
        )

        cached_rank_result = await contribution_rank_cache.get()
        cached_rank_data = cached_rank_result[0] if cached_rank_result else None
        use_cache = cached_rank_data is not None

        tasks = [
            client.get(VM_QUERY_URL, params={"query": metrics_query}),
            client.get(VM_QUERY_URL, params={"query": timestamps_query}),
            client.get(VM_QUERY_URL, params={"query": first_seen_query}),
            client.get(VM_QUERY_URL, params={"query": last_seen_query}),
        ]
        if not use_cache:
            tasks.append(
                client.get(VM_QUERY_URL, params={"query": all_installations_query})
            )

        results_list = await asyncio.gather(*tasks)

        response = results_list[0]
        count_resp = results_list[1]
        first_resp = results_list[2]
        last_resp = results_list[3]
        rank_resp = results_list[4] if not use_cache else None

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Installation not found")

        data = response.json()
        if not data.get("data") or not data["data"].get("result"):
            raise HTTPException(
                status_code=404, detail="No data found for this installation"
            )

        results = data["data"]["result"]

        heatpump_model = "Unknown"
        for result in results:
            metric = result.get("metric", {})
            if "model" in metric:
                heatpump_model = metric["model"]
                break
            if "heatpump_model" in metric:
                heatpump_model = metric["heatpump_model"]
                break

        unique_metrics = len(set(r["metric"]["__name__"] for r in results))
        data_quality_score = min(1.0, unique_metrics / 20.0)

        total_submissions = 0
        if count_resp.status_code == 200:
            count_data = count_resp.json()
            if count_data.get("data") and count_data["data"].get("result"):
                total_submissions = sum(
                    int(float(r["value"][1]))
                    for r in count_data["data"]["result"]
                    if r.get("value") and len(r["value"]) > 1
                )

        first_seen = None
        if first_resp.status_code == 200:
            first_data = first_resp.json()
            if first_data.get("data") and first_data["data"].get("result"):
                timestamps = [
                    float(r["value"][0])
                    for r in first_data["data"]["result"]
                    if r.get("value")
                ]
                if timestamps:
                    first_seen = min(timestamps)

        last_seen = None
        if last_resp.status_code == 200:
            last_data = last_resp.json()
            if (
                last_data.get("data")
                and last_data["data"]["result"]
                and last_data["data"]["result"][0].get("value")
                and len(last_data["data"]["result"][0]["value"]) > 0
            ):
                last_seen = float(last_data["data"]["result"][0]["value"][0])

        model_downloads = []
        try:
            from audit_log import get_audit_logs

            logs = get_audit_logs(
                action="model_download", installation_id=target_id, limit=50
            )
            model_downloads = [
                {
                    "model": log.get("metadata", {}).get("model", "Unknown"),
                    "downloaded_at": log.get("timestamp"),
                }
                for log in logs
            ]
        except Exception:
            pass

        contribution_rank = "Unknown"
        if use_cache and cached_rank_data:
            rank_data = cached_rank_data
        elif rank_resp and rank_resp.status_code == 200:
            rank_data = rank_resp.json()
            await contribution_rank_cache.set(rank_data)
        else:
            rank_data = None

        if rank_data and rank_data.get("data") and rank_data["data"].get("result"):
            counts = [
                (r["metric"].get("installation_id"), int(r["value"][1]))
                for r in rank_data["data"]["result"]
                if r.get("value") and len(r["value"]) > 1
            ]
            counts.sort(key=lambda x: x[1], reverse=True)

            total_installs = len(counts)
            for idx, (inst_id, _) in enumerate(counts):
                if inst_id == target_id:
                    percentile = ((idx + 1) / total_installs) * 100
                    if percentile <= 10:
                        contribution_rank = "Top 10%"
                    elif percentile <= 25:
                        contribution_rank = "Top 25%"
                    elif percentile <= 50:
                        contribution_rank = "Top 50%"
                    else:
                        contribution_rank = f"Top {int(percentile)}%"
                    break

        return {
            "installation_id": target_id,
            "heatpump_model": heatpump_model,
            "first_seen": (
                datetime.fromtimestamp(first_seen, timezone.utc).isoformat()
                if first_seen
                else None
            ),
            "last_seen": (
                datetime.fromtimestamp(last_seen, timezone.utc).isoformat()
                if last_seen
                else None
            ),
            "total_submissions": total_submissions,
            "data_quality_score": round(data_quality_score, 2),
            "model_downloads": model_downloads,
            "contribution_rank": contribution_rank,
            "unique_metrics": unique_metrics,
            "is_admin": target_id.lower() in ADMIN_IDS,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "admin_installation_details_failed", error=str(e), installation_id=target_id
        )
        raise HTTPException(
            status_code=500, detail="Failed to get installation details"
        )


@app.get("/api/v1/admin/installations/{target_id}/history")
async def admin_installation_history(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    limit: int = 50,
):
    """Admin: Get submission history for a specific installation."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    validate_installation_id(target_id)

    try:
        client = request.app.state.http_client

        query = f'count_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[1h])'
        response = await client.get(
            VM_QUERY_URL.replace("/query", "/query_range"),
            params={
                "query": query,
                "start": int(time.time()) - 30 * 24 * 3600,
                "end": int(time.time()),
                "step": "3600",
            },
        )

        history = []
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("result"):
                for result in data["data"]["result"]:
                    metric_name = result["metric"].get("__name__", "unknown")
                    for timestamp, value in result.get("values", []):
                        history.append(
                            {
                                "timestamp": datetime.fromtimestamp(
                                    float(timestamp), timezone.utc
                                ).isoformat(),
                                "metric": metric_name,
                                "count": int(float(value)),
                            }
                        )

        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "installation_id": target_id,
            "history": history[:limit],
            "total": len(history),
        }

    except Exception as e:
        logger.error(
            "admin_installation_history_failed", error=str(e), installation_id=target_id
        )
        raise HTTPException(
            status_code=500, detail="Failed to get installation history"
        )


@app.get("/api/v1/admin/health")
async def admin_server_health(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get server health stats."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    try:
        import psutil
        import platform

        def _get_system_stats():
            return {
                "hostname": platform.node(),
                "boot_time": psutil.boot_time(),
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory": psutil.virtual_memory(),
                "disk": psutil.disk_usage("/"),
            }

        sys_stats = await asyncio.to_thread(_get_system_stats)

        vm_response = await request.app.state.http_client.get(f"{VM_QUERY_URL}/health")
        vm_healthy = vm_response.status_code == 200

        def _get_model_stats():
            model_dir = Path(MODEL_DIR)
            if not model_dir.exists():
                return 0, 0
            files = list(model_dir.glob("*.enc"))
            count = len(files)
            size = sum(f.stat().st_size for f in files)
            return count, size

        model_count, total_size = await asyncio.to_thread(_get_model_stats)

        return {
            "server": {
                "hostname": sys_stats["hostname"],
                "uptime": time.time() - sys_stats["boot_time"],
                "uptime_formatted": str(
                    timedelta(seconds=int(time.time() - sys_stats["boot_time"]))
                ),
                "cpu_percent": sys_stats["cpu_percent"],
                "memory": {
                    "total_gb": round(
                        sys_stats["memory"].total / 1024 / 1024 / 1024, 2
                    ),
                    "available_gb": round(
                        sys_stats["memory"].available / 1024 / 1024 / 1024, 2
                    ),
                    "used_gb": round(sys_stats["memory"].used / 1024 / 1024 / 1024, 2),
                    "percent": sys_stats["memory"].percent,
                },
                "disk": {
                    "total_gb": round(sys_stats["disk"].total / 1024 / 1024 / 1024, 2),
                    "used_gb": round(sys_stats["disk"].used / 1024 / 1024 / 1024, 2),
                    "free_gb": round(sys_stats["disk"].free / 1024 / 1024 / 1024, 2),
                    "percent": sys_stats["disk"].percent,
                },
            },
            "victoriametrics": {
                "healthy": vm_healthy,
                "url": VM_QUERY_URL,
            },
            "models": {
                "count": model_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
            },
            "admin_ids": list(ADMIN_IDS),
            "timestamp": time.time(),
        }
    except ImportError:
        raise HTTPException(status_code=501, detail="psutil not installed")
    except Exception as e:
        logger.error("admin_health_check_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/api/v1/admin/metrics")
async def admin_get_metrics(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get metrics for monitoring dashboard."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    if not PROMETHEUS_AVAILABLE:
        raise HTTPException(
            status_code=501, detail="Metrics not available. Install prometheus_client."
        )

    try:
        from prometheus_client import REGISTRY

        metrics_data = {}
        metrics_cache = []
        try:
            for collector in REGISTRY._collector_to_names.keys():
                for metric in collector.collect():
                    for sample in metric.samples:
                        metrics_cache.append((metric.name, sample.labels, sample.value))
        except Exception as e:
            logger.warning("metrics_collection_partial_failure", error=str(e))

        def get_metric_value(metric_name, labels=None):
            try:
                for name, sample_labels, value in metrics_cache:
                    if name == metric_name:
                        if labels:
                            if all(sample_labels.get(k) == v for k, v in labels.items()):
                                return value
                        else:
                            return value
                return 0
            except Exception:
                return 0

        metrics_data["requests"] = {
            "total": get_metric_value("telemetry_requests_total"),
            "errors": get_metric_value("telemetry_errors_total"),
            "rate_limit_hits": get_metric_value("rate_limit_hits_total"),
        }

        metrics_data["business"] = {
            "submissions": get_metric_value("telemetry_data_submissions_total"),
            "data_points": get_metric_value("telemetry_data_points_submitted_total"),
            "model_downloads": get_metric_value("model_downloads_total"),
            "training_runs": get_metric_value("telemetry_training_runs_total"),
            "active_installations": get_metric_value("telemetry_active_installations"),
        }

        metrics_data["cache"] = {
            "hits": get_metric_value("telemetry_cache_hits_total"),
            "misses": get_metric_value("telemetry_cache_misses_total"),
            "hit_rate": 0.0,
        }

        total_cache_requests = (
            metrics_data["cache"]["hits"] + metrics_data["cache"]["misses"]
        )
        if total_cache_requests > 0:
            metrics_data["cache"]["hit_rate"] = (
                metrics_data["cache"]["hits"] / total_cache_requests
            ) * 100

        metrics_data["performance"] = {
            "avg_request_duration_ms": 0.0,
            "p95_request_duration_ms": 0.0,
            "p99_request_duration_ms": 0.0,
        }

        return metrics_data

    except Exception as e:
        logger.error("admin_metrics_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@app.get("/api/v1/admin/audit-log")
async def admin_get_audit_log(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    limit: int = 100,
    action: Optional[str] = None,
    admin_filter: Optional[str] = None,
    success_only: Optional[bool] = None,
    format: Optional[str] = None,
):
    """Admin: Get audit log events."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    try:
        limit = min(limit, 500)

        if action:
            events = await asyncio.to_thread(
                audit_logger.get_events_by_action, action, limit=limit
            )
        elif admin_filter:
            events = await asyncio.to_thread(
                audit_logger.get_events_by_admin, admin_filter, limit=limit
            )
        else:
            events = await asyncio.to_thread(
                audit_logger.get_recent_events, limit=limit
            )

        if success_only is not None:
            wanted = "success" if success_only else "failure"
            events = [e for e in events if str(e.get("result", "")).lower() == wanted]

        if format and format.lower() == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "timestamp",
                    "action",
                    "admin_id",
                    "ip_address",
                    "resource",
                    "result",
                    "metadata",
                ],
            )
            writer.writeheader()
            for event in events:
                writer.writerow(
                    {
                        "timestamp": event.get("timestamp"),
                        "action": event.get("action"),
                        "admin_id": event.get("admin_id"),
                        "ip_address": event.get("ip_address"),
                        "resource": event.get("resource"),
                        "result": event.get("result"),
                        "metadata": json.dumps(
                            event.get("metadata", {}), ensure_ascii=False
                        ),
                    }
                )

            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="telemetry_audit_log.csv"'
                },
            )

        return {
            "events": events,
            "count": len(events),
            "limit": limit,
            "filters": {
                "action": action,
                "admin_filter": admin_filter,
                "success_only": success_only,
            },
        }
    except Exception as e:
        logger.error("admin_audit_log_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get audit log")


# ==================== PERMISSION MANAGEMENT ENDPOINTS ====================


@app.get("/api/v1/admin/runtime-limits")
async def admin_get_runtime_limits(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get runtime limits. Requires admin:full permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)
    if not has_permission(admin_id, "admin:full"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:full"
        )
    return {"limits": ADMIN_RUNTIME_SETTINGS}


@app.put("/api/v1/admin/runtime-limits")
async def admin_update_runtime_limits(
    payload: RuntimeLimitsUpdate,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Update runtime limits. Requires admin:full permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)
    if not has_permission(admin_id, "admin:full"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:full"
        )

    updates = {}
    if payload.admin_rate_limit is not None:
        if payload.admin_rate_limit < 1 or payload.admin_rate_limit > 10000:
            raise HTTPException(
                status_code=400, detail="admin_rate_limit must be 1..10000"
            )
        updates["admin_rate_limit"] = int(payload.admin_rate_limit)
    if payload.max_training_queue is not None:
        if payload.max_training_queue < 1 or payload.max_training_queue > 1000:
            raise HTTPException(
                status_code=400, detail="max_training_queue must be 1..1000"
            )
        updates["max_training_queue"] = int(payload.max_training_queue)
    if payload.max_parallel_training is not None:
        if payload.max_parallel_training != 1:
            raise HTTPException(
                status_code=400,
                detail="max_parallel_training currently supports only value 1",
            )
        updates["max_parallel_training"] = int(payload.max_parallel_training)
    if payload.min_installations is not None:
        if payload.min_installations < 1 or payload.min_installations > 1000:
            raise HTTPException(
                status_code=400, detail="min_installations must be 1..1000"
            )
        updates["min_installations"] = int(payload.min_installations)
    if payload.min_data_points is not None:
        if payload.min_data_points < 0 or payload.min_data_points > 10_000_000:
            raise HTTPException(
                status_code=400, detail="min_data_points must be 0..10000000"
            )
        updates["min_data_points"] = int(payload.min_data_points)

    ADMIN_RUNTIME_SETTINGS.update(updates)
    audit_logger.log(
        action="runtime_limits_update",
        admin_id=admin_id,
        ip_address=get_client_ip(request),
        resource="runtime_limits",
        result="success",
        metadata={"updates": updates},
    )
    return {"success": True, "limits": ADMIN_RUNTIME_SETTINGS}


@app.get("/api/v1/admin/permissions/presets")
async def admin_get_permission_presets(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get permission presets. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)
    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )
    return {"presets": PERMISSION_PRESETS}


@app.post("/api/v1/admin/permissions/apply-preset")
async def admin_apply_permission_preset(
    payload: PermissionPresetApply,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Apply a permission preset to an admin. Requires admin:full permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)
    if not has_permission(admin_id, "admin:full"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:full"
        )

    preset_name = payload.preset.strip().lower()
    if preset_name not in PERMISSION_PRESETS:
        raise HTTPException(status_code=400, detail=f"Unknown preset: {preset_name}")

    target_id = payload.target_admin_id.strip().lower()
    desired = set(PERMISSION_PRESETS[preset_name])
    current_info = permission_manager.get_admin_info(target_id) or {}
    current = set(current_info.get("permissions", []))

    to_add = desired - current
    to_remove = set()
    if not payload.merge:
        to_remove = current - desired

    for perm in sorted(to_add):
        permission_manager.grant_permission(target_id, perm, granted_by=admin_id)
    for perm in sorted(to_remove):
        if target_id == admin_id.lower() and perm == "admin:full":
            continue
        permission_manager.revoke_permission(target_id, perm, revoked_by=admin_id)

    audit_logger.log(
        action="permission_preset_applied",
        admin_id=admin_id,
        ip_address=get_client_ip(request),
        resource=target_id,
        result="success",
        metadata={"preset": preset_name, "merge": payload.merge},
    )

    return {
        "success": True,
        "target_admin_id": target_id,
        "preset": preset_name,
        "merge": payload.merge,
        "permissions": permission_manager.get_admin_info(target_id),
    }


@app.get("/api/v1/admin/permissions")
async def admin_list_permissions(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: List all admins and their permissions. Requires admin:full permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:full"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:full"
        )

    try:
        admins = permission_manager.list_admins()
        return {
            "admins": admins,
            "total": len(admins),
            "available_permissions": PERMISSIONS,
        }
    except Exception as e:
        logger.error("admin_list_permissions_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list permissions")


@app.post("/api/v1/admin/permissions/grant")
async def admin_grant_permission(
    request: Request,
    target_admin_id: str,
    permission: str,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Grant a permission to another admin. Requires admin:full permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:full"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:full"
        )

    try:
        if permission not in PERMISSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid permission. Must be one of: {list(PERMISSIONS.keys())}",
            )

        granted = permission_manager.grant_permission(
            target_admin_id, permission, granted_by=admin_id
        )

        if granted:
            logger.info(
                "permission_granted",
                target=target_admin_id,
                permission=permission,
                by=admin_id,
            )
            return {
                "success": True,
                "message": f"Permission {permission} granted to {target_admin_id}",
                "target_admin_id": target_admin_id,
                "permission": permission,
                "granted_by": admin_id,
            }
        else:
            return {
                "success": False,
                "message": f"Permission {permission} already exists for {target_admin_id}",
                "target_admin_id": target_admin_id,
                "permission": permission,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("admin_grant_permission_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to grant permission")


@app.post("/api/v1/admin/permissions/revoke")
async def admin_revoke_permission(
    request: Request,
    target_admin_id: str,
    permission: str,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Revoke a permission from another admin. Requires admin:full permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:full"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:full"
        )

    if target_admin_id.lower() == admin_id.lower() and permission == "admin:full":
        raise HTTPException(
            status_code=400, detail="Cannot revoke your own admin:full permission"
        )

    try:
        revoked = permission_manager.revoke_permission(
            target_admin_id, permission, revoked_by=admin_id
        )

        if revoked:
            logger.info(
                "permission_revoked",
                target=target_admin_id,
                permission=permission,
                by=admin_id,
            )
            return {
                "success": True,
                "message": f"Permission {permission} revoked from {target_admin_id}",
                "target_admin_id": target_admin_id,
                "permission": permission,
                "revoked_by": admin_id,
            }
        else:
            return {
                "success": False,
                "message": f"Permission {permission} not found for {target_admin_id}",
                "target_admin_id": target_admin_id,
                "permission": permission,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("admin_revoke_permission_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to revoke permission")


@app.get("/api/v1/admin/permissions/{target_admin_id}")
async def admin_get_permissions(
    target_admin_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get permissions for a specific admin. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    try:
        admin_info = permission_manager.get_admin_info(target_admin_id)

        if not admin_info:
            raise HTTPException(
                status_code=404, detail=f"Admin {target_admin_id} not found"
            )

        return {
            "admin_id": target_admin_id,
            "permissions": admin_info,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("admin_get_permissions_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get permissions")


# =====================================================================
# Installation Role and Ban Management Endpoints
# =====================================================================


@app.get("/api/v1/admin/installations/roles")
async def admin_get_role_definitions(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get role definitions and features. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    return {
        "roles": [
            {
                "name": role.value,
                "description": ROLE_DESCRIPTIONS.get(role, ""),
                "features": ROLE_FEATURES.get(role, []),
            }
            for role in InstallationRole
        ],
        "ban_types": [
            {"name": bt.value, "description": f"{bt.value.title()} ban"}
            for bt in BanType
        ],
    }


@app.get("/api/v1/admin/installations/stats")
async def admin_get_installation_stats(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get installation statistics. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    return installation_manager.get_stats()


@app.get("/api/v1/admin/installations/list")
async def admin_list_installations_filtered(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    role: Optional[str] = None,
    banned_only: bool = False,
    limit: int = 100,
    offset: int = 0,
):
    """Admin: List installations with filters. Requires admin:users permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:users"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:users"
        )

    role_filter = None
    if role:
        try:
            role_filter = InstallationRole(role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")

    return installation_manager.list_installations(
        role_filter=role_filter,
        banned_only=banned_only,
        limit=min(limit, 500),
        offset=offset,
    )


@app.get("/api/v1/admin/installations/{target_id}/role")
async def admin_get_installation_role(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get role and ban status for an installation. Requires admin:view permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    info = installation_manager.get_installation(target_id)

    return {
        "installation_id": target_id,
        "role": info["effective_role"] if info else "guest",
        "is_banned": info["is_banned"] if info else False,
        "active_bans": info["active_bans"] if info else [],
        "notes": info.get("notes", "") if info else "",
        "created_at": info.get("created_at") if info else None,
        "metadata": info.get("metadata", {}) if info else {},
    }


@app.get("/api/v1/admin/installations/{target_id}/settings")
async def admin_get_installation_settings(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Get telemetry policy, alert tuning and feature flags for an installation."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:view"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:view"
        )

    info = installation_manager.get_installation(target_id)
    metadata = info.get("metadata", {}) if info else {}
    settings = _merge_installation_settings(metadata)

    return {"installation_id": target_id, "settings": settings}


@app.put("/api/v1/admin/installations/{target_id}/settings")
async def admin_update_installation_settings(
    target_id: str,
    payload: InstallationSettingsUpdate,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Update telemetry policy, alert tuning and feature flags for an installation."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:users"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:users"
        )

    updates = _sanitize_installation_settings(payload)
    if not updates:
        raise HTTPException(status_code=400, detail="No settings provided")

    installation_manager.update_metadata(target_id, updates, updated_by=admin_id)
    merged = _merge_installation_settings(
        (installation_manager.get_installation(target_id) or {}).get("metadata", {})
    )

    audit_logger.log(
        action="installation_settings_update",
        admin_id=admin_id,
        ip_address=get_client_ip(request),
        resource=target_id,
        result="success",
        metadata={"updated_keys": list(updates.keys())},
    )

    return {"success": True, "installation_id": target_id, "settings": merged}


@app.post("/api/v1/admin/installations/{target_id}/role")
async def admin_set_installation_role(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    role: str = None,
    reason: Optional[str] = None,
):
    """Admin: Set role for an installation. Requires admin:users permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:users"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:users"
        )

    if not role:
        raise HTTPException(status_code=400, detail="role parameter is required")

    try:
        new_role = InstallationRole(role)
    except ValueError:
        valid_roles = [r.value for r in InstallationRole]
        raise HTTPException(
            status_code=400, detail=f"Invalid role: {role}. Valid: {valid_roles}"
        )

    changed = installation_manager.set_role(
        target_id,
        new_role,
        set_by=admin_id,
        reason=reason,
    )

    logger.info(
        "admin_set_role",
        admin_id=admin_id,
        target_id=target_id,
        role=role,
        changed=changed,
    )

    return {
        "success": True,
        "installation_id": target_id,
        "role": role,
        "changed": changed,
        "set_by": admin_id,
    }


@app.post("/api/v1/admin/installations/{target_id}/ban")
async def admin_ban_installation(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    ban_type: str = "full",
    reason: str = None,
    duration_hours: Optional[int] = None,
):
    """Admin: Ban an installation. Requires admin:users permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:users"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:users"
        )

    if not reason:
        raise HTTPException(status_code=400, detail="reason parameter is required")

    try:
        bt = BanType(ban_type)
    except ValueError:
        valid_types = [t.value for t in BanType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ban_type: {ban_type}. Valid: {valid_types}",
        )

    ban_record = installation_manager.ban_installation(
        target_id,
        bt,
        banned_by=admin_id,
        reason=reason,
        duration_hours=duration_hours,
    )

    logger.warning(
        "admin_ban_installation",
        admin_id=admin_id,
        target_id=target_id,
        ban_type=ban_type,
        reason=reason,
        duration_hours=duration_hours,
    )

    return {
        "success": True,
        "installation_id": target_id,
        "ban": ban_record,
        "message": f"Installation {target_id} has been banned ({ban_type})"
        + (f" for {duration_hours} hours" if duration_hours else " permanently"),
    }


@app.post("/api/v1/admin/installations/{target_id}/unban")
async def admin_unban_installation(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    ban_type: str = "full",
    reason: Optional[str] = None,
):
    """Admin: Remove a ban from an installation. Requires admin:users permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:users"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:users"
        )

    try:
        bt = BanType(ban_type)
    except ValueError:
        valid_types = [t.value for t in BanType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ban_type: {ban_type}. Valid: {valid_types}",
        )

    success = installation_manager.unban_installation(
        target_id,
        bt,
        unbanned_by=admin_id,
        reason=reason,
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No active {ban_type} ban found for {target_id}",
        )

    logger.info(
        "admin_unban_installation",
        admin_id=admin_id,
        target_id=target_id,
        ban_type=ban_type,
    )

    return {
        "success": True,
        "installation_id": target_id,
        "ban_type": ban_type,
        "message": f"Ban removed for {target_id}",
    }


@app.post("/api/v1/admin/installations/{target_id}/notes")
async def admin_set_installation_notes(
    target_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    notes: str = "",
):
    """Admin: Set notes for an installation. Requires admin:users permission."""
    await check_admin_rate_limit(request)
    admin_id = await verify_admin(authorization, installation_id)

    if not has_permission(admin_id, "admin:users"):
        raise HTTPException(
            status_code=403, detail="Insufficient permissions. Required: admin:users"
        )

    installation_manager.set_notes(target_id, notes, set_by=admin_id)

    return {
        "success": True,
        "installation_id": target_id,
        "notes": notes,
    }


# Prometheus Metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest

    telemetry_requests_total = Counter(
        "telemetry_requests_total", "Total telemetry requests received", ["endpoint"]
    )
    telemetry_errors_total = Counter(
        "telemetry_errors_total", "Total errors occurred", ["endpoint", "error_type"]
    )
    request_duration_seconds = Histogram(
        "telemetry_request_duration_seconds",
        "Request duration in seconds",
        ["endpoint"],
    )
    model_downloads_total = Counter(
        "model_downloads_total", "Total model downloads", ["model"]
    )
    rate_limit_hits_total = Counter(
        "rate_limit_hits_total", "Total rate limit violations"
    )

    data_submissions_total = Counter(
        "telemetry_data_submissions_total", "Total data submissions", ["heatpump_model"]
    )
    data_points_submitted_total = Counter(
        "telemetry_data_points_submitted_total", "Total data points submitted"
    )
    training_runs_total = Counter(
        "telemetry_training_runs_total", "Total training runs", ["result"]
    )
    training_duration_seconds = Histogram(
        "telemetry_training_duration_seconds", "Training duration in seconds"
    )
    active_installations = Gauge(
        "telemetry_active_installations", "Number of active installations"
    )
    cache_hits_total = Counter(
        "telemetry_cache_hits_total", "Total cache hits", ["cache_type"]
    )
    cache_misses_total = Counter(
        "telemetry_cache_misses_total", "Total cache misses", ["cache_type"]
    )
    telemetry_http_responses_total = Counter(
        "telemetry_http_responses_total",
        "HTTP responses by endpoint and status code",
        ["endpoint", "status_code"],
    )
    telemetry_security_events_total = Counter(
        "telemetry_security_events_total",
        "Security-relevant events",
        ["event_type"],
    )
    telemetry_admin_requests_total = Counter(
        "telemetry_admin_requests_total",
        "Total requests to admin endpoints",
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning(
        "prometheus_not_available",
        message="prometheus_client not installed, metrics endpoint disabled",
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        raise HTTPException(
            status_code=501, detail="Metrics not available. Install prometheus_client."
        )

    return Response(content=generate_latest(), media_type="text/plain")


# Metrics tracking middleware
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Track request metrics for Prometheus."""
    if PROMETHEUS_AVAILABLE:
        endpoint = request.url.path
        start = time.time()

        try:
            response = await call_next(request)
            telemetry_requests_total.labels(endpoint=endpoint).inc()
            telemetry_http_responses_total.labels(
                endpoint=endpoint, status_code=str(response.status_code)
            ).inc()
            if endpoint.startswith("/api/v1/admin/"):
                telemetry_admin_requests_total.inc()

            if response.status_code == 401:
                telemetry_security_events_total.labels(event_type="auth_401").inc()
            elif response.status_code == 403:
                telemetry_security_events_total.labels(event_type="auth_403").inc()
            elif response.status_code == 429:
                telemetry_security_events_total.labels(
                    event_type="rate_limit_429"
                ).inc()
            return response
        except Exception as e:
            telemetry_errors_total.labels(
                endpoint=endpoint, error_type=type(e).__name__
            ).inc()
            raise
        finally:
            request_duration_seconds.labels(endpoint=endpoint).observe(
                time.time() - start
            )
    else:
        return await call_next(request)
