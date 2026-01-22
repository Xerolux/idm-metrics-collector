## 2025-02-18 - Internal API Protection
**Vulnerability:** The `/api/internal/ml_alert` endpoint was exposed without authentication, relying on network isolation ("internal service communication") which is insufficient (Zero Trust violation).
**Learning:** "Internal" endpoints are often overlooked. Assuming Docker network isolation is sufficient is a common pitfall. If a container is compromised or a port is accidentally mapped, the endpoint is vulnerable.
**Prevention:** Implement Shared Secret (API Key) or mTLS for service-to-service communication. Even a simple environment-variable-based secret header adds significant defense-in-depth.

## 2025-02-21 - Fix Fail-Open in Internal API Auth
**Vulnerability:** The `ml_alert` endpoint authentication logic was "Fail Open" - if `INTERNAL_API_KEY` was not configured (None), the check was skipped entirely, allowing unauthorized access.
**Learning:** Security checks must always "Fail Closed". If a required secret or configuration is missing, the system should deny access rather than allowing it. Conditional security logic (`if key: check`) is prone to misconfiguration vulnerabilities.
**Prevention:** Always initialize security variables to safe defaults (deny/block) and assert their presence before allowing access. Use `if not key: raise/return error`.
