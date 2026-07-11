"""Load DreamVault discord modules without importing dreamvault package root."""

from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path
from types import ModuleType
from typing import Any


def dreamvault_root() -> Path:
    raw = os.getenv("DREAMVAULT_ROOT", "").strip()
    if not raw:
        raise RuntimeError("DREAMVAULT_ROOT is not set")
    return Path(raw)


def _ensure_dreamvault_discord_namespace() -> None:
    if "dreamvault" not in sys.modules:
        sys.modules["dreamvault"] = types.ModuleType("dreamvault")
    if "dreamvault.discord" not in sys.modules:
        sys.modules["dreamvault.discord"] = types.ModuleType("dreamvault.discord")


def load_module(name: str, relative_path: str, *, register_as: str | None = None) -> ModuleType:
    path = dreamvault_root() / relative_path
    if not path.is_file():
        raise FileNotFoundError(path)
    module_name = register_as or name
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_flowr_store() -> dict[str, Any]:
    mod = load_module(
        "dreamvault.discord.flowr_timeblock_store",
        "src/dreamvault/discord/flowr_timeblock_store.py",
        register_as="dreamvault.discord.flowr_timeblock_store",
    )
    return {
        "add_block": mod.add_block,
        "build_panel_summary": mod.build_panel_summary,
        "clear_blocks": mod.clear_blocks,
        "complete_active_block": mod.complete_active_block,
        "format_blocks_summary": mod.format_blocks_summary,
        "load_state": mod.load_state,
        "pause_timer": mod.pause_timer,
        "planner_focus_lines": mod.planner_focus_lines,
        "reset_timer": mod.reset_timer,
        "start_focus_timer": mod.start_focus_timer,
    }


def load_daily_command_hub_live() -> ModuleType:
    _ensure_dreamvault_discord_namespace()
    hub_view = load_module(
        "dreamvault.discord.daily_command_hub_view",
        "src/dreamvault/discord/daily_command_hub_view.py",
        register_as="dreamvault.discord.daily_command_hub_view",
    )
    sys.modules["dreamvault.discord.daily_command_hub_view"] = hub_view
    return load_module(
        "dreamvault.discord.daily_command_hub_live_view",
        "src/dreamvault/discord/daily_command_hub_live_view.py",
        register_as="dreamvault.discord.daily_command_hub_live_view",
    )
