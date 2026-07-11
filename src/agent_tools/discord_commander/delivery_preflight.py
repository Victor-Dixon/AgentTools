"""Preflight checks for PyAutoGUI delivery — virtual screen + layout selection."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_LAYOUT_PRIORITY = ("4-agent-1monitor", "8-agent", "4-agent", "2-agent")


def get_virtual_screen() -> tuple[int, int, int, int]:
    """Return (min_x, min_y, max_x, max_y) for the OS virtual desktop."""
    try:
        import ctypes

        user32 = ctypes.windll.user32
        min_x = int(user32.GetSystemMetrics(76))
        min_y = int(user32.GetSystemMetrics(77))
        max_x = min_x + int(user32.GetSystemMetrics(78))
        max_y = min_y + int(user32.GetSystemMetrics(79))
        return min_x, min_y, max_x, max_y
    except Exception:
        return 0, 0, 5000, 5000


def point_in_virtual_screen(x: int, y: int) -> bool:
    min_x, min_y, max_x, max_y = get_virtual_screen()
    return min_x <= x <= max_x and min_y <= y <= max_y


def load_layouts(root: Path) -> dict[str, Any]:
    candidates = (
        root / "runtime" / "config" / "agent_transport" / "cursor_agent_coords.json",
        root / "runtime" / "agent_comms" / "cursor_agent_coords.json",
    )
    for coords_file in candidates:
        if coords_file.is_file():
            return json.loads(coords_file.read_text(encoding="utf-8"))
    return {}


def agent_input_coords(layouts: dict[str, Any], layout: str, agent_id: str) -> Optional[tuple[int, int]]:
    agent = agent_id if agent_id.startswith("Agent-") else f"Agent-{agent_id}"
    block = layouts.get(layout, {}).get(agent)
    if not block:
        return None
    loc = block.get("input_box") or block.get("starter_location_box")
    if not loc:
        return None
    return int(loc["x"]), int(loc["y"])


def layout_has_in_bounds_agent(layouts: dict[str, Any], layout: str, agent_id: str) -> bool:
    coords = agent_input_coords(layouts, layout, agent_id)
    if coords is None:
        return False
    return point_in_virtual_screen(coords[0], coords[1])


def resolve_layout_for_agent(root: Path, agent_id: str) -> tuple[str, Optional[str]]:
    """Pick a layout mode where agent input coords are on-screen.

    Returns (layout_mode, warning_message).
    """
    env_layout = os.environ.get("AGENT_GAS_LAYOUT_MODE", "").strip() or "4-agent-1monitor"
    layouts = load_layouts(root)
    if not layouts:
        return env_layout, "coords file missing; cannot preflight layout"

    if layout_has_in_bounds_agent(layouts, env_layout, agent_id):
        return env_layout, None

    env_warning: Optional[str] = None
    if env_layout in layouts:
        env_warning = (
            f"AGENT_GAS_LAYOUT_MODE={env_layout} has off-screen coords for {agent_id} on "
            f"virtual screen {get_virtual_screen()}. Re-calibrate: "
            f"python D:\\DreamVault\\runtime\\scripts\\set_agent_coords.py --layout {env_layout}"
        )

    candidates: list[str] = []
    for layout in _LAYOUT_PRIORITY:
        if layout not in candidates:
            candidates.append(layout)
    for layout in layouts:
        if layout not in candidates:
            candidates.append(layout)

    for layout in candidates:
        if layout == env_layout:
            continue
        if layout_has_in_bounds_agent(layouts, layout, agent_id):
            return (
                layout,
                env_warning
                or f"AGENT_GAS_LAYOUT_MODE={env_layout} unusable for {agent_id}; using {layout} instead",
            )

    return env_layout, env_warning or (
        f"No layout has on-screen input coords for {agent_id} on virtual screen "
        f"{get_virtual_screen()}. Re-calibrate with DreamVault set_agent_coords.py"
    )


@dataclass
class PyAutoGUIReadiness:
    """Outcome of pre-send PyAutoGUI readiness gate."""

    ready: bool
    coords_root: Path
    layout_mode: str
    error_code: Optional[str] = None
    detail: Optional[str] = None
    warnings: list[str] = field(default_factory=list)


def validate_pyautogui_readiness(
    agent_id: str,
    *,
    coords_root: Path | None = None,
) -> PyAutoGUIReadiness:
    """Validate live injection + coords before !message send (fail fast)."""
    from .messaging_roots import resolve_coords_root

    root = coords_root or resolve_coords_root()
    agent = agent_id if agent_id.startswith("Agent-") else f"Agent-{agent_id}"

    if os.environ.get("ALLOW_LIVE_CURSOR_INJECTION", "").strip() != "1":
        return PyAutoGUIReadiness(
            ready=False,
            coords_root=root,
            layout_mode=os.environ.get("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor"),
            error_code="LIVE_INJECTION_DISABLED",
            detail="Set ALLOW_LIVE_CURSOR_INJECTION=1 for live PyAutoGUI delivery",
        )

    layouts = load_layouts(root)
    if not layouts:
        return PyAutoGUIReadiness(
            ready=False,
            coords_root=root,
            layout_mode=os.environ.get("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor"),
            error_code="COORDS_MISSING",
            detail=f"No cursor_agent_coords.json under {root}",
        )

    layout, warning = resolve_layout_for_agent(root, agent)
    warnings = [warning] if warning else []
    if not layout_has_in_bounds_agent(layouts, layout, agent):
        coords = agent_input_coords(layouts, layout, agent)
        xy = f"({coords[0]}, {coords[1]})" if coords else "missing"
        return PyAutoGUIReadiness(
            ready=False,
            coords_root=root,
            layout_mode=layout,
            error_code="COORDS_OUT_OF_BOUNDS",
            detail=f"{agent} input {xy} off-screen for layout {layout}. Re-calibrate coords.",
            warnings=warnings,
        )

    if agent not in layouts.get(layout, {}):
        return PyAutoGUIReadiness(
            ready=False,
            coords_root=root,
            layout_mode=layout,
            error_code="AGENT_NOT_IN_LAYOUT",
            detail=f"{agent} not in layout {layout} at {root}",
            warnings=warnings,
        )

    return PyAutoGUIReadiness(
        ready=True,
        coords_root=root,
        layout_mode=layout,
        warnings=warnings,
    )
