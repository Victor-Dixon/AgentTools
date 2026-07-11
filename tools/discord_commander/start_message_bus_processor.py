#!/usr/bin/env python3
"""Start DreamVault unified message bus processor (SSOT) for Discord D2A delivery.

Replaces legacy start_message_queue_processor.py JSON queue. All Discord → agent
messages enqueue on bus_state.json; this process drains via PyAutoGUI.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.env_bootstrap import bootstrap_commander_env  # noqa: E402


def main() -> int:
    vault = bootstrap_commander_env()
    if vault is None:
        print("BLOCKED: DREAMVAULT_ROOT not found", file=sys.stderr)
        return 1

    script = vault / "runtime" / "scripts" / "message_bus_queue_processor_001.py"
    if not script.is_file():
        print(f"BLOCKED: missing {script}", file=sys.stderr)
        return 1

    os.environ["ALLOW_LIVE_CURSOR_INJECTION"] = "1"
    cmd = [sys.executable, "-u", str(script), "--live"]
    print(f"MESSAGE_BUS_PROCESSOR_START vault={vault}")
    print(f"CMD={' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(vault))


if __name__ == "__main__":
    raise SystemExit(main())
