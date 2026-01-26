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
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "change-me-to-something-secure")

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telemetry-server")

app = FastAPI(title="IDM Telemetry Server")

class TelemetryPayload(BaseModel):
    installation_id: str
    heatpump_model: str
    version: str
    data: List[Dict[str, Any]]

async def verify_token(authorization: Optional[str] = Header(None)):
    if not AUTH_TOKEN:
        return # Open access if no token configured (not recommended)

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Token")

@app.post("/api/v1/submit")
async def submit_telemetry(payload: TelemetryPayload, request: Request, auth: None = Depends(verify_token)):
    """
    Ingest telemetry data and forward to VictoriaMetrics.
    """
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
                    fields.append(f"{key}={str(value).lower()}") # bool as boolean

            if fields:
                # Line Protocol: measurement,tags fields timestamp
                line = f"heatpump_metrics,{tags} {','.join(fields)} {ts_ns}"
                lines.append(line)

        if lines:
            # Batch write to VictoriaMetrics
            data = "\n".join(lines)
            response = requests.post(VM_WRITE_URL, data=data)

            if response.status_code != 204: # VM returns 204 on success
                logger.error(f"VictoriaMetrics write failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=502, detail="Database Write Failed")

            logger.info(f"Ingested {len(lines)} points from {payload.installation_id} ({payload.heatpump_model})")

        return {"status": "success", "processed": len(lines)}

    except Exception as e:
        logger.error(f"Error processing telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
