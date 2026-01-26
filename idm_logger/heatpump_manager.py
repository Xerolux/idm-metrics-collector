# SPDX-License-Identifier: MIT
"""
Heat Pump Manager - Central management for multiple heat pumps.

This module provides the HeatpumpManager class which handles:
- Connection management for multiple heat pumps
- Parallel sensor reading across all devices
- Device lifecycle (add, remove, enable, disable)
- Status monitoring and error tracking

Architecture:
    HeatpumpManager
        |
        +-- HeatpumpConnection (per device)
        |       |
        |       +-- ModbusClient (connection)
        |       +-- HeatpumpDriver (manufacturer-specific logic)
        |       +-- SensorDefinitions (sensor list)
        |
        +-- Database (persistence)
        +-- MetricsWriter (time-series storage)

Usage:
    from idm_logger.heatpump_manager import HeatpumpManager, heatpump_manager

    # Initialize (call once at startup)
    await heatpump_manager.initialize()

    # Read all heatpumps
    data = await heatpump_manager.read_all()

    # Add a new heatpump
    hp_id = await heatpump_manager.add_heatpump({
        "name": "Main Building",
        "manufacturer": "idm",
        "model": "navigator_2_0",
        "connection": {"host": "192.168.1.100", "port": 502}
    })
"""

import asyncio
import logging
import time
import uuid
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

from pymodbus.client import ModbusTcpClient

from .db import db
from .manufacturers import (
    ManufacturerRegistry,
    HeatpumpDriver,
    SensorDefinition,
    ReadGroup,
)

logger = logging.getLogger(__name__)

# Thread pool for blocking Modbus operations
_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="modbus_")


