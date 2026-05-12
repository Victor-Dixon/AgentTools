"""
Tool Registry
=============

Dynamic tool registry for agent toolbelt operations.

V2 Compliance: <200 lines
Author: Agent-5 (Business Intelligence Specialist)
"""

import importlib
import json
import logging
from typing import Any

from .adapters.base_adapter import IToolAdapter
from .adapters.error_types import ToolNotFoundError

logger = logging.getLogger(__name__)

# Singleton instance
_registry_instance = None


class ToolRegistry:
    """Dynamic registry for tool discovery and resolution."""

    def __init__(self):
        """Initialize registry."""
        self._cache: dict[str, IToolAdapter] = {}
        self._registry_data = self._load_registry_data()

    def _load_registry_data(self) -> dict[str, list[str]]:
        """Load tool registry data from JSON file."""
        try:
            with open("tools_v2/tool_registry.lock.json", "r") as f:
                data = json.load(f)
                return data.get("tools", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load registry data: {e}")
            return {}

    def _resolve_tool_class(self, tool_name: str) -> type[IToolAdapter]:
        """Resolve tool class by name, loading it if necessary."""
        if tool_name in self._cache:
            return self._cache[tool_name]

        if tool_name not in self._registry_data:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")

        module_path, class_name = self._registry_data[tool_name]

        try:
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)

            self._cache[tool_name] = tool_class
            return tool_class

        except (ImportError, AttributeError) as e:
            raise ToolNotFoundError(f"Could not load tool '{tool_name}': {e}")

    def get_tool_class(self, tool_name: str) -> type[IToolAdapter]:
        """Get tool class by name."""
        return self._resolve_tool_class(tool_name)

    def get_tool(self, tool_name: str) -> IToolAdapter:
        """Instantiate tool adapter by name."""
        tool_class = self.get_tool_class(tool_name)
        return tool_class()

    def resolve(self, tool_name: str) -> type[IToolAdapter]:
        """Resolve tool class by name."""
        return self.get_tool_class(tool_name)

    def list_tools(self) -> list[str]:
        """List all available tools."""
        return sorted(self._registry_data.keys())

    def list_by_category(self, category: str | None = None):
        """List tools grouped by category or return a single category."""

        grouped: dict[str, list[str]] = {}

        for tool_name in self._registry_data.keys():
            try:
                tool = self.get_tool(tool_name)
                cat = tool.get_spec().category

                grouped.setdefault(cat, []).append(tool_name)

            except Exception:
                continue

        grouped = {
            key: sorted(value)
            for key, value in sorted(grouped.items())
        }

        # Legacy compatibility aliases
        msg_tools = sorted([
            tool_name
            for tool_name in self._registry_data.keys()
            if tool_name.startswith("msg.")
        ])

        if msg_tools:
            grouped["msg"] = msg_tools

        if category is None:
            return grouped

        return grouped.get(category, [])

    def export_lock(self, output_path: str) -> None:
        """Export registry lock data to a JSON file."""

        payload = {
            "version": "2.0",
            "count": len(self._registry_data),
            "tool_count": len(self._registry_data),
            "categories": self.get_categories(),
            "tools": self._registry_data,
        }

        with open(output_path, "w") as f:
            json.dump(payload, f, indent=2, sort_keys=True)

    def get_categories(self) -> list[str]:
        """Get all available categories."""
        categories = set()
        for tool_name in self._registry_data.keys():
            try:
                tool = self.get_tool(tool_name)
                categories.add(tool.get_spec().category)
            except Exception:
                continue
        return sorted(categories)

    def clear_cache(self):
        """Clear the tool cache."""
        self._cache.clear()


def get_tool_registry() -> ToolRegistry:
    """Get singleton tool registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ToolRegistry()
    return _registry_instance
