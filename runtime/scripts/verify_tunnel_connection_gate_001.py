#!/usr/bin/env python3
"""Verify Dream.OS Secure MCP Tunnel connection gate (local checks only).

Does not require CONTROL_PLANE_API_KEY unless --require-doctor is passed.
Never prints or persists API keys.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mcp_servers"))
import dreamos_control_plane_server as cps  # noqa: E402

TUNNEL_EXE = ROOT / "bin" / "tunnel-client" / "tunnel-client.exe"
PROFILE = "dreamos-control-plane"
PROFILE_PATH = Path.home() / "AppData" / "Roaming" / "tunnel-client" / f"{PROFILE}.yaml"
MCP_CMD = r"python D:/agent-tools/mcp_servers/dreamos_control_plane_server.py"
TUNNEL_ID = "tunnel_6a8f57082d248191a5a0a47531804744"
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
    / "tunnel_connection_gate_latest.json"
)
COORD = (
    Path(r"D:\DreamVault")
    / "agent_workspaces"
    / "Agent-1"
    / "coordination"
    / "tunnel_connection_gate_20260826.json"
)

APPROVED_TOOLS = sorted(
    [
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
)

FORBIDDEN_TOOL_NAMES = {
    "shell",
    "exec",
    "delete_ref",
    "read_file",
    "write_file",
    "run_command",
    "filesystem",
}


def _maskzero_gate() -> dict:
    if not MASKZERO.is_file():
        return {"status": "SKIP", "ok": False, "reason": "manifest_missing"}
    manifest = json.loads(MASKZERO.read_text(encoding="utf-8"))
    if manifest.get("status") == "executed":
        receipt = cps.get_branch_delete_receipt()
        return {
            "status": "ALREADY_EXECUTED",
            "ok": receipt.get("ok") is True or bool(receipt.get("receipt")),
            "repository": manifest.get("repository"),
            "branch": manifest.get("branch"),
            "executed_at": manifest.get("executed_at"),
            "receipt_probe": {"ok": receipt.get("ok"), "found": bool(receipt.get("receipt"))},
        }
    out = cps.dry_run_approved_branch_delete(str(MASKZERO))
    return {
        "status": out.get("status"),
        "ok": out.get("ok") is True and out.get("status") == "DRY_RUN_PASS",
        "reason": out.get("reason"),
    }


def _run_doctor() -> dict:
    if not TUNNEL_EXE.is_file():
        return {"status": "SKIP", "exit_code": None, "pass": False, "reason": "binary_missing"}
    if not os.environ.get("CONTROL_PLANE_API_KEY"):
        return {
            "status": "BLOCKED",
            "exit_code": None,
            "pass": False,
            "reason": "CONTROL_PLANE_API_KEY not set in environment",
        }
    proc = subprocess.run(
        [str(TUNNEL_EXE), "doctor", "--profile", PROFILE],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    combined = (proc.stdout or "") + (proc.stderr or "")
    passed = proc.returncode == 0 and "RESULT pass" in combined
    return {
        "status": "PASS" if passed else "FAIL",
        "exit_code": proc.returncode,
        "pass": passed,
        "summary_line": next((ln.strip() for ln in combined.splitlines() if ln.startswith("RESULT ")), ""),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-doctor",
        action="store_true",
        help="Fail unless CONTROL_PLANE_API_KEY is set and tunnel-client doctor passes",
    )
    args = parser.parse_args()

    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    client_installed = TUNNEL_EXE.is_file()
    version = None
    if client_installed:
        proc = subprocess.run(
            [str(TUNNEL_EXE), "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        version = (proc.stdout or proc.stderr or "").strip()

    init = cps.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    listed = cps.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tool_names = sorted(t["name"] for t in listed["result"]["tools"])
    forbidden_hits = [n for n in tool_names if n in FORBIDDEN_TOOL_NAMES]

    src = (ROOT / "mcp_servers" / "dreamos_control_plane_server.py").read_text(encoding="utf-8")
    github_ready = (GAB / "runtime/scripts/approved_branch_delete_lib.py").is_file()
    discord_health = cps.health()
    discord_ready = isinstance(discord_health.get("discord"), dict)

    doctor = _run_doctor()
    maskzero = _maskzero_gate()

    gate = {
        "tunnel": {
            "client_installed": client_installed,
            "client_path": str(TUNNEL_EXE),
            "version": version,
            "profile": PROFILE,
            "profile_path": str(PROFILE_PATH) if PROFILE_PATH.is_file() else None,
            "tunnel_id": TUNNEL_ID,
            "mcp_command": MCP_CMD,
            "api_key_env_set": bool(os.environ.get("CONTROL_PLANE_API_KEY")),
            "doctor": doctor["status"],
            "doctor_pass": doctor["pass"],
            "run_state": "NOT_STARTED",
        },
        "mcp": {
            "initialize": "PASS" if init.get("result", {}).get("serverInfo", {}).get("name") == "dreamos-control-plane" else "FAIL",
            "tool_count": len(tool_names),
            "approved_tools_only": tool_names == APPROVED_TOOLS and not forbidden_hits,
            "tools": tool_names,
            "forbidden_hits": forbidden_hits,
            "no_delete_ref_in_source": "git/refs" not in src and "-X DELETE" not in src,
        },
        "control_plane": {
            "github_architect": "READY" if github_ready else "MISSING",
            "discord": "READY" if discord_ready else "DEGRADED",
            "maskzero": maskzero,
        },
    }

    local_ready = (
        gate["tunnel"]["client_installed"]
        and gate["tunnel"]["profile_path"]
        and gate["mcp"]["initialize"] == "PASS"
        and gate["mcp"]["approved_tools_only"]
        and gate["control_plane"]["github_architect"] == "READY"
        and gate["control_plane"]["discord"] == "READY"
        and (maskzero.get("ok") or maskzero.get("status") in {"SKIP"})
    )

    full_ready = local_ready and doctor["pass"]

    if args.require_doctor and not doctor["pass"]:
        overall = "BLOCKED_DOCTOR"
    elif full_ready:
        overall = "READY_FOR_CHATGPT_SCAN"
    elif local_ready:
        overall = "BLOCKED_OPERATOR_KEY"
    else:
        overall = "NOT_READY"

    report = {
        "schema": "agenttools.tunnel_connection_gate.v1",
        "generated_at": now,
        "status": overall,
        "gate": gate,
        "chatgpt_next": [
            "Set CONTROL_PLANE_API_KEY in the terminal (never paste into chat)",
            f"$env:CONTROL_PLANE_TUNNEL_ID = '{TUNNEL_ID}'",
            f"& '{TUNNEL_EXE}' doctor --profile {PROFILE}",
            f"& '{TUNNEL_EXE}' run --profile {PROFILE}",
            "ChatGPT → Settings → Connectors → Connection: Tunnel → Scan Tools",
            "Acceptance: health + list_bots (read-only); get_branch_delete_receipt (MaskZero already executed)",
        ],
        "operator_commands": {
            "doctor": f"& '{TUNNEL_EXE}' doctor --profile {PROFILE} --explain",
            "run": f"& '{TUNNEL_EXE}' run --profile {PROFILE}",
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    COORD.parent.mkdir(parents=True, exist_ok=True)
    COORD.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"STATUS={overall}")
    print(f"OUT={OUT}")
    print(json.dumps({"gate": gate, "status": overall}, indent=2))
    if args.require_doctor:
        return 0 if full_ready else 1
    return 0 if local_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
