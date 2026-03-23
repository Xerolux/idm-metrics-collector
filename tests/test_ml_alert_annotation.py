# Xerolux 2026
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestMLAlertAnnotation(unittest.TestCase):
    def setUp(self):
        # Mock modules
        mock_db_module = MagicMock()
        mock_db_object = MagicMock()
        mock_db_object.get_setting.return_value = None
        mock_db_module.db = mock_db_object

        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": mock_db_module,
                "idm_logger.mqtt": MagicMock(),
                "idm_logger.scheduler": MagicMock(),
                "idm_logger.modbus": MagicMock(),
            },
        )
        self.modules_patcher.start()

        # Patch config instance
        self.config_patcher = patch("idm_logger.web.config")
        self.mock_config = self.config_patcher.start()

        # Configure config
        self.mock_config.get_flask_secret_key.return_value = "secret"
        self.mock_config.internal_api_key = "secret"
        self.mock_config.api_whitelist = ["127.0.0.0/8"]

        def config_get(k, default=None):
            if k == "internal_api_key":
                return "secret"
            if k == "RATELIMIT_STORAGE_URI":
                return "memory://"
            return default

        self.mock_config.get.side_effect = config_get
        self.mock_config.data = {}
        self.mock_config.setdefault.side_effect = lambda k, default=None: default

        # Because web.py imports config from idm_logger.config at the top level
        # and we mocked it inside idm_logger.web, it's safer to mock idm_logger.config.config
        # before reloading
        self.global_config_patcher = patch("idm_logger.config.config", self.mock_config)
        self.global_config_patcher.start()

        # Import web
        import importlib
        import idm_logger.web as web

        importlib.reload(web)

        self.web = web
        self.app = web.app
        self.client = self.app.test_client()

        # Patch managers
        self.web.annotation_manager = MagicMock()
        self.web.notification_manager = MagicMock()

    def tearDown(self):
        self.global_config_patcher.stop()
        self.config_patcher.stop()
        self.modules_patcher.stop()

    def test_alert_creates_annotation(self):
        payload = {
            "score": 0.8,
            "threshold": 0.7,
            "message": "Test Alert",
            "data": {
                "mode": "heating",
                "top_features": [{"feature": "temp_out", "score": 2.5}],
            },
        }

        headers = {"X-Internal-Secret": "secret", "Content-Type": "application/json"}

        response = self.client.post(
            "/api/internal/ml_alert", data=json.dumps(payload), headers=headers
        )

        self.assertEqual(response.status_code, 200)

        self.web.notification_manager.send_all.assert_called_with(
            message="Test Alert", subject="IDM ML Anomalie-Warnung"
        )

        self.web.annotation_manager.add_annotation.assert_called()
        args, kwargs = self.web.annotation_manager.add_annotation.call_args

        self.assertEqual(kwargs["text"], "Test Alert")
        self.assertEqual(kwargs["tags"], ["ai", "anomaly", "heating"])
        self.assertEqual(kwargs["color"], "#ef4444")


if __name__ == "__main__":
    unittest.main()
