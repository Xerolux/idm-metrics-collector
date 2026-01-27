# SPDX-License-Identifier: MIT
"""
Pytest configuration and fixtures for idm-metrics-collector tests.

This conftest.py sets up proper mocking and test fixtures to ensure
tests can run without requiring actual database connections or
external services.
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch

# Create a unique test directory for this test session
_TEST_DATA_DIR = tempfile.mkdtemp(prefix="idm_test_")

# Set environment variables before any imports
os.environ["TESTING"] = "1"
os.environ["DATA_DIR"] = _TEST_DATA_DIR


def _clean_idm_modules():
    """Remove all idm_logger modules from sys.modules."""
    modules_to_remove = [
        key for key in list(sys.modules.keys()) if key.startswith("idm_logger")
    ]
    for mod in modules_to_remove:
        del sys.modules[mod]


def create_mock_db_module():
    """Create a properly configured mock db module.

    This ensures that db.get_setting() returns None instead of a MagicMock,
    which would cause json.loads() to fail.
    """
    mock_db = MagicMock()
    mock_db.get_setting.return_value = None
    mock_db.set_setting = MagicMock()
    mock_db.get_jobs.return_value = []
    mock_db.get_alerts.return_value = []
    mock_db.get_heatpumps.return_value = []
    mock_db.get_dashboards.return_value = []
    mock_db.add_job = MagicMock()
    mock_db.add_alert = MagicMock()
    mock_db.update_job = MagicMock()
    mock_db.update_alert = MagicMock()
    mock_db.delete_job = MagicMock()
    mock_db.delete_alert = MagicMock()
    mock_db.update_jobs_last_run = MagicMock()
    mock_db.update_alerts_last_triggered = MagicMock()

    mock_module = MagicMock()
    mock_module.db = mock_db
    mock_module.Database = MagicMock(return_value=mock_db)
    return mock_module


def create_mock_config():
    """Create a properly configured mock config object."""
    config = MagicMock()
    config.get_flask_secret_key.return_value = b"test-secret-key-for-testing-123"
    config.get.return_value = None
    config.data = {
        "idm": {"host": "192.168.1.1", "port": 502, "circuits": ["A"], "zones": []},
        "metrics": {"url": "http://localhost:8428/write"},
        "web": {
            "enabled": True,
            "host": "0.0.0.0",
            "port": 5000,
            "write_enabled": False,
            "websocket_enabled": False,
            "secure_cookies": False,
            "admin_password_hash": "pbkdf2:sha256:test",
        },
        "network_security": {"enabled": False, "whitelist": [], "blacklist": []},
        "logging": {"interval": 30, "realtime_mode": False, "level": "INFO"},
        "mqtt": {"enabled": False, "broker": "", "port": 1883},
        "signal": {
            "enabled": False,
            "cli_path": "signal-cli",
            "sender": "",
            "recipients": [],
        },
        "telegram": {"enabled": False, "bot_token": "", "chat_ids": []},
        "discord": {"enabled": False, "webhook_url": ""},
        "email": {"enabled": False},
        "webdav": {"enabled": False},
        "ai": {"enabled": False, "sensitivity": 3.0},
        "updates": {"enabled": False},
        "backup": {"enabled": False},
        "internal_api_key": "test-internal-key",
        "setup_completed": True,
        "heatpump_model": "TEST_MODEL",
        "share_data": False,
        "installation_id": "test-installation-id",
        "telemetry_auth_token": "test-telemetry-token",
        "annotations": [],
        "variables": [],
        "sharing": {"tokens": []},
    }
    config.save = MagicMock()
    config.is_setup.return_value = True
    config.check_admin_password.return_value = True
    return config


@pytest.fixture(autouse=True)
def clean_modules_before_test():
    """Clean up idm_logger modules before each test to prevent contamination."""
    _clean_idm_modules()
    yield
    _clean_idm_modules()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables for the entire session."""
    os.environ["DATA_DIR"] = _TEST_DATA_DIR
    os.environ["TESTING"] = "1"
    yield
    # Cleanup (tempfile handles this automatically)


@pytest.fixture
def mock_config():
    """Provide a mocked config object."""
    return create_mock_config()


@pytest.fixture
def mock_db():
    """Provide a mocked database object."""
    return create_mock_db_module().db


@pytest.fixture
def mock_db_module():
    """Provide a mocked db module for patching sys.modules."""
    return create_mock_db_module()


@pytest.fixture
def flask_app(mock_config):
    """Create a Flask test application with mocked dependencies."""
    _clean_idm_modules()

    mock_db_mod = create_mock_db_module()

    # Patch modules before import
    with patch.dict(
        sys.modules,
        {
            "idm_logger.db": mock_db_mod,
            "idm_logger.mqtt": MagicMock(),
            "idm_logger.modbus": MagicMock(),
        },
    ):
        with patch("idm_logger.config.config", mock_config):
            from idm_logger.web import app

            app.config["TESTING"] = True
            app.secret_key = b"test-secret"
            yield app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask application."""
    return flask_app.test_client()


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client."""
    with client.session_transaction() as sess:
        sess["logged_in"] = True
    return client
