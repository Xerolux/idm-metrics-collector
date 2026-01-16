from playwright.sync_api import sync_playwright, expect

def test_about_page_content(page):
    # Navigate to the About page
    # It seems the vite server is serving at /static/
    page.goto("http://localhost:3000/static/#/about")

    # Wait for the content to load
    page.wait_for_load_state("networkidle")

    # Check for the new title "Hauptfunktionen"
    expect(page.get_by_role("heading", name="Hauptfunktionen")).to_be_visible()

    # Check for the new list items
    expect(page.get_by_text("AI Anomalie-Erkennung (Echtzeit-Überwachung mit River)")).to_be_visible()
    expect(page.get_by_text("Techniker-Tools (Code Generator)")).to_be_visible()

    # Check for "River (Online ML)" in Powered By section
    expect(page.get_by_text("River (Online ML)")).to_be_visible()

    # Take a screenshot
    page.screenshot(path="/home/jules/verification/about_page.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_about_page_content(page)
            print("Verification script finished successfully.")
        except Exception as e:
            print(f"Verification script failed: {e}")
            page.screenshot(path="/home/jules/verification/failure.png")
        finally:
            browser.close()
