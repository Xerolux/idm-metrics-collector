"""Sensor addresses."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, IntEnum, IntFlag
from typing import Generic, TypeVar, Any
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian

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


@dataclass(kw_only=True)
class BaseSensorAddress(ABC, Generic[_T]):
    """Base class for (binary) sensors of an IDM heatpump."""

    address: int
    name: str
    supported_features: SensorFeatures = SensorFeatures.NONE
    force_single: bool = False
    unit: str | None = None

    @property
    def size(self) -> int:
        """Get number of registers this sensor's value occupies."""
        # 32bit types use 2 registers, 16bit use 1
        if self.datatype in ('float32', 'int32', 'uint32'):
            return 2
        return 1

    @property
    @abstractmethod
    def datatype(self) -> str:
        """Get the datatype name."""

    def _decode_raw(self, registers: list[int]):
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers,
            byteorder=Endian.Big,
            wordorder=Endian.Little
        )

        if self.datatype == 'float32':
            return decoder.decode_32bit_float()
        elif self.datatype == 'int16':
            return decoder.decode_16bit_int()
        elif self.datatype == 'uint16':
            return decoder.decode_16bit_uint()
        elif self.datatype == 'int32':
            return decoder.decode_32bit_int()
        elif self.datatype == 'uint32':
            return decoder.decode_32bit_uint()
        return registers[0]

    def _encode_raw(self, value: int | float) -> list[int]:
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)

        if self.datatype == 'float32':
            builder.add_32bit_float(float(value))
        elif self.datatype == 'int16':
            builder.add_16bit_int(int(value))
        elif self.datatype == 'uint16':
            builder.add_16bit_uint(int(value))
        elif self.datatype == 'int32':
            builder.add_32bit_int(int(value))
        elif self.datatype == 'uint32':
            builder.add_32bit_uint(int(value))

        return builder.to_registers()

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
        return 'uint16'

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
        return 'float32'

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
        return 'uint16'

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
        return 'int16'

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
        return 'uint16'

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
        return 'uint16'

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

ZONE_OFFSETS = [2000 + 65 * i for i in range(10)]
ROOM_OFFSETS = [2 + 7 * i for i in range(8)]

