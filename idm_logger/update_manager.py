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

# Docker images on GHCR
DOCKER_IMAGES = {
    "idm-logger": "ghcr.io/xerolux/idm-metrics-collector",
    "ml-service": "ghcr.io/xerolux/idm-metrics-collector-ml",
}

# Channels:
# - latest: rolling updates from main (version: 0.6.<hash>)
# - beta: pre-releases from GitHub (version: 0.6.x-betaX)
# - release: stable releases from GitHub (version: 0.6.x)


def get_repo_path() -> Optional[str]:
    """
    Determines the path to the git repository.
    Priority:
    1. REPO_PATH env var
    2. config.system.repo_path
    3. Current working directory (if .git exists)
    4. /app (if .git exists)
    5. Default /opt/idm-metrics-collector

    Returns None if no valid repo found.
    """
    # 1. Environment variable
    env_path = os.environ.get("REPO_PATH")
    if env_path:
        if (Path(env_path) / ".git").exists():
            return env_path
        logger.warning(f"REPO_PATH set but .git not found: {env_path}")

    # 2. Config
    conf_path = config.get("system.repo_path")
    if conf_path:
        if (Path(conf_path) / ".git").exists():
            return conf_path
        logger.warning(f"system.repo_path set but .git not found: {conf_path}")

    # 3. Current directory
    cwd = os.getcwd()
    if (Path(cwd) / ".git").exists():
        return cwd

    # 4. /app (common in Docker)
    if (Path("/app") / ".git").exists():
        return "/app"

    # 5. Default /opt/idm-metrics-collector
    default_path = "/opt/idm-metrics-collector"
    if (Path(default_path) / ".git").exists():
        return default_path

    # No repo found - return None (changed from returning invalid path)
    logger.debug("No git repository found - updates disabled")
    return None


def get_file_version() -> Optional[str]:
    """Reads the base version from VERSION file."""
    # Fallback to VERSION file (usually at /app/VERSION or repo_path/VERSION)
    version_file = Path("/app/VERSION")
    if not version_file.exists():
        repo_path = get_repo_path()
        if repo_path:
            version_file = Path(repo_path) / "VERSION"

    if version_file.exists():
        return version_file.read_text().strip()
    return None


def get_current_version() -> str:
    try:
        # Try to use the detected repo path for git describe
        repo_path = get_repo_path()
        if repo_path and (Path(repo_path) / ".git").exists():
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
    except Exception as exc:
        logger.debug(f"Git version lookup failed: {exc}")

    v = get_file_version()
    if v:
        return v

    return "unknown"


def get_local_image_id(image_name: str) -> Optional[str]:
    """Get the image ID of a locally running container's image."""
    try:
        # First try to get the image ID from running container
        result = subprocess.run(
            ["docker", "images", "--no-trunc", "-q", f"{image_name}:latest"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
    except Exception as e:
        logger.debug(f"Failed to get local image ID for {image_name}: {e}")
    return None


def get_remote_image_digest(image_name: str, tag: str = "latest") -> Optional[str]:
    """
    Get the digest of a remote image from GHCR using the registry API.
    Returns the manifest digest which can be compared to check for updates.
    """
    try:
        # Parse image name: ghcr.io/xerolux/idm-metrics-collector -> xerolux/idm-metrics-collector
        if image_name.startswith("ghcr.io/"):
            repo = image_name[8:]  # Remove "ghcr.io/"
        else:
            repo = image_name

        # GHCR uses token auth - get anonymous token first
        token_url = f"https://ghcr.io/token?scope=repository:{repo}:pull"
        token_resp = requests.get(token_url, timeout=10)
        if token_resp.status_code != 200:
            logger.debug(f"Failed to get GHCR token: {token_resp.status_code}")
            return None

        token = token_resp.json().get("token")
        if not token:
            return None

        # Get manifest digest
        manifest_url = f"https://ghcr.io/v2/{repo}/manifests/{tag}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json, "
            "application/vnd.oci.image.manifest.v1+json",
        }
        manifest_resp = requests.head(manifest_url, headers=headers, timeout=10)

        if manifest_resp.status_code == 200:
            digest = manifest_resp.headers.get("Docker-Content-Digest")
            return digest

    except Exception as e:
        logger.debug(f"Failed to get remote digest for {image_name}: {e}")
    return None


def get_local_image_digest(image_name: str) -> Optional[str]:
    """Get the RepoDigest of a local image (matches remote digest format)."""
    try:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{index .RepoDigests 0}}",
                f"{image_name}:latest",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Format: ghcr.io/xerolux/image@sha256:abc123
            full_digest = result.stdout.strip()
            if "@" in full_digest:
                return full_digest.split("@")[1]
    except Exception as e:
        logger.debug(f"Failed to get local digest for {image_name}: {e}")
    return None


