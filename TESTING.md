# Docker Compose Testing Guide

Dieses Dokument beschreibt, wie das Docker Compose Setup und die GHCR Images getestet werden können.

## Voraussetzungen

- Docker und Docker Compose installiert
- Zugriff auf GitHub Container Registry (ghcr.io)
- Port 5008 (Webseite), 8086 (InfluxDB) und 3000 (Grafana) müssen verfügbar sein

## Schnellstart

### 1. Services starten

```bash
docker compose down  # Alte Container stoppen
docker compose pull  # Neuestes Image von GHCR ziehen
docker compose up -d # Services im Hintergrund starten
```

### 2. Status prüfen

```bash
docker compose ps    # Container Status
docker compose logs -f idm-logger  # Logs verfolgen
```

## Detaillierte Tests

### Test 1: GHCR Image wird korrekt heruntergeladen

```bash
# Image manuell ziehen
docker pull ghcr.io/xerolux/idm-metrics-collector:latest

# Image Info anzeigen
docker images | grep idm-metrics-collector
```

**Erwartetes Ergebnis:**
- Image wird erfolgreich heruntergeladen
- Image-Tag ist "latest"
- Image-Größe sollte ca. 150-300 MB sein

### Test 2: Container Health Checks

```bash
# Alle Container prüfen
docker compose ps

# Health Check Status einzeln prüfen
docker inspect idm-logger --format='{{.State.Health.Status}}'
docker inspect idm-influxdb --format='{{.State.Health.Status}}'
docker inspect idm-grafana --format='{{.State.Health.Status}}'
```

**Erwartetes Ergebnis:**
- Alle Container zeigen Status "healthy" nach ca. 30-60 Sekunden
- idm-logger: healthy
- idm-influxdb: healthy
- idm-grafana: healthy

### Test 3: Webseite auf Port 5008

```bash
# Health Endpoint testen
curl http://localhost:5008/api/health

# Status Endpoint testen
curl http://localhost:5008/api/status

# Webseite im Browser öffnen
# Linux:
xdg-open http://localhost:5008

# macOS:
open http://localhost:5008

# Windows:
start http://localhost:5008
```

**Erwartetes Ergebnis:**
```json
{
  "status": "healthy",
  "setup_completed": false
}
```

### Test 4: InfluxDB Verbindung

```bash
# InfluxDB Health prüfen
curl http://localhost:8086/health

# InfluxDB API testen
curl http://localhost:8086/api/v2/ping
```

**Erwartetes Ergebnis:**
- HTTP 200 OK
- InfluxDB ist erreichbar

### Test 5: Grafana Dashboard

```bash
# Grafana Health prüfen
curl http://localhost:3000/api/health

# Grafana im Browser öffnen
# Linux:
xdg-open http://localhost:3000

# macOS:
open http://localhost:3000

# Windows:
start http://localhost:3000
```

**Login Credentials:**
- Username: `admin`
- Password: `admin`

**Erwartetes Ergebnis:**
- Grafana Login-Seite wird angezeigt
- Nach Login: Dashboard ist verfügbar
- InfluxDB Datasource ist vorkonfiguriert

### Test 6: Setup-Prozess durchlaufen

1. Öffne http://localhost:5008
2. Du solltest automatisch zum Setup weitergeleitet werden
3. Fülle das Setup-Formular aus:
   - **IDM Host:** IP-Adresse deiner IDM Wärmepumpe
   - **IDM Port:** 502 (Standard Modbus Port)
   - **InfluxDB URL:** http://idm-influxdb:8086 (bereits vorkonfiguriert)
   - **InfluxDB Org:** my-org (bereits vorkonfiguriert)
   - **InfluxDB Bucket:** idm (bereits vorkonfiguriert)
   - **InfluxDB Token:** my-super-secret-token-change-me (bereits vorkonfiguriert)
   - **Admin Password:** Wähle ein sicheres Passwort (mind. 6 Zeichen)
4. Klicke auf "Complete Setup"

**Erwartetes Ergebnis:**
- Setup wird erfolgreich abgeschlossen
- Weiterleitung zur Login-Seite
- Nach Login: Dashboard ist zugänglich

### Test 7: Container Logs prüfen

```bash
# Alle Logs anzeigen
docker compose logs

# Nur IDM Logger Logs
docker compose logs idm-logger

# Nur InfluxDB Logs
docker compose logs influxdb

# Nur Grafana Logs
docker compose logs grafana

# Logs live verfolgen
docker compose logs -f
```

**Erwartetes Ergebnis:**
- Keine ERROR Messages
- IDM Logger zeigt "Starting web server on 0.0.0.0:5000"
- InfluxDB zeigt erfolgreichen Start
- Grafana zeigt erfolgreichen Start

### Test 8: Volumes und Persistenz

```bash
# Volumes auflisten
docker volume ls | grep idm

# Volume Details
docker volume inspect idm-logger-data
docker volume inspect idm-influxdb-data
docker volume inspect idm-grafana-data
```

