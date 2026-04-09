# Xerolux 2026
# SPDX-License-Identifier: MIT
import logging
import time
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

# Connection configuration
MODBUS_TIMEOUT = config.get(
    "modbus.timeout", 3
)  # Reduced from 10s to 3s for faster recovery
MODBUS_RETRIES = config.get("modbus.retries", 3)
RECONNECT_BASE_DELAY = config.get("modbus.reconnect_base_delay", 1.0)
RECONNECT_MAX_DELAY = config.get("modbus.reconnect_max_delay", 60.0)
RECONNECT_MULTIPLIER = config.get("modbus.reconnect_multiplier", 2.0)


def _normalize_binary_value(value):
    """Normalize binary sensor input to a strict bool value."""
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        raise ValueError("Binary sensors accept only 0/1 for integer values")

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
        raise ValueError(
            "Binary sensors accept only true/false, yes/no, on/off, or 0/1"
        )

    raise ValueError("Binary sensors accept only bool, int, or string values")


class ModbusClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = ModbusTcpClient(
            host, port=port, timeout=MODBUS_TIMEOUT, retries=MODBUS_RETRIES
        )

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

        # Cache management - store sensor config hash to detect changes
        self._read_blocks = None
        self._failed_blocks = {}  # Changed to dict: {(start, end): timestamp}
        self._sensor_config_hash = self._compute_sensor_hash()
        self._last_failed_cleanup = time.time()
        self._FAILED_BLOCK_TTL = 3600  # 1 hour TTL for failed blocks
        self._FAILED_BLOCK_CLEANUP_INTERVAL = 300  # Cleanup every 5 minutes

        # Connection state tracking for exponential backoff
        self._connection_was_lost = False
        self._reconnect_delay = RECONNECT_BASE_DELAY
        self._last_reconnect_attempt = 0
        self._consecutive_failures = 0

        # Connection health statistics
        self._stats = {
            "total_connects": 0,
            "total_disconnects": 0,
            "total_reconnects": 0,
            "total_read_errors": 0,
            "total_write_errors": 0,
            "last_successful_read": None,
            "last_error": None,
            "uptime_start": None,
        }

    def _compute_sensor_hash(self) -> int:
        """Compute hash of current sensor configuration for cache invalidation."""
        sensor_keys = tuple(sorted(self.sensors.keys()))
        binary_keys = tuple(sorted(self.binary_sensors.keys()))
        return hash((sensor_keys, binary_keys))

    def invalidate_cache(self):
        """Invalidate the read blocks cache. Call when sensor config changes."""
        self._read_blocks = None
        self._failed_blocks = {}
        self._sensor_config_hash = self._compute_sensor_hash()
        logger.debug("Modbus read blocks cache invalidated")

    def _cleanup_failed_blocks(self):
        """Remove expired failed block entries to prevent memory leak."""
        now = time.time()
        if now - self._last_failed_cleanup < self._FAILED_BLOCK_CLEANUP_INTERVAL:
            return

        # Remove entries older than TTL
        expired_keys = [
            key
            for key, timestamp in self._failed_blocks.items()
            if now - timestamp > self._FAILED_BLOCK_TTL
        ]

        if expired_keys:
            for key in expired_keys:
                del self._failed_blocks[key]
            logger.debug(f"Cleaned up {len(expired_keys)} expired failed block entries")

        self._last_failed_cleanup = now

    def connect(self):
        """Connects to the Modbus server."""
        if not self.host:
            logger.error("Modbus host is not configured")
            return False

        if self.client.is_socket_open():
            return True

        logger.info(f"Connecting to Modbus server at {self.host}:{self.port}")
        try:
            result = self.client.connect()
            if result:
                self._stats["total_connects"] += 1
                self._stats["uptime_start"] = time.time()
                self._reconnect_delay = RECONNECT_BASE_DELAY
                self._consecutive_failures = 0
                logger.info("Modbus connection established successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to connect to Modbus server: {e}")
            self._stats["last_error"] = str(e)
            return False

    def close(self):
        """Closes the Modbus connection."""
        if self.client.is_socket_open():
            logger.info("Closing Modbus connection")
            self._stats["total_disconnects"] += 1
            self.client.close()

    def __del__(self):
        """Ensure connection is closed on garbage collection."""
        try:
            self.close()
        except Exception:
            pass

    def get_connection_stats(self) -> dict:
        """Returns connection health statistics."""
        stats = self._stats.copy()
        stats["is_connected"] = self.client.is_socket_open()
        stats["consecutive_failures"] = self._consecutive_failures
        stats["current_reconnect_delay"] = self._reconnect_delay
        if stats["uptime_start"] and stats["is_connected"]:
            stats["uptime_seconds"] = int(time.time() - stats["uptime_start"])
        else:
            stats["uptime_seconds"] = 0
        return stats

    def _ensure_connection(self):
        """
        Ensures the client is connected, using exponential backoff for reconnection.
        Returns True if connected, False otherwise.
        """
        if self.client.is_socket_open():
            if self._connection_was_lost:
                logger.info("Modbus connection restored")
                self._connection_was_lost = False
                self._stats["total_reconnects"] += 1
                self._reconnect_delay = RECONNECT_BASE_DELAY
                self._consecutive_failures = 0
            return True

        # Check if we should wait before next reconnect attempt (exponential backoff)
        now = time.time()
        time_since_last_attempt = now - self._last_reconnect_attempt

        if time_since_last_attempt < self._reconnect_delay:
            # Still in backoff period, don't spam reconnects
            return False

        self._last_reconnect_attempt = now

        # Log warning only on first detection of connection loss
        if not self._connection_was_lost:
            logger.warning("Modbus connection lost. Attempting to reconnect...")
            self._connection_was_lost = True
            self._stats["total_disconnects"] += 1
        else:
            logger.debug(
                f"Modbus reconnect attempt (delay: {self._reconnect_delay:.1f}s, "
                f"failures: {self._consecutive_failures})"
            )

        # Attempt to reconnect
        try:
            result = self.client.connect()
            if result:
                # Note: total_reconnects is incremented in the next call when
                # is_socket_open() returns True and _connection_was_lost is still set
                self._stats["uptime_start"] = time.time()
                return True
        except Exception as e:
            logger.debug(f"Reconnect attempt failed: {e}")
            self._stats["last_error"] = str(e)

        # Increase backoff delay for next attempt
        self._consecutive_failures += 1
        self._reconnect_delay = min(
            self._reconnect_delay * RECONNECT_MULTIPLIER, RECONNECT_MAX_DELAY
        )

        return False

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
            if self._consecutive_failures == 1:
                # Only log error on first failure to avoid log spam
                logger.error("Could not connect to Modbus server")
            return data

        try:
            # Check if sensor config changed and invalidate cache if needed
            current_hash = self._compute_sensor_hash()
            if current_hash != self._sensor_config_hash:
                logger.info("Sensor configuration changed, rebuilding read blocks")
                self.invalidate_cache()
                self._sensor_config_hash = current_hash

            # Build blocks if not cached
            if self._read_blocks is None:
                self._read_blocks = self._build_read_blocks()
                logger.info(
                    f"Optimized Modbus reading: {len(self._read_blocks)} requests for {len(self.sensors) + len(self.binary_sensors)} sensors"
                )

            # Periodic cleanup of failed blocks to prevent memory leak
            self._cleanup_failed_blocks()

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

                # Small delay between blocks to be nice to the device (especially if shared)
                if block_idx > 0:
                    time.sleep(0.05)

                try:
                    # Retry logic for busy devices
                    rr = None
                    for attempt in range(2):
                        try:
                            rr = self.client.read_holding_registers(
                                start_addr, count=count, device_id=1
                            )
                            if not rr.isError():
                                break
                            time.sleep(0.2)  # Wait before retry
                        except Exception as e:
                            if attempt == 1:
                                raise e
                            time.sleep(0.2)

                    if rr.isError():
                        # Check if this is an illegal address error (exception code 2)
                        if hasattr(rr, "exception_code") and rr.exception_code == 2:
                            logger.debug(
                                f"Bulk read failed for block {start_addr}-{end_addr}: Illegal Data Address. Marking block for individual reads."
                            )
                            self._failed_blocks[block_key] = (
                                time.time()
                            )  # Store with timestamp
                        else:
                            logger.warning(
                                f"Bulk read failed for block {start_addr}-{end_addr}: {rr}. Falling back to individual reads."
                            )

                        # Fallback to individual sensor reads
                        self._read_block_individually(block, data)
                        continue

                    if not hasattr(rr, "registers"):
                        logger.warning(
                            f"Bulk read returned malformed response for block {start_addr}-{end_addr}. "
                            "Falling back to individual reads."
                        )
                        self._stats["total_read_errors"] += 1
                        self._stats["last_error"] = (
                            "Malformed Modbus response: missing registers"
                        )
                        self._read_block_individually(block, data)
                        continue

                    if len(rr.registers) < count:
                        logger.warning(
                            f"Bulk read returned {len(rr.registers)} registers for block {start_addr}-{end_addr}, "
                            f"expected at least {count}. Falling back to individual reads."
                        )
                        self._stats["total_read_errors"] += 1
                        self._stats["last_error"] = (
                            f"Short Modbus response: got {len(rr.registers)}, expected {count}"
                        )
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
                    # Don't close connection on read errors, just log and mark block
                    logger.warning(
                        f"Exception reading block starting at {start_addr}: {e}"
                    )
                    self._stats["total_read_errors"] += 1
                    self._stats["last_error"] = str(e)
                    # Mark block as failed and use individual reads
                    self._failed_blocks[block_key] = time.time()
                    self._read_block_individually(block, data)

            # Update statistics on successful read
            if data:
                self._stats["last_successful_read"] = time.time()

        except Exception as e:
            # Fatal error (e.g. connection lost logic inside ensuring connection) should be handled there,
            # but if we get here it's likely fatal.
            logger.error(f"Unhandled exception in read_sensors: {e}")
            self._stats["total_read_errors"] += 1
            self._stats["last_error"] = str(e)
            self.close()
            # Do NOT re-raise, allow the main loop to continue and try again next cycle
            # raise

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
                value = _normalize_binary_value(value)

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
                self._stats["total_write_errors"] += 1
                self._stats["last_error"] = f"Write error: {rr}"
                raise IOError(f"Modbus write error: {rr}")
        except IOError:
            raise  # Re-raise IOError without additional handling
        except Exception as e:
            logger.error(f"Write failed: {e}")
            self._stats["total_write_errors"] += 1
            self._stats["last_error"] = str(e)
            self.close()  # Close connection on error
            raise

        return True
