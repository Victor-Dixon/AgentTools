#!/usr/bin/env python3
"""Verify planner unlock → Discord capability evolution feed slice."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EMIT = ROOT / "runtime/scripts/planner_unlock_discord_capability_feed_001.py"
PAYLOAD = ROOT / "data/reports/discord/capability_evolution_feed/latest_capability_evolution_event.json"
CARD = ROOT / "data/reports/discord/capability_evolution_feed/latest_capability_evolution_card.md"


def main() -> int:
    proc = subprocess.run(
        [sys.executable, str(EMIT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    emit_ok = proc.returncode == 0 and "DISCORD_CAPABILITY_EVOLUTION_FEED=PASS" in proc.stdout

    payload_ok = False
    if PAYLOAD.is_file():
        data = json.loads(PAYLOAD.read_text(encoding="utf-8"))
        payload_ok = (
            data.get("source_task") == "planner_unlock_priority_engine_001"
            and len(data.get("capability_unlocks") or []) >= 4
            and data.get("channel_key") == "master-task-log"
            and bool(data.get("planner_context", {}).get("top_lanes"))
        )

    card_ok = CARD.is_file() and "Capability Unlocked" in CARD.read_text(encoding="utf-8")

    ok = emit_ok and payload_ok and card_ok
    print(f"PLANNER_UNLOCK_DISCORD_FEED_VERIFY={'PASS' if ok else 'FAIL'}")
    print(f"  emit={'PASS' if emit_ok else 'FAIL'}")
    print(f"  payload={'PASS' if payload_ok else 'FAIL'}")
    print(f"  card={'PASS' if card_ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
