#!/usr/bin/env python3
"""
Swarm Activation Launcher
=========================

Ignites the Swarm Ecosystem.
Starts necessary MCP servers and initializes the coordination loop.

Usage:
    python start_swarm.py
"""

import sys
import time
import subprocess
from pathlib import Path

def print_banner():
    print("""
    🐺 WE ARE SWARM 🐺
    ==================
    Initializing Autonomous Coordination System...
    """)

def check_requirements():
    print("🔍 Checking System Status...")
    # Check if swarm-mcp is installed
    try:
        import swarm_mcp
        print(f"   ✅ swarm-mcp package found (v{swarm_mcp.__version__ if hasattr(swarm_mcp, '__version__') else 'dev'})")
    except ImportError:
        print("   ❌ swarm-mcp package NOT installed. Run 'pip install -e .'")
        sys.exit(1)

    # Check directories
    dirs = ["swarm_messages", "swarm_memory", "swarm_consensus", "swarm_dna"]
    for d in dirs:
        p = Path(d)
        if not p.exists():
            p.mkdir()
            print(f"   ✨ Created territory: {d}")
        else:
            print(f"   ✅ Territory exists: {d}")

def main():
    print_banner()
    check_requirements()
    
    print("\n🚀 SWARM READY FOR ACTIVATION")
    print("-" * 40)
    
    print("To activate the Swarm, configure your Agent (Cursor/Claude) with:")
    
    config = """
    {
      "mcpServers": {
        "swarm-tools": { "command": "swarm-tools-server" },
        "swarm-memory": { "command": "swarm-memory-server" },
        "swarm-messaging": { "command": "swarm-messaging-server" },
        "swarm-tasks": { "command": "swarm-tasks-server" },
        "swarm-control": { "command": "swarm-control-server" }
      }
    }
    """
    print(config)
    
    print("-" * 40)
    print("Once connected, your Agent can:")
    print("1. Monitor the system:  run_monitor()")
    print("2. Check for tasks:     list_tasks()")
    print("3. Coordinate:          send_message('Captain', 'Ready')")
    print("\n🐺 The pack is waiting.")

if __name__ == "__main__":
    main()
