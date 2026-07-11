"""Legacy CLI module shim package for tooling expecting `tools/cli.py`.

This package preserves the historical import surface while routing execution to
the unified CLI dispatcher.
"""

from tools.cli.dispatchers.unified_dispatcher import UnifiedCLIDispatcher
from tools.cli.main import main

__all__ = ["main", "UnifiedCLIDispatcher"]
