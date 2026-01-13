#!/usr/bin/env python3
"""
Messaging CLI Wrapper for Agent Tools
======================================

Wrapper script that properly calls the messaging CLI from Agent_Cellphone_V2_Repository.
This fixes the "ModuleNotFoundError: No module named 'src.services'" error.

Usage: python tools/messaging_cli_wrapper.py [args...]
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Path to the Agent_Cellphone_V2_Repository
    cellphone_repo = Path("D:/Agent_Cellphone_V2_Repository")

    if not cellphone_repo.exists():
        print("❌ ERROR: Agent_Cellphone_V2_Repository not found at D:/Agent_Cellphone_V2_Repository", file=sys.stderr)
        print("   Please ensure the repository is cloned to the correct location.", file=sys.stderr)
        return 1

    # Change to cellphone repo directory and run the messaging CLI
    try:
        os.chdir(cellphone_repo)

        # Prepare the command to run the messaging CLI from cellphone repo
        cmd = [sys.executable, "-m", "src.services.messaging_cli"] + sys.argv[1:]

        # Run the command
        result = subprocess.run(cmd, capture_output=False, text=True)

        return result.returncode

    except Exception as e:
        print(f"❌ ERROR: Failed to execute messaging CLI: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())