"""AgentTools adapter: the reusable execution toolbelt.

Before implementing a helper inside dream_control, look here.  This module
reports which AgentTools capabilities are reachable from the *current*
environment, because two agents may have different tool access.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config import OperatorConfig, project_root_for, read_json, tool_available

# Surfaces AgentTools already owns. Entries map a capability name to the
# import/CLI surface that provides it.
KNOWN_SURFACES: dict[str, dict[str, str]] = {
    "mcp_servers": {"module": "swarm_mcp.servers", "cli": "swarm-tasks-server"},
    "agent_messaging": {"module": "swarm_mcp.servers.messaging", "cli": "swarm-messaging-server"},
    "shared_memory": {"module": "swarm_mcp.servers.memory", "cli": "swarm-memory-server"},
    "swarm_control": {"module": "swarm_mcp.servers.control", "cli": "swarm-control-server"},
    "toolbelt_cli": {"module": "swarm_mcp.cli", "cli": "swarm"},
    "discord_commander": {"module": "agent_tools.discord_commander", "cli": ""},
}

CAPABILITY_REGISTRY = Path("data") / "registry" / "agenttools_capability_registry.json"


def root(config: OperatorConfig | None = None) -> Path | None:
    return project_root_for("AgentTools", config or OperatorConfig.load())


def _importable(module: str) -> bool:
    import importlib.util

    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def collect(config: OperatorConfig | None = None) -> dict[str, Any]:
    """AgentTools capabilities available to the agent reading this passdown."""
    config = config or OperatorConfig.load()
    at_root = root(config)
    if at_root is None:
        return {"available": False, "reason": "AgentTools checkout not found on this machine"}

    surfaces: dict[str, dict[str, Any]] = {}
    for name, surface in KNOWN_SURFACES.items():
        surfaces[name] = {
            "module": surface["module"],
            "cli": surface["cli"],
            "importable": _importable(surface["module"]),
            "cli_on_path": bool(surface["cli"]) and tool_available(surface["cli"]),
        }

    # DreamVault publishes an observed capability registry for AgentTools;
    # prefer its record over ours when present.
    dv_root = project_root_for("DreamVault", config)
    observed = read_json(dv_root / CAPABILITY_REGISTRY, {}) if dv_root else {}

    return {
        "available": True,
        "root": str(at_root),
        "surfaces": surfaces,
        "reachable": sorted(
            name for name, s in surfaces.items() if s["importable"] or s["cli_on_path"]
        ),
        "observed_registry": observed.get("capabilities", []) if isinstance(observed, dict) else [],
    }


def provides(capability: str, config: OperatorConfig | None = None) -> dict[str, Any] | None:
    """If AgentTools already provides ``capability``, say where."""
    state = collect(config)
    if not state.get("available"):
        return None
    key = capability.strip().lower().replace("-", "_").replace(" ", "_")
    for name, surface in state["surfaces"].items():
        if key == name or key in name or name in key:
            return {"repo": "AgentTools", "capability": name, **surface}
    for entry in state.get("observed_registry", []):
        if isinstance(entry, dict) and key in str(entry.get("id", "")).lower():
            return {"repo": "AgentTools", "capability": entry.get("id"), **entry}
    return None
