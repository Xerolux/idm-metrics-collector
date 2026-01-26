# SPDX-License-Identifier: MIT
"""
iDM Navigator 2.0 Heat Pump Driver.

This driver provides support for iDM heat pumps with Navigator 2.0 controller.
It uses the existing sensor definitions from sensor_addresses.py and wraps
them in the new multi-heatpump architecture.

Supported features:
- Heating (up to 7 circuits: A-G)
- Cooling (active and passive)
- Hot water
- Solar integration
- Smart Grid
- Photovoltaic integration
- Zone control (up to 12 zones)
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
import struct

from ..base import (
    HeatpumpDriver,
    SensorDefinition,
    SensorCategory,
    DataType,
    AccessMode,
    HeatpumpCapabilities,
    ReadGroup,
)
from .. import ManufacturerRegistry

# Import existing sensor definitions
from ...sensor_addresses import (
    COMMON_SENSORS,
    BINARY_SENSOR_ADDRESSES,
    heating_circuit_sensors,
    zone_sensors,
    HeatingCircuit,
    BaseSensorAddress,
    IdmBinarySensorAddress,
    _FloatSensorAddress,
    _UCharSensorAddress,
    _WordSensorAddress,
    _EnumSensorAddress,
    _BitFieldSensorAddress,
    SensorFeatures,
)

logger = logging.getLogger(__name__)


def _convert_legacy_sensor(
    legacy: BaseSensorAddress, category: Optional[SensorCategory] = None
) -> SensorDefinition:
    """
    Converts a legacy sensor definition to the new SensorDefinition format.

    Args:
        legacy: Legacy sensor from sensor_addresses.py
        category: Optional category override

    Returns:
        SensorDefinition in new format
    """
    # Determine category from sensor name or type
    if category is None:
        category = _infer_category(legacy.name, legacy)

    # Determine data type
    datatype = _convert_datatype(legacy.datatype)

    # Determine access mode
    if not legacy.read_supported:
        access = AccessMode.WRITE_ONLY
    elif legacy.supported_features != SensorFeatures.NONE:
        access = AccessMode.READ_WRITE
    else:
        access = AccessMode.READ_ONLY

    # Get constraints
    min_val = getattr(legacy, "min_value", None)
    max_val = getattr(legacy, "max_value", None)
    scale = getattr(legacy, "scale", 1.0)

    # Get enum values if applicable
    enum_values = None
    if isinstance(legacy, _EnumSensorAddress):
        enum_values = {e.value: e.name for e in legacy.enum}
    elif isinstance(legacy, _BitFieldSensorAddress):
        enum_values = {f.value: f.name for f in legacy.flag}

    return SensorDefinition(
        id=legacy.name,
        name=_format_name(legacy.name),
        name_de=_format_name_de(legacy.name),
        category=category,
        address=legacy.address,
        datatype=datatype,
        unit=legacy.unit,
        access=access,
        scale=scale if scale != 1.0 else 1.0,
        min_value=min_val,
        max_value=max_val,
        enum_values=enum_values,
        eeprom_sensitive=legacy.eeprom_sensitive,
    )


def _convert_datatype(legacy_type: str) -> DataType:
    """Converts legacy datatype string to DataType enum."""
    mapping = {
        "float32": DataType.FLOAT,
        "uint16": DataType.UINT16,
        "int16": DataType.INT16,
        "uint32": DataType.UINT32,
        "int32": DataType.INT32,
    }
    return mapping.get(legacy_type, DataType.UINT16)


def _infer_category(name: str, sensor: BaseSensorAddress) -> SensorCategory:
    """Infers sensor category from name and type."""
    name_lower = name.lower()

    if "temp" in name_lower:
        if "target" in name_lower or "request" in name_lower:
            return SensorCategory.SETPOINT
        return SensorCategory.TEMPERATURE
    elif "power" in name_lower:
        return SensorCategory.POWER
    elif "energy" in name_lower:
        return SensorCategory.ENERGY
    elif "humidity" in name_lower:
        return SensorCategory.HUMIDITY
    elif "status" in name_lower or "mode" in name_lower or "state" in name_lower:
        return SensorCategory.STATUS
    elif "valve" in name_lower:
        return SensorCategory.STATUS
    elif isinstance(sensor, IdmBinarySensorAddress):
        return SensorCategory.BINARY
    elif "request" in name_lower:
        return SensorCategory.STATUS

    return SensorCategory.STATUS


def _format_name(sensor_name: str) -> str:
    """Formats sensor name for display (English)."""
    return sensor_name.replace("_", " ").title()


def _format_name_de(sensor_name: str) -> str:
    """Formats sensor name for display (German)."""
    translations = {
        "temp_outside": "Außentemperatur",
        "temp_outside_avg": "Gemittelte Außentemperatur",
        "temp_heat_storage": "Wärmespeichertemperatur",
        "temp_cold_storage": "Kältespeichertemperatur",
        "temp_water_heater_bottom": "Trinkwassererwärmer unten",
        "temp_water_heater_top": "Trinkwassererwärmer oben",
        "temp_water_heater_tap": "Warmwasserzapftemperatur",
        "temp_water_target": "Warmwasser-Solltemperatur",
        "temp_heat_pump_flow": "Vorlauftemperatur",
        "temp_heat_pump_return": "Rücklauftemperatur",
        "temp_heat_source_input": "Wärmequelle Eingang",
        "temp_heat_source_output": "Wärmequelle Ausgang",
        "power_current": "Aktuelle Leistung",
        "power_current_draw": "Stromaufnahme",
        "power_thermal": "Thermische Leistung",
        "energy_heat_total": "Wärmeenergie Gesamt",
        "energy_heat_heating": "Wärmeenergie Heizen",
        "energy_heat_total_water": "Wärmeenergie Warmwasser",
        "energy_heat_total_cooling": "Wärmeenergie Kühlen",
        "status_system": "Systembetriebsart",
        "status_heat_pump": "Wärmepumpenstatus",
        "status_smart_grid": "Smart Grid Status",
        "humidity": "Luftfeuchtigkeit",
        "failure_id": "Fehlernummer",
        "failure_heat_pump": "Störung Wärmepumpe",
    }
    return translations.get(sensor_name, _format_name(sensor_name))


@ManufacturerRegistry.register
class IDMNavigator20Driver(HeatpumpDriver):
    """
    Driver for iDM heat pumps with Navigator 2.0 controller.

    The Navigator 2.0 is iDM's current generation controller supporting:
    - Modbus TCP on port 502
    - Up to 7 heating circuits (A-G)
    - Up to 12 zones for individual room control
    - Solar thermal integration
    - Smart Grid / PV integration
    - Active and passive cooling

    Configuration options:
        circuits: List of heating circuit names ["A", "B", ...]
        zones: List of zone IDs [1, 2, 3, ...]
    """

    MANUFACTURER = "idm"
    MODEL = "navigator_2_0"
    DISPLAY_NAME = "iDM Navigator 2.0"
    PROTOCOL = "modbus_tcp"
    DEFAULT_PORT = 502

    def __init__(self):
        super().__init__()
        self._sensor_cache: Dict[str, List[SensorDefinition]] = {}

    def get_sensors(self, config: Dict[str, Any]) -> List[SensorDefinition]:
        """
        Returns all sensors based on configuration.

        Args:
            config: Device config with 'circuits' and 'zones' lists

        Returns:
            List of SensorDefinition objects
        """
        # Create cache key from config
        circuits = tuple(config.get("circuits", ["A"]))
        zones = tuple(config.get("zones", []))
        cache_key = f"{circuits}_{zones}"

        if cache_key in self._sensor_cache:
            return self._sensor_cache[cache_key]

        sensors = []

        # Add common sensors
        for legacy in COMMON_SENSORS:
            sensors.append(_convert_legacy_sensor(legacy))

        # Add binary sensors
        for name, legacy in BINARY_SENSOR_ADDRESSES.items():
            sensors.append(_convert_legacy_sensor(legacy, SensorCategory.BINARY))

        # Add heating circuit sensors
        for circuit_name in circuits:
            try:
                circuit_enum = HeatingCircuit[circuit_name.upper()]
                circuit_sensors = heating_circuit_sensors(circuit_enum)
                for legacy in circuit_sensors:
                    sensors.append(_convert_legacy_sensor(legacy))
            except KeyError:
                logger.warning(f"Invalid heating circuit: {circuit_name}")

        # Add zone sensors
        for zone_id in zones:
            try:
                zone_id_int = int(zone_id)
                if 0 <= zone_id_int < 10:
                    z_sensors = zone_sensors(zone_id_int)
                    for legacy in z_sensors:
                        sensors.append(_convert_legacy_sensor(legacy))
            except (ValueError, IndexError) as e:
                logger.warning(f"Invalid zone ID: {zone_id} ({e})")

        self._sensor_cache[cache_key] = sensors
        return sensors

    def get_capabilities(self) -> HeatpumpCapabilities:
        """Returns the capabilities of iDM Navigator 2.0."""
        return HeatpumpCapabilities(
            heating=True,
            cooling=True,
            hot_water=True,
            pool_heating=True,
            solar_integration=True,
            smart_grid=True,
            photovoltaic=True,
            max_circuits=7,  # A-G
            max_zones=10,
            supports_modbus_write=True,
            writable_sensors=[
                "status_system",
                "temp_water_target",
                "temp_room_target_heating_normal_circuit_a",
                "temp_room_target_cooling_normal_circuit_a",
                "power_solar_surplus",
                "power_solar_production",
                "request_heating",
                "request_cooling",
                "request_water",
            ],
        )

    def parse_value(self, sensor: SensorDefinition, raw_registers: List[int]) -> Any:
        """
        Parses raw Modbus registers for iDM-specific encoding.

        iDM uses:
        - Big-endian byte order within words
        - Little-endian word order for 32-bit values (low word first)
        """
        try:
            if sensor.datatype == DataType.FLOAT:
                # iDM: Little-endian word order, big-endian bytes
                if len(raw_registers) < 2:
                    return None

                # Swap words (little-endian word order)
                low_word = raw_registers[0]
                high_word = raw_registers[1]

                # Pack as big-endian words, then reinterpret
                byte_data = struct.pack(">HH", low_word, high_word)
                # Unpack as little-endian float
                value = struct.unpack("<f", byte_data)[0]

            elif sensor.datatype == DataType.UINT16:
                value = raw_registers[0]
                # Check for invalid value marker
                if value == 0xFFFF:
                    return None

            elif sensor.datatype == DataType.INT16:
                value = struct.unpack(">h", struct.pack(">H", raw_registers[0]))[0]
                # Check for invalid value marker
                if (
                    value == -1
                    and sensor.min_value is not None
                    and sensor.min_value >= 0
                ):
                    return None

            elif sensor.datatype == DataType.BOOL:
                value = bool(raw_registers[0])

            else:
                value = raw_registers[0]

            # Apply scale
            if isinstance(value, (int, float)) and sensor.datatype != DataType.BOOL:
                value = value * sensor.scale + sensor.offset

            # Handle enum values
            if sensor.enum_values is not None:
                int_value = int(value) if isinstance(value, float) else value
                if int_value in sensor.enum_values:
                    return {"value": int_value, "text": sensor.enum_values[int_value]}

            return value

        except Exception as e:
            logger.debug(f"Error parsing {sensor.id}: {e}")
            return None

    def encode_value(self, sensor: SensorDefinition, value: Any) -> List[int]:
        """
        Encodes a value to Modbus registers for iDM.

        Uses the same encoding as parse_value in reverse.
        """
        # Remove scale and offset
        if isinstance(value, (int, float)) and sensor.datatype != DataType.BOOL:
            value = (value - sensor.offset) / sensor.scale

        try:
            if sensor.datatype == DataType.FLOAT:
                # Pack as little-endian float
                byte_data = struct.pack("<f", float(value))
                # Unpack as big-endian words
                words = struct.unpack(">HH", byte_data)
                return list(words)

            elif sensor.datatype in (DataType.UINT16, DataType.INT16):
                return [int(value) & 0xFFFF]

            elif sensor.datatype == DataType.BOOL:
                return [1 if value else 0]

            else:
                return [int(value) & 0xFFFF]

        except Exception as e:
            logger.error(f"Error encoding {sensor.id}: {e}")
            raise ValueError(f"Cannot encode {value} for {sensor.id}")

    def get_dashboard_template(self) -> Dict[str, Any]:
        """Returns the default dashboard template for iDM heat pumps."""
        return {
            "name": "iDM Wärmepumpe",
            "charts": [
                {
                    "id": "temps_main",
                    "title": "Temperaturen",
                    "type": "line",
                    "queries": [
                        {
                            "label": "Außentemperatur",
                            "metric": "temp_outside",
                            "color": "#3b82f6",
                        },
                        {
                            "label": "Vorlauf",
                            "metric": "temp_heat_pump_flow",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Rücklauf",
                            "metric": "temp_heat_pump_return",
                            "color": "#f97316",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": "temps_storage",
                    "title": "Speichertemperaturen",
                    "type": "line",
                    "queries": [
                        {
                            "label": "Wärmespeicher",
                            "metric": "temp_heat_storage",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Kältespeicher",
                            "metric": "temp_cold_storage",
                            "color": "#3b82f6",
                        },
                        {
                            "label": "Warmwasser oben",
                            "metric": "temp_water_heater_top",
                            "color": "#f59e0b",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": "power",
                    "title": "Leistung",
                    "type": "line",
                    "queries": [
                        {
                            "label": "Aktuelle Leistung",
                            "metric": "power_current",
                            "color": "#22c55e",
                        },
                        {
                            "label": "Stromaufnahme",
                            "metric": "power_current_draw",
                            "color": "#ef4444",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "id": "energy",
                    "title": "Energie (kumulativ)",
                    "type": "line",
                    "queries": [
                        {
                            "label": "Heizen",
                            "metric": "energy_heat_heating",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Warmwasser",
                            "metric": "energy_heat_total_water",
                            "color": "#f59e0b",
                        },
                        {
                            "label": "Kühlen",
                            "metric": "energy_heat_total_cooling",
                            "color": "#3b82f6",
                        },
                    ],
                    "hours": 168,  # 1 week
                },
                {
                    "id": "hot_water_gauge",
                    "title": "Warmwasser",
                    "type": "gauge",
                    "queries": [
                        {"label": "Temperatur", "metric": "temp_water_heater_top"},
                    ],
                    "min": 0,
                    "max": 65,
                    "thresholds": [
                        {"value": 45, "color": "#22c55e"},
                        {"value": 55, "color": "#f59e0b"},
                        {"value": 60, "color": "#ef4444"},
                    ],
                },
                {
                    "id": "status",
                    "title": "Status",
                    "type": "stat",
                    "queries": [
                        {"label": "Betriebsart", "metric": "status_system_str"},
                        {"label": "Smart Grid", "metric": "status_smart_grid_str"},
                    ],
                },
            ],
        }

    def get_setup_instructions(self) -> str:
        """Returns setup instructions for iDM Navigator 2.0."""
        return """
