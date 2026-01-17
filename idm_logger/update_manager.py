# SPDX-License-Identifier: MIT
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import requests
from .config import config

logger = logging.getLogger(__name__)

GITHUB_REPO = "Xerolux/idm-metrics-collector"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"

# Channels:
# - latest: rolling updates from main (version: 0.6.<hash>)
# - beta: pre-releases from GitHub (version: 0.6.x-betaX)
# - release: stable releases from GitHub (version: 0.6.x)


def get_repo_path() -> str:
    """
    Determines the path to the git repository.
    Priority:
    1. REPO_PATH env var
    2. config.system.repo_path
    3. Current working directory (if .git exists)
    4. /app (if .git exists)
    5. Default /opt/idm-metrics-collector
    """
    # 1. Environment variable
    env_path = os.environ.get("REPO_PATH")
    if env_path:
        return env_path

    # 2. Config
    conf_path = config.get("system.repo_path")
    if conf_path:
        return conf_path

    # 3. Current directory
    cwd = os.getcwd()
    if (Path(cwd) / ".git").exists():
        return cwd

    # 4. /app (common in Docker)
    if (Path("/app") / ".git").exists():
        return "/app"

    # 5. Default
    return "/opt/idm-metrics-collector"


def get_current_version() -> str:
    try:
        # Try to use the detected repo path for git describe
        repo_path = get_repo_path()
        cwd_arg = repo_path if (Path(repo_path) / ".git").exists() else "/app"

        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            cwd=cwd_arg,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as exc:
        logger.debug(f"Git version lookup failed: {exc}")

    # Fallback to VERSION file (usually at /app/VERSION or repo_path/VERSION)
    version_file = Path("/app/VERSION")
    if not version_file.exists():
         version_file = Path(get_repo_path()) / "VERSION"

    if version_file.exists():
        return version_file.read_text().strip()

    return "unknown"


def _parse_version(version: str) -> Optional[Tuple[int, int, int, int, int]]:
    """
    Parses a version string into a tuple for comparison.
    Format: (major, minor, patch, release_type, pre_release_num)

    release_type:
    - 0: alpha/beta/rc (prerelease)
    - 1: stable (release)
    - 2: dev/latest (hash-based, treated as newest if local hash logic isn't used)

    However, we usually compare within channels.
    But to support 0.6.0 > 0.6.0-beta1:
    0.6.0 -> (0, 6, 0, 1, 0)
    0.6.0-beta1 -> (0, 6, 0, 0, 1)

    For hash versions (0.6.<hash>):
    We can't easily compare numerically against semantic versions without context.
    But for this function, we try to extract what we can.
    """
    if not version or version == "unknown":
        return None

    cleaned = version.lstrip("v")

    # Check for dev/hash version (e.g. 0.6.a1b2c3d)
    # Or beta version (e.g. 0.6.0-beta1)

    try:
        # Split by '-' to separate prerelease info
        parts = cleaned.split("-")
        main_part = parts[0]
        suffix = parts[1] if len(parts) > 1 else ""

        main_segments = main_part.split(".")
        major = int(main_segments[0])
        minor = int(main_segments[1]) if len(main_segments) > 1 else 0
        patch = 0

        # Check 3rd segment
        if len(main_segments) > 2:
            seg3 = main_segments[2]
            if seg3.isdigit():
                patch = int(seg3)
                is_hash = False
            else:
                # It's a hash, e.g. 0.6.a1b2c3d
                # Treat as patch 0, but mark as special?
                # Actually, our 'latest' channel uses 0.6.<hash>.
                # We can't compare hashes numerically.
                patch = 0
                is_hash = True
        else:
            is_hash = False

        if is_hash:
            # Hash versions are tricky. We usually rely on git/api to check 'latest' updates.
            # But for sorting, let's just say it's type 2 (dev)
            return (major, minor, patch, 2, 0)

        if suffix:
            # Handle beta/rc/alpha
            # e.g. beta1
            import re
            match = re.match(r"([a-zA-Z]+)(\d+)?", suffix)
            if match:
                # _type_str = match.group(1) # e.g. beta
                num = int(match.group(2)) if match.group(2) else 0
                return (major, minor, patch, 0, num)
            else:
                 # Unknown suffix
                 return (major, minor, patch, 0, 0)
        else:
            # Stable
            return (major, minor, patch, 1, 0)

    except (ValueError, IndexError):
        return None


