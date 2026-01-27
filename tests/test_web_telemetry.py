# SPDX-License-Identifier: MIT
"""Tests for web telemetry proxy functionality."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import helper from conftest
from conftest import create_mock_db_module, create_mock_config


class TestWebTelemetryProxy(unittest.TestCase):
    """Test telemetry proxy endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Clean up any existing idm_logger modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        # Create properly configured mocks
        self.mock_db_module = create_mock_db_module()
        self.mock_config = create_mock_config()
        self.mock_config.data["telemetry_auth_token"] = "test-token-123"

        # Patch modules before importing web
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": self.mock_db_module,
                "idm_logger.mqtt": MagicMock(),
                "idm_logger.modbus": MagicMock(),
            },
        )
        self.modules_patcher.start()

        # Patch config
        self.config_patcher = patch("idm_logger.config.config", self.mock_config)
        self.config_patcher.start()

        # Now import the web module
        from idm_logger.web import app

        self.app = app
        self.app.config["TESTING"] = True
        self.app.secret_key = b"test-secret"
        self.client = self.app.test_client()

        # Store config reference for tests to modify
        import idm_logger.web as web_module

        self.web_config = web_module.config

    def tearDown(self):
        """Clean up after tests."""
        self.config_patcher.stop()
        self.modules_patcher.stop()

        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

    @patch("idm_logger.web.requests.get")
    def test_get_community_averages_success(self, mock_get):
        """Test successful community averages retrieval."""
        # Setup mock response from telemetry server
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "AERO_SLM",
            "metrics": {"cop_current": {"avg": 4.5, "min": 3.0, "max": 5.5}},
        }
        mock_get.return_value = mock_response

        # Mock session login
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
        """Test community averages with no telemetry token configured."""
        # Simulate missing token in config
        self.mock_config.data["telemetry_auth_token"] = None

        # Mock session login
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.client.get("/api/telemetry/community/averages?model=AERO_SLM")

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("not configured", data["error"])

    def test_get_community_averages_no_model(self):
        """Test community averages with missing model parameter."""
        # Mock session login
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.client.get("/api/telemetry/community/averages")

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Model parameter is required", data["error"])

    @patch("idm_logger.web.requests.get")
    def test_get_community_averages_upstream_error(self, mock_get):
        """Test community averages with upstream server error."""
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
