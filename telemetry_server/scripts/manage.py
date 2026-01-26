import requests
import argparse
import sys
import os
import time
from datetime import datetime

# Can be run inside the container or locally if ports are forwarded
API_URL = "http://localhost:8000/api/v1"
# For CLI, we assume we are admin and can read the token from env or arg
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "change-me-to-something-secure")

def get_headers():
    return {"Authorization": f"Bearer {AUTH_TOKEN}"}

def show_status():
    """Show server status and stats."""
    try:
        response = requests.get(f"{API_URL}/status", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            print("=== Telemetry Server Status ===")
            print(f"Status: {data.get('status')}")
            print(f"Active Installations (30d): {data.get('active_installations_30d')}")
            print(f"Server Time: {datetime.fromtimestamp(data.get('timestamp', time.time()))}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

def check_training(model_file="model.pkl"):
    """Check model file status."""
    if os.path.exists(model_file):
        mod_time = datetime.fromtimestamp(os.path.getmtime(model_file))
        size = os.path.getsize(model_file) / 1024 # KB
        print(f"\n=== Model Status ===")
        print(f"File: {model_file}")
        print(f"Last Trained: {mod_time}")
        print(f"Size: {size:.2f} KB")
    else:
        print(f"\n=== Model Status ===")
        print(f"File: {model_file} not found (No training yet)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telemetry Server Management CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Status command
    subparsers.add_parser("status", help="Show server statistics")

    args = parser.parse_args()

    if args.command == "status":
        show_status()
        check_training()
    else:
        parser.print_help()
