import time
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Route API calls to mock responses
    def handle_auth_check(route):
        route.fulfill(json={
            "authenticated": True,
            "must_change_password": True
        })

    def handle_config(route):
        # Handle password change
        if route.request.method == "POST":
            route.fulfill(json={"success": True})
        else:
            route.fulfill(json={"error": "Not mocked"})

    page.route("**/api/auth/check", handle_auth_check)
    page.route("**/api/config", handle_config)

    # Visit the app
    # Note: Vite uses /static/ base
    page.goto("http://localhost:5173/static/")

    # Since we mocked authenticated=True and must_change_password=True,
    # it should redirect to /change-password immediately or after auth check

    # Wait for the redirection or the component to load
    page.wait_for_url("**/change-password")

    # Verify we are on the correct page
    expect(page.get_by_text("Sicherheitswarnung")).to_be_visible()
    expect(page.get_by_text("Sie verwenden noch das Standardpasswort")).to_be_visible()

    # Take screenshot of the Force Password Change screen
    page.screenshot(path="/home/jules/verification/force_password_change.png")

    print("Screenshot saved to /home/jules/verification/force_password_change.png")

    # Test interaction
    page.get_by_label("Neues Passwort").fill("NewStrongPassword123!")
    page.get_by_label("Passwort bestätigen").fill("NewStrongPassword123!")

    # Mock the next auth check to return false for must_change_password
    def handle_auth_check_success(route):
        route.fulfill(json={
            "authenticated": True,
            "must_change_password": False
        })

    page.unroute("**/api/auth/check")
    page.route("**/api/auth/check", handle_auth_check_success)

    page.get_by_role("button", name="Passwort ändern").click()

    # Should redirect to Dashboard
    page.wait_for_url("**/static/")

    # Verify Dashboard
    expect(page.get_by_text("System Status")).to_be_visible() # Assuming dashboard has this text or similar

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
