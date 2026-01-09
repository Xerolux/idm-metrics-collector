import logging
from pymodbus.client import ModbusTcpClient

from .config import config
from .sensor_addresses import SENSOR_ADDRESSES, BINARY_SENSOR_ADDRESSES, heating_circuit_sensors, HeatingCircuit, SensorFeatures

logger = logging.getLogger(__name__)

class ModbusClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(host, port=port)
        self.sensors = SENSOR_ADDRESSES.copy()
        self.binary_sensors = BINARY_SENSOR_ADDRESSES.copy()

        # Add configured heating circuits
        circuits = config.get("idm.circuits", [])
        for c_name in circuits:
            try:
                c_enum = HeatingCircuit[c_name.upper()]
                c_sensors = heating_circuit_sensors(c_enum)
                for s in c_sensors:
                    self.sensors[s.name] = s
            except KeyError:
                logger.warning(f"Invalid heating circuit configured: {c_name}")


    def connect(self):
        return self.client.connect()

    def close(self):
        self.client.close()

    def read_sensors(self):
        data = {}
        if not self.connect():
            logger.error("Could not connect to Modbus server")
            return data

        # Reading sensors
        for name, sensor in self.sensors.items():
            try:
                # Pymodbus 3.x API: read_holding_registers(address, count=1, slave=1)
                # Note: `unit` was renamed to `slave` in 3.0, and `device_id` might be used in some contexts but `slave` is common.
                # Actually, check what ModbusTcpClient uses.
                # In 3.8, it uses `slave`.
                rr = self.client.read_holding_registers(sensor.address, count=sensor.size, slave=1)
                if rr.isError():
                    logger.warning(f"Error reading {name} at {sensor.address}: {rr}")
                    continue

                success, value = sensor.decode(rr.registers)
                if success:
                    # Handle Enums and Flags by converting to int or str
                    if hasattr(value, "value"):
                        data[name] = value.value
                        data[f"{name}_str"] = str(value)
                    else:
                        data[name] = value
                else:
                    logger.debug(f"Sensor {name} unavailable/invalid")

            except Exception as e:
                logger.error(f"Exception reading {name}: {e}")

        # Reading binary sensors
        for name, sensor in self.binary_sensors.items():
            try:
                rr = self.client.read_holding_registers(sensor.address, count=sensor.size, slave=1)
                if rr.isError():
                    logger.warning(f"Error reading binary {name} at {sensor.address}: {rr}")
                    continue

                success, value = sensor.decode(rr.registers)
                if success:
                    data[name] = value

            except Exception as e:
                logger.error(f"Exception reading binary {name}: {e}")

        return data

    def write_sensor(self, name, value):
        if name not in self.sensors and name not in self.binary_sensors:
            raise ValueError(f"Sensor {name} not found")

        sensor = self.sensors.get(name) or self.binary_sensors.get(name)

        if sensor.supported_features == SensorFeatures.NONE:
            raise ValueError(f"Sensor {name} is read-only")

        # Convert value based on type

        try:
             # If it's a binary sensor, expect bool or 0/1
            if isinstance(sensor, type(BINARY_SENSOR_ADDRESSES.get("request_heating"))): # simplistic check
                 value = bool(int(value) if str(value).isdigit() else value == 'true')

            # If it's a float sensor
            elif hasattr(sensor, "scale"):
                 value = float(value)

            # If it's an enum, we might need the Enum member or value.
            # The encode method of _EnumSensorAddress calls value.value.
            # So we need to pass an Enum member.
            elif hasattr(sensor, "enum"):
                 # value could be the int value or the name
                 if str(value).isdigit():
                      value = sensor.enum(int(value))
                 else:
                      value = sensor.enum[value] # access by name

            # If it's UChar/Word
            else:
                 value = int(value)

            registers = sensor.encode(value)
        except Exception as e:
            logger.error(f"Encoding error for {name}: {e}")
            raise ValueError(f"Invalid value for {name}: {e}")

        if not self.connect():
             raise IOError("Could not connect to Modbus")

        # Write
        try:
            # Pymodbus 3.x API: write_registers(address, values, slave=1)
            rr = self.client.write_registers(sensor.address, registers, slave=1)
            if rr.isError():
                 raise IOError(f"Modbus write error: {rr}")
        except Exception as e:
             logger.error(f"Write failed: {e}")
             raise

        return True
