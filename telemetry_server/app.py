from fastapi import FastAPI, HTTPException, Header, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
import requests
import time

# Configuration
# VictoriaMetrics Import Endpoint (Influx Line Protocol)
VM_WRITE_URL = os.environ.get("VM_WRITE_URL", "http://victoriametrics:8428/write")
VM_QUERY_URL = os.environ.get(
    "VM_QUERY_URL", "http://victoriametrics:8428/api/v1/query"
)
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "change-me-to-something-secure")

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("telemetry-server")

app = FastAPI(title="IDM Telemetry Server")


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
    client_ip = mask_ip(request.client.host)
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
async def check_eligibility(installation_id: str):
    """
    Check if an installation ID is eligible for community models.
    Concept: User must have submitted data in the last 30 days.
    """
    try:
        # Query: Check if this ID appears in the last 30 days
        query = f'last_over_time(heatpump_metrics{{installation_id="{installation_id}"}}[30d])'
        response = requests.get(VM_QUERY_URL, params={"query": query})

        eligible = False
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data["data"]["result"]:
                eligible = True

        return {"eligible": eligible}
    except Exception as e:
        logger.error(f"Eligibility check failed for {installation_id}: {e}")
        raise HTTPException(status_code=500, detail="Check failed")
