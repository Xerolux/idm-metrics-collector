import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.getcwd())

# Create mocks for dependencies
mock_torch = MagicMock()
sys.modules['torch'] = mock_torch
sys.modules['torch.nn'] = MagicMock()
sys.modules['schedule'] = MagicMock()
sys.modules['joblib'] = MagicMock()

# Mock idm_logger structure BEFORE importing ml_service.main
mock_idm_logger = MagicMock()
sys.modules['idm_logger'] = mock_idm_logger

mock_sensor_addresses = MagicMock()
sys.modules['idm_logger.sensor_addresses'] = mock_sensor_addresses
mock_sensor_addresses.COMMON_SENSORS = []
mock_sensor_addresses.BINARY_SENSOR_ADDRESSES = {}
mock_sensor_addresses.heating_circuit_sensors = MagicMock(return_value=[])
mock_sensor_addresses.zone_sensors = MagicMock(return_value=[])
mock_sensor_addresses.HeatingCircuit = MagicMock()

mock_const = MagicMock()
sys.modules['idm_logger.const'] = mock_const
mock_const.HeatPumpStatus = MagicMock()

# Set env vars
os.environ['ANOMALY_THRESHOLD'] = '0.7'
os.environ['IDM_LOGGER_URL'] = 'http://test-logger'
os.environ['INTERNAL_API_KEY'] = 'test-key'
# Prevent GPU usage or other side effects if torch was real
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Import ml_service.main
try:
    # We need to make sure we import from the file path because it's not a package
    # But sys.path has cwd, so 'ml_service.main' should be importable if ml_service is a package
    # Check if ml_service has __init__.py
    if not os.path.exists('ml_service/__init__.py'):
        # Create empty __init__.py to make it a package for import
        with open('ml_service/__init__.py', 'w') as f:
            pass

    import ml_service.main as ml_main
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

class TestMLSync(unittest.TestCase):
    def setUp(self):
        # Reset global threshold
        ml_main.ANOMALY_THRESHOLD = 0.7
        # Ensure logger is configured to not spam
        ml_main.logger.setLevel(logging.CRITICAL)

    def tearDown(self):
        pass

    @patch('ml_service.main.requests.get')
    def test_fetch_remote_config_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sensitivity": 5.0,
            "threshold": 0.774
        }
        mock_get.return_value = mock_response

        # Call function
        ml_main.fetch_remote_config()

        # Check if threshold updated
        self.assertAlmostEqual(ml_main.ANOMALY_THRESHOLD, 0.774, places=3)

        # Verify request
        mock_get.assert_called_with(
            'http://test-logger/api/internal/ml_config',
            headers={'X-Internal-Secret': 'test-key'},
            timeout=2
        )

    @patch('ml_service.main.requests.get')
    def test_fetch_remote_config_failure(self, mock_get):
        # Mock failure response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Call function
        ml_main.fetch_remote_config()

        # Check threshold remains unchanged
        self.assertEqual(ml_main.ANOMALY_THRESHOLD, 0.7)

    @patch('ml_service.main.requests.get')
    def test_fetch_remote_config_exception(self, mock_get):
        # Mock exception
        mock_get.side_effect = Exception("Connection error")

        # Call function (should not crash)
        ml_main.fetch_remote_config()

        # Check threshold remains unchanged
        self.assertEqual(ml_main.ANOMALY_THRESHOLD, 0.7)

    @patch('ml_service.main.fetch_remote_config')
    @patch('ml_service.main.fetch_latest_data')
    def test_job_calls_fetch_config(self, mock_fetch_data, mock_fetch_config):
        # Mock data fetch to return None to exit early
        mock_fetch_data.return_value = None

        # Call job
        ml_main.job()

        # Verify fetch_remote_config was called
        mock_fetch_config.assert_called_once()

import logging
if __name__ == '__main__':
    unittest.main()
