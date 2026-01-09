#!/usr/bin/env python3
"""
Test script to verify webserver functionality
"""
import sys
import os
import time
import threading
import urllib.request
import json

# Add the project directory to path
sys.path.insert(0, '/home/user/idm-metrics-collector')

def test_webserver():
    """Test the webserver by making HTTP requests"""
    print("=" * 60)
    print("WEBSERVER TEST")
    print("=" * 60)

    # Import after path is set
    from idm_logger.web import app
    from waitress import serve

    # Configure for testing
    app.config['TESTING'] = True
    port = 5555  # Use different port for testing
    host = '127.0.0.1'

    # Start server in background thread
    def run_server():
        try:
            print(f"\n✓ Starting test server on {host}:{port}...")
            serve(app, host=host, port=port, _quiet=True)
        except Exception as e:
            print(f"✗ Server error: {e}")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("✓ Waiting for server to initialize...")
    time.sleep(2)

    # Test cases
    tests_passed = 0
    tests_failed = 0

    base_url = f"http://{host}:{port}"

    # Test 1: Health endpoint
    print("\n" + "-" * 60)
    print("Test 1: GET /api/health")
    try:
        response = urllib.request.urlopen(f"{base_url}/api/health", timeout=5)
        data = json.loads(response.read().decode())
        # Accept both 'ok' and 'healthy' as valid statuses
        if response.status == 200 and data.get('status') in ['ok', 'healthy']:
            print(f"✓ PASSED - Status: {response.status}, Response: {data}")
            tests_passed += 1
        else:
            print(f"✗ FAILED - Unexpected response: {data}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ FAILED - Error: {e}")
        tests_failed += 1

    # Test 2: Root endpoint (SPA)
    print("\n" + "-" * 60)
    print("Test 2: GET / (root - SPA index.html)")
    try:
        response = urllib.request.urlopen(f"{base_url}/", timeout=5)
        html = response.read().decode()
        if response.status == 200 and '<!doctype html>' in html.lower() and 'id="app"' in html:
            print(f"✓ PASSED - Status: {response.status}")
            print(f"  HTML contains: <!doctype html> and <div id=\"app\">")
            tests_passed += 1
        else:
            print(f"✗ FAILED - Invalid HTML response")
            print(f"  First 200 chars: {html[:200]}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ FAILED - Error: {e}")
        tests_failed += 1

    # Test 3: Catch-all route (for SPA routing)
    print("\n" + "-" * 60)
    print("Test 3: GET /dashboard (catch-all route for Vue Router)")
    try:
        response = urllib.request.urlopen(f"{base_url}/dashboard", timeout=5)
        html = response.read().decode()
        if response.status == 200 and '<!doctype html>' in html.lower() and 'id="app"' in html:
            print(f"✓ PASSED - Status: {response.status}")
            print(f"  Catch-all route correctly serves index.html")
            tests_passed += 1
        else:
            print(f"✗ FAILED - Catch-all route not working")
            tests_failed += 1
    except Exception as e:
        print(f"✗ FAILED - Error: {e}")
        tests_failed += 1

    # Test 4: Auth check endpoint
    print("\n" + "-" * 60)
    print("Test 4: GET /api/auth/check")
    try:
        response = urllib.request.urlopen(f"{base_url}/api/auth/check", timeout=5)
        data = json.loads(response.read().decode())
        if response.status == 200 and 'authenticated' in data:
            print(f"✓ PASSED - Status: {response.status}, Response: {data}")
            tests_passed += 1
        else:
            print(f"✗ FAILED - Unexpected response: {data}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ FAILED - Error: {e}")
        tests_failed += 1

    # Test 5: Static assets
    print("\n" + "-" * 60)
    print("Test 5: GET /static/vite.svg (static file)")
    try:
        response = urllib.request.urlopen(f"{base_url}/static/vite.svg", timeout=5)
        if response.status == 200:
            print(f"✓ PASSED - Status: {response.status}")
            print(f"  Static files are served correctly")
            tests_passed += 1
        else:
            print(f"✗ FAILED - Status: {response.status}")
            tests_failed += 1
    except Exception as e:
        print(f"✗ FAILED - Error: {e}")
        tests_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests:  {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("\n✓ ALL TESTS PASSED - Webserver is working correctly!")
        print("=" * 60)
        return 0
    else:
        print(f"\n✗ {tests_failed} TEST(S) FAILED - Please review errors above")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    try:
        sys.exit(test_webserver())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
