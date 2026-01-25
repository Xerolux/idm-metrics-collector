
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Add repo root to path so we can import ml_service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies that might be missing or strictly configured
sys.modules['schedule'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['flask'] = MagicMock()
sys.modules['river'] = MagicMock()
sys.modules['river.anomaly'] = MagicMock()
sys.modules['river.preprocessing'] = MagicMock()
sys.modules['river.compose'] = MagicMock()
sys.modules['idm_logger.sensor_addresses'] = MagicMock()

# Patch environment variables BEFORE importing main
with patch.dict(os.environ, {
    "METRICS_URL": "http://test-vm",
    "MIN_DATA_RATIO": "0.4", # Intentionally high to test the override logic
    "MODEL_PATH": "/tmp/test_model.pkl"
}):
    from ml_service import main

class TestMLServiceLogic(unittest.TestCase):

    def setUp(self):
        # Reset globals
        main.SENSORS = ["sensor1", "sensor2", "sensor3", "sensor4", "sensor5"]
        main.model = MagicMock()
        main.logger = MagicMock()

    @patch('ml_service.main.fetch_latest_data')
    @patch('ml_service.main.write_metrics')
    @patch('ml_service.main.enrich_features')
    def test_job_proceeds_with_partial_data(self, mock_enrich, mock_write, mock_fetch):
        """Test that job() proceeds even if data count < min_features."""
        # Setup: 5 sensors, MIN_DATA_RATIO=0.4 => need 2 sensors.
        # But we only return 1 sensor.
        # With the fix, it should proceed.

        mock_fetch.return_value = {"sensor1": 10.0} # Only 1 sensor
        mock_enrich.return_value = {"sensor1": 10.0, "extra": 1} # Enriched

        main.model.score_one.return_value = 0.5

        # Run job
        main.job()

        # Verify warnings were logged
        main.logger.warning.assert_called()
        args, _ = main.logger.warning.call_args
        self.assertIn("Low data availability", args[0])

        # Verify metrics WERE written (Crucial check)
        mock_write.assert_called_once()

        # Verify model was updated
        main.model.learn_one.assert_called_once()

    @patch('ml_service.main.fetch_latest_data')
    @patch('ml_service.main.write_metrics')
    def test_job_aborts_on_no_data(self, mock_write, mock_fetch):
        """Test that job() aborts if NO data is fetched (empty dict or None)."""
        mock_fetch.return_value = {} # Empty dict

        main.job()

        # Should not write metrics
        mock_write.assert_not_called()
        main.model.learn_one.assert_not_called()

    def test_persistence_pickle(self):
        """Test save and load model state using pickle (mocked)."""
        main.USE_JOBLIB = False
        main.model = "test_model_obj"

        # Test Save
        with patch('builtins.open', mock_open()) as m:
            with patch('pickle.dump') as mock_dump:
                main.save_model_state()
                m.assert_called_with(main.MODEL_PATH, 'wb')
                mock_dump.assert_called_with("test_model_obj", m())

        # Test Load
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=b'data')) as m:
                with patch('pickle.load', return_value="loaded_model"):
                    res = main.load_model_state()
                    self.assertTrue(res)
                    self.assertEqual(main.model, "loaded_model")

if __name__ == '__main__':
    unittest.main()
