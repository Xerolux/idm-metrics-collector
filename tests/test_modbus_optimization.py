# Xerolux 2026
# SPDX-License-Identifier: MIT
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from idm_logger.modbus import ModbusClient
from idm_logger.sensor_addresses import _FloatSensorAddress


class TestModbusOptimization(unittest.TestCase):
    @patch("idm_logger.modbus.ModbusTcpClient")
    def test_block_creation(self, mock_client):
        # Create instance with mocked client
        client = ModbusClient("localhost", 502)

        # Override sensors with a controlled set for testing
        # 1. Block 1: 100, 102, 104 (Contiguous-ish)
        # 2. Gap: 150 (Should start new block)
        # 3. Block 2: 150, 152
        # 4. Forbidden: 160 (read_supported=False)
        # 5. Block 3: 162 (Should be separate from 152 because of 160 gap?
        #    Wait, 152+2 = 154. Gap to 162 is 8.
        #    If 160 is forbidden, and we try to read 154-162 (range), it includes 160.
        #    So it should split.

        s1 = _FloatSensorAddress(address=100, name="s1", unit="C")
        s2 = _FloatSensorAddress(address=102, name="s2", unit="C")
        s3 = _FloatSensorAddress(address=104, name="s3", unit="C")

        s4 = _FloatSensorAddress(address=150, name="s4", unit="C")
        s5 = _FloatSensorAddress(address=152, name="s5", unit="C")

        s_forbidden = _FloatSensorAddress(
            address=160, name="s_forbidden", unit="C", read_supported=False
        )

        s6 = _FloatSensorAddress(address=162, name="s6", unit="C")

        client.sensors = {
            "s1": s1,
            "s2": s2,
            "s3": s3,
            "s4": s4,
            "s5": s5,
            "s_forbidden": s_forbidden,
            "s6": s6,
        }
        client.binary_sensors = {}

        # Force rebuild blocks
        blocks = client._build_read_blocks()

        # Expected blocks:
        # [s1, s2, s3] -> 100-106 (size 6)
        # [s4, s5]     -> 150-154 (size 4)
        # [s6]         -> 162-164 (size 2)
        # Note: s5 ends at 154. s6 starts at 162. Gap is 8.
        # Max gap is 10. So normally they would merge.
        # BUT 160 is forbidden.
        # Range 154 to 162 covers 154, 155, ... 160, 161.
        # So 160 is inside the gap.
        # So it SHOULD split.

        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0], [s1, s2, s3])
        self.assertEqual(blocks[1], [s4, s5])
        self.assertEqual(blocks[2], [s6])

    @patch("idm_logger.modbus.ModbusTcpClient")
    def test_read_requests(self, mock_client_cls):
        # Setup mock instance
        mock_instance = mock_client_cls.return_value
        mock_instance.connect.return_value = True
        mock_instance.is_socket_open.return_value = True

        # Mock response
        # We need to return an object that has .isError() and .registers
        mock_rr = MagicMock()
        mock_rr.isError.return_value = False
        # Just return enough zeros
        mock_rr.registers = [0] * 100
        mock_instance.read_holding_registers.return_value = mock_rr

        client = ModbusClient("localhost", 502)

        # Use default sensors (COMMON_SENSORS)
        # There are about 80 sensors.
        # Without optimization, it would be 80 requests.
        # With optimization, it should be much less (e.g. < 25).

        client.read_sensors()

        # Check call count
        call_count = mock_instance.read_holding_registers.call_count
        print(f"DEBUG: Optimized call count: {call_count}")

        # Assert it's significantly less than number of sensors (approx 80-90)
        self.assertLess(call_count, 35)

        # Also ensure it's > 0
        self.assertGreater(call_count, 0)


if __name__ == "__main__":
    unittest.main()
