import logging
from pymodbus.client import ModbusTcpClient

from .config import config
from .sensor_addresses import (
    BINARY_SENSOR_ADDRESSES,
    COMMON_SENSORS,
    heating_circuit_sensors,
    zone_sensors,
    HeatingCircuit,
    SensorFeatures,
)

logger = logging.getLogger(__name__)


class ModbusClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(host, port=port, timeout=10, retries=3)

        # Initialize with common sensors
        self.sensors = {s.name: s for s in COMMON_SENSORS}
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

        # Add configured zones
        zones = config.get("idm.zones", [])
        for zone_id in zones:
            try:
                z_sensors = zone_sensors(int(zone_id))
                for s in z_sensors:
                    self.sensors[s.name] = s
            except Exception as e:
                logger.warning(f"Invalid zone configured: {zone_id} ({e})")

    def connect(self):
        """Connects to the Modbus server."""
        if self.client.is_socket_open():
            return True
        logger.info(f"Connecting to Modbus server at {self.host}:{self.port}")
        return self.client.connect()

    def close(self):
        """Closes the Modbus connection."""
        if self.client.is_socket_open():
            logger.info("Closing Modbus connection")
            self.client.close()

    def _ensure_connection(self):
        """Ensures the client is connected, reconnecting if necessary."""
        if self.client.is_socket_open():
            return True
        logger.warning("Modbus connection lost. Attempting to reconnect...")
        return self.connect()

    def _build_read_blocks(self):
        """Groups sensors into contiguous blocks for optimized reading."""
        # Combine all read-supported sensors
        all_sensors = []
        for s in list(self.sensors.values()) + list(self.binary_sensors.values()):
            if s.read_supported:
                all_sensors.append(s)

        # Sort by address
        all_sensors.sort(key=lambda s: s.address)

        blocks = []
        if not all_sensors:
            return blocks

        current_block = [all_sensors[0]]

        # Max registers to read in one request (conservative for IDM heat pumps)
        MAX_BLOCK_SIZE = 50

        # Max gap size to bridge (reading useless data is cheaper than new request)
        MAX_GAP = 5

        # Addresses that MUST NOT be read (read_supported=False)
        forbidden_addresses = set()
        for s in list(self.sensors.values()) + list(self.binary_sensors.values()):
            if not s.read_supported:
                # Mark all registers occupied by this sensor as forbidden
                for i in range(s.size):
                    forbidden_addresses.add(s.address + i)

        for i in range(1, len(all_sensors)):
            sensor = all_sensors[i]
            prev_sensor = current_block[-1]

            # Calculate end of previous sensor
            prev_end = prev_sensor.address + prev_sensor.size

            # Calculate gap
            gap = sensor.address - prev_end

            # Check if we should extend the block
            should_extend = True

            # 1. Check max block size
            # Current block size + gap + new sensor size
            new_block_size = (sensor.address + sensor.size) - current_block[0].address
            if new_block_size > MAX_BLOCK_SIZE:
                should_extend = False

            # 2. Check max gap
            if gap > MAX_GAP:
                should_extend = False

            # 3. Check for forbidden addresses in the gap
            if should_extend and gap > 0:
                for addr in range(prev_end, sensor.address):
                    if addr in forbidden_addresses:
                        should_extend = False
                        break

            if should_extend:
                current_block.append(sensor)
            else:
                blocks.append(current_block)
                current_block = [sensor]

        if current_block:
            blocks.append(current_block)

        return blocks

    def read_sensors(self):
        data = {}
        if not self._ensure_connection():
            logger.error("Could not connect to Modbus server")
            return data

        try:
            # Build blocks if not already done (could be cached if sensors don't change)
            # For now we rebuild since sensors can be added dynamically? No, they are set in __init__
            # But let's cache it for performance
            if not hasattr(self, "_read_blocks"):
                self._read_blocks = self._build_read_blocks()
                self._failed_blocks = set()  # Track blocks that consistently fail
                logger.info(
                    f"Optimized Modbus reading: {len(self._read_blocks)} requests for {len(self.sensors) + len(self.binary_sensors)} sensors"
                )

            for block_idx, block in enumerate(self._read_blocks):
                if not block:
                    continue

                start_addr = block[0].address
                end_addr = max(s.address + s.size for s in block)
                count = end_addr - start_addr

                # Skip blocks that have failed multiple times
                block_key = (start_addr, end_addr)
                if block_key in self._failed_blocks:
                    # Directly read individual sensors for known failed blocks
                    self._read_block_individually(block, data)
                    continue

                try:
                    rr = self.client.read_holding_registers(
                        start_addr, count=count, device_id=1
                    )
                    if rr.isError():
                        # Check if this is an illegal address error (exception code 2)
                        if hasattr(rr, "exception_code") and rr.exception_code == 2:
                            logger.debug(
                                f"Bulk read failed for block {start_addr}-{end_addr}: Illegal Data Address. Marking block for individual reads."
                            )
                            self._failed_blocks.add(block_key)
                        else:
                            logger.warning(
                                f"Bulk read failed for block {start_addr}-{end_addr}: {rr}. Falling back to individual reads."
                            )

                        # Fallback to individual sensor reads
                        self._read_block_individually(block, data)
                        continue

                    # Parse sensors in this block
                    for sensor in block:
                        # Calculate offset in the response registers
                        offset = sensor.address - start_addr
                        sensor_registers = rr.registers[offset : offset + sensor.size]

                        try:
                            success, value = sensor.decode(sensor_registers)
                            if success:
                                # Handle Enums and Flags
                                if hasattr(value, "value"):
                                    data[sensor.name] = value.value
                                    data[f"{sensor.name}_str"] = str(value)
                                else:
                                    data[sensor.name] = value
                        except Exception as e:
                            logger.debug(f"Error decoding {sensor.name}: {e}")

                except Exception as e:
                    logger.error(
                        f"Exception reading block starting at {start_addr}: {e}"
                    )
                    # Mark block as failed and use individual reads
                    self._failed_blocks.add(block_key)
                    self._read_block_individually(block, data)
        except Exception as e:
            logger.error(f"Unhandled exception in read_sensors: {e}")
            self.close()
            raise  # Re-raise the exception to the caller

        return data

    def _read_block_individually(self, block, data):
        """Reads each sensor in a block individually and updates the data dictionary."""
        for sensor in block:
            try:
                sensor_rr = self.client.read_holding_registers(
                    sensor.address, count=sensor.size, device_id=1
                )
                if sensor_rr.isError():
                    logger.debug(
                        f"Individual read failed for {sensor.name} @ {sensor.address}: {sensor_rr}"
                    )
                    continue

                success, value = sensor.decode(sensor_rr.registers)
                if success:
                    if hasattr(value, "value"):
                        data[sensor.name] = value.value
                        data[f"{sensor.name}_str"] = str(value)
                    else:
                        data[sensor.name] = value
            except Exception as e:
                logger.debug(f"Exception reading individual sensor {sensor.name}: {e}")

    def write_sensor(self, name, value):
        if name not in self.sensors and name not in self.binary_sensors:
            raise ValueError(f"Sensor {name} not found")

        sensor = self.sensors.get(name) or self.binary_sensors.get(name)

        if sensor.supported_features == SensorFeatures.NONE:
            raise ValueError(f"Sensor {name} is read-only")

        # Convert value based on type

        try:
            if name in self.binary_sensors:
                if isinstance(value, bool):
                    value = value
                elif isinstance(value, int):
                    if value not in (0, 1):
                        raise ValueError("Binary sensors accept only 0 or 1")
                    value = bool(value)
                elif isinstance(value, str):
                    normalized = value.strip().lower()
                    if normalized in {"true", "1", "yes", "on"}:
                        value = True
                    elif normalized in {"false", "0", "no", "off"}:
                        value = False
                    else:
                        raise ValueError("Binary sensors accept only true/false or 0/1")
                else:
                    raise ValueError(
                        "Binary sensors accept only bool, int, or string values"
                    )

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
                    value = sensor.enum[str(value).strip().upper()]  # access by name

            # If it's UChar/Word
            else:
                value = int(value)

            registers = sensor.encode(value)
        except Exception as e:
            logger.error(f"Encoding error for {name}: {e}")
            raise ValueError(f"Invalid value for {name}: {e}")

        if not self._ensure_connection():
            raise IOError("Could not connect to Modbus")

        # Write
        try:
            # Pymodbus 3.x API: write_registers(address, values, device_id=1)
            rr = self.client.write_registers(sensor.address, registers, device_id=1)
            if rr.isError():
                raise IOError(f"Modbus write error: {rr}")
        except Exception as e:
            logger.error(f"Write failed: {e}")
            self.close()  # Close connection on error
            raise

        return True
