# SPDX-License-Identifier: MIT
"""
NIBE S-Series Heat Pump Driver (Modbus TCP).

Supports NIBE S1155, S1255, S2125, etc.
"""

from typing import List, Dict, Any

from ..base import (
    HeatpumpDriver,
    SensorDefinition,
    SensorCategory,
    DataType,
    AccessMode,
    HeatpumpCapabilities,
)
from .. import ManufacturerRegistry


@ManufacturerRegistry.register
class NIBESSeriesDriver(HeatpumpDriver):
    MANUFACTURER = "nibe"
    MODEL = "s_series"
    DISPLAY_NAME = "NIBE S-Series (S1155, S1255, S2125)"
    PROTOCOL = "Modbus TCP"
    DEFAULT_PORT = 502

    # NIBE Modbus Register Map
    # Based on official Modbus list for S-Series
    REGISTER_MAP = {
        # Temperatures
        "temp_outside": {
            "address": 40004,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Außentemperatur",
        },
        "temp_hot_water_top": {
            "address": 40013,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Warmwasser Oben",
        },
        "temp_hot_water_charging": {
            "address": 40014,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Warmwasser Ladung",
        },
        "temp_brine_in": {
            "address": 40015,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Sole Ein",
        },
        "temp_brine_out": {
            "address": 40016,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Sole Aus",
        },
        "temp_condenser": {
            "address": 40017,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Kondensator",
        },
        "temp_discharge": {
            "address": 40018,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Heißgas",
        },
        "temp_suction": {
            "address": 40019,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Sauggas",
        },
        "temp_supply_line": {
            "address": 40008,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Vorlauf",
        },
        "temp_return_line": {
            "address": 40012,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Rücklauf",
        },
        # System Status
        "compressor_frequency": {
            "address": 43136,
            "datatype": DataType.UINT16,
            "scale": 0.1,
            "category": SensorCategory.STATUS,
            "name": "Verdichter Frequenz",
            "unit": "Hz",
        },
        "compressor_starts": {
            "address": 43416,
            "datatype": DataType.UINT32,
            "scale": 1,
            "category": SensorCategory.STATUS,
            "name": "Verdichter Starts",
            "unit": "",
        },
        "compressor_hours": {
            "address": 43420,
            "datatype": DataType.UINT32,
            "scale": 1,
            "category": SensorCategory.STATUS,
            "name": "Verdichter Stunden",
            "unit": "h",
        },
        "current_power": {
            "address": 43084,
            "datatype": DataType.UINT16,
            "scale": 0.01,
            "category": SensorCategory.POWER,
            "name": "Momentanleistung",
            "unit": "kW",
        },
        "energy_produced_heating": {
            "address": 44298,
            "datatype": DataType.UINT32,
            "scale": 0.1,
            "category": SensorCategory.ENERGY,
            "name": "Energie Heizen",
            "unit": "kWh",
        },
        "energy_produced_hot_water": {
            "address": 44300,
            "datatype": DataType.UINT32,
            "scale": 0.1,
            "category": SensorCategory.ENERGY,
            "name": "Energie Warmwasser",
            "unit": "kWh",
        },
        # Settings / Control
        "heating_curve": {
            "address": 47007,
            "datatype": DataType.INT16,
            "scale": 1,
            "category": SensorCategory.CONTROL,
            "name": "Heizkurve",
            "unit": "",
            "access": AccessMode.READ_WRITE,
        },
        "hot_water_start_temp": {
            "address": 47041,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.CONTROL,
            "name": "WW Starttemperatur",
            "unit": "°C",
            "access": AccessMode.READ_WRITE,
        },
        "hot_water_stop_temp": {
            "address": 47043,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.CONTROL,
            "name": "WW Stopptemperatur",
            "unit": "°C",
            "access": AccessMode.READ_WRITE,
        },
        "operating_mode": {
            "address": 47137,
            "datatype": DataType.UINT8,
            "scale": 1,
            "category": SensorCategory.STATUS,
            "name": "Betriebsmodus",
            "unit": "",
            "access": AccessMode.READ_WRITE,
        },
        "degree_minutes": {
            "address": 43005,
            "datatype": DataType.INT16,
            "scale": 1,
            "category": SensorCategory.CONTROL,
            "name": "Gradminuten",
            "unit": "GM",
        },
    }

    def get_sensors(self, config: Dict[str, Any]) -> List[SensorDefinition]:
        sensors = []
        for sensor_id, reg_info in self.REGISTER_MAP.items():
            access = reg_info.get("access", AccessMode.READ_ONLY)
            # Override access if defined in reg_info

            sensors.append(
                SensorDefinition(
                    id=sensor_id,
                    name=reg_info["name"],
                    name_de=reg_info["name"],
                    category=reg_info["category"],
                    unit=reg_info.get(
                        "unit",
                        "°C"
                        if reg_info["category"] == SensorCategory.TEMPERATURE
                        else "",
                    ),
                    address=reg_info["address"],
                    datatype=reg_info["datatype"],
                    access=access,
                    scale=reg_info["scale"],
                )
            )
        return sensors

    def get_capabilities(self) -> HeatpumpCapabilities:
        return HeatpumpCapabilities(
            heating=True,
            cooling=True,
            hot_water=True,
            solar_integration=False,
            smart_grid=True,
            max_circuits=4,
            max_zones=4,
        )

    def parse_value(self, sensor: SensorDefinition, raw_bytes: List[int]) -> Any:
        # NIBE uses Big-Endian
        # pymodbus returns list of 16-bit integers (registers)
        # raw_bytes argument is actually List[int] from HeatpumpManager

        if not raw_bytes:
            return None

        value = 0

        if sensor.datatype == DataType.INT16:
            # Signed 16-bit
            val = raw_bytes[0]
            # Convert unsigned 16-bit to signed 16-bit
            if val > 32767:
                val -= 65536
            value = val

        elif sensor.datatype == DataType.UINT16:
            value = raw_bytes[0]

        elif sensor.datatype == DataType.UINT32:
            # 32-bit unsigned (2 registers)
            # Big-endian: High word first? usually.
            # Modbus standard is usually Big-Endian registers.
            # Let's assume High Word First (Big Endian)
            if len(raw_bytes) >= 2:
                high = raw_bytes[0]
                low = raw_bytes[1]
                value = (high << 16) | low
            else:
                return None

        elif sensor.datatype == DataType.INT32:
            if len(raw_bytes) >= 2:
                high = raw_bytes[0]
                low = raw_bytes[1]
                val = (high << 16) | low
                if val > 2147483647:
                    val -= 4294967296
                value = val
            else:
                return None

        elif sensor.datatype == DataType.UINT8:
            # Often packed in low byte
            value = raw_bytes[0] & 0xFF

        else:
            value = raw_bytes[0]

        return round(value * sensor.scale, 2)

    def encode_value(self, sensor: SensorDefinition, value: Any) -> List[int]:
        # Inverse of parse_value
        raw_val = int(value / sensor.scale)

        if sensor.datatype in [DataType.INT16, DataType.UINT16]:
            # Clamp to 16-bit
            if sensor.datatype == DataType.INT16:
                if raw_val < -32768:
                    raw_val = -32768
                if raw_val > 32767:
                    raw_val = 32767
                if raw_val < 0:
                    raw_val += 65536
            return [raw_val & 0xFFFF]

        elif sensor.datatype in [DataType.INT32, DataType.UINT32]:
            high = (raw_val >> 16) & 0xFFFF
            low = raw_val & 0xFFFF
            return [high, low]

        return [int(value)]

    def get_dashboard_template(self) -> Dict[str, Any]:
        return {
            "name": "NIBE Dashboard",
            "charts": [
                {
                    "title": "Temperaturen",
                    "type": "line",
                    "queries": [
                        {"label": "Außen", "query": "temp_outside", "color": "#3b82f6"},
                        {
                            "label": "Vorlauf",
                            "query": "temp_supply_line",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Rücklauf",
                            "query": "temp_return_line",
                            "color": "#f59e0b",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "title": "Warmwasser",
                    "type": "line",
                    "queries": [
                        {
                            "label": "WW Oben",
                            "query": "temp_hot_water_top",
                            "color": "#ec4899",
                        },
                        {
                            "label": "WW Ladung",
                            "query": "temp_hot_water_charging",
                            "color": "#8b5cf6",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "title": "Leistung",
                    "type": "line",
                    "queries": [
                        {
                            "label": "Verdichter Freq.",
                            "query": "compressor_frequency",
                            "color": "#10b981",
                        },
                        {
                            "label": "Leistung",
                            "query": "current_power",
                            "color": "#f97316",
                        },
                    ],
                    "hours": 24,
                },
            ],
        }

    def get_setup_instructions(self) -> str:
        return """
        NIBE S-Serie Setup:
        1. Modbus TCP in den Einstellungen aktivieren (Menü 5.2.3).
        2. Port ist standardmäßig 502.
        3. Unit-ID ist standardmäßig 1.
        4. Sicherstellen, dass "Modbus TCP/IP" auf "Ein" steht.
        """
