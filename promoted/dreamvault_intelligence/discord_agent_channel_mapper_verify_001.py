#!/usr/bin/env python3
"""Verify per-agent Discord channel map SSOT — one agent, one channel, one transport."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

REQUIRED_AGENTS = ("Agent-1", "Agent-2", "Agent-3", "Agent-4")
SSOT = Path("data/registry/discord_agent_channel_map.yaml")


def load_map(root: Path) -> dict:
    path = root / SSOT
    if not path.is_file():
        raise FileNotFoundError(path)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def verify(root: Path) -> dict:
    data = load_map(root)
    agents = data.get("agents") or {}
    channels: set[str] = set()
    issues: list[str] = []

    for agent_id in REQUIRED_AGENTS:
        entry = agents.get(agent_id)
        if not entry:
            issues.append(f"missing_agent:{agent_id}")
            continue
        ch = str(entry.get("discord_channel") or "").strip()
        if not ch:
            issues.append(f"missing_channel:{agent_id}")
        elif ch in channels:
            issues.append(f"duplicate_channel:{ch}")
        else:
            channels.add(ch)
        if not entry.get("webhook_env"):
            issues.append(f"missing_webhook_env:{agent_id}")

    bridge = data.get("discord_commander_bridge") or {}
    if bridge.get("target") != "agent_messaging_send_001.py":
        issues.append("bridge_target_not_messaging_ssot")

    messaging = data.get("messaging_ssot") or {}
    if messaging.get("send_cli") != "runtime/scripts/agent_messaging_send_001.py":
        issues.append("messaging_ssot_send_cli_mismatch")

    status = "PASS" if not issues else "BLOCKED"
    return {
        "status": status,
        "ssot": str(SSOT).replace("\\", "/"),
        "agents_mapped": len(agents),
        "unique_channels": sorted(channels),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    result = verify(root)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"DISCORD_AGENT_CHANNEL_MAP={result['status']}")
        if result["issues"]:
            print("ISSUES=" + ",".join(result["issues"]))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
