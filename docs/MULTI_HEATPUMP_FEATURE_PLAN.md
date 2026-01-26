# Multi-Heatpump Support - Feature Plan

> **Ziel**: Unterstützung für mehrere Wärmepumpen verschiedener Hersteller in einem einzigen System

## Übersicht

Dieses Feature ermöglicht:
- Verwaltung von 2, 3, 4 oder mehr Wärmepumpen
- Dynamische Dashboards pro Gerät
- Herstellerübergreifende Unterstützung (IDM, NIBE, Daikin, Bosch/Luxtronik)
- Individuelle KI-Überwachung pro Gerät
- Zentralisierte Telemetrie-Datenerfassung

---

## Phase 1: Architektur-Grundlagen

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

## Phase 2: Hersteller-Abstraktionsschicht

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

```python
# manufacturers/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class SensorCategory(Enum):
    TEMPERATURE = "temperature"
    POWER = "power"
    ENERGY = "energy"
    STATUS = "status"
    PRESSURE = "pressure"
    FLOW = "flow"
    BINARY = "binary"

@dataclass
class SensorDefinition:
    """Universelle Sensor-Definition"""
    id: str                      # Eindeutige ID (z.B. "temp_outside")
    name: str                    # Anzeigename
    name_de: str                 # Deutscher Name
    category: SensorCategory
    unit: Optional[str]          # °C, kW, kWh, etc.
    address: int                 # Modbus-Adresse
    datatype: str                # FLOAT, WORD, BOOL, etc.
    access: str                  # RO, RW
    scale: float = 1.0           # Skalierungsfaktor
    offset: float = 0.0          # Offset
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum_values: Optional[Dict[int, str]] = None

@dataclass
class HeatpumpCapabilities:
    """Was kann diese Wärmepumpe?"""
    heating: bool = True
    cooling: bool = False
    hot_water: bool = True
    solar_integration: bool = False
    smart_grid: bool = False
    max_circuits: int = 1
    max_zones: int = 1
    writable_sensors: List[str] = None

class HeatpumpDriver(ABC):
    """Abstrakte Basisklasse für alle Wärmepumpen-Treiber"""

    MANUFACTURER: str = ""
    MODEL: str = ""
    DISPLAY_NAME: str = ""

    @abstractmethod
    def get_sensors(self, config: Dict) -> List[SensorDefinition]:
        """Gibt alle verfügbaren Sensoren zurück"""
        pass

    @abstractmethod
    def get_capabilities(self) -> HeatpumpCapabilities:
        """Gibt die Fähigkeiten des Geräts zurück"""
        pass

    @abstractmethod
    def parse_value(self, sensor: SensorDefinition, raw_bytes: bytes) -> Any:
        """Konvertiert Roh-Bytes in einen Wert"""
        pass

    @abstractmethod
    def encode_value(self, sensor: SensorDefinition, value: Any) -> bytes:
        """Konvertiert einen Wert in Roh-Bytes für Schreiboperationen"""
        pass

    def get_read_groups(self, sensors: List[SensorDefinition]) -> List[tuple]:
        """Optimiert Sensoren in zusammenhängende Lesegruppen"""
        # Standard-Implementierung, kann überschrieben werden
        pass

    def get_dashboard_template(self) -> Dict:
        """Gibt ein Standard-Dashboard-Template für dieses Modell zurück"""
        pass
```

### 2.3 IDM Navigator 2.0 Driver

```python
# manufacturers/idm/navigator_2_0.py

from ..base import HeatpumpDriver, SensorDefinition, HeatpumpCapabilities, SensorCategory
import yaml
import struct
from pathlib import Path

class IDMNavigator20Driver(HeatpumpDriver):
    MANUFACTURER = "idm"
    MODEL = "navigator_2_0"
    DISPLAY_NAME = "iDM Navigator 2.0"

    def __init__(self):
        self._load_registers()

    def _load_registers(self):
        """Lädt Register aus YAML-Datei"""
        yaml_path = Path(__file__).parent / "registers.yaml"
        with open(yaml_path) as f:
            self._registers = yaml.safe_load(f)

    def get_sensors(self, config: Dict) -> List[SensorDefinition]:
        sensors = []
        circuits = config.get("circuits", ["A"])
        zones = config.get("zones", [])

        # Basis-Sensoren
        for reg in self._registers["registers"]:
            if self._is_common_sensor(reg):
                sensors.append(self._reg_to_sensor(reg))

        # Heizkreis-spezifische Sensoren
        for circuit in circuits:
            circuit_sensors = self._get_circuit_sensors(circuit)
            sensors.extend(circuit_sensors)

        # Zonen-spezifische Sensoren
        for zone in zones:
            zone_sensors = self._get_zone_sensors(zone)
            sensors.extend(zone_sensors)

        return sensors

    def get_capabilities(self) -> HeatpumpCapabilities:
        return HeatpumpCapabilities(
            heating=True,
            cooling=True,
            hot_water=True,
            solar_integration=True,
            smart_grid=True,
            max_circuits=7,  # A-G
            max_zones=12,
            writable_sensors=[
                "system_mode", "hot_water_target", "circuit_target_temp",
                "zone_target_temp", "zone_mode"
            ]
        )

    def parse_value(self, sensor: SensorDefinition, raw_bytes: bytes) -> Any:
        if sensor.datatype == "FLOAT":
            # IDM: Little-endian word order, big-endian byte order
            low_word = struct.unpack(">H", raw_bytes[0:2])[0]
            high_word = struct.unpack(">H", raw_bytes[2:4])[0]
            combined = struct.pack("<HH", low_word, high_word)
            value = struct.unpack("<f", combined)[0]
        elif sensor.datatype == "WORD":
            value = struct.unpack(">H", raw_bytes)[0]
        elif sensor.datatype == "UCHAR":
            value = raw_bytes[1]  # High byte is padding
        elif sensor.datatype == "BOOL":
            value = bool(struct.unpack(">H", raw_bytes)[0])
        else:
            value = struct.unpack(">H", raw_bytes)[0]

        return value * sensor.scale + sensor.offset

    def get_dashboard_template(self) -> Dict:
        return {
            "name": "IDM Wärmepumpe",
            "charts": [
                {
                    "title": "Temperaturen",
                    "type": "line",
                    "queries": [
                        {"label": "Außentemperatur", "metric": "temp_outside"},
                        {"label": "Vorlauf", "metric": "temp_flow"},
                        {"label": "Rücklauf", "metric": "temp_return"}
                    ]
                },
                {
                    "title": "Leistung",
                    "type": "line",
                    "queries": [
                        {"label": "Aktuelle Leistung", "metric": "power_current"},
                        {"label": "Stromaufnahme", "metric": "power_current_draw"}
                    ]
                },
                {
                    "title": "Warmwasser",
                    "type": "gauge",
                    "queries": [
                        {"label": "Temperatur", "metric": "temp_hot_water_top"}
                    ],
                    "min": 0, "max": 70
                }
            ]
        }
```

