# IDM Metrics Collector 0.6.0

[![GitHub Release][releases-shield]][releases]
[![Downloads][downloads-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![Buy Me A Coffee][buymeacoffee-badge]][buymeacoffee]
[![Tesla](https://img.shields.io/badge/Tesla-Referral-red?style=for-the-badge&logo=tesla)](https://ts.la/sebastian564489)

**Das ultimative Dashboard für deine IDM Wärmepumpe.**

Ein modernes, docker-basiertes System zur Überwachung, Steuerung und Automatisierung von IDM Wärmepumpen (Navigator 2.0). Inklusive Langzeitspeicherung (VictoriaMetrics) und professioneller Visualisierung (Grafana).

> **Hardware Kompatibilität**
>
> ✅ **Verifiziert:** Getestet an einer **IDM ALM 6-15** Wärmepumpe.
>
> Das System nutzt das standardisierte Modbus TCP Interface des Navigator 2.0 Reglers und sollte mit den meisten modernen IDM Anlagen kompatibel sein.

---

![Demo](docs/images/demo.gif)

## ✨ Funktionen

| Feature | Beschreibung |
| :--- | :--- |
| 🚀 **Docker-First** | Fertiges `docker-compose` Setup. Startklar in Sekunden. |
| 📊 **Visualisierung** | Vorkonfiguriertes **Grafana** Dashboard + **VictoriaMetrics** DB. |
| 📱 **Responsive UI** | Modernes Web-Interface für Desktop, Tablet und Mobile. |
| ⚡ **Zero-Config** | Automatische Erkennung und Einrichtung der Datenbank. |
| 🤖 **Automatisierung** | Integrierter Zeitplaner für Heizkreise & Warmwasser. |
| 🔔 **Alerting** | Benachrichtigungen bei Störungen oder Grenzwertüberschreitungen. |
| 🔑 **Service Codes** | Eingebauter Generator für Fachmann- & Technikercodes. |

## 📸 Einblicke

| Dashboard | Steuerung |
| :---: | :---: |
| ![Dashboard](docs/screenshots/02_dashboard.png) | ![Control](docs/screenshots/03_control.png) |
| **Alles im Blick** | **Volle Kontrolle** |

| Zeitplaner | Konfiguration |
| :---: | :---: |
| ![Schedule](docs/screenshots/04_schedule.png) | ![Config](docs/screenshots/06_config.png) |
| **Smarte Zeitpläne** | **Einfache Einrichtung** |

## 🚀 Schnellstart

Die Installation ist dank Docker denkbar einfach. Du benötigst lediglich ein System mit installiertem Docker & Docker Compose.

### 1. Repository klonen
```bash
git clone https://github.com/Xerolux/idm-metrics-collector.git
cd idm-metrics-collector
```

### 2. Starten
```bash
docker compose up -d
```
*Das war's! Die Container werden gebaut und gestartet.*

### 3. Zugriff

| Dienst | URL | Login (Default) | Beschreibung |
| :--- | :--- | :--- | :--- |
| **Web UI** | `http://<ip>:5008` | `admin` / `admin` | Hauptinterface, Config, Steuerung |
| **Grafana** | `http://<ip>:3001` | `admin` / `admin` | Historische Daten & Analysen |
| **Datenbank** | `http://<ip>:8428` | - | VictoriaMetrics API Endpunkte |

---

## ⚙️ Konfiguration

Die Konfiguration erfolgt primär über die Web-Oberfläche (`Einstellungen`). Alternativ kann die Datei `config.yaml` direkt bearbeitet werden.

**Wichtigste Einstellungen:**
*   **IDM Host:** IP-Adresse deiner Wärmepumpe.
*   **Heizkreise:** Welche Heizkreise (A, B, C...) sind aktiv?
*   **Schreibzugriff:** Muss explizit aktiviert werden, um Werte zu ändern.

## ⚠️ Haftungsausschluss

Dieses Projekt ist eine private Entwicklung und steht in keiner Verbindung zu IDM Energiesysteme GmbH.
Die Nutzung erfolgt auf eigene Gefahr. Insbesondere Schreibvorgänge (Steuerung) sollten mit Bedacht konfiguriert werden.

## 🤝 Support & Community

Probleme? Fragen? Ideen?

*   🐛 [Issue erstellen](https://github.com/xerolux/idm-metrics-collector/issues)
*   💬 [Discord Community][discord]
*   ☕ [Unterstütze das Projekt][buymeacoffee]

---
License: MIT

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
