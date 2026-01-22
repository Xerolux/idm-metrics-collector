import unittest
from unittest.mock import patch
import sys
import os

# We need to import ml_service.main but it executes code on import.
# We will mock the environment variables before import to prevent side effects?
# Or just patch relevant parts.

# Since ml_service/main.py is a script with global execution, importing it runs it.
# We should probably refactor it to avoid global execution, but for now we'll import it
# and assume it doesn't crash if env vars are missing (defaults used).
# But it calls get_all_readable_sensors() which imports idm_logger.
# That is fine.

sys.path.insert(0, os.getcwd())

# Mock requests to avoid network calls during import if any (wait_for_connection is called in main, not at module level)
# But SENSORS = get_all_readable_sensors() IS called at module level.
# That's fine, it just reads config.

with patch("requests.get"), patch("requests.post"):
    from ml_service import main as ml_main


class TestMlRatio(unittest.TestCase):
    def setUp(self):
        # Reset global state if needed
        pass

    @patch("ml_service.main.fetch_latest_data")
    @patch("ml_service.main.logger")
    def test_job_skips_if_insufficient_data(self, mock_logger, mock_fetch):
        # Setup: Ratio is 0.4 (default in code now)
        # SENSORS length is likely around 80-90.
        # Let's override SENSORS for testing to a small number
        original_sensors = ml_main.SENSORS
        ml_main.SENSORS = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]
        # 10 sensors. 40% is 4.

        # Case 1: 3 sensors (30%) -> Should skip
        mock_fetch.return_value = {"s1": 1.0, "s2": 1.0, "s3": 1.0}

        ml_main.job()

        # Verify warning logged
        mock_logger.warning.assert_any_call(
            "Insufficient data fetched (3/10 sensors, need 4). Skipping."
        )
        # Verify missing sensors logged
        # We need to check if the second warning was called with missing sensors
        # The exact string is "Missing sensors (first 10): ..."
        # Let's check if any call starts with "Missing sensors"
        found_missing_log = False
        for call in mock_logger.warning.call_args_list:
            if call[0][0].startswith("Missing sensors"):
                found_missing_log = True
                self.assertIn("s4", call[0][0])
                break
        self.assertTrue(found_missing_log, "Should log missing sensors")

        ml_main.SENSORS = original_sensors

    @patch("ml_service.main.fetch_latest_data")
    @patch("ml_service.main.write_metrics")
    @patch("ml_service.main.logger")
    def test_job_proceeds_if_sufficient_data(self, mock_logger, mock_write, mock_fetch):
        # Setup
        original_sensors = ml_main.SENSORS
        ml_main.SENSORS = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]

        # Case 2: 4 sensors (40%) -> Should proceed (since ratio is 0.4)
        mock_fetch.return_value = {"s1": 1.0, "s2": 1.0, "s3": 1.0, "s4": 1.0}

        ml_main.job()

        # Verify write_metrics called
        mock_write.assert_called()

        ml_main.SENSORS = original_sensors


if __name__ == "__main__":
    unittest.main()
