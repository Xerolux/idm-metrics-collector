# Xerolux 2026
# SPDX-License-Identifier: MIT
import os
from playwright.sync_api import sync_playwright
from PIL import Image

# Required dependencies:
# pip install playwright pillow

# Configuration
SCREENSHOT_DIR = "docs/screenshots"
FINAL_GIF = "docs/images/demo.gif"
SCREENSHOT_SIZE = {"width": 1280, "height": 800}

# Mock Data
MOCK_CONFIG = {
    "idm": {"host": "192.168.1.10", "port": 502, "circuits": ["A"], "zones": [1]},
    "web": {"write_enabled": True},
    "metrics": {"url": "http://victoriametrics:8428/write"},
    "mqtt": {
        "enabled": True,
        "broker": "mqtt.example.com",
        "port": 1883,
        "username": "user",
        "password": "mysecretpassword",
        "topic_prefix": "idm",
    },
    "signal": {
        "enabled": False,
        "sender": "+49123456789",
        "recipients": ["+49987654321"],
    },
    "network_security": {
        "enabled": True,
        "whitelist": ["192.168.1.0/24"],
        "blacklist": [],
    },
    "setup_completed": True,
}

MOCK_DATA = {
    "outside_temp": 12.5,
    "flow_temp": 35.0,
    "return_temp": 30.0,
    "hot_water_temp": 48.0,
    "buffer_temp": 40.0,
    "heat_source_temp": 8.0,
    "cold_source_temp": 4.0,
    "power_consumption": 1200,
    "heat_production": 4500,
    "cop": 3.75,
    "operating_mode_str": "Heizen",
    "status_code": 0,
    "error_code": 0,
}

MOCK_LOGS = [
    {"timestamp": "2023-10-27 10:00:00", "level": "INFO", "message": "System started"},
    {
        "timestamp": "2023-10-27 10:05:00",
        "level": "INFO",
        "message": "Connected to Modbus",
    },
    {
        "timestamp": "2023-10-27 10:10:00",
        "level": "WARNING",
        "message": "High pressure warning (simulated)",
    },
]

MOCK_ALERTS = [
    {
        "id": "1",
        "name": "High Temp",
        "type": "threshold",
        "sensor": "flow_temp",
        "threshold": 50,
        "operator": ">",
        "enabled": True,
    },
    {"id": "2", "name": "Error Status", "type": "status", "enabled": True},
]

MOCK_TECHNICIAN_CODE = {"level_1": "1234", "level_2": "56789"}


def mock_api_routes(page):
    # Auth
    page.route(
        "**/api/auth/check", lambda route: route.fulfill(json={"authenticated": True})
    )
    page.route("**/api/auth/login", lambda route: route.fulfill(json={"success": True}))
    page.route("**/api/version", lambda route: route.fulfill(json={"version": "0.6.0"}))

    # Data
    page.route("**/api/data", lambda route: route.fulfill(json=MOCK_DATA))
    page.route("**/api/config", lambda route: route.fulfill(json=MOCK_CONFIG))
    page.route("**/api/logs", lambda route: route.fulfill(json=MOCK_LOGS))
    page.route("**/api/alerts", lambda route: route.fulfill(json=MOCK_ALERTS))
    page.route("**/api/alerts/templates", lambda route: route.fulfill(json=[]))
    page.route(
        "**/api/tools/technician-code*",
        lambda route: route.fulfill(json=MOCK_TECHNICIAN_CODE),
    )
    page.route("**/api/backup/list", lambda route: route.fulfill(json={"backups": []}))

    # Control/Schedule
    page.route(
        "**/api/control",
        lambda route: route.fulfill(
            json=[
                {
                    "name": "operating_mode",
                    "description": "Operating Mode",
                    "enum": [{"name": "Off", "value": 0}, {"name": "Heat", "value": 1}],
                    "features": "WRITE",
                    "unit": "",
                },
                {
                    "name": "target_temp",
                    "description": "Target Temp",
                    "min": 10,
                    "max": 30,
                    "features": "WRITE",
                    "unit": "°C",
                },
            ]
        ),
    )
    page.route(
        "**/api/schedule", lambda route: route.fulfill(json={"jobs": [], "sensors": []})
    )

    # Status
    page.route(
        "**/api/status",
        lambda route: route.fulfill(
            json={
                "status": "running",
                "setup_completed": True,
                "modbus_connected": True,
                "scheduler_running": True,
                "mqtt": {"connected": True},
                "metrics": {"connected": True},
            }
        ),
    )

    page.route(
        "**/api/signal/status",
        lambda route: route.fulfill(
            json={
                "enabled": False,
                "sender_set": False,
                "recipients_count": 0,
                "cli_path": "signal-cli",
                "cli_available": False,
            }
        ),
    )

    page.route(
        "**/api/check-update",
        lambda route: route.fulfill(
            json={
                "current_version": "v0.6.0",
                "latest_version": "v0.6.1",
                "update_available": True,
            }
        ),
    )


