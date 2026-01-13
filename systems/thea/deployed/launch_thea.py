#!/usr/bin/env python3
"""
Thea GUI Launcher
Agent-4 Strategic Implementation
"""

import sys
import os
from pathlib import Path

# Add deployed directory to path
deploy_dir = Path(__file__).parent
sys.path.insert(0, str(deploy_dir))

# Import and run main window
from main_window import main

if __name__ == "__main__":
    print("🚀 Launching Thea MMORPG GUI...")
    print("Agent-4 Strategic Deployment")
    print("=" * 40)
    main()
