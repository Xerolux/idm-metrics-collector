import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.getcwd())

# Mock requests to avoid network calls during import
with patch("requests.get"), patch("requests.post"):
    from ml_service import main as ml_main


class TestMlRatio(unittest.TestCase):
    def setUp(self):
        # Reset logger mock for each test
        ml_main.logger = MagicMock()
        # Ensure model is mocked and returns a valid float score
        ml_main.model = MagicMock()
        ml_main.model.score_one.return_value = 0.5

    @patch("ml_service.main.fetch_latest_data")
    @patch("ml_service.main.write_metrics")
    def test_job_proceeds_even_if_insufficient_data(self, mock_write, mock_fetch):
        # Setup: Ratio is 0.4.
        original_sensors = ml_main.SENSORS
        ml_main.SENSORS = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]

        # Case 1: 3 sensors (30%) -> Should NO LONGER skip, but proceed with warning
        # New architecture: fetch returns {hp_id: {sensor: value}}
        mock_fetch.return_value = {"default": {"s1": 1.0, "s2": 1.0, "s3": 1.0}}

        original_ratio = ml_main.MIN_DATA_RATIO
        ml_main.MIN_DATA_RATIO = 0.4

        ml_main.job()

        # Verify warning logged
        ml_main.logger.warning.assert_called()
        found_warning = False
        for call in ml_main.logger.warning.call_args_list:
            msg = call[0][0]
            if "Low data availability" in msg and "Proceeding anyway" in msg:
                found_warning = True
                break

        self.assertTrue(found_warning, "Should log 'Low data availability' warning")

        # Verify write_metrics called
        mock_write.assert_called()

        # Cleanup
        ml_main.SENSORS = original_sensors
        ml_main.MIN_DATA_RATIO = original_ratio

    @patch("ml_service.main.fetch_latest_data")
    @patch("ml_service.main.write_metrics")
    def test_job_proceeds_if_sufficient_data(self, mock_write, mock_fetch):
        # Setup
        original_sensors = ml_main.SENSORS
        ml_main.SENSORS = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]
        original_ratio = ml_main.MIN_DATA_RATIO
        ml_main.MIN_DATA_RATIO = 0.4

        # Case 2: 4 sensors (40%) -> Should proceed (since ratio is 0.4)
        # New architecture: fetch returns {hp_id: {sensor: value}}
        mock_fetch.return_value = {"default": {"s1": 1.0, "s2": 1.0, "s3": 1.0, "s4": 1.0}}

        ml_main.job()

        # Verify write_metrics called
        mock_write.assert_called()

        # Cleanup
        ml_main.SENSORS = original_sensors
        ml_main.MIN_DATA_RATIO = original_ratio


if __name__ == "__main__":
    unittest.main()
