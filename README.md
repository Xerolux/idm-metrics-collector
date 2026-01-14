# IDM Metrics Collector v0.6.0

[![GitHub Release][releases-shield]][releases]
[![Downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![Buy Me A Coffee][buymeacoffee-badge]][buymeacoffee]
[![Tesla](https://img.shields.io/badge/Tesla-Referral-red?style=for-the-badge&logo=tesla)](https://ts.la/sebastian564489)

Ein umfassendes Überwachungs- und Steuerungssystem für IDM Wärmepumpen (Navigator 2.0) mit VictoriaMetrics Speicherung und Grafana-Visualisierung.

## Funktionen

*   **Docker-First**: Optimiert für Docker und Docker Compose Deployments
*   **Zero-Config Setup**: Vollständiger Stack mit VictoriaMetrics und Grafana vorkonfiguriert
*   **Datenquelle**: Liest von der IDM Wärmepumpe via Modbus TCP
*   **Datensenke**: VictoriaMetrics (Prometheus-kompatibel, effizient)
*   **Weboberfläche**: Modernes Dashboard für Live-Daten, Konfiguration, manuelle Steuerung und Zeitplanung
*   **Automatisierung**: Eingebauter Zeitplaner, um Werte (z.B. Temperaturen) zu bestimmten Zeiten zu schreiben
*   **Produktionsbereit**: Health Checks, automatische Neustarts, persistente Daten
*   **Service Code Generator** : Erstellt die aktuellen Codes für Ebene 1 und Ebene 2

## Schnellstart

### Installation mit Docker Compose **[EMPFOHLEN]**

Dies installiert:
- **IDM Metrics Collector** (Web UI + API)
- **VictoriaMetrics** (High-Performance Time Series Database)
- **Grafana** (Visualisierungsplattform)

```bash
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
docker compose up -d
```

Alle Dienste sind vorkonfiguriert und einsatzbereit!

## Zugriff auf die Dienste

### Nach der Installation

**Web UI** (IDM Metrics Collector)
- URL: `http://dein-server-ip:5008`
- Standard-Login: `admin` / `admin` (bitte nach dem ersten Login ändern)
- Funktionen: Live-Dashboard, Bedienfeld, Zeitplaner, Konfiguration

**Grafana**
- URL: `http://dein-server-ip:3001`
- Standard-Login: `admin` / `admin`
- Vorkonfiguriert mit VictoriaMetrics Datenquelle und IDM Dashboard

**VictoriaMetrics**
- URL: `http://dein-server-ip:8428`
- Metrics Ingest Endpoint: `/write` (InfluxDB Line Protocol kompatibel)
- Prometheus Endpoint: `/prometheus`

## Konfiguration

Pfad zur Konfigurationsdatei: `/opt/idm-metrics-collector/config.yaml` oder via Web UI.

Beispiel:

```yaml
idm:
  host: "192.168.1.100"  # IP deiner IDM Wärmepumpe
  port: 502              # Modbus Port
  circuits: ["A"]        # Aktivierte Heizkreise

metrics:
  url: "http://victoriametrics:8428/write"

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

Zugriff auf die Weboberfläche unter `http://<deine-server-ip>:5008`.

*   **Login**: Die Oberfläche ist durch ein Passwort geschützt (Standard: `admin`).
*   **Live Dashboard**: Zeigt kategorisierte Sensorwerte mit automatischer Aktualisierung.
*   **Steuerung**: (Wenn aktiviert) Schreibe Werte auf beschreibbare Sensoren.
*   **Zeitplan**: (Wenn aktiviert) Automatisiere das Setzen von Werten basierend auf Zeit und Tag.
*   **Service Codes**: Code-Generator für Techniker- und Fachmannebene.

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
