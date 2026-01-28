# SPDX-License-Identifier: MIT
import requests

def upload(text, url="https://paste.blueml.eu"):
    """
    Upload text to MicroBin (simple API, no encryption).

    Args:
        text: Content to upload
        url: URL of the paste service

    Returns:
        Share link URL
    """
    try:
        # MicroBin API endpoint
        api_url = f"{url.rstrip('/')}/api/v2/paste"

        # Payload for MicroBin
        payload = {
            "content": text,
            "title": "IDM Logger Protokoll",
            "expires": "1week",
            "privacy": "public"
        }

        headers = {
            "Content-Type": "application/json"
        }

        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()

        try:
            data = resp.json()
        except ValueError:
            raise Exception(f"MicroBin returned invalid response: {resp.text[:200]}")

        # MicroBin returns paste ID
        paste_id = data.get("id") or data.get("paste_id")
        if paste_id:
            return f"{url.rstrip('/')}/{paste_id}"
        else:
            raise Exception(f"MicroBin Error: No paste ID returned")

    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")
