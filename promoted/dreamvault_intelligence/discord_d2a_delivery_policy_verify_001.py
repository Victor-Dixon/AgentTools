#!/usr/bin/env python3
"""Verify Discord !message delivery policy: PyAutoGUI-only, single delivery owner.

Checks:
  - DreamVault preflight + bridge regression tests pass
  - agent-tools agent_message_sender has no webhook fallback path
  - message_bus_bridge uses processor-owned delivery when processor is up

Usage:
  python runtime/scripts/discord_d2a_delivery_policy_verify_001.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_TOOLS_SENDER = Path(r"D:\agent-tools\src\agent_tools\discord_commander\agent_message_sender.py")
AGENT_TOOLS_BRIDGE = Path(r"D:\agent-tools\src\agent_tools\discord_commander\message_bus_bridge.py")
OUT = REPO_ROOT / "data/reports/coordination/discord_d2a_delivery_policy_latest.json"


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def run_policy_checks() -> dict:
    failures: list[str] = []
    sender_src = _read(AGENT_TOOLS_SENDER)
    bridge_src = _read(AGENT_TOOLS_BRIDGE)

    if "post_to_discord" in sender_src:
        failures.append("agent_message_sender still imports/calls post_to_discord")
    if "outbound_webhook" in sender_src:
        failures.append("agent_message_sender still references outbound_webhook")
    if "_webhook_fallback_enabled" in sender_src:
        failures.append("agent_message_sender still has webhook fallback helper")
    if (
        "falling back to direct PyAutoGUI" not in sender_src
        and "trying direct PyAutoGUI once" not in sender_src
    ):
        failures.append("agent_message_sender missing PyAutoGUI fallback after bus fail")
    if "_poll_bus_message" not in bridge_src:
        failures.append("message_bus_bridge missing processor poll helper")
    if "message_bus_processor_live" not in bridge_src:
        failures.append("message_bus_bridge missing processor-owned transport label")

    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_discord_message_bus_bridge_failclosed_001.py",
        "tests/test_discord_d2a_routing_preflight_001.py",
        "-q",
    ]
    proc = subprocess.run(pytest_cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    pytest_ok = proc.returncode == 0
    if not pytest_ok:
        failures.append(f"DreamVault pytest failed: {proc.stdout[-400:]}{proc.stderr[-400:]}")

    agent_tools_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_messaging_delivery_tdd.py::TestSendAgentMessageDelivery",
        "-q",
    ]
    at_proc = subprocess.run(
        agent_tools_cmd,
        cwd=r"D:\agent-tools",
        capture_output=True,
        text=True,
        env={**dict(**__import__("os").environ), "PYTHONPATH": r"D:\agent-tools\src;D:\DreamVault\src"},
    )
    at_ok = at_proc.returncode == 0
    if not at_ok:
        failures.append(f"agent-tools pytest failed: {at_proc.stdout[-400:]}{at_proc.stderr[-400:]}")

    payload = {
        "schema": "dreamvault.discord_d2a_delivery_policy.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "pass": not failures,
        "policy": {
            "pyautogui_only": True,
            "webhook_fallback": False,
            "bus_fail_fallback": "direct_pyautogui",
            "single_delivery_owner": "processor_when_running_else_inline_or_direct_pyautogui",
        },
        "checks": {
            "sender_no_webhook": "post_to_discord" not in sender_src,
            "bridge_processor_poll": "_poll_bus_message" in bridge_src,
            "dreamvault_pytest": pytest_ok,
            "agent_tools_pytest": at_ok,
        },
        "failures": failures,
        "verify_cmd": "python runtime/scripts/discord_d2a_delivery_policy_verify_001.py",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=OUT)
    args = parser.parse_args()

    proof = run_policy_checks()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")

    status = "PASS" if proof["pass"] else "FAIL"
    print(f"DISCORD_D2A_DELIVERY_POLICY={status}")
    if proof["failures"]:
        for item in proof["failures"]:
            print(f"  FAIL: {item}", file=sys.stderr)
    print(f"PROOF={args.json_out}")
    return 0 if proof["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
