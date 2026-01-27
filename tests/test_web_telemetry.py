import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import app from web module
# We mock Config methods to prevent DB access during import
with (
    patch(
        "idm_logger.config.Config._load_or_create_key",
        return_value=b"test-key-12345678901234567890123456789012=",
    ),
    patch("idm_logger.config.Config._load_data", return_value={}),
    patch("idm_logger.config.Config._apply_env_overrides"),
):
    from idm_logger.web import app, config


class TestWebTelemetryProxy(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Setup config data for tests
        config.data = {
            "telemetry_auth_token": "test-token-123",
            "metrics": {"url": "http://vm:8428/write"},
            "web": {
                "websocket_enabled": False,
                "secure_cookies": False,
                "admin_password_hash": "pbkdf2:sha256:...",  # Fake hash
            },
        }
        # Flask needs secret key
        app.secret_key = b"test-secret"

    @patch("idm_logger.web.requests.get")
    def test_get_community_averages_success(self, mock_get):
        # Setup mock response from telemetry server
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "AERO_SLM",
            "metrics": {"cop_current": {"avg": 4.5, "min": 3.0, "max": 5.5}},
        }
        mock_get.return_value = mock_response

        # Mock session login (using @auth_or_token_required)
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        # Make request
        response = self.client.get(
            "/api/telemetry/community/averages?model=AERO_SLM&metrics=cop_current"
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["model"], "AERO_SLM")

        # Check if requests.get was called correctly
        args, kwargs = mock_get.call_args
        self.assertIn("/api/v1/community/averages", args[0])
        self.assertEqual(kwargs["params"]["model"], "AERO_SLM")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-token-123")

    @patch("idm_logger.web.requests.get")
    def test_get_community_averages_no_token(self, mock_get):
        # Simulate missing token in config
        config.data["telemetry_auth_token"] = None

        # Mock session login
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.client.get("/api/telemetry/community/averages?model=AERO_SLM")

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("not configured", data["error"])

    def test_get_community_averages_no_model(self):
        # Mock session login
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.client.get("/api/telemetry/community/averages")

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Model parameter is required", data["error"])

    @patch("idm_logger.web.requests.get")
    def test_get_community_averages_upstream_error(self, mock_get):
        # Simulate upstream error
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.text = "Bad Gateway"
        mock_get.return_value = mock_response

        # Mock session login
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.client.get("/api/telemetry/community/averages?model=AERO_SLM")

        self.assertEqual(response.status_code, 502)
        data = json.loads(response.data)
        self.assertIn("Telemetry server error", data["error"])


if __name__ == "__main__":
    unittest.main()
