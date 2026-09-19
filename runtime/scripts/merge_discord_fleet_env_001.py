#!/usr/bin/env python3
"""Merge VPS discord-fleet.env into runtime/secrets/secrets.local.env (no stdout secrets)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "runtime" / "secrets"
FLEET = SECRETS / "discord-fleet.env"
LOCAL = SECRETS / "secrets.local.env"


def parse_env_lines(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r"^export\s+", "", s)
        if "=" not in s:
            continue
        key, val = s.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and "\n" not in val and "\r" not in val:
            out[key] = val
    return out


def protect_path(path: Path, *, is_dir: bool = False) -> None:
    """User-only NTFS ACL via icacls (no secret content touched)."""
    import os
    import subprocess

    if not path.exists():
        return
    user = os.environ.get("USERNAME") or ""
    if not user:
        return
    grant = f"{user}:(OI)(CI)M" if is_dir else f"{user}:F"
    subprocess.run(
        ["icacls", str(path), "/inheritance:r", "/grant:r", grant],
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    if not FLEET.is_file():
        print(f"MISSING={FLEET}", file=sys.stderr)
        return 1

    fleet_vars = parse_env_lines(FLEET.read_text(encoding="utf-8"))
    local_vars = parse_env_lines(LOCAL.read_text(encoding="utf-8")) if LOCAL.is_file() else {}

    merged = {**local_vars, **fleet_vars}

    lines = [
        "# Merged local secrets (gitignored). Never commit.",
        "# discord-fleet.env pulled from VPS ~/secrets/discord-fleet.env",
        "",
    ]
    for key in sorted(merged):
        val = merged[key]
        esc = val.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{esc}'")
    lines.append("")

    LOCAL.write_text("\n".join(lines), encoding="utf-8")

    protect_path(SECRETS, is_dir=True)
    protect_path(FLEET, is_dir=False)
    protect_path(LOCAL, is_dir=False)

    print("MERGE=OK")
    print(f"FLEET_KEYS={len(fleet_vars)}")
    print(f"TOTAL_KEYS={len(merged)}")
    print(f"LOCAL={LOCAL.resolve()}")
    print(f"FLEET_MIRROR={FLEET.resolve()}")
    print("KEYS=" + ",".join(sorted(fleet_vars.keys())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
