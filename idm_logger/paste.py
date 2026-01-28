# SPDX-License-Identifier: MIT
import requests
from urllib.parse import urljoin


def upload(text, url="https://paste.blueml.eu"):
    """
    Upload text to MicroBin using the web form endpoint.

    Args:
        text: Content to upload
        url: URL of the paste service

    Returns:
        Share link URL
    """
    base_url = url.rstrip("/")
    upload_url = f"{base_url}/upload"

    # MicroBin form data - use files parameter to force multipart/form-data encoding
    # Each field is a tuple of (filename, value) where filename=None for text fields
    form_fields = {
        "content": (None, text),
        "expiration": (None, "1week"),
        "privacy": (None, "unlisted"),
        "burn_after": (None, "0"),
        "syntax_highlight": (None, ""),
        "encrypt_client": (None, ""),
        "random_key": (None, ""),
        "plain_key": (None, ""),
    }

    try:
        # POST to /upload endpoint - MicroBin returns 302 redirect to the paste URL
        resp = requests.post(
            upload_url,
            files=form_fields,
            timeout=15,
            allow_redirects=False,
        )

        # MicroBin returns 302 redirect with Location header containing the paste URL
        if resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get("Location") or resp.headers.get("location")
            if location:
                # Convert relative URL to absolute if needed
                return urljoin(f"{base_url}/", location)

        # If we followed redirects or got 200, check the final URL
        if resp.status_code == 200 and resp.url and resp.url != upload_url:
            return resp.url

        resp.raise_for_status()
        raise Exception(
            f"MicroBin returned unexpected response (status {resp.status_code})"
        )

    except requests.RequestException as e:
        raise Exception(f"Upload failed: {e}") from e
