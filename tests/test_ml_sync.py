import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.getcwd())

# Create mocks for external dependencies not present in CI root environment
mock_torch = MagicMock()
sys.modules["torch"] = mock_torch
sys.modules["torch.nn"] = MagicMock()
sys.modules["schedule"] = MagicMock()
sys.modules["joblib"] = MagicMock()

# Set env vars
os.environ["ANOMALY_THRESHOLD"] = "0.85"
os.environ["IDM_LOGGER_URL"] = "http://test-logger"
os.environ["INTERNAL_API_KEY"] = "test-key"
# Prevent GPU usage or other side effects if torch was real
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Import ml_service.main
try:
    import ml_service.main as ml_main
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)


class TestMLSync(unittest.TestCase):
    def setUp(self):
        # Reset global threshold
        ml_main.ANOMALY_THRESHOLD = 0.85
        # Ensure logger is configured to not spam
        ml_main.logger.setLevel(logging.CRITICAL)

    def tearDown(self):
        pass

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"sensitivity": 5.0, "threshold": 0.85}
        mock_get.return_value = mock_response

        # Call function
        ml_main.fetch_remote_config()

        # Check if threshold updated
        self.assertAlmostEqual(ml_main.ANOMALY_THRESHOLD, 0.85, places=3)

        # Verify request
        mock_get.assert_called_with(
            "http://test-logger/api/internal/ml_config",
            headers={"X-Internal-Secret": "test-key"},
            timeout=2,
        )

    @patch("ml_service.main.http_session.get")
    def test_fetch_remote_config_failure(self, mock_get):
        # Mock failure response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Call function
        ml_main.fetch_remote_config()

        # Check threshold remains unchanged
        self.assertEqual(ml_main.ANOMALY_THRESHOLD, 0.85)

    @patch("ml_service.main.requests.get")
    def test_fetch_remote_config_exception(self, mock_get):
        # Mock exception
        mock_get.side_effect = Exception("Connection error")

        # Call function (should not crash)
        ml_main.fetch_remote_config()

        # Check threshold remains unchanged
        self.assertEqual(ml_main.ANOMALY_THRESHOLD, 0.85)

    @patch("ml_service.main.fetch_remote_config")
    @patch("ml_service.main.fetch_latest_data")
    def test_job_calls_fetch_config(self, mock_fetch_data, mock_fetch_config):
        # Mock data fetch to return None to exit early
        mock_fetch_data.return_value = None

        # Call job
        ml_main.job()

        # Verify fetch_remote_config was called
        mock_fetch_config.assert_called_once()


if __name__ == "__main__":
    unittest.main()
