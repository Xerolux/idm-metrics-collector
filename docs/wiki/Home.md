# 🔥 IDM Metrics Collector - AI-Powered Heat Pump Monitoring & Control

<div align="center">

[![GitHub Release][releases-shield]][releases]
[![Downloads][downloads-shield]][releases]
[![License][license-shield]](LICENSE)
[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]
[![Docker Pulls](https://img.shields.io/docker/pulls/xerolux/idm-metrics-collector?style=for-the-badge)](https://hub.docker.com/r/xerolux/idm-metrics-collector)

</div>

## 🎯 Die intelligente All-in-One Monitoring & Steuerungslösung für IDM Wärmepumpen

> **Künstliche Intelligenz trifft auf Smart Home** - Die professionelle Monitoring-Plattform mit integrierter **KI-Anomalieerkennung**, **Home Assistant Integration** und **vollautomatischer Steuerung** für IDM Navigator 2.0 Wärmepumpen.

<div align="center">

### 🚀 Echtzeit-Überwachung • 🤖 Machine Learning • 📊 Langzeitanalyse • 🏠 Home Assistant • ⚡ Vollautomatisierung

</div>

---

**Keywords:** *Heat Pump Monitoring, IDM Wärmepumpe, AI Anomaly Detection, Machine Learning HVAC, Smart Heating Control, Home Automation, MQTT Integration, Modbus TCP, Energy Efficiency Monitor, COP Analysis, Predictive Maintenance, Smart Home Heat Pump, KI-gesteuerte Heizung, Intelligente Heizungssteuerung, Wärmepumpen-Überwachung, IoT Heating System*

<div align="center">

![Demo Animation](images/demo.gif)

*Echtzeitüberwachung Ihrer IDM Wärmepumpe mit integrierter KI-Anomalieerkennung*

</div>

---

## 📸 Screenshots - Moderne Benutzeroberfläche

<details>
<summary><b>🖼️ Galerie anzeigen (12 Screenshots)</b></summary>
<br>

| 📊 Dashboard Übersicht | 🎮 Intuitive Steuerung |
|:---:|:---:|
| ![Hauptseite](images/screenshots/Hauptseite.png) | ![Steuerung](images/screenshots/Steuerung.png) |
| *Live-Daten aller Sensoren auf einen Blick* | *Direkte Kontrolle über Betriebsmodi und Sollwerte* |

| 📅 Intelligente Zeitpläne | 📝 Detaillierte Protokolle |
|:---:|:---:|
| ![Zeitplan](images/screenshots/Zeitplan.png) | ![Protokoll](images/screenshots/Protokoll.png) |
| *Wochenplan mit Drag & Drop Editor* | *Lückenlose Dokumentation aller Ereignisse* |

| 🔔 Multi-Kanal Benachrichtigungen | 🚨 Sofortige Alarmmeldungen |
|:---:|:---:|
| ![Benachrichtigung](images/screenshots/Benachrichtigung.png) | ![Alarm](images/screenshots/Alarm_Message.png) |
| *Push, Email, Telegram, Signal, Discord* | *Kritische Warnungen in Echtzeit* |

| 🤖 KI-Anomalieerkennung | ⚙️ Umfangreiche Einstellungen |
|:---:|:---:|
| ![KI_Anomalie](images/screenshots/KI_Anomalie.png) | ![Einstellung](images/screenshots/Einstellung.png) |
| *Machine Learning erkennt ungewöhnliches Verhalten* | *Zentrale Konfiguration aller Systemparameter* |

| 🏠 Home Assistant Integration | 🔧 Professionelle Wartungstools |
|:---:|:---:|
| ![MQTT](images/screenshots/MQTT.png) | ![Wartung](images/screenshots/Wartung.png) |
| *Native MQTT Discovery für Home Assistant* | *Service-Codes und Systemdiagnose* |

| 🔑 Code-Generator | 🔐 Sicherer Login |
|:---:|:---:|
| ![Codegenerator](images/screenshots/Codegenerator.png) | ![Login](images/screenshots/Login.png) |
| *Temporäre Techniker-Codes generieren* | *Geschützter Zugang mit Session-Management* |

</details>

---

## 🎯 Warum IDM Metrics Collector?

### Die einzige All-in-One Lösung mit integrierter Künstlicher Intelligenz

Im Gegensatz zu fragmentierten Setups (Modbus-Client + InfluxDB + Grafana + Node-RED + ...) bietet der IDM Metrics Collector **alles aus einer Hand** - optimiert für IDM Wärmepumpen und angetrieben von **Machine Learning**.

<table>
<tr>
<td width="50%">

### 🏆 Traditionelle Lösung
❌ Modbus-Client einrichten<br>
❌ InfluxDB installieren & konfigurieren<br>
❌ Grafana aufsetzen & Dashboards erstellen<br>
❌ Node-RED für Automatisierung<br>
❌ Separate Alerting-Tools<br>
❌ Manuelle MQTT-Integration<br>
❌ 5+ unterschiedliche Systeme<br>
❌ Komplexe Wartung & Updates<br>
❌ Keine KI-Features

</td>
<td width="50%">

### ✅ IDM Metrics Collector
✅ **Ein** Docker-Compose Befehl<br>
✅ VictoriaMetrics bereits integriert<br>
✅ Modernes Dashboard vorinstalliert<br>
✅ Scheduler & Automatisierung eingebaut<br>
✅ Multi-Kanal Alerting out-of-the-box<br>
✅ Native Home Assistant Integration<br>
✅ **Alles in einem** System<br>
✅ Automatische Updates via Watchtower<br>
✅ **🤖 KI-Anomalieerkennung inklusive!**

</td>
</tr>
</table>

---

## 🤖 KI-Features: Der Game Changer

### Warum ist die integrierte KI so revolutionär?

<div align="center">

| Feature | Ohne KI (Traditional) | Mit IDM Metrics Collector AI |
|---------|----------------------|------------------------------|
| **Fehlererkennung** | ⚠️ Manuelle Schwellwerte<br>Viele False Positives | ✅ **Automatisches Lernen**<br>Erkennt Muster & Anomalien |
| **Wartungsvorhersage** | ❌ Reaktiv nach Ausfall | ✅ **Predictive Maintenance**<br>Frühwarnung vor Problemen |
| **Betriebsoptimierung** | ⚠️ Statische Regelung | ✅ **Adaptive Intelligence**<br>Lernt Ihr Heizverhalten |
| **Expertenwissen** | ❌ Techniker erforderlich | ✅ **Community Learning**<br>Profitiert von tausenden Anlagen |

</div>

### 🧠 So funktioniert die KI

```
┌─────────────────────────────────────────────────────────────────┐
│                    ONLINE MACHINE LEARNING                      │
│                   (River/HalfSpaceTrees)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │   1. DATENERFASSUNG (alle 30-60s)    │
         │   • 50+ Sensoren der Wärmepumpe       │
         │   • Außentemperatur, Vorlauf, COP      │
         │   • Betriebsmodus, Verdichterstatus    │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │   2. FEATURE ENGINEERING (Automatisch)│
         │   • Zeitliche Merkmale (Stunde, Tag)  │
         │   • Delta-Features (Änderungsraten)    │
         │   • Berechnete Werte (Spreizung, COP) │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │   3. MULTI-MODE LEARNING              │
         │   🔥 Heizen  ❄️ Kühlen  💧 Warmwasser │
         │   Separate Modelle pro Betriebsmodus   │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │   4. ANOMALIEERKENNUNG (Score 0-1)    │
         │   • Vergleich mit gelerntem Normalzustand│
         │   • Ensemble aus 25 Decision Trees     │
         │   • Debouncing: 3+ aufeinanderfolgende │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │   5. INTELLIGENTES ALERTING           │
         │   🔔 Push • 📧 Email • 💬 Telegram    │
         │   • 1h Cooldown (kein Spam)           │
         │   • Nur bei echten Anomalien          │
         └────────────────────────────────────────┘
```

### 🎯 Praktische Beispiele: Was die KI erkennt

| Anomalie | Wie die KI es findet | Traditionelle Schwellwerte |
|----------|----------------------|----------------------------|
| **Defekter Durchflusssensor** | Temperatur-Spreizung passt nicht zu Leistung | ❌ Schwer zu erkennen |
| **Undichte Heizkreis** | COP sinkt schleichend über Wochen | ❌ Zu langsam für Alarm |
| **Verschmutzter Filter** | Druckdifferenz erhöht sich graduell | ❌ Keine historischen Daten |
| **Falsche Heizkurve** | System verhält sich anders als ähnliche Anlagen | ❌ Unmöglich ohne Community-Daten |
| **Beginnender Kompressor-Defekt** | Untypische Vibrationen/Laufzeiten | ✅ **KI erkennt es 2-4 Wochen vorher!** |

---

## ⚡ Highlights & Alleinstellungsmerkmale

<div align="center">

### 🏆 Was macht diese Software einzigartig?

</div>

| Feature | Beschreibung | Vorteil |
|---------|-------------|---------|
| 🤖 **Online Machine Learning** | Modell lernt kontinuierlich während des Betriebs | Keine manuelle Konfiguration, automatische Verbesserung |
| 🏠 **Native Home Assistant Integration** | MQTT Discovery - Sensoren erscheinen automatisch in HA | Plug & Play ohne manuelle YAML-Konfiguration |
| 📊 **Grafana-ähnliches Dashboard** | Drag & Drop, Zoom, Pan, Dual Y-Achsen, Chart Templates | Keine separate Grafana-Installation nötig |
| ⚡ **Modbus mit Exponential Backoff** | Intelligente Wiederverbindung bei Netzwerkproblemen | 99.9% Verfügbarkeit auch bei instabilen Verbindungen |
| 🔔 **Multi-Channel Alerting** | Signal, Telegram, Discord, Email, ntfy, MQTT | Warnungen dort, wo Sie sie brauchen |
| 🌙 **Dark Mode Support** | Automatische System-Preference Erkennung | Augenschonend bei Tag & Nacht |
| 📅 **Visueller Zeitplan-Editor** | Wochenplan mit Drag & Drop | Heizzeiten ohne Programmierkenntnisse |
| ☀️ **Solar PV Integration** | Überschussstrom-Steuerung über Register 74 | Maximale Eigenverbrauchsoptimierung |
| 🔐 **Techniker-Code Generator** | Temporäre Service-Codes mit Zeitbegrenzung | Sicherer Fernzugriff für Wartung |
| 📦 **Docker-Basiert** | Multi-Container mit Auto-Updates (Watchtower) | Einfache Installation, automatische Sicherheitsupdates |
| 💾 **Automatische Backups** | WebDAV-Support (Nextcloud, Seafile, etc.) | Datensicherheit ohne manuelle Eingriffe |
| 🔍 **VictoriaMetrics TimeseriesDB** | 1 Jahr Datenretention, schnelle Abfragen | Langzeit-Trendanalysen und Effizienzvergleiche |

### 🎨 Dashboard Features - Auf Grafana-Niveau

- **Modernes Dashboard** mit Drag & Drop, Zoom & Pan
- **Dual Y-Achsen** für Temperatur + Leistung in einem Chart
- **Stat & Gauge Panels** für Soll/Ist-Vergleiche und COP-Anzeigen
- **Chart Templates** - One-Click Dashboards für alle Anwendungsfälle
- **Vollbildmodus** für jeden einzelnen Chart
- **Export-Funktion** - Dashboards als PNG/PDF speichern
- **Responsive Design** - Optimiert für Desktop, Tablet & Smartphone
- **WebSocket Live-Updates** - Keine Verzögerung, keine Polling-Lags

---

## 📚 Dokumentation & Ressourcen

### Umfassende Anleitungen für jeden Bedarf

<table>
<tr>
<td>

#### 📖 Benutzer-Dokumentation
- **[Benutzerhandbuch (PDF)][docs-pdf]** - Komplette Bedienungsanleitung (50+ Seiten)
- **[Online Dokumentation][docs-online]** - Interaktive Feature-Referenz
- **[Installations-Guide](docs/INSTALL.md)** - Schritt-für-Schritt Anleitung
- **[FAQ & Troubleshooting](docs/FAQ.md)** - Häufige Fragen beantwortet

</td>
<td>

#### 🔧 Technische Dokumentation
- **[Feature-Übersicht](FEATURES.md)** - Alle Features im Detail
- **[Architektur-Diagramm](docs/ARCHITECTURE.md)** - System-Design
- **[MQTT Setup Guide](docs/MQTT_SETUP.md)** - Home Assistant Integration
- **[Backup & Restore](docs/BACKUP_RESTORE.md)** - Datensicherung

</td>
</tr>
<tr>
<td>

#### 🌍 Weitere Hersteller
- **[Alpha Innotec / Stiebel Eltron](docs/ALPHAINNOTEC_STIEBEL_ELTRON_MODBUS_REGISTERS.md)**
- **[Bosch / Buderus](docs/BOSCH_BUDERUS_MODBUS_REGISTERS.md)**
- **[Viessmann Vitocal](docs/VIESSMANN_VITOCAL_MODBUS_REGISTERS.md)**
- **[NIBE S-Series](docs/NIBE_S_SERIES_MODBUS_REGISTERS.md)**
- **[Wolf CHA](docs/WOLF_CHA_MODBUS_REGISTERS.md)**

</td>
<td>

#### 🚀 Erweiterte Themen
- **[Solar Integration](docs/SOLAR_INTEGRATION.md)** - PV-Überschusssteuerung
- **[Sicherheitsanalyse](docs/SECURITY_ANALYSIS.md)** - Penetration Test Ergebnisse
- **[Changelog](CHANGELOG.md)** - Versionshistorie
- **[Roadmap](ROADMAP.md)** - Geplante Features

</td>
</tr>
</table>

---
