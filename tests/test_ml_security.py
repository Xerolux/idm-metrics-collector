import unittest
from unittest.mock import patch
from idm_logger.web import app


class TestMLSecurity(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.endpoint = "/api/internal/ml_alert"

    def test_fail_closed_when_key_missing(self):
        """Test that the endpoint returns 503 when INTERNAL_API_KEY is not configured."""
        # Patch config.get to return None for 'internal_api_key'
        with patch("idm_logger.web.config.get") as mock_get:

            def side_effect(key, default=None):
                if key == "internal_api_key":
                    return None
                return default

            mock_get.side_effect = side_effect

            response = self.client.post(self.endpoint, json={"score": 0.9})
            self.assertEqual(response.status_code, 503)
            self.assertIn("Configuration Error", response.get_json().get("error"))

    def test_fail_auth_when_key_set_but_header_missing(self):
        """Test that the endpoint returns 401 when key is set but header is missing."""
        with patch("idm_logger.web.config.get") as mock_get:

            def side_effect(key, default=None):
                if key == "internal_api_key":
                    return "secure-key"
                return default

            mock_get.side_effect = side_effect

            response = self.client.post(self.endpoint, json={"score": 0.9})
            self.assertEqual(response.status_code, 401)
            self.assertIn("Unauthorized", response.get_json().get("error"))

    def test_success_when_key_and_header_match(self):
        """Test that the endpoint returns success when key matches header."""
        with patch("idm_logger.web.config.get") as mock_get:

            def side_effect(key, default=None):
                if key == "internal_api_key":
                    return "secure-key"
                return default

            mock_get.side_effect = side_effect

            # Also mock notification_manager.send_all to avoid actual sending
            with patch("idm_logger.web.notification_manager.send_all"):
                response = self.client.post(
                    self.endpoint,
                    json={"score": 0.9},
                    headers={"X-Internal-Secret": "secure-key"},
                )
                self.assertIn(response.status_code, [200, 201])


if __name__ == "__main__":
    unittest.main()
