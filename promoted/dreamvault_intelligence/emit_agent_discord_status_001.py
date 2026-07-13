#!/usr/bin/env python3
"""Emit per-agent Discord status — required operator visibility when away from desktop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dreamvault.discord.agent_status_emitter import (  # noqa: E402
    emit_agent_discord_status,
    emit_from_status_json,
)

DEFAULT_AGENTS = ("Agent-1", "Agent-2", "Agent-3", "Agent-4")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post agent lane status to Discord (per-agent webhook)",
        epilog=(
            "Required after every task slice, A2A reply, and hard onboard.\n"
            "Live: --live or DISCORD_DISPATCH_MODE=live\n"
            "Policy: runtime/policies/agent_discord_status_required_001.yaml"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-a", "--agent", action="append", help="Agent-N (repeatable; default Agent-4)")
    parser.add_argument("--fleet", action="store_true", help="Post all quad agents from status.json")
    parser.add_argument("--from-status", action="store_true", help="Read fields from status.json")
    parser.add_argument("--summary", "-s", help="Operator-visible summary (required unless --from-status)")
    parser.add_argument("--phase", default="", help="Current phase label")
    parser.add_argument("--status", default="", help="Agent status string")
    parser.add_argument("--task", default="", help="Task id")
    parser.add_argument("--artifact", action="append", default=[], help="Proof artifact path (repeatable)")
    parser.add_argument("--next", dest="next_step", default="", help="Next concrete step")
    parser.add_argument("--gas-slice", default="", help="Gas slice e.g. 2/5")
    parser.add_argument("--live", action="store_true", help="Live Discord post")
    parser.add_argument("--json", action="store_true", help="Print full result JSON")
    args = parser.parse_args()

    targets = list(args.agent or [])
    if args.fleet:
        targets = list(DEFAULT_AGENTS)
    if not targets:
        targets = ["Agent-4"]

    if not args.from_status and not args.summary and len(targets) == 1:
        parser.error("--summary required unless --from-status or --fleet")

    results: list[dict] = []
    ok_all = True
    for agent_id in targets:
        try:
            if args.from_status or args.fleet:
                result = emit_from_status_json(
                    agent_id,
                    summary=args.summary,
                    vault_root=REPO_ROOT,
                    live=args.live if args.live else None,
                )
            else:
                result = emit_agent_discord_status(
                    agent_id,
                    args.summary or "",
                    phase=args.phase,
                    status=args.status,
                    task_id=args.task,
                    artifacts=args.artifact or None,
                    next_step=args.next_step,
                    gas_slice=args.gas_slice,
                    vault_root=REPO_ROOT,
                    live=args.live if args.live else None,
                )
        except FileNotFoundError as exc:
            result = {"ok": False, "agent_id": agent_id, "error": str(exc)}
        results.append(result)
        ok_all = ok_all and bool(result.get("ok"))

        mode = "LIVE" if result.get("live") else "DRY_RUN"
        send = result.get("send_result") or {}
        print(
            f"{mode} {agent_id}: ok={result.get('ok')} "
            f"webhook={result.get('webhook_resolved')} "
            f"http={send.get('status_code')} msg={send.get('message', result.get('error', ''))}"
        )
        outputs = result.get("outputs") or {}
        if outputs.get("artifact_latest"):
            print(f"  artifact={outputs['artifact_latest']}")

    if args.json:
        print(json.dumps(results, indent=2))

    print(f"EMIT_AGENT_DISCORD_STATUS={'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
