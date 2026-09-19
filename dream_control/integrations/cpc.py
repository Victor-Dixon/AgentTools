"""CPC / cliprun adapter: command execution capture as an event producer.

CPC captures are turned into control-plane events *locally*.  External
publishing (Discord and friends) stays behind ``policy.publish``; a capture
never implies a public post.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..config import OperatorConfig, project_root_for
from ..events import record
from ..models import Event
from ..policy.publish import PublishDecision, load_policy, publish_allowed

CPC_TOOLS_RELPATH = Path("runtime") / "tools" / "cpc"


def locate(config: OperatorConfig | None = None) -> dict[str, Any]:
    """Find cliprun and the CPC toolchain in this environment."""
    config = config or OperatorConfig.load()
    cliprun = Path(os.path.expandvars(config.clipboard_command)).expanduser()
    dv_root = project_root_for("DreamVault", config)
    cpc_dir = (dv_root / CPC_TOOLS_RELPATH) if dv_root else None
    return {
        "cliprun": str(cliprun),
        "cliprun_present": cliprun.exists(),
        "cpc_tools_dir": str(cpc_dir) if cpc_dir else None,
        "cpc_tools_present": bool(cpc_dir and cpc_dir.is_dir()),
        "usage": f'"{config.clipboard_command}" "$HOME/<script>.sh"',
    }


def capture_event(
    *,
    actor: str,
    environment: str,
    command: str,
    status: str,
    repo: str | None = None,
    lane: str | None = None,
    capture_path: str | None = None,
    extra: dict[str, Any] | None = None,
) -> Event:
    """Record a CPC capture as an internal control-plane event."""
    return record(
        Event(
            event="cpc_capture_created",
            actor=actor,
            environment=environment,
            repo=repo,
            lane=lane,
            status=status,
            source="cpc",
            payload={"command": command, "capture_path": capture_path, **(extra or {})},
        )
    )


def publication_plan(*, channels: tuple[str, ...] = ("discord", "slack", "x")) -> dict[str, Any]:
    """What a CPC capture is allowed to do, split internal vs external."""
    policy = load_policy()
    decisions: dict[str, PublishDecision] = {c: publish_allowed(c) for c in channels}
    return {
        "internal": {
            "local_capture": policy["local_capture"],
            "control_plane_event": policy["control_plane_event"],
            "cockpit_feed": policy["cockpit_feed"],
        },
        "external": {c: d.to_dict() for c, d in decisions.items()},
        "note": "Internal recording is automatic; external publishing is opt-in per channel.",
    }
