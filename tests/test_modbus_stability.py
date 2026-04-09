# Xerolux 2026
# SPDX-License-Identifier: MIT
import unittest
from unittest.mock import MagicMock, patch

from idm_logger.modbus import ModbusClient, _normalize_binary_value
from idm_logger.sensor_addresses import IdmBinarySensorAddress, SensorFeatures


class TestModbusWriteStability(unittest.TestCase):
    def test_normalize_binary_value_accepts_supported_types(self):
        self.assertTrue(_normalize_binary_value(True))
        self.assertFalse(_normalize_binary_value(False))
        self.assertTrue(_normalize_binary_value(1))
        self.assertFalse(_normalize_binary_value(0))
        self.assertTrue(_normalize_binary_value("yes"))
        self.assertFalse(_normalize_binary_value("off"))

    def test_normalize_binary_value_rejects_unsupported_values(self):
        with self.assertRaises(ValueError):
            _normalize_binary_value(2)

        with self.assertRaises(ValueError):
            _normalize_binary_value("maybe")

        with self.assertRaises(ValueError):
            _normalize_binary_value(1.0)

    @patch("idm_logger.modbus.ModbusTcpClient")
    def test_write_sensor_accepts_bool_int_and_string_for_binary(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.is_socket_open.return_value = True
        write_rr = MagicMock()
        write_rr.isError.return_value = False
        mock_client.write_registers.return_value = write_rr

        client = ModbusClient("localhost", 502)
        client.binary_sensors = {
            "relay": IdmBinarySensorAddress(
                address=1234, name="relay", supported_features=SensorFeatures.SET_BINARY
            )
        }
        client.sensors = {}

        self.assertTrue(client.write_sensor("relay", True))
        self.assertTrue(client.write_sensor("relay", 1))
        self.assertTrue(client.write_sensor("relay", "off"))

        calls = mock_client.write_registers.call_args_list
        self.assertEqual(calls[0].args[1], [1])
        self.assertEqual(calls[1].args[1], [1])
        self.assertEqual(calls[2].args[1], [0])

    @patch("idm_logger.modbus.ModbusTcpClient")
    def test_write_sensor_rejects_invalid_binary_input(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.is_socket_open.return_value = True

        client = ModbusClient("localhost", 502)
        client.binary_sensors = {
            "relay": IdmBinarySensorAddress(
                address=1234, name="relay", supported_features=SensorFeatures.SET_BINARY
            )
        }
        client.sensors = {}

        with self.assertRaises(ValueError):
            client.write_sensor("relay", 2)

        mock_client.write_registers.assert_not_called()


class TestModbusReadStability(unittest.TestCase):
    @patch("idm_logger.modbus.ModbusTcpClient")
    def test_read_sensors_falls_back_on_short_bulk_response(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.is_socket_open.return_value = True

        short_rr = MagicMock()
        short_rr.isError.return_value = False
        short_rr.registers = []

        ok_rr = MagicMock()
        ok_rr.isError.return_value = False
        ok_rr.registers = [1, 2]

        # 1st call: short bulk response, 2nd call: individual fallback response
        mock_client.read_holding_registers.side_effect = [short_rr, ok_rr]

        client = ModbusClient("localhost", 502)
        sensor = IdmBinarySensorAddress(address=2000, name="binary_test")
        client.sensors = {}
        client.binary_sensors = {"binary_test": sensor}
        client.invalidate_cache()

        data = client.read_sensors()

        self.assertIn("binary_test", data)
        self.assertGreater(client.get_connection_stats()["total_read_errors"], 0)
        self.assertEqual(mock_client.read_holding_registers.call_count, 2)


if __name__ == "__main__":
    unittest.main()
