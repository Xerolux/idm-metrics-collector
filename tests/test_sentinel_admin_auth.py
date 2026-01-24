
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock modules to avoid side effects
sys.modules['idm_logger.db'] = MagicMock()
sys.modules['idm_logger.db'].db = MagicMock()
sys.modules['idm_logger.db'].db.get_setting.return_value = None

# Mock config
from idm_logger.config import Config

class TestAdminAuth(unittest.TestCase):
    def setUp(self):
        # We need to re-instantiate Config for each test to clear state
        # But Config() calls _load_data which uses env vars.
        # So we should patch os.environ in each test.
        self.patcher = patch.dict(os.environ, {}, clear=True)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_no_fallback_when_hash_missing(self):
        """Verify that the system DOES NOT fall back to 'admin' when hash is missing."""
        # Setup: config without hash
        # Mock _load_data or just let it run with empty env
        config = Config()

        # Ensure hash is missing
        if "admin_password_hash" in config.data["web"]:
            del config.data["web"]["admin_password_hash"]

        # This should now return False
        self.assertFalse(config.check_admin_password("admin"))

    def test_setup_wizard_forced_when_password_missing(self):
        """Verify setup_completed is False if password is missing, even with METRICS_URL."""
        with patch.dict(os.environ, {"METRICS_URL": "http://test:8428"}):
            config = Config()
            # Should have metrics url
            self.assertEqual(config.data["metrics"]["url"], "http://test:8428")
            # But setup_completed should be False because no password
            self.assertFalse(config.data["setup_completed"])
            # And check_admin_password should fail
            self.assertFalse(config.check_admin_password("admin"))

    def test_admin_password_env_var(self):
        """Verify ADMIN_PASSWORD env var sets hash and completes setup."""
        with patch.dict(os.environ, {
            "METRICS_URL": "http://test:8428",
            "ADMIN_PASSWORD": "secure_password_123"
        }):
            config = Config()

            # Setup should be completed
            self.assertTrue(config.data["setup_completed"])

            # Password should be set
            self.assertIn("admin_password_hash", config.data["web"])

            # Login with env password should work
            self.assertTrue(config.check_admin_password("secure_password_123"))

            # Login with "admin" should fail (unless password IS admin, but we set secure one)
            self.assertFalse(config.check_admin_password("admin"))

if __name__ == '__main__':
    unittest.main()
