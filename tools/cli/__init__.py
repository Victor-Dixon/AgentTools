"""
CLI Tools Package - Unified CLI Framework
==========================================

Provides the unified CLI dispatcher for all tools.

Usage:
    from tools.cli import main
    main()

Or via command line:
    python -m tools.cli [command] [args]
    python -m tools.cli --security-scan [args]

Supports both:
- Positional commands: security-scan, monitor, validate
- Flag-style commands: --security-scan, --monitor, --validate
"""

import sys
from pathlib import Path

# Ensure workspace root is in path
_workspace_root = Path(__file__).parent.parent.parent
if str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

# Import the unified main that handles both styles
# We need to import from the cli.py file in parent, but that causes circular import
# So we define main here directly
from tools.cli.dispatchers.unified_dispatcher import main as _dispatcher_main
from tools.cli.dispatchers.unified_dispatcher import UnifiedCLIDispatcher


def main() -> int:
    """Main entry point that handles both flag-style and command-style args."""
    import importlib
    
    # Check if first arg is a toolbelt flag (starts with -- or -)
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        
        # Skip standard flags
        if first_arg in ("--help", "-h", "--list"):
            return _dispatcher_main()
        
        # Handle toolbelt flags (--something or -X)
        if first_arg.startswith("-"):
            from tools.toolbelt_registry import ToolRegistry
            
            registry = ToolRegistry()
            tool = registry.get_tool_for_flag(first_arg)
            
            if not tool:
                # Fall back to dispatcher (might be a dispatcher flag)
                return _dispatcher_main()
            
            try:
                module = importlib.import_module(tool["module"])
                handler = getattr(module, tool.get("main_function", "main"))
                
                original_argv = sys.argv[:]
                try:
                    sys.argv = [tool["module"]] + sys.argv[2:]
                    result = handler()
                    return result if isinstance(result, int) else 0
                finally:
                    sys.argv = original_argv
            except Exception as e:
                print(f"❌ Error executing {first_arg}: {e}")
                return 1
    
    # Fall back to unified dispatcher for positional commands
    return _dispatcher_main()


__all__ = ["main", "UnifiedCLIDispatcher"]
