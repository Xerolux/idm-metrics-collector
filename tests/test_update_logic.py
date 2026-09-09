# Xerolux 2026
# SPDX-License-Identifier: MIT
import unittest
from unittest.mock import MagicMock, patch
from idm_logger import update_manager


class TestUpdateLogic(unittest.TestCase):
    @patch("idm_logger.update_manager.subprocess.run")
    @patch("idm_logger.update_manager.requests.get")
    @patch("idm_logger.update_manager.requests.head")
    def test_update_available_when_digests_differ(self, mock_head, mock_get, mock_run):
        # Mock Docker version check
        mock_run.side_effect = self._mock_subprocess_side_effect

        # Mock GHCR Token
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"token": "fake-token"}

        # Mock Remote Digest (Newer)
        mock_head.return_value.status_code = 200
        mock_head.return_value.headers = {
            "Docker-Content-Digest": "sha256:remote_digest"
        }

        # Helper to handle subprocess calls dynamically
        # We need to return different things for different commands
        # 1. docker --version -> ok
        # 2. docker images ... -> returns local ID (unused in digest path usually, but helper calls it?)
        # 3. docker inspect ... -> returns local digest

        result = update_manager.check_for_update()

        self.assertTrue(result["update_available"])
        self.assertEqual(result["update_type"], "patch")
        self.assertIn("Neues Docker Image verfügbar", result["release_notes"])

    @patch("idm_logger.update_manager.subprocess.run")
    @patch("idm_logger.update_manager.requests.get")
    @patch("idm_logger.update_manager.requests.head")
    def test_no_update_when_digests_match(self, mock_head, mock_get, mock_run):
        mock_run.side_effect = self._mock_subprocess_side_effect_matching

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"token": "fake-token"}

        mock_head.return_value.status_code = 200
        mock_head.return_value.headers = {
            "Docker-Content-Digest": "sha256:local_digest"
        }

        result = update_manager.check_for_update()

        self.assertFalse(result["update_available"])
        self.assertEqual(result["update_type"], "none")

    def _mock_subprocess_side_effect(self, args, **kwargs):
        cmd = " ".join(args)
        mock_res = MagicMock()
        mock_res.returncode = 0

        if "docker --version" in cmd:
            return mock_res

        if "docker inspect" in cmd:
            # Return a local digest different from remote
            mock_res.stdout = (
                "ghcr.io/xerolux/idm-metrics-collector@sha256:local_digest"
            )
            return mock_res

        return mock_res

    def _mock_subprocess_side_effect_matching(self, args, **kwargs):
        cmd = " ".join(args)
        mock_res = MagicMock()
        mock_res.returncode = 0

        if "docker --version" in cmd:
            return mock_res

        if "docker inspect" in cmd:
            # Return same digest as remote mock
            mock_res.stdout = (
                "ghcr.io/xerolux/idm-metrics-collector@sha256:local_digest"
            )
            return mock_res

        return mock_res


if __name__ == "__main__":
    unittest.main()
