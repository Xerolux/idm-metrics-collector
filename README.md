# IDM Metrics Collector v0.5.0

[![GitHub Release][releases-shield]][releases]
[![Downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![Buy Me A Coffee][buymeacoffee-badge]][buymeacoffee]
[![Tesla](https://img.shields.io/badge/Tesla-Referral-red?style=for-the-badge&logo=tesla)](https://ts.la/sebastian564489)

Ein umfassendes Überwachungs- und Steuerungssystem für IDM Wärmepumpen (Navigator 2.0) mit InfluxDB v3 Metrik-Speicherung und Grafana-Visualisierung.

## Funktionen

*   **Docker-First**: Optimiert für Docker und Docker Compose Deployments
*   **Zero-Config Setup**: Vollständiger Stack mit InfluxDB v3 und Grafana vorkonfiguriert
*   **Automatischer Installer**: Ein-Befehl-Installation erledigt alles
*   **Datenquelle**: Liest von der IDM Wärmepumpe via Modbus TCP
*   **Datensenke**: InfluxDB v3 Core mit SQL-Abfrage-Unterstützung
*   **Weboberfläche**: Modernes Dashboard für Live-Daten, Konfiguration, manuelle Steuerung und Zeitplanung
*   **Automatisierung**: Eingebauter Zeitplaner, um Werte (z.B. Temperaturen) zu bestimmten Zeiten zu schreiben
*   **Produktionsbereit**: Health Checks, automatische Neustarts, persistente Daten

## Schnellstart

### Ein-Befehl-Installation

```bash
curl -fsSL https://raw.githubusercontent.com/Xerolux/idm-metrics-collector/main/install.sh | sudo bash
```

Oder klonen und ausführen:

```bash
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
sudo chmod +x install.sh
sudo ./install.sh
```

Der Installer wird:
1. Dein Betriebssystem erkennen und Docker/Docker Compose installieren
2. Erforderliche Abhängigkeiten installieren (git, curl, usw.)
3. Dich bitten, die Installationsmethode zu wählen:
   - **Docker**: Einzelner Container (nur die App)
   - **Docker Compose**: Kompletter Stack (App + InfluxDB + Grafana) **[EMPFOHLEN]**
4. Repository klonen, Images bauen und alle Dienste starten

### Installationsmethoden

#### Option 1: Docker (Einzelner Container)

Am besten für: Verbindung zu einer bestehenden InfluxDB-Instanz

```bash
sudo ./install.sh
# Wähle Option 1: Docker
```

Nach der Installation:
```bash
# Konfiguration bearbeiten
sudo nano /opt/idm-metrics-collector/config.yaml

# Container neustarten
docker restart idm-metrics-collector

# Logs anzeigen
docker logs -f idm-metrics-collector
```

#### Option 2: Docker Compose (Full Stack) **[EMPFOHLEN]**

Am besten für: Komplette schlüsselfertige Lösung mit Monitoring

```bash
sudo ./install.sh
# Wähle Option 2: Docker Compose
```

Dies installiert:
- **IDM Metrics Collector** (Web UI + API)
- **InfluxDB v3 Core** (Zeitreihendatenbank mit SQL-Support)
- **Grafana** (Visualisierungsplattform mit InfluxDB v3 Integration)

Alle Dienste sind vorkonfiguriert und einsatzbereit!

Nach der Installation:
```bash
# Konfiguration bearbeiten (setze deine Wärmepumpen-IP)
sudo nano /opt/idm-metrics-collector/config.yaml

# Stack neustarten
cd /opt/idm-metrics-collector && docker compose restart
```

## Zugriff auf die Dienste

### Nach der Installation

**Web UI** (IDM Metrics Collector)
- URL (Docker Compose Standard): `http://dein-server-ip:5008`
- URL (Einzelner Container Standard): `http://dein-server-ip:5000`
- Standard-Login: `admin` / `admin` (bitte nach dem ersten Login ändern)
- Funktionen: Live-Dashboard, Bedienfeld, Zeitplaner, Konfiguration

**Grafana** (nur Docker Compose)
- URL: `http://dein-server-ip:3001`
- Standard-Login: `admin` / `admin`
- Vorkonfiguriert mit InfluxDB Datenquelle und IDM Dashboard

**InfluxDB v3** (nur Docker Compose)
- URL: `http://dein-server-ip:8181`
- Standard-Konfiguration:
  - Datenbank: `idm`
  - Token: `my-super-secret-token-change-me`
  - Abfragesprache: SQL (ersetzt Flux aus v2)
  - Hinweis: Datenbank wird beim ersten Schreibvorgang automatisch erstellt

### Docker Image (GHCR)

Vorgebaute Images sind über die GitHub Container Registry verfügbar:

```bash
docker pull ghcr.io/xerolux/idm-metrics-collector:latest
docker run --rm -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  ghcr.io/xerolux/idm-metrics-collector:latest
```

Images werden automatisch gebaut bei:
- Pushes auf den `main` Branch (getaggt als `latest`)
- Git Tags, die mit `v` beginnen (z.B. `v1.0.0`)

## Konfiguration

Pfad zur Konfigurationsdatei: `/opt/idm-metrics-collector/config.yaml`

Beispiel:

```yaml
idm:
  host: "192.168.1.100"  # IP deiner IDM Wärmepumpe
  port: 502              # Modbus Port
  circuits: ["A"]        # Aktivierte Heizkreise

influx:
  url: "http://localhost:8181"
  database: "idm"
  token: "my-token"

web:
  enabled: true
  port: 5000
  admin_password: "admin" # Passwort für Login
  write_enabled: false    # Schreiben auf die Wärmepumpe erlauben (Steuerung/Zeitplan)

logging:
  interval: 60           # Sekunden zwischen den Lesezyklen
  level: "INFO"
```

## Weboberfläche

Zugriff auf die Weboberfläche unter `http://<deine-server-ip>:5008` bei Verwendung von Docker Compose, oder `http://<deine-server-ip>:5000` für das Einzel-Container-Setup.

*   **Login**: Die Oberfläche ist durch ein Passwort geschützt (Standard: `admin`).
    ![Login](docs/images/login.png)

*   **Live Dashboard**: Zeigt kategorisierte Sensorwerte mit automatischer Aktualisierung und anpassbaren Widgets.
    ![Dashboard](docs/images/dashboard.png)

*   **Steuerung**: (Wenn aktiviert) Schreibe Werte auf beschreibbare Sensoren.
    ![Control](docs/images/control.png)

*   **Zeitplan**: (Wenn aktiviert) Automatisiere das Setzen von Werten basierend auf Zeit und Tag.
    ![Schedule](docs/images/schedule.png)

*   **Konfiguration**:
    *   **Allgemein**: Konfiguriere IDM Verbindung, InfluxDB und Logging.
        ![Config General](docs/images/config_general.png)
    *   **MQTT**: Richte MQTT Publishing und Home Assistant Discovery ein.
        ![Config MQTT](docs/images/config_mqtt.png)
    *   **Tools**: Generiere Technikercodes und verwalte die Datenbank.
        ![Config Tools](docs/images/config_tools.png)

*   **Protokolle**: Siehe Live-Systemprotokolle ein.
    ![Logs](docs/images/logs.png)

*   **Solar-Integration**: Schreibe PV-Überschuss via MQTT auf die Wärmepumpe. Siehe [SOLAR_INTEGRATION.md](docs/SOLAR_INTEGRATION.md).

## Nutzung & Haftungsausschluss

Verwende dieses Projekt so wie es ist und auf eigenes Risiko. Stelle sicher, dass du die Auswirkungen des Lesens von oder Schreibens auf deine Wärmepumpe verstehst, bevor du Steuerungsfunktionen aktivierst.

## Lizenz

MIT Lizenz. Siehe [LICENSE](LICENSE).

---

Dieses Projekt steht in keiner Verbindung zu IDM Energiesysteme GmbH und wird unabhängig bereitgestellt.

<!-- Badge Links -->
[releases-shield]: https://img.shields.io/github/release/xerolux/idm-metrics-collector.svg?style=for-the-badge
[releases]: https://github.com/xerolux/idm-metrics-collector/releases
[downloads-shield]: https://img.shields.io/github/downloads/xerolux/idm-metrics-collector/latest/total.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/xerolux/idm-metrics-collector.svg?style=for-the-badge
[commits]: https://github.com/xerolux/idm-metrics-collector/commits/main
[license-shield]: https://img.shields.io/github/license/xerolux/idm-metrics-collector.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[buymeacoffee]: https://www.buymeacoffee.com/xerolux
[buymeacoffee-badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
