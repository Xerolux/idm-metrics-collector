# Telemetry Server Security Setup (Production)

Diese Anleitung stellt sicher, dass auf einem **öffentlichen Server** wirklich nur legitime Admins Zugriff auf den Admin-Bereich bekommen.

Für tägliche Betriebsbefehle siehe auch:
- [`OPS_README.md`](./OPS_README.md)

## 1. Sichere `.env` anlegen

1. Im Verzeichnis `telemetry_server`:
```bash
cp .env.production.example .env
```
2. Werte in `.env` setzen:
- `AUTH_TOKEN`: starkes Token für normale Client-Endpunkte
- `ADMIN_AUTH_TOKEN`: starkes, separates Token nur für Admin-Endpunkte
- `STRICT_ADMIN_AUTH=true`
- `ADMIN_INSTALLATION_IDS=<uuid1>,<uuid2>`
- `TELEMETRY_ENCRYPTION_KEY` setzen

Wichtig:
- `AUTH_TOKEN` und `ADMIN_AUTH_TOKEN` dürfen **nicht** gleich sein.
- Beide Tokens sollten mindestens 32 zufällige Zeichen haben.

## 2. Sichere Secrets erzeugen

Beispiele:
```bash
# Linux/macOS
openssl rand -base64 48

# Python
python3 - << 'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

Für den Encryption Key:
```bash
openssl rand -base64 32
```

## 3. Docker Compose mit `.env` starten

Im Verzeichnis `telemetry_server`:
```bash
docker compose --env-file .env up -d
```

Danach:
```bash
docker compose ps
docker compose logs telemetry-api --tail 100
```

## 4. Öffentlich absichern (Firewall + Netzwerk)

- Nur Port `8000/tcp` öffentlich freigeben, wenn nötig.
- VictoriaMetrics (`8428`) nur intern/localhost binden.
- Reverse Proxy (Nginx/Caddy) mit TLS und Request-Limits vor die API setzen.

### Nginx Beispiel (TLS + Limits)

```nginx
limit_req_zone $binary_remote_addr zone=telemetry_api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=telemetry_admin:10m rate=2r/s;

server {
    listen 443 ssl http2;
    server_name telemetry.example.com;

    # SSL config (certificates omitted here)

    location /api/v1/admin/ {
        limit_req zone=telemetry_admin burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 1m;
    }

    location /api/v1/submit {
        limit_req zone=telemetry_api burst=30 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 15m;
    }

    location / {
        limit_req zone=telemetry_api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy Beispiel (TLS + Basic Rate Limits)

```caddyfile
telemetry.example.com {
    encode zstd gzip

    @admin path /api/v1/admin/*
    handle @admin {
        rate_limit {
            zone admin
            key {remote_host}
            events 120
            window 1m
        }
        reverse_proxy 127.0.0.1:8000
    }

    handle {
        reverse_proxy 127.0.0.1:8000
    }
}
```

## 5. Verifikation (Pflichttests)

### A) Admin ohne Token
```bash
curl -i "https://<dein-server>/api/v1/admin/health?installation_id=<admin-uuid>"
```
Erwartung: `401` oder `403`.

### B) Admin mit falschem Token
```bash
curl -i "https://<dein-server>/api/v1/admin/health?installation_id=<admin-uuid>" \
  -H "Authorization: Bearer WRONG_TOKEN"
```
Erwartung: `403`.

### C) Admin mit richtigem Token, aber nicht-admin UUID
```bash
curl -i "https://<dein-server>/api/v1/admin/health?installation_id=<non-admin-uuid>" \
  -H "Authorization: Bearer <ADMIN_AUTH_TOKEN>"
```
Erwartung: `403`.

### D) Admin mit richtigem Token + admin UUID
```bash
curl -i "https://<dein-server>/api/v1/admin/health?installation_id=<admin-uuid>" \
  -H "Authorization: Bearer <ADMIN_AUTH_TOKEN>"
```
Erwartung: `200`.

## 6. Betriebsempfehlungen

- Tokens regelmäßig rotieren (z. B. monatlich/vierteljährlich).
- Audit-Log regelmäßig prüfen (`/api/v1/admin/audit-log`).
- Admin-Liste (`ADMIN_INSTALLATION_IDS`) minimal halten.
- Für produktive Public Deployments `STRICT_ADMIN_AUTH` niemals deaktivieren.
- Images auf Digest pinnen (keine mutable `:latest` Tags im Produktivbetrieb).

### A) Image Digest Pinning

```bash
cd telemetry_server
./scripts/pin_images.sh
docker compose --env-file .env up -d
```

Oder über den globalen Wrapper:
```bash
telemetry pin-images
```

### B) Secret Rotation Runbook

```bash
cd telemetry_server
./scripts/rotate_secrets.sh --all --restart
```

Oder über den Wrapper:
```bash
telemetry rotate-secrets --all --restart
```

Hinweise:
- `AUTH_TOKEN` Rotation betrifft Clients mit globalem Token.
- Bestehende `.env` wird als Backup `telemetry_server/.env.backup-<timestamp>` gesichert.
- Bei Zwischenfall mindestens `--admin --restart` sofort ausführen.

### C) Backup & Restore Verifikation

Empfohlene Backup-Dateien pro Snapshot:
- `.env`
- `vmdata.tar.gz`
- `model-data.tar.gz`

Verifikation:
```bash
cd telemetry_server
./scripts/verify_backup_restore.sh --backup-dir /path/to/backup
```

Oder über den Wrapper:
```bash
telemetry verify-backup --backup-dir /path/to/backup
```

### D) Monitoring / Alerts

- Neue Security- und Error-Metriken:
  - `telemetry_http_responses_total`
  - `telemetry_security_events_total`
  - `telemetry_admin_requests_total`
- Beispiel-Regeln: `telemetry_server/monitoring/alerts.example.yml`
- Schwellenwerte können über `.env` dokumentiert und in Prometheus-Regeln gespiegelt werden:
  - `ALERT_401_PER_5M`
  - `ALERT_403_PER_5M`
  - `ALERT_429_PER_5M`
  - `ALERT_ADMIN_REQUESTS_PER_5M`

Live-Setup:
```bash
cd telemetry_server
set -a; source .env; set +a
python3 monitoring/render_alert_rules.py
```

Danach:
- `monitoring/alerts.generated.yml` nach Prometheus mounten (`/etc/prometheus/alerts/telemetry-alerts.yml`)
- Beispiel-Config: `monitoring/prometheus.example.yml`

## 7. Notfallmaßnahmen bei Verdacht auf Missbrauch

1. `ADMIN_AUTH_TOKEN` sofort rotieren.
2. `AUTH_TOKEN` rotieren.
3. `ADMIN_INSTALLATION_IDS` prüfen/bereinigen.
4. Container neu starten:
```bash
docker compose --env-file .env up -d
```
5. Audit-Log exportieren und prüfen (CSV-Export in Admin Zone).
