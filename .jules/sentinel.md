## 2026-01-18 - Exposed Secrets in Config API
**Vulnerability:** The `/api/config` endpoint returned the full configuration object including decrypted passwords (MQTT, Email, WebDAV) in plaintext to authenticated users.
**Learning:** Returning internal configuration objects directly to the frontend often leaks sensitive data that the frontend doesn't need or shouldn't see. Shallow copies are insufficient when modifying nested dictionaries for redaction.
**Prevention:** Always deep-copy and redact configuration objects before sending them to the client. Use dedicated DTOs (Data Transfer Objects) for API responses instead of raw internal state.
