import json
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import collections

# Mock the logger to suppress output during tests
with patch("logging.getLogger"):
    from idm_logger.ai.anomaly import AnomalyDetector, ANOMALY_STATE_FILE

class TestAIHistory(unittest.TestCase):

    def setUp(self):
        # Ensure we start with a fresh instance for each test
        # We need to patch os.path.exists to return False so it tries to fetch from DB
        self.patcher_exists = patch("os.path.exists", return_value=False)
        self.mock_exists = self.patcher_exists.start()

        # Patch requests.get
        self.patcher_requests = patch("requests.get")
        self.mock_get = self.patcher_requests.start()

        # Patch config
        self.patcher_config = patch("idm_logger.ai.anomaly.config")
        self.mock_config = self.patcher_config.start()
        # Default config behavior
        self.mock_config.get.side_effect = lambda key, default=None: {
            "metrics.url": "http://victoriametrics:8428/write",
            "metrics.measurement": "idm_heatpump",
            "metrics.db": "prometheus"
        }.get(key, default)

        # Patch open to prevent file writing during save()
        self.patcher_open = patch("builtins.open", mock_open())
        self.mock_open = self.patcher_open.start()

    def tearDown(self):
        self.patcher_exists.stop()
        self.patcher_requests.stop()
        self.patcher_config.stop()
        self.patcher_open.stop()

    def test_fetch_history_success(self):
        # Mock successful DB response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{
                "series": [{
                    "name": "idm_heatpump",
                    "columns": ["time", "temp_out", "power_usage"],
                    "values": [
                        [1620000060000, 10.5, 2000], # Newest (index 0)
                        [1620000000000, 10.0, 1500], # Oldest (index 1)
                    ]
                }]
            }]
        }
        self.mock_get.return_value = mock_response

        # Instantiate AnomalyDetector, which calls load(), which calls fetch_history_from_db()
        detector = AnomalyDetector()

        # Verify requests.get was called with correct URL and query
        expected_url = "http://victoriametrics:8428/query"
        self.mock_get.assert_called_once()
        args, kwargs = self.mock_get.call_args
        self.assertEqual(args[0], expected_url)
        self.assertIn("q", kwargs["params"])
        self.assertIn("SELECT * FROM idm_heatpump ORDER BY time DESC LIMIT 25000", kwargs["params"]["q"])

        # Verify data was loaded into models
        # RollingWindow should have history
        rolling_model = detector.models["rolling"]
        self.assertIn("temp_out", rolling_model.history)
        self.assertIn("power_usage", rolling_model.history)

        # Check values (remember fetch_history reverses the list)
        # So it processes [10.0, 1500] then [10.5, 2000]
        self.assertEqual(list(rolling_model.history["temp_out"]), [10.0, 10.5])
        self.assertEqual(list(rolling_model.history["power_usage"]), [1500, 2000])

    def test_url_parsing(self):
        """Test different URL formats to ensure robust parsing."""
        # Case 1: Trailing slash
        self.mock_config.get.side_effect = lambda key, default=None: {
            "metrics.url": "http://vm:8428/write/",
        }.get(key, default)

        # We need to reset the detector or mock method to check the call
        # Since __init__ calls it, we just create a new one.
        # We need to reset the mock_get
        self.mock_get.reset_mock()
        self.mock_get.return_value.status_code = 500 # Just to stop execution early

        AnomalyDetector()
        args, _ = self.mock_get.call_args
        self.assertEqual(args[0], "http://vm:8428/query")

        # Case 2: Custom path
        self.mock_get.reset_mock()
        self.mock_config.get.side_effect = lambda key, default=None: {
            "metrics.url": "http://vm:8428/api/v1/write",
        }.get(key, default)

        AnomalyDetector()
        args, _ = self.mock_get.call_args
        self.assertEqual(args[0], "http://vm:8428/api/v1/query")

    def test_fetch_history_failure(self):
        # Mock failed DB response
        mock_response = MagicMock()
        mock_response.status_code = 500
        self.mock_get.return_value = mock_response

        detector = AnomalyDetector()

        # Verify no data loaded (empty models)
        rolling_model = detector.models["rolling"]
        self.assertEqual(len(rolling_model.history), 0)

if __name__ == "__main__":
    unittest.main()
