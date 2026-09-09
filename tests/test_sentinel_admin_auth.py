# Xerolux 2026
import os
from unittest.mock import patch, MagicMock
import sys


class TestSentinelAdminAuth:
    def setup_method(self):
        # Mock idm_logger.db before importing config
        self.mock_db_module = MagicMock()
        self.mock_db_instance = MagicMock()
        # Configure get_setting to return None by default so _load_data returns defaults
        self.mock_db_instance.get_setting.return_value = None
        self.mock_db_module.db = self.mock_db_instance
        self.patcher = patch.dict(sys.modules, {"idm_logger.db": self.mock_db_module})
        self.patcher.start()

        import importlib
        import idm_logger.config

        importlib.reload(idm_logger.config)
        self.Config = idm_logger.config.Config

        # Reset environment variables before each test
        if "ADMIN_PASSWORD" in os.environ:
            del os.environ["ADMIN_PASSWORD"]

    def teardown_method(self):
        self.patcher.stop()
        # Clean up
        if "ADMIN_PASSWORD" in os.environ:
            del os.environ["ADMIN_PASSWORD"]

    def test_default_admin_password(self):
        """Verify that with no hash set, default 'admin' password works."""
        # Setup clean config
        with patch.dict(os.environ, clear=True):
            # Instantiate Config
            config = self.Config()

            # Ensure no hash is present (in case defaults change)
            if "admin_password_hash" in config.data["web"]:
                del config.data["web"]["admin_password_hash"]

            # Default password 'admin' should work
            assert config.check_admin_password("admin") is True
            # Other passwords should fail
            assert config.check_admin_password("secret") is False
            assert config.check_admin_password("") is False

    def test_admin_password_env_var(self):
        """Verify that ADMIN_PASSWORD environment variable sets the hash correctly."""
        test_password = "secure_password_123"
        with patch.dict(os.environ, {"ADMIN_PASSWORD": test_password}):
            config = self.Config()

            # Check if hash was generated
            assert "admin_password_hash" in config.data["web"]

            # Check if password works
            assert config.check_admin_password(test_password) is True
            assert config.check_admin_password("wrong_password") is False
            assert config.check_admin_password("admin") is False

    def test_existing_hash_respected(self):
        """Verify that an existing hash is respected."""
        from werkzeug.security import generate_password_hash

        existing_pass = "existing_secret"
        hashed = generate_password_hash(existing_pass)

        # We patch _load_data to simulate reading from DB/file
        with patch.object(self.Config, "_load_data") as mock_load:
            # Create a mock data structure mimicking what _load_data returns
            # We must provide all keys that __init__ might access or merge
            mock_data = {
                "web": {
                    "admin_password_hash": hashed,
                    "enabled": True,
                    "host": "0.0.0.0",
                    "port": 5000,
                    "write_enabled": False,
                },
                "idm": {},
                "metrics": {},
                "network_security": {},
                "logging": {},
                "mqtt": {},
                "signal": {},
                "telegram": {},
                "discord": {},
                "email": {},
                "webdav": {},
                "ai": {},
                "updates": {},
                "backup": {},
                "internal_api_key": None,
            }
            mock_load.return_value = mock_data

            with patch.dict(os.environ, clear=True):
                config = self.Config()

                assert config.check_admin_password(existing_pass) is True
                assert config.check_admin_password("admin") is False