@dataclass
class HeatpumpConnection:
    """
    Represents an active connection to a single heat pump.

    Attributes:
        id: Unique identifier
        name: User-friendly name
        manufacturer: Manufacturer ID
        model: Model ID
        driver: Manufacturer-specific driver instance
        client: Modbus TCP client
        sensors: List of sensor definitions
        enabled: Whether this connection is active
        last_read: Timestamp of last successful read
        last_values: Most recent sensor values
        error_count: Consecutive error count
        last_error: Last error message
    """

    id: str
    name: str
    manufacturer: str
    model: str
    driver: HeatpumpDriver
    client: ModbusTcpClient
    sensors: List[SensorDefinition]
    enabled: bool = True
    last_read: float = 0
    last_values: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    last_error: Optional[str] = None
    _read_groups: Optional[List[ReadGroup]] = field(default=None, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def is_connected(self) -> bool:
        """Check if the Modbus client is connected."""
        return self.client is not None and self.client.is_socket_open()

    def get_read_groups(self) -> List[ReadGroup]:
        """Get optimized read groups for sensors."""
        if self._read_groups is None:
            self._read_groups = self.driver.get_read_groups(self.sensors)
        return self._read_groups

    def invalidate_cache(self):
        """Invalidate cached read groups."""
        self._read_groups = None


class HeatpumpManager:
    """
    Central manager for multiple heat pump connections.

    This class handles the lifecycle and data collection for all
    configured heat pumps in the system.
    """

    def __init__(self):
        self._connections: Dict[str, HeatpumpConnection] = {}
        self._initialized = False
        self._config_cache: Dict[str, dict] = {}

    async def initialize(self):
        """
        Initialize the manager and connect to all configured heat pumps.

        This should be called once at application startup.
        """
        if self._initialized:
            logger.warning("HeatpumpManager already initialized")
            return

        logger.info("Initializing HeatpumpManager...")

        # Load all enabled heatpumps from database
        heatpumps = db.get_enabled_heatpumps()

        if not heatpumps:
            logger.info("No heatpumps configured yet")
            self._initialized = True
            return

        # Connect to each heatpump
        for hp in heatpumps:
            try:
                await self._connect_heatpump(hp)
            except Exception as e:
                logger.error(f"Failed to initialize heatpump {hp['id']}: {e}")

        self._initialized = True
        logger.info(
            f"HeatpumpManager initialized with {len(self._connections)} connection(s)"
        )

    async def _connect_heatpump(self, hp_config: dict) -> bool:
        """
        Create a connection to a single heat pump.

        Args:
            hp_config: Heat pump configuration from database

        Returns:
            True if connection was successful
        """
        hp_id = hp_config["id"]

        if hp_id in self._connections:
            logger.warning(f"Heatpump {hp_id} already connected, skipping")
            return True

        # Get the driver for this manufacturer/model
        driver = ManufacturerRegistry.get_driver(
            hp_config["manufacturer"], hp_config["model"]
        )

        if not driver:
            logger.error(
                f"No driver found for {hp_config['manufacturer']}/{hp_config['model']}"
            )
            return False

        # Get connection config
        conn_config = hp_config.get("connection_config", {})
        host = conn_config.get("host", "")
        port = conn_config.get("port", 502)
        unit_id = conn_config.get("unit_id", 1)
        timeout = conn_config.get("timeout", 10)

        if not host:
            logger.error(f"No host configured for heatpump {hp_id}")
            return False

        # Get sensors for this configuration
        device_config = hp_config.get("device_config", {})
        sensors = driver.get_sensors(device_config)

        # Create client (Modbus or custom)
        if driver.requires_custom_client() and hasattr(driver, "create_client"):
            client = driver.create_client(conn_config)
        else:
            client = ModbusTcpClient(host=host, port=port, timeout=timeout, retries=3)

        # Store connection
        connection = HeatpumpConnection(
            id=hp_id,
            name=hp_config.get("name", f"Heatpump {hp_id}"),
            manufacturer=hp_config["manufacturer"],
            model=hp_config["model"],
            driver=driver,
            client=client,
            sensors=sensors,
            enabled=hp_config.get("enabled", True),
        )

        self._connections[hp_id] = connection
        self._config_cache[hp_id] = hp_config

        # Try to connect
        try:
            loop = asyncio.get_event_loop()
            connected = await loop.run_in_executor(_executor, client.connect)
            if connected:
                logger.info(
                    f"Connected to heatpump '{hp_config['name']}' "
                    f"({hp_config['manufacturer']}/{hp_config['model']}) "
                    f"at {host}:{port} with {len(sensors)} sensors"
                )
                return True
            else:
                logger.warning(
                    f"Could not connect to heatpump {hp_id} at {host}:{port}"
                )
                return False
        except Exception as e:
            logger.error(f"Connection error for {hp_id}: {e}")
            connection.last_error = str(e)
            connection.error_count += 1
            return False

    async def read_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Read sensor values from all connected heat pumps.

        Returns:
            Dict mapping heatpump_id to sensor values dict
        """
        if not self._connections:
            return {}

        # Read all heatpumps in parallel
        tasks = [
            self._read_heatpump(hp_id)
            for hp_id, conn in self._connections.items()
            if conn.enabled
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        all_data = {}
        for hp_id, values in zip(
            [hp_id for hp_id, c in self._connections.items() if c.enabled], results
        ):
            if isinstance(values, Exception):
                logger.error(f"Read error for {hp_id}: {values}")
                self._connections[hp_id].error_count += 1
                self._connections[hp_id].last_error = str(values)
            elif values:
                all_data[hp_id] = values
                self._connections[hp_id].last_values = values
                self._connections[hp_id].last_read = time.time()
                self._connections[hp_id].error_count = 0
                self._connections[hp_id].last_error = None

        return all_data

    async def _read_heatpump(self, hp_id: str) -> Dict[str, Any]:
        """
        Read all sensors from a single heat pump.

        Args:
            hp_id: Heat pump ID

        Returns:
            Dict of sensor_id -> value
        """
        if hp_id not in self._connections:
            raise ValueError(f"Unknown heatpump: {hp_id}")

        conn = self._connections[hp_id]

        # Ensure connection
        if not conn.is_connected:
            loop = asyncio.get_event_loop()
            connected = await loop.run_in_executor(_executor, conn.client.connect)
            if not connected:
                raise ConnectionError(f"Cannot connect to {hp_id}")

        values = {}
        read_groups = conn.get_read_groups()

        for group in read_groups:
            try:
                # Read registers for this group
                raw_registers = await self._read_registers(
                    conn, group.start_address, group.count
                )

                if raw_registers is None:
                    continue

                # Parse each sensor in the group
                for sensor in group.sensors:
                    offset = sensor.address - group.start_address
                    sensor_regs = raw_registers[offset : offset + sensor.size]

                    if len(sensor_regs) >= sensor.size:
                        value = conn.driver.parse_value(sensor, sensor_regs)
                        if value is not None:
                            values[sensor.id] = value

            except Exception as e:
                logger.debug(f"Error reading group at {group.start_address}: {e}")
                # Try individual reads as fallback
                for sensor in group.sensors:
                    try:
                        raw = await self._read_registers(
                            conn, sensor.address, sensor.size
                        )
                        if raw:
                            value = conn.driver.parse_value(sensor, raw)
                            if value is not None:
                                values[sensor.id] = value
                    except Exception:
                        pass

        return values

    async def _read_registers(
        self, conn: HeatpumpConnection, address: int, count: int
    ) -> Optional[List[int]]:
        """
        Read Modbus registers asynchronously.

        Args:
            conn: Heatpump connection object
            address: Start address
            count: Number of registers

        Returns:
            List of register values or None on error
        """
        loop = asyncio.get_event_loop()

        def _do_read():
            with conn._lock:
                result = conn.client.read_holding_registers(
                    address, count=count, slave=1
                )
                if result.isError():
                    return None
                return result.registers

        try:
            return await loop.run_in_executor(_executor, _do_read)
        except Exception as e:
            logger.debug(f"Register read error at {address}: {e}")
            return None

    async def read_heatpump(self, hp_id: str) -> Dict[str, Any]:
        """
        Read sensor values from a specific heat pump.

        Args:
            hp_id: Heat pump ID

        Returns:
            Dict of sensor values
        """
        return await self._read_heatpump(hp_id)

    async def write_value(self, hp_id: str, sensor_id: str, value: Any) -> bool:
        """
        Write a value to a heat pump sensor.

        Args:
            hp_id: Heat pump ID
            sensor_id: Sensor ID
            value: Value to write

        Returns:
            True if successful
        """
        if hp_id not in self._connections:
            raise ValueError(f"Unknown heatpump: {hp_id}")

        conn = self._connections[hp_id]

        # Find the sensor
        sensor = None
        for s in conn.sensors:
            if s.id == sensor_id:
                sensor = s
                break

        if not sensor:
            raise ValueError(f"Unknown sensor: {sensor_id}")

        if not sensor.is_writable:
            raise ValueError(f"Sensor {sensor_id} is read-only")

        # Encode the value
        registers = conn.driver.encode_value(sensor, value)

        # Ensure connection
        if not conn.is_connected:
            loop = asyncio.get_event_loop()
            connected = await loop.run_in_executor(_executor, conn.client.connect)
            if not connected:
                raise ConnectionError(f"Cannot connect to {hp_id}")

        # Write registers
        loop = asyncio.get_event_loop()

        def _do_write():
            with conn._lock:
                result = conn.client.write_registers(sensor.address, registers, slave=1)
                return not result.isError()

        try:
            success = await loop.run_in_executor(_executor, _do_write)
            if success:
                logger.info(f"Wrote {value} to {hp_id}/{sensor_id}")
            return success
        except Exception as e:
            logger.error(f"Write error for {hp_id}/{sensor_id}: {e}")
            raise

    # ==================== CRUD Operations ====================

    async def add_heatpump(self, config: dict) -> str:
        """
        Add a new heat pump.

        Args:
            config: Configuration dict with:
                - name: Display name
                - manufacturer: Manufacturer ID
                - model: Model ID
                - connection: {host, port, unit_id, timeout}
                - config: Device-specific config (circuits, zones, etc.)

        Returns:
            The new heatpump ID
        """
        # Validate manufacturer/model
        driver = ManufacturerRegistry.get_driver(
            config["manufacturer"], config["model"]
        )
        if not driver:
            raise ValueError(f"Unsupported: {config['manufacturer']}/{config['model']}")

        # Validate device config
        device_config = config.get("config", {})
        valid, error = driver.validate_config(device_config)
        if not valid:
            raise ValueError(f"Invalid configuration: {error}")

        # Create database entry
        hp_data = {
            "name": config["name"],
            "manufacturer": config["manufacturer"],
            "model": config["model"],
            "connection_config": config.get("connection", {}),
            "device_config": device_config,
            "enabled": config.get("enabled", True),
        }

        hp_id = db.add_heatpump(hp_data)

        # Get the full record
        hp_config = db.get_heatpump(hp_id)

        # Connect
        await self._connect_heatpump(hp_config)

        # Create default dashboard
        await self._create_default_dashboard(hp_id, driver)

        logger.info(f"Added heatpump {hp_id}: {config['name']}")
        return hp_id

    async def _create_default_dashboard(self, hp_id: str, driver: HeatpumpDriver):
        """Create a default dashboard for a new heatpump."""
        template = driver.get_dashboard_template()

        dashboard = {
            "name": template.get("name", f"Dashboard for {hp_id}"),
            "heatpump_id": hp_id,
            "config": template,
            "position": 0,
        }

        db.add_dashboard(dashboard)
        logger.info(f"Created default dashboard for heatpump {hp_id}")

    async def remove_heatpump(self, hp_id: str):
        """
        Remove a heat pump and clean up.

        Args:
            hp_id: Heat pump ID to remove
        """
        # Disconnect if connected
        if hp_id in self._connections:
            conn = self._connections[hp_id]
            if conn.client:
                try:
                    conn.client.close()
                except Exception:
                    pass
            del self._connections[hp_id]

        if hp_id in self._config_cache:
            del self._config_cache[hp_id]

        # Delete from database (cascades to dashboards)
        db.delete_heatpump(hp_id)

        logger.info(f"Removed heatpump {hp_id}")

    async def update_heatpump(self, hp_id: str, updates: dict):
        """
        Update heat pump configuration.

        Args:
            hp_id: Heat pump ID
            updates: Fields to update
        """
        # Update database
        db.update_heatpump(hp_id, updates)

        # Reconnect if connection settings changed
        if "connection_config" in updates or "device_config" in updates:
            await self.reconnect(hp_id)

    async def reconnect(self, hp_id: str):
        """
        Reconnect to a heat pump.

        Args:
            hp_id: Heat pump ID
        """
        # Disconnect first
        if hp_id in self._connections:
            conn = self._connections[hp_id]
            if conn.client:
                try:
                    conn.client.close()
                except Exception:
                    pass
            del self._connections[hp_id]

        # Get fresh config from database
        hp_config = db.get_heatpump(hp_id)
        if hp_config and hp_config.get("enabled"):
            await self._connect_heatpump(hp_config)

    async def enable_heatpump(self, hp_id: str, enabled: bool = True):
        """
        Enable or disable a heat pump.

        Args:
            hp_id: Heat pump ID
            enabled: Whether to enable
        """
        db.update_heatpump(hp_id, {"enabled": enabled})

        if enabled:
            await self.reconnect(hp_id)
        elif hp_id in self._connections:
            self._connections[hp_id].enabled = False
            if self._connections[hp_id].client:
                try:
                    self._connections[hp_id].client.close()
                except Exception:
                    pass

    # ==================== Status and Info ====================

    def get_status(self) -> List[dict]:
        """
        Get status information for all heat pumps.

        Returns:
            List of status dicts
        """
        status_list = []

        for hp_id, conn in self._connections.items():
            config = self._config_cache.get(hp_id, {})
            conn_config = config.get("connection_config", {})

            status_list.append(
                {
                    "id": hp_id,
                    "name": conn.name,
                    "manufacturer": conn.manufacturer,
                    "model": conn.model,
                    "host": conn_config.get("host", ""),
                    "port": conn_config.get("port", 502),
                    "connected": conn.is_connected,
                    "enabled": conn.enabled,
                    "sensor_count": len(conn.sensors),
                    "last_read": conn.last_read,
                    "error_count": conn.error_count,
                    "last_error": conn.last_error,
                }
            )

        return status_list

    def get_heatpump_info(self, hp_id: str) -> Optional[dict]:
        """
        Get detailed info for a specific heat pump.

        Args:
            hp_id: Heat pump ID

        Returns:
            Info dict or None
        """
        if hp_id not in self._connections:
            return None

        conn = self._connections[hp_id]
        config = self._config_cache.get(hp_id, {})

        return {
            "id": hp_id,
            "name": conn.name,
            "manufacturer": conn.manufacturer,
            "model": conn.model,
            "connection_config": config.get("connection_config", {}),
            "device_config": config.get("device_config", {}),
            "connected": conn.is_connected,
            "enabled": conn.enabled,
            "sensors": [
                {
                    "id": s.id,
                    "name": s.name,
                    "name_de": s.name_de,
                    "category": s.category.value,
                    "unit": s.unit,
                    "writable": s.is_writable,
                }
                for s in conn.sensors
            ],
            "capabilities": conn.driver.get_capabilities().to_dict(),
            "last_read": conn.last_read,
            "last_values": conn.last_values,
            "error_count": conn.error_count,
            "last_error": conn.last_error,
        }

    def get_all_configs(self) -> Dict[str, dict]:
        """Get all heatpump configurations (cached)."""
        return self._config_cache.copy()

    def get_connection(self, hp_id: str) -> Optional[HeatpumpConnection]:
        """Get a specific connection."""
        return self._connections.get(hp_id)

    @property
    def connection_count(self) -> int:
        """Number of configured connections."""
        return len(self._connections)

    @property
    def connected_count(self) -> int:
        """Number of currently connected heat pumps."""
        return sum(1 for c in self._connections.values() if c.is_connected)

    async def close(self):
        """Close all connections."""
        for hp_id, conn in self._connections.items():
            if conn.client:
                try:
                    conn.client.close()
                except Exception:
                    pass
        self._connections.clear()
        self._config_cache.clear()
        logger.info("HeatpumpManager closed all connections")


# Global singleton instance
heatpump_manager = HeatpumpManager()
