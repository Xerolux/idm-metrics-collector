import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the parent directory is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestMLServicePooling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock dependencies that are not available in the environment
        cls.patcher = patch.dict(
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
        cls.patcher.start()

        # Import main after modules are patched
        import ml_service.main as main
        cls.main = main

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_http_session_initialized(self):
        """Test that the global http_session is initialized."""
        self.assertIsNotNone(self.main.http_session)

    @patch("ml_service.main.http_session.post")
    def test_fetch_latest_data_uses_session(self, mock_post):
        """Test that fetch_latest_data uses the global session."""
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
        """Test that write_metrics uses the global session."""
        mock_post.return_value.status_code = 204

        self.main.write_metrics(0.1, False, 1, 0.05, "standby")

        mock_post.assert_called()

    @patch("ml_service.main.http_session.post")
    def test_send_anomaly_alert_uses_session(self, mock_post):
        """Test that send_anomaly_alert uses the global session."""
        mock_post.return_value.status_code = 200

        # Ensure cooldown doesn't prevent call
        self.main.last_alert_time = 0
        self.main.ENABLE_ALERTS = True

        self.main.send_anomaly_alert(0.9, {"sensor": 1}, "heating", [])

        mock_post.assert_called()

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_uses_session(self, mock_get):
        """Test that fetch_remote_config uses the global session."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"threshold": 0.8}

        self.main.fetch_remote_config()

        mock_get.assert_called()

    @patch("ml_service.main.http_session.get")
    @patch("time.sleep", side_effect=InterruptedError)  # Break the loop
    def test_wait_for_connection_uses_session(self, mock_sleep, mock_get):
        """Test that wait_for_connection uses the global session."""
        mock_get.return_value.status_code = 200

        try:
            self.main.wait_for_connection()
        except InterruptedError:
            pass

        mock_get.assert_called()


if __name__ == "__main__":
    unittest.main()
