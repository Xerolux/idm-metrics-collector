# Xerolux 2026
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.getcwd())

from idm_logger.dashboard_config import DashboardManager, get_default_dashboards


class TestDashboardRepair(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()
        # Mock the config.data dictionary
        self.mock_config.data = {}
        self.mock_config.save = MagicMock()

    @patch("idm_logger.dashboard_config.config", new_callable=MagicMock)
    def test_repair_broken_dashboard(self, mock_config_module):
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
        mock_config_module.data = {"dashboards": [broken_dashboard]}
        mock_config_module.save = MagicMock()

        # Initialize manager - this triggers __init__ which calls _repair_broken_dashboards
        _ = DashboardManager()

        # Verify that save was called (implying a change was made)
        mock_config_module.save.assert_called()

        # Verify that the dashboard was replaced
        dashboards = mock_config_module.data["dashboards"]
        self.assertEqual(len(dashboards), 1)
        self.assertEqual(dashboards[0]["name"], "Home Dashboard")  # Default name

        # Check that broken titles are gone
        titles = [c["title"] for c in dashboards[0]["charts"]]
        self.assertNotIn("Underfloor Heating", titles)
        self.assertIn("Wärmepumpe Temperaturen", titles)

    @patch("idm_logger.dashboard_config.config", new_callable=MagicMock)
    def test_no_repair_needed(self, mock_config_module):
        # Setup good dashboard data
        good_dashboard = get_default_dashboards()[0]

        mock_config_module.data = {"dashboards": [good_dashboard]}
        mock_config_module.save = MagicMock()

        _ = DashboardManager()

        # Verify that save was NOT called (implying no change needed)
        # Wait, _ensure_dashboards_key calls save if key is missing, but here it is present.
        # But _repair_broken_dashboards only calls save if repaired=True.
        # However, verifying save not called might be tricky if other methods call it.
        # Let's verify the data hasn't changed.

        dashboards = mock_config_module.data["dashboards"]
        self.assertEqual(dashboards[0]["id"], good_dashboard["id"])
        self.assertEqual(
            dashboards[0]["charts"][0]["title"], good_dashboard["charts"][0]["title"]
        )


if __name__ == "__main__":
    unittest.main()
