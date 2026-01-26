import os
from unittest.mock import patch, MagicMock
import sys

# Mock idm_logger.db before importing config
mock_db_module = MagicMock()
mock_db_instance = MagicMock()
# Configure get_setting to return None by default so _load_data returns defaults
mock_db_instance.get_setting.return_value = None
mock_db_module.db = mock_db_instance
sys.modules["idm_logger.db"] = mock_db_module

# Now we can safely import Config
from idm_logger.config import Config


class TestLockoutScenario:
    def setup_method(self):
        # Clear relevant env vars
        if "ADMIN_PASSWORD" in os.environ:
            del os.environ["ADMIN_PASSWORD"]
        if "METRICS_URL" in os.environ:
            del os.environ["METRICS_URL"]

    def teardown_method(self):
        # Cleanup
        if "ADMIN_PASSWORD" in os.environ:
            del os.environ["ADMIN_PASSWORD"]
        if "METRICS_URL" in os.environ:
            del os.environ["METRICS_URL"]

    def test_lockout_prevention(self):
        """
        Verify the Lockout Prevention fix:
        If METRICS_URL is set but ADMIN_PASSWORD is NOT set,
        the system should NOT mark setup_completed=True.

        This ensures the user is directed to the Setup Wizard to set a password.
        """
        env_vars = {
            "METRICS_URL": "http://victoriametrics:8428/write",
            # "ADMIN_PASSWORD" is deliberately missing
        }

        with patch.dict(os.environ, env_vars):
            config = Config()

            # Verify fix:
            is_setup = config.is_setup()

            # Assert NEW CORRECT behavior
            assert is_setup is False, (
                "System should remain in setup mode if password is missing"
            )

            # Login still fails (Fail Closed)
            login_works = config.check_admin_password("admin")
            assert login_works is False

    def test_setup_complete_with_password(self):
        """
        Verify that if both METRICS_URL and ADMIN_PASSWORD are set,
        setup is marked as complete.
        """
        env_vars = {
            "METRICS_URL": "http://victoriametrics:8428/write",
            "ADMIN_PASSWORD": "secure_password",
        }

        with patch.dict(os.environ, env_vars):
            config = Config()

            assert config.is_setup() is True
            assert config.check_admin_password("secure_password") is True
