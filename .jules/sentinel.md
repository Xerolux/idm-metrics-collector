## 2025-02-18 - [Critical] Unauthenticated Internal Endpoint
**Vulnerability:** The `/api/internal/ml_alert` endpoint was accessible without any authentication, allowing anyone with network access to trigger anomaly alerts.
**Learning:** Internal endpoints are often overlooked in security reviews under the assumption of "perimeter security". Defense in depth requires every service boundary to be secured.
**Prevention:** Enforce shared secret authentication (e.g. `X-Internal-Secret`) for all service-to-service communication, even within the same docker network.
