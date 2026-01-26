from playwright.sync_api import sync_playwright, expect
import os


def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Mock API responses
    page.route(
        "/api/auth/check", lambda route: route.fulfill(json={"authenticated": True})
    )
    page.route(
        "/api/heatpumps",
        lambda route: route.fulfill(
            json=[
                {
                    "id": "hp-1",
                    "name": "Wärmepumpe 1",
                    "model": "navigator_2_0",
                    "connected": True,
                },
                {
                    "id": "hp-2",
                    "name": "Wärmepumpe 2",
                    "model": "navigator_2_0",
                    "connected": False,
                },
            ]
        ),
    )
    page.route(
        "/api/dashboards/heatpump/hp-1",
        lambda route: route.fulfill(
            json=[
                {
                    "id": "dash-1",
                    "name": "Übersicht HP1",
                    "heatpump_id": "hp-1",
                    "charts": [],
                }
            ]
        ),
    )
    page.route(
        "/api/dashboards",
        lambda route: route.fulfill(
            json=[
                {
                    "id": "dash-1",
                    "name": "Übersicht HP1",
                    "heatpump_id": "hp-1",
                    "charts": [],
                }
            ]
        ),
    )
    page.route(
        "/api/metrics/available",
        lambda route: route.fulfill(
            json={
                "temperature": [{"name": "temp_outdoor", "display": "Aussentemperatur"}]
            }
        ),
    )
    page.route("/api/variables", lambda route: route.fulfill(json=[]))
    page.route("/api/metrics/current", lambda route: route.fulfill(json={}))
    page.route("/api/data/hp-1", lambda route: route.fulfill(json={}))

    # Go to page
    page.goto("http://localhost:8081/#/")

    # Wait for loading
    page.wait_for_timeout(2000)

    # Check if selector exists and has text "Wärmepumpe 1"
    # The selector might display the selected value.
    # PrimeVue Select usually renders a span with p-select-label or similar.

    # We look for the heatpump selector. It's the first one in the top bar usually.
    # HeatpumpSelector.vue uses a Select with optionLabel="name".

    # Take screenshot
    if not os.path.exists("verification"):
        os.makedirs("verification")

    page.screenshot(path="verification/dashboard.png")

    # Basic assertions
    # Verify "Wärmepumpe 1" is visible (it should be selected by default)
    expect(page.get_by_text("Wärmepumpe 1")).to_be_visible()

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
