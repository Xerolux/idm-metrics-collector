# SPDX-License-Identifier: MIT
import unittest
import os
import uuid
from unittest.mock import patch
from idm_logger.config import Config
from idm_logger.telemetry import TelemetryManager


class TestConfigTelemetry(unittest.TestCase):
    def setUp(self):
        # Use a temporary file for config
        self.config_file = "test_config_telemetry.json"
        self.key_file = ".test_secret.key"

        # Patch db.get_setting/set_setting to use a dict instead of real DB
        self.settings_db = {}
        self.db_patcher = patch("idm_logger.config.db")
        self.mock_db = self.db_patcher.start()

        def get_setting(key):
            return self.settings_db.get(key)

        def set_setting(key, value):
            self.settings_db[key] = value

        self.mock_db.get_setting.side_effect = get_setting
        self.mock_db.set_setting.side_effect = set_setting

        # Initialize Config
        if os.path.exists(self.key_file):
            os.remove(self.key_file)

        self.config = Config()

    def tearDown(self):
        self.db_patcher.stop()
        if os.path.exists(self.key_file):
            os.remove(self.key_file)

    def test_default_values(self):
        """Test that new config fields have correct defaults."""
        self.assertEqual(self.config.get("heatpump_model"), "")
        self.assertTrue(self.config.get("share_data"))
        self.assertIsNotNone(self.config.get("installation_id"))
        # Verify UUID format
        try:
            uuid.UUID(self.config.get("installation_id"))
        except ValueError:
            self.fail("installation_id is not a valid UUID")

    def test_save_load(self):
        """Test saving and loading the new fields."""
        self.config.data["heatpump_model"] = "AERO SLM"
        self.config.data["share_data"] = False
        self.config.save()

        # Reload
        new_config = Config()
        self.assertEqual(new_config.get("heatpump_model"), "AERO SLM")
        self.assertFalse(new_config.get("share_data"))
        # UUID should persist if it was saved?
        # Actually Config logic generates a NEW one if not in DB.
        # But wait, self.config.save() saves it to DB.
        # So new_config._load_data() should pick it up from DB.
        original_uuid = self.config.get("installation_id")
        self.assertEqual(new_config.get("installation_id"), original_uuid)

    @patch("idm_logger.telemetry.requests.post")
    def test_telemetry_submission(self, mock_post):
        """Test that telemetry sends data when enabled."""
        tm = TelemetryManager(self.config)
        # Change endpoint to a specific test domain (not example.com which is blocked in loop)
        tm.endpoint = "https://my-test-server.com/api"

        self.config.data["heatpump_model"] = "TEST_MODEL"
        self.config.data["share_data"] = True

        # Add data
        data = {"temp": 10}
        tm.submit_data(data)

        # Force flush
        tm._flush_buffer()

        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        self.assertEqual(payload["heatpump_model"], "TEST_MODEL")
        self.assertEqual(payload["data"][0]["temp"], 10)

        # Verify Auth Header
        # By default no token in test setup
        self.assertNotIn("Authorization", kwargs.get("headers", {}))

    @patch("idm_logger.telemetry.requests.post")
    def test_telemetry_disabled(self, mock_post):
        """Test that telemetry does NOT send data when disabled."""
        tm = TelemetryManager(self.config)
        self.config.data["heatpump_model"] = "TEST_MODEL"
        self.config.data["share_data"] = False

        tm.submit_data({"temp": 10})
        tm._flush_buffer()

        mock_post.assert_not_called()

    @patch("idm_logger.telemetry.requests.post")
    def test_telemetry_no_model(self, mock_post):
        """Test that telemetry does NOT send data when model is missing."""
        tm = TelemetryManager(self.config)
        self.config.data["heatpump_model"] = ""
        self.config.data["share_data"] = True

        tm.submit_data({"temp": 10})
        tm._flush_buffer()

        mock_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
