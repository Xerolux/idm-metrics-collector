from playwright.sync_api import sync_playwright, expect
import time


def test_consent_text():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # We need to simulate the Setup page
        print("Navigating to http://localhost:5173/#/setup...")
        page.goto("http://localhost:5173/#/setup")

        time.sleep(2)

        # Look for the new consent text
        print("Checking for consent text...")
        # Search for a fragment of the text
        try:
            expect(page.get_by_text("Eigentum des Tool-Betreibers")).to_be_visible()
            expect(page.get_by_text("kommerziell")).to_be_visible()
            print("Consent text found.")
        except Exception as e:
            page.screenshot(path="verification/consent_fail.png")
            raise e

        page.screenshot(path="verification/setup_consent.png")
        print("Screenshot saved to verification/setup_consent.png")
        browser.close()


if __name__ == "__main__":
    test_consent_text()
