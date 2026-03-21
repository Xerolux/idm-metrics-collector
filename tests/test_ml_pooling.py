import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Only mock missing packages, but keep 'flask' intact if installed
# In the test environment, we might have flask installed.


# DO NOT mock globally. We use patch.dict
class TestMLServicePooling(unittest.TestCase):
    def setUp(self):
        # We mock what we need specifically for ml_service.main using patch.dict
        self.mock_sys_modules = {
            "torch": MagicMock(),
            "torch.nn": MagicMock(),
            "torch.nn.Module": MagicMock,
            "schedule": MagicMock(),
        }
        self.module_patcher = patch.dict(sys.modules, self.mock_sys_modules)
        self.module_patcher.start()

        import ml_service.main as main

        self.main = main

    def tearDown(self):
        self.module_patcher.stop()

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
        self.main.ENABLE_ALERTS = True

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
