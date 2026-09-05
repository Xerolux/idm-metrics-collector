# Xerolux 2026
from playwright.sync_api import sync_playwright, expect
import json


def verify_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Grant permissions for clipboard if needed, though not strictly required for this test
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Debugging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        page.on(
            "requestfailed",
            lambda req: print(f"REQUEST FAILED: {req.url} {req.failure}"),
        )

        # Mock API responses

        # 1. Auth Check - Authenticated
        page.route(
            "**/api/auth/check",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"authenticated": True, "must_change_password": False}),
            ),
        )

        # 2. Version
        page.route(
            "**/api/version",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"version": "verify-test"}),
            ),
        )

        # 3. Dashboard Configuration (The key part we changed)
        # providing the structure expected by the frontend
        dashboards_response = [
            {
                "id": "default",
                "name": "Standard Dashboard",
                "charts": [
                    {
                        "id": "temp_chart",
                        "title": "Temperaturen",
                        "queries": [
                            {
                                "label": "Außen",
                                "query": "temp_outside",
                                "color": "#3b82f6",
                            },
                            {
                                "label": "Vorlauf",
                                "query": "temp_supply",
                                "color": "#ef4444",
                            },
                        ],
                        "hours": 24,
                    },
                    {
                        "id": "power_chart",
                        "title": "Leistung",
                        "queries": [
                            {
                                "label": "Aktuell",
                                "query": "power_current",
                                "color": "#10b981",
                            }
                        ],
                        "hours": 24,
                    },
                ],
            }
        ]

        page.route(
            "**/api/dashboards",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(dashboards_response),
            ),
        )

        # 4. Mock Metrics Data (Query Range)
        # We need to return data so charts render
        def handle_query_range(route):
            # VictoriaMetrics response format
            response_data = {
                "status": "success",
                "data": {
                    "resultType": "matrix",
                    "result": [
                        {
                            "metric": {"__name__": "dummy_metric"},
                            "values": [
                                [1700000000, "10"],
                                [1700003600, "15"],
                                [1700007200, "12"],
                                [1700010800, "20"],
                            ],
                        }
                    ],
                },
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(response_data),
            )

        page.route("**/api/metrics/query_range*", handle_query_range)

        # 5. Mock Sensor Data (Available and Current values for sidebar)
        # The sidebar calls /api/metrics/available and /api/metrics/current

        page.route(
            "**/api/metrics/available",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "temperature": [
                            {"name": "temp_outside", "display": "Außentemperatur"},
                            {"name": "temp_supply", "display": "Vorlauftemperatur"},
                        ],
                        "power": [
                            {"name": "power_current", "display": "Aktuelle Leistung"}
                        ],
                    }
                ),
            ),
        )

        page.route(
            "**/api/metrics/current",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "temp_outside": {"value": 5.5, "timestamp": 1700000000},
                        "temp_supply": {"value": 45.2, "timestamp": 1700000000},
                        "power_current": {"value": 1200, "timestamp": 1700000000},
                    }
                ),
            ),
        )

        # Navigate to the app
        # Assuming pnpm dev is running on 5173
        try:
            page.goto("http://localhost:5173", timeout=60000)

            # Wait for dashboard to load
            expect(page.get_by_text("Standard Dashboard")).to_be_visible(timeout=20000)

            # Verify Charts are present - strict mode might fail if text appears multiple times (sidebar + chart)
            # We use .first to just ensure it's on the page
            expect(page.get_by_text("Temperaturen").first).to_be_visible()
            expect(page.get_by_text("Leistung").first).to_be_visible()

            # Verify Sidebar is present (Check for a category header or specific sensor)
            expect(page.get_by_text("Außentemperatur")).to_be_visible()

            # Verify New Controls (Time Range)
            # Check for "24 Stunden" (default value display)
            # It appears multiple times (Dropdown + Chart subtitles).
            expect(page.get_by_text("24 Stunden").first).to_be_visible()

            # Take a screenshot
            page.screenshot(path="verification_dashboard.png", full_page=True)
            print("Screenshot saved to verification_dashboard.png")

        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification_failure.png")
            raise e
        finally:
            browser.close()


if __name__ == "__main__":
    verify_dashboard()
