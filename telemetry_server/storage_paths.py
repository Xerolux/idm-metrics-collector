"""Utilities for resilient storage directory handling."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def _probe_writable(path: Path) -> bool:
    """Return True if directory can be created and written to."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        with open(probe, "a", encoding="utf-8"):
            pass
        try:
            probe.unlink()
        except Exception:
            # Probe cleanup failure should not mark directory unusable.
            pass
        return True
    except Exception:
        return False


def resolve_storage_dir(env_var: str, default_dir: str, purpose: str) -> Path:
    """
    Resolve a writable directory for persistent-ish storage.

    Priority:
    1. explicit env path (if set)
    2. provided default path
    3. workspace fallback: ./telemetry_data/<purpose>
    4. temp fallback: /tmp/telemetry/<purpose>
    """
    configured = os.environ.get(env_var, "").strip()
    preferred = Path(configured) if configured else Path(default_dir)

    candidates: List[Path] = [preferred]
    candidates.append(Path(tempfile.gettempdir()) / "telemetry" / purpose)
    candidates.append(Path.cwd() / "telemetry_data" / purpose)

    seen = set()
    for candidate in candidates:
        normalized = str(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)

        if _probe_writable(candidate):
            if candidate != preferred:
                logger.warning(
                    "storage_path_fallback",
                    extra={
                        "env_var": env_var,
                        "preferred": str(preferred),
                        "fallback": str(candidate),
                        "purpose": purpose,
                    },
                )
            return candidate

    # Last resort: return preferred path and let caller fail gracefully on write.
    logger.error(
        "storage_path_unwritable",
        extra={"env_var": env_var, "path": str(preferred), "purpose": purpose},
    )
    return preferred
