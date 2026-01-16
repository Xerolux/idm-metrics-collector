import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

import requests
from .config import config

logger = logging.getLogger(__name__)

GITHUB_RELEASES_API = (
    "https://api.github.com/repos/Xerolux/idm-metrics-collector/releases/latest"
)

# If configured channel is 'dev', we check against main branch via git
# If 'release', we check against GitHub Releases API


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
    # Handle version suffixes like .at<hash> by splitting them off
    # We only care about the major.minor.patch part for numerical comparison
    base_part = cleaned

    # If the version has more than 3 parts (major.minor.patch.suffix), keep only first 3
    # Or if one of the parts is not an integer, stop parsing there

    parts = base_part.split(".")

    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0

        # Handle patch version: check if it's an integer, otherwise treat as 0 or parse until non-digit
        patch = 0
        if len(parts) > 2:
            patch_str = parts[2]
            # If patch contains non-digits (like 'at073geu'), try to extract leading digits
            # But usually '0.6.at...' means patch is effectively 0 or the 'at' is the patch?
            # Assuming 'v0.6.at...' means Major 0, Minor 6, Patch 0 (or unknown) + Metadata
            # If the user follows v0.6.1.at... then patch is 1.
            # If the user uses v0.6.at... then parts[2] is 'at...' which is not an int.

            if patch_str.isdigit():
                patch = int(patch_str)
            else:
                # Try to extract leading digits if any, otherwise 0
                import re
                match = re.match(r'^(\d+)', patch_str)
                if match:
                    patch = int(match.group(1))
                else:
                    patch = 0

        return major, minor, patch
    except (ValueError, IndexError):
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
    channel = config.get("updates.channel", "dev")

    latest_version = ""
    release_date = ""
    release_notes = ""
    update_available = False

    try:
        if channel == "release":
            response = requests.get(GITHUB_RELEASES_API, timeout=10)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release.get("tag_name", "")
            release_date = latest_release.get("published_at", "")
            release_notes = latest_release.get("body", "")[:200]
            # Simple string comparison for now, assuming v0.6.1 > v0.6.0
            update_available = (latest_version != current_version and latest_version > current_version)

        else: # dev
            # For dev, we check if local is behind origin/main
            # This requires git fetch first

            git_worked = False
            try:
                # First check if git is available and we are in a git repo
                subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                subprocess.run(["git", "fetch", "origin", "main"], timeout=10, cwd="/app", capture_output=True, check=True)
                # Get hash of HEAD
                head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd="/app", text=True).strip()
                # Get hash of origin/main
                remote = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd="/app", text=True).strip()

                latest_version = f"dev-{remote[:7]}"
                if head != remote:
                    update_available = True
                    release_notes = "Neue Entwickler-Version verfügbar"
                else:
                    release_notes = "System ist auf dem neuesten Stand (Dev)"
                git_worked = True
            except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
                logger.debug(f"Git check failed, trying API fallback: {e}")

            if not git_worked:
                # Fallback to GitHub API for dev check
                try:
                    # Get local commit hash from version string
                    # Version format expected: v0.6.at<hash> or similar
                    current_hash = None
                    if ".at" in current_version:
                        current_hash = current_version.split(".at")[-1]

                    if current_hash:
                        # Fetch latest main commit from GitHub
                        resp = requests.get("https://api.github.com/repos/Xerolux/idm-metrics-collector/commits/main", timeout=10)
                        resp.raise_for_status()
                        remote_data = resp.json()
                        remote_hash = remote_data["sha"] # Full hash

                        # Compare (remote_hash starts with current_hash?)
                        # current_hash is likely short.
                        if not remote_hash.startswith(current_hash):
                            update_available = True
                            latest_version = f"dev-{remote_hash[:7]}"
                            release_notes = f"Neue Version verfügbar: {remote_data.get('commit', {}).get('message', '').splitlines()[0]}"
                        else:
                            latest_version = current_version
                            release_notes = "System ist auf dem neuesten Stand (Dev)"
                    else:
                        release_notes = "Version kann nicht geprüft werden (Kein Git, kein Hash in Version)"
                        latest_version = "unknown"

                except Exception as e:
                     logger.warning(f"API check failed: {e}")
                     latest_version = "unknown"

    except Exception as e:
        logger.error(f"Update check failed: {e}")
        return {"error": str(e)}

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

    channel = config.get("updates.channel", "dev")
    logger.info(f"Performing update (Channel: {channel})...")

    if channel == "release":
        # Get latest tag
        try:
             response = requests.get(GITHUB_RELEASES_API, timeout=10)
             response.raise_for_status()
             tag = response.json().get("tag_name")
             if not tag:
                 raise RuntimeError("Kein Release-Tag gefunden")

             logger.info(f"Fetching tags and checking out {tag}...")
             subprocess.run(["git", "fetch", "--tags"], check=True, cwd=repo_path)
             subprocess.run(["git", "checkout", tag], check=True, cwd=repo_path)
        except Exception as e:
            raise RuntimeError(f"Release update failed: {e}")

    else: # dev
        logger.info("Pulling latest changes from git (main)...")
        # Ensure we are on main
        subprocess.run(["git", "checkout", "main"], check=False, cwd=repo_path)
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
