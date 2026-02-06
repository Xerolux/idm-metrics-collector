from playwright.sync_api import sync_playwright, expect
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to Login page
        # Note: server serves from root but base is /static/
        url = "http://localhost:5173/static/#/login"
        print(f"Navigating to {url}")
        page.goto(url)

        # Wait for password input
        # It has id="password"
        password_input = page.locator("#password")
        expect(password_input).to_be_visible()

        # Type a password
        password_input.fill("secret123")

        # Check initial type is password
        expect(password_input).to_have_attribute("type", "password")

        # Find the toggle button
        # It should be next to the input. We can find it by aria-label "Passwort anzeigen"
        toggle_btn = page.get_by_label("Passwort anzeigen")
        expect(toggle_btn).to_be_visible()

        # Take screenshot before toggle
        page.screenshot(path="verification/login_before_toggle.png")
        print("Screenshot taken: login_before_toggle.png")

        # Click the toggle
        toggle_btn.click()

        # Verify type changed to text
        expect(password_input).to_have_attribute("type", "text")

        # Verify label changed
        toggle_btn_hidden = page.get_by_label("Passwort verbergen")
        expect(toggle_btn_hidden).to_be_visible()

        # Take screenshot after toggle
        page.screenshot(path="verification/login_after_toggle.png")
        print("Screenshot taken: login_after_toggle.png")

        browser.close()

if __name__ == "__main__":
    run()
