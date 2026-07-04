"""
CLI Toolbelt Entry Point
========================

Main entry point for the unified CLI toolbelt.
Routes flags to specific tool modules based on the registry.

Usage:
    python -m tools.toolbelt [FLAG] [ARGS...]
    python -m tools.toolbelt --help
    python -m tools.toolbelt --list
    python -m tools.toolbelt --monitor --help
"""

from __future__ import annotations

import importlib
import inspect
import logging
import sys
from typing import NoReturn

try:
    from tools.toolbelt_registry import ToolRegistry
except ImportError:
    sys.path.append("...")
    from tools.toolbelt_registry import ToolRegistry

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def _invoke_entry_point(entry_point, module_name: str, remaining: list[str]) -> NoReturn:
    """Call tool entry point, passing argv when the function expects it."""
    sys.argv = [module_name] + remaining
    params = list(inspect.signature(entry_point).parameters.values())
    if params and params[0].name in {"argv", "args"}:
        sys.exit(entry_point(remaining))
    sys.exit(entry_point())


def main() -> NoReturn:
    """Main entry point."""
    registry = ToolRegistry()

    if len(sys.argv) < 2:
        print_help(registry)
        sys.exit(1)

    flag = sys.argv[1]

    if flag in {"--help", "-h"}:
        print_help(registry)
        sys.exit(0)

    if flag == "--list":
        print_tools(registry)
        sys.exit(0)

    tool_config = registry.get_tool_for_flag(flag)
    if not tool_config:
        logger.error("Unknown flag: %s", flag)
        print("\nAvailable tools:")
        print_tools(registry)
        sys.exit(1)

    module_name = tool_config["module"]
    function_name = tool_config["main_function"]
    remaining = sys.argv[2:]

    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, function_name):
            logger.error("Entry point '%s' not found in %s", function_name, module_name)
            sys.exit(1)

        entry_point = getattr(module, function_name)
        logger.info("Executing %s (%s)...", tool_config["name"], module_name)
        _invoke_entry_point(entry_point, module_name, remaining)

    except ImportError as exc:
        logger.error("Could not import module %s: %s", module_name, exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Error executing %s: %s", tool_config["name"], exc)
        sys.exit(1)


def print_help(registry: ToolRegistry) -> None:
    """Print help message."""
    print("Swarm CLI Toolbelt")
    print("==================")
    print("Usage: python -m tools.toolbelt [FLAG] [TOOL_ARGS...]")
    print()
    print("Top-level flags:")
    print("  --help, -h     Show this overview")
    print("  --list         List all registered tools with descriptions")
    print()
    print("Per-tool help:")
    print("  python -m tools.toolbelt --monitor --help")
    print("  python -m tools.toolbelt --onboard-soft --help")
    print("  python -m tools.toolbelt --message --help")
    print()
    print("Registered tools (use --list for full detail):")
    for tool in registry.list_tools():
        flags = ", ".join(tool["flags"])
        print(f"  {flags:<22} {tool['description']}")


def print_tools(registry: ToolRegistry) -> None:
    """List all tools."""
    print("Available Tools:")
    for tool in registry.list_tools():
        primary = tool["flags"][0]
        print(f"\n{tool['name']} ({tool['id']})")
        print(f"   Flags: {', '.join(tool['flags'])}")
        print(f"   Module: {tool['module']}.{tool['main_function']}")
        print(f"   Help:   python -m tools.toolbelt {primary} --help")
        print(f"   Desc:   {tool['description']}")


if __name__ == "__main__":
    main()