**Erwartetes Ergebnis:**
- 4 Volumes existieren:
  - idm-logger-data
  - idm-influxdb-data
  - idm-influxdb-config
  - idm-grafana-data

### Test 9: Neustart-Verhalten

```bash
# Container stoppen
docker compose down

# Container neu starten
docker compose up -d

# Status prüfen
docker compose ps

# Setup Status prüfen (sollte noch completed sein)
curl http://localhost:5008/api/health
```

**Erwartetes Ergebnis:**
- Container starten erfolgreich neu
- Setup-Daten bleiben erhalten (setup_completed: true)
- Konfiguration bleibt erhalten

### Test 10: Image Update testen

```bash
# Neuestes Image ziehen
docker compose pull

# Container mit neuem Image starten
docker compose up -d

# Logs prüfen
docker compose logs -f idm-logger
```

**Erwartetes Ergebnis:**
- Neues Image wird heruntergeladen (falls verfügbar)
- Container startet mit neuem Image
- Daten bleiben erhalten

## Häufige Probleme

### Problem: "docker: command not found"

**Lösung:** Docker ist nicht installiert. Installiere Docker:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose

# Oder Docker Desktop von https://www.docker.com/products/docker-desktop
```

### Problem: "permission denied"

**Lösung:** Dein Benutzer muss in der Docker-Gruppe sein:
```bash
sudo usermod -aG docker $USER
# Logout und Login erforderlich
```

### Problem: "port already in use"

**Lösung:** Ein anderer Service nutzt bereits Port 5008, 8086 oder 3000:
```bash
# Port-Nutzung prüfen
sudo netstat -tulpn | grep -E '5008|8086|3000'

# Ports in docker-compose.yml anpassen
# Beispiel: "5009:5000" statt "5008:5000"
```

### Problem: "failed to pull image"

**Lösung:**
1. Prüfe deine Internet-Verbindung
2. Prüfe ob das Image existiert:
   ```bash
   curl -H "Authorization: Bearer $(gh auth token)" \
     https://ghcr.io/v2/xerolux/idm-metrics-collector/manifests/latest
   ```
3. Falls das Image nicht existiert, muss es erst gebaut und gepusht werden (siehe unten)

### Problem: Container sind "unhealthy"

**Lösung:**
```bash
# Detaillierte Logs prüfen
docker compose logs idm-logger

# Health Check manuell ausführen
docker exec idm-logger python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)"
```

## GHCR Image Build und Push

Falls das Image noch nicht in GHCR existiert, muss es zuerst gebaut und gepusht werden:

### Option 1: Via GitHub Actions (empfohlen)

```bash
# Push zu main branch triggert automatisch den Build
git add .
git commit -m "Update Docker configuration"
git push origin main

# Workflow Status prüfen
gh workflow view "Build and publish IDM Metrics Collector Docker image"
gh run list --workflow="docker-image.yml"
```

### Option 2: Manuell lokal bauen und pushen

```bash
# Bei GHCR anmelden
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Image bauen
docker build -t ghcr.io/xerolux/idm-metrics-collector:latest .

# Image pushen
docker push ghcr.io/xerolux/idm-metrics-collector:latest
```

## Cleanup

```bash
# Alle Container stoppen und entfernen
docker compose down

# Container + Volumes entfernen (ACHTUNG: Löscht alle Daten!)
docker compose down -v

# Images entfernen
docker rmi ghcr.io/xerolux/idm-metrics-collector:latest
```

## Architektur Übersicht

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Host Machine                                   │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Port 5008 → idm-logger:5000            │  │
│  │  (Flask Web App + Modbus Client)         │  │
│  │  Image: ghcr.io/xerolux/idm-metrics...   │  │
│  └──────────────────────────────────────────┘  │
│               ↓                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Port 8086 → influxdb:8086              │  │
│  │  (Time Series Database)                  │  │
│  │  Image: influxdb:2                       │  │
│  └──────────────────────────────────────────┘  │
│               ↓                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Port 3000 → grafana:3000               │  │
│  │  (Dashboard & Visualization)             │  │
│  │  Image: grafana/grafana:latest           │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Nächste Schritte

Nach erfolgreichem Test:

1. ✅ Webseite ist erreichbar unter http://localhost:5008
2. ✅ Setup-Prozess durchlaufen
3. ✅ IDM Wärmepumpe konfigurieren
4. ✅ Modbus-Verbindung testen
5. ✅ Daten in InfluxDB prüfen
6. ✅ Grafana Dashboard anschauen
7. ✅ Metriken überwachen

## Support

Bei Problemen:
- Logs prüfen: `docker compose logs -f`
- GitHub Issues: https://github.com/Xerolux/idm-metrics-collector/issues
- README.md für weitere Dokumentation

---

**Stand:** 2026-01-08
**Version:** 1.0
