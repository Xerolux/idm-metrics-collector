# SPDX-License-Identifier: MIT
import requests
from urllib.parse import urljoin

def _extract_share_link(resp, base_url, api_url):
    """Extract a share link from a MicroBin response."""
    resp.raise_for_status()

    data = None
    try:
        data = resp.json()
    except ValueError:
        data = None

    if isinstance(data, dict):
        direct_url = data.get("url")
        if direct_url:
            return direct_url
        paste_id = data.get("id") or data.get("paste_id")
        if paste_id:
            return f"{base_url.rstrip('/')}/{paste_id}"

    if resp.url and resp.url.rstrip("/") != api_url.rstrip("/") and resp.url.startswith(base_url.rstrip("/")):
        return resp.url

    location = resp.headers.get("Location") or resp.headers.get("location")
    if location:
        return urljoin(f"{base_url.rstrip('/')}/", location)

    return None

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
        base_url = url.rstrip("/")
        errors = []

        # MicroBin API endpoint (v2 JSON)
        api_url = f"{base_url}/api/v2/paste"

        # Payload for MicroBin
        payload = {
            "content": text,
            "title": "IDM Logger Protokoll",
            "expires": "1week",
            "privacy": "public"
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
            link = _extract_share_link(resp, base_url, api_url)
            if link:
                return link
            errors.append(f"MicroBin returned invalid response: {resp.text[:200]}")
        except Exception as exc:
            errors.append(str(exc))

        # Fallback to legacy API (form-encoded)
        api_url = f"{base_url}/api/paste"
        payload = {
            "content": text,
            "title": "IDM Logger Protokoll",
            "expiration": "1week",
            "visibility": "public"
        }

        headers = {
            "Accept": "application/json"
        }

        resp = requests.post(api_url, data=payload, headers=headers, timeout=10)
        link = _extract_share_link(resp, base_url, api_url)
        if link:
            return link
        raise Exception(f"MicroBin returned invalid response: {resp.text[:200]}")

    except Exception as e:
        message = str(e)
        if "errors" in locals() and errors:
            message = f"{message}; previous errors: {' | '.join(errors)}"
        raise Exception(f"Upload failed: {message}")
