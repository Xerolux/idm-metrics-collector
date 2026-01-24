## 2025-02-18 - Internal API Protection
**Vulnerability:** The `/api/internal/ml_alert` endpoint was exposed without authentication, relying on network isolation ("internal service communication") which is insufficient (Zero Trust violation).
**Learning:** "Internal" endpoints are often overlooked. Assuming Docker network isolation is sufficient is a common pitfall. If a container is compromised or a port is accidentally mapped, the endpoint is vulnerable.
**Prevention:** Implement Shared Secret (API Key) or mTLS for service-to-service communication. Even a simple environment-variable-based secret header adds significant defense-in-depth.

## 2025-02-21 - Fix Fail-Open in Internal API Auth
**Vulnerability:** The `ml_alert` endpoint authentication logic was "Fail Open" - if `INTERNAL_API_KEY` was not configured (None), the check was skipped entirely, allowing unauthorized access.
**Learning:** Security checks must always "Fail Closed". If a required secret or configuration is missing, the system should deny access rather than allowing it. Conditional security logic (`if key: check`) is prone to misconfiguration vulnerabilities.
**Prevention:** Always initialize security variables to safe defaults (deny/block) and assert their presence before allowing access. Use `if not key: raise/return error`.

## 2025-02-24 - Fix Default Admin Password Vulnerability
**Vulnerability:** The system allowed login with "admin" / "admin" by default if the `admin_password_hash` was missing from configuration. In Docker environments with `METRICS_URL` set, `setup_completed` was automatically set to `True`, bypassing the setup wizard and leaving the system exposed with the default insecure password.
**Learning:** "Zero Config" convenience features often undermine security by skipping essential setup steps like password creation. A system should never be considered "Setup Complete" if no authentication credential has been established.
**Prevention:** Remove insecure fallbacks for authentication. Ensure `setup_completed` status is strictly coupled to the existence of valid credentials. Use environment variables (like `ADMIN_PASSWORD`) to allow secure automated setup without resorting to hardcoded defaults.
