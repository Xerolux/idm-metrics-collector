#!/usr/bin/env python3
"""Render Prometheus alert rules from .env threshold values."""

from pathlib import Path
import os


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError:
        return default


def main() -> int:
    threshold_401 = env_int("ALERT_401_PER_5M", 50)
    threshold_403 = env_int("ALERT_403_PER_5M", 30)
    threshold_429 = env_int("ALERT_429_PER_5M", 30)
    threshold_admin = env_int("ALERT_ADMIN_REQUESTS_PER_5M", 200)

    out = f"""groups:
  - name: telemetry-security
    interval: 30s
    rules:
      - alert: TelemetryHigh401Rate
        expr: sum(increase(telemetry_security_events_total{{event_type="auth_401"}}[5m])) > {threshold_401}
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High 401 rate on telemetry server"
          description: "More than {threshold_401} unauthorized requests in 5 minutes."

      - alert: TelemetryHigh403Rate
        expr: sum(increase(telemetry_security_events_total{{event_type="auth_403"}}[5m])) > {threshold_403}
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High 403 rate on telemetry server"
          description: "More than {threshold_403} forbidden requests in 5 minutes."

      - alert: TelemetryHigh429Rate
        expr: sum(increase(telemetry_security_events_total{{event_type="rate_limit_429"}}[5m])) > {threshold_429}
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High 429 rate on telemetry server"
          description: "More than {threshold_429} rate-limit responses in 5 minutes."

      - alert: TelemetryAdminTrafficSpike
        expr: sum(increase(telemetry_admin_requests_total[5m])) > {threshold_admin}
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Admin API traffic spike"
          description: "More than {threshold_admin} requests to /api/v1/admin/* in 5 minutes."
"""

    out_path = Path(__file__).resolve().parent / "alerts.generated.yml"
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
