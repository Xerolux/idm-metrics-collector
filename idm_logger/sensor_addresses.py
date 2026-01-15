"""Sensor addresses."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, IntEnum, IntFlag
from typing import Generic, TypeVar

from .const import (
    ActiveCircuitMode,
    CircuitMode,
    HeatPumpStatus,
    IscMode,
    RoomMode,
    SensorFeatures,
    SmartGridStatus,
    SolarMode,
    SystemStatus,
    ValveStateHeatingCooling,
    ValveStateHeatingWater,
    ValveStateHeatSourceColdStorage,
    ValveStateStorageBypass,
    ValveStateStorageHeatSource,
    ZoneMode,
)

import logging
import struct

LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")
_EnumT = TypeVar("_EnumT", bound=IntEnum)
_FlagT = TypeVar("_FlagT", bound=IntFlag)

PERCENTAGE = "%"
CURRENCY_EURO = "EUR"


class UnitOfEnergy:
    KILO_WATT_HOUR = "kWh"


class UnitOfPower:
    KILO_WATT = "kW"


class UnitOfTemperature:
    CELSIUS = "°C"


NAME_POWER_USAGE = "power_current_draw"


def _decode_registers(
    registers: list[int],
    datatype: str,
    byteorder: str = "big",
    wordorder: str = "little",
):
    """Decode registers to value using struct (replacement for BinaryPayloadDecoder)."""
    # Convert registers to bytes
    # With Big endian byte order and Little endian word order
    if wordorder.lower() == "little":
        # Reverse word order for multi-register values
        if len(registers) > 1:
            registers = list(reversed(registers))

    # Pack registers to bytes (each register is 16 bits)
    byte_data = b""
    for reg in registers:
        if byteorder.lower() == "big":
            byte_data += struct.pack(">H", reg)  # Big endian 16-bit
        else:
            byte_data += struct.pack("<H", reg)  # Little endian 16-bit

    # Decode based on datatype
    if datatype == "float32":
        if byteorder.lower() == "big":
            return struct.unpack(">f", byte_data)[0]
        else:
            return struct.unpack("<f", byte_data)[0]
    elif datatype == "int16":
        if byteorder.lower() == "big":
            return struct.unpack(">h", byte_data[:2])[0]
        else:
            return struct.unpack("<h", byte_data[:2])[0]
    elif datatype == "uint16":
        if byteorder.lower() == "big":
            return struct.unpack(">H", byte_data[:2])[0]
        else:
            return struct.unpack("<H", byte_data[:2])[0]
    elif datatype == "int32":
        if byteorder.lower() == "big":
            return struct.unpack(">i", byte_data)[0]
        else:
            return struct.unpack("<i", byte_data)[0]
    elif datatype == "uint32":
        if byteorder.lower() == "big":
            return struct.unpack(">I", byte_data)[0]
        else:
            return struct.unpack("<I", byte_data)[0]
    return registers[0]


def _encode_value(
    value: int | float, datatype: str, byteorder: str = "big", wordorder: str = "little"
) -> list[int]:
    """Encode value to registers using struct (replacement for BinaryPayloadBuilder)."""
    # Pack value to bytes based on datatype
    if datatype == "float32":
        if byteorder.lower() == "big":
            byte_data = struct.pack(">f", float(value))
        else:
            byte_data = struct.pack("<f", float(value))
    elif datatype == "int16":
        if byteorder.lower() == "big":
            byte_data = struct.pack(">h", int(value))
        else:
            byte_data = struct.pack("<h", int(value))
    elif datatype == "uint16":
        if byteorder.lower() == "big":
            byte_data = struct.pack(">H", int(value))
        else:
            byte_data = struct.pack("<H", int(value))
    elif datatype == "int32":
        if byteorder.lower() == "big":
            byte_data = struct.pack(">i", int(value))
        else:
            byte_data = struct.pack("<i", int(value))
    elif datatype == "uint32":
        if byteorder.lower() == "big":
            byte_data = struct.pack(">I", int(value))
        else:
            byte_data = struct.pack("<I", int(value))
    else:
        byte_data = struct.pack(">H", int(value))

    # Convert bytes to registers (16-bit chunks)
    registers = []
    for i in range(0, len(byte_data), 2):
        if byteorder.lower() == "big":
            registers.append(struct.unpack(">H", byte_data[i : i + 2])[0])
        else:
            registers.append(struct.unpack("<H", byte_data[i : i + 2])[0])

    # Apply word order
    if wordorder.lower() == "little" and len(registers) > 1:
        registers = list(reversed(registers))

    return registers


@dataclass(kw_only=True)
class BaseSensorAddress(ABC, Generic[_T]):
    """Base class for (binary) sensors of an IDM heatpump."""

    address: int
    name: str
    supported_features: SensorFeatures = SensorFeatures.NONE
    force_single: bool = False
    unit: str | None = None
    eeprom_sensitive: bool = False
    cyclic_change_required: bool = False
    read_supported: bool = True

    @property
    def size(self) -> int:
        """Get number of registers this sensor's value occupies."""
        # 32bit types use 2 registers, 16bit use 1
        if self.datatype in ("float32", "int32", "uint32"):
            return 2
        return 1

    @property
    @abstractmethod
    def datatype(self) -> str:
        """Get the datatype name."""

    def _decode_raw(self, registers: list[int]):
        return _decode_registers(
            registers, self.datatype, byteorder="big", wordorder="little"
        )

    def _encode_raw(self, value: int | float) -> list[int]:
        return _encode_value(value, self.datatype, byteorder="big", wordorder="little")

    @abstractmethod
    def decode(self, registers: list[int]) -> tuple[bool, _T]:
        """Decode this sensor's value."""

    @abstractmethod
    def encode(self, value: _T) -> list[int]:
        """Encode this sensor's value."""

    @property
    def zone_id(self) -> int | None:
        if self.address < 2000 or self.address > ZONE_OFFSETS[-1] + 65:
            return None
        for i, offset in enumerate(ZONE_OFFSETS):
            if offset > self.address:
                return i - 1
        return len(ZONE_OFFSETS)


