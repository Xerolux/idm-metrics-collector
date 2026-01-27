# Telemetry Server & Community Features - Roadmap & Übergabedokumentation

> **Erstellt:** 2026-01-27
> **Letzte Bearbeitung:** Claude (Session 017Z6yfcDMS5mkLwNHH9KKYc)
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
| **Model Training** (`train_model.py`) | ✅ Fertig | Muss manuell ausgeführt werden |
| **WebUI Config Widget** | ✅ Fertig | In Config.vue integriert |
| **Dashboard Card** | ✅ Fertig | TelemetryStatusCard.vue |
| **Backend Proxy** (`/api/telemetry/pool-status`) | ✅ Fertig | In web.py |

---

## Abgeschlossene Arbeiten

### Session 017Z6yfcDMS5mkLwNHH9KKYc (2026-01-27)

#### Commit 1: `3ef10e1` - Telemetry Server Implementation
- Fehlenden `/api/v1/model/download` Endpoint hinzugefügt
- `/api/v1/pool/status` für Cold-Start-Feedback erstellt
- `/api/v1/models` Admin-Endpoint für Model-Liste
- Rate-Limiting (100 req/min pro IP)
- Deutsche und englische Meldungen für Datenpool-Status
- Model-Hash in Eligibility-Response
- `train_model.py` vollständig implementiert
- Docker-Compose mit Model-Volume und Healthcheck

#### Commit 2: `2a2a689` - Config.vue Data Pool Widget
- Community Datenpool Status Widget in Konfiguration
- Zeigt: Installationen, Datenpunkte, verfügbare Modelle
- Automatisches Laden beim Seitenaufruf
- Refresh-Button für manuelle Aktualisierung
- Backend-Proxy `/api/telemetry/pool-status` in web.py

#### Commit 3: `839830e` - TelemetryStatusCard Dashboard Component
- Neue Dashboard-Karte für Community-Status
- Registriert als Chart-Typ `telemetry_status`
- Kann via Drag-Drop zum Dashboard hinzugefügt werden
- Auto-Refresh alle 5 Minuten

---

## Offene Aufgaben

### Priorität: HOCH

#### 1. Model-Training Pipeline automatisieren
**Datei:** `telemetry_server/scripts/train_model.py`

Aktuell muss das Training manuell ausgeführt werden:
```bash
python train_model.py --model "AERO_SLM" --output model.pkl
```

**TODO:**
- [ ] Cron-Job oder Scheduled Task für automatisches Training
- [ ] GitHub Action für nächtliches Training wenn genug Daten
- [ ] Benachrichtigung an Admin wenn neues Model verfügbar

#### 2. Model-Verschlüsselung vervollständigen
**Datei:** `telemetry_server/scripts/export_model.py`

Der Export existiert, aber:
- [ ] Schlüssel-Management verbessern (nicht hardcoded)
- [ ] Signatur für Model-Integrität hinzufügen
- [ ] Versionierung der Models

#### 3. Tests für Telemetry-Server
**Verzeichnis:** `telemetry_server/tests/` (existiert nicht)

**TODO:**
- [ ] Unit-Tests für alle Endpoints
- [ ] Integration-Tests mit Mock-VictoriaMetrics
- [ ] Load-Tests für Rate-Limiting

---

### Priorität: MITTEL

#### 4. i18n Übersetzungen
**Dateien:**
- `frontend/src/locales/de.json`
- `frontend/src/locales/en.json`

Neue Strings zu übersetzen:
```json
{
  "telemetry": {
    "poolStatus": "Community Data Pool Status",
    "building": "Building data pool",
    "ready": "Data pool ready",
    "sharingEnabled": "Data sharing enabled",
    "sharingDisabled": "Data sharing disabled",
    "installations": "Installations",
    "dataPoints": "Data points",
    "modelsAvailable": "Models available"
  }
}
```

#### 5. Datenvergleich-Feature
**Konzept:** Benutzer können ihre Werte mit Community-Durchschnitt vergleichen

**Benötigt:**
- [ ] Backend-Endpoint für aggregierte Community-Daten
- [ ] Neue Chart-Komponente `CommunityComparisonCard.vue`
- [ ] Datenschutz-Konzept (nur Durchschnittswerte, keine individuellen Daten)

**Beispiel-API:**
```
GET /api/v1/community/averages?model=AERO_SLM&metrics=cop,temp_outdoor
Response: {
  "cop_avg": 4.2,
  "cop_min": 2.8,
  "cop_max": 5.1,
  "temp_outdoor_avg": 8.5,
  "sample_size": 42
}
```

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

### 1. Hardcoded Encryption Key
**Datei:** `telemetry_server/scripts/export_model.py`
```python
# FIXME: Key sollte aus Umgebungsvariable oder Secret Manager kommen
ENCRYPTION_KEY = b'...'  # Hardcoded!
```

### 2. Keine Retry-Logik im TelemetryManager
**Datei:** `idm_logger/telemetry.py`
- Bei Netzwerkfehlern gehen Daten verloren
- TODO: Lokale Persistenz für fehlgeschlagene Sends

### 3. VictoriaMetrics Export Format
**Datei:** `telemetry_server/scripts/train_model.py`
- `eval()` wird verwendet statt `json.loads()` (Sicherheitsrisiko)
- Zeile 38: `yield eval(line)` sollte ersetzt werden

### 4. Fehlende Input-Validierung
**Datei:** `telemetry_server/app.py`
- `installation_id` wird nicht auf gültiges UUID-Format geprüft
- `model` Parameter könnte Path-Traversal-Angriffe ermöglichen

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

# Pool-Status (öffentlich)
curl http://localhost:8000/api/v1/pool/status

# Eligibility prüfen (mit Auth)
curl -H "Authorization: Bearer change-me-to-something-secure" \
  "http://localhost:8000/api/v1/model/check?installation_id=test-uuid"

# Daten senden (mit Auth)
curl -X POST http://localhost:8000/api/v1/submit \
  -H "Authorization: Bearer change-me-to-something-secure" \
  -H "Content-Type: application/json" \
  -d '{
    "installation_id": "test-uuid",
    "heatpump_model": "AERO_SLM",
    "version": "1.0.1",
    "data": [{"timestamp": 1706400000, "temp_outdoor": 5.5}]
  }'
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

---

*Dieses Dokument wurde automatisch erstellt und sollte bei weiteren Änderungen aktualisiert werden.*
