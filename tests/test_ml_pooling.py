import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the parent directory is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies that are not available in the environment
sys.modules["requests"] = MagicMock()
sys.modules["torch"] = MagicMock()
sys.modules["torch.nn"] = MagicMock()
sys.modules["torch.nn.Module"] = MagicMock
sys.modules["schedule"] = MagicMock()
sys.modules["flask"] = MagicMock()

import ml_service.main as main  # noqa: E402


class TestMLServicePooling(unittest.TestCase):
    def test_http_session_initialized(self):
        """Test that the global http_session is initialized."""
        self.assertIsNotNone(main.http_session)

    @patch("ml_service.main.http_session.post")
    def test_fetch_latest_data_uses_session(self, mock_post):
        """Test that fetch_latest_data uses the global session."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "data": {"result": []},
        }

        main.SENSORS = ["sensor1"]
        main.fetch_latest_data()

        mock_post.assert_called()

    @patch("ml_service.main.http_session.post")
    def test_write_metrics_uses_session(self, mock_post):
        """Test that write_metrics uses the global session."""
        mock_post.return_value.status_code = 204

        main.write_metrics(0.1, False, 1, 0.05, "standby")

        mock_post.assert_called()

    @patch("ml_service.main.http_session.post")
    def test_send_anomaly_alert_uses_session(self, mock_post):
        """Test that send_anomaly_alert uses the global session."""
        mock_post.return_value.status_code = 200

        # Ensure cooldown doesn't prevent call
        main.last_alert_time = 0
        main.ENABLE_ALERTS = True

        main.send_anomaly_alert(0.9, {"sensor": 1}, "heating", [])

        mock_post.assert_called()

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_uses_session(self, mock_get):
        """Test that fetch_remote_config uses the global session."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"threshold": 0.8}

        main.fetch_remote_config()

        mock_get.assert_called()

    @patch("ml_service.main.http_session.get")
    @patch("time.sleep", side_effect=InterruptedError)  # Break the loop
    def test_wait_for_connection_uses_session(self, mock_sleep, mock_get):
        """Test that wait_for_connection uses the global session."""
        mock_get.return_value.status_code = 200

        try:
            main.wait_for_connection()
        except InterruptedError:
            pass

        mock_get.assert_called()


if __name__ == "__main__":
    unittest.main()
