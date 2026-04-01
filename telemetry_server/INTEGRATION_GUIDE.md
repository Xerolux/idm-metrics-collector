# IDM Telemetry Server Integration Guide

This document outlines the requirements and protocols for clients (data collectors) to integrate with the IDM Telemetry Server. The server collects heat pump telemetry data, aggregates community statistics, and distributes trained anomaly detection models.

**Target Audience:** Developers & AI Agents implementing a client.

## 1. Configuration Checklist

Before starting implementation, ensure you have:

*   [ ] **Server URL:** `https://collector.xerolux.de` (Production)
*   [ ] **Auth Token:** A valid Bearer Token (shared secret).
*   [ ] **Installation ID:** A generated UUID v4 (persistent across restarts).
*   [ ] **Heat Pump Model:** The specific model name (e.g., "AERO_SLM").

## 2. Authentication

*   **Protocol:** HTTPS (TLS 1.2+ required).
*   **Header:** `Authorization: Bearer <YOUR_AUTH_TOKEN>`
*   **Scope:** Required for all endpoints except `/health` and `/api/v1/pool/status`.

## 3. Client Logic Flow (Happy Path)

An AI agent or developer should implement the following state machine:

1.  **Startup:**
    *   Load configuration (Token, URL).
    *   Load or generate (and save) `installation_id` (UUID v4).
2.  **Maintenance (Daily):**
    *   Call `GET /api/v1/model/check` with `installation_id`.
    *   If `eligible` is `true` AND `update_available` is `true`:
        *   Call `GET /api/v1/model/download`.
        *   Save the downloaded `.enc` file locally.
3.  **Data Collection Loop:**
    *   Collect sensor data (every ~60s).
    *   Buffer data locally (RAM or disk).
4.  **Submission (Interval: 1h - 24h):**
    *   Format buffered data into the JSON payload.
    *   Call `POST /api/v1/submit`.
    *   If successful (HTTP 200/204): Clear buffer.
    *   If failed (HTTP 5xx): Keep buffer, retry later (exponential backoff).
    *   If failed (HTTP 4xx): Discard buffer (invalid data), log error.

## 4. Endpoints & Examples

### A. Check Eligibility & Model Status

Check if the client is allowed to download models and if a new model is available.

*   **Method:** `GET`
*   **URL:** `/api/v1/model/check`
*   **Params:** `installation_id` (UUID), `model` (String), `current_hash` (Optional String)

**Request (cURL):**
```bash
curl -X GET "https://collector.xerolux.de/api/v1/model/check?installation_id=550e8400-e29b-41d4-a716-446655440000&model=AERO_SLM" \
     -H "Authorization: Bearer my-secret-token"
```

Hinweis:
- Für normale Clients wird das reguläre Client-Token verwendet.
- Für Admin-Installationen sollte im produktiven Betrieb das dedizierte `ADMIN_AUTH_TOKEN` genutzt werden, damit Admin-Infos (`is_admin`, `server_stats`) ausgeliefert werden.

**Response (JSON):**
```json
{
  "eligible": true,
  "reason": "Eligible for community model.",
  "model_available": true,
  "model_hash": "a1b2c3d4...",
  "update_available": true,
  "model_metadata": {
    "model_name": "AERO_SLM",
    "trained_at": "2024-03-01T03:00:00.123456",
    "samples_processed": 150000,
    "data_points": 2500000,
    "installations": 42
  }
}
```

### B. Download Model

Download the encrypted model file.

*   **Method:** `GET`
*   **URL:** `/api/v1/model/download`
*   **Params:** `installation_id` (UUID), `model` (String)

**Request (cURL):**
```bash
curl -X GET "https://collector.xerolux.de/api/v1/model/download?installation_id=550e8400-e29b-41d4-a716-446655440000&model=AERO_SLM" \
     -H "Authorization: Bearer my-secret-token" \
     -o model.enc
```

**Response:** Binary stream (`application/octet-stream`).

### C. Submit Telemetry Data

Upload buffered data.

*   **Method:** `POST`
*   **URL:** `/api/v1/submit`
*   **Content-Type:** `application/json`

**Request (cURL):**
```bash
curl -X POST "https://collector.xerolux.de/api/v1/submit" \
     -H "Authorization: Bearer my-secret-token" \
     -H "Content-Type: application/json" \
     -d '{
           "installation_id": "550e8400-e29b-41d4-a716-446655440000",
           "heatpump_model": "AERO_SLM",
           "version": "1.2.0",
           "data": [
             {
               "timestamp": 1709286000.123,
               "temp_outdoor": 5.4,
               "temp_flow": 32.1,
               "power_compressor": 1200
             },
             {
               "timestamp": 1709286060.123,
               "temp_outdoor": 5.3,
               "temp_flow": 32.3,
               "power_compressor": 1210
             }
           ]
         }'
```

**Payload Schema:**

| Field | Type | Required | Notes |
| :--- | :--- | :--- | :--- |
| `installation_id` | UUID | Yes | Must be a valid UUID string. |
| `heatpump_model` | String | Yes | No special characters allowed except `_`, `-`, `.`, `()`. |
| `version` | String | Yes | Client version. |
| `data` | List[Object] | Yes | List of measurements. |

**Measurement Object:**

| Field | Type | Required | Notes |
| :--- | :--- | :--- | :--- |
| `timestamp` | Float | Yes | Unix timestamp (seconds). Critical for reconstruction. |
| `[metric]` | Number/Bool | No | e.g. `temp_outdoor`, `cop_current`. |

## 5. Security & Privacy

-   **Transport Security:** All traffic MUST use HTTPS.
-   **IP Masking:** The server automatically masks client IP addresses (e.g., `192.168.xxx.xxx`) in logs to comply with privacy standards (GDPR).
-   **Data Isolation:** Data is aggregated for community statistics. Individual installation data is used for training but never exposed raw to other users.

## 6. Administration

The Telemetry Server supports a special "Admin" mode for specific installations.

For production hardening and strict admin access setup, read:
- [`SECURITY_SETUP.md`](./SECURITY_SETUP.md)

### Server Configuration

To grant admin privileges to one or more clients, create a `.env` file in the same directory as your `docker-compose.yml` and add the `ADMIN_INSTALLATION_IDS` variable. This list should be comma-separated.

**.env** example (minimal):
```ini
ADMIN_INSTALLATION_IDS=550e8400-e29b-41d4-a716-446655440000,123e4567-e89b-12d3-a456-426614174000
ADMIN_AUTH_TOKEN=REPLACE_WITH_STRONG_ADMIN_TOKEN
STRICT_ADMIN_AUTH=true
```

The `docker-compose.yml` is already configured to read this variable:
```yaml
environment:
  - ADMIN_INSTALLATION_IDS=${ADMIN_INSTALLATION_IDS:-}
```

### Client Behavior

When a client with a matching `installation_id` calls the `/api/v1/model/check` endpoint, the response will include:

```json
{
  "is_admin": true,
  "server_stats": {
    "models": [ ... ],
    "active_installations": 150,
    "total_points": 5000000
  }
}
```

The standard client software detects this flag and enables the **"Admin Zone"** tab in the WebUI (`Config` -> `Admin Zone`). This allows authorized users to view server health, total data points, and model generation status directly from their local interface.