SENSOR_ADDRESSES: dict[str, IdmSensorAddress] = {
    s.name: s
    for s in [
        _FloatSensorAddress(
            address=74,
            name="power_solar_surplus",
            unit=UnitOfPower.KILO_WATT,
            supported_features=SensorFeatures.SET_POWER,
        ),
        _FloatSensorAddress(
            address=76,
            name="power_resistive_heater",
            unit=UnitOfPower.KILO_WATT,
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
            address=1000,
            name="temp_outside",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1002,
            name="temp_outside_avg",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _UCharSensorAddress(
            address=1004,
            name="failure_id",
            unit=None,
        ),
        _EnumSensorAddress(
            enum=SystemStatus,
            address=1005,
            name="status_system",
            supported_features=SensorFeatures.SET_SYSTEM_STATUS,
        ),
        _EnumSensorAddress(
            enum=SmartGridStatus,
            address=1006,
            name="status_smart_grid",
        ),
        _FloatSensorAddress(
            address=1008,
            name="temp_heat_storage",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1010,
            name="temp_cold_storage",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1012,
            name="temp_water_heater_top",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1014,
            name="temp_water_heater_bottom",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1030,
            name="temp_water_heater_tap",
            unit=UnitOfTemperature.CELSIUS,
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
            address=1048,
            name="price_energy",
            unit=CURRENCY_EURO,
            scale=0.001,
        ),
        _FloatSensorAddress(
            address=1050,
            name="temp_heat_pump_flow",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1052,
            name="temp_heat_pump_return",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1054,
            name="temp_hgl_flow",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1056,
            name="temp_heat_source_input",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1058,
            name="temp_heat_source_output",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1060,
            name="temp_air_input",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1062,
            name="temp_air_heat_exchanger",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1064,
            name="temp_air_input_2",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1066,
            name="temp_charge_sensor",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _BitFieldSensorAddress(
            flag=HeatPumpStatus,
            address=1090,
            name="status_heat_pump",
        ),
        _UCharSensorAddress(
            address=1091,
            name="request_heating_status",
        ),
        _UCharSensorAddress(
            address=1092,
            name="request_cooling_status",
        ),
        _UCharSensorAddress(
            address=1093,
            name="request_water_status",
        ),
        _UCharSensorAddress(
            address=1098,
            name="evu_lock_status",
        ),
        _WordSensorAddress(
            address=1104,
            name="state_charge_pump",
            unit=None,
            min_value=-1,
            max_value=100,
        ),
        _WordSensorAddress(
            address=1105,
            name="state_brine_pump",
            unit=None,
            min_value=-1,
            max_value=100,
        ),
        _WordSensorAddress(
            address=1106,
            name="state_ground_water_pump",
            unit=None,
            min_value=-1,
            max_value=100,
        ),
        _WordSensorAddress(
            address=1108,
            name="load_isc_cold_storage_pump",
            unit=PERCENTAGE,
            min_value=0,
            max_value=100,
        ),
        _WordSensorAddress(
            address=1109,
            name="load_isc_recooling_pump",
            unit=PERCENTAGE,
            min_value=0,
            max_value=100,
        ),
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
            address=1112,
            name="valve_state_main_heating_water",
            enum=ValveStateHeatingWater,
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
            address=1117,
            name="valve_state_isc_bypass",
            enum=ValveStateStorageBypass,
        ),
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
        # Cascade Parameters 1147-1231
        _UCharSensorAddress(address=1147, name="cascade_stages_available_heating"),
        _UCharSensorAddress(address=1148, name="cascade_stages_available_cooling"),
        _UCharSensorAddress(address=1149, name="cascade_stages_available_water"),
        _UCharSensorAddress(
            address=1150,
            name="count_running_compressor_stages_heating",
            unit=None,
        ),
        _UCharSensorAddress(
            address=1151,
            name="count_running_compressor_stages_cooling",
            unit=None,
        ),
        _UCharSensorAddress(
            address=1152,
            name="count_running_compressor_stages_water",
            unit=None,
        ),
        _FloatSensorAddress(address=1200, name="cascade_requested_temp_heating", unit=UnitOfTemperature.CELSIUS),
        _FloatSensorAddress(address=1202, name="cascade_requested_temp_cooling", unit=UnitOfTemperature.CELSIUS),
        _FloatSensorAddress(address=1204, name="cascade_requested_temp_water", unit=UnitOfTemperature.CELSIUS),
        _FloatSensorAddress(address=1206, name="cascade_avg_flow_temp_heating", unit=UnitOfTemperature.CELSIUS),
        _FloatSensorAddress(address=1208, name="cascade_avg_flow_temp_cooling", unit=UnitOfTemperature.CELSIUS),
        _FloatSensorAddress(address=1210, name="cascade_avg_flow_temp_water", unit=UnitOfTemperature.CELSIUS),

        _FloatSensorAddress(
            address=1392,
            name="humidity",
            unit=PERCENTAGE,
            min_value=0,
            max_value=100,
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
        _FloatSensorAddress(
            address=1790,
            name="power_current",
            unit=UnitOfPower.KILO_WATT,
        ),
        _FloatSensorAddress(
            address=1792,
            name="power_current_solar",
            unit=UnitOfPower.KILO_WATT,
        ),
        _FloatSensorAddress(
            address=1850,
            name="temp_solar_collector",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1852,
            name="temp_solar_collector_return",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1854,
            name="temp_solar_charge",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _EnumSensorAddress(
            enum=SolarMode,
            address=1856,
            name="mode_solar",
        ),
        _FloatSensorAddress(
            address=1857,
            name="temp_solar_reference",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1870,
            name="temp_isc_charge_cooling",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _FloatSensorAddress(
            address=1872,
            name="temp_isc_recooling",
            unit=UnitOfTemperature.CELSIUS,
        ),
        _BitFieldSensorAddress(
            flag=IscMode,
            address=1874,
            name="mode_isc",
        ),
        _UCharSensorAddress(address=1999, name="acknowledge_faults", supported_features=SensorFeatures.SET_BINARY),

        _FloatSensorAddress(
            address=4122,
            name=NAME_POWER_USAGE,
            unit=UnitOfPower.KILO_WATT,
            min_value=0,
        ),
    ]
}


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
