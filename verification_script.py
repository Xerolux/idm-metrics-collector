from playwright.sync_api import sync_playwright
import json
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.on("console", lambda msg: print(f"PAGE CONSOLE: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))

    # Debug requests
    def log_response(response):
        if "api/dashboards" in response.url:
            print(f"RESPONSE api/dashboards status: {response.status}")
            try:
                print(f"RESPONSE api/dashboards body: {response.json()}")
            except:
                pass

    page.on("response", log_response)

    # Mock API endpoints
    # Register catch-all FIRST so specific routes override it (if last wins)
    page.route("**/api/*", lambda route: route.fulfill(status=200, json={}))

    # Auth
    page.route("**/api/auth/check", lambda route: route.fulfill(json={"authenticated": True}))

    # Config
    page.route("**/api/config", lambda route: route.fulfill(json={"hp_model": "AERO ALM 6-15", "admin_installations": []}))
    page.route("**/api/telemetry/status", lambda route: route.fulfill(json={"is_admin": True}))
    page.route("**/api/info", lambda route: route.fulfill(json={"heat_pump_models": ["AERO ALM 6-15"]}))

    # Dashboards
    dashboards_data = [
        {
            "id": "dash1",
            "name": "Test Dashboard",
            "charts": [
                {
                    "id": "chart1",
                    "type": "line",
                    "title": "Test Chart",
                    "queries": [{"query": "test_metric", "label": "Test Metric", "color": "#ff0000"}],
                    "hours": 12
                },
                {
                    "id": "bar1",
                    "type": "bar",
                    "title": "Test Bar",
                    "queries": [{"query": "test_metric", "label": "Test Metric", "color": "#00ff00"}],
                    "hours": 12
                },
                {
                    "id": "table1",
                    "type": "table",
                    "title": "Test Table",
                    "queries": [{"query": "test_metric", "label": "Test Metric"}],
                    "hours": 12,
                    "columns": [{"key": "timestamp", "label": "Zeit", "type": "timestamp"}, {"key": "value", "label": "Wert", "type": "number"}]
                },
                {
                    "id": "heatmap1",
                    "type": "heatmap",
                    "title": "Test Heatmap",
                    "queries": {"query": "test_metric"},
                    "hours": 12
                }
            ],
            "customCss": ""
        }
    ]
    page.route("**/api/dashboards", lambda route: route.fulfill(json=dashboards_data))

    page.route("**/api/annotations*", lambda route: route.fulfill(json=[]))
    page.route("**/api/variables*", lambda route: route.fulfill(json=[]))

    # Metrics
    page.route("**/api/metrics/query_range*", lambda route: route.fulfill(json={
        "status": "success",
        "data": {
            "resultType": "matrix",
            "result": [
                {
                    "metric": {"__name__": "test_metric"},
                    "values": [[time.time(), "100"], [time.time()-60, "90"]]
                }
            ]
        }
    }))

    page.route("**/api/query*", lambda route: route.fulfill(json={
        "status": "success",
        "data": {
            "resultType": "matrix",
            "result": [
                 {
                    "metric": {"__name__": "test_metric"},
                    "values": [[time.time(), "100"], [time.time()-60, "90"]]
                }
            ],
            "values": [[time.time(), 100], [time.time()-60, 90]]
        }
    }))

    page.route("**/api/metrics/available", lambda route: route.fulfill(json={"temperature": [{"name": "temp1", "display": "Temp 1"}]}))
    page.route("**/api/metrics/current", lambda route: route.fulfill(json={"temp1": {"value": 25, "timestamp": time.time()}}))

    print("Navigating to http://localhost:5173/static/")
    page.goto("http://localhost:5173/static/")

    # Handle Modal if it appears
    try:
        # Short timeout for modal check
        if page.is_visible("text=System Update erforderlich", timeout=2000):
            print("Handling Modal...")
            page.locator("text=Modell wählen").click()
            page.get_by_text("AERO ALM 6-15").click()
            page.get_by_role("button", name="Speichern").click()
            print("Modal dismissed.")
            page.wait_for_timeout(1000)
    except Exception as e:
        pass # Modal didn't appear or whatever

    # Wait for dashboard to load
    print("Waiting for dashboard...")
    try:
        page.wait_for_selector("[data-dashboard-id='dash1']", timeout=10000)
    except Exception as e:
        print(f"Timeout waiting for dashboard. Current URL: {page.url}")
        page.screenshot(path="timeout_screenshot_4.png")
        raise e

    print("Dashboard loaded.")

    # Click "Edit Mode"
    try:
        page.get_by_role("button", name="Normal").click()
    except:
        page.get_by_role("button", name="Bearbeiten").click()

    print("Clicked Edit Mode.")

    # Wait for edit buttons
    page.wait_for_selector("button[aria-label='Chart bearbeiten']")

    # Take screenshot
    page.screenshot(path="verification_screenshot.png")
    print("Screenshot saved to verification_screenshot.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