### 2.4 NIBE S-Series Driver

```python
# manufacturers/nibe/s_series.py

from ..base import HeatpumpDriver, SensorDefinition, HeatpumpCapabilities, SensorCategory
import struct

class NIBESSeriesDriver(HeatpumpDriver):
    MANUFACTURER = "nibe"
    MODEL = "s_series"
    DISPLAY_NAME = "NIBE S-Series (S1155, S1255, S2125)"

    # NIBE verwendet andere Register-Adressen als IDM
    REGISTER_MAP = {
        "temp_outside": {"address": 40004, "datatype": "INT16", "scale": 0.1},
        "temp_hot_water_top": {"address": 40013, "datatype": "INT16", "scale": 0.1},
        "temp_hot_water_charging": {"address": 40014, "datatype": "INT16", "scale": 0.1},
        "temp_brine_in": {"address": 40015, "datatype": "INT16", "scale": 0.1},
        "temp_brine_out": {"address": 40016, "datatype": "INT16", "scale": 0.1},
        "temp_condenser": {"address": 40017, "datatype": "INT16", "scale": 0.1},
        "temp_discharge": {"address": 40018, "datatype": "INT16", "scale": 0.1},
        "temp_suction": {"address": 40019, "datatype": "INT16", "scale": 0.1},
        "temp_supply_line": {"address": 40008, "datatype": "INT16", "scale": 0.1},
        "temp_return_line": {"address": 40012, "datatype": "INT16", "scale": 0.1},
        "compressor_frequency": {"address": 43136, "datatype": "UINT16", "scale": 0.1},
        "compressor_starts": {"address": 43416, "datatype": "UINT32", "scale": 1},
        "compressor_hours": {"address": 43420, "datatype": "UINT32", "scale": 1},
        "current_power": {"address": 43084, "datatype": "UINT16", "scale": 0.01},
        "heating_curve": {"address": 47007, "datatype": "INT16", "scale": 1},
        "hot_water_start_temp": {"address": 47041, "datatype": "INT16", "scale": 0.1},
        "hot_water_stop_temp": {"address": 47043, "datatype": "INT16", "scale": 0.1},
        "operating_mode": {"address": 47137, "datatype": "UINT8", "scale": 1},
    }

    def get_sensors(self, config: Dict) -> List[SensorDefinition]:
        sensors = []
        for sensor_id, reg_info in self.REGISTER_MAP.items():
            sensors.append(SensorDefinition(
                id=sensor_id,
                name=sensor_id.replace("_", " ").title(),
                name_de=self._translate(sensor_id),
                category=self._categorize(sensor_id),
                unit=self._get_unit(sensor_id),
                address=reg_info["address"],
                datatype=reg_info["datatype"],
                access="RO" if reg_info["address"] < 45000 else "RW",
                scale=reg_info["scale"]
            ))
        return sensors

    def get_capabilities(self) -> HeatpumpCapabilities:
        return HeatpumpCapabilities(
            heating=True,
            cooling=True,  # Model-abhängig
            hot_water=True,
            solar_integration=False,
            smart_grid=True,
            max_circuits=4,
            max_zones=4
        )

    def parse_value(self, sensor: SensorDefinition, raw_bytes: bytes) -> Any:
        # NIBE verwendet Big-Endian
        if sensor.datatype == "INT16":
            value = struct.unpack(">h", raw_bytes)[0]
        elif sensor.datatype == "UINT16":
            value = struct.unpack(">H", raw_bytes)[0]
        elif sensor.datatype == "UINT32":
            value = struct.unpack(">I", raw_bytes)[0]
        elif sensor.datatype == "UINT8":
            value = raw_bytes[1]
        else:
            value = struct.unpack(">H", raw_bytes)[0]

        return value * sensor.scale
```

### 2.5 Luxtronik 2.1 Driver (Bosch, Alpha Innotec, etc.)

