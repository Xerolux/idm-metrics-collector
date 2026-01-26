# SPDX-License-Identifier: MIT
"""
Daikin Altherma Heat Pump Driver.
Requires Daikin Home Hub (EKRHH) in Modbus TCP mode.
"""

from typing import List, Dict, Any, Optional

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
class DaikinAlthermaDriver(HeatpumpDriver):
    """
    Daikin Altherma - benötigt HomeHub (EKRHH) in Mode 3
    Modbus TCP über Port 502
    """

    MANUFACTURER = "daikin"
    MODEL = "altherma"
    DISPLAY_NAME = "Daikin Altherma (via HomeHub)"
    PROTOCOL = "Modbus TCP"
    DEFAULT_PORT = 502

    # Daikin Modbus Register (basierend auf EKMBDXB7V1 Spezifikation)
    REGISTER_MAP = {
        "temp_outside": {
            "address": 3,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Außentemperatur",
        },
        "temp_leaving_water": {
            "address": 4,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Vorlauf",
        },
        "temp_return_water": {
            "address": 5,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Rücklauf",
        },
        "temp_hot_water": {
            "address": 6,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Warmwasser",
        },
        "temp_refrigerant": {
            "address": 7,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "category": SensorCategory.TEMPERATURE,
            "name": "Kältemittel",
        },
        "operation_mode": {
            "address": 0,
            "datatype": DataType.UINT16,
            "scale": 1,
            "category": SensorCategory.STATUS,
            "name": "Betriebsmodus",
        },
        "target_temp_heating": {
            "address": 30,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "access": AccessMode.READ_WRITE,
            "category": SensorCategory.CONTROL,
            "name": "Sollwert Heizen",
        },
        "target_temp_hot_water": {
            "address": 31,
            "datatype": DataType.INT16,
            "scale": 0.1,
            "access": AccessMode.READ_WRITE,
            "category": SensorCategory.CONTROL,
            "name": "Sollwert WW",
        },
        "compressor_status": {
            "address": 20,
            "datatype": DataType.UINT16,
            "scale": 1,
            "category": SensorCategory.STATUS,
            "name": "Verdichter Status",
        },
        "defrost_status": {
            "address": 21,
            "datatype": DataType.UINT16,
            "scale": 1,
            "category": SensorCategory.STATUS,
            "name": "Abtau Status",
        },
        "error_code": {
            "address": 50,
            "datatype": DataType.UINT16,
            "scale": 1,
            "category": SensorCategory.STATUS,
            "name": "Fehlercode",
        },
    }

    def get_sensors(self, config: Dict[str, Any]) -> List[SensorDefinition]:
        sensors = []
        for sensor_id, reg_info in self.REGISTER_MAP.items():
            access = reg_info.get("access", AccessMode.READ_ONLY)

            sensors.append(
                SensorDefinition(
                    id=sensor_id,
                    name=reg_info["name"],
                    name_de=reg_info["name"],
                    category=reg_info["category"],
                    unit="°C"
                    if reg_info["category"] == SensorCategory.TEMPERATURE
                    else "",
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
            max_circuits=2,
            max_zones=2,
        )

    def parse_value(self, sensor: SensorDefinition, raw_bytes: List[int]) -> Any:
        if not raw_bytes:
            return None

        value = 0
        if sensor.datatype == DataType.INT16:
            val = raw_bytes[0]
            if val > 32767:
                val -= 65536
            value = val
        else:
            value = raw_bytes[0]

        return round(value * sensor.scale, 2)

    def encode_value(self, sensor: SensorDefinition, value: Any) -> List[int]:
        raw_val = int(value / sensor.scale)
        if raw_val < -32768:
            raw_val = -32768
        if raw_val > 32767:
            raw_val = 32767
        if raw_val < 0:
            raw_val += 65536
        return [raw_val & 0xFFFF]

    def get_dashboard_template(self) -> Dict[str, Any]:
        return {
            "name": "Daikin Dashboard",
            "charts": [
                {
                    "title": "Temperaturen",
                    "type": "line",
                    "queries": [
                        {"label": "Außen", "query": "temp_outside", "color": "#3b82f6"},
                        {
                            "label": "Vorlauf",
                            "query": "temp_leaving_water",
                            "color": "#ef4444",
                        },
                        {
                            "label": "Rücklauf",
                            "query": "temp_return_water",
                            "color": "#f59e0b",
                        },
                    ],
                    "hours": 24,
                },
                {
                    "title": "Warmwasser",
                    "type": "line",
                    "queries": [
                        {"label": "Ist", "query": "temp_hot_water", "color": "#ec4899"},
                        {
                            "label": "Soll",
                            "query": "target_temp_hot_water",
                            "color": "#8b5cf6",
                        },
                    ],
                    "hours": 24,
                },
            ],
        }

    def get_setup_instructions(self) -> str:
        return """
        Daikin Altherma Setup:
        1. HomeHub (EKRHH) erforderlich.
        2. HomeHub in Mode 3 (Modbus TCP/IP) konfigurieren.
        3. IP-Adresse des HomeHub im Netzwerk ermitteln.
        4. Standard-Port: 502.
        """
