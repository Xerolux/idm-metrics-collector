import datetime
import re
import json
from playwright.sync_api import sync_playwright

def calculate_expected_codes():
    now = datetime.datetime.now()

    # Level 1: DDMM
    level1 = f"{now.day:02d}{now.month:02d}"

    # Level 2: hh_last + hh_first + year_last + month_last + day_last
    # Note: Python's now.hour is 0-23.
    hours_str = f"{now.hour:02d}"
    hh_first = hours_str[0]
    hh_last = hours_str[1]

    year_last = str(now.year)[-1]
    month_last = str(now.month)[-1]
    day_last = str(now.day)[-1]

    level2 = f"{hh_last}{hh_first}{year_last}{month_last}{day_last}"

    return level1, level2

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Enable console logs
    page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
    page.on("request", lambda request: print(f">> {request.method} {request.url}"))
    page.on("response", lambda response: print(f"<< {response.status} {response.url}"))

    # Mock Auth and Config
    # Using regex to catch any variation of the URL
    page.route(re.compile(r".*/api/auth/.*"), lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"authenticated": true, "user": "admin"}'
    ))

    # Complete Config Mock to avoid Vue errors
    config_mock = {
        "idm": {"host": "192.168.1.10", "port": 502, "circuits": ["A"], "zones": []},
        "logging": {"interval": 60, "realtime_mode": False},
        "influx": {"url": "http://localhost:8086", "org": "myorg", "bucket": "mybucket"},
        "web": {"write_enabled": True},
        "mqtt": {"enabled": False},
        "network_security": {"enabled": False, "whitelist": [], "blacklist": []}
    }

    page.route(re.compile(r".*/api/config"), lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(config_mock)
    ))

    page.route(re.compile(r".*/api/health"), lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"client_ip": "127.0.0.1"}'
    ))

    page.route(re.compile(r".*/api/backup/list"), lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"backups": []}'
    ))

    try:
        # Navigate to the config page
        # Using the Vite dev server URL
        url = "http://localhost:5175/static/#/config"
        print(f"Navigating to {url}")
        page.goto(url)

        # Check if we are stuck on login
        try:
            page.wait_for_selector("input[placeholder='Password']", timeout=2000)
            print("Detected Login Page. Attempting to bypass...")
        except:
            pass

        print("Waiting for Configuration header...")
        page.wait_for_selector("h1:text('Configuration')", timeout=15000)

        # Click on Tools tab
        print("Clicking Tools tab...")
        # Use a more specific selector if generic text fails, but text=Tools is usually good for PrimeVue tabs
        page.click("text=Tools")

        # Wait for Technician Code Generator to appear
        print("Waiting for component...")
        page.wait_for_selector("text=Technician Code Generator")
        page.wait_for_selector("text=Reference Time")

        # Verify Level 1 Code
        expected_l1, expected_l2 = calculate_expected_codes()
        print(f"Expected Codes: L1={expected_l1}, L2={expected_l2}")

        # Get displayed codes
        l1_element = page.locator("span.text-blue-400")
        l1_text = l1_element.inner_text().strip()

        l2_element = page.locator("span.text-green-400")
        l2_text = l2_element.inner_text().strip()

        print(f"Found Codes: L1={l1_text}, L2={l2_text}")

        # Assertions
        assert l1_text == expected_l1, f"Level 1 mismatch: expected {expected_l1}, got {l1_text}"
        assert l2_text == expected_l2, f"Level 2 mismatch: expected {expected_l2}, got {l2_text}"

        print("Verification Successful!")
        page.screenshot(path="verification_success.png")

    except Exception as e:
        print(f"Verification Failed: {e}")
        page.screenshot(path="verification_failure.png")
        raise e
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