```python
# manufacturers/luxtronik/luxtronik_2_1.py

from ..base import HeatpumpDriver, SensorDefinition, HeatpumpCapabilities

class Luxtronik21Driver(HeatpumpDriver):
    """
    Luxtronik 2.1 Controller - verwendet von:
    - Bosch
    - Alpha Innotec
    - Novelan
    - Siemens Novelan
    """
    MANUFACTURER = "luxtronik"
    MODEL = "luxtronik_2_1"
    DISPLAY_NAME = "Luxtronik 2.1 (Bosch, Alpha Innotec)"

    # Luxtronik verwendet ein spezielles Protokoll über Port 8889
    # NICHT Standard-Modbus, aber TCP-basiert
    PROTOCOL_PORT = 8889

    # Parameter-IDs statt Register-Adressen
    PARAMETERS = {
        "temp_outside": {"id": 10, "type": "temperature"},
        "temp_outside_avg": {"id": 11, "type": "temperature"},
        "temp_hot_water": {"id": 17, "type": "temperature"},
        "temp_hot_water_target": {"id": 18, "type": "temperature"},
        "temp_flow": {"id": 10, "type": "temperature"},
        "temp_return": {"id": 11, "type": "temperature"},
        "temp_source_in": {"id": 19, "type": "temperature"},
        "temp_source_out": {"id": 20, "type": "temperature"},
        "compressor_output": {"id": 257, "type": "percent"},
        "operating_hours_heating": {"id": 63, "type": "hours"},
        "operating_hours_hot_water": {"id": 64, "type": "hours"},
        "operating_hours_cooling": {"id": 65, "type": "hours"},
        "heat_quantity_heating": {"id": 151, "type": "energy"},
        "heat_quantity_hot_water": {"id": 152, "type": "energy"},
    }

    def get_capabilities(self) -> HeatpumpCapabilities:
        return HeatpumpCapabilities(
            heating=True,
            cooling=True,
            hot_water=True,
            solar_integration=True,
            smart_grid=False,
            max_circuits=3,
            max_zones=3
        )

    # Luxtronik benötigt einen eigenen Client statt Modbus
    def requires_custom_client(self) -> bool:
        return True

    def get_client_class(self):
        from .luxtronik_client import LuxtronikClient
        return LuxtronikClient
```

### 2.6 Daikin Altherma Driver

```python
# manufacturers/daikin/altherma.py

from ..base import HeatpumpDriver, SensorDefinition, HeatpumpCapabilities

class DaikinAlthermaDriver(HeatpumpDriver):
    """
    Daikin Altherma - benötigt HomeHub (EKRHH) in Mode 3
    Modbus TCP über Port 502
    """
    MANUFACTURER = "daikin"
    MODEL = "altherma"
    DISPLAY_NAME = "Daikin Altherma (via HomeHub)"

    # Daikin Modbus Register (basierend auf EKMBDXB7V1 Spezifikation)
    REGISTER_MAP = {
        "temp_outside": {"address": 3, "datatype": "INT16", "scale": 0.1},
        "temp_leaving_water": {"address": 4, "datatype": "INT16", "scale": 0.1},
        "temp_return_water": {"address": 5, "datatype": "INT16", "scale": 0.1},
        "temp_hot_water": {"address": 6, "datatype": "INT16", "scale": 0.1},
        "temp_refrigerant": {"address": 7, "datatype": "INT16", "scale": 0.1},
        "operation_mode": {"address": 0, "datatype": "UINT16", "scale": 1},
        "target_temp_heating": {"address": 30, "datatype": "INT16", "scale": 0.1, "access": "RW"},
        "target_temp_hot_water": {"address": 31, "datatype": "INT16", "scale": 0.1, "access": "RW"},
        "compressor_status": {"address": 20, "datatype": "UINT16", "scale": 1},
        "defrost_status": {"address": 21, "datatype": "UINT16", "scale": 1},
        "error_code": {"address": 50, "datatype": "UINT16", "scale": 1},
    }

    def get_capabilities(self) -> HeatpumpCapabilities:
        return HeatpumpCapabilities(
            heating=True,
            cooling=True,
            hot_water=True,
            solar_integration=False,
            smart_grid=True,
            max_circuits=2,
            max_zones=2
        )

    # Hinweis für Benutzer
    @staticmethod
    def get_setup_instructions() -> str:
        return """
        Daikin Altherma Setup:
        1. HomeHub (EKRHH) erforderlich
        2. HomeHub in Mode 3 (Modbus TCP/IP) konfigurieren
        3. IP-Adresse des HomeHub im Netzwerk ermitteln
        4. Standard-Port: 502
        """
```

### 2.7 Hersteller-Registry

```python
# manufacturers/__init__.py

from typing import Dict, Type, Optional
from .base import HeatpumpDriver

class ManufacturerRegistry:
    """Zentrale Registry für alle unterstützten Wärmepumpen-Treiber"""

    _drivers: Dict[str, Dict[str, Type[HeatpumpDriver]]] = {}

    @classmethod
    def register(cls, driver_class: Type[HeatpumpDriver]):
        """Registriert einen Treiber"""
        mfr = driver_class.MANUFACTURER
        model = driver_class.MODEL

        if mfr not in cls._drivers:
            cls._drivers[mfr] = {}

        cls._drivers[mfr][model] = driver_class
        return driver_class

    @classmethod
    def get_driver(cls, manufacturer: str, model: str) -> Optional[HeatpumpDriver]:
        """Gibt eine Treiber-Instanz zurück"""
        if manufacturer in cls._drivers and model in cls._drivers[manufacturer]:
            return cls._drivers[manufacturer][model]()
        return None

    @classmethod
    def list_manufacturers(cls) -> list:
        """Liste aller unterstützten Hersteller"""
        return [
            {
                "id": mfr,
                "name": cls._get_manufacturer_display_name(mfr),
                "models": [
                    {"id": model, "name": driver.DISPLAY_NAME}
                    for model, driver in models.items()
                ]
            }
            for mfr, models in cls._drivers.items()
        ]

    @classmethod
    def _get_manufacturer_display_name(cls, mfr: str) -> str:
        names = {
            "idm": "iDM Energiesysteme",
            "nibe": "NIBE",
            "daikin": "Daikin",
            "luxtronik": "Luxtronik (Bosch, Alpha Innotec)",
            "viessmann": "Viessmann",
            "vaillant": "Vaillant",
            "stiebel_eltron": "Stiebel Eltron"
        }
        return names.get(mfr, mfr.title())

# Auto-Discovery der Treiber
def _discover_drivers():
    from .idm.navigator_2_0 import IDMNavigator20Driver
    from .nibe.s_series import NIBESSeriesDriver
    from .daikin.altherma import DaikinAlthermaDriver
    from .luxtronik.luxtronik_2_1 import Luxtronik21Driver

    ManufacturerRegistry.register(IDMNavigator20Driver)
    ManufacturerRegistry.register(NIBESSeriesDriver)
    ManufacturerRegistry.register(DaikinAlthermaDriver)
    ManufacturerRegistry.register(Luxtronik21Driver)

_discover_drivers()
```

