# Xerolux 2026
import unittest
from unittest.mock import MagicMock, patch
import json
import base64
import hmac
import hashlib

from idm_logger.telemetry import TelemetryManager, DEFAULT_ENCRYPTION_KEY
from idm_logger.config import config


class TestTelemetry(unittest.TestCase):
    def setUp(self):
        # Patch config methods to isolate tests and prevent disk I/O
        self.patcher_get = patch.object(config, "get")
        self.mock_get = self.patcher_get.start()
        self.addCleanup(self.patcher_get.stop)

        self.patcher_save = patch.object(config, "save")
        self.mock_save = self.patcher_save.start()
        self.addCleanup(self.patcher_save.stop)

        self.patcher_set = patch.object(config, "set")
        self.mock_set = self.patcher_set.start()
        self.addCleanup(self.patcher_set.stop)

        # Default behavior for get to allow TelemetryManager initialization
        def default_get(key, default=None):
            if key == "telemetry":
                return {
                    "manual_downloads_today": 0,
                    "last_manual_download": 0,
                    "is_admin": False,
                    "server_stats": None,
                }
            return default

        self.mock_get.side_effect = default_get

        self.tm = TelemetryManager()

        # Reset internal state
        self.tm.manual_downloads_today = 0
        self.tm.last_manual_download = 0

    @patch("idm_logger.telemetry.requests")
    def test_submit_data_success(self, mock_requests):
        # Configure the mock config for this test
        self.mock_get.side_effect = lambda k, d=None: {
            "telemetry.enabled": True,
            "telemetry.server_url": "http://test-server",
            "telemetry.auth_token": "token",
            "metrics.url": "http://vm:8428/write",
            "installation_id": "uuid",
            "hp_model": "TestModel",
        }.get(k, d)

        # Reload state to pick up the config
        self.tm._load_state()

        # Mock VM Export response
        mock_response_vm = MagicMock()
        mock_response_vm.status_code = 200
        mock_response_vm.iter_lines.return_value = [
            json.dumps(
                {
                    "metric": {"__name__": "idm_heatpump_temp"},
                    "values": [20.5],
                    "timestamps": [1000],
                }
            ).encode(),
        ]

        # Mock Server Submit response
        mock_response_server = MagicMock()
        mock_response_server.status_code = 200

        mock_requests.get.return_value = mock_response_vm
        mock_requests.post.return_value = mock_response_server

        # Run
        success = self.tm.submit_data()

        self.assertTrue(success)
        mock_requests.get.assert_called()
        mock_requests.post.assert_called()

        args, kwargs = mock_requests.post.call_args
        self.assertEqual(args[0], "http://test-server/api/v1/submit")

    @patch("idm_logger.telemetry.requests")
    def test_submit_data_batching(self, mock_requests):
        self.mock_get.side_effect = lambda k, d=None: {
            "telemetry.enabled": True,
            "telemetry.server_url": "http://test-server",
            "telemetry.auth_token": "token",
            "metrics.url": "http://vm:8428/write",
            "installation_id": "uuid",
            "hp_model": "TestModel",
        }.get(k, d)

        self.tm._load_state()

        # 1100 records (to force batching since MAX_BATCH_SIZE=1000)
        records = []
        for i in range(1100):
            records.append(
                json.dumps(
                    {
                        "metric": {"__name__": "idm_heatpump_temp"},
                        "values": [i],
                        "timestamps": [i * 1000],
                    }
                ).encode()
            )

        mock_response_vm = MagicMock()
        mock_response_vm.status_code = 200
        mock_response_vm.iter_lines.return_value = records
        mock_requests.get.return_value = mock_response_vm
        mock_requests.post.return_value = MagicMock(status_code=200)

        # Run
        success = self.tm.submit_data()

        self.assertTrue(success)
        self.assertEqual(mock_requests.post.call_count, 2)

    @patch("idm_logger.telemetry.requests")
    def test_download_model_success(self, mock_requests):
        self.mock_get.side_effect = lambda k, d=None: {
            "installation_id": "uuid",
            "hp_model": "TestModel",
            "telemetry.server_url": "http://test-server",
            "internal_api_key": "secret",
        }.get(k, d)

        self.tm._load_state()

        # Responses
        mock_resp_check = MagicMock()
        mock_resp_check.status_code = 200
        mock_resp_check.json.return_value = {
            "eligible": True,
            "model_available": True,
            "update_available": True,
        }

        # Encrypted Model
        try:
            from cryptography.fernet import Fernet

            key = DEFAULT_ENCRYPTION_KEY
            f = Fernet(key)
            original_data = b"serialized_model_data"
            encrypted_data = f.encrypt(original_data)
            payload_b64 = base64.b64encode(encrypted_data).decode("utf-8")
        except ImportError:
            self.skipTest("cryptography module missing")

        metadata = {"filename": "model.pkl"}
        metadata_json = json.dumps(metadata, sort_keys=True)
        msg = f"{payload_b64}.{metadata_json}".encode("utf-8")
        signature = hmac.new(key, msg, hashlib.sha256).hexdigest()

        envelope = {
            "payload": payload_b64,
            "metadata": metadata,
            "signature": signature,
        }

        mock_resp_download = MagicMock()
        mock_resp_download.status_code = 200
        mock_resp_download.json.return_value = envelope
        # Content is needed for hash verification
        mock_resp_download.content = json.dumps(envelope).encode("utf-8")
        # Headers needed to avoid MagicMock in get()
        actual_hash = hashlib.sha256(mock_resp_download.content).hexdigest()
        mock_resp_download.headers = {"X-Model-Hash": actual_hash}

        mock_resp_upload = MagicMock()
        mock_resp_upload.status_code = 200

        mock_requests.get.side_effect = [mock_resp_check, mock_resp_download]
        mock_requests.post.return_value = mock_resp_upload

        # Run
        success = self.tm.download_and_install_model(manual=True)

        self.assertTrue(success)

    def test_rate_limit(self):
        self.tm.manual_downloads_today = 3
        with self.assertRaises(Exception) as cm:
            self.tm.download_and_install_model(manual=True)
        self.assertIn("Limit", str(cm.exception))

    @patch("idm_logger.telemetry.requests")
    def test_admin_status_update(self, mock_requests):
        """Test that is_admin status is correctly updated from server response."""
        self.mock_get.side_effect = lambda k, d=None: {
            "installation_id": "uuid",
            "hp_model": "TestModel",
            "telemetry.server_url": "http://test-server",
        }.get(k, d)

        self.tm._load_state()

        # Case 1: Server says is_admin = True
        mock_resp_check_true = MagicMock()
        mock_resp_check_true.status_code = 200
        mock_resp_check_true.json.return_value = {
            "eligible": True,
            "model_available": False,
            "update_available": False,
            "is_admin": True,
            "server_stats": {"active_installations": 10},
        }

        mock_requests.get.return_value = mock_resp_check_true

        # Run
        try:
            self.tm.download_and_install_model(manual=True)
        except Exception:
            pass  # Expected because model_available=False

        # Verify
        self.assertTrue(self.tm.is_admin)
        self.assertEqual(self.tm.server_stats["active_installations"], 10)

        # Case 2: Server says is_admin = False
        mock_resp_check_false = MagicMock()
        mock_resp_check_false.status_code = 200
        mock_resp_check_false.json.return_value = {
            "eligible": True,
            "model_available": False,
            "update_available": False,
            "is_admin": False,
        }

        mock_requests.get.return_value = mock_resp_check_false

        # Run again
        try:
            self.tm.download_and_install_model(manual=True)
        except Exception:
            pass

        # Verify
        self.assertFalse(self.tm.is_admin)
        self.assertIsNone(self.tm.server_stats)


if __name__ == "__main__":
    unittest.main()
