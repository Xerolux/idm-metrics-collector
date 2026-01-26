import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestMLAlertAnnotation(unittest.TestCase):
    def setUp(self):
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        # Mock modules
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": MagicMock(),
                "idm_logger.mqtt": MagicMock(),
                "idm_logger.scheduler": MagicMock(),
                "idm_logger.modbus": MagicMock(),
            },
        )
        self.modules_patcher.start()

        # Import config with json.loads patched to avoid db error
        with patch("json.loads", return_value={}):
            pass

        # Patch config instance
        self.config_patcher = patch("idm_logger.config.config")
        self.mock_config = self.config_patcher.start()

        # Configure config
        self.mock_config.get_flask_secret_key.return_value = "secret"
        self.mock_config.get.side_effect = (
            lambda k, d=None: "secret" if k == "internal_api_key" else d
        )
        self.mock_config.data = {}

        # Import web
        import idm_logger.web as web

        self.web = web
        self.app = web.app
        self.client = self.app.test_client()

        # Patch managers
        self.web.annotation_manager = MagicMock()
        self.web.notification_manager = MagicMock()

    def tearDown(self):
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
