# SPDX-License-Identifier: MIT
"""
Luxtronik 2.1 Heat Pump Driver (TCP).
Used by Bosch, Alpha Innotec, Novelan, etc.
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
    PROTOCOL = "Luxtronik TCP"
    DEFAULT_PORT = 8889

    # Luxtronik verwendet Port 8889 und ein binäres Protokoll
    # Es gibt keine Register-Adressen wie bei Modbus, sondern Parameter-Indizes
    # Wir mappen diese Indizes auf Sensor-IDs

    # PARAMETER IDs are typically > 0
    # CALCULATIONS are typically 3000 series (mapped internally)

    # Simplified mapping for demonstration
    # In reality, Luxtronik needs a custom client implementation, but we can simulate
    # it via HeatpumpManager if we create a special ModbusClient wrapper or modify HeatpumpManager.
    # For now, we define the structure.

    PARAMETERS = {
        "temp_outside": {
            "index": 10,
            "type": "temperature",
            "category": SensorCategory.TEMPERATURE,
            "name": "Außentemperatur",
        },
        "temp_outside_avg": {
            "index": 11,
            "type": "temperature",
            "category": SensorCategory.TEMPERATURE,
            "name": "Außentemperatur Mittel",
        },
        "temp_hot_water": {
            "index": 17,
            "type": "temperature",
            "category": SensorCategory.TEMPERATURE,
            "name": "Warmwasser Ist",
        },
        "temp_hot_water_target": {
            "index": 18,
            "type": "temperature",
            "category": SensorCategory.CONTROL,
            "name": "Warmwasser Soll",
        },
        "temp_flow": {
            "index": 10,
            "type": "temperature",
            "category": SensorCategory.TEMPERATURE,
            "name": "Vorlauf",
        },  # Check ID
        "temp_return": {
            "index": 11,
            "type": "temperature",
            "category": SensorCategory.TEMPERATURE,
            "name": "Rücklauf",
        },  # Check ID
        "temp_source_in": {
            "index": 19,
            "type": "temperature",
            "category": SensorCategory.TEMPERATURE,
            "name": "Wärmequelle Ein",
        },
        "temp_source_out": {
            "index": 20,
            "type": "temperature",
            "category": SensorCategory.TEMPERATURE,
            "name": "Wärmequelle Aus",
        },
        "compressor_output": {
            "index": 257,
            "type": "percent",
            "category": SensorCategory.STATUS,
            "name": "Verdichter Leistung",
        },
        "heat_quantity_heating": {
            "index": 151,
            "type": "energy",
            "category": SensorCategory.ENERGY,
            "name": "Wärmemenge Heizen",
        },
        "heat_quantity_hot_water": {
            "index": 152,
            "type": "energy",
            "category": SensorCategory.ENERGY,
            "name": "Wärmemenge WW",
        },
    }

    def get_sensors(self, config: Dict[str, Any]) -> List[SensorDefinition]:
        sensors = []
        for sensor_id, info in self.PARAMETERS.items():
            sensors.append(
                SensorDefinition(
                    id=sensor_id,
                    name=info["name"],
                    name_de=info["name"],
                    category=info["category"],
                    unit="°C"
                    if info["type"] == "temperature"
                    else ("kWh" if info["type"] == "energy" else ""),
                    address=info["index"],
                    datatype=DataType.INT32,  # Luxtronik sends 32-bit ints (often scaled by 10)
                    access=AccessMode.READ_ONLY,
                    scale=0.1 if info["type"] == "temperature" else 1.0,
                )
            )
        return sensors

    def get_capabilities(self) -> HeatpumpCapabilities:
        return HeatpumpCapabilities(
            heating=True,
            cooling=True,
            hot_water=True,
            solar_integration=True,
            smart_grid=False,
            max_circuits=3,
            max_zones=3,
        )

    # Luxtronik is NOT Modbus.
    # HeatpumpManager expects ModbusTcpClient.
    # To support this, we would need to implement a LuxtronikClient adapter that mimics pymodbus.
    # Or flag this driver as requiring a custom client.

    # For now, we implement parse_value assuming raw_bytes come from our adapter

    def parse_value(self, sensor: SensorDefinition, raw_bytes: List[int]) -> Any:
        if not raw_bytes:
            return None
        # Assuming raw_bytes is [value] from our custom reader
        return raw_bytes[0] * sensor.scale

    def encode_value(self, sensor: SensorDefinition, value: Any) -> List[int]:
        return [int(value / sensor.scale)]

    def get_dashboard_template(self) -> Dict[str, Any]:
        return {
            "name": "Luxtronik Dashboard",
            "charts": [
                {
                    "title": "Temperaturen",
                    "type": "line",
                    "queries": [
                        {"label": "Außen", "query": "temp_outside", "color": "#3b82f6"},
                        {
                            "label": "Quelle Ein",
                            "query": "temp_source_in",
                            "color": "#10b981",
                        },
                        {
                            "label": "Quelle Aus",
                            "query": "temp_source_out",
                            "color": "#f59e0b",
                        },
                    ],
                    "hours": 24,
                }
            ],
        }

    def get_setup_instructions(self) -> str:
        return """
        Luxtronik 2.1 Setup:
        1. IP-Adresse der Wärmepumpe ermitteln.
        2. Standard-Port ist 8889.
        3. Hinweis: Aktuell wird nur das Lesen von Temperaturen unterstützt (Alpha).
        """
