
import re
import time
from playwright.sync_api import Page, expect, sync_playwright

def verify_admin_ui(page: Page):
    # Mock Auth
    page.route("**/api/auth/check", lambda route: route.fulfill(json={"authenticated": True}))
    page.route("**/login", lambda route: route.fulfill(json={"success": True}))

    # Mock local API
    page.route("**/api/config", lambda route: route.fulfill(json={
        "installation_id": "test-install-id",
        "hp_model": "TestModel",
        "idm": {"host": "1.2.3.4", "port": 502, "circuits": ["A"], "zones": []},
        "metrics": {"url": "http://vm:8428/write"},
        "web": {"write_enabled": False},
        "logging": {"interval": 60, "realtime_mode": False},
        "mqtt": {"enabled": False},
        "network_security": {"enabled": False},
        "signal": {"enabled": False},
        "telegram": {"enabled": False},
        "discord": {"enabled": False},
        "email": {"enabled": False},
        "webdav": {"enabled": False},
        "ai": {"enabled": False},
        "telemetry": {"enabled": True, "url": "https://collector.xerolux.de"},
        "updates": {"enabled": False},
        "backup": {"enabled": False}
    }))

    page.route("**/api/telemetry/status", lambda route: route.fulfill(json={
        "is_admin": True,
        "server_url": "https://collector.xerolux.de",
        "last_submission": 1700000000,
        "last_model_check": 1700000000,
        "manual_downloads_today": 0,
        "server_stats": {
            "total_points": 1000000,
            "active_installations": 50,
            "models": [{"name": "TestModel"}]
        }
    }))

    page.route("**/api/check-update", lambda route: route.fulfill(json={"update_available": False}))
    page.route("**/api/signal/status", lambda route: route.fulfill(json={"status": "ok"}))
    page.route("**/api/ai/status", lambda route: route.fulfill(json={"online": True}))
    page.route("**/api/info", lambda route: route.fulfill(json={"heat_pump_models": ["TestModel"]}))
    page.route("**/api/health", lambda route: route.fulfill(json={"client_ip": "127.0.0.1"}))
    page.route("**/api/backup/list", lambda route: route.fulfill(json={"backups": []}))

    # Mock Telemetry Server APIs

    def handle_telemetry(route):
        print(f"Telemetry Request: {route.request.url}")
        url = route.request.url
        if "/api/v1/admin/health" in url:
            route.fulfill(json={"server": {"hostname": "test-server"}, "victoriametrics": {"healthy": True}, "models": {"count": 1}})
        elif "/api/v1/admin/installations/list" in url:
             route.fulfill(json={"items": [{"installation_id": "inst-1", "role": "admin"}]})
        elif "/api/v1/admin/installations" in url:
            route.fulfill(json={"installations": [{"installation_id": "inst-1", "data_points": 100}], "total": 1})
        elif "/api/v1/admin/models" in url:
            route.fulfill(json={"models": [{"name": "TestModel", "size_mb": 1.0, "modified_formatted": "2024-01-01", "download_count": 5}], "total": 1})
        elif "/api/v1/admin/metrics" in url:
            route.fulfill(json={"requests": {"total": 100}, "business": {"submissions": 50}})
        elif "/api/v1/community/averages" in url:
            route.fulfill(json={"model": "TestModel", "sample_size": 10, "metrics": {"cop": {"avg": 3.5}}})
        # NEW APIs
        elif "/api/v1/admin/audit-log" in url:
            route.fulfill(json={"events": [
                {"timestamp": 1700000000, "action": "test_action", "admin_id": "admin-1", "success": True}
            ]})
        elif "/api/v1/admin/training/current" in url:
            route.fulfill(json={"running": True, "task_id": "task-123", "started_at": 1700000000})
        elif "/api/v1/admin/training/history" in url:
            route.fulfill(json={"tasks": [
                {"task_id": "task-001", "status": "completed", "created_at": 1699990000, "duration": 120.5}
            ]})
        elif "/api/v1/admin/permissions" in url:
            route.fulfill(json={"admins": {
                "admin-1": {"permissions": ["admin:full"], "effective_permissions": ["admin:full", "admin:view"]}
            }})
        else:
            print(f"Unhandled telemetry URL: {url}")
            route.fulfill(status=404)

    page.route(re.compile(r"https://collector\.xerolux\.de/.*"), handle_telemetry)

    print("Navigating...")
    page.goto("http://localhost:5173/static/#/config")

    # Check if we are on login page
    try:
        if page.get_by_text("idm-metrics-collector").is_visible(timeout=2000):
            print("Redirected to Login. Attempting to login...")
            page.get_by_placeholder("Passwort eingeben").fill("password")
            page.get_by_role("button", name="Login").click()
            print("Clicked login...")
    except Exception as e:
        print(f"Not on login page or error: {e}")

    # Wait for loading to finish (use heading)
    print("Waiting for Konfiguration...")
    expect(page.get_by_role("heading", name="Konfiguration")).to_be_visible(timeout=10000)

    print("Clicking Admin Zone...")
    page.get_by_role("button", name="Admin Zone").click()

    # Verify new sections are visible - Using exact texts from legends
    # Fieldset legends are inside a button usually in PrimeVue or just legend element?
    # In Config.vue: <Fieldset legend="Audit Log" ...>
    # PrimeVue renders legend as a <span class="p-fieldset-legend-label">...</span> inside a <button> or <a> if toggleable.

    # We can check for the text "Audit Log" but ensuring it's the legend.
    # Or just wait for something inside the fieldset.

    print("Refreshing Training Info...")
    expect(page.get_by_text("Training in progress")).to_be_visible(timeout=5000) # Should come from auto-refresh

    print("Refreshing Permissions...")
    page.locator("fieldset").filter(has_text="Permission Management").get_by_role("button", name="Refresh").click()
    expect(page.get_by_text("admin-1")).to_be_visible(timeout=5000)

    print("Refreshing Audit Log...")
    page.locator("fieldset").filter(has_text="Audit Log").get_by_role("button", name="Refresh Log").click()
    expect(page.get_by_text("test_action")).to_be_visible(timeout=5000)

    # Take screenshot
    page.screenshot(path="verification/verification.png", full_page=True)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
        try:
            verify_admin_ui(page)
            print("Verification script executed successfully.")
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
