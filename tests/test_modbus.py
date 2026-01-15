#!/usr/bin/env python3
"""Test Modbus connection to IDM Heat Pump."""

import sys
from pymodbus.client import ModbusTcpClient

# Connection settings
HOST = "192.168.178.103"
PORT = 502
DEVICE_ID = 1

# Test addresses (from sensor_addresses.py)
TEST_ADDRESSES = [
    (1000, 2, "System Status (uint32)"),
    (1003, 1, "Heat Pump Status (uint16)"),
    (1010, 2, "Temperature Outside (float32)"),
    (1012, 2, "Temperature Flow (float32)"),
    (1999, 1, "Acknowledge Faults (uint16)"),
]


def test_connection():
    """Test Modbus TCP connection."""
    print(f"Testing Modbus connection to {HOST}:{PORT}...")
    print("=" * 60)

    # Create client
    client = ModbusTcpClient(host=HOST, port=PORT, timeout=5)

    # Try to connect
    print(f"\n1. Attempting to connect to {HOST}:{PORT}...")
    try:
        connection = client.connect()
        if connection:
            print("   ✓ Connection successful!")
        else:
            print("   ✗ Connection failed!")
            print("\nPossible issues:")
            print("   - Heat pump is not reachable (network issue)")
            print("   - Firewall blocking port 502")
            print("   - Modbus TCP not enabled on heat pump")
            print("   - Wrong IP address")
            return False
    except Exception as e:
        print(f"   ✗ Connection error: {e}")
        return False

    # Test reading registers
    print(f"\n2. Testing register reads (device_id={DEVICE_ID})...")
    success_count = 0
    failed_count = 0

    for address, count, description in TEST_ADDRESSES:
        try:
            result = client.read_holding_registers(
                address, count=count, device_id=DEVICE_ID
            )

            if result.isError():
                print(f"   ✗ Address {address:4d} ({description})")
                print(f"      Error: {result}")
                failed_count += 1
            else:
                print(f"   ✓ Address {address:4d} ({description})")
                print(f"      Registers: {result.registers}")
                success_count += 1

        except Exception as e:
            print(f"   ✗ Address {address:4d} ({description})")
            print(f"      Exception: {e}")
            failed_count += 1

    # Close connection
    client.close()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Successful reads: {success_count}/{len(TEST_ADDRESSES)}")
    print(f"  Failed reads:     {failed_count}/{len(TEST_ADDRESSES)}")

    if success_count > 0:
        print("\n  ✓ Modbus connection is working!")
        if failed_count > 0:
            print("    Some registers are not accessible (this might be normal)")
        return True
    else:
        print("\n  ✗ No registers could be read!")
        print("\nPossible issues:")
        print("  - Wrong device_id (currently using 1)")
        print("  - Heat pump uses different register addresses")
        print("  - Modbus gateway/protocol mismatch")
        return False


if __name__ == "__main__":
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
