import hashlib
import re
import time
from typing import Optional, Tuple
from ipaddress import ip_address


def mask_ip(ip: str) -> str:
    if not ip:
        return "0.0.0.0"
    if ":" in ip:
        return "xxxx:xxxx"
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.xxx.xxx"
    return "xxx.xxx.xxx.xxx"


def mask_id(id_str: str) -> str:
    if not id_str:
        return "unknown"
    if len(id_str) >= 8:
        return f"{id_str[:8]}..."
    return "xxx"


def validate_installation_id(installation_id: str) -> str:
    try:
        import uuid

        uuid.UUID(installation_id)
        return installation_id
    except ValueError:
        raise ValueError("Invalid installation ID format (must be UUID)")


def validate_model_name(model_name: Optional[str]) -> Optional[str]:
    if not model_name:
        return None
    if "\x00" in model_name:
        raise ValueError("Model name contains null bytes")
    if len(model_name) > 100:
        raise ValueError("Model name too long")
    if not re.match(r"^[a-zA-Z0-9_\-\. \(\)]+$", model_name):
        raise ValueError("Model name contains invalid characters")
    if ".." in model_name or "/" in model_name or "\\" in model_name:
        raise ValueError("Model name contains invalid characters")
    return model_name.replace(" ", "_")


def get_client_ip(request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
