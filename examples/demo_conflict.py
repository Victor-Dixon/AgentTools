#!/usr/bin/env python3
"""
Conflict Detection Demo
=======================

Demonstrates the ConflictDetector module.
Scenario: Two agents try to modify the same file at the same time.

Usage:
    python examples/demo_conflict.py
"""

import sys
import time
from pathlib import Path

# Ensure we can import swarm_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.core.conflict import ConflictDetector, WorkIntent, ConflictSeverity

def main():
    print("🛡️  Initializing Conflict Detector...")
    detector = ConflictDetector()
    
    # 1. Agent A declares intent
    print("\n🐺 Agent-A is starting work...")
    # declare_intent returns (intent, conflicts)
    intent_a, conflicts_a = detector.declare_intent(
        agent_id="Agent-A",
        files=["src/auth.py", "src/login.py"],
        description="Refactoring auth logic",
        keywords=["auth", "login"]
    )
    
    if not conflicts_a:
        print("   ✅ Agent-A granted access to: src/auth.py, src/login.py")
    else:
        print(f"   ❌ Access DENIED: {conflicts_a[0].reason}")

    # 2. Agent B tries to touch overlapping file
    print("\n🐺 Agent-B is starting work...")
    print(f"   Agent-B requesting: src/login.py, src/ui.py")
    
    # Check before declaring (best practice)
    conflicts_b = detector.check_conflicts(
        agent_id="Agent-B",
        files=["src/login.py", "src/ui.py"],
        keywords=["login", "ui"]
    )
    
    if conflicts_b:
        print(f"   ❌ CONFLICT DETECTED!")
        conflict = conflicts_b[0]
        print(f"      Severity: {conflict.severity.value}")
        print(f"      With: {conflict.agents}")
        print(f"      Reason: {conflict.reason}")
        print("   ⛔ Agent-B must wait or coordinate with Agent-A.")
    else:
        detector.declare_intent(
            agent_id="Agent-B",
            files=["src/login.py", "src/ui.py"],
            description="Updating login UI"
        )
        print("   ✅ Agent-B granted access.")

    # 3. Agent A finishes
    print("\n🐺 Agent-A finishes work.")
    detector.complete_work("Agent-A")
    print("   ✅ Agent-A released locks.")

    # 4. Agent B tries again
    print("\n🐺 Agent-B retries...")
    conflicts_retry = detector.check_conflicts(
        agent_id="Agent-B",
        files=["src/login.py", "src/ui.py"]
    )
    
    if not conflicts_retry:
        detector.declare_intent(
            agent_id="Agent-B",
            files=["src/login.py", "src/ui.py"],
            description="Updating login UI"
        )
        print("   ✅ Agent-B granted access to: src/login.py")
    else:
        print("   ❌ Still blocked.")

if __name__ == "__main__":
    main()
