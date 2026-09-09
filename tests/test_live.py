#!/usr/bin/env python3
# Xerolux 2026
# SPDX-License-Identifier: MIT
"""Live test script for IDM heat pump - READ ONLY"""

import logging
import sys
import struct
import os

import pytest

# Import for pymodbus 3.x
from pymodbus.client import ModbusTcpClient

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Test configuration
HOST = "192.168.178.103"
PORT = 502
UNIT = 1

# Important registers to test (read-only)
TEST_REGISTERS = {
    "Außentemperatur": 1000,
    "Außentemperatur Durchschnitt": 1002,
    "System Status": 1005,
    "Wärmespeicher Temperatur": 1008,
    "Warmwasser oben Temperatur": 1012,
    "Warmwasser unten Temperatur": 1014,
    "Wärmepumpe Vorlauf": 1050,
    "Wärmepumpe Rücklauf": 1052,
    "Wärmequelle Eingang": 1056,
    "Wärmequelle Ausgang": 1058,
    "Aktuelle Leistung": 1790,
    "Heizenergie gesamt": 1750,
}


def decode_float32(registers):
    """Decode 2 registers as float32 (Big Endian byteorder, Little Endian wordorder)"""
    # In IDM, wordorder is Little (swap the two 16-bit words)
    word1 = registers[1]  # Little endian word order
    word2 = registers[0]

    # Pack as two 16-bit unsigned integers in big endian byte order
    bytes_data = struct.pack(">HH", word1, word2)
    # Unpack as float
    value = struct.unpack(">f", bytes_data)[0]
    return value


def decode_uint16(registers):
    """Decode 1 register as uint16"""
    return registers[0]


def test_connection():
    """Test connection and read basic values"""
    if os.getenv("IDM_LIVE_TEST") != "1":
        pytest.skip("Live Modbus test requires IDM_LIVE_TEST=1 to run.")
    print(f"\n{'=' * 60}")
    print("IDM Wärmepumpe Live-Test (READ ONLY)")
    print(f"{'=' * 60}")
    print(f"Host: {HOST}:{PORT}")
    print(f"{'=' * 60}\n")

    # Create client
    client = ModbusTcpClient(HOST, port=PORT)

    # Connect
    print("Verbindung wird hergestellt...")
    if not client.connect():
        print("❌ FEHLER: Konnte keine Verbindung herstellen!")
        print("   Mögliche Ursachen:")
        print("   - Wärmepumpe ist nicht erreichbar")
        print("   - Falsche IP-Adresse oder Port")
        print("   - Firewall blockiert die Verbindung")
        sys.exit(1)

    print("[OK] Verbindung erfolgreich!\n")

    # Read values
    print(f"{'Sensor':<35} {'Wert':<15} {'Register'}")
    print(f"{'-' * 60}")

    for name, address in TEST_REGISTERS.items():
        try:
            # Most values are float32 (2 registers), status is uint16 (1 register)
            if address == 1005:  # System status
                count = 1
            else:
                count = 2

            result = client.read_holding_registers(address, count=count, device_id=UNIT)

            if result.isError():
                print(f"{name:<35} {'FEHLER':<15} {address}")
                continue

            # Decode value
            if count == 2:
                value = decode_float32(result.registers)
                # Determine unit
                if "Temperatur" in name or "Vorlauf" in name or "Rücklauf" in name:
                    value_str = f"{value:.1f} °C"
                elif "Leistung" in name:
                    value_str = f"{value:.2f} kW"
                elif "Energie" in name:
                    value_str = f"{value:.1f} kWh"
                else:
                    value_str = f"{value:.2f}"
            else:
                value = decode_uint16(result.registers)
                value_str = f"{value}"

            print(f"{name:<35} {value_str:<15} {address}")

        except Exception as e:
            print(f"{name:<35} {'EXCEPTION':<15} {address} - {e}")

    # Close connection
    client.close()
    print(f"\n{'=' * 60}")
    print("[OK] Test abgeschlossen - Verbindung geschlossen")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    test_connection()
