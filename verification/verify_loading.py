from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    page = context.new_page()

    # Mock API
    page.route("**/api/auth/check", lambda route: route.fulfill(json={"authenticated": True}))
    page.route("**/api/config", lambda route: route.fulfill(json={"hp_model": "TestModel", "telemetry": {"enabled": False}, "ai": {"enabled": False}}))
    page.route("**/api/variables", lambda route: route.fulfill(json=[]))
    page.route("**/api/annotations**", lambda route: route.fulfill(json=[]))

    # Mock Dashboards
    dashboard = {
        "id": "dash1",
        "name": "Test Dashboard",
        "charts": [
            {
                "id": "chart1",
                "title": "Loading Chart",
                "type": "line",
                "queries": [{"query": "temp_outdoor", "label": "Outdoor Temp", "color": "#f00"}],
                "hours": 12
            },
            {
                "id": "chart2",
                "title": "No Data Chart",
                "type": "line",
                "queries": [], # No queries -> No Data immediately
                "hours": 12
            }
        ]
    }
    page.route("**/api/dashboards", lambda route: route.fulfill(json=[dashboard]))
    page.route("**/api/dashboards/dash1", lambda route: route.fulfill(json=dashboard))

    # Mock Metrics - Delay response to capture Loading state
    def handle_metrics(route):
        # Allow Chart 2 (No Data) to render immediately (it doesn't fetch because queries is empty)
        # Chart 1 fetches.
        # We simulate delay.
        time.sleep(2)
        route.fulfill(json={"status": "success", "data": {"result": []}})

    page.route("**/api/metrics/query_range**", handle_metrics)

    print("Navigating...")
    page.goto("http://localhost:5173/")

    print("Waiting for dashboard...")
    # Wait for the dashboard dropdown to appear
    page.wait_for_selector(".p-select", state="visible")

    # Allow some time for components to mount and start fetching
    time.sleep(0.5)

    print("Taking screenshot of LOADING state...")
    # Take screenshot of loading state
    # Chart 1 should show the spinner. Chart 2 should show No Data (or empty instructions).
    page.screenshot(path="verification/loading_state.png")

    # Wait for loading to finish (metrics handler sleeps 2s)
    print("Waiting for data load...")
    time.sleep(3)

    print("Taking screenshot of NO DATA state...")
    # Take screenshot of No Data state
    # Chart 1 returned empty list, so it should now show "No Data" or "Keine Daten".
    page.screenshot(path="verification/no_data_state.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
