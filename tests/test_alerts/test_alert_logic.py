# Xerolux 2026
# SPDX-License-Identifier: MIT
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
        self.mock_config = MagicMock()  # This is likely failing because `from .config import config` in alerts.py doesn't expose 'config' as an attribute of the module in the way patch expects if it was imported differently or if patch can't find it.
        # Actually, in idm_logger/alerts.py we do `from .config import config`. So `idm_logger.alerts.config` should exist.
        # But wait, I refactored alerts.py to use `idm_logger.notifications.notification_manager`.

        # Patch db
        self.db_patcher = patch("idm_logger.alerts.db", self.mock_db)
        self.db_patcher.start()

        self.mock_db.get_alerts.return_value = []

        # We need to patch the notification_manager in alerts.py, not config or send_signal_message anymore.
        self.notification_manager_patcher = patch(
            "idm_logger.alerts.notification_manager"
        )
        self.mock_notification_manager = self.notification_manager_patcher.start()

        self.alert_manager = AlertManager()

    def tearDown(self):
        self.db_patcher.stop()
        self.notification_manager_patcher.stop()

    def test_threshold_alert_gt(self):
        # Setup alert
        alert = {
            "id": "1",
            "name": "Test Alert",
            "type": "threshold",
            "sensor": "temp",
            "condition": ">",
            "threshold": 50,
            "message": "High Temp: {value}",
            "enabled": True,
            "interval_seconds": 60,
            "last_triggered": 0,
        }
        self.alert_manager.alerts = [alert]

        # Test case 1: Value below threshold
        self.alert_manager.check_alerts({"temp": 40})
        self.mock_notification_manager.send_all.assert_not_called()

        # Test case 2: Value above threshold
        self.alert_manager.check_alerts({"temp": 60})
        self.mock_notification_manager.send_all.assert_called_with(
            "High Temp: 60", subject="IDM Alert: Test Alert"
        )
        self.mock_db.update_alerts_last_triggered.assert_called_once_with(["1"], ANY)

    def test_threshold_alert_cooldown(self):
        # Setup alert with triggered state
        now = time.time()
        alert = {
            "id": "1",
            "name": "Test Alert",
            "type": "threshold",
            "sensor": "temp",
            "condition": ">",
            "threshold": 50,
            "message": "High Temp",
            "enabled": True,
            "interval_seconds": 60,
            "last_triggered": now - 30,  # Only 30s ago
        }
        self.alert_manager.alerts = [alert]

        # Should not trigger due to cooldown
        self.alert_manager.check_alerts({"temp": 60})
        self.mock_notification_manager.send_all.assert_not_called()

        # Adjust time to be past cooldown
        alert["last_triggered"] = now - 70
        self.alert_manager.check_alerts({"temp": 60})
        self.mock_notification_manager.send_all.assert_called()

    def test_status_alert(self):
        # Setup status alert
        alert = {
            "id": "2",
            "name": "Status Report",
            "type": "status",
            "message": "Status OK",
            "enabled": True,
            "interval_seconds": 3600,
            "last_triggered": 0,
        }
        self.alert_manager.alerts = [alert]

        # Should trigger
        self.alert_manager.check_alerts({})
        self.mock_notification_manager.send_all.assert_called_with(
            "Status OK", subject="IDM Alert: Status Report"
        )


if __name__ == "__main__":
    unittest.main()
