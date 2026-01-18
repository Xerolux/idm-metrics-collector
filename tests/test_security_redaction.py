#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Test script to verify config security (redaction of passwords)
"""

import sys
import os
import time
import threading
import json
import requests
import pytest

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_config_security():
    """Test that /api/config does NOT expose plaintext passwords"""
    print("=" * 60)
    print("CONFIG SECURITY TEST")
    print("=" * 60)

    # Import after path is set
    from idm_logger.web import app, config
    from waitress import serve

    # Configure for testing
    app.config["TESTING"] = True
    app.secret_key = "test_secret"
    port = 5556  # Use different port for testing
    host = "127.0.0.1"
    base_url = f"http://{host}:{port}"

    # Inject sensitive data
    config.data["mqtt"]["password"] = "mqtt_secret_123"
    config.data["email"]["password"] = "email_secret_456"
    config.data["webdav"]["password"] = "webdav_secret_789"

    # Set admin password for login
    config.set_admin_password("admin123")

    server_error = None

    # Start server in background thread
    def run_server():
        nonlocal server_error
        try:
            serve(app, host=host, port=port, _quiet=True)
        except Exception as e:
            server_error = e

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    if server_error:
        pytest.fail(f"Server failed to start: {server_error}")

    session = requests.Session()

    # 1. Login
    print("Logging in...")
    resp = session.post(f"{base_url}/login", json={"password": "admin123"})
    if resp.status_code != 200:
        pytest.fail(f"Login failed: {resp.text}")

    # 2. Get Config
    print("Fetching config...")
    resp = session.get(f"{base_url}/api/config")
    if resp.status_code != 200:
        pytest.fail(f"Failed to get config: {resp.text}")

    data = resp.json()

    # 3. Check for exposed secrets
    exposed = []

    if data.get("mqtt", {}).get("password") == "mqtt_secret_123":
        exposed.append("MQTT password")

    if data.get("email", {}).get("password") == "email_secret_456":
        exposed.append("Email password")

    if data.get("webdav", {}).get("password") == "webdav_secret_789":
        exposed.append("WebDAV password")

    if exposed:
        print(f"⚠️  VULNERABILITY CONFIRMED: Exposed secrets: {', '.join(exposed)}")
    else:
        print("✅ SECURE: No secrets exposed in /api/config")

    # FOR VERIFICATION: Assert that we CANNOT see the secrets
    assert "MQTT password" not in exposed, "Fix failed: MQTT password still exposed"
    assert "Email password" not in exposed, "Fix failed: Email password still exposed"
    assert "WebDAV password" not in exposed, "Fix failed: WebDAV password still exposed"

    # Assert values are None (which JSON serializes to null)
    # The fix uses `conf["mqtt"]["password"] = None`
    assert data.get("mqtt", {}).get("password") is None, f"Expected None/null, got {data.get('mqtt', {}).get('password')}"
    assert data.get("email", {}).get("password") is None
    assert data.get("webdav", {}).get("password") is None

    print("\n✓ Verification successful: Secrets are redacted.")

if __name__ == "__main__":
    try:
        test_config_security()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
