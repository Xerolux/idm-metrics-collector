#!/usr/bin/env python3
"""Fail CI if production hardening invariants are violated."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
TELEMETRY_DIR = ROOT / "telemetry_server"


def fail(msg: str) -> None:
    print(f"[SECURITY CHECK] FAIL: {msg}")
    sys.exit(1)


def require(condition: bool, msg: str) -> None:
    if not condition:
        fail(msg)


def main() -> int:
    compose = (TELEMETRY_DIR / "docker-compose.yml").read_text(encoding="utf-8")
    env_example = (TELEMETRY_DIR / ".env.production.example").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    # 1) No hardcoded auth token in compose
    require(
        "AUTH_TOKEN=COMMUNITY-CONTRIBUTOR-TOKEN-2026" not in compose,
        "docker-compose.yml still contains hardcoded AUTH_TOKEN",
    )
    require(
        "AUTH_TOKEN=${AUTH_TOKEN:-}" in compose,
        "docker-compose.yml must source AUTH_TOKEN from env",
    )
    require(
        "ADMIN_AUTH_TOKEN=${ADMIN_AUTH_TOKEN:-}" in compose,
        "docker-compose.yml must source ADMIN_AUTH_TOKEN from env",
    )

    # 2) Strict admin auth enabled by default in production template
    require(
        re.search(r"^STRICT_ADMIN_AUTH=true$", env_example, re.MULTILINE) is not None,
        ".env.production.example must set STRICT_ADMIN_AUTH=true",
    )

    # 3) Ensure env files are ignored
    require(".env.*" in gitignore, ".gitignore must ignore .env.*")
    require("telemetry_server/.env" in gitignore, ".gitignore must ignore telemetry_server/.env")

    print("[SECURITY CHECK] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
