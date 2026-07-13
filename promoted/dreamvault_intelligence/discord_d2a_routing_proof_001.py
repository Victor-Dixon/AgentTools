#!/usr/bin/env python3
"""One-shot D2A routing proof: enqueue + live dispatch to Agent-1."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

AGENT_TOOLS = Path(r"D:\agent-tools")
DREAMVAULT = Path(r"D:\DreamVault")
sys.path.insert(0, str(AGENT_TOOLS / "src"))

from agent_tools.discord_commander.env_bootstrap import bootstrap_commander_env  # noqa: E402
from agent_tools.discord_commander.agent_message_sender import send_agent_message  # noqa: E402

bootstrap_commander_env()

body = (
    "[LIVE ROUTING PROOF] Discord D2A bus test — reply ROUTING_OK if you see this in Cursor."
)
result = send_agent_message(
    "Agent-1",
    body,
    source="routing_proof_live2",
)
print(f"ENQUEUE success={result.success} detail={result.message}")
bus_id = (result.data or {}).get("bus_message_id")
print(f"BUS_ID={bus_id}")

if not result.success:
    raise SystemExit(1)

proc = subprocess.run(
    [
        sys.executable,
        str(DREAMVAULT / "runtime" / "scripts" / "message_bus_dispatch_001.py"),
        "dispatch",
        "--live",
    ],
    cwd=str(DREAMVAULT),
    capture_output=True,
    text=True,
    env={**dict(**__import__("os").environ), "ALLOW_LIVE_CURSOR_INJECTION": "1", "AGENT_GAS_LAYOUT_MODE": "4-agent-1monitor"},
)
print(proc.stdout.strip() or proc.stderr.strip())
raise SystemExit(proc.returncode)
