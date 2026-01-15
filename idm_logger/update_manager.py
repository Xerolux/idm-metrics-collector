import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

import requests

logger = logging.getLogger(__name__)

GITHUB_RELEASES_API = (
    "https://api.github.com/repos/Xerolux/idm-metrics-collector/releases/latest"
)


def get_current_version() -> str:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            cwd="/app",
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as exc:
        logger.debug(f"Git version lookup failed: {exc}")

    version_file = Path("/app/VERSION")
    if version_file.exists():
        return version_file.read_text().strip()

    return "unknown"


def _parse_version(version: str) -> Any:
    if not version:
        return None
    cleaned = version.lstrip("v")
    parts = cleaned.split(".")
    if len(parts) < 2:
        return None
    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2]) if len(parts) > 2 else 0
        return major, minor, patch
    except ValueError:
        return None


def get_update_type(current_version: str, latest_version: str) -> str:
    current = _parse_version(current_version)
    latest = _parse_version(latest_version)
    if not current or not latest:
        return "unknown"
    if latest[0] != current[0]:
        return "major"
    if latest[1] != current[1]:
        return "minor"
    if latest[2] != current[2]:
        return "patch"
    return "none"


def is_update_allowed(update_type: str, target: str) -> bool:
    if update_type in ("none", "unknown"):
        return False
    if target == "all":
        return True
    return update_type == target


def check_for_update() -> Dict[str, Any]:
    current_version = get_current_version()
    response = requests.get(GITHUB_RELEASES_API, timeout=10)
    response.raise_for_status()
    latest_release = response.json()
    latest_version = latest_release.get("tag_name", "")
    release_date = latest_release.get("published_at", "")
    release_notes = latest_release.get("body", "")[:200]
    update_available = (
        latest_version != current_version and latest_version > current_version
    )
    update_type = (
        get_update_type(current_version, latest_version) if update_available else "none"
    )

    return {
        "update_available": update_available,
        "update_type": update_type,
        "current_version": current_version,
        "latest_version": latest_version,
        "release_date": release_date,
        "release_notes": release_notes,
    }


def perform_update(repo_path: str = "/opt/idm-metrics-collector") -> None:
    # Check if we are in a git repository
    git_dir = Path(repo_path) / ".git"
    if not git_dir.exists():
        logger.error(
            f"Cannot update: {repo_path} is not a git repository (or .git is missing). This installation method does not support auto-update via git."
        )
        raise RuntimeError("Update fehlgeschlagen: Keine Git-Installation gefunden.")

    logger.info("Pulling latest changes from git...")
    result = subprocess.run(
        ["git", "pull", "origin", "main"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=repo_path,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Git pull failed: {result.stderr}")

    logger.info("Restarting Docker Compose stack...")
    compose_cmd = ["docker", "compose"]
    check_result = subprocess.run(
        compose_cmd + ["version"], capture_output=True, timeout=5
    )

    if check_result.returncode != 0:
        compose_cmd = ["docker-compose"]

    subprocess.run(
        compose_cmd + ["pull"], capture_output=True, timeout=300, cwd=repo_path
    )

    subprocess.run(
        compose_cmd + ["down"], capture_output=True, timeout=60, cwd=repo_path
    )

    subprocess.run(
        compose_cmd + ["up", "-d"], capture_output=True, timeout=120, cwd=repo_path
    )

    logger.info("Update completed successfully")


def can_run_updates(repo_path: str = "/opt/idm-metrics-collector") -> bool:
    return os.path.isdir(repo_path)
