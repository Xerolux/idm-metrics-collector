# Xerolux 2026
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
from datetime import timedelta
import hashlib
import re
import uuid
import json
import base64
import hmac
import tempfile
from cryptography.fernet import Fernet
from pathlib import Path
from collections import defaultdict
from analysis import get_community_averages
import structlog
from audit_log import (
    audit_logger,
    log_model_delete,
    log_model_download,
    log_training_trigger,
    log_failed_auth,
    log_admin_access,
)
from token_manager import (
    token_manager,
    generate_token,
    validate_token as validate_installation_token,
    revoke_token,
    token_exists,
    get_encryption_key,
    has_encryption_key,
)

# Redis (optional, for persistent rate limiting)
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# Configuration
# VictoriaMetrics Import Endpoint (Influx Line Protocol)
VM_WRITE_URL = os.environ.get("VM_WRITE_URL", "http://victoriametrics:8428/write")
VM_QUERY_URL = os.environ.get(
    "VM_QUERY_URL", "http://victoriametrics:8428/api/v1/query"
)
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "change-me-to-something-secure")

# Shared encryption key for backward compatibility
# Per-installation keys are preferred (see token_manager.py)
_encryption_key_str = os.environ.get(
    "TELEMETRY_ENCRYPTION_KEY",
    "gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="
)
DEFAULT_ENCRYPTION_KEY = _encryption_key_str.encode() if isinstance(_encryption_key_str, str) else _encryption_key_str

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

# Admin IDs (comma separated UUIDs)
raw_admin_ids = os.environ.get("ADMIN_INSTALLATION_IDS", "")
ADMIN_IDS = {x.strip().lower() for x in raw_admin_ids.split(",") if x.strip()}

logger.info("loaded_admin_ids", count=len(ADMIN_IDS))
if not ADMIN_IDS and raw_admin_ids:
    logger.warning(
        "admin_ids_empty_but_set",
        message="ADMIN_INSTALLATION_IDS was present but parsed to empty list. Check delimiters.",
    )

# Model storage directory
MODEL_DIR = os.environ.get("MODEL_DIR", "/app/models")

# Cold start configuration
MIN_INSTALLATIONS_FOR_MODEL = int(os.environ.get("MIN_INSTALLATIONS", "5"))
MIN_DATA_POINTS_FOR_MODEL = int(os.environ.get("MIN_DATA_POINTS", "10000"))

# Request size limit
MAX_PAYLOAD_SIZE = int(
    os.environ.get("MAX_PAYLOAD_SIZE", str(10 * 1024 * 1024))
)  # 10 MB default

# Simple in-memory rate limiting with endpoint-specific limits
_rate_limit_store: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))  # seconds
MAX_RATE_LIMIT_ENTRIES = int(
    os.environ.get("MAX_RATE_LIMIT_ENTRIES", "10000")
)  # Max IPs to track

# Endpoint-specific rate limits (requests per window)
RATE_LIMITS = {
    "default": int(os.environ.get("RATE_LIMIT_DEFAULT", "100")),
    "submit": int(os.environ.get("RATE_LIMIT_SUBMIT", "60")),  # Telemetry submission
    "status": int(os.environ.get("RATE_LIMIT_STATUS", "30")),  # Status checks
    "model": int(os.environ.get("RATE_LIMIT_MODEL", "10")),  # Model downloads
    "admin": int(os.environ.get("RATE_LIMIT_ADMIN", "20")),  # Admin operations
}

# IP Ban store
_banned_ips: Dict[str, Tuple[float, int]] = {}  # {ip: (ban_time, duration)}
DEFAULT_BAN_DURATION = int(
    os.environ.get("DEFAULT_BAN_DURATION", "3600")
)  # 1 hour default

# Cache configurations
HASH_CACHE_TTL = int(os.environ.get("HASH_CACHE_TTL", "3600"))  # 1 hour
POOL_STATS_CACHE_TTL = int(os.environ.get("POOL_STATS_CACHE_TTL", "60"))  # 1 minute
COMMUNITY_AVG_CACHE_TTL = int(os.environ.get("COMMUNITY_AVG_CACHE_TTL", "300"))  # 5 minutes

# Redis configuration (optional, for persistent rate limiting)
REDIS_URL = os.environ.get(
    "REDIS_URL", ""
)  # e.g., "redis://localhost:6379/0" or "redis://:password@localhost:6379/0"
USE_REDIS = REDIS_AVAILABLE and bool(REDIS_URL)
_redis_client = None  # Will be initialized on startup if USE_REDIS is True

# Cache stores
_file_hash_cache: Dict[
    str, Tuple[Optional[str], float]
] = {}  # {path: (hash, timestamp)}
_pool_stats_cache: Tuple[Optional[Dict[str, Any]], float] = (
    None,
    0,
)  # (stats, timestamp)
_community_avg_cache: Dict[
    str, Tuple[Dict[str, Any], float]
] = {}  # {cache_key: (result, timestamp)} - cache_key = f"{model}:{metrics}"


