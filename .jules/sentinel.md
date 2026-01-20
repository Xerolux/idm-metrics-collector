## 2024-05-22 - Unprotected Internal Endpoints
**Vulnerability:** The `/api/internal/ml_alert` endpoint was accessible without authentication, relying solely on network isolation.
**Learning:** Internal service-to-service endpoints in `idm_logger` were not implementing shared secret validation, assuming Docker network security was sufficient.
**Prevention:** Enforce `X-Internal-Secret` checks on all `/api/internal/*` endpoints using a shared `INTERNAL_API_KEY`.
