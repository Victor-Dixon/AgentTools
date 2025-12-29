#!/usr/bin/env python3
"""
CLI Entry Point - Unified CLI Dispatcher
=========================================

Entry point for running the CLI directly:
    python tools/cli.py [command] [args]
    python tools/cli.py --security-scan [args]

Or via module:
    python -m tools.cli [command] [args]

Supports both:
- Positional commands: security-scan, monitor, validate
- Flag-style commands: --security-scan, --monitor, --validate
"""

import sys
import importlib
from pathlib import Path

# Add workspace root to path for direct execution
workspace_root = Path(__file__).parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))


def run_toolbelt_command(flag: str, remaining_args: list) -> int:
    """Run a command from the toolbelt registry using a flag."""
    from tools.toolbelt_registry import ToolRegistry
    
    registry = ToolRegistry()
    tool = registry.get_tool_for_flag(flag)
    
    if not tool:
        print(f"❌ Unknown flag: {flag}")
        print("\nAvailable toolbelt flags:")
        for tid, cfg in registry.tools.items():
            flags = ", ".join(cfg.get("flags", []))
            print(f"  {flags:40} - {cfg.get('description', tid)[:50]}")
        return 1
    
    try:
        module = importlib.import_module(tool["module"])
        handler = getattr(module, tool.get("main_function", "main"))
        
        # Set up argv for the tool
        original_argv = sys.argv[:]
        try:
            sys.argv = [tool["module"]] + remaining_args
            result = handler()
            return result if isinstance(result, int) else 0
        finally:
            sys.argv = original_argv
    except ImportError as e:
        print(f"❌ Error importing module '{tool['module']}': {e}")
        return 1
    except AttributeError as e:
        print(f"❌ Error: Function not found in module: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point that handles both flag-style and command-style args."""
    # Check if first arg is a toolbelt flag (starts with -- or -)
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        
        # Skip standard flags
        if first_arg in ("--help", "-h", "--list"):
            from tools.cli.dispatchers.unified_dispatcher import main as dispatcher_main
            return dispatcher_main()
        
        # Handle toolbelt flags (--something or -X)
        if first_arg.startswith("-"):
            return run_toolbelt_command(first_arg, sys.argv[2:])
    
    # Fall back to unified dispatcher for positional commands
    from tools.cli.dispatchers.unified_dispatcher import main as dispatcher_main
    return dispatcher_main()


if __name__ == "__main__":
    sys.exit(main())
