# Changelog - IDM Metrics Collector

Alle Änderungen, Features und Verbesserungen chronologisch dokumentiert.

---

## [1.0.8] - 2026-04-01

### 🔒 Security Patch Release

Dieses Release schließt die offenen Dependabot-Warnungen aus Frontend- und Telemetry-Abhängigkeiten.

### ✨ Änderungen

- Telemetry Dependencies aktualisiert:
  - `cryptography` auf `46.0.6`
  - `orjson` auf `3.11.6`
  - `requests` auf `2.33.1`
- Frontend Dependency/Lockfile gehärtet:
  - `socket.io-client` auf `^4.8.3`
  - sichere Versionen für `brace-expansion`, `picomatch`, `flatted`, `socket.io-parser`
- `pnpm-lock.yaml` regeneriert

### ✅ Ergebnis

- Open Dependabot Alerts: **0**

*Stand: 2026-04-01*
*Version: 1.0.8*

---

## [1.0.7] - 2026-04-01

### 🔐 Security, Telemetry & Ops Release

Dieses Release fokussiert sich auf produktionsreifes Telemetry-Hardening, Admin-Schutz und vereinfachte Betriebsabläufe.

### ✨ Highlights

- Striktere Admin-Absicherung im Telemetry Server (dediziertes Admin-Token + Schutzpfade)
- Neue Ops- und Security-Dokumentation für Public Deployments
- Neue Betriebs-Skripte:
  - Secret Rotation
  - Image Digest Pinning
  - Backup/Restore-Verifikation
- Erweiterter `telemetry` Wrapper mit Menü, Risiko-Stufen, Bestätigungen und sicherem Update-Modus
- Monitoring-Verbesserungen inkl. Alert-Regel-Generator und Prometheus-Beispiel
- CI-Härtung mit automatischem Security-Check für produktive Konfigurationen
- Shared Dashboard View im Frontend/Backend vervollständigt

### 🧪 Qualität

- Neue und angepasste Telemetry-Tests für Strict Admin Auth und Rollenverhalten
- Build/Runtime Checks für neue Telemetry- und Ops-Komponenten

*Stand: 2026-04-01*
*Version: 1.0.7*

---

## [1.0.3] - 2026-01-28

### 🔧 Code Quality & Maintenance Release

Dieses Release fokussiert sich auf Code-Qualität, Refactoring und Stabilität.

---

### ✨ Verbesserungen

#### Dynamische Versionsverwaltung
- Swagger API-Version wird nun dynamisch aus der VERSION-Datei gelesen
- Update-Manager verwendet lokale VERSION-Datei als primäre Quelle
- Konsistente Versionierung über alle Komponenten hinweg

#### Code-Cleanup
- Entfernung von Debug console.log-Statements im Frontend
- WebSocket-Client bereinigt von unnötigem Debug-Logging
- ChartCard-Komponente optimiert und aufgeräumt

#### Linter-Konformität
- Python-Code entspricht jetzt vollständig Ruff-Standards
- Frontend-Code entspricht ESLint-Standards
- Entfernung ungenutzter Imports und Variablen
- Formatierung aller Python-Dateien mit Ruff

#### Stabilität
- Verbesserte Modbus-Verbindungsstabilität
- ML-Service-Verbindungen für Produktionseinsatz optimiert

---

### 📊 Statistiken

**Geänderte Dateien:** 15+
**Entfernte Debug-Statements:** 20+
**Code-Qualität:** Ruff & ESLint konform

*Stand: 2026-01-28*
*Version: 1.0.3*

---

## [0.7.0] - 2025-01-22

### 🎉 Major Release - Dashboard Revolution

Dieses Release bringt das integrierte Dashboard auf ~85% Feature-Parität zu Grafana!

---

### ✨ Neue Features

#### Dashboard & Visualisierung

**🌙 Dark Mode Support**
- Automatische Erkennung von System-Preference (prefers-color-scheme)
- Manuelle Umschaltung via Button (Mond/Sonne Icon)
- Persistenz im LocalStorage
- Alle Components passen sich an (Charts, Tooltips, Grids)
- Reactive Farbgebung basierend auf Theme

**📋 Chart Templates (One-Click Dashboards)**
- 7+ vorkonfigurierte Templates für häufige Anwendungsfälle
- Template-Dialog mit Kategorie-Filter
- Automatische Dashboard-Erstellung aus Templates

**⚡ Chart Zoom & Pan**
- Mausrad-Zoom (Geschwindigkeit 0.1)
- Drag-to-Zoom mit visueller Markierung
- Pinch-Zoom für Touch-Geräte
- Pan mit Ctrl+Drag
- Reset-Button erscheint bei Zoom

**📊 Dual Y-Achsen**
- Linke Y-Achse: Erste Query (z.B. Temperatur)
- Rechte Y-Achse: Zweite+ Queries (z.B. Leistung)
- Unabhängige Skalierung beider Achsen

**💬 Verbesserte Tooltips**
- Deutsches Datumsformat (dd.MM.yyyy HH:mm)
- Weißer/Heller Hintergrund je nach Theme
- Farbige Indikatoren pro Serie
- 2 Dezimalstellen für Präzision

**📈 StatCard Component**
- Große Einzelwert-Anzeige
- Trend-Indikator (Pfeil + Prozent)
- Farbschwellen (low/high/normal)
- Soll/Ist Vergleich mit Fortschrittsbalken

**🎯 GaugeCard Component**
- Halbkreis-Tachometer mit Animation
- Farbige Zonen (Grün → Gelb → Rot)
- Min/Max Konfiguration

**📥 Dashboard Export (PNG/PDF)**
- PNG Export mit Qualitätseinstellungen (1x-4x Scale)
- PDF Export (A4 Querformat)
- Automatische Dateinamen mit Datum

---

### 📚 Dokumentation

**Neue Dokumentations-Files:**

1. **FEATURES.md** - Umfassende Feature-Dokumentation
2. **ROADMAP.md** - Detaillierte Planung zu 100% Parität
3. **README.md** - Professionell überarbeitet

---

### 📊 Feature-Parität zu Grafana

| Feature | v0.6.0 | v0.7.0 | Grafana |
|---------|--------|--------|---------|
| Line Charts | ✅ | ✅ | ✅ |
| Zoom & Pan | ❌ | ✅ | ✅ |
| Dual Y-Achsen | ❌ | ✅ | ✅ |
| Stat Panels | ❌ | ✅ | ✅ |
| Gauge Charts | ❌ | ✅ | ✅ |
| Dark Mode | ❌ | ✅ | ✅ |
| Templates | ❌ | ✅ | ✅ |
| Export | ❌ | ✅ | ✅ |

**Gesamt-Parität**: ~85% (von ~65% in v0.6.0)

---

### 📈 Statistiken

**Neue Files:** 12 Components/Utilities
**Code-Zeilen:** ~3.800+ hinzugefügt
**Geänderte Files:** 8 aktualisiert

*Stand: 2025-01-22*
*Version: 0.7.0*
