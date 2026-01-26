## 2025-02-18 - Internal API Protection
**Vulnerability:** The `/api/internal/ml_alert` endpoint was exposed without authentication, relying on network isolation ("internal service communication") which is insufficient (Zero Trust violation).
**Learning:** "Internal" endpoints are often overlooked. Assuming Docker network isolation is sufficient is a common pitfall. If a container is compromised or a port is accidentally mapped, the endpoint is vulnerable.
**Prevention:** Implement Shared Secret (API Key) or mTLS for service-to-service communication. Even a simple environment-variable-based secret header adds significant defense-in-depth.

## 2025-02-21 - Fix Fail-Open in Internal API Auth
**Vulnerability:** The `ml_alert` endpoint authentication logic was "Fail Open" - if `INTERNAL_API_KEY` was not configured (None), the check was skipped entirely, allowing unauthorized access.
**Learning:** Security checks must always "Fail Closed". If a required secret or configuration is missing, the system should deny access rather than allowing it. Conditional security logic (`if key: check`) is prone to misconfiguration vulnerabilities.
**Prevention:** Always initialize security variables to safe defaults (deny/block) and assert their presence before allowing access. Use `if not key: raise/return error`.

## 2026-01-25 - Remove Hardcoded Admin Fallback
**Vulnerability:** `Config.check_admin_password` allowed a hardcoded fallback to `admin` password if no hash was set.
**Learning:** Default credentials in "fallback" logic are dangerous because they are often forgotten or triggered unexpectedly (e.g., config load failure). This violates "Fail Closed".
**Prevention:** Remove all default password fallbacks. Use environment variables (e.g., `ADMIN_PASSWORD`) to allow secure initialization of credentials in automated environments.

## 2026-02-28 - Fix Auth Lockout Configuration Trap
**Vulnerability:** The configuration logic assumed that if `METRICS_URL` was present, the system was "Setup Complete", even if no `ADMIN_PASSWORD` was provided. This led to a "Fail Locked" state where users were locked out by default in some deployments, potentially encouraging insecure workarounds.
**Learning:** "Setup Complete" status should only be inferred if *all* required security parameters (like admin password) are present. Partial configuration should logically result in an "Incomplete" state (TOFU), guiding the user to the secure setup flow.
**Prevention:** In configuration initialization, conditionally set "setup completed" flags only when verifying that critical authentication credentials are valid/present.