def get_update_type(current_version: str, latest_version: str) -> str:
    # This is a rough estimation because strict semantic versioning isn't fully enforced
    current = _parse_version(current_version)
    latest = _parse_version(latest_version)

    if not current or not latest:
        return "unknown"

    # If major diff
    if latest[0] != current[0]:
        return "major"
    # If minor diff
    if latest[1] != current[1]:
        return "minor"
    # If patch diff
    if latest[2] != current[2]:
        return "patch"

    # If release type diff (beta vs stable) or prerelease num diff
    if latest[3:] != current[3:]:
         # Consider this a patch level update for simplicity
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
    # Default channel is now 'latest' (formerly dev)
    channel = config.get("updates.channel", "latest")

    # Also need repo path for git checks
    repo_path = get_repo_path()

    latest_version = ""
    release_date = ""
    release_notes = ""
    update_available = False

    try:
        if channel == "release":
            # Check for latest stable release
            url = f"{GITHUB_API_BASE}/releases/latest"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            latest_version = data.get("tag_name", "")
            release_date = data.get("published_at", "")
            release_notes = data.get("body", "")[:200]

            # Simple string comparison isn't enough (v0.6.0-beta vs v0.6.0)
            # But typically 'latest' endpoint only returns stable.
            if latest_version != current_version:
                 # Ensure we don't downgrade or reinstall same
                 # But parsing is hard. Let's assume if strings differ, it's an update
                 # unless current is 'newer'.
                 # Actually, if I am on 0.6.0-beta1 and latest is 0.6.0, I want update.
                 # If I am on 0.6.1 and latest is 0.6.0, I don't.

                 # Basic check:
                 curr_p = _parse_version(current_version)
                 lat_p = _parse_version(latest_version)

                 if lat_p and curr_p and lat_p > curr_p:
                     update_available = True

        elif channel == "beta":
            # Check for latest release (including prereleases)
            url = f"{GITHUB_API_BASE}/releases"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            releases = response.json()

            # Find the newest tag (releases are usually sorted by date desc)
            # We want the first one that is newer than current.
            # Or simply the first one in the list is the candidate.
            if releases:
                candidate = releases[0]
                latest_version = candidate.get("tag_name", "")
                release_date = candidate.get("published_at", "")
                release_notes = candidate.get("body", "")[:200]

                curr_p = _parse_version(current_version)
                lat_p = _parse_version(latest_version)

                if lat_p and curr_p and lat_p > curr_p:
                     update_available = True
                elif lat_p and not curr_p:
                    # If current is unknown, assume update
                    update_available = True

        else: # channel == 'latest' (formerly dev)
            # Checks against main branch

            git_worked = False
            try:
                # Check git availability
                subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                subprocess.run(["git", "fetch", "origin", "main"], timeout=10, cwd=repo_path, capture_output=True, check=True)
                head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path, text=True).strip()
                remote = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=repo_path, text=True).strip()

                latest_version = f"dev-{remote[:7]}"
                if head != remote:
                    update_available = True
                    release_notes = "Neue Version auf 'main' verfügbar"
                else:
                    release_notes = "System ist aktuell (latest)"
                git_worked = True
            except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
                logger.debug(f"Git check failed: {e}")

            if not git_worked:
                # Fallback to GitHub API for commits/main
                try:
                    # Parse current hash from version 0.6.<hash>
                    current_hash = None
                    parts = current_version.split(".")
                    if len(parts) >= 3:
                        current_hash = parts[-1]
                        if ".at" in current_hash:
                             current_hash = current_hash.split(".at")[-1]

                    resp = requests.get(f"{GITHUB_API_BASE}/commits/main", timeout=10)
                    resp.raise_for_status()
                    remote_data = resp.json()
                    remote_hash = remote_data["sha"]

                    latest_version = f"0.6.{remote_hash[:7]}"

                    if current_hash and not remote_hash.startswith(current_hash):
                        update_available = True
                        release_notes = f"Update: {remote_data.get('commit', {}).get('message', '').splitlines()[0]}"
                    elif not current_hash:
                         # Can't determine current hash, assume update if version looks wrong
                         update_available = True
                    else:
                        release_notes = "System ist aktuell (latest)"

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


def perform_update(repo_path: Optional[str] = None) -> None:
    # Use detected path if none provided, but prioritize argument if given
    if repo_path is None:
        repo_path = get_repo_path()

    git_dir = Path(repo_path) / ".git"
    if not git_dir.exists():
        logger.error(f"Cannot update: {repo_path} is not a git repository.")
        raise RuntimeError(f"Update fehlgeschlagen: {repo_path} ist kein Git-Repository.")

    channel = config.get("updates.channel", "latest")
    logger.info(f"Performing update (Channel: {channel}) in {repo_path}...")

    if channel in ["release", "beta"]:
        # Fetch tags
        try:
             # Logic is similar for beta and release: find the tag we want
             check_res = check_for_update()
             if not check_res.get("update_available"):
                 logger.info("No update available according to check.")
                 # Force pull anyway if user requested?
                 # But we need a target tag.
                 # If check_for_update fails or says no update, we might stick to current or latest available.
                 pass

             target_tag = check_res.get("latest_version")
             if not target_tag or target_tag == "unknown":
                 # Fallback: fetch tags and checkout based on logic again?
                 # Or just fail
                 raise RuntimeError("Konnte Ziel-Version nicht ermitteln.")

             logger.info(f"Fetching tags and checking out {target_tag}...")
             subprocess.run(["git", "fetch", "--tags"], check=True, cwd=repo_path)
             subprocess.run(["git", "checkout", target_tag], check=True, cwd=repo_path)

        except Exception as e:
            raise RuntimeError(f"Update failed: {e}")

    else: # latest (main branch)
        logger.info("Pulling latest changes from git (main)...")
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


def can_run_updates(repo_path: Optional[str] = None) -> bool:
    if repo_path is None:
        repo_path = get_repo_path()

    path_obj = Path(repo_path)
    if not path_obj.is_dir():
        return False

    # Check for .git directory to confirm it's a repo
    if not (path_obj / ".git").exists():
        return False

    return True
