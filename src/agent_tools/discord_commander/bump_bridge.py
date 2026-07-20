"""Discord Commander → DreamVault quad force Agent-mode bump (local PyAutoGUI only).

!bump must run on the Windows desktop with Cursor windows — never VPS webhook.
"""

from __future__ import annotations

import os as _bump_env
_bump_env.environ["DREAMVAULT_ROOT"] = r"D:\DreamVault"
_bump_env.environ["DREAMOS_VAULT_ROOT"] = r"D:\DreamVault"
_bump_env.environ["VAULT_ROOT"] = r"D:\DreamVault"
_bump_env.environ.setdefault("ALLOW_LIVE_CURSOR_INJECTION", "1")
_bump_env.environ.setdefault("DEFAULT_MODE", "pyautogui")
_bump_env.environ.setdefault("COORDINATE_MODE", "4-agent-1monitor")
_bump_env.environ.setdefault("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor")
_bump_env.environ.setdefault("DREAMOS_ALLOW_PYAUTOGUI_FAILSAFE_OVERRIDE", "1")

import logging
import os
from typing import Any

from agent_tools.discord_commander.env_bootstrap import bootstrap_commander_env
from agent_tools.discord_commander.models import OnboardResult
from agent_tools.discord_commander.onboard_bridge import QUAD_AGENTS, _live_allowed, _run_script
from agent_tools.discord_commander.template_bridge import resolve_dreamvault_root

logger = logging.getLogger(__name__)

SCRIPT_REL = "runtime/scripts/quad_force_agent_mode_ctrl_i_001.py"
REPORT_REL = "data/reports/coordination/quad_force_agent_mode_ctrl_i_latest.json"


def bump_agent(
    agent_id: str,
    *,
    live: bool = True,
    dry_run: bool = False,
) -> OnboardResult:
    """Force Agent mode for one agent: starter click → Ctrl+I → Enter."""
    bootstrap_commander_env()
    root = resolve_dreamvault_root()
    if root is None:
        return OnboardResult(
            success=False,
            message="DreamVault root not found",
            action="bump",
            error_code="DREAMVAULT_MISSING",
        )

    from agent_tools.discord_commander.agent_message_sender import normalize_agent_id

    normalized = normalize_agent_id(agent_id)
    if not normalized:
        return OnboardResult(
            success=False,
            message=f"Invalid agent: {agent_id}",
            action="bump",
            error_code="INVALID_AGENT",
        )

    return _run_bump(agents=[normalized], live=live, dry_run=dry_run, root=root)


def bump_quad(*, live: bool = True, dry_run: bool = False) -> OnboardResult:
    """Force Agent mode for all four agents (starter → Ctrl+I → Enter)."""
    bootstrap_commander_env()
    root = resolve_dreamvault_root()
    if root is None:
        return OnboardResult(
            success=False,
            message="DreamVault root not found",
            action="bump_quad",
            error_code="DREAMVAULT_MISSING",
        )
    return _run_bump(agents=list(QUAD_AGENTS), live=live, dry_run=dry_run, root=root)


def _run_bump(
    *,
    agents: list[str],
    live: bool,
    dry_run: bool,
    root,
) -> OnboardResult:
    want_live = bool(live) and not dry_run
    if want_live and not _live_allowed():
        return OnboardResult(
            success=False,
            message="ALLOW_LIVE_CURSOR_INJECTION=1 required for live bump",
            action="bump",
            error_code="LIVE_INJECTION_BLOCKED",
            data={"agents": agents},
        )

    args = [
        "--target",
        "starter_location_box",
        "--enter",
        "--agents",
        ",".join(agents),
        "--json",
    ]
    if want_live:
        args.insert(0, "--live")
    else:
        args.insert(0, "--dry-run")

    code, out = _run_script(SCRIPT_REL, args, root=root)
    report_path = root / REPORT_REL
    report: dict[str, Any] = {}
    if report_path.is_file():
        try:
            import json

            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("bump report read failed: %s", exc)

    status = str(report.get("status") or ("LIVE_PASS" if code == 0 and want_live else "UNKNOWN"))
    ok = code == 0 and status in ("LIVE_PASS", "DRY_RUN_PASS")
    mode = "live" if want_live else "dry_run"
    return OnboardResult(
        success=ok,
        message=(
            f"Bump {mode} {'PASS' if ok else 'FAIL'} agents={','.join(agents)} "
            f"status={status}\n{out[:1500]}"
        ),
        action="bump_quad" if len(agents) > 1 else "bump",
        error_code=None if ok else status or f"EXIT_{code}",
        data={
            "agents": agents,
            "status": status,
            "report": REPORT_REL,
            "exit_code": code,
            "mode": mode,
            "target": "starter_location_box",
            "press_enter": True,
        },
    )
