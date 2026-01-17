## 2025-02-18 - Internal API Protection
**Vulnerability:** The `/api/internal/ml_alert` endpoint was exposed without authentication, relying on network isolation ("internal service communication") which is insufficient (Zero Trust violation).
**Learning:** "Internal" endpoints are often overlooked. Assuming Docker network isolation is sufficient is a common pitfall. If a container is compromised or a port is accidentally mapped, the endpoint is vulnerable.
**Prevention:** Implement Shared Secret (API Key) or mTLS for service-to-service communication. Even a simple environment-variable-based secret header adds significant defense-in-depth.