def check_docker_updates() -> Dict[str, Any]:
    """
    Check if Docker image updates are available on GHCR.
    Returns status for each image and whether updates are available.
    """
    result = {
        "docker_available": False,
        "updates_available": False,
        "images": {},
    }

    # Check if docker is available
    try:
        docker_check = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            timeout=5,
        )
        result["docker_available"] = docker_check.returncode == 0
    except Exception:
        return result

    if not result["docker_available"]:
        return result

    for name, image in DOCKER_IMAGES.items():
        image_status = {
            "image": image,
            "local_digest": None,
            "remote_digest": None,
            "update_available": False,
            "error": None,
        }

        try:
            local_digest = get_local_image_digest(image)
            remote_digest = get_remote_image_digest(image)

            image_status["local_digest"] = local_digest[:16] if local_digest else None
            image_status["remote_digest"] = (
                remote_digest[:16] if remote_digest else None
            )

            if local_digest and remote_digest:
                if local_digest != remote_digest:
                    image_status["update_available"] = True
                    result["updates_available"] = True
            elif remote_digest and not local_digest:
                # Image not pulled yet or no digest info
                image_status["update_available"] = True
                result["updates_available"] = True

        except Exception as e:
            image_status["error"] = str(e)

        result["images"][name] = image_status

    return result


def can_run_docker_updates() -> bool:
    """Check if Docker-based updates can be performed."""
    try:
        # Check docker availability
        docker_check = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            timeout=5,
        )
        if docker_check.returncode != 0:
            return False

        # Check docker compose availability
        for cmd in [["docker", "compose", "version"], ["docker-compose", "version"]]:
            try:
                compose_check = subprocess.run(cmd, capture_output=True, timeout=5)
                if compose_check.returncode == 0:
                    return True
            except Exception:
                continue

        return False
    except Exception:
        return False


