# Telemetry Server & Community Features - Roadmap & Übergabedokumentation

> **Erstellt:** 2026-01-27
> **Letzte Bearbeitung:** Jules (Session Update)
> **Branch:** `claude/telemetry-server-review-W1oKn`
> **Status:** In Entwicklung

---

## Inhaltsverzeichnis

1. [Aktueller Stand](#aktueller-stand)
2. [Abgeschlossene Arbeiten](#abgeschlossene-arbeiten)
3. [Offene Aufgaben](#offene-aufgaben)
4. [Zukünftige Features](#zukünftige-features)
5. [Technische Schulden](#technische-schulden)
6. [Architektur-Entscheidungen](#architektur-entscheidungen)
7. [Wichtige Dateien](#wichtige-dateien)
8. [Test-Hinweise](#test-hinweise)

---

## Aktueller Stand

### Telemetry-System Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEMETRY ARCHITEKTUR                        │
└─────────────────────────────────────────────────────────────────┘

  IDM Logger (Client)              Telemetry Server
  ┌─────────────────┐              ┌─────────────────┐
  │ TelemetryManager│──────────────│ FastAPI App     │
  │ - Buffer (2000) │   HTTPS      │ - /api/v1/submit│
  │ - 24h Intervall │   POST       │ - /api/v1/check │
  │ - Auth Token    │              │ - /api/v1/download
  └────────┬────────┘              └────────┬────────┘
           │                                │
  ┌────────▼────────┐              ┌────────▼────────┐
  │ ModelUpdater    │◄─────────────│ VictoriaMetrics │
  │ - Eligibility   │   Model.enc  │ - 12 Monate     │
  │ - Download      │              │ - Retention     │
  └─────────────────┘              └─────────────────┘
```

### Funktionsstatus

| Komponente | Status | Hinweise |
|------------|--------|----------|
| **Datenempfang** (`/api/v1/submit`) | ✅ Fertig | Rate-Limiting implementiert |
| **Eligibility Check** (`/api/v1/model/check`) | ✅ Fertig | Mit Cold-Start-Feedback |
| **Model Download** (`/api/v1/model/download`) | ✅ Fertig | Hash-basierte Updates |
| **Pool Status** (`/api/v1/pool/status`) | ✅ Fertig | Öffentlicher Endpoint |
| **Community Averages** (`/api/v1/community/averages`) | ✅ Fertig | Aggregierte Metriken (Avg/Min/Max) |
| **Model Training** (`train_model.py`) | ✅ Fertig | Automatisiert via Scheduler |
| **WebUI Config Widget** | ✅ Fertig | In Config.vue integriert |
| **Dashboard Card** | ✅ Fertig | TelemetryStatusCard.vue |
| **Backend Proxy** (`/api/telemetry/pool-status`) | ✅ Fertig | In web.py |

---

## Abgeschlossene Arbeiten

### Session Update (Jules)

#### Feature: Model Encryption & Testing
- `export_model.py`: Auf JSON-Format umgestellt, signiert (HMAC-SHA256) und Env-Var für Key.
- `ml_service/utils/crypto.py`: Support für JSON-formatiertes Community-Model hinzugefügt.
- Bugfix: `load_encrypted_model` gibt nun deserialisiertes Objekt zurück.
- Test-Suite für Telemetry-Server erstellt (`test_crypto.py`, `test_app.py`).

#### Feature: Automation & Security Hardening
- `training_scheduler.py`: Täglicher Trainings-Job für Community-Modelle.
- `telemetry_server/docker-compose.yml`: Neuer Service `telemetry-trainer`.
- `telemetry_server/app.py`: Strikte Input-Validierung (UUID, Regex) hinzugefügt.
- Security: Signaturen umfassen nun auch Metadaten (Model-Name, Timestamp).
- Unit Tests erweitert und `eval()` aus Code entfernt.

#### Feature: Localization (i18n)
- Telemetry-UI ins Deutsche und Englische übersetzt (`en.json`, `de.json`).
- `Config.vue` und `TelemetryStatusCard.vue` aktualisiert.

#### Feature: Data Comparison (Datenvergleich)
- **Backend-Endpoint:** `/api/v1/community/averages` implementiert.
- **Logik (`analysis.py`):** Aggregation von Community-Daten (Avg, Min, Max) via VictoriaMetrics.
- **Tests:** Unit Tests für Analyse-Logik und API-Endpoint hinzugefügt.

---

## Offene Aufgaben

### Priorität: HOCH

#### 5. Frontend Integration Datenvergleich
**Konzept:** Visualisierung der Community-Daten im Vergleich zu eigenen Werten.

- [ ] Neue Chart-Komponente `CommunityComparisonCard.vue`.
- [ ] Integration in Dashboard.
- [ ] Backend-Proxy im `idm_logger` für den neuen Endpoint.

---

### Priorität: MITTEL

#### 6. COP-Ranking Widget
**Konzept:** Anonymes Ranking der COP-Werte

- [ ] Backend: Percentil-Berechnung
- [ ] Frontend: Ranking-Anzeige ("Ihr COP ist besser als 75% der Nutzer")
- [ ] Gamification: Badges für Effizienz

---

### Priorität: NIEDRIG

#### 7. Push-Notifications für Eligibility
**Konzept:** Benachrichtigung wenn Benutzer für Community-Model berechtigt wird

- [ ] Nach 30 Tagen Datensammlung
- [ ] Über bestehende Notification-Kanäle (Telegram, Discord, etc.)

#### 8. Telemetry-Dashboard für Admins
**Konzept:** Separate Admin-Oberfläche für Telemetry-Server

- [ ] Übersicht aller Installationen (anonymisiert)
- [ ] Model-Training-Status
- [ ] Datenqualitäts-Metriken

---

## Zukünftige Features

### Neue Wärmepumpen-Unterstützung

| Hersteller | Modell | Protokoll | Priorität | Status |
|------------|--------|-----------|-----------|--------|
| **Viessmann** | Vitocal 250-A | Modbus TCP | Hoch | Nicht begonnen |
| **Vaillant** | aroTHERM plus | Modbus TCP | Hoch | Nicht begonnen |
| **Stiebel Eltron** | WPL-A Premium | Modbus TCP | Mittel | Nicht begonnen |
| **Mitsubishi** | Ecodan | Modbus TCP | Mittel | Nicht begonnen |
| **Panasonic** | Aquarea | Modbus TCP | Niedrig | Nicht begonnen |

**Implementierungs-Template:**
```
idm_logger/manufacturers/
└── viessmann/
    ├── __init__.py
    ├── vitocal.py          # Register-Definitionen
    └── sensor_addresses.py  # Modbus-Adressen
```

### ML/KI Erweiterungen

#### Predictive Maintenance
- Vorhersage von Wartungsbedarf basierend auf Betriebsmuster
- Anomalie-Erkennung für verschleißbedingte Änderungen

#### Wetter-Integration
- Automatische Anpassung der Heizkurve basierend auf Wettervorhersage
- Integration mit OpenWeatherMap oder ähnlichen APIs

#### Energie-Optimierung
- Automatische Vorschläge zur Effizienzsteigerung
- Smart-Grid-Integration für PV-Überschuss-Nutzung

---

## Technische Schulden

### 1. Keine Retry-Logik im TelemetryManager
**Datei:** `idm_logger/telemetry.py`
- Bei Netzwerkfehlern gehen Daten verloren
- TODO: Lokale Persistenz für fehlgeschlagene Sends

---

## Architektur-Entscheidungen

### ADR-001: Separater Telemetry-Server
**Entscheidung:** Telemetry-Server läuft unabhängig vom Haupt-Logger

**Begründung:**
- Skalierbarkeit: Kann auf dediziertem Server laufen
- Sicherheit: Trennung von Benutzer- und Community-Daten
- Unabhängigkeit: Updates am Logger beeinflussen Server nicht

### ADR-002: VictoriaMetrics für Telemetry
**Entscheidung:** VictoriaMetrics statt InfluxDB oder TimescaleDB

**Begründung:**
- Bereits im Projekt verwendet
- Geringer Ressourcenverbrauch
- Einfache PromQL-Abfragen

### ADR-003: 30-Tage Eligibility-Fenster
**Entscheidung:** Benutzer müssen 30 Tage Daten senden für Community-Model

**Begründung:**
- Verhindert "Hit-and-Run" (einmal senden, immer profitieren)
- Fördert kontinuierliche Teilnahme
- Ausreichend Daten für sinnvollen Beitrag

### ADR-004: Quid-Pro-Quo Modell
**Entscheidung:** Nur Daten-Beitragende erhalten Community-Modelle

**Begründung:**
- Fairer Austausch
- Motivation zur Teilnahme
- Qualitätssicherung der Daten

---

## Wichtige Dateien

### Telemetry Server
```
telemetry_server/
├── app.py                      # FastAPI Server (Haupt-Endpoints)
├── analysis.py                 # Community Data Aggregation
├── training_scheduler.py       # Training Automation
├── docker-compose.yml          # Container-Orchestrierung
├── Dockerfile                  # Container-Build
├── requirements.txt            # Python-Abhängigkeiten
└── scripts/
    ├── train_model.py          # ML-Training Pipeline
    ├── export_model.py         # Model-Verschlüsselung
    └── manage.py               # CLI-Verwaltung
```

### Client-Seite (IDM Logger)
```
idm_logger/
├── telemetry.py                # TelemetryManager (Daten senden)
├── model_updater.py            # ModelUpdater (Models empfangen)
└── web.py                      # Backend-Proxy (/api/telemetry/pool-status)
```

### Frontend
```
frontend/src/
├── components/
│   ├── TelemetryStatusCard.vue # Dashboard-Karte
│   └── DashboardManager.vue    # Integration (Zeile 225-228)
├── views/
│   └── Config.vue              # Datenpool-Widget (Zeile 283-344)
└── utils/
    └── chartTypes.js           # Chart-Typ Registry (TELEMETRY_STATUS)
```

---

## Test-Hinweise

### Telemetry-Server lokal testen
```bash
cd telemetry_server

# Server starten
docker compose up -d

# Health-Check
curl http://localhost:8000/health

# Community Averages abrufen (mit Auth)
curl -H "Authorization: Bearer change-me-to-something-secure" \
  "http://localhost:8000/api/v1/community/averages?model=AERO_SLM&metrics=cop_current,temp_outdoor"
```

### Frontend testen
```bash
cd frontend
pnpm install
pnpm run dev

# Browser öffnen: http://localhost:5173
# Navigieren zu: Konfiguration > KI-Analyse
# Das "Community Datenpool Status" Widget sollte sichtbar sein
```

### Backend-Proxy testen
```bash
# Annahme: Logger läuft auf Port 5008
curl http://localhost:5008/api/telemetry/pool-status
```

---

## Ansprechpartner & Ressourcen

- **Repository:** https://github.com/Xerolux/idm-metrics-collector
- **Issues:** https://github.com/Xerolux/idm-metrics-collector/issues
- **Dokumentation:** `docs/` Verzeichnis

---

## Changelog dieser Session

| Commit | Beschreibung |
|--------|--------------|
| `3ef10e1` | Complete telemetry server implementation with cold start handling |
| `2a2a689` | Add data pool status widget to Config.vue |
| `839830e` | Add TelemetryStatusCard dashboard component |
| `[Pending]` | Telemetry Model Encryption, Automation, Localization & Comparison |

---

*Dieses Dokument wurde automatisch erstellt und sollte bei weiteren Änderungen aktualisiert werden.*