## iDM Navigator 2.0 - Einrichtung

### Voraussetzungen
- iDM Wärmepumpe mit Navigator 2.0 Regelung
- Netzwerkverbindung zur Wärmepumpe (LAN)
- Modbus TCP muss aktiviert sein

### Modbus aktivieren
1. Am Navigator Display: Menü → Einstellungen → Kommunikation
2. Modbus TCP aktivieren
3. IP-Adresse notieren (oder DHCP verwenden)

### Verbindungseinstellungen
- **Port:** 502 (Standard)
- **Unit ID:** 1
- **Timeout:** 10 Sekunden empfohlen

### Heizkreise konfigurieren
Wählen Sie die vorhandenen Heizkreise aus:
- Heizkreis A (Standard)
- Heizkreis B-G (falls vorhanden)

### Zonen (optional)
Falls Sie die iDM Einzelraumregelung nutzen, können Sie
bis zu 10 Zonen konfigurieren.

### Hinweise
- Schreibzugriff muss in der Wärmepumpe freigegeben sein
- Einige Parameter sind EEPROM-sensitiv (begrenzte Schreibzyklen)
"""

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validates the device configuration."""
        circuits = config.get("circuits", [])
        zones = config.get("zones", [])

        # Validate circuits
        valid_circuits = {"A", "B", "C", "D", "E", "F", "G"}
        for c in circuits:
            if c.upper() not in valid_circuits:
                return False, f"Ungültiger Heizkreis: {c}. Erlaubt: A-G"

        # Validate zones
        for z in zones:
            try:
                z_int = int(z)
                if z_int < 0 or z_int >= 10:
                    return False, f"Ungültige Zone: {z}. Erlaubt: 0-9"
            except ValueError:
                return False, f"Zone muss eine Zahl sein: {z}"

        return True, None

    def get_available_circuits(self) -> List[Dict[str, str]]:
        """Returns list of available heating circuits."""
        return [
            {"id": "A", "name": "Heizkreis A"},
            {"id": "B", "name": "Heizkreis B"},
            {"id": "C", "name": "Heizkreis C"},
            {"id": "D", "name": "Heizkreis D"},
            {"id": "E", "name": "Heizkreis E"},
            {"id": "F", "name": "Heizkreis F"},
            {"id": "G", "name": "Heizkreis G"},
        ]

    def get_available_zones(self) -> List[Dict[str, Any]]:
        """Returns list of available zones."""
        return [{"id": i, "name": f"Zone {i + 1}"} for i in range(10)]
