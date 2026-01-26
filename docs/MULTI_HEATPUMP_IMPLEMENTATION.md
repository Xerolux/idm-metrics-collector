# Multi-Heatpump Implementation Progress

> **Status**: Phase 1-5 Complete - Core Architecture + API + Frontend + ML Service + Drivers
>
> Last Updated: 2026-01-26

This document tracks the implementation progress of multi-heatpump support.

---

## Completed Components

### 1. Manufacturer Abstraction Layer

**Files:**
- `idm_logger/manufacturers/__init__.py` - Central registry
- `idm_logger/manufacturers/base.py` - Base classes and interfaces

**Key Classes:**
```python
# Base classes
SensorDefinition      # Universal sensor definition
HeatpumpCapabilities  # Device capabilities
HeatpumpDriver        # Abstract driver interface
ManufacturerRegistry  # Driver registration and lookup

# Data types
SensorCategory        # Temperature, Power, Energy, etc.
DataType             # FLOAT, UINT16, INT16, BOOL, etc.
AccessMode           # READ_ONLY, READ_WRITE, WRITE_ONLY
ConnectionConfig     # Host, port, unit_id, timeout
ReadGroup            # Optimized register groups
```

### 2. IDM Navigator 2.0 Driver

**File:** `idm_logger/manufacturers/idm/navigator_2_0.py`

**Features:**
- Wraps existing sensor definitions from `sensor_addresses.py`
- Converts legacy sensors to new `SensorDefinition` format
- Supports heating circuits A-G
- Supports zones 0-9
- IDM-specific byte/word order handling
- Default dashboard template

### 3. NIBE S-Series Driver

**File:** `idm_logger/manufacturers/nibe/s_series.py`

**Features:**
- Supports NIBE S1155, S1255, S2125 via Modbus TCP
- Maps NIBE-specific registers (40000+)
- Handles big-endian data types (INT16, UINT32, etc.)
- Provides default dashboard with temperatures and performance data

### 4. Daikin Altherma Driver

**File:** `idm_logger/manufacturers/daikin/altherma.py`

**Features:**
- Supports Daikin Altherma via Home Hub (EKRHH) in Modbus TCP mode
- Maps registers based on EKMBDXB7V1 specification
- Supports heating, cooling, and hot water control

### 5. Luxtronik 2.1 Driver

**File:** `idm_logger/manufacturers/luxtronik/luxtronik_2_1.py`
**File:** `idm_logger/manufacturers/luxtronik/client.py`

**Features:**
- Supports Bosch, Alpha Innotec, Novelan heat pumps
- Uses custom TCP client to speak the proprietary Luxtronik binary protocol (Port 8889)
- Maps calculations (measurements) and parameters to a unified sensor interface

### 6. Database Schema Extensions

**File:** `idm_logger/db.py`

**New Tables:**
- `heatpumps`: Stores device configuration
- `dashboards`: Stores per-device dashboards

**Extended Tables:**
- `jobs`: Added `heatpump_id`
- `alerts`: Added `heatpump_id`

### 7. HeatpumpManager

**File:** `idm_logger/heatpump_manager.py`

**Features:**
- Manages multiple concurrent connections (Modbus TCP & Custom Clients)
- Parallel sensor reading across all devices
- Async/await based with thread-safe execution
- Automatic reconnection on failure
- Error tracking per device

### 8. Migration System

**File:** `idm_logger/migrations.py`

**Features:**
- Automatically migrates single-device config to multi-device
- Creates "hp-legacy" heatpump from existing `config.idm` settings
- Associates existing jobs/alerts with legacy heatpump

### 9. Metrics Writer Extensions

**File:** `idm_logger/metrics.py`

**New Format:**
```
idm_heatpump_temp_outside{heatpump_id="hp-001",manufacturer="idm",model="navigator_2_0"} 5.2
```

---

## Completed: API Endpoints

**File:** `idm_logger/web.py`

- Full CRUD for Heatpumps
- Manufacturer & Model discovery
- Setup instructions endpoint
- Multi-device data reading and writing
- Dashboard management

---

## Completed: Frontend

- `HeatpumpSelector.vue`: Dropdown to switch active heatpump context
- `HeatpumpSetup.vue`: Wizard for adding new devices
- `DashboardManager.vue`: Updated to support multi-dashboard and heatpump selection
- `heatpumps.js` (Pinia Store): Manages list of devices and active context

---

## Completed: ML Service

**File:** `ml_service/main.py`

- **Multi-Context Architecture:** Maintains separate River anomaly detection models for each heatpump.
- **Grouped Data Fetching:** Queries VictoriaMetrics for all heatpumps and groups results by `heatpump_id`.
- **Per-Device Training:** Models learn and score independently for each device.

---

## Integration

Updated `logger.py` main loop to:
- Use `HeatpumpManager` instead of `ModbusClient`
- Call `heatpump_manager.read_all()`
- Use `metrics.write_all_heatpumps()`
- Run migration at startup

---

## File Structure

```
idm_logger/
├── manufacturers/
│   ├── __init__.py              # Registry (done)
│   ├── base.py                  # Base classes (done)
│   ├── idm/
│   │   ├── __init__.py          # (done)
│   │   └── navigator_2_0.py     # IDM driver (done)
│   ├── nibe/
│   │   ├── __init__.py          # (done)
│   │   └── s_series.py          # NIBE driver (done)
│   ├── daikin/
│   │   ├── __init__.py          # (done)
│   │   └── altherma.py          # Daikin driver (done)
│   └── luxtronik/
│       ├── __init__.py          # (done)
│       ├── luxtronik_2_1.py     # Luxtronik driver (done)
│       └── client.py            # Luxtronik TCP client (done)
├── heatpump_manager.py          # Manager class (done)
├── migrations.py                # Migration logic (done)
├── db.py                        # Extended (done)
├── metrics.py                   # Extended (done)
├── web.py                       # API endpoints (done)
└── logger.py                    # Integration (done)
ml_service/
└── main.py                      # Multi-device support (done)
```

---

## Testing

To test the new components:

```python
# Test driver loading
from idm_logger.manufacturers import ManufacturerRegistry
print(ManufacturerRegistry.list_manufacturers())

# Test database
from idm_logger.db import db
hp_id = db.add_heatpump({
    "name": "Test",
    "manufacturer": "idm",
    "model": "navigator_2_0",
    "connection_config": {"host": "192.168.1.100", "port": 502},
    "device_config": {"circuits": ["A"]}
})
print(db.get_heatpumps())
db.delete_heatpump(hp_id)
```

## Future Work

- Viessmann (API)
- Vaillant (Modbus)
- Stiebel Eltron (Modbus)
