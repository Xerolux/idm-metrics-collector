import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure we can import idm_logger
sys.path.append(os.getcwd())

from idm_logger.web import app


class TestApiLogsShare(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("requests.post")
    @patch("idm_logger.web.memory_handler")
    def test_share_logs_success(self, mock_memory, mock_post):
        # Setup Logs
        mock_memory.get_logs.return_value = [
            {
                "timestamp": "2023-01-01 10:00:00",
                "level": "INFO",
                "message": "Test log 1",
            }
        ]

        # Setup Upload Mock Response
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": 0,
            "id": "test_id",
            "url": "https://paste.blueml.eu?test_id",
        }
        mock_post.return_value = mock_resp

        # Simulate Login
        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        # Request
        response = self.client.post("/api/logs/share")

        # Verify
        if response.status_code != 200:
            print(f"Response error: {response.get_json()}")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])

        # Check link format
        link = data["link"]
        self.assertTrue(link.startswith("https://paste.blueml.eu?test_id#"))

        # Verify Upload content was encrypted (we can't check plaintext easily here without decrypting)
        # But we can check requests.post was called with correct URL
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://paste.blueml.eu")
        payload = kwargs["json"]
        self.assertEqual(payload["v"], 2)

    @patch("requests.post")
    def test_share_logs_failure(self, mock_post):
        mock_post.side_effect = Exception("Connection failed")

        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

        response = self.client.post("/api/logs/share")

        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Connection failed", data["error"])