---

## Phase 3: Backend-Implementierung

### 3.1 Multi-Modbus-Manager

```python
# idm_logger/heatpump_manager.py

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from .manufacturers import ManufacturerRegistry
from .modbus import ModbusClient

logger = logging.getLogger(__name__)

@dataclass
class HeatpumpConnection:
    """Repräsentiert eine aktive Wärmepumpen-Verbindung"""
    id: str
    name: str
    driver: 'HeatpumpDriver'
    client: ModbusClient
    sensors: List['SensorDefinition']
    enabled: bool
    last_read: float = 0
    error_count: int = 0

class HeatpumpManager:
    """Verwaltet mehrere Wärmepumpen-Verbindungen"""

    def __init__(self, config: 'ConfigManager', db: 'Database'):
        self.config = config
        self.db = db
        self._connections: Dict[str, HeatpumpConnection] = {}
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialisiert alle konfigurierten Wärmepumpen"""
        heatpumps = self.db.get_all_heatpumps()

        for hp in heatpumps:
            if hp["enabled"]:
                await self._connect_heatpump(hp)

    async def _connect_heatpump(self, hp_config: dict):
        """Erstellt eine neue Verbindung zu einer Wärmepumpe"""
        hp_id = hp_config["id"]

        try:
            # Treiber laden
            driver = ManufacturerRegistry.get_driver(
                hp_config["manufacturer"],
                hp_config["model"]
            )

            if not driver:
                logger.error(f"Kein Treiber für {hp_config['manufacturer']}/{hp_config['model']}")
                return

            # Sensoren abrufen
            sensors = driver.get_sensors(hp_config.get("device_config", {}))

            # Modbus-Client erstellen
            conn = hp_config["connection_config"]
            client = ModbusClient(
                host=conn["host"],
                port=conn.get("port", 502),
                unit_id=conn.get("unit_id", 1),
                timeout=conn.get("timeout", 10)
            )

            # Verbindung speichern
            self._connections[hp_id] = HeatpumpConnection(
                id=hp_id,
                name=hp_config["name"],
                driver=driver,
                client=client,
                sensors=sensors,
                enabled=True
            )

            logger.info(f"Wärmepumpe '{hp_config['name']}' verbunden ({len(sensors)} Sensoren)")

        except Exception as e:
            logger.error(f"Fehler beim Verbinden von {hp_id}: {e}")

    async def read_all(self) -> Dict[str, Dict[str, any]]:
        """Liest Werte von allen Wärmepumpen"""
        results = {}

        # Paralleles Lesen von allen Geräten
        tasks = [
            self._read_heatpump(hp_id)
            for hp_id, conn in self._connections.items()
            if conn.enabled
        ]

        readings = await asyncio.gather(*tasks, return_exceptions=True)

        for hp_id, values in zip(self._connections.keys(), readings):
            if isinstance(values, Exception):
                logger.error(f"Lesefehler bei {hp_id}: {values}")
                self._connections[hp_id].error_count += 1
            else:
                results[hp_id] = values
                self._connections[hp_id].error_count = 0

        return results

    async def _read_heatpump(self, hp_id: str) -> Dict[str, any]:
        """Liest alle Werte einer einzelnen Wärmepumpe"""
        conn = self._connections[hp_id]
        values = {}

        # Bulk-Read mit Optimierung
        read_groups = conn.driver.get_read_groups(conn.sensors)

        for start_addr, count, sensors_in_group in read_groups:
            raw_data = await conn.client.read_registers(start_addr, count)

            for sensor in sensors_in_group:
                offset = sensor.address - start_addr
                raw_bytes = raw_data[offset:offset + self._get_register_count(sensor)]
                values[sensor.id] = conn.driver.parse_value(sensor, raw_bytes)

        return values

    async def write_value(self, hp_id: str, sensor_id: str, value: any):
        """Schreibt einen Wert zu einer Wärmepumpe"""
        if hp_id not in self._connections:
            raise ValueError(f"Unbekannte Wärmepumpe: {hp_id}")

        conn = self._connections[hp_id]
        sensor = next((s for s in conn.sensors if s.id == sensor_id), None)

        if not sensor:
            raise ValueError(f"Unbekannter Sensor: {sensor_id}")

        if sensor.access != "RW":
            raise ValueError(f"Sensor {sensor_id} ist nicht beschreibbar")

        encoded = conn.driver.encode_value(sensor, value)
        await conn.client.write_registers(sensor.address, encoded)

        logger.info(f"Wert geschrieben: {hp_id}/{sensor_id} = {value}")

    # CRUD-Operationen für Wärmepumpen
    async def add_heatpump(self, config: dict) -> str:
        """Fügt eine neue Wärmepumpe hinzu"""
        import uuid
        hp_id = f"hp-{uuid.uuid4().hex[:8]}"

        hp_config = {
            "id": hp_id,
            "name": config["name"],
            "manufacturer": config["manufacturer"],
            "model": config["model"],
            "connection_config": config["connection"],
            "device_config": config.get("config", {}),
            "enabled": True
        }

        # In DB speichern
        self.db.save_heatpump(hp_config)

        # Verbindung herstellen
        await self._connect_heatpump(hp_config)

        # Standard-Dashboard erstellen
        await self._create_default_dashboard(hp_id, config["manufacturer"], config["model"])

        return hp_id

    async def remove_heatpump(self, hp_id: str):
        """Entfernt eine Wärmepumpe"""
        if hp_id in self._connections:
            # Verbindung schließen
            conn = self._connections[hp_id]
            await conn.client.close()
            del self._connections[hp_id]

        # Aus DB löschen
        self.db.delete_heatpump(hp_id)

        # Dashboard löschen
        self.db.delete_dashboards_for_heatpump(hp_id)

        # Alerts und Jobs anpassen
        self.db.delete_alerts_for_heatpump(hp_id)
        self.db.delete_jobs_for_heatpump(hp_id)

        logger.info(f"Wärmepumpe {hp_id} entfernt")

    async def _create_default_dashboard(self, hp_id: str, manufacturer: str, model: str):
        """Erstellt ein Standard-Dashboard für eine neue Wärmepumpe"""
        driver = ManufacturerRegistry.get_driver(manufacturer, model)
        if driver:
            template = driver.get_dashboard_template()
            template["heatpump_id"] = hp_id
            self.db.save_dashboard(template)

    def get_status(self) -> List[dict]:
        """Gibt den Status aller Verbindungen zurück"""
        return [
            {
                "id": conn.id,
                "name": conn.name,
                "connected": conn.client.is_connected,
                "sensor_count": len(conn.sensors),
                "error_count": conn.error_count,
                "enabled": conn.enabled
            }
            for conn in self._connections.values()
        ]
```

