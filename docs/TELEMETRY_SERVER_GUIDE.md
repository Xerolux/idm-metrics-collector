# Telemetry Server Guide

## Überblick

Dieser Ordner enthält eine Referenzimplementierung für den Telemetry-Server, der Daten von den IDM-Loggern empfängt.

## Architektur

1.  **Ingest API (FastAPI)**: Empfängt POST-Requests, validiert den Token und konvertiert JSON in das Influx Line Protocol.
2.  **Datenbank (VictoriaMetrics)**: Speichert die Zeitreihendaten effizient.
3.  **Training Scripts**: Python-Skripte zum Extrahieren von Daten und Trainieren von KI-Modellen.

## Setup

### Voraussetzungen

*   Server mit Docker & Docker Compose
*   Domain (z.B. `collector.xerolux.de`)
*   SSL Zertifikat (Let's Encrypt)

### Installation

1.  Ordner auf den Server kopieren.
2.  `docker-compose.yml` anpassen (Passwörter ändern!).
3.  Starten: `docker compose up -d`

### Security Best Practices

1.  **Reverse Proxy**: Nutze Nginx oder Traefik als Reverse Proxy vor dem Container.
2.  **SSL/TLS**: Erzwinge HTTPS.
3.  **Firewall**: Erlaube nur Port 443 (HTTPS) und Port 22 (SSH) von außen. Der Port 8428 (VictoriaMetrics) ist standardmäßig an `127.0.0.1` gebunden und somit **nicht** öffentlich erreichbar.
4.  **Token**: Setze ein starkes `AUTH_TOKEN` in der `docker-compose.yml`.

### DSGVO / GDPR Hinweise

*   **Serverstandort**: Wähle einen Hoster mit Rechenzentrum in Deutschland.
*   **IP-Adressen**: Die Software maskiert IP-Adressen im Log (`1.2.xxx.xxx`), um Personenbezug zu minimieren.
*   **Zugriff**: Nur API-Zugriff erlauben. SSH nur per Key-Authentication.

## Verwaltung (CLI)

Wenn du per SSH auf dem Server bist, kannst du den Status abrufen:

```bash
docker compose exec telemetry-api python scripts/manage.py status
```

Dies zeigt:
*   Anzahl aktiver Installationen (letzte 30 Tage)
*   Server Status
*   Modell Status

## Workflow: Vom Datensatz zum KI-Modell

1.  **Daten sammeln**: Warte, bis genügend Clients Daten senden.
2.  **Training**:
    *   Führe `python scripts/train_model.py --model "AERO SLM"` aus.
    *   Dies erzeugt eine `model.pkl` Datei.
3.  **Verteilung**:
    *   Integriere die `model.pkl` in das nächste Docker-Image des `ml-service` im Hauptprojekt.
    *   Beim Update erhalten alle Nutzer das verbesserte Modell.

## API Format

**POST /api/v1/submit**

Header: `Authorization: Bearer <TOKEN>`

Payload:
```json
{
  "installation_id": "uuid...",
  "heatpump_model": "AERO SLM",
  "version": "1.0.0",
  "data": [
    { "timestamp": 1234567890.123, "temp_outdoor": 5.5, ... }
  ]
}
```
