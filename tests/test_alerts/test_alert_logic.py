# SPDX-License-Identifier: MIT
"""Tests for alert manager logic."""

import unittest
import time
from unittest.mock import MagicMock, patch, ANY
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import helper from conftest
from tests.conftest import create_mock_db_module


class TestAlertManager(unittest.TestCase):
    def setUp(self):
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        # Create properly configured mock db module
        self.mock_db_module = create_mock_db_module()
        self.mock_db = self.mock_db_module.db
        self.mock_db.get_alerts.return_value = []

        # Patch modules before importing alerts
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": self.mock_db_module,
            },
        )
        self.modules_patcher.start()

        # We need to patch the notification_manager in alerts.py
        self.notification_manager_patcher = patch(
            "idm_logger.alerts.notification_manager"
        )
        self.mock_notification_manager = self.notification_manager_patcher.start()

        # Now import AlertManager
        from idm_logger.alerts import AlertManager

        self.AlertManager = AlertManager
        self.alert_manager = AlertManager()

    def tearDown(self):
        self.notification_manager_patcher.stop()
        self.modules_patcher.stop()
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

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
