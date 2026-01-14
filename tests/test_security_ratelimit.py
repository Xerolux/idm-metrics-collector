
import sys
import os
import time
import unittest
from unittest.mock import MagicMock, patch

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from idm_logger.web import app, login_attempts

class TestRateLimitSecurity(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clear login attempts before each test
        login_attempts.clear()

    def test_login_attempts_memory_leak(self):
        """Test that login_attempts does not grow indefinitely."""

        # Simulate attacks from many different IPs
        num_ips = 2000

        # We need to patch request.remote_addr for each call
        # Since we can't easily patch it inside the loop for the client call
        # (client.post doesn't take remote_addr argument easily without environ_overrides),
        # we will use environ_overrides.

        for i in range(num_ips):
            ip = f"10.0.{i // 256}.{i % 256}"
            self.app.post('/login',
                          json={'password': 'wrong'},
                          environ_overrides={'REMOTE_ADDR': ip})

        # Check size of login_attempts
        print(f"Login attempts size: {len(login_attempts)}")

        # IF vulnerability exists, size should be num_ips
        # We want to assert that it is capped (e.g. at 1000)
        # But first we want to reproduce the failure, so we assert it IS num_ips for now to prove leak?
        # No, I should write the test to FAIL if leak exists (i.e., Assert size <= 1000)

        # Assert that the size is limited (e.g. max 1000 IPs tracked)
        self.assertLessEqual(len(login_attempts), 1050, "login_attempts grew too large! Memory leak detected.")

if __name__ == '__main__':
    unittest.main()
