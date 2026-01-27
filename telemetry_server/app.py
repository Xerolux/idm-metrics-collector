from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import os
import logging
import requests
import time
import hashlib
import re
import uuid
from pathlib import Path
from collections import defaultdict
from analysis import get_community_averages

# Configuration
# VictoriaMetrics Import Endpoint (Influx Line Protocol)
VM_WRITE_URL = os.environ.get("VM_WRITE_URL", "http://victoriametrics:8428/write")
VM_QUERY_URL = os.environ.get(
    "VM_QUERY_URL", "http://victoriametrics:8428/api/v1/query"
)
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "change-me-to-something-secure")

# Model storage directory
MODEL_DIR = os.environ.get("MODEL_DIR", "/app/models")

# Cold start configuration
MIN_INSTALLATIONS_FOR_MODEL = int(os.environ.get("MIN_INSTALLATIONS", "5"))
MIN_DATA_POINTS_FOR_MODEL = int(os.environ.get("MIN_DATA_POINTS", "10000"))

# Simple in-memory rate limiting
_rate_limit_store: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("telemetry-server")

app = FastAPI(title="IDM Telemetry Server", version="1.1.0")


def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting check. Returns True if request is allowed."""
    now = time.time()
    # Clean old entries
    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip] if now - t < RATE_LIMIT_WINDOW
    ]
    # Check limit
    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    _rate_limit_store[client_ip].append(now)
    return True


def get_file_hash(filepath: str) -> Optional[str]:
    """Calculate SHA256 hash of a file."""
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
    # Allow alphanumeric, underscore, hyphen, dot, space, parentheses
    if not re.match(r"^[a-zA-Z0-9_\-\. \(\)]+$", model_name):
        raise HTTPException(status_code=400, detail="Invalid model name format")
    return model_name


def get_data_pool_stats() -> Dict[str, Any]:
    """
    Get current data pool statistics from VictoriaMetrics.
    Used for cold start feedback.
    """
    stats = {
        "total_installations": 0,
        "total_data_points": 0,
        "models_available": [],
        "data_sufficient": False,
        "message": "",
        "message_de": "",
    }

    try:
        # Count unique installations (last 30 days)
        query_installations = (
            'count(count_over_time(heatpump_metrics{installation_id!=""}[30d]))'
        )
        response = requests.get(
            VM_QUERY_URL, params={"query": query_installations}, timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["total_installations"] = int(
                    data["data"]["result"][0]["value"][1]
                )

        # Count total data points (last 30 days)
        query_points = "sum(count_over_time(heatpump_metrics{}[30d]))"
        response = requests.get(VM_QUERY_URL, params={"query": query_points}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                stats["total_data_points"] = int(
                    float(data["data"]["result"][0]["value"][1])
                )

        # Check which models are available
        model_dir = Path(MODEL_DIR)
        if model_dir.exists():
            for model_file in model_dir.glob("*.enc"):
                model_name = model_file.stem.replace("_", " ")
                stats["models_available"].append(model_name)

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
        logger.error(f"Error getting data pool stats: {e}")
        stats["message"] = "Data pool status temporarily unavailable."
        stats["message_de"] = "Datenpool-Status vorübergehend nicht verfügbar."

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


async def verify_token(authorization: Optional[str] = Header(None)):
    if not AUTH_TOKEN:
        return  # Open access if no token configured (not recommended)

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Token")


@app.post("/api/v1/submit")
async def submit_telemetry(
    payload: TelemetryPayload, request: Request, auth: None = Depends(verify_token)
):
    """
    Ingest telemetry data and forward to VictoriaMetrics.
    """
    raw_ip = request.client.host if request.client else "unknown"
    client_ip = mask_ip(raw_ip)

    # Rate limiting
    if not check_rate_limit(raw_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429, detail="Too many requests. Please try again later."
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
            # Batch write to VictoriaMetrics
            data = "\n".join(lines)
            response = requests.post(VM_WRITE_URL, data=data)

            if response.status_code != 204:  # VM returns 204 on success
                logger.error(
                    f"VictoriaMetrics write failed: {response.status_code} - {response.text}"
                )
                raise HTTPException(status_code=502, detail="Database Write Failed")

            logger.info(
                f"Ingested {len(lines)} points from {payload.installation_id} ({client_ip})"
            )

        return {"status": "success", "processed": len(lines)}

    except Exception as e:
        logger.error(f"Error processing telemetry from {client_ip}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/status")
async def server_status(auth: None = Depends(verify_token)):
    """
    Get server statistics (Internal/Admin only).
    """
    try:
        # Count unique installations (approximate)
        # Using a count query on installation_id tag
        query = 'count(count_over_time(heatpump_metrics{installation_id!=""}[30d]))'
        response = requests.get(VM_QUERY_URL, params={"query": query})
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
        logger.error(f"Status check failed: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/v1/model/check")
async def check_eligibility(
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
    validate_model_name(model)

    try:
        result = {
            "eligible": False,
            "reason": "",
            "reason_de": "",
            "model_hash": None,
            "model_available": False,
            "update_available": False,
            "data_pool": get_data_pool_stats(),
        }

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
        query = f'last_over_time(heatpump_metrics{{installation_id="{installation_id}"}}[30d])'
        response = requests.get(VM_QUERY_URL, params={"query": query}, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                result["eligible"] = True

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

        if model:
            # Look for model-specific file
            safe_model_name = model.replace(" ", "_").replace("/", "_")
            model_file = model_dir / f"{safe_model_name}.enc"
            if not model_file.exists():
                # Fall back to generic model
                model_file = model_dir / "community_model.enc"
        else:
            model_file = model_dir / "community_model.enc"

        if model_file and model_file.exists():
            result["model_available"] = True
            result["model_hash"] = get_file_hash(str(model_file))

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

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Eligibility check failed for {installation_id}: {e}")
        raise HTTPException(status_code=500, detail="Check failed")


@app.get("/api/v1/model/download")
async def download_model(
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
    validate_model_name(model)

    try:
        # Verify eligibility first
        query = f'last_over_time(heatpump_metrics{{installation_id="{installation_id}"}}[30d])'
        response = requests.get(VM_QUERY_URL, params={"query": query}, timeout=5)

        eligible = False
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                eligible = True

        if not eligible:
            raise HTTPException(
                status_code=403,
                detail="Not eligible. Contribute data for 30 days to access community models.",
            )

        # Find model file
        model_dir = Path(MODEL_DIR)
        model_file = None

        if model:
            safe_model_name = model.replace(" ", "_").replace("/", "_")
            model_file = model_dir / f"{safe_model_name}.enc"
            if not model_file.exists():
                model_file = model_dir / "community_model.enc"
        else:
            model_file = model_dir / "community_model.enc"

        if not model_file or not model_file.exists():
            raise HTTPException(
                status_code=404,
                detail="No model available yet. The community model is still being trained.",
            )

        logger.info(f"Model download by {installation_id}: {model_file.name}")

        return FileResponse(
            path=str(model_file),
            filename=model_file.name,
            media_type="application/octet-stream",
            headers={
                "X-Model-Hash": get_file_hash(str(model_file)) or "",
                "X-Model-Name": model_file.stem,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model download failed for {installation_id}: {e}")
        raise HTTPException(status_code=500, detail="Download failed")


@app.get("/api/v1/pool/status")
async def data_pool_status():
    """
    Get the current status of the data pool.
    Public endpoint - no authentication required.
    Useful for displaying cold start information to users.
    """
    stats = get_data_pool_stats()
    stats["timestamp"] = time.time()
    return stats


@app.get("/api/v1/models")
async def list_available_models(auth: None = Depends(verify_token)):
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
                    "hash": get_file_hash(str(model_file)),
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
    model: str, metrics: Optional[str] = None, auth: None = Depends(verify_token)
):
    """
    Get aggregated community statistics.
    Requires authentication (token).
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

    result = get_community_averages(model, metric_list)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
