# Multi-Heatpump Support - Feature Plan

> **Ziel**: Unterstützung für mehrere Wärmepumpen verschiedener Hersteller in einem einzigen System

**Status**: Framework Implemented (Phases 1-4 Complete)

## Übersicht

Dieses Feature ermöglicht:
- Verwaltung von 2, 3, 4 oder mehr Wärmepumpen
- Dynamische Dashboards pro Gerät
- Herstellerübergreifende Unterstützung (IDM, NIBE, Daikin, Bosch/Luxtronik)
- Individuelle KI-Überwachung pro Gerät
- Zentralisierte Telemetrie-Datenerfassung

---

## Phase 1: Architektur-Grundlagen (Complete)

### 1.1 Neues Konfigurationsmodell

**Aktuell (Single-Device):**
```python
{
  "idm": {
    "host": "192.168.1.100",
    "port": 502,
    "circuits": ["A"],
    "zones": []
  }
}
```

**Neu (Multi-Device):**
```python
{
  "heatpumps": [
    {
      "id": "hp-001",                    # Eindeutige ID (auto-generiert)
      "name": "Wärmepumpe Gebäude A",    # Benutzerfreundlicher Name
      "manufacturer": "idm",              # Hersteller-Schlüssel
      "model": "navigator_2_0",           # Modell-Schlüssel
      "connection": {
        "host": "192.168.1.100",
        "port": 502,
        "unit_id": 1,
        "timeout": 10,
        "retries": 3
      },
      "config": {
        "circuits": ["A", "B"],           # IDM-spezifisch
        "zones": [1, 2]
      },
      "enabled": true,
      "created_at": "2025-01-26T10:00:00Z"
    },
    {
      "id": "hp-002",
      "name": "Wärmepumpe Gebäude B",
      "manufacturer": "nibe",
      "model": "s1255",
      "connection": {
        "host": "192.168.1.101",
        "port": 502,
        "unit_id": 1
      },
      "config": {},
      "enabled": true
    }
  ],
  # Legacy-Felder für Abwärtskompatibilität (Migration)
  "idm": { ... }  # Wird bei erster Migration zu heatpumps[0] konvertiert
}
```

### 1.2 Datenbank-Schema Erweiterungen

**Neue Tabelle: `heatpumps`**
```sql
CREATE TABLE heatpumps (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    connection_config TEXT NOT NULL,  -- JSON: host, port, unit_id, etc.
    device_config TEXT DEFAULT '{}',  -- JSON: circuits, zones, etc.
    enabled INTEGER DEFAULT 1,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
```

**Erweiterung: `alerts`**
```sql
ALTER TABLE alerts ADD COLUMN heatpump_id TEXT DEFAULT NULL;
-- NULL = gilt für alle, spezifische ID = nur für diese Wärmepumpe
```

**Erweiterung: `jobs`**
```sql
ALTER TABLE jobs ADD COLUMN heatpump_id TEXT NOT NULL DEFAULT 'default';
```

**Neue Tabelle: `dashboards`** (Migration aus settings)
```sql
CREATE TABLE dashboards (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    heatpump_id TEXT,  -- NULL = Übersicht, ID = gerätespezifisch
    config TEXT NOT NULL,  -- JSON: charts array
    position INTEGER DEFAULT 0,
    created_at REAL NOT NULL
);
```

### 1.3 Metric-Naming Convention

**Format:** `idm_heatpump_{metric_name}{heatpump_id="{id}", manufacturer="{mfr}", model="{model}"}`

**Beispiele:**
```
idm_heatpump_temp_outside{heatpump_id="hp-001", manufacturer="idm", model="navigator_2_0"}
idm_heatpump_temp_outside{heatpump_id="hp-002", manufacturer="nibe", model="s1255"}
idm_heatpump_power_current{heatpump_id="hp-001", manufacturer="idm"}
```

