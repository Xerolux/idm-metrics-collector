#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Test script to verify webserver functionality
"""

import sys
import os
import time
import threading
import urllib.request
import json
import pytest

# Add the project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_webserver():
    """Test the webserver by making HTTP requests"""
    print("=" * 60)
    print("WEBSERVER TEST")
    print("=" * 60)

    # Import after path is set
    from idm_logger.web import app
    from waitress import serve

    # Configure for testing
    app.config["TESTING"] = True
    port = 5555  # Use different port for testing
    host = "127.0.0.1"
    base_url = f"http://{host}:{port}"
    server_error = None

    # Setup: Create dummy index.html if not exists
    # This is required because the backend tests might run without a frontend build
    from pathlib import Path
    static_dir = Path(os.path.join(os.path.dirname(__file__), "..", "idm_logger", "static"))
    index_file = static_dir / "index.html"
    created_dummy = False

    # Ensure static directory exists
    static_dir.mkdir(parents=True, exist_ok=True)

    if not index_file.exists():
        print(f"\n✓ Creating dummy {index_file} for testing...")
        try:
            with open(index_file, "w") as f:
                f.write('<!doctype html><html><body><div id="app"></div></body></html>')
            created_dummy = True
        except Exception as e:
            print(f"✗ Failed to create dummy index.html: {e}")

    # Start server in background thread
    def run_server():
        nonlocal server_error
        try:
            print(f"\n✓ Starting test server on {host}:{port}...")
            serve(app, host=host, port=port, _quiet=True)
        except Exception as e:
            print(f"✗ Server error: {e}")
            server_error = e

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("✓ Waiting for server to initialize...")
    time.sleep(2)

    if server_error:
        pytest.fail(f"Server failed to start: {server_error}")

    # Test cases
    failures = []

    # Test 1: Health endpoint
    print("\n" + "-" * 60)
    print("Test 1: GET /api/health")
    try:
        response = urllib.request.urlopen(f"{base_url}/api/health", timeout=5)
        data = json.loads(response.read().decode())
        # Accept both 'ok' and 'healthy' as valid statuses
        if response.status == 200 and data.get("status") in ["ok", "healthy"]:
            print(f"✓ PASSED - Status: {response.status}, Response: {data}")
        else:
            msg = f"Test 1 FAILED - Unexpected response: {data}"
            print(f"✗ {msg}")
            failures.append(msg)
    except Exception as e:
        msg = f"Test 1 FAILED - Error: {e}"
        print(f"✗ {msg}")
        failures.append(msg)

    # Test 2: Root endpoint (SPA)
    print("\n" + "-" * 60)
    print("Test 2: GET / (root - SPA index.html)")
    try:
        response = urllib.request.urlopen(f"{base_url}/", timeout=5)
        html = response.read().decode()
        if (
            response.status == 200
            and "<!doctype html>" in html.lower()
            and 'id="app"' in html
        ):
            print(f"✓ PASSED - Status: {response.status}")
            print('  HTML contains: <!doctype html> and <div id="app">')
        else:
            msg = "Test 2 FAILED - Invalid HTML response"
            print(f"✗ {msg}")
            print(f"  First 200 chars: {html[:200]}")
            failures.append(msg)
    except Exception as e:
        msg = f"Test 2 FAILED - Error: {e}"
        print(f"✗ {msg}")
        failures.append(msg)

    # Test 3: Catch-all route (for SPA routing)
    print("\n" + "-" * 60)
    print("Test 3: GET /dashboard (catch-all route for Vue Router)")
    try:
        response = urllib.request.urlopen(f"{base_url}/dashboard", timeout=5)
        html = response.read().decode()
        if (
            response.status == 200
            and "<!doctype html>" in html.lower()
            and 'id="app"' in html
        ):
            print(f"✓ PASSED - Status: {response.status}")
            print("  Catch-all route correctly serves index.html")
        else:
            msg = "Test 3 FAILED - Catch-all route not working"
            print(f"✗ {msg}")
            failures.append(msg)
    except Exception as e:
        msg = f"Test 3 FAILED - Error: {e}"
        print(f"✗ {msg}")
        failures.append(msg)

    # Test 4: Auth check endpoint
    print("\n" + "-" * 60)
    print("Test 4: GET /api/auth/check")
    try:
        response = urllib.request.urlopen(f"{base_url}/api/auth/check", timeout=5)
        data = json.loads(response.read().decode())
        if response.status == 200 and "authenticated" in data:
            print(f"✓ PASSED - Status: {response.status}, Response: {data}")
        else:
            msg = f"Test 4 FAILED - Unexpected response: {data}"
            print(f"✗ {msg}")
            failures.append(msg)
    except Exception as e:
        msg = f"Test 4 FAILED - Error: {e}"
        print(f"✗ {msg}")
        failures.append(msg)

    # Test 5: Static assets
    print("\n" + "-" * 60)
    print("Test 5: GET /static/vite.svg (static file)")
    try:
        response = urllib.request.urlopen(f"{base_url}/static/vite.svg", timeout=5)
        if response.status == 200:
            print(f"✓ PASSED - Status: {response.status}")
            print("  Static files are served correctly")
        else:
            msg = f"Test 5 FAILED - Status: {response.status}"
            print(f"✗ {msg}")
            failures.append(msg)
    except Exception as e:
        msg = f"Test 5 FAILED - Error: {e}"
        print(f"✗ {msg}")
        failures.append(msg)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    # Teardown: Remove dummy index.html if we created it
    if created_dummy and index_file.exists():
        print(f"\n✓ Removing dummy {index_file}...")
        try:
            os.remove(index_file)
        except Exception as e:
            print(f"✗ Failed to remove dummy index.html: {e}")

    if failures:
        print(f"✗ {len(failures)} TEST(S) FAILED:")
        for fail in failures:
            print(f"  - {fail}")
        print("=" * 60)
        assert False, f"Webserver tests failed: {failures}"
    else:
        print("\n✓ ALL TESTS PASSED - Webserver is working correctly!")
        print("=" * 60)


if __name__ == "__main__":
    try:
        test_webserver()
        sys.exit(0)
    except AssertionError:
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
