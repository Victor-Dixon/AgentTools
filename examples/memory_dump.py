#!/usr/bin/env python3
"""
Memory Dump Example (Swarm Brain)
=================================

Demonstrates the Shared Memory system:
1. An agent learns something new.
2. It saves this "Learning" to the Brain.
3. Another agent recalls it later.

Usage:
    python examples/memory_dump.py
"""

import sys
from pathlib import Path

# Ensure we can import swarm_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.core.brain import SwarmBrain

def main():
    print("🧠 Initializing Swarm Brain...")
    brain = SwarmBrain()
    
    # 1. Share a learning
    print("\n📝 Agent-1 is sharing a learning...")
    learning = brain.share_learning(
        agent_id="Agent-1",
        category="security",
        title="Don't commit .env files",
        content="We found that committing .env files leads to key leaks. Use .gitignore!",
        tags=["security", "git", "config"]
    )
    print(f"   Saved Learning ID: {learning.id}")

    # 2. Record a decision
    print("\n⚖️  Agent-2 is recording a decision...")
    decision = brain.record_decision(
        agent_id="Agent-2",
        decision="Use PyTest over Unittest",
        context="Unittest is too verbose.",
        outcome="Test suite is 30% smaller",
        success=True
    )
    print(f"   Saved Decision ID: {decision.id}")

    # 3. Recall Information
    print("\n🔍 Agent-3 is searching for 'security'...")
    results = brain.search("security", category="security")
    
    if results:
        for item in results:
            print(f"   Found: {item.title} (by {item.agent_id})")
            print(f"   Content: {item.content}")
    else:
        print("   Nothing found.")

    print("\n✅ Memory interaction complete.")

if __name__ == "__main__":
    main()