@dataclass(kw_only=True)
class IdmSensorAddress(BaseSensorAddress[_T]):
    pass


@dataclass(kw_only=True)
class IdmBinarySensorAddress(BaseSensorAddress[bool]):
    @property
    def datatype(self) -> str:
        return "uint16"

    def decode(self, registers: list[int]) -> tuple[bool, bool]:
        value = self._decode_raw(registers)
        return (True, value > 0)

    def encode(self, value: bool) -> list[int]:
        return self._encode_raw(1 if value else 0)


@dataclass(kw_only=True)
class _FloatSensorAddress(IdmSensorAddress[float]):
    unit: str | None
    decimal_digits: int = 2
    scale: float = 1
    min_value: float | None = None
    max_value: float | None = None

    @property
    def datatype(self) -> str:
        return "float32"

    def decode(self, registers: list[int]) -> tuple[bool, float]:
        raw_value = self._decode_raw(registers)
        value = round(raw_value * self.scale, self.decimal_digits)

        if self.min_value == 0.0 and value == -1:
            return (False, 0.0)

        if (self.min_value is not None and value < self.min_value) or (
            self.max_value is not None and value > self.max_value
        ):
            pass

        return (True, value)

    def encode(self, value: float) -> list[int]:
        return self._encode_raw(value)


@dataclass(kw_only=True)
class _UCharSensorAddress(IdmSensorAddress[int]):
    unit: str | None
    min_value: int | None = None
    max_value: int | None = 0xFFFE

    @property
    def datatype(self) -> str:
        return "uint16"

    def decode(self, registers: list[int]) -> tuple[bool, int]:
        value = self._decode_raw(registers)
        if self.max_value == 0xFFFE and value == 0xFFFF:
            return (False, 0)
        return (True, value)

    def encode(self, value: int) -> list[int]:
        return self._encode_raw(value)


@dataclass(kw_only=True)
class _WordSensorAddress(IdmSensorAddress[int]):
    unit: str | None
    min_value: int | None = None
    max_value: int | None = None

    @property
    def datatype(self) -> str:
        return "int16"

    def decode(self, registers: list[int]) -> tuple[bool, int]:
        value = self._decode_raw(registers)
        if self.min_value == 0 and value == -1:
            return (False, 0)
        return (True, value)

    def encode(self, value: int) -> list[int]:
        return self._encode_raw(value)