**Abfrage in VictoriaMetrics:**
```promql
# Alle Wärmepumpen
idm_heatpump_temp_outside

# Nur IDM-Geräte
idm_heatpump_temp_outside{manufacturer="idm"}

# Spezifische Wärmepumpe
idm_heatpump_temp_outside{heatpump_id="hp-001"}

# Vergleich mehrerer Geräte
idm_heatpump_temp_outside{heatpump_id=~"hp-001|hp-002"}
```

---

## Phase 2: Hersteller-Abstraktionsschicht (Complete)

### 2.1 Plugin-Architektur

```
idm_logger/
├── manufacturers/
│   ├── __init__.py           # Registry & Factory
│   ├── base.py               # Abstrakte Basisklasse
│   ├── idm/
│   │   ├── __init__.py
│   │   ├── navigator_2_0.py  # IDM Navigator 2.0
│   │   └── registers.yaml    # Register-Definitionen
│   ├── nibe/
│   │   ├── __init__.py
│   │   ├── s_series.py       # NIBE S1155, S1255, S2125
│   │   ├── f_series.py       # NIBE F750, F1145, F1245
│   │   └── registers.yaml
│   ├── daikin/
│   │   ├── __init__.py
│   │   ├── altherma.py       # Daikin Altherma (via HomeHub)
│   │   └── registers.yaml
│   └── luxtronik/
│       ├── __init__.py
│       ├── luxtronik_2_1.py  # Bosch, Alpha Innotec, etc.
│       └── registers.yaml
```

### 2.2 Basis-Interface

Implemented in `manufacturers/base.py`.

### 2.3 IDM Navigator 2.0 Driver

Implemented in `manufacturers/idm/navigator_2_0.py`.

### 2.7 Hersteller-Registry

Implemented in `manufacturers/__init__.py`.

---

## Phase 3: Backend-Implementierung (Complete)

### 3.1 Multi-Modbus-Manager

Implemented in `heatpump_manager.py`.

### 3.2 Erweiterte API-Endpunkte

Implemented in `web.py`.

### 3.3 Erweiterte Metriken

Implemented in `metrics.py`.

---

## Phase 4: Frontend-Implementierung (Complete)

### 4.1 Vue-Komponenten

Implemented in `frontend/src/components/heatpump/`.

### 4.2 Pinia Store

Implemented in `frontend/src/stores/heatpumps.js`.

### 4.3 Setup-Wizard Komponente

Implemented in `frontend/src/components/heatpump/HeatpumpSetup.vue`.

### 4.4 Dashboard-Auswahl

Implemented in `frontend/src/components/heatpump/HeatpumpSelector.vue`.

---

## Phase 5: ML-Service Erweiterungen (Complete)

### 5.1 Multi-Model Training

Implemented in `ml_service/main.py`.

---

## Phase 6: Telemetrie-Erweiterungen (Complete)

### 6.1 Telemetrie-Erweiterungen

Implemented in `idm_logger/telemetry.py`.

---

## Phase 7: Migration & Abwärtskompatibilität (Complete)

### 7.1 Migrations-Script

Implemented in `idm_logger/migrations.py`.

---

## Implementierungs-Reihenfolge

### Milestone 1: Basis-Architektur
- [x] Config-Schema erweitern
- [x] Datenbank-Tabellen erstellen
- [x] Migration implementieren
- [x] HeatpumpManager Basisklasse

### Milestone 2: IDM Multi-Instance
- [x] IDM-Driver extrahieren
- [x] Multi-Modbus-Verbindungen
- [x] Metriken mit Labels
- [x] API-Endpunkte erweitern

### Milestone 3: Frontend Multi-Dashboard
- [x] Heatpumps Pinia Store
- [x] HeatpumpSelector Komponente
- [x] HeatpumpSetup Wizard
- [x] Dashboard pro Gerät

### Milestone 4: Weitere Hersteller
- [ ] NIBE S-Series Driver
- [ ] Daikin Altherma Driver
- [ ] Luxtronik Driver

### Milestone 5: ML & Telemetrie
- [x] Multi-Model Training
- [x] Telemetrie v2 Format
- [x] Vergleichs-Dashboards (Partially supported via Multi-Dashboard)

