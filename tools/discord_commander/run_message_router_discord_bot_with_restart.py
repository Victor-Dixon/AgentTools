#!/usr/bin/env python3
"""Run message-router backup bot with auto-restart (prefix !message only)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.env_bootstrap import bootstrap_commander_env

bootstrap_commander_env()


def run_bot() -> int:
    return subprocess.call(
        [sys.executable, "-m", "agent_tools.discord_commander.message_router_discord_bot"]
    )


def main() -> int:
    print("Message router bot runner (auto-restart)")
    crash_count = 0
    while True:
        code = run_bot()
        if code == 0:
            return 0
        crash_count += 1
        if crash_count >= 3:
            print("Message router bot crashed 3 times; stopping.")
            return code
        print(f"Crash {crash_count}/3; retry in 10s...")
        time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