def perform_docker_update(compose_path: Optional[str] = None) -> None:
    """
    Perform a Docker-only update (pull new images and restart).
    Does not require git repository.
    """
    # Find compose file
    if compose_path is None:
        # Check common locations
        for path in [
            "/app/docker-compose.yml",
            "/opt/idm-metrics-collector/docker-compose.yml",
            os.path.join(os.getcwd(), "docker-compose.yml"),
        ]:
            if os.path.exists(path):
                compose_path = os.path.dirname(path) or "."
                break

        # Also check repo path if available
        repo_path = get_repo_path()
        if repo_path and os.path.exists(os.path.join(repo_path, "docker-compose.yml")):
            compose_path = repo_path

    if not compose_path:
        raise RuntimeError(
            "docker-compose.yml nicht gefunden. "
            "Bitte geben Sie den Pfad an oder führen Sie das Update "
            "im Verzeichnis mit docker-compose.yml aus."
        )

    logger.info(f"Performing Docker update in {compose_path}...")

    # Determine compose command
    compose_cmd = ["docker", "compose"]
    check_result = subprocess.run(
        compose_cmd + ["version"], capture_output=True, timeout=5
    )
    if check_result.returncode != 0:
        compose_cmd = ["docker-compose"]

    # Pull new images
    logger.info("Pulling latest Docker images...")
    pull_result = subprocess.run(
        compose_cmd + ["pull"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=compose_path,
    )
    if pull_result.returncode != 0:
        raise RuntimeError(f"Docker pull failed: {pull_result.stderr}")

    # Restart containers
    logger.info("Restarting containers...")
    subprocess.run(
        compose_cmd + ["down"], capture_output=True, timeout=60, cwd=compose_path
    )
    subprocess.run(
        compose_cmd + ["up", "-d"], capture_output=True, timeout=120, cwd=compose_path
    )

    logger.info("Docker update completed successfully")


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

        else:  # channel == 'latest' (formerly dev)
            # Checks against main branch

            git_worked = False
            if repo_path:
                try:
                    # Check git availability
                    subprocess.run(
                        ["git", "--version"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )

                    subprocess.run(
                        ["git", "fetch", "origin", "main"],
                        timeout=10,
                        cwd=repo_path,
                        capture_output=True,
                        check=True,
                    )
                    head = subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], cwd=repo_path, text=True
                    ).strip()
                    remote = subprocess.check_output(
                        ["git", "rev-parse", "origin/main"], cwd=repo_path, text=True
                    ).strip()

                    latest_version = f"dev-{remote[:7]}"
                    if head != remote:
                        update_available = True
                        release_notes = "Neue Version auf 'main' verfügbar"
                    else:
                        release_notes = "System ist aktuell (latest)"
                    git_worked = True
                except (
                    subprocess.CalledProcessError,
                    FileNotFoundError,
                    Exception,
                ) as e:
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

                    # Try to fetch authoritative base version from GitHub
                    # First try local VERSION file, then remote, then hardcoded fallback
                    base_ver = get_file_version() or "1.0.3"
                    try:
                        v_resp = requests.get(
                            f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/VERSION",
                            timeout=5,
                        )
                        if v_resp.status_code == 200:
                            base_ver = v_resp.text.strip()
                        else:
                            # Fallback to local
                            local_ver = get_file_version()
                            if local_ver:
                                base_ver = local_ver
                                # Strip hash if present (assuming max 3 parts for base: X.Y.Z)
                                parts = base_ver.split(".")
                                if len(parts) > 3:
                                    base_ver = ".".join(parts[:3])
                    except Exception:
                        local_ver = get_file_version()
                        if local_ver:
                            base_ver = local_ver
                            parts = base_ver.split(".")
                            if len(parts) > 3:
                                base_ver = ".".join(parts[:3])

                    latest_version = f"{base_ver}.{remote_hash[:7]}"

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

    # Also check Docker image updates
    docker_status = check_docker_updates()

    # Combine update availability
    any_update_available = update_available or docker_status.get(
        "updates_available", False
    )

    return {
        "update_available": any_update_available,
        "git_update_available": update_available,
        "update_type": update_type,
        "current_version": current_version,
        "latest_version": latest_version,
        "release_date": release_date,
        "release_notes": release_notes,
        "docker": docker_status,
    }


def perform_update(repo_path: Optional[str] = None, docker_only: bool = False) -> None:
    """
    Perform system update.

    Args:
        repo_path: Path to git repository (optional)
        docker_only: If True, only pull Docker images without git operations
    """
    # Use detected path if none provided, but prioritize argument if given
    if repo_path is None:
        repo_path = get_repo_path()

    # If no git repo and docker_only not explicitly set, try Docker-only update
    if not repo_path or docker_only:
        if can_run_docker_updates():
            logger.info("No git repository found - performing Docker-only update")
            perform_docker_update()
            return
        else:
            raise RuntimeError(
                "Update fehlgeschlagen: Weder Git-Repository noch Docker verfügbar."
            )

    git_dir = Path(repo_path) / ".git"
    if not git_dir.exists():
        # Try Docker-only update as fallback
        if can_run_docker_updates():
            logger.info(f"{repo_path} has no .git - performing Docker-only update")
            perform_docker_update(repo_path)
            return
        logger.error(f"Cannot update: {repo_path} is not a git repository.")
        raise RuntimeError(
            f"Update fehlgeschlagen: {repo_path} ist kein Git-Repository."
        )

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

    else:  # latest (main branch)
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

    if not repo_path:
        return False

    path_obj = Path(repo_path)
    if not path_obj.is_dir():
        return False

    # Check for .git directory to confirm it's a repo
    if not (path_obj / ".git").exists():
        return False

    return True