def inject_blur_css(page):
    # Inject CSS to blur specific sensitive elements
    css = """
    /* Passwords in config inputs */
    input[type="password"] {
        filter: blur(5px) !important;
        color: transparent !important;
    }

    /* Technician Codes */
    .font-mono.tracking-widest {
        filter: blur(8px) !important;
    }
    """
    page.add_style_tag(content=css)


def run():
    if os.path.exists(SCREENSHOT_DIR):
        # We don't want to delete the dir if it exists, just overwrite files
        pass
    else:
        os.makedirs(SCREENSHOT_DIR)

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        # Device scale factor 2 for "really good quality"
        context = browser.new_context(viewport=SCREENSHOT_SIZE, device_scale_factor=2)
        page = context.new_page()

        # Setup Mocking
        mock_api_routes(page)

        # Base URL - assuming vite is running on 5173
        base_url = "http://localhost:5173"

        # List of pages to capture
        pages = [
            {"path": "/#/login", "name": "01_login"},
            {"path": "/#/", "name": "02_dashboard"},
            {"path": "/#/control", "name": "03_control"},
            {"path": "/#/schedule", "name": "04_schedule"},
            {"path": "/#/alerts", "name": "05_alerts"},
            {"path": "/#/config", "name": "06_config"},
            {"path": "/#/logs", "name": "07_logs"},
            {"path": "/#/tools", "name": "08_tools"},
            {"path": "/#/about", "name": "09_about"},
        ]

        # First, go to dashboard to "hydrate" the store
        page.goto(f"{base_url}/#/")
        page.wait_for_timeout(2000)  # Wait for load

        # Iterate and capture
        for item in pages:
            print(f"Capturing {item['name']}...")

            if item["name"] == "01_login":
                # Temporarily unroute auth check or return false
                page.unroute("**/api/auth/check")
                page.route(
                    "**/api/auth/check",
                    lambda route: route.fulfill(json={"authenticated": False}),
                )
                page.goto(f"{base_url}{item['path']}")
            else:
                # Restore auth
                page.unroute("**/api/auth/check")
                page.route(
                    "**/api/auth/check",
                    lambda route: route.fulfill(json={"authenticated": True}),
                )
                page.goto(f"{base_url}{item['path']}")

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)  # Extra wait for animations

            # Inject CSS for blurring
            inject_blur_css(page)

            page.screenshot(path=f"{SCREENSHOT_DIR}/{item['name']}.png")

        browser.close()

    print("Screenshots captured.")

    # Create GIF
    create_gif()


def create_gif():
    images = []
    file_names = sorted(os.listdir(SCREENSHOT_DIR))

    for filename in file_names:
        if filename.endswith(".png"):
            file_path = os.path.join(SCREENSHOT_DIR, filename)
            # Read image
            img = Image.open(file_path)
            # Resize for GIF to reduce size but keep quality reasonable
            img.thumbnail((1280, 800), Image.Resampling.LANCZOS)
            images.append(img)

    # Save GIF
    print(f"Creating GIF at {FINAL_GIF}...")
    if not os.path.exists(os.path.dirname(FINAL_GIF)):
        os.makedirs(os.path.dirname(FINAL_GIF))

    # duration in ms. 2 seconds per slide.
    images[0].save(
        FINAL_GIF, save_all=True, append_images=images[1:], duration=2000, loop=0
    )
    print("GIF created.")


if __name__ == "__main__":
    run()
