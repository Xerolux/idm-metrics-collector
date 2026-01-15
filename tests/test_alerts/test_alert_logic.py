import unittest
import time
from unittest.mock import MagicMock, patch, ANY
import sys
import os

# Add repo root to path
sys.path.append(os.getcwd())

from idm_logger.alerts import AlertManager

class TestAlertManager(unittest.TestCase):
    def setUp(self):
        # Mock database and configuration
        self.mock_db = MagicMock()
        self.mock_config = MagicMock()

        # Patch db and config in the alerts module
        self.db_patcher = patch('idm_logger.alerts.db', self.mock_db)
        self.config_patcher = patch('idm_logger.alerts.config', self.mock_config)
        self.db_patcher.start()
        self.config_patcher.start()

        # Default mock config
        self.mock_config.get.return_value = True # signal.enabled = True
        self.mock_db.get_alerts.return_value = []

        self.alert_manager = AlertManager()

        # Patch send_signal_message
        self.send_patcher = patch('idm_logger.alerts.send_signal_message')
        self.mock_send = self.send_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()
        self.config_patcher.stop()
        self.send_patcher.stop()

    def test_threshold_alert_gt(self):
        # Setup alert
        alert = {
            'id': '1',
            'name': 'Test Alert',
            'type': 'threshold',
            'sensor': 'temp',
            'condition': '>',
            'threshold': 50,
            'message': 'High Temp: {value}',
            'enabled': True,
            'interval_seconds': 60,
            'last_triggered': 0
        }
        self.alert_manager.alerts = [alert]

        # Test case 1: Value below threshold
        self.alert_manager.check_alerts({'temp': 40})
        self.mock_send.assert_not_called()

        # Test case 2: Value above threshold
        self.alert_manager.check_alerts({'temp': 60})
        self.mock_send.assert_called_with('High Temp: 60')
        self.mock_db.update_alerts_last_triggered.assert_called_once_with(['1'], ANY)

    def test_threshold_alert_cooldown(self):
        # Setup alert with triggered state
        now = time.time()
        alert = {
            'id': '1',
            'name': 'Test Alert',
            'type': 'threshold',
            'sensor': 'temp',
            'condition': '>',
            'threshold': 50,
            'message': 'High Temp',
            'enabled': True,
            'interval_seconds': 60,
            'last_triggered': now - 30 # Only 30s ago
        }
        self.alert_manager.alerts = [alert]

        # Should not trigger due to cooldown
        self.alert_manager.check_alerts({'temp': 60})
        self.mock_send.assert_not_called()

        # Adjust time to be past cooldown
        alert['last_triggered'] = now - 70
        self.alert_manager.check_alerts({'temp': 60})
        self.mock_send.assert_called()

    def test_status_alert(self):
        # Setup status alert
        alert = {
            'id': '2',
            'name': 'Status Report',
            'type': 'status',
            'message': 'Status OK',
            'enabled': True,
            'interval_seconds': 3600,
            'last_triggered': 0
        }
        self.alert_manager.alerts = [alert]

        # Should trigger
        self.alert_manager.check_alerts({})
        self.mock_send.assert_called_with('Status OK')

if __name__ == '__main__':
    unittest.main()
