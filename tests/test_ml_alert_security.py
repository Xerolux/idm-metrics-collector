# SPDX-License-Identifier: MIT
"""Tests for ML alert security functionality."""

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

            # Store config reference
            app.test_mock_config = mock_config

            with app.test_client() as test_client:
                yield test_client, mock_config


def test_ml_alert_no_auth_by_default(client):
    """
    Test that the endpoint returns 503 if no key is configured.
    """
    test_client, mock_config = client

    # Ensure no key is set
    mock_config.data["internal_api_key"] = None

    with patch("idm_logger.web.notification_manager"):
        response = test_client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
        )
        assert response.status_code == 503


def test_ml_alert_auth_enforced(client):
    """
    Test that auth is enforced when key is configured.
    """
    test_client, mock_config = client

    # Set key
    mock_config.data["internal_api_key"] = "super-secret-key"

    with patch("idm_logger.web.notification_manager") as mock_notify:
        # Case 1: No header
        response = test_client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
        )
        assert response.status_code == 401

        # Case 2: Wrong header
        response = test_client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
            headers={"X-Internal-Secret": "wrong-key"},
        )
        assert response.status_code == 401

        # Case 3: Correct header
        response = test_client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
            headers={"X-Internal-Secret": "super-secret-key"},
        )
        assert response.status_code == 200
        mock_notify.send_all.assert_called_once()