### 3.2 Erweiterte API-Endpunkte

```python
# Neue Endpunkte in web.py

# ===== Wärmepumpen-Management =====

@app.route("/api/heatpumps", methods=["GET"])
@require_auth
def list_heatpumps():
    """Liste aller konfigurierten Wärmepumpen"""
    heatpumps = db.get_all_heatpumps()
    status = heatpump_manager.get_status()

    # Status mit Config zusammenführen
    for hp in heatpumps:
        hp_status = next((s for s in status if s["id"] == hp["id"]), {})
        hp.update(hp_status)

    return jsonify(heatpumps)

@app.route("/api/heatpumps", methods=["POST"])
@require_auth
def add_heatpump():
    """Neue Wärmepumpe hinzufügen"""
    data = request.json

    # Validierung
    required = ["name", "manufacturer", "model", "connection"]
    if not all(k in data for k in required):
        return jsonify({"error": "Fehlende Pflichtfelder"}), 400

    # Verbindung testen
    test_result = test_connection(
        data["connection"]["host"],
        data["connection"].get("port", 502),
        data["manufacturer"],
        data["model"]
    )

    if not test_result["success"]:
        return jsonify({"error": f"Verbindungstest fehlgeschlagen: {test_result['message']}"}), 400

    # Wärmepumpe hinzufügen
    hp_id = asyncio.run(heatpump_manager.add_heatpump(data))

    return jsonify({"id": hp_id, "message": "Wärmepumpe hinzugefügt"}), 201

@app.route("/api/heatpumps/<hp_id>", methods=["GET"])
@require_auth
def get_heatpump(hp_id):
    """Details einer Wärmepumpe"""
    hp = db.get_heatpump(hp_id)
    if not hp:
        return jsonify({"error": "Nicht gefunden"}), 404

    # Capabilities hinzufügen
    driver = ManufacturerRegistry.get_driver(hp["manufacturer"], hp["model"])
    if driver:
        hp["capabilities"] = driver.get_capabilities().__dict__

    return jsonify(hp)

@app.route("/api/heatpumps/<hp_id>", methods=["PUT"])
@require_auth
def update_heatpump(hp_id):
    """Wärmepumpe aktualisieren"""
    data = request.json
    db.update_heatpump(hp_id, data)

    # Verbindung neu aufbauen wenn nötig
    if "connection" in data:
        asyncio.run(heatpump_manager.reconnect(hp_id))

    return jsonify({"message": "Aktualisiert"})

@app.route("/api/heatpumps/<hp_id>", methods=["DELETE"])
@require_auth
def delete_heatpump(hp_id):
    """Wärmepumpe entfernen"""
    asyncio.run(heatpump_manager.remove_heatpump(hp_id))
    return jsonify({"message": "Wärmepumpe und zugehöriges Dashboard entfernt"})

@app.route("/api/heatpumps/<hp_id>/test", methods=["POST"])
@require_auth
def test_heatpump_connection(hp_id):
    """Verbindung testen"""
    hp = db.get_heatpump(hp_id)
    result = test_connection(
        hp["connection_config"]["host"],
        hp["connection_config"].get("port", 502),
        hp["manufacturer"],
        hp["model"]
    )
    return jsonify(result)

# ===== Hersteller & Modelle =====

@app.route("/api/manufacturers", methods=["GET"])
def list_manufacturers():
    """Liste aller unterstützten Hersteller und Modelle"""
    return jsonify(ManufacturerRegistry.list_manufacturers())

@app.route("/api/manufacturers/<mfr>/models/<model>/setup", methods=["GET"])
def get_setup_instructions(mfr, model):
    """Setup-Anleitung für ein spezifisches Modell"""
    driver = ManufacturerRegistry.get_driver(mfr, model)
    if not driver:
        return jsonify({"error": "Nicht gefunden"}), 404

    return jsonify({
        "manufacturer": mfr,
        "model": model,
        "display_name": driver.DISPLAY_NAME,
        "capabilities": driver.get_capabilities().__dict__,
        "instructions": getattr(driver, 'get_setup_instructions', lambda: None)()
    })

# ===== Daten-Endpunkte mit Multi-Device Support =====

@app.route("/api/data", methods=["GET"])
def get_current_data():
    """Aktuelle Werte aller oder spezifischer Wärmepumpen"""
    hp_ids = request.args.getlist("heatpump_id") or None

    all_data = asyncio.run(heatpump_manager.read_all())

    if hp_ids:
        all_data = {k: v for k, v in all_data.items() if k in hp_ids}

    return jsonify(all_data)

@app.route("/api/data/<hp_id>", methods=["GET"])
def get_heatpump_data(hp_id):
    """Aktuelle Werte einer spezifischen Wärmepumpe"""
    data = asyncio.run(heatpump_manager.read_all())

    if hp_id not in data:
        return jsonify({"error": "Nicht gefunden"}), 404

    return jsonify(data[hp_id])

@app.route("/api/control/<hp_id>", methods=["POST"])
@require_auth
def control_heatpump(hp_id):
    """Wert zu einer Wärmepumpe schreiben"""
    data = request.json
    sensor_id = data.get("sensor")
    value = data.get("value")

    try:
        asyncio.run(heatpump_manager.write_value(hp_id, sensor_id, value))
        return jsonify({"message": "Wert geschrieben"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
```

