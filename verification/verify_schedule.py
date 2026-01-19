from playwright.sync_api import sync_playwright

def verify_schedule_accessibility():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use existing context to reuse state if possible, or new context
        # We need to bypass auth or login
        context = browser.new_context()
        page = context.new_page()

        # Handle console messages
        page.on("console", lambda msg: print(f"Console: {msg.text}"))

        # Mock the auth check to avoid login
        page.route("**/api/auth/check", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"authenticated": true, "must_change_password": false}'
        ))

        # Mock schedule data
        page.route("**/api/schedule", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"jobs": [{"id": 1, "sensor": "Temperature", "value": "22", "time": "08:00", "days": ["Mon"], "enabled": true}], "sensors": [{"name": "Temperature"}]}'
        ))

        # Also mock /api/config which might be called in App.vue or Layout.vue
        page.route("**/api/config", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{}'
        ))

        # Also mock /api/health
        page.route("**/api/health", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"status": "ok"}'
        ))

        # NOTE: Using hash history mode based on router/index.js
        page.goto("http://localhost:5173/static/#/schedule")

        # Wait for content to load, try waiting for body first
        page.wait_for_selector("body")

        # Wait for the specific element, increase timeout
        try:
            page.wait_for_selector(".p-card", timeout=10000)
        except Exception as e:
            print(f"Error waiting for .p-card: {e}")
            page.screenshot(path="verification/error_state.png")
            # Dump page content
            print(page.content())
            return

        # Verify aria-labels are present
        buttons = page.locator(".p-card-footer button")
        count = buttons.count()
        print(f"Found {count} buttons in footer")

        for i in range(count):
            btn = buttons.nth(i)
            aria_label = btn.get_attribute("aria-label")
            print(f"Button {i} aria-label: {aria_label}")
            if not aria_label:
                print(f"Error: Button {i} missing aria-label")

        # Take screenshot
        page.screenshot(path="verification/schedule_buttons.png")
        browser.close()

if __name__ == "__main__":
    verify_schedule_accessibility()
