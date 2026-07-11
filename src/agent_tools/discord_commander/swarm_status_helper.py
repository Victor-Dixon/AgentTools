"""Read agent status.json files for Discord Commander views and commands."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def vault_root() -> Path:
    raw = os.getenv("DREAMVAULT_ROOT", "D:\\DreamVault").strip()
    return Path(raw)


def read_swarm_statuses() -> dict[str, dict[str, Any]]:
    vault = vault_root()
    if not vault.is_dir():
        return {}
    src = vault / "src"
    commander_src = vault / "runtime" / "discord_commander" / "src"
    for path in (src, commander_src):
        if path.is_dir() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    try:
        from dreamvault.discord.commander.swarm_status_reader import (
            SwarmStatusReader,
            resolve_agent_workspace_dir,
        )

        workspace = resolve_agent_workspace_dir(vault)
        reader = SwarmStatusReader(workspace)
        return reader.read_all_statuses()
    except Exception:
        return {}


def list_quad_agents() -> list[str]:
    return [f"Agent-{i}" for i in range(1, 5)]


def list_swarm_agents() -> list[str]:
    return [f"Agent-{i}" for i in range(1, 9)]


def agent_row(agent_id: str, statuses: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    statuses = statuses if statuses is not None else read_swarm_statuses()
    row = statuses.get(agent_id, {})
    return {
        "id": agent_id,
        "name": row.get("agent_name") or agent_id,
        "status": row.get("status") or row.get("fsm_state") or "unknown",
        "mission": str(row.get("current_mission") or row.get("current_task") or "")[:120],
        "task": str(row.get("current_task") or ""),
    }


def status_emoji(status: str) -> str:
    upper = str(status).upper()
    if "ACTIVE" in upper or "JET_FUEL" in upper:
        return "🟢"
    if "COMPLETE" in upper or "CLOSED" in upper or "PASS" in upper:
        return "✅"
    if "REST" in upper or "STANDBY" in upper or "IDLE" in upper:
        return "💤"
    if "ERROR" in upper or "FAILED" in upper or "BLOCK" in upper:
        return "🔴"
    return "🟡"
