# Multi-Heatpump Implementation Progress

> **Status**: Phase 1+2 Complete - Core Architecture + API Implemented
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

**Usage:**
```python
from idm_logger.manufacturers import ManufacturerRegistry

# List all manufacturers
manufacturers = ManufacturerRegistry.list_manufacturers()

# Get a driver
driver = ManufacturerRegistry.get_driver("idm", "navigator_2_0")
sensors = driver.get_sensors({"circuits": ["A", "B"]})
capabilities = driver.get_capabilities()
```

---

### 2. IDM Navigator 2.0 Driver

**File:** `idm_logger/manufacturers/idm/navigator_2_0.py`

**Features:**
- Wraps existing sensor definitions from `sensor_addresses.py`
- Converts legacy sensors to new `SensorDefinition` format
- Supports heating circuits A-G
- Supports zones 0-9
- IDM-specific byte/word order handling
- Default dashboard template

**Configuration:**
```python
device_config = {
    "circuits": ["A", "B"],  # Heating circuits
    "zones": [0, 1, 2]       # Zone IDs
}
```

---

### 3. Database Schema Extensions

**File:** `idm_logger/db.py`

**New Tables:**
```sql
-- Heat pumps
CREATE TABLE heatpumps (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    connection_config TEXT NOT NULL,  -- JSON
    device_config TEXT DEFAULT '{}',  -- JSON
    enabled INTEGER DEFAULT 1,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

-- Per-device dashboards
CREATE TABLE dashboards (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    heatpump_id TEXT,
    config TEXT NOT NULL,  -- JSON
    position INTEGER DEFAULT 0,
    created_at REAL NOT NULL,
    FOREIGN KEY (heatpump_id) REFERENCES heatpumps(id) ON DELETE CASCADE
);
```

**Extended Tables:**
```sql
-- jobs and alerts now have heatpump_id column
ALTER TABLE jobs ADD COLUMN heatpump_id TEXT DEFAULT NULL;
ALTER TABLE alerts ADD COLUMN heatpump_id TEXT DEFAULT NULL;
```

**New Methods:**
```python
# Heatpump CRUD
db.get_heatpumps()
db.get_heatpump(hp_id)
db.add_heatpump(config)
db.update_heatpump(hp_id, fields)
db.delete_heatpump(hp_id)
db.get_enabled_heatpumps()

# Dashboard CRUD
db.get_dashboards(heatpump_id=None)
db.get_dashboard(dash_id)
db.add_dashboard(config)
db.update_dashboard(dash_id, fields)
db.delete_dashboard(dash_id)
db.delete_dashboards_for_heatpump(hp_id)

# Filtered queries
db.get_jobs_for_heatpump(hp_id)
db.get_alerts_for_heatpump(hp_id)
```

---

### 4. HeatpumpManager

**File:** `idm_logger/heatpump_manager.py`

**Features:**
- Manages multiple concurrent Modbus connections
- Parallel sensor reading across all devices
- Async/await based with thread pool for blocking I/O
- Automatic reconnection on failure
- Error tracking per device

**API:**
```python
from idm_logger.heatpump_manager import heatpump_manager

# Initialize at startup
await heatpump_manager.initialize()

# Read all heatpumps
data = await heatpump_manager.read_all()
# Returns: {"hp-001": {"temp_outside": 5.2, ...}, "hp-002": {...}}

# Read specific heatpump
data = await heatpump_manager.read_heatpump("hp-001")

# Write value
await heatpump_manager.write_value("hp-001", "temp_water_target", 50)

# CRUD operations
hp_id = await heatpump_manager.add_heatpump({
    "name": "Main Building",
    "manufacturer": "idm",
    "model": "navigator_2_0",
    "connection": {"host": "192.168.1.100", "port": 502},
    "config": {"circuits": ["A", "B"]}
})

await heatpump_manager.remove_heatpump(hp_id)
await heatpump_manager.update_heatpump(hp_id, {"name": "New Name"})
await heatpump_manager.enable_heatpump(hp_id, enabled=True)

# Status
status = heatpump_manager.get_status()
info = heatpump_manager.get_heatpump_info(hp_id)
```

---

### 5. Migration System

**File:** `idm_logger/migrations.py`

**Features:**
- Automatically migrates single-device config to multi-device
- Creates "hp-legacy" heatpump from existing `config.idm` settings
- Associates existing jobs/alerts with legacy heatpump
- Creates default dashboard for migrated heatpump

**Usage:**
```python
from idm_logger.migrations import run_migration, get_default_heatpump_id

# Run at startup (idempotent)
run_migration()

# Get default heatpump for legacy API calls
default_id = get_default_heatpump_id()
```

