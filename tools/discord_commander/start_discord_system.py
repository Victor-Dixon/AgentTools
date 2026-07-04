#!/usr/bin/env python3
"""Start complete Discord system (bot + queue processor).

Adapted from Agent_Cellphone_V2_Repository/tools/start_discord_system.py
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _token_present() -> bool:
    return bool(os.getenv("DISCORD_BOT_TOKEN"))


def _spawn(script: str) -> subprocess.Popen | None:
    path = TOOLS / script
    if not path.exists():
        logger.error("Script not found: %s", path)
        return None
    return subprocess.Popen([sys.executable, str(path)], cwd=str(ROOT))


def main() -> int:
    print("Starting Discord Commander system (bot + queue)")
    if not _token_present():
        logger.error("DISCORD_BOT_TOKEN not set")
        return 1

    bot = _spawn("run_unified_discord_bot_with_restart.py")
    if bot is None:
        return 1
    time.sleep(3)
    queue = _spawn("start_message_queue_processor.py")

    print(f"Bot PID: {bot.pid}")
    print(f"Queue PID: {queue.pid if queue else 'FAILED'}")

    try:
        while True:
            time.sleep(1)
            if bot.poll() is not None:
                logger.error("Discord bot exited (code %s)", bot.returncode)
                break
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        for proc in (bot, queue):
            if proc and proc.poll() is None:
                proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
