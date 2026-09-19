#!/usr/bin/env python3
"""Run Discord bot with auto-restart support.

Adapted from Agent_Cellphone_V2_Repository/tools/run_unified_discord_bot_with_restart.py
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def run_bot() -> int:
    module = "agent_tools.discord_commander.bot_runner_service"
    return subprocess.call([sys.executable, "-m", module])


def main() -> int:
    print("Discord Commander bot runner (auto-restart)")
    restart_flag = ROOT / ".discord_bot_restart"
    crash_count = 0
    max_crashes = 3
    crash_cooldown = 10

    while True:
        exit_code = run_bot()
        if restart_flag.exists():
            restart_flag.unlink()
            crash_count = 0
            print("Restart requested — restarting in 3 seconds...")
            time.sleep(3)
            continue
        if exit_code != 0:
            crash_count += 1
            if crash_count >= max_crashes:
                print(f"Bot crashed {max_crashes} times; stopping auto-restart.")
                return exit_code
            print(f"Crash {crash_count}/{max_crashes}; retrying in {crash_cooldown}s...")
            time.sleep(crash_cooldown)
            continue
        break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
