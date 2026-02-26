from playwright.sync_api import sync_playwright


def verify_loading_states():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        # Grant permissions for clipboard if needed, though not used here
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        # Console logging
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        page.on("pageerror", lambda err: print(f"BROWSER ERROR: {err}"))

        try:
            print("Setting up mocks...")
            # Mock Authentication Check to bypass Login
            page.route(
                "**/api/auth/check",
                lambda route: route.fulfill(
                    status=200,
                    body='{"authenticated": true}',
                    headers={"Content-Type": "application/json"},
                ),
            )

            # Mock Config
            page.route(
                "**/api/config",
                lambda route: route.fulfill(
                    status=200,
                    body='{"hp_model": "test-model"}',
                    headers={"Content-Type": "application/json"},
                ),
            )

            # Mock Dashboards
            page.route(
                "**/api/dashboards",
                lambda route: route.fulfill(
                    status=200,
                    body='[{"id": "d1", "name": "Test Dashboard", "charts": []}]',
                    headers={"Content-Type": "application/json"},
                ),
            )

            # Mock Variables
            page.route(
                "**/api/variables",
                lambda route: route.fulfill(
                    status=200, body="[]", headers={"Content-Type": "application/json"}
                ),
            )

            # Mock Annotations (List)
            page.route(
                "**/api/annotations*",
                lambda route: route.fulfill(
                    status=200, body="[]", headers={"Content-Type": "application/json"}
                ),
            )

            # Mock Version
            page.route(
                "**/api/version",
                lambda route: route.fulfill(
                    status=200,
                    body='{"version": "1.0.0"}',
                    headers={"Content-Type": "application/json"},
                ),
            )

            # Mock Metrics
            page.route(
                "**/api/metrics/*",
                lambda route: route.fulfill(
                    status=200, body="{}", headers={"Content-Type": "application/json"}
                ),
            )

            print("Navigating...")
            page.goto("http://localhost:5173")
            page.wait_for_load_state("networkidle")

            page.screenshot(path="debug_initial_load.png")

            # --- Test 1: Add Chart Loading State ---
            print("Test 1: Add Chart Loading State")

            # Wait for the "Neuen Chart erstellen" button
            create_btn = page.locator('button[aria-label="Neuen Chart erstellen"]')
            if not create_btn.is_visible():
                # Fallback to text search if aria-label is missing (it shouldn't be, but primevue button uses label prop)
                create_btn = page.locator("button").filter(
                    has_text="Neuen Chart erstellen"
                )

            print("Waiting for Create Button...")
            create_btn.wait_for(state="visible", timeout=10000)

            print("Clicking Create Button...")
            create_btn.click(force=True)
            page.wait_for_timeout(500)  # Wait for animation

            page.screenshot(path="debug_after_click.png")

            # Wait for dialog
            print("Waiting for dialog...")
            page.wait_for_selector('div[role="dialog"]', state="visible", timeout=5000)

            # Fill details
            print("Filling details...")
            page.fill('input[placeholder="Chart-Titel"]', "Test Loading Chart")

            # Setup route holding for chart creation
            chart_route_holder = []

            def hold_chart_route(route):
                print("Intercepted chart creation request")
                chart_route_holder.append(route)

            page.route("**/api/dashboards/*/charts", hold_chart_route)

            # Click Add
            print("Clicking Add...")
            add_btn = page.locator('button[aria-label="Hinzufügen"]')
            if not add_btn.is_visible():
                add_btn = page.locator("button").filter(has_text="Hinzufügen")

            add_btn.click()

            # Check for loading state immediately
            print("Checking for loading state...")

            # We verify that the button has the loading class
            try:
                page.wait_for_function(
                    """
                    () => {
                        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Hinzufügen'));
                        return btn && (btn.classList.contains('p-button-loading') || btn.querySelector('.p-button-loading-icon'));
                    }
                """,
                    timeout=5000,
                )
                print("✅ Chart Add button entered loading state")
            except Exception as e:
                print("❌ Failed to detect loading state on Add button")
                page.screenshot(path="debug_failed_loading.png")
                # print class list
                classes = add_btn.get_attribute("class")
                print(f"Button classes: {classes}")
                raise e

            page.screenshot(path="verification_chart_loading.png")

            # Fulfill the request to let UI proceed
            if chart_route_holder:
                chart_route_holder[0].fulfill(
                    status=200,
                    body='{"id": "new-chart", "title": "Test Loading Chart", "type": "line", "queries": [], "hours": 24}',
                    headers={"Content-Type": "application/json"},
                )
            else:
                print("WARNING: No chart creation request intercepted!")

            page.wait_for_timeout(1000)  # Wait for dialog to close

            # --- Test 2: Annotation Loading State ---
            print("Test 2: Annotation Loading State")

            # Open Annotations dialog
            anno_btn = page.locator('button[aria-label="Annotations"]')
            if not anno_btn.is_visible():
                anno_btn = page.locator('button[title="Annotations"]')

            anno_btn.click()

            # Wait for Annotation List dialog
            print("Waiting for Annotation Dialog...")
            page.wait_for_selector('div[role="dialog"]', state="visible")

            # Find "Neu" button
            print("Clicking Neu...")
            # We need to be careful about which "Neu" button if multiple exist
            # Scoping to the visible dialog is safer
            dialog = page.locator('div[role="dialog"]')
            new_anno_btn = dialog.locator('button[aria-label="Neu"]')
            if not new_anno_btn.is_visible():
                new_anno_btn = dialog.locator("button").filter(has_text="Neu")

            new_anno_btn.click()

            # Wait for second dialog (or content update)
            page.wait_for_timeout(500)

            # Fill text
            print("Filling annotation...")
            page.fill("textarea", "Test Annotation Loading")

            # Hold route
            anno_route_holder = []

            def hold_anno_route(route):
                print("Intercepted annotation save request")
                anno_route_holder.append(route)

            page.route("**/api/annotations", hold_anno_route)

            # Click Save
            print("Clicking Save...")
            save_btn = page.locator("button").filter(has_text="Speichern").last
            save_btn.click()

            # Check loading
            print("Checking annotation loading state...")
            try:
                page.wait_for_function(
                    """
                    () => {
                        const btns = Array.from(document.querySelectorAll('button'));
                        const saveBtn = btns.find(b => b.textContent.includes('Speichern'));
                        return saveBtn && (saveBtn.classList.contains('p-button-loading') || saveBtn.querySelector('.p-button-loading-icon'));
                    }
                """,
                    timeout=5000,
                )
                print("✅ Annotation Save button entered loading state")
            except Exception as e:
                print("❌ Failed to detect loading state on Annotation Save button")
                raise e

            page.screenshot(path="verification_annotation_loading.png")

            # Fulfill
            if anno_route_holder:
                anno_route_holder[0].fulfill(
                    status=200,
                    body='{"id": "a1", "text": "Test Annotation Loading", "time": 1234567890}',
                    headers={"Content-Type": "application/json"},
                )

            print("ALL TESTS PASSED")

        except Exception as e:
            print(f"❌ Critical Error: {e}")
            page.screenshot(path="verification_error_final.png")
            raise e
        finally:
            browser.close()


if __name__ == "__main__":
    verify_loading_states()