### 3.3 Erweiterte Metriken

```python
# idm_logger/metrics.py - Erweiterungen

class MetricsWriter:
    async def write_heatpump_values(self, hp_id: str, hp_config: dict, values: dict):
        """Schreibt Werte einer Wärmepumpe mit Labels"""
        labels = {
            "heatpump_id": hp_id,
            "manufacturer": hp_config["manufacturer"],
            "model": hp_config["model"],
            "name": hp_config["name"]
        }

        for sensor_id, value in values.items():
            if value is not None:
                metric_name = f"idm_heatpump_{sensor_id}"
                await self._queue_metric(metric_name, value, labels)

    async def write_all_heatpumps(self, all_values: dict, configs: dict):
        """Schreibt Werte aller Wärmepumpen"""
        for hp_id, values in all_values.items():
            if hp_id in configs:
                await self.write_heatpump_values(hp_id, configs[hp_id], values)
```

---

## Phase 4: Frontend-Implementierung

### 4.1 Vue-Komponenten

```
frontend/src/
├── components/
│   ├── heatpump/
│   │   ├── HeatpumpCard.vue        # Übersichtskarte pro Gerät
│   │   ├── HeatpumpSelector.vue    # Dropdown zur Geräteauswahl
│   │   ├── HeatpumpSetup.vue       # Wizard für neue Geräte
│   │   ├── HeatpumpStatus.vue      # Verbindungsstatus
│   │   └── HeatpumpCompare.vue     # Vergleichsansicht
│   └── ...
├── stores/
│   ├── heatpumps.ts               # Pinia Store für Wärmepumpen
│   └── ...
└── views/
    ├── Heatpumps.vue              # Übersicht aller Geräte
    └── ...
```

### 4.2 Pinia Store

```typescript
// stores/heatpumps.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

interface Heatpump {
  id: string
  name: string
  manufacturer: string
  model: string
  connection_config: {
    host: string
    port: number
    unit_id: number
  }
  device_config: Record<string, any>
  enabled: boolean
  connected?: boolean
  error_count?: number
}

interface Manufacturer {
  id: string
  name: string
  models: { id: string; name: string }[]
}

export const useHeatpumpsStore = defineStore('heatpumps', () => {
  const heatpumps = ref<Heatpump[]>([])
  const manufacturers = ref<Manufacturer[]>([])
  const activeHeatpumpId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const activeHeatpump = computed(() =>
    heatpumps.value.find(hp => hp.id === activeHeatpumpId.value)
  )

  const connectedHeatpumps = computed(() =>
    heatpumps.value.filter(hp => hp.connected && hp.enabled)
  )

  // Actions
  async function fetchHeatpumps() {
    loading.value = true
    try {
      const response = await api.get('/api/heatpumps')
      heatpumps.value = response.data

      // Setze erste Wärmepumpe als aktiv wenn keine ausgewählt
      if (!activeHeatpumpId.value && heatpumps.value.length > 0) {
        activeHeatpumpId.value = heatpumps.value[0].id
      }
    } catch (e) {
      error.value = 'Fehler beim Laden der Wärmepumpen'
    } finally {
      loading.value = false
    }
  }

  async function fetchManufacturers() {
    const response = await api.get('/api/manufacturers')
    manufacturers.value = response.data
  }

  async function addHeatpump(config: Partial<Heatpump>) {
    const response = await api.post('/api/heatpumps', config)
    await fetchHeatpumps()
    return response.data.id
  }

  async function removeHeatpump(id: string) {
    await api.delete(`/api/heatpumps/${id}`)
    await fetchHeatpumps()

    if (activeHeatpumpId.value === id) {
      activeHeatpumpId.value = heatpumps.value[0]?.id || null
    }
  }

  async function testConnection(id: string) {
    const response = await api.post(`/api/heatpumps/${id}/test`)
    return response.data
  }

  function setActiveHeatpump(id: string) {
    activeHeatpumpId.value = id
  }

  return {
    heatpumps,
    manufacturers,
    activeHeatpumpId,
    activeHeatpump,
    connectedHeatpumps,
    loading,
    error,
    fetchHeatpumps,
    fetchManufacturers,
    addHeatpump,
    removeHeatpump,
    testConnection,
    setActiveHeatpump
  }
})
```

### 4.3 Setup-Wizard Komponente

