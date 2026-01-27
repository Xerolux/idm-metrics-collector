from playwright.sync_api import sync_playwright, expect
import json

def verify_i18n(page):
    # Log console messages
    page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"Browser Error: {err}"))

    full_config = {
        "idm": {"host": "", "port": 502, "circuits": ["A"], "zones": []},
        "metrics": {"url": ""},
        "web": {"write_enabled": False},
        "logging": {"interval": 60, "realtime_mode": False},
        "mqtt": {"enabled": False},
        "network_security": {"enabled": False, "whitelist": [], "blacklist": []},
        "signal": {"enabled": False, "recipients": []},
        "telegram": {"enabled": False, "chat_ids": []},
        "discord": {"enabled": False},
        "email": {"enabled": False, "recipients": []},
        "webdav": {"enabled": False},
        "ai": {"enabled": True},
        "updates": {"enabled": False, "channel": "latest"},
        "backup": {"enabled": False},
        "heatpump_model": "",
        "share_data": True,
        "telemetry_auth_token": ""
    }

    # Mock API responses
    page.route("**/api/auth/check", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"authenticated": true}'
    ))
    page.route("**/api/config", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(full_config)
    ))
    page.route("**/api/health", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"client_ip": "127.0.0.1", "status": "ok"}'
    ))
    page.route("**/api/backup/list", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"backups": []}'
    ))
    page.route("**/api/check-update**", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"update_available": false}'
    ))
    page.route("**/api/signal/status", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{}'
    ))
    page.route("**/api/ai/status", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"online": true, "service": "mock", "source": "Local"}'
    ))
    page.route("**/api/telemetry/pool-status", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"data_sufficient": true, "total_installations": 42, "total_data_points": 100000, "models_available": ["AERO_SLM"], "message": "Ready"}'
    ))

    # Navigate to Config page (hash router) with base
    page.goto("http://localhost:5173/static/#/config")

    # Wait for page to load
    page.wait_for_selector("h1", state="visible")

    # Click on "KI-Analyse" tab
    page.get_by_role("tab", name="KI-Analyse").click()

    # Wait for content
    page.wait_for_timeout(2000)

    # Take screenshot
    page.screenshot(path="verification/verification.png", full_page=True)
    print("Screenshot taken.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_i18n(page)
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