---

### 6. Metrics Writer Extensions

**File:** `idm_logger/metrics.py`

**New Format:**
```
idm_heatpump_temp_outside{heatpump_id="hp-001",manufacturer="idm",model="navigator_2_0",name="Main Building"} 5.2
idm_heatpump_power_current{heatpump_id="hp-001",manufacturer="idm",model="navigator_2_0",name="Main Building"} 3.5
```

**New Methods:**
```python
# Write with labels
metrics.write_heatpump(
    heatpump_id="hp-001",
    manufacturer="idm",
    model="navigator_2_0",
    measurements={"temp_outside": 5.2, "power_current": 3.5},
    heatpump_name="Main Building"
)

# Write all at once
metrics.write_all_heatpumps(all_values, configs)
```

---

## Completed: API Endpoints

### 7. API Endpoints (DONE)

**File:** `idm_logger/web.py`

Implemented endpoints:

```python
# Heatpump management
GET    /api/heatpumps              # List all with status
POST   /api/heatpumps              # Add new heatpump
GET    /api/heatpumps/<id>         # Get details + capabilities
PUT    /api/heatpumps/<id>         # Update config
DELETE /api/heatpumps/<id>         # Remove heatpump
POST   /api/heatpumps/<id>/test    # Test Modbus connection
POST   /api/heatpumps/<id>/enable  # Enable/disable

# Manufacturers
GET    /api/manufacturers                          # List supported
GET    /api/manufacturers/<m>/models/<m>/setup     # Setup instructions

# Multi-device data
GET    /api/data/all       # Read all heatpumps
GET    /api/data/<id>      # Read specific heatpump
POST   /api/control/<id>   # Write to specific heatpump

# Dashboards
GET    /api/dashboards/heatpump/<id>  # Get dashboards for device
```

**Usage Example:**
```bash
# List all heatpumps
curl http://localhost:5000/api/heatpumps

# Add a new heatpump
curl -X POST http://localhost:5000/api/heatpumps \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Building A",
    "manufacturer": "idm",
    "model": "navigator_2_0",
    "connection": {"host": "192.168.1.100", "port": 502},
    "config": {"circuits": ["A", "B"]}
  }'

# Read data from specific heatpump
curl http://localhost:5000/api/data/hp-001

# Write a value
curl -X POST http://localhost:5000/api/control/hp-001 \
  -H "Content-Type: application/json" \
  -d '{"sensor": "temp_water_target", "value": 50}'
```

---

## Pending Components

### 8. Frontend Changes (TODO)

- Heatpump selector component
- Setup wizard for new heatpumps
- Per-device dashboard views
- Comparison views

### 9. Logger Integration (TODO)

Update `logger.py` main loop to:
- Use `HeatpumpManager` instead of `ModbusClient`
- Call `heatpump_manager.read_all()`
- Use `metrics.write_all_heatpumps()`
- Run migration at startup

### 10. Additional Drivers (TODO)

- NIBE S-Series (`manufacturers/nibe/s_series.py`)
- Daikin Altherma (`manufacturers/daikin/altherma.py`)
- Luxtronik 2.1 (`manufacturers/luxtronik/luxtronik_2_1.py`)

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
│   │   └── __init__.py          # Placeholder (done)
│   ├── daikin/
│   │   └── __init__.py          # Placeholder (done)
│   └── luxtronik/
│       └── __init__.py          # Placeholder (done)
├── heatpump_manager.py          # Manager class (done)
├── migrations.py                # Migration logic (done)
├── db.py                        # Extended (done)
├── metrics.py                   # Extended (done)
├── web.py                       # API endpoints (done)
└── logger.py                    # TODO: Integration
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

# Test migration
from idm_logger.migrations import needs_migration, run_migration
if needs_migration():
    run_migration()
```

---

## Next Steps

1. **Integrate with main loop** (`logger.py`)
   - Replace direct ModbusClient usage with HeatpumpManager
   - Run migration at startup
   - Use new metrics format

2. **Add API endpoints** (`web.py`)
   - Heatpump CRUD endpoints
   - Update existing endpoints for multi-device

3. **Frontend updates**
   - Heatpump selector
   - Setup wizard
   - Multi-dashboard support

4. **Additional drivers**
   - NIBE S-Series
   - Others based on demand

---

## Backwards Compatibility

The system maintains backwards compatibility:

1. **Legacy Config**: `config.idm.host` is migrated to `heatpumps` table
2. **Legacy Metrics**: Old format still works (no labels)
3. **Legacy API**: Endpoints work with default heatpump if no ID specified
4. **Legacy Dashboard**: Settings-based dashboards still loaded

Migration is automatic and idempotent.
