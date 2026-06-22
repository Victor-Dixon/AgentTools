#!/usr/bin/env python3
"""Deprecated shim — use `python -m tools.toolbelt` onboarding flags instead."""

from __future__ import annotations

import subprocess
import sys

_LEGACY_TO_TOOLBELT = {
    "onboard:soft": ["--onboard-soft"],
    "onboard:status": ["--onboard-status"],
    "onboard:hard": ["--onboard-hard"],
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print("Deprecated: use python -m tools.toolbelt onboarding flags instead.")
        print("  python -m tools.toolbelt --onboard-soft --agent Agent-5")
        print("  python -m tools.toolbelt --onboard-status --agent Agent-5")
        print("  python -m tools.toolbelt --onboard-hard --agent Agent-5 --yes")
        return 0 if argv and argv[0] in {"-h", "--help", "help"} else 2

    mapped = _LEGACY_TO_TOOLBELT.get(argv[0])
    if not mapped:
        print(f"Unknown command '{argv[0]}'. Use python -m tools.toolbelt --help", file=sys.stderr)
        return 2

    cmd = [sys.executable, "-m", "tools.toolbelt", *mapped, *argv[1:]]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
