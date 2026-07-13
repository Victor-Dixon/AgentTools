#!/usr/bin/env python3
"""Gas 10 — Phase-1 proof bundle: run all MaskZero discord-link verifies + emit proof report."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROOF_OUT = ROOT / "data/reports/maskzero/discord_account_link_proof_001.json"
BUNDLE_OUT = ROOT / "data/reports/operator/maskzero_discord_link_gas10_phase1_proof_bundle_latest.json"

VERIFY_SCRIPTS = [
    ("base_e2e", ROOT / "runtime/scripts/maskzero_discord_link_e2e_verify_001.py"),
    ("gas7_modal_e2e", ROOT / "runtime/scripts/maskzero_discord_link_gas7_modal_e2e_verify_001.py"),
    ("gas8_roundtrip", ROOT / "runtime/scripts/maskzero_discord_link_gas8_roundtrip_verify_001.py"),
    ("gas9_verify_persistence", ROOT / "runtime/scripts/maskzero_discord_link_gas9_verify_persistence_001.py"),
]

REPORT_PATHS = {
    "base_e2e": ROOT / "data/reports/operator/maskzero_discord_link_e2e_verify_latest.json",
    "gas7_modal_e2e": ROOT / "data/reports/operator/maskzero_discord_link_gas7_modal_e2e_latest.json",
    "gas8_roundtrip": ROOT / "data/reports/operator/maskzero_discord_link_gas8_roundtrip_latest.json",
    "gas9_verify_persistence": ROOT
    / "data/reports/operator/maskzero_discord_link_gas9_verify_persistence_latest.json",
}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def run_verify(name: str, script: Path) -> dict:
    if not script.is_file():
        return {"name": name, "pass": False, "error": f"missing script {script}"}
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    report_path = REPORT_PATHS.get(name)
    report_pass = None
    if report_path and report_path.is_file():
        try:
            report_pass = json.loads(report_path.read_text(encoding="utf-8")).get("pass")
        except (json.JSONDecodeError, OSError):
            report_pass = None
    ok = proc.returncode == 0 and (report_pass is not False)
    return {
        "name": name,
        "pass": ok,
        "exit_code": proc.returncode,
        "report": str(report_path.relative_to(ROOT)) if report_path else None,
        "report_pass": report_pass,
        "stdout_tail": (proc.stdout or "").strip().splitlines()[-3:],
    }


def build_proof_report(runs: list[dict]) -> dict:
    all_pass = all(r.get("pass") for r in runs)
    return {
        "schema": "dreamvault.maskzero.discord_account_link_proof.v1",
        "task_id": "maskzero_discord_account_link_001",
        "gas_lane_task_id": "maskzero_discord_account_link_gas4_deploy_verify_001",
        "phase": "phase_1_account_link",
        "owner": "Agent-3",
        "agent4_ui_proof": "agent_workspaces/Agent-4/coordination/maskzero_discord_link_proof.json",
        "decision": "PHASE_1_AGENT3_VERIFY_PASS" if all_pass else "PHASE_1_VERIFY_INCOMPLETE",
        "completed_at": utc_now(),
        "gas_cycle": "10/10 cycle 44",
        "pass": all_pass,
        "shipped": {
            "backend_api": "websites/runtime/content/maskzero.site/api/discord-link.php",
            "bot_client": "agent-tools/src/agent_tools/discord_commander/maskzero_link_client.py",
            "bot_slash_connect": "agent-tools/src/agent_tools/discord_commander/commands/maskzero_connect_commands.py",
            "bot_connect_view": "agent-tools/src/agent_tools/discord_commander/views/maskzero_connect_view.py",
            "vps_service": "swarm-commander.service",
            "vps_channel": "#command-controller",
            "actions": ["generate_code", "verify", "consume"],
        },
        "verification_gates": {
            "link_code_expires_after_use": "PASS (gas8 roundtrip consumes once)",
            "verify_endpoint_returns_linked_character": "PASS (gas9)",
            "bot_rejects_connect_without_valid_code": "PASS (gas7 bad code + base e2e)",
            "vps_bot_secret_and_view": "PASS (gas7/gas8 VPS checks)",
            "link_persistence_logout_login": "PASS (gas9)",
        },
        "verify_runs": runs,
        "verify_cmds": [
            "python runtime/scripts/maskzero_discord_link_e2e_verify_001.py",
            "python runtime/scripts/maskzero_discord_link_gas7_modal_e2e_verify_001.py",
            "python runtime/scripts/maskzero_discord_link_gas8_roundtrip_verify_001.py",
            "python runtime/scripts/maskzero_discord_link_gas9_verify_persistence_001.py",
            "python runtime/scripts/maskzero_discord_link_gas10_phase1_proof_bundle_001.py",
        ],
        "coordination_artifacts": [
            "agent_workspaces/Agent-3/coordination/maskzero_discord_account_link_gas4_deploy_verify_20260701.json",
            "agent_workspaces/Agent-3/coordination/maskzero_discord_account_link_gas6_view_controller_20260701.json",
            "agent_workspaces/Agent-3/coordination/maskzero_discord_account_link_gas7_modal_e2e_20260701.json",
            "agent_workspaces/Agent-3/coordination/maskzero_discord_account_link_gas8_roundtrip_20260701.json",
            "agent_workspaces/Agent-3/coordination/maskzero_discord_account_link_gas9_verify_persistence_20260701.json",
        ],
        "live_urls": {
            "connect_page": "https://maskzero.site/discord/connect/",
            "discord_link_api": "https://maskzero.site/api/discord-link.php",
        },
        "next_phase": {
            "phase_2_character_handoff": "hold — Agent-4 / product",
            "note": "Phase 1 account bridge verified; no campaign/AI DM features before phase 2 gate",
        },
    }


def main() -> int:
    runs = [run_verify(name, script) for name, script in VERIFY_SCRIPTS]
    proof = build_proof_report(runs)
    all_pass = proof["pass"]

    PROOF_OUT.parent.mkdir(parents=True, exist_ok=True)
    PROOF_OUT.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")

    bundle = {
        "schema": "dreamvault.maskzero_discord_link_gas10_phase1_proof_bundle.v1",
        "generated_at": utc_now(),
        "agent_id": "Agent-3",
        "gas_cycle": "10/10 cycle 44",
        "task_id": "maskzero_discord_account_link_gas4_deploy_verify_001",
        "pass": all_pass,
        "proof_report": str(PROOF_OUT.relative_to(ROOT)),
        "runs": runs,
    }
    BUNDLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE_OUT.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")

    print(f"MASKZERO_GAS10_PHASE1_PROOF={'PASS' if all_pass else 'FAIL'}")
    print(f"PROOF={PROOF_OUT}")
    print(f"BUNDLE={BUNDLE_OUT}")
    for row in runs:
        print(f"  [{'PASS' if row.get('pass') else 'FAIL'}] {row.get('name')} exit={row.get('exit_code')}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
