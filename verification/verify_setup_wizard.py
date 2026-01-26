import time
from playwright.sync_api import sync_playwright, expect


def test_setup_wizard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to http://localhost:5173/#/setup...")
        page.goto("http://localhost:5173/#/setup")

        # Wait for redirect or load
        time.sleep(2)

        print("Checking for Setup Wizard...")
        try:
            expect(page.get_by_text("Ersteinrichtung")).to_be_visible(timeout=10000)
            print("Setup Wizard visible.")
        except Exception as e:
            print(f"Setup Wizard not found. Current URL: {page.url}")
            page.screenshot(path="verification/error.png")
            raise e

        # Check for new fields
        expect(page.get_by_text("Modell", exact=True)).to_be_visible()

        # Interact with Dropdown
        print("Selecting Model...")
        # PrimeVue Dropdown usually renders the placeholder text if empty
        page.get_by_text("Maschine auswählen").click()
        page.get_by_text("AERO ALM 6-15").click()

        # Check Data Sharing
        expect(page.get_by_text("Community Daten")).to_be_visible()

        # Take Screenshot
        page.screenshot(path="verification/setup_wizard.png")
        print("Screenshot saved to verification/setup_wizard.png")

        browser.close()


if __name__ == "__main__":
    test_setup_wizard()
