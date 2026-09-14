# Xerolux 2026
from playwright.sync_api import sync_playwright, expect
import json
import time


def verify_ux_labels():
    print("Starting verification of UX labels...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Context with permissions for clipboard if needed
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        # Debugging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        # --- MOCK API RESPONSES ---

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
                body=json.dumps({"version": "ux-test"}),
            ),
        )

        # 3. Dashboards
        dashboards_response = [
            {
                "id": "default",
                "name": "UX Test Dashboard",
                "charts": [],
                "customCss": "",
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

        # 4. Variables (needed for Variable Selector/Dialog)
        variables_response = [
            {
                "id": "var1",
                "name": "Test Variable",
                "type": "custom",
                "multi": False,
                "values": [{"label": "A", "value": "a"}, {"label": "B", "value": "b"}],
                "default": "a",
            }
        ]
        page.route(
            "**/api/variables",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(variables_response),
            ),
        )
        # Mock variable values endpoint
        page.route(
            "**/api/variables/*",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(variables_response[0]),
            ),
        )

        # 5. Annotations/Anomalies (for Bell icon)
        # To test the bell icon, we need unacknowledged anomalies
        anomalies_response = [
            {
                "id": "ano1",
                "text": "Something went wrong",
                "time": 1700000000,
                "tags": ["anomaly"],
                "acknowledged": False,
            }
        ]
        page.route(
            "**/api/annotations",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(anomalies_response),
            ),
        )

        # 6. Metrics (Empty for now as we don't test charts)
        page.route(
            "**/api/metrics/*",
            lambda route: route.fulfill(status=200, body=json.dumps({})),
        )

        # --- NAVIGATION ---

        # Note: Using /static/ base path as configured in vite.config.js
        url = "http://localhost:5173/static/"
        print(f"Navigating to {url}")
        try:
            page.goto(url, timeout=30000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            # Try root just in case
            page.goto("http://localhost:5173/", timeout=30000)

        # Wait for dashboard to load
        try:
            expect(page.get_by_text("UX Test Dashboard")).to_be_visible(timeout=10000)
            print("Dashboard loaded successfully.")
        except Exception as e:
            print("Dashboard failed to load.")
            page.screenshot(path="dashboard_load_fail.png")
            raise e

        # Handle auto-opened Alarm Dialog
        # It opens because we mocked anomalies
        try:
            # PrimeVue 4 Dialog close button
            # It might have a specific class or aria-label
            close_btn = page.locator(".p-dialog-header-actions button")
            if close_btn.count() > 0 and close_btn.is_visible():
                print("Closing auto-opened Alarm Dialog...")
                close_btn.click()
                time.sleep(0.5)  # Wait for animation
        except Exception as e:
            print(f"Error handling alarm dialog: {e}")

        # --- VERIFICATION ---

        failures = []

        def check_button(title_or_desc, locator_strategy, expected_label=None):
            print(f"Checking button: {title_or_desc}")
            try:
                # Find button
                btn = locator_strategy
                expect(btn).to_be_visible(timeout=2000)

                # Check aria-label
                aria_label = btn.get_attribute("aria-label")
                if not aria_label:
                    print(f"  FAILED: Missing aria-label for '{title_or_desc}'")
                    failures.append(f"Missing aria-label: {title_or_desc}")
                else:
                    print(f"  SUCCESS: Found aria-label='{aria_label}'")
                    if expected_label and aria_label != expected_label:
                        print(
                            f"  WARNING: Expected '{expected_label}', got '{aria_label}'"
                        )
            except Exception as e:
                print(f"  ERROR: Could not find/check button '{title_or_desc}': {e}")
                failures.append(f"Button not found/visible: {title_or_desc}")

        # 1. New Dashboard (Plus icon)
        check_button(
            "New Dashboard",
            page.locator('button[title="Neues Dashboard"]'),
            "Neues Dashboard",
        )

        # 2. Template (Copy icon)
        check_button(
            "Template",
            page.locator('button[title="Aus Vorlage erstellen"]'),
            "Aus Vorlage erstellen",
        )

        # 3. Settings (Cog icon)
        check_button(
            "Settings",
            page.locator('button[title="Dashboard Einstellungen"]'),
            "Dashboard Einstellungen",
        )

        # 4. Delete (Trash icon)
        # Note: might be disabled if only 1 dashboard, but still should have label
        check_button(
            "Delete Dashboard",
            page.locator('button[title="Dashboard löschen"]'),
            "Dashboard löschen",
        )

        # 5. Warnings (Bell icon)
        # Should be visible because we mocked anomalies
        check_button(
            "Warnings",
            page.locator('button[title="Aktive Warnungen"]'),
            "Aktive Warnungen",
        )

        # 6. Export (Download icon)
        check_button(
            "Export", page.locator('button[title="Exportieren"]'), "Exportieren"
        )

        # 7. Annotations (Bookmark icon)
        check_button(
            "Annotations", page.locator('button[title="Annotations"]'), "Annotations"
        )

        # 8. Variables (Sliders icon)
        check_button(
            "Variables", page.locator('button[title="Variables"]'), "Variables"
        )

        # 9. Test Dialog Buttons (Variable Dialog)
        # Open Variables Dialog first
        print("Opening Variables Dialog...")
        page.locator('button[title="Variables"]').click()

        # Wait for dialog content
        try:
            # Scope to dialog
            dialog = page.locator(".p-dialog")
            expect(dialog).to_be_visible()

            # Check Edit Variable button (Pencil)
            # Find the button inside the dialog
            edit_btn_row = dialog.locator("button:has(.pi-pencil)")
            check_button("Edit Variable (Row)", edit_btn_row, "Variable bearbeiten")

            delete_btn_row = dialog.locator("button.p-button-danger:has(.pi-times)")
            check_button("Delete Variable", delete_btn_row, "Variable löschen")

        except Exception as e:
            print(f"Failed to check dialog buttons: {e}")
            failures.append("Dialog interaction failed")

        if failures:
            print("\nVerification FAILED. The following issues were found:")
            for f in failures:
                print(f"- {f}")
            page.screenshot(path="verification_failures.png")
            exit(1)
        else:
            print("\nVerification PASSED! All buttons have accessible labels.")
            page.screenshot(path="verification_success.png")
            exit(0)


if __name__ == "__main__":
    verify_ux_labels()