```vue
<!-- components/heatpump/HeatpumpSetup.vue -->
<template>
  <div class="heatpump-setup">
    <!-- Step Indicator -->
    <div class="steps">
      <div v-for="(step, i) in steps" :key="i"
           :class="['step', { active: currentStep === i, completed: currentStep > i }]">
        {{ step }}
      </div>
    </div>

    <!-- Step 1: Hersteller & Modell -->
    <div v-if="currentStep === 0" class="step-content">
      <h3>Hersteller auswählen</h3>
      <div class="manufacturer-grid">
        <div v-for="mfr in manufacturers" :key="mfr.id"
             :class="['mfr-card', { selected: form.manufacturer === mfr.id }]"
             @click="selectManufacturer(mfr.id)">
          <img :src="`/logos/${mfr.id}.png`" :alt="mfr.name" />
          <span>{{ mfr.name }}</span>
        </div>
      </div>

      <div v-if="form.manufacturer" class="model-select">
        <h3>Modell auswählen</h3>
        <select v-model="form.model">
          <option v-for="model in selectedManufacturer?.models" :key="model.id" :value="model.id">
            {{ model.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Step 2: Verbindung -->
    <div v-if="currentStep === 1" class="step-content">
      <h3>Verbindungseinstellungen</h3>

      <div v-if="setupInstructions" class="instructions">
        <p>{{ setupInstructions }}</p>
      </div>

      <div class="form-group">
        <label>IP-Adresse / Hostname</label>
        <input v-model="form.connection.host" type="text" placeholder="192.168.1.100" />
      </div>

      <div class="form-group">
        <label>Port</label>
        <input v-model.number="form.connection.port" type="number" />
      </div>

      <div class="form-group">
        <label>Unit ID (Modbus)</label>
        <input v-model.number="form.connection.unit_id" type="number" />
      </div>

      <button @click="testConnection" :disabled="testing">
        {{ testing ? 'Teste...' : 'Verbindung testen' }}
      </button>

      <div v-if="testResult" :class="['test-result', testResult.success ? 'success' : 'error']">
        {{ testResult.message }}
      </div>
    </div>

    <!-- Step 3: Konfiguration -->
    <div v-if="currentStep === 2" class="step-content">
      <h3>Gerätekonfiguration</h3>

      <div class="form-group">
        <label>Name</label>
        <input v-model="form.name" type="text" placeholder="z.B. Wärmepumpe Gebäude A" />
      </div>

      <!-- IDM-spezifisch -->
      <template v-if="form.manufacturer === 'idm'">
        <div class="form-group">
          <label>Heizkreise</label>
          <div class="checkbox-group">
            <label v-for="circuit in ['A', 'B', 'C', 'D', 'E', 'F', 'G']" :key="circuit">
              <input type="checkbox" v-model="form.config.circuits" :value="circuit" />
              {{ circuit }}
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>Zonen</label>
          <div class="checkbox-group">
            <label v-for="zone in 12" :key="zone">
              <input type="checkbox" v-model="form.config.zones" :value="zone" />
              Zone {{ zone }}
            </label>
          </div>
        </div>
      </template>
    </div>

    <!-- Step 4: Zusammenfassung -->
    <div v-if="currentStep === 3" class="step-content">
      <h3>Zusammenfassung</h3>

      <div class="summary">
        <p><strong>Name:</strong> {{ form.name }}</p>
        <p><strong>Hersteller:</strong> {{ selectedManufacturer?.name }}</p>
        <p><strong>Modell:</strong> {{ selectedModel?.name }}</p>
        <p><strong>Adresse:</strong> {{ form.connection.host }}:{{ form.connection.port }}</p>
      </div>

      <div class="info-box">
        <p>Nach dem Hinzufügen wird automatisch ein Dashboard für diese Wärmepumpe erstellt.</p>
      </div>
    </div>

    <!-- Navigation -->
    <div class="step-navigation">
      <button v-if="currentStep > 0" @click="currentStep--">Zurück</button>
      <button v-if="currentStep < 3" @click="currentStep++" :disabled="!canProceed">Weiter</button>
      <button v-if="currentStep === 3" @click="submit" :disabled="submitting">
        {{ submitting ? 'Wird hinzugefügt...' : 'Wärmepumpe hinzufügen' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useHeatpumpsStore } from '@/stores/heatpumps'

const store = useHeatpumpsStore()
const emit = defineEmits(['complete', 'cancel'])

const steps = ['Hersteller', 'Verbindung', 'Konfiguration', 'Fertig']
const currentStep = ref(0)
const testing = ref(false)
const testResult = ref(null)
const submitting = ref(false)

const form = ref({
  name: '',
  manufacturer: '',
  model: '',
  connection: {
    host: '',
    port: 502,
    unit_id: 1
  },
  config: {
    circuits: ['A'],
    zones: []
  }
})

// ... computed properties und methods
</script>
```

### 4.4 Dashboard-Auswahl

```vue
<!-- components/heatpump/HeatpumpSelector.vue -->
<template>
  <div class="heatpump-selector">
    <select v-model="activeId" @change="onChange">
      <option value="__all__">Alle Wärmepumpen</option>
      <option v-for="hp in heatpumps" :key="hp.id" :value="hp.id">
        {{ hp.name }}
        <span v-if="!hp.connected" class="status-offline">(Offline)</span>
      </option>
    </select>

    <button class="add-btn" @click="showAddDialog = true" title="Wärmepumpe hinzufügen">
      +
    </button>

    <!-- Add Dialog -->
    <HeatpumpSetup v-if="showAddDialog" @complete="onAdded" @cancel="showAddDialog = false" />
  </div>
</template>
```

---

## Phase 5: ML-Service Erweiterungen

### 5.1 Multi-Model Training

```python
# ml_service/main.py - Erweiterungen

class MultiHeatpumpAnomalyDetector:
    """Trainiert separate Modelle pro Wärmepumpen-Typ"""

    def __init__(self):
        self.models: Dict[str, HalfSpaceTrees] = {}
        self.model_configs: Dict[str, dict] = {}

    def get_or_create_model(self, hp_id: str, manufacturer: str, model: str):
        """Gibt existierendes Modell zurück oder erstellt ein neues"""
        model_key = f"{manufacturer}_{model}"

        if model_key not in self.models:
            self.models[model_key] = HalfSpaceTrees(
                n_trees=CONFIG["n_trees"],
                height=CONFIG["height"],
                window_size=CONFIG["window_size"]
            )
            self.model_configs[model_key] = {
                "heatpump_ids": set(),
                "training_samples": 0
            }

        self.model_configs[model_key]["heatpump_ids"].add(hp_id)
        return self.models[model_key]

    def train_on_values(self, hp_id: str, manufacturer: str, model_name: str, values: dict):
        """Trainiert das Modell mit neuen Werten"""
        model = self.get_or_create_model(hp_id, manufacturer, model_name)

        # Feature-Vektor erstellen
        features = self._create_feature_vector(values, manufacturer, model_name)

        # Anomalie-Score berechnen
        score = model.score_one(features)

        # Lernen
        model.learn_one(features)

        self.model_configs[f"{manufacturer}_{model_name}"]["training_samples"] += 1

        return score

    def _create_feature_vector(self, values: dict, manufacturer: str, model: str) -> dict:
        """Erstellt einen normalisierten Feature-Vektor"""
        # Basis-Features die alle Wärmepumpen haben
        common_features = [
            "temp_outside", "temp_flow", "temp_return",
            "temp_hot_water", "power_current"
        ]

        features = {}
        for f in common_features:
            if f in values:
                features[f] = values[f]

        return features
```

