#!/usr/bin/env python3
"""
CLI Package Entry Point
=======================

Allows running the CLI as: python -m tools.cli [command] [args]
"""

import sys
from tools.cli.dispatchers.unified_dispatcher import main

if __name__ == "__main__":
    sys.exit(main())
