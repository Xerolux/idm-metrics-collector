import unittest
from unittest.mock import MagicMock, patch
import asyncio
from idm_logger.heatpump_manager import HeatpumpManager, HeatpumpConnection


class TestHeatpumpManagerPatch(unittest.TestCase):
    @patch("idm_logger.heatpump_manager.ModbusTcpClient")
    def test_modbus_calls_use_device_id(self, mock_client_cls):
        # Setup
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.connect.return_value = True

        # Mock read result
        mock_read_result = MagicMock()
        mock_read_result.isError.return_value = False
        mock_read_result.registers = [123]
        mock_client.read_holding_registers.return_value = mock_read_result

        # Mock write result
        mock_write_result = MagicMock()
        mock_write_result.isError.return_value = False
        mock_client.write_registers.return_value = mock_write_result

        # Create connection object manually to avoid full manager init overhead
        conn = HeatpumpConnection(
            id="test_hp",
            name="Test HP",
            manufacturer="test",
            model="test",
            driver=MagicMock(),
            client=mock_client,
            sensors=[],
            unit_id=42,
        )

        manager = HeatpumpManager()
        # Inject connection
        manager._connections["test_hp"] = conn

        # Test Read
        # We need to test the private method _read_registers or ensure public read calls it
        # _read_registers is async

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Call _read_registers
        loop.run_until_complete(manager._read_registers(conn, 100, 2))

        # Verify read call used device_id
        mock_client.read_holding_registers.assert_called_with(
            100, count=2, device_id=42
        )

        # Test Write
        # We need a dummy sensor
        sensor = MagicMock()
        sensor.id = "s1"
        sensor.is_writable = True
        sensor.address = 200
        conn.sensors = [sensor]
        conn.driver.encode_value.return_value = [1]

        loop.run_until_complete(manager.write_value("test_hp", "s1", 1))

        # Verify write call used device_id
        mock_client.write_registers.assert_called_with(200, [1], device_id=42)

        loop.close()


if __name__ == "__main__":
    unittest.main()
