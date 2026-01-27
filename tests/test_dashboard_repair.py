# SPDX-License-Identifier: MIT
"""Tests for dashboard repair functionality."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import helpers from conftest
from conftest import create_mock_db_module


class TestDashboardRepair(unittest.TestCase):
    def setUp(self):
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

        self.mock_config = MagicMock()
        # Mock the config.data dictionary
        self.mock_config.data = {}
        self.mock_config.save = MagicMock()

        # Create mock db module
        self.mock_db_module = create_mock_db_module()

        # Patch db module before importing dashboard_config
        self.modules_patcher = patch.dict(
            sys.modules,
            {
                "idm_logger.db": self.mock_db_module,
            },
        )
        self.modules_patcher.start()

    def tearDown(self):
        self.modules_patcher.stop()
        # Clean up modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("idm_logger"):
                del sys.modules[mod]

    def test_repair_broken_dashboard(self):
        # Setup broken dashboard data
        broken_dashboard = {
            "id": "default",
            "name": "Broken Dashboard",
            "charts": [
                {"title": "Underfloor Heating", "id": "1", "queries": [], "hours": 24},
                {"title": "Some Other Chart", "id": "2", "queries": [], "hours": 24},
            ],
        }

        # Configure the mock config to return this data
        mock_config = MagicMock()
        mock_config.data = {"dashboards": [broken_dashboard]}
        mock_config.save = MagicMock()

        with patch("idm_logger.dashboard_config.config", mock_config):
            from idm_logger.dashboard_config import DashboardManager

            # Initialize manager - this triggers __init__ which calls _repair_broken_dashboards
            _ = DashboardManager()

            # Verify that save was called (implying a change was made)
            mock_config.save.assert_called()

            # Verify that the dashboard was replaced
            dashboards = mock_config.data["dashboards"]
            self.assertEqual(len(dashboards), 1)
            self.assertEqual(dashboards[0]["name"], "Home Dashboard")  # Default name

            # Check that broken titles are gone
            titles = [c["title"] for c in dashboards[0]["charts"]]
            self.assertNotIn("Underfloor Heating", titles)
            self.assertIn("Wärmepumpe Temperaturen", titles)

    def test_no_repair_needed(self):
        with patch("idm_logger.dashboard_config.config") as mock_config:
            from idm_logger.dashboard_config import (
                get_default_dashboards,
                DashboardManager,
            )

            # Setup good dashboard data
            good_dashboard = get_default_dashboards()[0]

            mock_config.data = {"dashboards": [good_dashboard]}
            mock_config.save = MagicMock()

            _ = DashboardManager()

            # Verify the data hasn't changed
            dashboards = mock_config.data["dashboards"]
            self.assertEqual(dashboards[0]["id"], good_dashboard["id"])
            self.assertEqual(
                dashboards[0]["charts"][0]["title"],
                good_dashboard["charts"][0]["title"],
            )


if __name__ == "__main__":
    unittest.main()
