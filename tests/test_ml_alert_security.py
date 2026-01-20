#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Test script to verify ML Alert Endpoint Security
"""

import sys
import os
import pytest
from unittest.mock import patch

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from idm_logger.web import app

def test_ml_alert_security():
    """Test the ML alert endpoint security using Flask test client"""
    print("=" * 60)
    print("ML ALERT SECURITY TEST (Flask Client)")
    print("=" * 60)

    app.config["TESTING"] = True
    client = app.test_client()

    endpoint = "/api/internal/ml_alert"
    payload = {"score": 0.9, "message": "Test alert"}
    secret = "supersecretkey"

    # Patch the INTERNAL_API_KEY in the web module
    with patch("idm_logger.web.INTERNAL_API_KEY", secret):

        # Test 1: No header -> Should be 401
        print("\nTest 1: POST /api/internal/ml_alert (No Header)")
        response = client.post(endpoint, json=payload)
        print(f"  Status: {response.status_code}")

        if response.status_code == 401:
             print("✓ PASSED - Request rejected with 401")
        else:
            pytest.fail(f"Test 1 FAILED - Expected 401, got {response.status_code}")

        # Test 2: Wrong header -> Should be 401
        print("\nTest 2: POST /api/internal/ml_alert (Wrong Header)")
        response = client.post(endpoint, json=payload, headers={'X-Internal-Secret': 'wrongkey'})
        print(f"  Status: {response.status_code}")

        if response.status_code == 401:
             print("✓ PASSED - Request rejected with 401")
        else:
            pytest.fail(f"Test 2 FAILED - Expected 401, got {response.status_code}")

        # Test 3: Correct header -> Should be 200
        print("\nTest 3: POST /api/internal/ml_alert (Correct Header)")
        response = client.post(endpoint, json=payload, headers={'X-Internal-Secret': secret})
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("✓ PASSED - Request succeeded")
        else:
            pytest.fail(f"Test 3 FAILED - Expected 200, got {response.status_code}")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    pytest.main([__file__])
