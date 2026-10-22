# Xerolux 2026
import pytest
from unittest.mock import patch
from idm_logger.web import app, config


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_ml_alert_no_auth_by_default(client):
    """
    Test that the endpoint returns 503 if no key is configured.
    """
    # Ensure no key is set
    if "internal_api_key" in config.data:
        del config.data["internal_api_key"]

    with patch("idm_logger.web.notification_manager"):
        response = client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
        )
        assert response.status_code == 503


def test_ml_alert_auth_enforced(client):
    """
    Test that auth is enforced when key is configured.
    """
    # Set key
    config.data["internal_api_key"] = "super-secret-key"

    with patch("idm_logger.web.notification_manager") as mock_notify:
        # Case 1: No header
        response = client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
        )
        assert response.status_code == 401

        # Case 2: Wrong header
        response = client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
            headers={"X-Internal-Secret": "wrong-key"},
        )
        assert response.status_code == 401

        # Case 3: Correct header
        response = client.post(
            "/api/internal/ml_alert",
            json={"score": 0.9, "threshold": 0.7, "message": "Test"},
            headers={"X-Internal-Secret": "super-secret-key"},
        )
        assert response.status_code == 200
        mock_notify.send_all.assert_called_once()

    # Cleanup
    if "internal_api_key" in config.data:
        del config.data["internal_api_key"]
