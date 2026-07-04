#!/usr/bin/env python3
"""Inbound Discord dry-run health check.

Adapted from Agent_Cellphone_V2_Repository/scripts/health/discord_dry_run.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.inbound_dry_run import inbound_dry_run


def main() -> int:
    result = inbound_dry_run()
    print(result.message)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
