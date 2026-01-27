# SPDX-License-Identifier: MIT
"""Tests for technician API server time functionality."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import helpers from conftest
from conftest import create_mock_db_module, create_mock_config


@pytest.fixture(autouse=True)
def clean_modules():
    """Clean up idm_logger modules before and after each test."""
    for mod in list(sys.modules.keys()):
        if mod.startswith("idm_logger"):
            del sys.modules[mod]
    yield
    for mod in list(sys.modules.keys()):
        if mod.startswith("idm_logger"):
            del sys.modules[mod]


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    mock_db_module = create_mock_db_module()
    mock_config = create_mock_config()

    with patch.dict(
        sys.modules,
        {
            "idm_logger.db": mock_db_module,
            "idm_logger.mqtt": MagicMock(),
            "idm_logger.modbus": MagicMock(),
        },
    ):
        with patch("idm_logger.config.config", mock_config):
            from idm_logger.web import app

            app.config["TESTING"] = True
            app.secret_key = b"test-secret"
            with app.test_client() as test_client:
                with test_client.session_transaction() as sess:
                    sess["logged_in"] = True
                yield test_client


def test_technician_code_returns_server_time(client):
    """Test that technician code endpoint returns server time."""
    # Mock calculate_codes to return dummy codes
    with patch("idm_logger.web.calculate_codes") as mock_calc:
        mock_calc.return_value = {"level_1": "1234", "level_2": "12345"}

        response = client.get("/api/tools/technician-code")

        assert response.status_code == 200
        data = response.get_json()
        assert "server_time" in data
        # Check format HH:MM:SS
        assert len(data["server_time"].split(":")) == 3
        assert data["level_1"] == "1234"