async def run_sync(func, *args):
    """Run a synchronous function in the default executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


# Security: Disable Docs, ReDoc, and OpenAPI to prevent scanning
app = FastAPI(
    title="IDM Telemetry Server",
    version="1.0.5",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    default_response_class=ORJSONResponse,
)


async def cleanup_rate_limits_and_bans():
    """Background task to clean up stale rate limit entries and expired bans."""
    while True:
        await asyncio.sleep(300)  # Clean every 5 minutes
        try:
            now = time.time()
            keys_to_remove = []

            # Clean rate limit entries
            for ip, timestamps in list(_rate_limit_store.items()):
                # Filter out old timestamps first
                valid_timestamps = [
                    t for t in timestamps if now - t < RATE_LIMIT_WINDOW
                ]
                if not valid_timestamps:
                    keys_to_remove.append(ip)
                else:
                    _rate_limit_store[ip] = valid_timestamps

            for k in keys_to_remove:
                if k in _rate_limit_store:
                    del _rate_limit_store[k]

            if keys_to_remove:
                logger.info("rate_limit_cleanup", removed=len(keys_to_remove))

            # Clean expired IP bans
            expired_bans = []
            for ip, (ban_time, duration) in list(_banned_ips.items()):
                if now - ban_time >= duration:
                    expired_bans.append(ip)

            for ip in expired_bans:
                del _banned_ips[ip]

            if expired_bans:
                logger.info("ip_ban_cleanup", expired=len(expired_bans))

            # Clean file hash cache
            expired_hashes = []
            for path, (_, timestamp) in list(_file_hash_cache.items()):
                if now - timestamp >= HASH_CACHE_TTL:
                    expired_hashes.append(path)

            for path in expired_hashes:
                del _file_hash_cache[path]

            # Clean community averages cache
            expired_avg_cache = []
            for cache_key, (_, timestamp) in list(_community_avg_cache.items()):
                if now - timestamp >= COMMUNITY_AVG_CACHE_TTL:
                    expired_avg_cache.append(cache_key)

            for cache_key in expired_avg_cache:
                del _community_avg_cache[cache_key]

            if expired_avg_cache:
                logger.info("community_avg_cache_cleanup", expired=len(expired_avg_cache))

            # Clean old audit logs (run once per day)
            # Check if we should run daily cleanup (every ~288 iterations of 5min = 24h)
            if not hasattr(cleanup_rate_limits_and_bans, '_cleanup_counter'):
                cleanup_rate_limits_and_bans._cleanup_counter = 0

            cleanup_rate_limits_and_bans._cleanup_counter += 1

            # Run audit log cleanup once per day (every 288 iterations)
            if cleanup_rate_limits_and_bans._cleanup_counter >= 288:
                audit_logger.cleanup_old_logs()
                cleanup_rate_limits_and_bans._cleanup_counter = 0

        except Exception as e:
            logger.error("cleanup_error", error=str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize HTTP client, Redis, and start background tasks."""
    global _redis_client

    # Create HTTPX client with connection pooling
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    logger.info("http_client_initialized")

    # Initialize Redis if configured
    if USE_REDIS:
        try:
            _redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            _redis_client.ping()

            # Mask Redis Password
            safe_url = REDIS_URL
            try:
                parsed = urlparse(REDIS_URL)
                if parsed.password:
                    # Construct masked URL safely
                    user_part = parsed.username if parsed.username is not None else ""
                    host_part = parsed.hostname if parsed.hostname else ""
                    port_part = f":{parsed.port}" if parsed.port else ""
                    safe_netloc = f"{user_part}:***@{host_part}{port_part}"
                    safe_url = parsed._replace(netloc=safe_netloc).geturl()
            except Exception:
                safe_url = "redis://***"

            logger.info(
                "redis_connected",
                url=safe_url,
            )
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

    # Start cleanup task
    asyncio.create_task(cleanup_rate_limits_and_bans())
    logger.info("background_tasks_started")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources."""
    if hasattr(app.state, "http_client"):
        await app.state.http_client.aclose()
        logger.info("http_client_closed")

    # Close Redis connection
    if _redis_client:
        try:
            _redis_client.close()
            logger.info("redis_closed")
        except Exception as e:
            logger.warning("redis_close_error", error=str(e))


# Middleware for HTTPS enforcement and Security Headers
@app.middleware("http")
async def enforce_https(request: Request, call_next):
    # Trust X-Forwarded-Proto from reverse proxy
    proto = request.headers.get("X-Forwarded-Proto", "https")
    if proto == "http":
        return PlainTextResponse(
            "Service Unavailable", status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    # HSTS (only if already HTTPS)
    if proto == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    # Content Security Policy (restrictive for API)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';"
    )

    return response


# Obfuscate 404 errors (Scanning attempts)
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


def check_rate_limit(
    client_ip: str, endpoint_type: str = "default"
) -> Tuple[bool, Dict[str, str]]:
    """
    Rate limiting check with headers and endpoint-specific limits.
    Supports Redis for persistence (falls back to in-memory).

    Returns (allowed, headers_dict).

    Args:
        client_ip: The client IP address
        endpoint_type: Type of endpoint (default, submit, status, model, admin)
    """
    now = time.time()

    # Get rate limit for this endpoint type
    rate_limit = RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])

    # Use compound key for IP + endpoint type
    compound_key = f"ratelimit:{client_ip}:{endpoint_type}"

    # Use Redis if available, otherwise fall back to in-memory
    if _redis_client:
        try:
            # Redis-based rate limiting using Sorted Sets
            # Use timestamp as score for automatic expiration
            pipe = _redis_client.pipeline()

            # Remove entries outside the time window
            min_score = now - RATE_LIMIT_WINDOW
            pipe.zremrangebyscore(compound_key, 0, min_score)

            # Count current requests in window
            pipe.zcard(compound_key)
            pipe.zadd(compound_key, {str(now): now})
            pipe.expire(compound_key, RATE_LIMIT_WINDOW)

            results = pipe.execute()
            current_count = results[1]  # zcard result

            remaining = max(0, rate_limit - current_count)
            # Get oldest timestamp for reset time calculation
            oldest = _redis_client.zrange(compound_key, 0, 0, withscores=True)
            reset_time = (
                int(oldest[0][1] + RATE_LIMIT_WINDOW)
                if oldest
                else int(now + RATE_LIMIT_WINDOW)
            )

            # Check limit
            if current_count >= rate_limit:
                logger.warning(
                    "rate_limit_exceeded_redis",
                    ip=mask_ip(client_ip),
                    endpoint=endpoint_type,
                )
                return False, {
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(RATE_LIMIT_WINDOW),
                }

            return True, {
                "X-RateLimit-Limit": str(rate_limit),
                "X-RateLimit-Remaining": str(remaining - 1),
                "X-RateLimit-Reset": str(reset_time),
            }

        except Exception as e:
            logger.warning(
                "redis_rate_limit_failed", error=str(e), fallback="in_memory"
            )
            # Fall through to in-memory implementation

    # In-memory rate limiting (fallback)
    # Check if too many IPs stored
    if len(_rate_limit_store) >= MAX_RATE_LIMIT_ENTRIES:
        # Remove oldest entries
        oldest_keys = sorted(
            _rate_limit_store.keys(),
            key=lambda k: min(_rate_limit_store[k]) if _rate_limit_store[k] else 0,
        )[:100]
        for k in oldest_keys:
            del _rate_limit_store[k]
        logger.warning("rate_limit_eviction", evicted=len(oldest_keys))

    # Clean old entries
    _rate_limit_store[compound_key] = [
        t for t in _rate_limit_store[compound_key] if now - t < RATE_LIMIT_WINDOW
    ]

    remaining = max(0, rate_limit - len(_rate_limit_store[compound_key]))
    reset_time = int(
        max(_rate_limit_store[compound_key]) + RATE_LIMIT_WINDOW
        if _rate_limit_store[compound_key]
        else now + RATE_LIMIT_WINDOW
    )

    # Check limit
    if len(_rate_limit_store[compound_key]) >= rate_limit:
        logger.warning(
            "rate_limit_exceeded_memory", ip=mask_ip(client_ip), endpoint=endpoint_type
        )
        return False, {
            "X-RateLimit-Limit": str(rate_limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_time),
            "Retry-After": str(RATE_LIMIT_WINDOW),
        }

    _rate_limit_store[compound_key].append(now)
    return True, {
        "X-RateLimit-Limit": str(rate_limit),
        "X-RateLimit-Remaining": str(remaining - 1),
        "X-RateLimit-Reset": str(reset_time),
    }


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


def _get_file_hash_sync(filepath: str) -> Optional[str]:
    """Synchronous internal function for hash calculation."""
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None


async def get_file_hash(filepath: str) -> Optional[str]:
    """Calculate SHA256 hash of a file with caching."""
    now = time.time()

    # Check cache
    if filepath in _file_hash_cache:
        cached_hash, timestamp = _file_hash_cache[filepath]
        if now - timestamp < HASH_CACHE_TTL:
            return cached_hash

    # Calculate new hash
    loop = asyncio.get_event_loop()
    hash_val = await loop.run_in_executor(None, _get_file_hash_sync, filepath)

    # Cache it
    if hash_val:
        _file_hash_cache[filepath] = (hash_val, now)

    return hash_val


def validate_installation_id(installation_id: str) -> str:
    """Validate installation ID is a UUID."""
    try:
        uuid.UUID(installation_id)
        return installation_id
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid installation_id format (must be UUID)"
        )


def validate_model_name(model_name: Optional[str]) -> Optional[str]:
    """Validate model name contains only safe characters."""
    if not model_name:
        return None

    # Check for null bytes
    if "\x00" in model_name:
        raise HTTPException(status_code=400, detail="Invalid model name format")

    # Check length
    if len(model_name) > 100:
        raise HTTPException(status_code=400, detail="Model name too long")

    # Allow alphanumeric, underscore, hyphen, dot, space, parentheses
    if not re.match(r"^[a-zA-Z0-9_\-\. \(\)]+$", model_name):
        raise HTTPException(status_code=400, detail="Invalid model name format")

    # Prevent path traversal
    if ".." in model_name or "/" in model_name or "\\" in model_name:
        raise HTTPException(status_code=400, detail="Invalid model name format")

    # Normalize spaces to underscores
    return model_name.replace(" ", "_")


async def get_data_pool_stats(request: Request) -> Dict[str, Any]:
    """
    Get current data pool statistics from VictoriaMetrics with caching.
    Used for cold start feedback.
    """
    global _pool_stats_cache
    now = time.time()

    # Check cache
    cached_stats, timestamp = _pool_stats_cache
    if cached_stats and now - timestamp < POOL_STATS_CACHE_TTL:
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
        response = await client.get(VM_QUERY_URL, params={"query": query_installations})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["total_installations"] = int(
                    data["data"]["result"][0]["value"][1]
                )

        # Count total data points (last 30 days)
        query_points = 'sum(count_over_time({__name__=~"heatpump_metrics_.*"}[30d]))'
        response = await client.get(VM_QUERY_URL, params={"query": query_points})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["total_data_points"] = int(
                    float(data["data"]["result"][0]["value"][1])
                )

        # Check which models are available
        model_dir = Path(MODEL_DIR)

        def _list_models():
            if model_dir.exists():
                return [f.stem.replace("_", " ") for f in model_dir.glob("*.enc")]
            return []

        stats["models_available"] = await run_sync(_list_models)

        # Determine if data is sufficient
        stats["data_sufficient"] = (
            stats["total_installations"] >= MIN_INSTALLATIONS_FOR_MODEL
            and stats["total_data_points"] >= MIN_DATA_POINTS_FOR_MODEL
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

    # Update cache
    _pool_stats_cache = (stats, now)

    return stats


def mask_ip(ip: str) -> str:
    """Mask IP address for GDPR compliance logging."""
    if not ip:
        return "0.0.0.0"
    if ":" in ip:  # IPv6
        return "xxxx:xxxx"
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.xxx.xxx"
    return "xxx.xxx.xxx.xxx"


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


async def verify_token(authorization: Optional[str] = Header(None)):
    """Verify global AUTH_TOKEN (for admin endpoints)."""
    if not AUTH_TOKEN:
        return  # Open access if no token configured (not recommended)

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Token")


async def verify_token_with_fallback(
    installation_id: str,
    authorization: Optional[str] = Header(None)
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
            logger.debug("token_validated", installation_id=installation_id, type="per_installation")
            return
        else:
            # Token exists but doesn't match - fail immediately
            logger.warning("token_mismatch", installation_id=installation_id)
            raise HTTPException(status_code=403, detail="Invalid Token for this installation")

    # Fallback to global token (for backward compatibility / migration)
    if AUTH_TOKEN and token == AUTH_TOKEN:
        logger.info("global_token_used", installation_id=installation_id, migrating=True)
        # Auto-register this installation with unique token AND encryption key
        try:
            result = generate_token(
                installation_id,
                metadata={"migrated_from_global": True},
                with_encryption_key=True
            )
            # Result is tuple of (token, encryption_key)
            logger.info("installation_auto_registered", installation_id=installation_id, has_encryption_key=True)
            # Note: Client doesn't know about the new credentials yet, but on next model check it will be notified
        except Exception as e:
            logger.error("auto_registration_failed", installation_id=installation_id, error=str(e))
        return

    # Neither per-installation nor global token worked
    raise HTTPException(status_code=403, detail="Invalid Token")


@app.post("/api/v1/register")
async def register_installation(
    installation_id: str,
    heatpump_model: Optional[str] = None,
    authorization: Optional[str] = Header(None)
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
        raise HTTPException(status_code=403, detail="Invalid global token for registration")

    # Check if already registered
    if token_exists(installation_id):
        logger.warning("registration_duplicate", installation_id=installation_id)
        raise HTTPException(
            status_code=409,
            detail="Installation already registered. Use /api/v1/token/refresh to get a new token."
        )

    # Generate new token AND encryption key
    try:
        result = generate_token(
            installation_id,
            metadata={"heatpump_model": heatpump_model} if heatpump_model else {},
            with_encryption_key=True  # Generate encryption key alongside token
        )

        # Unpack result (tuple of token, encryption_key)
        new_token, encryption_key = result

        logger.info("installation_registered", installation_id=installation_id, has_encryption_key=True)

        return {
            "installation_id": installation_id,
            "auth_token": new_token,
            "encryption_key": encryption_key,  # NEW: Per-installation encryption key
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "message": "Credentials generated successfully. Store these securely - they won't be shown again!",
            "security_note": "Your personal encryption key provides additional security. Future model downloads will use per-installation encryption."
        }
    except Exception as e:
        logger.error("registration_failed", installation_id=installation_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/api/v1/submit")
async def submit_telemetry(
    payload: TelemetryPayload,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Ingest telemetry data and forward to VictoriaMetrics.

    Uses per-installation tokens with fallback to global token for migration.
    """
    # Verify token (per-installation with fallback)
    await verify_token_with_fallback(payload.installation_id, authorization)

    # Prefer X-Forwarded-For if behind proxy, else fallback to direct connection
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        raw_ip = forwarded.split(",")[0].strip()
    else:
        raw_ip = request.client.host if request.client else "unknown"

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
        lines = []

        # Tags common to all points in this batch
        tags = f"installation_id={payload.installation_id},model={payload.heatpump_model.replace(' ', '_')},version={payload.version}"

        for record in payload.data:
            timestamp = record.get("timestamp")
            if not timestamp:
                continue

            # Timestamp in nanoseconds for Influx/VM Line Protocol
            ts_ns = int(timestamp * 1e9)

            # Fields
            fields = []
            for key, value in record.items():
                if key == "timestamp":
                    continue
                if isinstance(value, (int, float)):
                    fields.append(f"{key}={value}")
                elif isinstance(value, bool):
                    fields.append(f"{key}={str(value).lower()}")  # bool as boolean

            if fields:
                # Line Protocol: measurement,tags fields timestamp
                line = f"heatpump_metrics,{tags} {','.join(fields)} {ts_ns}"
                lines.append(line)

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
                data_submissions_total.labels(heatpump_model=payload.heatpump_model).inc()
                data_points_submitted_total.inc(len(lines))

        return JSONResponse(
            {"status": "success", "processed": len(lines)}, headers=rate_limit_headers
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("telemetry_processing_error", ip=client_ip, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


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
            if data.get("status") == "success" and data["data"]["result"]:
                installations = int(data["data"]["result"][0]["value"][1])

        return {
            "status": "online",
            "active_installations_30d": installations,
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error("status_check_failed", error=str(e))
        return {"status": "error", "message": str(e)}


@app.get("/api/v1/model/check")
async def check_eligibility(
    request: Request,
    installation_id: str,
    model: Optional[str] = None,
    current_hash: Optional[str] = None,
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

        # Check if Admin
        is_admin_check = installation_id.lower() in ADMIN_IDS
        logger.info(
            "eligibility_check",
            installation_id=installation_id,
            is_admin=is_admin_check,
        )

        if is_admin_check:
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
            model_file = model_dir / f"{model}.enc"
            metadata_file = model_dir / f"{model}_metadata.json"
            if not model_file.exists():
                # Fall back to generic model
                model_file = model_dir / "community_model.enc"
                metadata_file = model_dir / "community_model_metadata.json"
        else:
            model_file = model_dir / "community_model.enc"
            metadata_file = model_dir / "community_model_metadata.json"

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
                "message": "You have a personal authentication token. Make sure to use it instead of the shared token."
            }

        # Add encryption key information (for per-installation encryption)
        result["has_personal_encryption_key"] = has_encryption_key(installation_id)
        if result["has_personal_encryption_key"]:
            result["encryption_key_info"] = {
                "message": "You have a personal encryption key for enhanced security. This will be used for future model encryption.",
                "note": "Currently using shared encryption for backward compatibility. Migration to per-installation encryption is planned."
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
    auth: None = Depends(verify_token),
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
    model = validate_model_name(model)  # Returns normalized/validated name or None

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
            model_file = model_dir / f"{model}.enc"
            if not model_file.exists():
                model_file = model_dir / "community_model.enc"
        else:
            model_file = model_dir / "community_model.enc"

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
            success=True
        )

        # Check if installation has personal encryption key
        personal_key = get_encryption_key(installation_id)

        if personal_key:
            # Re-encrypt model with personal key for enhanced security
            logger.info(
                "model_reencrypt_personal",
                installation_id=installation_id,
                model=model_file.stem
            )

            try:
                # Read encrypted model file (JSON envelope)
                def _read_and_reencrypt():
                    with open(model_file, 'r', encoding='utf-8') as f:
                        envelope = json.load(f)

                    # Decrypt with shared key
                    shared_fernet = Fernet(DEFAULT_ENCRYPTION_KEY)
                    encrypted_data = base64.b64decode(envelope['payload'])
                    model_data = shared_fernet.decrypt(encrypted_data)

                    # Encrypt with personal key
                    personal_fernet = Fernet(personal_key)
                    personal_encrypted = personal_fernet.encrypt(model_data)

                    # Create new envelope with personal encryption
                    new_envelope = {
                        "version": envelope.get("version", "2.0"),
                        "metadata": envelope["metadata"].copy(),
                        "payload": base64.b64encode(personal_encrypted).decode('utf-8'),
                        "encryption": "per-installation"  # Mark as personally encrypted
                    }

                    # Add installation info to metadata
                    new_envelope["metadata"]["encrypted_for"] = installation_id
                    new_envelope["metadata"]["encryption_type"] = "per-installation"

                    # Create signature with personal key
                    metadata_json = json.dumps(new_envelope["metadata"], sort_keys=True)
                    msg = f"{new_envelope['payload']}.{metadata_json}".encode('utf-8')
                    signature = hmac.new(personal_key, msg, hashlib.sha256).hexdigest()
                    new_envelope["signature"] = signature

                    return new_envelope

                # Execute re-encryption in thread pool (I/O intensive)
                new_envelope = await asyncio.get_event_loop().run_in_executor(
                    None, _read_and_reencrypt
                )

                # Write to temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.enc',
                    delete=False,
                    encoding='utf-8'
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
                        model=model_file.stem
                    )

                    return response

                except Exception as e:
                    # Clean up temp file on error
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                    raise e

            except Exception as e:
                logger.error(
                    "personal_encryption_failed",
                    installation_id=installation_id,
                    error=str(e),
                    fallback_to_shared=True
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
        for model_file in model_dir.glob("*.enc"):
            models.append(
                {
                    "name": model_file.stem.replace("_", " "),
                    "filename": model_file.name,
                    "size_bytes": model_file.stat().st_size,
                    "hash": await get_file_hash(str(model_file)),
                    "modified": model_file.stat().st_mtime,
                }
            )

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

    # Check cache
    global _community_avg_cache
    if cache_key in _community_avg_cache:
        cached_result, cached_time = _community_avg_cache[cache_key]
        if time.time() - cached_time < COMMUNITY_AVG_CACHE_TTL:
            logger.info("community_averages_cache_hit", model=model, metrics=len(metric_list))

            # Track cache hit metric
            if PROMETHEUS_AVAILABLE:
                cache_hits_total.labels(cache_type="community_averages").inc()

            return cached_result

    # Cache miss - fetch from VictoriaMetrics
    logger.info("community_averages_cache_miss", model=model, metrics=len(metric_list))

    # Track cache miss metric
    if PROMETHEUS_AVAILABLE:
        cache_misses_total.labels(cache_type="community_averages").inc()
    result = await get_community_averages(
        model, metric_list, client=request.app.state.http_client
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Store in cache
    _community_avg_cache[cache_key] = (result, time.time())

    return result


# ==================== ADMIN ENDPOINTS ====================


async def verify_admin(
    authorization: Optional[str] = Header(None), installation_id: Optional[str] = None
):
    """Verify admin access (token + admin ID)."""
    # Verify token if configured
    if AUTH_TOKEN:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization Header")

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or token != AUTH_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid Token")

    # Verify admin ID
    if not installation_id:
        raise HTTPException(
            status_code=401, detail="Missing installation_id for admin check"
        )

    if installation_id.lower() not in ADMIN_IDS:
        logger.warning("unauthorized_admin_access", installation_id=installation_id)
        raise HTTPException(status_code=403, detail="Not authorized as admin")


async def check_admin_rate_limit(request: Request) -> None:
    """Check rate limit for admin endpoints."""
    forwarded = request.headers.get("X-Forwarded-For")
    raw_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else "unknown")
    )

    allowed, rate_limit_headers = check_rate_limit(raw_ip, "admin")
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
    """Admin: List all models with details."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    model_dir = Path(MODEL_DIR)

    async def _get_model_details(model_file):
        stat = await run_sync(model_file.stat)

        # Get download count from Prometheus counter
        download_count = 0
        if PROMETHEUS_AVAILABLE:
            try:
                # Get the counter value for this specific model
                metric_value = model_downloads_total.labels(model=model_file.stem)._value.get()
                download_count = int(metric_value) if metric_value else 0
            except:
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
        for mf in model_files:
            models.append(await _get_model_details(mf))

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
    """Admin: Delete a model file."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    # Sanitize model name
    safe_name = os.path.basename(model_name).replace(" ", "_")
    if not safe_name.endswith(".enc"):
        safe_name += ".enc"

    model_file = Path(MODEL_DIR) / safe_name

    exists = await run_sync(model_file.exists)
    if not exists:
        raise HTTPException(status_code=404, detail="Model not found")

    # Get client IP for audit log
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else "unknown")
    )

    try:
        await run_sync(model_file.unlink)
        logger.info(
            "admin_model_deleted",
            model=safe_name,
            admin_id=installation_id,
        )

        # Audit log
        log_model_delete(
            admin_id=installation_id,
            ip_address=client_ip,
            model_name=safe_name,
            success=True
        )

        return {"success": True, "message": f"Model {safe_name} deleted"}
    except Exception as e:
        logger.error("admin_model_delete_failed", model=safe_name, error=str(e))

        # Audit log failure
        log_model_delete(
            admin_id=installation_id,
            ip_address=client_ip,
            model_name=safe_name,
            success=False
        )

        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.post("/api/v1/admin/models/trigger-training")
