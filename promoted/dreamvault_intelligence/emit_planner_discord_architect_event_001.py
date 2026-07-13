#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

root = Path.cwd()

def read_text(path: Path, fallback: str = "unknown") -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return fallback

def read_json(path: Path, fallback: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

next_lane_md = read_text(root / "data/reports/planner/next_lane.md", "unknown")
runtime_summary = read_json(root / "data/reports/governance/runtime_governance_summary.json", {})

latest_task = read_text(root / "runtime/tasks/discord/planner_discord_architect_bridge_001.yaml", "")

event = {
    "event_id": f"planner_update_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
    "event_type": "planner_transition",
    "source": "dreamvault.planner",
    "target_channel": "master-task-log",
    "created_at": datetime.now(UTC).isoformat(),
    "severity": "info",
    "title": "Planner Transition",
    "summary": "Planner emitted current next-lane state.",
    "content": "\n".join([
        "🧭 **Planner Transition**",
        "",
        "**Next Lane**",
        f"```text\n{next_lane_md[:1200]}\n```",
        "",
        "**Governance**",
        f"- risk: `{runtime_summary.get('governance_risk', 'unknown')}`",
        f"- next_lane: `{runtime_summary.get('next_lane', 'unknown')}`",
        "",
        "Route: `master-task-log`",
        "Source task: `planner_discord_architect_bridge_001`",
    ]),
    "payload": {
        "next_lane": next_lane_md,
        "runtime_governance_summary": runtime_summary,
        "latest_task_preview": latest_task[:1000],
    },
}

event_dir = root / "discord_architect/data/runtime/events"
event_dir.mkdir(parents=True, exist_ok=True)

latest_event = event_dir / "latest_planner_event.json"
journal = event_dir / "planner_events.jsonl"

latest_event.write_text(json.dumps(event, indent=2), encoding="utf-8")
with journal.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False) + "\n")

node = """
const fs = require("fs");
const { dispatchCapabilityEvent } = require("./discord_architect/src/runtime/liveCapabilityEventDispatcher.js");

async function main() {
  const event = JSON.parse(fs.readFileSync("discord_architect/data/runtime/events/latest_planner_event.json", "utf8"));
  const receipt = await dispatchCapabilityEvent({ event, mode: process.env.DISCORD_DISPATCH_MODE || "dry-run" });
  console.log(JSON.stringify(receipt, null, 2));
}

main().catch((err) => {
  console.error(err.stack || String(err));
  process.exit(1);
});
"""

result = subprocess.run(
    ["node", "-e", node],
    cwd=root,
    text=True,
    capture_output=True,
    env=os.environ,
)

receipt = {
    "ok": result.returncode == 0,
    "mode": os.environ.get("DISCORD_DISPATCH_MODE", "dry-run"),
    "event": str(latest_event),
    "stdout": result.stdout,
    "stderr": result.stderr,
}

out = root / "data/reports/planner_discord_bridge/latest_receipt.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

print("PLANNER_DISCORD_ARCHITECT_EVENT=PASS" if receipt["ok"] else "PLANNER_DISCORD_ARCHITECT_EVENT=FAIL")
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
    raise SystemExit(result.returncode)
