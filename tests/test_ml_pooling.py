import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestMLServicePooling(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.dict(
            sys.modules,
            {
                "requests": MagicMock(),
                "torch": MagicMock(),
                "torch.nn": MagicMock(),
                "torch.nn.Module": MagicMock,
                "schedule": MagicMock(),
                "flask": MagicMock(),
            },
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

        import ml_service.config as ml_config
        import ml_service.main as main

        importlib.reload(ml_config)
        importlib.reload(main)
        self.main = main

    def test_http_session_initialized(self):
        self.assertIsNotNone(self.main.http_session)

    @patch("ml_service.main.http_session.post")
    def test_fetch_latest_data_uses_session(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "data": {"result": []},
        }

        self.main.SENSORS = ["sensor1"]
        self.main.fetch_latest_data()

        mock_post.assert_called()

    @patch("ml_service.main.http_session.post")
    def test_write_metrics_uses_session(self, mock_post):
        mock_post.return_value.status_code = 204

        self.main.write_metrics(0.1, False, 1, 0.05, "standby")

        mock_post.assert_called()

    @patch("ml_service.main.http_session.post")
    def test_send_anomaly_alert_uses_session(self, mock_post):
        mock_post.return_value.status_code = 200

        self.main.last_alert_time = 0

        with patch("ml_service.main.config") as mock_cfg:
            mock_cfg.enable_alerts = True
            mock_cfg.alert_cooldown = 3600
            mock_cfg.anomaly_threshold = 0.85
            mock_cfg.idm_logger_url = "http://test-logger"
            mock_cfg.internal_api_key = "test-key"
            mock_cfg.retry_base_delay = 1.0
            mock_cfg.retry_multiplier = 2.0
            mock_cfg.retry_max_delay = 60.0
            mock_cfg.retry_max_attempts = 3
            self.main.send_anomaly_alert(0.9, {"sensor": 1}, "heating", [])

        mock_post.assert_called()

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_uses_session(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"threshold": 0.8}

        self.main.fetch_remote_config()

        mock_get.assert_called()

    @patch("ml_service.main.http_session.get")
    @patch("time.sleep", side_effect=InterruptedError)
    def test_wait_for_connection_uses_session(self, mock_sleep, mock_get):
        mock_get.return_value.status_code = 200

        try:
            self.main.wait_for_connection()
        except InterruptedError:
            pass

        mock_get.assert_called()


if __name__ == "__main__":
    unittest.main()