@dataclass(kw_only=True)
class _EnumSensorAddress(IdmSensorAddress[_EnumT], Generic[_EnumT]):
    enum: type[_EnumT]

    @property
    def datatype(self) -> str:
        return "uint16"

    def decode(self, registers: list[int]) -> tuple[bool, _EnumT]:
        value = self._decode_raw(registers)
        if value == 0xFFFF and 0xFFFF not in list(map(int, self.enum)):
            return (False, self.enum(None))
        try:
            return (True, self.enum(value))
        except ValueError:
            return (False, None)

    def encode(self, value: _EnumT) -> list[int]:
        return self._encode_raw(value.value)


@dataclass(kw_only=True)
class _BitFieldSensorAddress(IdmSensorAddress[_FlagT], Generic[_FlagT]):
    flag: type[_FlagT]

    @property
    def datatype(self) -> str:
        return "uint16"

    def decode(self, registers: list[int]) -> tuple[bool, _FlagT]:
        value = self._decode_raw(registers)
        if value == 0xFFFF:
            return (False, self.flag(None))
        try:
            return (True, self.flag(value))
        except ValueError:
            return (False, None)

    def encode(self, value: _FlagT) -> list[int]:
        return self._encode_raw(value)


class HeatingCircuit(Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6


def heating_circuit_sensors(circuit: HeatingCircuit) -> list[IdmSensorAddress]:
    offset = circuit.value
    circuit_name = circuit.name.lower()
    return [
        _FloatSensorAddress(
            address=1350 + offset * 2,
            name=f"temp_flow_current_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1364 + offset * 2,
            name=f"temp_room_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1378 + offset * 2,
            name=f"temp_flow_target_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _EnumSensorAddress(
            enum=CircuitMode,
            address=1393 + offset,
            name=f"mode_circuit_{circuit_name}",
            supported_features=SensorFeatures.SET_CIRCUIT_MODE,
        ),
        _FloatSensorAddress(
            address=1401 + offset * 2,
            name=f"temp_room_target_heating_normal_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            supported_features=SensorFeatures.SET_TEMPERATURE,
            min_value=-10,
            max_value=80,
        ),
        _FloatSensorAddress(
            address=1415 + offset * 2,
            name=f"temp_room_target_heating_eco_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            supported_features=SensorFeatures.SET_TEMPERATURE,
            min_value=-10,
            max_value=80,
        ),
        _FloatSensorAddress(
            address=1429 + offset * 2,
            name=f"curve_circuit_{circuit_name}",
            unit=None,
        ),
        _UCharSensorAddress(
            address=1442 + offset,
            name=f"temp_threshold_heating_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            min_value=-10,
            max_value=80,
        ),
        _UCharSensorAddress(
            address=1449 + offset,
            name=f"temp_flow_target_constant_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            min_value=5,
            max_value=95,
        ),
        _FloatSensorAddress(
            address=1457 + offset * 2,
            name=f"temp_room_target_cooling_normal_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            min_value=-10,
            max_value=80,
        ),
        _FloatSensorAddress(
            address=1471 + offset * 2,
            name=f"temp_room_target_cooling_eco_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            min_value=-10,
            max_value=80,
        ),
        _UCharSensorAddress(
            address=1484 + offset,
            name=f"temp_threshold_cooling_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            min_value=-10,
            max_value=80,
        ),
        _UCharSensorAddress(
            address=1491 + offset,
            name=f"temp_flow_target_cooling_circuit_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            min_value=5,
            max_value=95,
        ),
        _EnumSensorAddress(
            enum=ActiveCircuitMode,
            address=1498 + offset,
            name=f"mode_active_circuit_{circuit_name}",
        ),
        _UCharSensorAddress(
            address=1505 + offset,
            name=f"curve_offset_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            supported_features=SensorFeatures.SET_TEMPERATURE,
        ),
        _FloatSensorAddress(
            address=1650 + offset * 2,
            name=f"temp_external_room_{circuit_name}",
            unit=UnitOfTemperature.CELSIUS,
            supported_features=SensorFeatures.SET_TEMPERATURE,
        ),
    ]


T = TypeVar("T")


def zone_sensors(zone_idx: int) -> list[IdmSensorAddress]:
    offset = ZONE_OFFSETS[zone_idx]
    zone_num = zone_idx + 1
    sensors: list[IdmSensorAddress] = [
        _EnumSensorAddress(address=offset, name=f"mode_zone_{zone_num}", enum=ZoneMode),
        _UCharSensorAddress(address=offset + 1, name=f"dehumidifier_zone_{zone_num}"),
    ]

    for room_idx in range(8):
        room_offset = offset + 2 + (room_idx * 7)
        room_num = room_idx + 1
        sensors.extend(
            [
                _FloatSensorAddress(
                    address=room_offset,
                    name=f"temp_room_zone_{zone_num}_room_{room_num}",
                    unit=UnitOfTemperature.CELSIUS,
                ),
                _FloatSensorAddress(
                    address=room_offset + 2,
                    name=f"temp_target_zone_{zone_num}_room_{room_num}",
                    unit=UnitOfTemperature.CELSIUS,
                    supported_features=SensorFeatures.SET_TEMPERATURE,
                ),
                _UCharSensorAddress(
                    address=room_offset + 4,
                    name=f"humidity_zone_{zone_num}_room_{room_num}",
                    unit=PERCENTAGE,
                ),
                _EnumSensorAddress(
                    address=room_offset + 5,
                    name=f"mode_zone_{zone_num}_room_{room_num}",
                    enum=RoomMode,
                    supported_features=SensorFeatures.SET_ROOM_MODE,
                ),
                _UCharSensorAddress(
                    address=room_offset + 6,
                    name=f"relay_zone_{zone_num}_room_{room_num}",
                ),
            ]
        )

    # Room 9 relay
    sensors.append(
        _UCharSensorAddress(address=offset + 64, name=f"relay_zone_{zone_num}_room_9")
    )

    return sensors


ZONE_OFFSETS = [2000 + 65 * i for i in range(10)]
ROOM_OFFSETS = [2 + 7 * i for i in range(8)]

# Renamed SENSOR_LIST to COMMON_SENSORS to make it clear this is the base list
COMMON_SENSORS = [
    _FloatSensorAddress(
        address=74,
        name="power_solar_surplus",
        unit=UnitOfPower.KILO_WATT,
        supported_features=SensorFeatures.SET_POWER,
        read_supported=False,
    ),
    _FloatSensorAddress(
        address=76, name="power_resistive_heater", unit=UnitOfPower.KILO_WATT
    ),
    _FloatSensorAddress(
        address=78,
        name="power_solar_production",
        unit=UnitOfPower.KILO_WATT,
        min_value=0,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _FloatSensorAddress(
        address=82,
        name="power_use_house",
        unit=UnitOfPower.KILO_WATT,
        min_value=0,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _FloatSensorAddress(
        address=84,
        name="power_drain_battery",
        unit=UnitOfPower.KILO_WATT,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _WordSensorAddress(
        address=86,
        name="charge_state_battery",
        unit=PERCENTAGE,
        min_value=0,
        max_value=100,
        supported_features=SensorFeatures.SET_BATTERY,
    ),
    _FloatSensorAddress(
        address=1000, name="temp_outside", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1002, name="temp_outside_avg", unit=UnitOfTemperature.CELSIUS
    ),
    _UCharSensorAddress(address=1004, name="failure_id"),
    _EnumSensorAddress(
        address=1005,
        name="status_system",
        enum=SystemStatus,
        eeprom_sensitive=True,
        supported_features=SensorFeatures.SET_SYSTEM_STATUS,
    ),
    _EnumSensorAddress(address=1006, name="status_smart_grid", enum=SmartGridStatus),
    _FloatSensorAddress(
        address=1008, name="temp_heat_storage", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1010, name="temp_cold_storage", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1012, name="temp_water_heater_bottom", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1014, name="temp_water_heater_top", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1030, name="temp_water_heater_tap", unit=UnitOfTemperature.CELSIUS
    ),
    _UCharSensorAddress(
        address=1032,
        name="temp_water_target",
        unit=UnitOfTemperature.CELSIUS,
        min_value=5,
        max_value=95,
    ),
    _UCharSensorAddress(
        address=1033,
        name="temp_water_switch_on",
        unit=UnitOfTemperature.CELSIUS,
        min_value=5,
        max_value=95,
    ),
    _UCharSensorAddress(
        address=1034,
        name="temp_water_switch_off",
        unit=UnitOfTemperature.CELSIUS,
        min_value=5,
        max_value=95,
    ),
    _FloatSensorAddress(
        address=1048, name="price_energy", unit=CURRENCY_EURO, scale=0.001
    ),
    _FloatSensorAddress(
        address=1050, name="temp_heat_pump_flow", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1052, name="temp_heat_pump_return", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1054, name="temp_hgl_flow", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1056, name="temp_heat_source_input", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1058, name="temp_heat_source_output", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1060, name="temp_air_input", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1062, name="temp_air_heat_exchanger", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1064, name="temp_air_input_2", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(address=1066, name="temp_charge_sensor"),
    _BitFieldSensorAddress(address=1090, name="status_heat_pump", flag=HeatPumpStatus),
    _UCharSensorAddress(address=1091, name="request_heating"),
    _UCharSensorAddress(address=1092, name="request_cooling"),
    _UCharSensorAddress(address=1093, name="request_water_status"),
    _UCharSensorAddress(address=1098, name="evu_lock_status"),
    _UCharSensorAddress(address=1099, name="failure_heat_pump"),
    _UCharSensorAddress(address=1100, name="state_compressor_1_uchar"),
    _UCharSensorAddress(address=1101, name="state_compressor_2_uchar"),
    _UCharSensorAddress(address=1102, name="state_compressor_3_uchar"),
    _UCharSensorAddress(address=1103, name="state_compressor_4_uchar"),
    _WordSensorAddress(
        address=1104, name="state_charge_pump", unit=None, min_value=-1, max_value=100
    ),
    _WordSensorAddress(
        address=1105, name="state_brine_pump", unit=None, min_value=-1, max_value=100
    ),
    _WordSensorAddress(
        address=1106,
        name="state_ground_water_pump",
        unit=None,
        min_value=-1,
        max_value=100,
    ),
    _WordSensorAddress(
        address=1108, name="load_isc_cold_storage_pump", unit=PERCENTAGE
    ),
    _WordSensorAddress(address=1109, name="load_isc_recooling_pump", unit=PERCENTAGE),
    _EnumSensorAddress(
        address=1110,
        name="valve_state_circuit_heating_cooling",
        enum=ValveStateHeatingCooling,
    ),
    _EnumSensorAddress(
        address=1111,
        name="valve_state_storage_heating_cooling",
        enum=ValveStateHeatingCooling,
    ),
    _EnumSensorAddress(
        address=1112, name="valve_state_main_heating_water", enum=ValveStateHeatingWater
    ),
    _EnumSensorAddress(
        address=1113,
        name="valve_state_source_heating_cooling",
        enum=ValveStateHeatingCooling,
    ),
    _EnumSensorAddress(
        address=1114,
        name="valve_state_solar_heating_water",
        enum=ValveStateHeatingWater,
    ),
    _EnumSensorAddress(
        address=1115,
        name="valve_state_solar_storage_source",
        enum=ValveStateStorageHeatSource,
    ),
    _EnumSensorAddress(
        address=1116,
        name="valve_state_isc_heating_cooling",
        enum=ValveStateHeatSourceColdStorage,
    ),
    _EnumSensorAddress(
        address=1117, name="valve_state_isc_bypass", enum=ValveStateStorageBypass
    ),
    _WordSensorAddress(address=1118, name="pump_circulation"),
    _WordSensorAddress(
        address=1120,
        name="temp_second_source_bivalence_1",
        unit=UnitOfTemperature.CELSIUS,
        min_value=-50,
        max_value=50,
    ),
    _WordSensorAddress(
        address=1121,
        name="temp_second_source_bivalence_2",
        unit=UnitOfTemperature.CELSIUS,
        min_value=-50,
        max_value=50,
    ),
    _WordSensorAddress(
        address=1122,
        name="temp_third_source_bivalence_1",
        unit=UnitOfTemperature.CELSIUS,
        min_value=-50,
        max_value=50,
    ),
    _WordSensorAddress(
        address=1123,
        name="temp_third_source_bivalence_2",
        unit=UnitOfTemperature.CELSIUS,
        min_value=-30,
        max_value=40,
    ),
    _UCharSensorAddress(address=1124, name="status_bivalence"),
    _UCharSensorAddress(address=1147, name="cascade_available_stages_heating"),
    _UCharSensorAddress(address=1148, name="cascade_available_stages_cooling"),
    _UCharSensorAddress(address=1149, name="cascade_available_stages_water"),
    _UCharSensorAddress(address=1150, name="cascade_running_stages_heating"),
    _UCharSensorAddress(address=1151, name="cascade_running_stages_cooling"),
    _UCharSensorAddress(address=1152, name="cascade_running_stages_water"),
    _FloatSensorAddress(
        address=1200,
        name="cascade_request_heating_temp",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _FloatSensorAddress(
        address=1202,
        name="cascade_request_cooling_temp",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _FloatSensorAddress(address=1204, name="cascade_temp_request_water"),
    _FloatSensorAddress(address=1206, name="cascade_temp_flow_avg_heating"),
    _FloatSensorAddress(address=1208, name="cascade_temp_flow_avg_cooling"),
    _FloatSensorAddress(address=1210, name="cascade_avg_flow_temp_c_water"),
    _UCharSensorAddress(
        address=1220,
        name="cascade_min_power_heating",
        unit=PERCENTAGE,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _UCharSensorAddress(
        address=1221,
        name="cascade_max_power_heating",
        unit=PERCENTAGE,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _UCharSensorAddress(
        address=1222,
        name="cascade_min_power_cooling",
        unit=PERCENTAGE,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _UCharSensorAddress(
        address=1223,
        name="cascade_max_power_cooling",
        unit=PERCENTAGE,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _UCharSensorAddress(
        address=1224,
        name="cascade_min_power_water",
        unit=PERCENTAGE,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _UCharSensorAddress(
        address=1225,
        name="cascade_max_power_water",
        unit=PERCENTAGE,
        supported_features=SensorFeatures.SET_POWER,
    ),
    _WordSensorAddress(
        address=1226,
        name="cascade_bivalence_heating_parallel",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _WordSensorAddress(
        address=1227,
        name="cascade_bivalence_heating_alternative",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _WordSensorAddress(
        address=1228,
        name="cascade_bivalence_cooling_parallel",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _WordSensorAddress(
        address=1229,
        name="cascade_bivalence_cooling_alternative",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _WordSensorAddress(
        address=1230,
        name="cascade_bivalence_water_parallel",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _WordSensorAddress(address=1231, name="cascade_bivalence_water_alternative"),
    _FloatSensorAddress(
        address=1392, name="humidity", unit=PERCENTAGE, min_value=0, max_value=100
    ),
    _FloatSensorAddress(
        address=1690,
        name="temp_external_outdoor",
        unit=UnitOfTemperature.CELSIUS,
        supported_features=SensorFeatures.SET_TEMPERATURE,
    ),
    _FloatSensorAddress(
        address=1692,
        name="temp_external_humidity",
        unit=PERCENTAGE,
        supported_features=SensorFeatures.SET_HUMIDITY,
        min_value=0,
        max_value=100,
    ),
    _UCharSensorAddress(
        address=1694,
        name="temp_external_request_heating",
        unit=UnitOfTemperature.CELSIUS,
        supported_features=SensorFeatures.SET_TEMPERATURE,
        min_value=-5,
        max_value=80,
    ),
    _UCharSensorAddress(
        address=1695,
        name="temp_external_request_cooling",
        unit=UnitOfTemperature.CELSIUS,
        supported_features=SensorFeatures.SET_TEMPERATURE,
        min_value=-5,
        max_value=80,
    ),
    _FloatSensorAddress(
        address=1696,
        name="temp_request_glt_heizen",
        unit=UnitOfTemperature.CELSIUS,
        supported_features=SensorFeatures.SET_TEMPERATURE,
    ),
    _FloatSensorAddress(
        address=1698,
        name="temp_request_glt_kuehlen_100",
        unit=UnitOfTemperature.CELSIUS,
        supported_features=SensorFeatures.SET_TEMPERATURE,
    ),
    _UCharSensorAddress(address=1714, name="request_pump_ground_water_external"),
    _UCharSensorAddress(address=1715, name="request_pump_ground_water_max_external"),
    _FloatSensorAddress(
        address=1716,
        name="temp_heat_storage_glt",
        supported_features=SensorFeatures.SET_TEMPERATURE,
    ),
    _FloatSensorAddress(
        address=1718,
        name="temp_cold_storage_glt",
        supported_features=SensorFeatures.SET_TEMPERATURE,
    ),
    _FloatSensorAddress(
        address=1720,
        name="temp_water_heater_bottom_target_glt",
        unit=UnitOfTemperature.CELSIUS,
        supported_features=SensorFeatures.SET_TEMPERATURE,
    ),
    _FloatSensorAddress(
        address=1722,
        name="temp_water_heater_top_target_glt",
        unit=UnitOfTemperature.CELSIUS,
    ),
    _FloatSensorAddress(
        address=1748,
        name="energy_heat_heating",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(
        address=1750,
        name="energy_heat_total",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(
        address=1752,
        name="energy_heat_total_cooling",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(
        address=1754,
        name="energy_heat_total_water",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(
        address=1756,
        name="energy_heat_total_defrost",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(
        address=1758,
        name="energy_heat_total_passive_cooling",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(
        address=1760,
        name="energy_heat_total_solar",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(
        address=1762,
        name="energy_heat_total_electric",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        min_value=0,
    ),
    _FloatSensorAddress(address=1790, name="power_current", unit=UnitOfPower.KILO_WATT),
    _FloatSensorAddress(
        address=1792, name="power_current_solar", unit=UnitOfPower.KILO_WATT
    ),
    _FloatSensorAddress(
        address=1850, name="temp_solar_collector", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1852, name="temp_solar_collector_return", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1854, name="temp_solar_charge", unit=UnitOfTemperature.CELSIUS
    ),
    _EnumSensorAddress(address=1856, name="mode_solar", enum=SolarMode),
    _FloatSensorAddress(
        address=1857, name="temp_solar_reference", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1870, name="temp_isc_charge_cooling", unit=UnitOfTemperature.CELSIUS
    ),
    _FloatSensorAddress(
        address=1872, name="temp_isc_recooling", unit=UnitOfTemperature.CELSIUS
    ),
    _BitFieldSensorAddress(address=1874, name="mode_isc", flag=IscMode),
    _UCharSensorAddress(
        address=1999,
        name="acknowledge_faults",
        supported_features=SensorFeatures.SET_BINARY,
        read_supported=False,
    ),
    _FloatSensorAddress(
        address=4122, name=NAME_POWER_USAGE, unit=UnitOfPower.KILO_WATT, min_value=0
    ),
    _FloatSensorAddress(address=4126, name="power_thermal", unit=UnitOfPower.KILO_WATT),
    _FloatSensorAddress(
        address=4128,
        name="energy_heat_total_flow_sensor",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
    ),
]

# Automatically add Circuit A by default for SENSOR_ADDRESSES, but allow customization in modbus.py
# ModbusClient will rebuild its own sensor list, but we keep SENSOR_ADDRESSES populated with defaults
# so other parts of the code (like tests) still have something to work with.
SENSOR_LIST = list(COMMON_SENSORS)
SENSOR_LIST.extend(heating_circuit_sensors(HeatingCircuit.A))

# We do NOT add other circuits or zones here automatically anymore.

SENSOR_ADDRESSES: dict[str, IdmSensorAddress] = {s.name: s for s in SENSOR_LIST}


BINARY_SENSOR_ADDRESSES: dict[str, IdmBinarySensorAddress] = {
    sensor.name: sensor
    for sensor in [
        IdmBinarySensorAddress(
            address=1099,
            name="failure_heat_pump",
        ),
        IdmBinarySensorAddress(
            address=1100,
            name="state_compressor_1",
        ),
        IdmBinarySensorAddress(
            address=1101,
            name="state_compressor_2",
        ),
        IdmBinarySensorAddress(
            address=1102,
            name="state_compressor_3",
        ),
        IdmBinarySensorAddress(
            address=1103,
            name="state_compressor_4",
        ),
        IdmBinarySensorAddress(
            address=1710,
            name="request_heating",
            supported_features=SensorFeatures.SET_BINARY,
        ),
        IdmBinarySensorAddress(
            address=1711,
            name="request_cooling",
            supported_features=SensorFeatures.SET_BINARY,
        ),
        IdmBinarySensorAddress(
            address=1712,
            name="request_water",
            supported_features=SensorFeatures.SET_BINARY,
        ),
        IdmBinarySensorAddress(
            address=1713,
            name="request_water_once",
            supported_features=SensorFeatures.SET_BINARY,
        ),
    ]
}
