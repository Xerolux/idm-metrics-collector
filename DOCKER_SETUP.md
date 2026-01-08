# Docker Setup für IDM Metrics Collector

## Änderungen für pymodbus 3.x

Das Repository wurde für **pymodbus 3.x** aktualisiert, da die neueste Version (3.11.4) eine andere API verwendet.

### Wichtige Änderungen:

1. **requirements.txt**: `pymodbus>=3.0.0` (statt `<3.0.0`)
2. **modbus.py**: API-Calls angepasst:
   - `unit=1` → `device_id=1`
   - Import vereinfacht zu `from pymodbus.client import ModbusTcpClient`

## Docker Compose Konfiguration

### Umgebungsvariablen

Die IDM-Wärmepumpe wird über Umgebungsvariablen in `docker-compose.yml` konfiguriert:

```yaml
environment:
  # IDM Heat Pump connection
  - IDM_HOST=192.168.178.103    # ÄNDERN: Ihre IDM IP-Adresse
  - IDM_PORT=502                 # Standard Modbus TCP Port
  # InfluxDB connection
  - INFLUX_URL=http://idm-influxdb:8086
  - INFLUX_ORG=my-org
  - INFLUX_BUCKET=idm
  - INFLUX_TOKEN=my-super-secret-token-change-me
```

### Deployment-Optionen

#### Option 1: Vorkompiliertes Image (Produktion)

```bash
# Starten mit GitHub Container Registry Image
docker compose up -d
```

#### Option 2: Lokaler Build (Development)

```bash
# Starten mit lokalem Build
docker compose -f docker-compose.dev.yml up -d
```

## Quick Start

### 1. Docker Desktop starten

Stellen Sie sicher, dass Docker Desktop läuft.

### 2. Konfiguration anpassen

Bearbeiten Sie `docker-compose.yml` und ändern Sie die IDM_HOST:

```yaml
- IDM_HOST=192.168.178.103  # Ihre IDM Wärmepumpe IP
```

### 3. Services starten

```bash
# Mit vorkompiliertem Image
docker compose up -d

# ODER mit lokalem Build
docker compose -f docker-compose.dev.yml up -d
```

### 4. Zugriff auf die Services

- **Web Interface**: http://localhost:5008
- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB**: http://localhost:8086 (admin/adminpassword123)

### 5. Logs anzeigen

```bash
# Alle Services
docker compose logs -f

# Nur IDM Logger
docker compose logs -f idm-logger
```

## Test der Modbus-Verbindung

Vor dem Docker-Start können Sie die Verbindung testen:

```bash
# Python-Abhängigkeiten installieren
pip install pymodbus

# Test-Skript ausführen
python test_live.py
```

Das Skript liest wichtige Sensordaten von Ihrer IDM-Wärmepumpe aus.

## Troubleshooting

### Container startet nicht

```bash
# Status prüfen
docker compose ps

# Logs prüfen
docker compose logs idm-logger
```

### Modbus-Verbindung schlägt fehl

1. IP-Adresse in `docker-compose.yml` überprüfen
2. Wärmepumpe ist über Modbus TCP erreichbar (Port 502)
3. Firewall-Regeln prüfen
4. Container neustarten: `docker compose restart idm-logger`

### InfluxDB nicht erreichbar

```bash
# InfluxDB Health Check
docker compose exec influxdb curl http://localhost:8086/health

# Warten bis InfluxDB bereit ist
docker compose logs influxdb
```

## Netzwerk-Modus

Der Container läuft im Bridge-Netzwerk-Modus. Wenn Ihre IDM-Wärmepumpe im gleichen Netzwerk ist, sollte die Verbindung funktionieren.

Falls nicht, können Sie den Host-Netzwerk-Modus verwenden (nur Linux):

```yaml
network_mode: "host"
```

## Volumes und Persistenz

Daten werden in benannten Volumes gespeichert:

- `idm-logger-data`: SQLite-Datenbank und Konfiguration
- `idm-influxdb-data`: InfluxDB Zeitreihendaten
- `idm-grafana-data`: Grafana Dashboards und Einstellungen

### Backup erstellen

```bash
# Volumes sichern
docker run --rm -v idm-logger-data:/data -v $(pwd):/backup alpine tar czf /backup/idm-logger-backup.tar.gz /data
```

## Build und Publish

### Lokaler Build

```bash
docker build -t idm-logger:latest .
```

### Multi-Platform Build (für GitHub Actions)

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/xerolux/idm-metrics-collector:latest .
```

## Weitere Informationen

- [README.md](README.md): Hauptdokumentation
- [INSTALL.md](INSTALL.md): Detaillierte Installationsanleitung
- [WEB_FEATURES.md](WEB_FEATURES.md): Web-Interface Features
