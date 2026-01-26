# SPDX-License-Identifier: MIT
"""
Base classes for heat pump manufacturer drivers.

This module provides the abstract base classes and data structures
for implementing heat pump drivers for different manufacturers.

Architecture:
    HeatpumpDriver (ABC)
        |
        +-- IDMNavigator20Driver (idm/navigator_2_0.py)
        +-- NIBESSeriesDriver (nibe/s_series.py)
        +-- DaikinAlthermaDriver (daikin/altherma.py)
        +-- Luxtronik21Driver (luxtronik/luxtronik_2_1.py)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type
from enum import Enum
import struct
import logging

logger = logging.getLogger(__name__)


class SensorCategory(Enum):
    """Categories for sensor classification."""

    TEMPERATURE = "temperature"
    POWER = "power"
    ENERGY = "energy"
    STATUS = "status"
    PRESSURE = "pressure"
    FLOW = "flow"
    BINARY = "binary"
    HUMIDITY = "humidity"
    TIME = "time"
    COUNTER = "counter"
    SETPOINT = "setpoint"
    CONTROL = "control"


class DataType(Enum):
    """Modbus data types."""

    BOOL = "BOOL"  # 1 register, boolean
    UCHAR = "UCHAR"  # 1 register, unsigned 8-bit
    UINT8 = "UINT8"  # 1 register, unsigned 8-bit (Alias)
    INT8 = "INT8"  # 1 register, signed 8-bit
    UINT16 = "UINT16"  # 1 register, unsigned 16-bit
    INT16 = "INT16"  # 1 register, signed 16-bit
    UINT32 = "UINT32"  # 2 registers, unsigned 32-bit
    INT32 = "INT32"  # 2 registers, signed 32-bit
    FLOAT = "FLOAT"  # 2 registers, IEEE 754 float
    # Legacy aliases
    WORD = "UINT16"


class AccessMode(Enum):
    """Sensor access modes."""

    READ_ONLY = "RO"
    READ_WRITE = "RW"
    WRITE_ONLY = "WO"


@dataclass
class SensorDefinition:
    """
    Universal sensor definition for all manufacturers.

    This class represents a single sensor/register that can be read
    from or written to a heat pump via Modbus or other protocols.

    Attributes:
        id: Unique identifier (e.g., "temp_outside")
        name: Display name in English
        name_de: Display name in German
        category: Sensor category for grouping
        unit: Measurement unit (e.g., "°C", "kW")
        address: Modbus register address
        datatype: Data type for encoding/decoding
        access: Read/write access mode
        scale: Multiplication factor for raw value
        offset: Addition offset for raw value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        enum_values: Mapping of integer values to string names
        description: Detailed description
        eeprom_sensitive: Whether writes affect EEPROM (limited cycles)
    """

    id: str
    name: str
    name_de: str
    category: SensorCategory
    address: int
    datatype: DataType
    unit: Optional[str] = None
    access: AccessMode = AccessMode.READ_ONLY
    scale: float = 1.0
    offset: float = 0.0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum_values: Optional[Dict[int, str]] = None
    description: Optional[str] = None
    eeprom_sensitive: bool = False

    @property
    def size(self) -> int:
        """Returns the number of Modbus registers this sensor occupies."""
        if self.datatype in (DataType.FLOAT, DataType.UINT32, DataType.INT32):
            return 2
        return 1

    @property
    def is_writable(self) -> bool:
        """Check if sensor can be written to."""
        return self.access in (AccessMode.READ_WRITE, AccessMode.WRITE_ONLY)

    def __hash__(self):
        return hash((self.id, self.address))


@dataclass
class HeatpumpCapabilities:
    """
    Describes the capabilities of a heat pump model.

    This information is used by the UI to show/hide features
    and by the system to validate operations.
    """

    heating: bool = True
    cooling: bool = False
    hot_water: bool = True
    pool_heating: bool = False
    solar_integration: bool = False
    smart_grid: bool = False
    photovoltaic: bool = False
    max_circuits: int = 1
    max_zones: int = 1
    supports_modbus_write: bool = True
    writable_sensors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "heating": self.heating,
            "cooling": self.cooling,
            "hot_water": self.hot_water,
            "pool_heating": self.pool_heating,
            "solar_integration": self.solar_integration,
            "smart_grid": self.smart_grid,
            "photovoltaic": self.photovoltaic,
            "max_circuits": self.max_circuits,
            "max_zones": self.max_zones,
            "supports_modbus_write": self.supports_modbus_write,
            "writable_sensors": self.writable_sensors,
        }


@dataclass
class ConnectionConfig:
    """
    Configuration for connecting to a heat pump.
    """

    host: str
    port: int = 502
    unit_id: int = 1
    timeout: float = 10.0
    retries: int = 3

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "unit_id": self.unit_id,
            "timeout": self.timeout,
            "retries": self.retries,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConnectionConfig":
        return cls(
            host=data.get("host", ""),
            port=data.get("port", 502),
            unit_id=data.get("unit_id", 1),
            timeout=data.get("timeout", 10.0),
            retries=data.get("retries", 3),
        )


@dataclass
class ReadGroup:
    """
    A group of sensors that can be read in a single Modbus request.

    Used for optimizing read operations by grouping contiguous registers.
    """

    start_address: int
    count: int
    sensors: List[SensorDefinition]


class HeatpumpDriver(ABC):
    """
    Abstract base class for all heat pump drivers.

    Each manufacturer/model implements this interface to provide:
    - Sensor definitions specific to the model
    - Value encoding/decoding logic
    - Dashboard templates
    - Setup instructions

    Example implementation:
        class MyHeatpumpDriver(HeatpumpDriver):
            MANUFACTURER = "my_brand"
            MODEL = "model_x"
            DISPLAY_NAME = "My Brand Model X"

            def get_sensors(self, config):
                return [...]
    """

    # Class attributes to be overridden by implementations
    MANUFACTURER: str = ""
    MODEL: str = ""
    DISPLAY_NAME: str = ""
    PROTOCOL: str = "modbus_tcp"  # modbus_tcp, modbus_rtu, luxtronik, http
    DEFAULT_PORT: int = 502

    def __init__(self):
        """Initialize the driver."""
        self._sensors_cache: Optional[List[SensorDefinition]] = None

    @abstractmethod
    def get_sensors(self, config: Dict[str, Any]) -> List[SensorDefinition]:
        """
        Returns all available sensors for this heat pump.

        Args:
            config: Device-specific configuration (circuits, zones, etc.)

        Returns:
            List of SensorDefinition objects
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> HeatpumpCapabilities:
        """
        Returns the capabilities of this heat pump model.

        Returns:
            HeatpumpCapabilities object
        """
        pass

    def parse_value(self, sensor: SensorDefinition, raw_registers: List[int]) -> Any:
        """
        Converts raw Modbus registers to a sensor value.

        This default implementation handles common data types.
        Override for manufacturer-specific encoding.

        Args:
            sensor: The sensor definition
            raw_registers: List of 16-bit register values

        Returns:
            Decoded value (float, int, bool, or string)
        """
        raw_bytes = b"".join(struct.pack(">H", r) for r in raw_registers)

        try:
            if sensor.datatype == DataType.BOOL:
                value = bool(raw_registers[0])
            elif sensor.datatype == DataType.UCHAR:
                value = raw_registers[0] & 0xFF
            elif sensor.datatype == DataType.INT8:
                value = raw_registers[0] & 0xFF
                if value > 127:
                    value -= 256
            elif sensor.datatype in (DataType.UINT16, DataType.WORD):
                value = raw_registers[0]
            elif sensor.datatype == DataType.INT16:
                value = struct.unpack(">h", raw_bytes[:2])[0]
            elif sensor.datatype == DataType.UINT32:
                value = struct.unpack(">I", raw_bytes[:4])[0]
            elif sensor.datatype == DataType.INT32:
                value = struct.unpack(">i", raw_bytes[:4])[0]
            elif sensor.datatype == DataType.FLOAT:
                value = struct.unpack(">f", raw_bytes[:4])[0]
            else:
                value = raw_registers[0]

            # Apply scale and offset
            if isinstance(value, (int, float)) and sensor.datatype != DataType.BOOL:
                value = value * sensor.scale + sensor.offset

            # Handle enum values
            if sensor.enum_values and isinstance(value, (int, float)):
                int_value = int(value)
                if int_value in sensor.enum_values:
                    return {"value": int_value, "text": sensor.enum_values[int_value]}

            return value

        except Exception as e:
            logger.warning(f"Error parsing {sensor.id}: {e}")
            return None

    def encode_value(self, sensor: SensorDefinition, value: Any) -> List[int]:
        """
        Converts a value to Modbus registers for writing.

        Args:
            sensor: The sensor definition
            value: The value to encode

        Returns:
            List of 16-bit register values
        """
        # Remove scale and offset
        if isinstance(value, (int, float)) and sensor.datatype != DataType.BOOL:
            value = (value - sensor.offset) / sensor.scale

        try:
            if sensor.datatype == DataType.BOOL:
                return [1 if value else 0]
            elif sensor.datatype in (DataType.UCHAR, DataType.INT8):
                return [int(value) & 0xFF]
            elif sensor.datatype in (DataType.UINT16, DataType.INT16, DataType.WORD):
                return [int(value) & 0xFFFF]
            elif sensor.datatype == DataType.UINT32:
                packed = struct.pack(">I", int(value))
                return [
                    struct.unpack(">H", packed[i : i + 2])[0] for i in range(0, 4, 2)
                ]
            elif sensor.datatype == DataType.INT32:
                packed = struct.pack(">i", int(value))
                return [
                    struct.unpack(">H", packed[i : i + 2])[0] for i in range(0, 4, 2)
                ]
            elif sensor.datatype == DataType.FLOAT:
                packed = struct.pack(">f", float(value))
                return [
                    struct.unpack(">H", packed[i : i + 2])[0] for i in range(0, 4, 2)
                ]
            else:
                return [int(value) & 0xFFFF]

        except Exception as e:
            logger.error(f"Error encoding {sensor.id}: {e}")
            raise ValueError(f"Cannot encode value {value} for {sensor.id}: {e}")

    def get_read_groups(
        self,
        sensors: List[SensorDefinition],
        max_block_size: int = 50,
        max_gap: int = 5,
    ) -> List[ReadGroup]:
        """
        Optimizes sensors into contiguous read groups.

        This reduces the number of Modbus requests by grouping
        sensors with adjacent addresses.

        Args:
            sensors: List of sensors to group
            max_block_size: Maximum registers per request
            max_gap: Maximum gap to bridge between sensors

        Returns:
            List of ReadGroup objects
        """
        if not sensors:
            return []

        # Filter to readable sensors and sort by address
        readable = [s for s in sensors if s.access != AccessMode.WRITE_ONLY]
        readable.sort(key=lambda s: s.address)

        groups = []
        current_sensors = [readable[0]]

        for i in range(1, len(readable)):
            sensor = readable[i]
            prev = current_sensors[-1]

            prev_end = prev.address + prev.size
            gap = sensor.address - prev_end
            new_size = (sensor.address + sensor.size) - current_sensors[0].address

            # Check if we can extend the current group
            if gap <= max_gap and new_size <= max_block_size:
                current_sensors.append(sensor)
            else:
                # Finalize current group and start new one
                start = current_sensors[0].address
                end = current_sensors[-1].address + current_sensors[-1].size
                groups.append(
                    ReadGroup(
                        start_address=start, count=end - start, sensors=current_sensors
                    )
                )
                current_sensors = [sensor]

        # Don't forget the last group
        if current_sensors:
            start = current_sensors[0].address
            end = current_sensors[-1].address + current_sensors[-1].size
            groups.append(
                ReadGroup(
                    start_address=start, count=end - start, sensors=current_sensors
                )
            )

        return groups

    def get_dashboard_template(self) -> Dict[str, Any]:
        """
        Returns a default dashboard configuration for this model.

        Override to provide model-specific dashboard layouts.

        Returns:
            Dashboard configuration dict
        """
        return {
            "name": f"{self.DISPLAY_NAME} Dashboard",
            "charts": [
                {
                    "title": "Temperaturen",
                    "type": "line",
                    "queries": [
                        {"label": "Außentemperatur", "metric": "temp_outside"},
                        {"label": "Vorlauf", "metric": "temp_flow"},
                        {"label": "Rücklauf", "metric": "temp_return"},
                    ],
                    "hours": 24,
                },
                {
                    "title": "Leistung",
                    "type": "line",
                    "queries": [
                        {"label": "Aktuelle Leistung", "metric": "power_current"},
                    ],
                    "hours": 24,
                },
            ],
        }

    def get_setup_instructions(self) -> Optional[str]:
        """
        Returns setup instructions for this heat pump model.

        Override to provide model-specific setup guidance.

        Returns:
            Setup instructions as markdown text, or None
        """
        return None

    def requires_custom_client(self) -> bool:
        """
        Returns True if this driver needs a custom client instead of Modbus.

        For example, Luxtronik uses its own TCP protocol.
        """
        return self.PROTOCOL != "modbus_tcp"

    def get_metric_prefix(self) -> str:
        """
        Returns the metric name prefix for this manufacturer.

        Default: idm_heatpump_
        """
        return "idm_heatpump_"

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates device-specific configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None

    def get_sensor_by_id(
        self, sensor_id: str, config: Dict[str, Any]
    ) -> Optional[SensorDefinition]:
        """
        Finds a sensor by its ID.

        Args:
            sensor_id: The sensor ID to find
            config: Device configuration

        Returns:
            SensorDefinition or None
        """
        sensors = self.get_sensors(config)
        for sensor in sensors:
            if sensor.id == sensor_id:
                return sensor
        return None

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.MANUFACTURER}/{self.MODEL}>"
