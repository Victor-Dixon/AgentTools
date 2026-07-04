#!/usr/bin/env python3
"""Outbound Discord dry-run health check (no webhook secrets printed)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.outbound_dry_run import outbound_dry_run


def main() -> int:
    result = outbound_dry_run()
    print(result.message)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