---

## Phase 6: Telemetrie-Erweiterungen

```python
# idm_logger/telemetry.py - Erweiterungen

class TelemetryManager:
    def prepare_telemetry_data(self, all_values: dict, configs: dict) -> dict:
        """Bereitet Telemetrie-Daten für mehrere Wärmepumpen vor"""
        return {
            "version": "2.0",
            "timestamp": time.time(),
            "installation_id": self.installation_id,
            "heatpumps": [
                {
                    "id": hp_id,
                    "manufacturer": configs[hp_id]["manufacturer"],
                    "model": configs[hp_id]["model"],
                    "values": self._anonymize_values(values)
                }
                for hp_id, values in all_values.items()
                if hp_id in configs and configs[hp_id].get("share_data", True)
            ]
        }
```

---

## Phase 7: Migration & Abwärtskompatibilität

### 7.1 Migrations-Script

```python
# idm_logger/migrations/001_multi_heatpump.py

def migrate(db: Database, config: ConfigManager):
    """Migriert von Single-Heatpump zu Multi-Heatpump"""

    # Prüfen ob bereits migriert
    if db.table_exists("heatpumps"):
        return

    # Neue Tabellen erstellen
    db.execute("""
        CREATE TABLE heatpumps (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            connection_config TEXT NOT NULL,
            device_config TEXT DEFAULT '{}',
            enabled INTEGER DEFAULT 1,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
    """)

    # Bestehende Konfiguration migrieren
    old_config = config.get("idm", {})
    if old_config.get("host"):
        hp_config = {
            "id": "hp-legacy",
            "name": "Wärmepumpe (Migriert)",
            "manufacturer": "idm",
            "model": "navigator_2_0",
            "connection_config": json.dumps({
                "host": old_config["host"],
                "port": old_config.get("port", 502),
                "unit_id": 1
            }),
            "device_config": json.dumps({
                "circuits": old_config.get("circuits", ["A"]),
                "zones": old_config.get("zones", [])
            }),
            "enabled": 1,
            "created_at": time.time(),
            "updated_at": time.time()
        }

        db.execute(
            "INSERT INTO heatpumps VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(hp_config.values())
        )

    # Alerts und Jobs erweitern
    db.execute("ALTER TABLE alerts ADD COLUMN heatpump_id TEXT DEFAULT 'hp-legacy'")
    db.execute("ALTER TABLE jobs ADD COLUMN heatpump_id TEXT DEFAULT 'hp-legacy'")

    print("Migration zu Multi-Heatpump abgeschlossen")
```

---

## Unterstützte Hersteller - Übersicht

| Hersteller | Modelle | Protokoll | Status |
|------------|---------|-----------|--------|
| **iDM** | Navigator 2.0 | Modbus TCP | Bereits implementiert |
| **NIBE** | S-Series (S1155, S1255, S2125), F-Series | Modbus TCP | Geplant |
| **Daikin** | Altherma (via HomeHub EKRHH) | Modbus TCP | Geplant |
| **Bosch** | via Luxtronik 2.1 | Luxtronik TCP (Port 8889) | Geplant |
| **Alpha Innotec** | via Luxtronik 2.1 | Luxtronik TCP | Geplant |
| **Viessmann** | (Cloud-API basiert) | HTTP REST API | Später |
| **Vaillant** | aroTHERM | Modbus TCP | Später |
| **Stiebel Eltron** | WPL-A | Modbus TCP | Später |

---

## Implementierungs-Reihenfolge

### Milestone 1: Basis-Architektur
- [ ] Config-Schema erweitern
- [ ] Datenbank-Tabellen erstellen
- [ ] Migration implementieren
- [ ] HeatpumpManager Basisklasse

### Milestone 2: IDM Multi-Instance
- [ ] IDM-Driver extrahieren
- [ ] Multi-Modbus-Verbindungen
- [ ] Metriken mit Labels
- [ ] API-Endpunkte erweitern

### Milestone 3: Frontend Multi-Dashboard
- [ ] Heatpumps Pinia Store
- [ ] HeatpumpSelector Komponente
- [ ] HeatpumpSetup Wizard
- [ ] Dashboard pro Gerät

### Milestone 4: Weitere Hersteller
- [ ] NIBE S-Series Driver
- [ ] Daikin Altherma Driver
- [ ] Luxtronik Driver

### Milestone 5: ML & Telemetrie
- [ ] Multi-Model Training
- [ ] Telemetrie v2 Format
- [ ] Vergleichs-Dashboards

---

## Quellen & Referenzen

- [NIBE Modbus Configuration (Home Assistant)](https://community.home-assistant.io/t/modbus-configuration-for-nibe-s-series-heatpumps/400422)
- [NIBE Python Library (GitHub)](https://github.com/yozik04/nibe)
- [Daikin Modbus Design Guide EKMBDXB7V1](https://www.daikin-ce.com/content/dam/document-library/Installer-reference-guide/ac/vrv/ekmbdxb/EKMBDXB_Design%20guide_4PEN642495-1A_English.pdf)
- [NIBE OpenHAB Binding](https://www.openhab.org/addons/bindings/nibeheatpump/)
- [EVCC Heat Pump Integration](https://docs.evcc.io/en/docs/devices/heating)
