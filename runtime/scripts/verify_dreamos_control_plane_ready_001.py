#!/usr/bin/env python3
"""Verify dreamos_control_plane_server ready_for_tunnel gate."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mcp_servers"))
import dreamos_control_plane_server as cps  # noqa: E402

GAB = Path(r"D:\Projects\github-architect-bot")
MASKZERO = (
    GAB
    / "runtime"
    / "manifests"
    / "branch_delete_requests"
    / "websites_maskzero_salvage_20260813.branch_delete.json"
)
OUT = (
    Path(r"D:\DreamVault")
    / "data"
    / "reports"
    / "control_plane"
    / "dreamos_control_plane_ready_latest.json"
)
DV_COORD = (
    Path(r"D:\DreamVault")
    / "agent_workspaces"
    / "Agent-1"
    / "coordination"
    / "dreamos_control_plane_mcp_ready_20260826.json"
)


def main() -> int:
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    tools = sorted(cps.TOOLS.keys())
    expected = [
        "bot_status",
        "collect_results",
        "dry_run_approved_branch_delete",
        "execute_approved_branch_delete",
        "fleet_status",
        "get_branch_delete_receipt",
        "health",
        "inspect_branch_delete_request",
        "list_bots",
        "list_channels",
        "list_webhooks",
        "recent_delivery_receipts",
        "send_agent_command",
        "send_embed",
        "send_message",
        "task_status",
    ]

    init = cps.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    listed = cps.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    listed_names = sorted(t["name"] for t in listed["result"]["tools"])

    src = (ROOT / "mcp_servers" / "dreamos_control_plane_server.py").read_text(encoding="utf-8")
    no_delete_ref = "git/refs" not in src and "-X DELETE" not in src

    maskzero = {"status": "SKIP", "ok": False}
    maskzero_ready = False
    if MASKZERO.is_file() and (GAB / "runtime/scripts/approved_branch_delete_lib.py").is_file():
        manifest = json.loads(MASKZERO.read_text(encoding="utf-8"))
        if manifest.get("status") == "executed":
            receipt = cps.get_branch_delete_receipt()
            maskzero = {
                "status": "ALREADY_EXECUTED",
                "ok": receipt.get("ok") is True or bool(receipt.get("receipt")),
                "repository": manifest.get("repository"),
                "branch": manifest.get("branch"),
                "executed_at": manifest.get("executed_at"),
            }
            maskzero_ready = maskzero["ok"]
        else:
            try:
                maskzero = cps.dry_run_approved_branch_delete(str(MASKZERO))
                maskzero_ready = maskzero.get("status") == "DRY_RUN_PASS"
            except Exception as exc:  # noqa: BLE001
                maskzero = {"status": "ERROR", "ok": False, "error": str(exc)}

    discord_dry = cps.send_message("Agent-1", "tunnel-proof", "dry-run", dry_run=True)
    health = cps.health()
    fail_closed = cps.execute_approved_branch_delete(str(MASKZERO) if MASKZERO.is_file() else "x", False)
    malformed = cps.handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "inspect_branch_delete_request",
                "arguments": {"request_path": r"C:\Temp\evil.json"},
            },
        }
    )
    malformed_body = json.loads(malformed["result"]["content"][0]["text"])

    secret_scan = {
        "webhook_list_clean": "https://discord.com/api/webhooks" not in json.dumps(cps.list_webhooks()),
        "health_clean": "sk-" not in json.dumps(health),
        "no_delete_ref_in_source": no_delete_ref,
    }

    ready = (
        init["result"]["serverInfo"]["name"] == "dreamos-control-plane"
        and listed_names == expected
        and no_delete_ref
        and maskzero_ready
        and bool(discord_dry.get("dry_run"))
        and fail_closed.get("reason") == "AUTHORITY_MISSING"
        and malformed_body.get("ok") is False
        and all(secret_scan.values())
    )

    report = {
        "schema": "dreamvault.dreamos_control_plane_ready.v1",
        "generated_at": now,
        "status": "READY" if ready else "NOT_READY",
        "server_path": str(ROOT / "mcp_servers" / "dreamos_control_plane_server.py"),
        "tools": listed_names,
        "github_architect_reused": True,
        "discord_reused": True,
        "tests": "pytest -q tests/test_dreamos_control_plane_server_001.py",
        "maskzero_dry_run": {
            "status": maskzero.get("status"),
            "ok": maskzero.get("ok"),
            "reason": maskzero.get("reason"),
            "delegated_to": maskzero.get("delegated_to"),
        },
        "discord_outbound_dry_run": {
            "ok": discord_dry.get("ok"),
            "dry_run": discord_dry.get("dry_run"),
            "target_configured": discord_dry.get("target_configured"),
        },
        "secret_scan": secret_scan,
        "fail_closed": {
            "execute_without_confirm": fail_closed.get("reason"),
            "malformed_request": malformed_body.get("error") or malformed_body.get("status"),
        },
        "ready_for_tunnel": ready,
        "tunnel_id_hint": "tunnel_6a8f57082d248191a5a0a47531804744",
        "mcp_command": r"python D:\agent-tools\mcp_servers\dreamos_control_plane_server.py",
        "next": [
            "Create CONTROL_PLANE_API_KEY (runtime) in OpenAI Platform — do not paste into chat",
            "$env:CONTROL_PLANE_TUNNEL_ID='tunnel_6a8f57082d248191a5a0a47531804744'",
            "$env:CONTROL_PLANE_API_KEY='<runtime-key>'",
            "tunnel-client init / doctor / run with MCP command above",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    DV_COORD.parent.mkdir(parents=True, exist_ok=True)
    DV_COORD.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"STATUS={report['status']}")
    print(f"ready_for_tunnel={ready}")
    print(f"OUT={OUT}")
    print(json.dumps({k: report[k] for k in ('server_path','tools','maskzero_dry_run','secret_scan','ready_for_tunnel')}, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
