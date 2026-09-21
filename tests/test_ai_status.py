# Xerolux 2026
# SPDX-License-Identifier: MIT
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Ensure we can import idm_logger
sys.path.append(os.getcwd())

from idm_logger import web


class TestAiStatus(unittest.TestCase):
    def setUp(self):
        web.app.config["TESTING"] = True
        self.app = web.app.test_client()

    @patch("idm_logger.web.requests.get")
    def test_get_ai_status_standard(self, mock_get):
        # Scenario 1: Standard metrics response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "result": [
                    {
                        "metric": {"__name__": "idm_anomaly_score"},
                        "value": [1600000000, "0.123"],
                    },
                    {
                        "metric": {"__name__": "idm_anomaly_flag"},
                        "value": [1600000000, "0"],
                    },
                ]
            },
        }
        mock_get.return_value = mock_response

        # Trigger update
        web._update_ai_status_once()

        # Mock login
        with self.app.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.app.get("/api/ai/status")
        data = json.loads(response.data)

        self.assertTrue(data["online"])
        self.assertEqual(data["score"], 0.123)
        self.assertEqual(data["last_update"], 1600000000)

    @patch("idm_logger.web.requests.get")
    def test_get_ai_status_influx_style(self, mock_get):
        # Scenario 2: InfluxDB style metrics (suffix _value)
        # This currently FAILS with existing code, which expects exact match
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "result": [
                    {
                        "metric": {"__name__": "idm_anomaly_score_value"},
                        "value": [1600000000, "0.456"],
                    },
                    {
                        "metric": {"__name__": "idm_anomaly_flag_value"},
                        "value": [1600000000, "1"],
                    },
                ]
            },
        }
        mock_get.return_value = mock_response

        # Trigger update
        web._update_ai_status_once()

        # Trigger update
        web._update_ai_status_once()

        with self.app.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.app.get("/api/ai/status")
        data = json.loads(response.data)

        # We assert what we WANT to happen (should detect it), but it might fail now
        # If I want to prove it fails, I assert False.
        # But I want to use this test to verify my fix later.

        # Current behavior: returns offline (False)
        # Desired behavior: returns online (True)
        # So I expect this to fail initially if I assert True
        self.assertTrue(data["online"], "Should recognize _value suffix")
        self.assertEqual(data["score"], 0.456)
        self.assertTrue(data["is_anomaly"])

    @patch("idm_logger.web.requests.get")
    def test_get_ai_status_empty(self, mock_get):
        # Scenario 3: Empty result (no data in instant query)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": {"result": []}}
        mock_get.return_value = mock_response

        with self.app.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.app.get("/api/ai/status")
        data = json.loads(response.data)

        self.assertFalse(data["online"])


if __name__ == "__main__":
    unittest.main()