async def admin_trigger_training(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """Admin: Trigger manual model training."""
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    # Get client IP for audit log
    forwarded = request.headers.get("X-Forwarded-For")
    client_ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else "unknown")
    )

    # Import training scheduler
    try:
        import subprocess

        result = subprocess.run(
            ["python3", "/app/scripts/train_models.py"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd="/app",
        )

        logger.info(
            "admin_training_triggered",
            admin_id=installation_id,
            returncode=result.returncode,
        )

        # Audit log
        log_training_trigger(
            admin_id=installation_id,
            ip_address=client_ip,
            success=(result.returncode == 0),
            metadata={
                "returncode": result.returncode,
                "has_stderr": bool(result.stderr),
            }
        )

        return {
            "success": result.returncode == 0,
            "message": "Training triggered"
            if result.returncode == 0
            else f"Training failed: {result.stderr}",
            "stdout": result.stdout if result.returncode != 0 else None,
            "stderr": result.stderr if result.returncode != 0 else None,
        }
    except Exception as e:
        logger.error("admin_training_trigger_failed", error=str(e))

        # Audit log failure
        log_training_trigger(
            admin_id=installation_id,
            ip_address=client_ip,
            success=False,
            metadata={"error": str(e)}
        )

        raise HTTPException(
            status_code=500, detail=f"Failed to trigger training: {str(e)}"
        )


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

        # Get all unique installation IDs from metrics
        query = "group by(installation_id) (count by (installation_id))"
        response = await client.get(VM_QUERY_URL, params={"query": query})

        installations = []
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                for result in data["data"]["result"]:
                    inst_id = result["metric"].get("installation_id", "unknown")
                    count = int(result["value"][1]) if result.get("value") else 0

                    # Get last activity timestamp
                    time_query = f'last_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{inst_id}"}}[30d])'
                    time_resp = await client.get(
                        VM_QUERY_URL, params={"query": time_query}
                    )

                    last_seen = None
                    if time_resp.status_code == 200:
                        time_data = time_resp.json()
                        if time_data.get("data") and time_data["data"].get("result"):
                            last_seen = float(
                                time_data["data"]["result"][0]["value"][0]
                            )

                    installations.append(
                        {
                            "installation_id": inst_id,
                            "data_points": count,
                            "last_seen": last_seen,
                            "last_seen_formatted": time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime(last_seen)
                            )
                            if last_seen
                            else "Unknown",
                            "is_admin": inst_id.lower() in ADMIN_IDS,
                        }
                    )

        # Sort by last seen
        installations.sort(key=lambda x: x.get("last_seen") or 0, reverse=True)

        return {
            "installations": installations[:limit],
            "total": len(installations),
            "showing": min(len(installations), limit),
        }
    except Exception as e:
        logger.error("admin_installations_list_failed", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to list installations: {str(e)}"
        )


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

        # Get all metrics for this installation (30d window)
        metrics_query = f'{{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}'
        response = await client.get(VM_QUERY_URL, params={"query": metrics_query})

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Installation not found")

        data = response.json()
        if not data.get("data") or not data["data"].get("result"):
            raise HTTPException(status_code=404, detail="No data found for this installation")

        results = data["data"]["result"]

        # Extract model from first metric (assuming all metrics have same model)
        heatpump_model = "Unknown"
        for result in results:
            if "heatpump_model" in result.get("metric", {}):
                heatpump_model = result["metric"]["heatpump_model"]
                break

        # Calculate total submissions (count of unique timestamps)
        timestamps_query = f'count_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[30d])'
        count_resp = await client.get(VM_QUERY_URL, params={"query": timestamps_query})

        total_submissions = 0
        if count_resp.status_code == 200:
            count_data = count_resp.json()
            if count_data.get("data") and count_data["data"].get("result"):
                total_submissions = sum(
                    int(float(r["value"][1])) for r in count_data["data"]["result"] if r.get("value")
                )

        # Get first seen (earliest timestamp)
        first_seen_query = f'min_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[30d])'
        first_resp = await client.get(VM_QUERY_URL, params={"query": first_seen_query})

        first_seen = None
        if first_resp.status_code == 200:
            first_data = first_resp.json()
            if first_data.get("data") and first_data["data"].get("result"):
                # Get the timestamp of the earliest metric
                timestamps = [float(r["value"][0]) for r in first_data["data"]["result"] if r.get("value")]
                if timestamps:
                    first_seen = min(timestamps)

        # Get last seen (latest timestamp)
        last_seen_query = f'last_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[30d])'
        last_resp = await client.get(VM_QUERY_URL, params={"query": last_seen_query})

        last_seen = None
        if last_resp.status_code == 200:
            last_data = last_resp.json()
            if last_data.get("data") and last_data["data"]["result"):
                last_seen = float(last_data["data"]["result"][0]["value"][0])

        # Calculate data quality score (based on completeness and consistency)
        # Simple heuristic: more metrics = better quality
        unique_metrics = len(set(r["metric"]["__name__"] for r in results))
        data_quality_score = min(1.0, unique_metrics / 20.0)  # Assuming 20+ metrics = good quality

        # Get model download history (from audit log if available)
        model_downloads = []
        try:
            from audit_log import get_audit_logs
            logs = get_audit_logs(
                action="model_download",
                installation_id=target_id,
                limit=50
            )
            model_downloads = [
                {
                    "model": log.get("metadata", {}).get("model", "Unknown"),
                    "downloaded_at": log.get("timestamp"),
                }
                for log in logs
            ]
        except Exception:
            # Audit log not available or error occurred
            pass

        # Calculate contribution rank
        # Get all installations and rank by submission count
        all_installations_query = 'group by(installation_id) (count by (installation_id))'
        rank_resp = await client.get(VM_QUERY_URL, params={"query": all_installations_query})

        contribution_rank = "Unknown"
        if rank_resp.status_code == 200:
            rank_data = rank_resp.json()
            if rank_data.get("data") and rank_data["data"].get("result"):
                counts = [(r["metric"].get("installation_id"), int(r["value"][1]))
                          for r in rank_data["data"]["result"] if r.get("value")]
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
            "first_seen": datetime.fromtimestamp(first_seen, timezone.utc).isoformat() if first_seen else None,
            "last_seen": datetime.fromtimestamp(last_seen, timezone.utc).isoformat() if last_seen else None,
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
        logger.error("admin_installation_details_failed", error=str(e), installation_id=target_id)
        raise HTTPException(
            status_code=500, detail=f"Failed to get installation details: {str(e)}"
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

        # Get time series data for this installation
        # Query last 30 days of data with 1-hour resolution
        query = f'count_over_time({{__name__=~"heatpump_metrics_.*", installation_id="{target_id}"}}[1h])'
        response = await client.get(
            VM_QUERY_URL.replace("/query", "/query_range"),
            params={
                "query": query,
                "start": int(time.time()) - 30*24*3600,  # 30 days ago
                "end": int(time.time()),
                "step": "3600",  # 1 hour resolution
            }
        )

        history = []
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("result"):
                # Aggregate all metrics into timeline
                for result in data["data"]["result"]:
                    metric_name = result["metric"].get("__name__", "unknown")
                    for timestamp, value in result.get("values", []):
                        history.append({
                            "timestamp": datetime.fromtimestamp(float(timestamp), timezone.utc).isoformat(),
                            "metric": metric_name,
                            "count": int(float(value)),
                        })

        # Sort by timestamp descending
        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "installation_id": target_id,
            "history": history[:limit],
            "total": len(history),
        }

    except Exception as e:
        logger.error("admin_installation_history_failed", error=str(e), installation_id=target_id)
        raise HTTPException(
            status_code=500, detail=f"Failed to get installation history: {str(e)}"
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
                "cpu_percent": psutil.cpu_percent(interval=None),  # Non-blocking
                "memory": psutil.virtual_memory(),
                "disk": psutil.disk_usage("/"),
            }

        sys_stats = await run_sync(_get_system_stats)

        # Check VictoriaMetrics
        vm_response = await request.app.state.http_client.get(f"{VM_QUERY_URL}/health")
        vm_healthy = vm_response.status_code == 200

        # Get model stats
        def _get_model_stats():
            model_dir = Path(MODEL_DIR)
            if not model_dir.exists():
                return 0, 0
            files = list(model_dir.glob("*.enc"))
            count = len(files)
            size = sum(f.stat().st_size for f in files)
            return count, size

        model_count, total_size = await run_sync(_get_model_stats)

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
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/api/v1/admin/metrics")
async def admin_get_metrics(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
):
    """
    Admin: Get metrics for monitoring dashboard.

    Returns metrics in a frontend-friendly format.
    """
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    if not PROMETHEUS_AVAILABLE:
        raise HTTPException(
            status_code=501, detail="Metrics not available. Install prometheus_client."
        )

    try:
        from prometheus_client import REGISTRY

        # Collect all metrics
        metrics_data = {}

        # Helper to get metric value
        def get_metric_value(metric_name, labels=None):
            try:
                for collector in REGISTRY._collector_to_names.keys():
                    for metric in collector.collect():
                        if metric.name == metric_name:
                            for sample in metric.samples:
                                if labels:
                                    # Match specific labels
                                    if all(sample.labels.get(k) == v for k, v in labels.items()):
                                        return sample.value
                                else:
                                    # Return first sample if no labels specified
                                    return sample.value
                return 0
            except Exception:
                return 0

        # Request metrics
        metrics_data["requests"] = {
            "total": get_metric_value("telemetry_requests_total"),
            "errors": get_metric_value("telemetry_errors_total"),
            "rate_limit_hits": get_metric_value("rate_limit_hits_total"),
        }

        # Business metrics
        metrics_data["business"] = {
            "submissions": get_metric_value("telemetry_data_submissions_total"),
            "data_points": get_metric_value("telemetry_data_points_submitted_total"),
            "model_downloads": get_metric_value("model_downloads_total"),
            "training_runs": get_metric_value("telemetry_training_runs_total"),
            "active_installations": get_metric_value("telemetry_active_installations"),
        }

        # Cache metrics
        metrics_data["cache"] = {
            "hits": get_metric_value("telemetry_cache_hits_total"),
            "misses": get_metric_value("telemetry_cache_misses_total"),
            "hit_rate": 0.0,
        }

        # Calculate cache hit rate
        total_cache_requests = metrics_data["cache"]["hits"] + metrics_data["cache"]["misses"]
        if total_cache_requests > 0:
            metrics_data["cache"]["hit_rate"] = (
                metrics_data["cache"]["hits"] / total_cache_requests
            ) * 100

        # Performance metrics (percentiles from histogram)
        metrics_data["performance"] = {
            "avg_request_duration_ms": 0.0,  # Would need histogram buckets
            "p95_request_duration_ms": 0.0,
            "p99_request_duration_ms": 0.0,
        }

        return metrics_data

    except Exception as e:
        logger.error("admin_metrics_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@app.get("/api/v1/admin/audit-log")
async def admin_get_audit_log(
    request: Request,
    authorization: Optional[str] = Header(None),
    installation_id: Optional[str] = None,
    limit: int = 100,
    action: Optional[str] = None,
    admin_filter: Optional[str] = None,
):
    """
    Admin: Get audit log events.

    Query parameters:
    - limit: Maximum number of events to return (default 100, max 500)
    - action: Filter by action type (e.g., "model_delete", "training_trigger")
    - admin_filter: Filter by specific admin installation ID
    """
    await check_admin_rate_limit(request)
    await verify_admin(authorization, installation_id)

    try:
        # Limit cap
        limit = min(limit, 500)

        # Get events based on filters
        if action:
            events = audit_logger.get_events_by_action(action, limit=limit)
        elif admin_filter:
            events = audit_logger.get_events_by_admin(admin_filter, limit=limit)
        else:
            events = audit_logger.get_recent_events(limit=limit)

        return {
            "events": events,
            "count": len(events),
            "limit": limit,
            "filters": {
                "action": action,
                "admin_filter": admin_filter,
            }
        }
    except Exception as e:
        logger.error("admin_audit_log_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get audit log: {str(e)}")


# Prometheus Metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY

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

    # Business Metrics
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
