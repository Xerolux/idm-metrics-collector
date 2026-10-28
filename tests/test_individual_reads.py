#!/usr/bin/env python3
# Xerolux 2026
# SPDX-License-Identifier: MIT
"""Test individual sensor reads to find which addresses work."""

import sys
import logging
from pymodbus.client import ModbusTcpClient

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Test critical addresses
TEST_ADDRESSES = [
    (1000, 2, "temp_outside"),
    (1002, 2, "temp_outside_avg"),
    (1004, 1, "failure_id"),
    (1005, 1, "status_system"),
    (1006, 1, "status_smart_grid"),
    (1008, 2, "temp_heat_storage"),
    (1010, 2, "temp_cold_storage"),
    (1012, 2, "temp_water_heater_bottom"),
    (1014, 2, "temp_water_heater_top"),
    (1090, 1, "status_heat_pump"),
    (1091, 1, "request_heating"),
    (1092, 1, "request_cooling"),
    (1093, 1, "request_water_status"),
    (1100, 1, "state_compressor_1"),
    (1104, 1, "state_charge_pump"),
]


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.178.103"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502

    print(f"Testing individual reads on {host}:{port}\n")
    print(
        f"{'Address':<10} {'Size':<6} {'Sensor Name':<30} {'Result':<15} {'Raw Values'}"
    )
    print("=" * 90)

    client = ModbusTcpClient(host, port=port)
    if not client.connect():
        print("Failed to connect!")
        return

    for address, size, name in TEST_ADDRESSES:
        try:
            rr = client.read_holding_registers(address, count=size, device_id=1)
            if rr.isError():
                print(f"{address:<10} {size:<6} {name:<30} {'ERROR':<15} {rr}")
            else:
                print(f"{address:<10} {size:<6} {name:<30} {'OK':<15} {rr.registers}")
        except Exception as e:
            print(f"{address:<10} {size:<6} {name:<30} {'EXCEPTION':<15} {e}")

    client.close()


if __name__ == "__main__":
    main()
