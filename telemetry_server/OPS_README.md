# Telemetry Ops Quick Guide

Diese Kurzanleitung ist für den Betrieb auf dem Server gedacht.

## 1) Wrapper aktualisieren

```bash
cd /home/idm-metrics-collector/telemetry_server
sudo bash telemetry_update.sh
```

Danach steht der Befehl `telemetry` global zur Verfügung.

## 2) Menü starten

```bash
telemetry menu
```

- Installiert bei Bedarf automatisch `whiptail` (Debian/Ubuntu).
- Fällt sonst auf Text-Menü zurück.

## 3) Wichtige Befehle

```bash
telemetry status
telemetry logs
telemetry update
telemetry update-force
telemetry harden
telemetry pin-images
telemetry rotate-secrets --all --restart
telemetry verify-backup --backup-dir /path/to/backup
```

## 4) Sicherheits-Hinweise

- `rotate-secrets` ist HIGH-RISK und fragt explizit nach Bestätigung.
- `update-force` ist HIGH-RISK (verwirft lokale Änderungen per reset/clean).
- Für Automationen ohne TTY: `telemetry rotate-secrets --yes --all --restart`
- `.env` niemals committen.
- Für Public Deployments immer `STRICT_ADMIN_AUTH=true` und getrennte Tokens nutzen.

## 6) Alert-Regeln aus `.env` erzeugen

```bash
cd /home/idm-metrics-collector/telemetry_server
set -a; source .env; set +a
python3 monitoring/render_alert_rules.py
```

## 5) Empfohlene Reihenfolge bei Neu-Setup

```bash
telemetry status
telemetry harden
telemetry rotate-secrets --all --restart
telemetry verify-backup --backup-dir /path/to/backup
```
