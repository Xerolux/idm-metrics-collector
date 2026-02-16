import os
from playwright.sync_api import sync_playwright, expect

def verify_aria_labels(page):
    # Debugging
    page.on("console", lambda msg: print(f"Console: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"Page Error: {exc}"))

    # Mock Auth
    page.route("**/api/auth/check", lambda route: route.fulfill(json={"authenticated": True}))
    page.route("**/api/check-update", lambda route: route.fulfill(json={"update_available": False}))
    page.route("**/api/signal/status", lambda route: route.fulfill(json={}))
    page.route("**/api/telemetry/status", lambda route: route.fulfill(json={"is_admin": True}))
    page.route("**/api/ai/status", lambda route: route.fulfill(json={}))

    # Mock Config (CRITICAL: hp_model must be set to avoid setup wizard)
    page.route("**/api/config", lambda route: route.fulfill(json={
        "hp_model": "iPump T 3-13",
        "installation_id": "test-install",
        "idm": {"host": "1.2.3.4"},
        "logging": {"interval": 60}
    }))

    # Mock API responses
    page.route("**/api/dashboards", lambda route: route.fulfill(json=[
        {
            "id": "test-dashboard",
            "name": "Test Dashboard",
            "charts": [
                {
                    "id": "table-1",
                    "title": "Test Table",
                    "type": "table",
                    "queries": [{"query": "metric_b", "label": "Metric B"}]
                }
            ]
        }
    ]))

    page.route("**/api/variables", lambda route: route.fulfill(json=[]))
    page.route("**/api/annotations", lambda route: route.fulfill(json=[]))

    # Mock metric data
    page.route("**/api/query", lambda route: route.fulfill(json={
        "status": "success",
        "data": {
            "result": [],
            "values": [[1600000000, "10"], [1600000060, "20"]]
        }
    }))

    print("Navigating to dashboard...")
    page.goto("http://localhost:5173/")

    # Wait for dashboard to load
    page.wait_for_selector("[data-dashboard-id='test-dashboard']", timeout=10000)

    print("Dashboard loaded. Enabling Edit Mode...")
    # Enable Edit Mode to see Edit/Delete buttons
    page.get_by_role("button", name="Normal").click()

    # Verify TableCard buttons
    print("Verifying TableCard buttons...")

    # Edit/Delete
    assert page.get_by_label("Bearbeiten").count() >= 1, "Edit button not found"
    assert page.get_by_label("Löschen").count() >= 1, "Delete button not found"

    # Fullscreen
    assert page.get_by_label("Vollbildmodus aktivieren").count() >= 1, "Fullscreen button not found"

    # Sort
    # Default is desc, so button should allow switching to asc ("Aufsteigend sortieren")
    # Wait, if icon is sort-amount-down (desc), it means "Current is desc".
    # Usually clicking it toggles.
    # My logic: :aria-label="sortOrder === 'asc' ? 'Absteigend sortieren' : 'Aufsteigend sortieren'"
    # Default sortOrder = 'desc'. So it returns 'Aufsteigend sortieren'.
    # This implies the button action is to sort ascending.
    expect(page.get_by_label("Aufsteigend sortieren")).to_be_visible()

    # Pagination
    expect(page.get_by_label("Vorherige Seite")).to_be_visible()
    expect(page.get_by_label("Nächste Seite")).to_be_visible()

    print("All ARIA labels found!")

    # Take screenshot
    page.screenshot(path="/home/jules/verification/aria_verification.png")

if __name__ == "__main__":
    os.makedirs("/home/jules/verification", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_aria_labels(page)
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="/home/jules/verification/failure.png")
            raise
        finally:
            browser.close()
