## 2025-02-18 - Internal API Protection
**Vulnerability:** The `/api/internal/ml_alert` endpoint was exposed without authentication, relying on network isolation ("internal service communication") which is insufficient (Zero Trust violation).
**Learning:** "Internal" endpoints are often overlooked. Assuming Docker network isolation is sufficient is a common pitfall. If a container is compromised or a port is accidentally mapped, the endpoint is vulnerable.
**Prevention:** Implement Shared Secret (API Key) or mTLS for service-to-service communication. Even a simple environment-variable-based secret header adds significant defense-in-depth.

## 2025-02-21 - Fix Fail-Open in Internal API Auth
**Vulnerability:** The `ml_alert` endpoint authentication logic was "Fail Open" - if `INTERNAL_API_KEY` was not configured (None), the check was skipped entirely, allowing unauthorized access.
**Learning:** Security checks must always "Fail Closed". If a required secret or configuration is missing, the system should deny access rather than allowing it. Conditional security logic (`if key: check`) is prone to misconfiguration vulnerabilities.
**Prevention:** Always initialize security variables to safe defaults (deny/block) and assert their presence before allowing access. Use `if not key: raise/return error`.

## 2025-02-24 - Default Password Fallback vulnerability
**Vulnerability:** The authentication system fell back to a hardcoded default password ("admin") if the password hash was missing from the configuration.
**Learning:** Fallback logic intended for "legacy migration" or "easy setup" often becomes a persistent backdoor. Security checks should fail closed (deny access) when configuration is missing, rather than degrading to a weak default.
**Prevention:** Avoid hardcoded fallbacks for authentication. Ensure that missing security configuration results in a "secure failure" (e.g., login disabled) rather than "insecure success" (default password enabled).
