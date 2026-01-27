# SPDX-License-Identifier: MIT
"""Tests for dashboard sharing functionality."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import helper from conftest
from conftest import create_mock_db_module, create_mock_config


class TestSharing(unittest.TestCase):
    """Test dashboard sharing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Clean up any existing idm_logger modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        # Create properly configured mocks
        self.mock_db_module = create_mock_db_module()
        self.mock_config = create_mock_config()
        self.mock_config.data["sharing"] = {"tokens": []}

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
        from idm_logger.sharing import SharingManager
        from idm_logger.dashboard_config import dashboard_manager

        self.app = app
        self.app.config["TESTING"] = True
        self.app.secret_key = b"test-secret"
        self.client = self.app.test_client()

        # Initialize sharing manager with mock config
        self.sharing_manager = SharingManager(self.mock_config)

        # Import web module and set sharing_manager
        import idm_logger.web as web_module

        web_module.sharing_manager = self.sharing_manager
        self.dashboard_manager = dashboard_manager

    def tearDown(self):
        """Clean up after tests."""
        self.config_patcher.stop()
        self.modules_patcher.stop()

        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

    def test_shared_dashboard_endpoint(self):
        """Test accessing a shared dashboard."""
        with patch.object(self.dashboard_manager, "get_dashboard") as mock_get_dash:
            mock_get_dash.return_value = {
                "id": "dash1",
                "name": "Test Dash",
                "charts": [],
            }

            # Create a share token (public)
            token = self.sharing_manager.create_share_token(
                dashboard_id="dash1", created_by="test", is_public=True
            )

            # Test access
            resp = self.client.get(f"/api/sharing/dashboard/{token.token_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json["id"], "dash1")

            # Create protected token
            token_protected = self.sharing_manager.create_share_token(
                dashboard_id="dash1",
                created_by="test",
                password="secret",
                is_public=False,
            )

            # Test access without password
            resp = self.client.get(f"/api/sharing/dashboard/{token_protected.token_id}")
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(resp.json["require_password"])

            # Test access with wrong password
            resp = self.client.get(
                f"/api/sharing/dashboard/{token_protected.token_id}",
                headers={"X-Share-Password": "wrong"},
            )
            self.assertEqual(resp.status_code, 403)

            # Test access with correct password
            resp = self.client.get(
                f"/api/sharing/dashboard/{token_protected.token_id}",
                headers={"X-Share-Password": "secret"},
            )
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json["id"], "dash1")

    def test_query_metrics_with_share_token(self):
        """Test querying metrics with a share token."""
        # Mock sharing manager to validate token
        with patch.object(self.sharing_manager, "validate_token") as mock_validate:
            mock_validate.return_value = True

            # Mock requests.get to VictoriaMetrics
            with patch("requests.get") as mock_requests_get:
                mock_requests_get.return_value.status_code = 200
                mock_requests_get.return_value.json.return_value = {
                    "status": "success",
                    "data": {},
                }

                # Access protected endpoint with token
                resp = self.client.get(
                    "/api/metrics/query_range?query=test",
                    headers={"X-Share-Token": "valid_token"},
                )

                self.assertEqual(resp.status_code, 200)
                mock_validate.assert_called_with("valid_token", None)

    def test_query_metrics_unauthorized(self):
        """Test unauthorized access to metrics endpoint."""
        # Access without login or token
        resp = self.client.get("/api/metrics/query_range?query=test")
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
