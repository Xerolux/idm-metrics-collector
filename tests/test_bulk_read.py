#!/usr/bin/env python3
"""Test script to verify bulk read optimization and log completeness."""

import sys
import os
import logging

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from idm_logger.modbus import ModbusClient
from idm_logger.config import config

# Configure logging to see debug output
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    # Use command line arguments if provided, otherwise use config
    host = sys.argv[1] if len(sys.argv) > 1 else config.get("idm.host")
    port = int(sys.argv[2]) if len(sys.argv) > 2 else config.get("idm.port")

    logger.info(f"Testing Modbus connection to {host}:{port}")

    # Create ModbusClient
    modbus = ModbusClient(host=host, port=port)

    # Show configured sensors
    logger.info(f"Configured sensors: {len(modbus.sensors)}")
    logger.info(f"Configured binary sensors: {len(modbus.binary_sensors)}")

    total_sensors = len(modbus.sensors) + len(modbus.binary_sensors)
    logger.info(f"Total sensors to read: {total_sensors}")

    # Show read blocks BEFORE reading
    blocks = modbus._build_read_blocks()
    logger.info(f"\n{'=' * 60}")
    logger.info(
        f"Read blocks optimization: {len(blocks)} blocks for {total_sensors} sensors"
    )
    logger.info(f"{'=' * 60}")

    sensors_in_blocks = 0
    for i, block in enumerate(blocks):
        start_addr = block[0].address
        end_addr = max(s.address + s.size for s in block)
        count = end_addr - start_addr
        sensors_in_blocks += len(block)

        logger.info(
            f"Block {i + 1}: Address {start_addr}-{end_addr} ({count} registers, {len(block)} sensors)"
        )
        for sensor in block:
            logger.info(f"  - {sensor.name} @ {sensor.address} (size: {sensor.size})")

    logger.info(f"\nSensors in blocks: {sensors_in_blocks}/{total_sensors}")

    if sensors_in_blocks != total_sensors:
        logger.error(
            f"⚠️  MISSING SENSORS! {total_sensors - sensors_in_blocks} sensors not in any block!"
        )

        # Find missing sensors
        sensors_in_blocks_set = set()
        for block in blocks:
            for sensor in block:
                sensors_in_blocks_set.add(sensor.name)

        all_sensors_set = set(modbus.sensors.keys()) | set(modbus.binary_sensors.keys())
        missing = all_sensors_set - sensors_in_blocks_set

        logger.error(f"Missing sensors: {missing}")

    # Now read data
    logger.info(f"\n{'=' * 60}")
    logger.info("Reading sensor data...")
    logger.info(f"{'=' * 60}\n")

    data = modbus.read_sensors()

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Read {len(data)} data points")
    logger.info(f"{'=' * 60}")

    # Sort and display all data
    for key in sorted(data.keys()):
        value = data[key]
        logger.info(f"{key:40s} = {value}")

    # Check if we got all sensors
    expected_keys = set(modbus.sensors.keys()) | set(modbus.binary_sensors.keys())
    # Also account for _str variants
    actual_keys = set(k for k in data.keys() if not k.endswith("_str"))

    missing_data = expected_keys - actual_keys
    if missing_data:
        logger.warning(f"\n⚠️  Missing data for {len(missing_data)} sensors:")
        for sensor_name in sorted(missing_data):
            sensor = modbus.sensors.get(sensor_name) or modbus.binary_sensors.get(
                sensor_name
            )
            if sensor:
                logger.warning(
                    f"  - {sensor_name} @ address {sensor.address} (read_supported: {sensor.read_supported})"
                )
    else:
        logger.info("\n✓ All sensors read successfully!")

    modbus.close()


if __name__ == "__main__":
    main()
