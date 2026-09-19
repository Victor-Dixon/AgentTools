"""AgentTools v2 registry package.

Keep package import dependency-light: registry consumers should not have to import
optional advisor/demo/category modules just to discover a tool. Optional legacy
surfaces are loaded only when explicitly requested.
"""

from __future__ import annotations

from .tool_registry import ToolRegistry, get_tool_registry

__all__ = ["ToolRegistry", "get_tool_registry", "ToolbeltCore", "get_toolbelt_core"]


def __getattr__(name: str):
    """Lazy compatibility exports for the legacy toolbelt core."""
    if name in {"ToolbeltCore", "get_toolbelt_core"}:
        from .toolbelt_core import ToolbeltCore, get_toolbelt_core

        globals()["ToolbeltCore"] = ToolbeltCore
        globals()["get_toolbelt_core"] = get_toolbelt_core
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
