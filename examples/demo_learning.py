#!/usr/bin/env python3
"""
Pattern Learning Demo
=====================

Demonstrates the PatternMiner module.
Scenario: The system observes agents and detects a recurring workflow.

Usage:
    python examples/demo_learning.py
"""

import sys
from pathlib import Path

# Ensure we can import swarm_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.core.pattern_miner import PatternMiner, CoordinationEvent

def main():
    print("🧠 Initializing Pattern Miner...")
    miner = PatternMiner()
    
    print("\n📜 Recording interaction history...")
    
    # Simulate a pattern occurring 3 times:
    # 1. QA finds bug
    # 2. Dev fixes bug
    # 3. QA verifies fix
    
    for i in range(3):
        print(f"   Iteration {i+1}...")
        
        # QA finds bug
        miner.record_event(
            event_type="report_bug",
            agents=["Agent-QA"],
            context={"category": "qa", "component": "login"},
            outcome="success",
            quality_score=1.0
        )
        
        # Dev fixes bug
        miner.record_event(
            event_type="fix_bug",
            agents=["Agent-Dev"],
            context={"category": "dev", "files": ["login.py"]},
            outcome="success",
            quality_score=1.0
        )
        
        # QA verifies
        miner.record_event(
            event_type="verify_fix",
            agents=["Agent-QA"],
            context={"category": "qa", "status": "passed"},
            outcome="success",
            quality_score=1.0
        )

    # Analyze
    print("\n🔍 Mining for patterns...")
    patterns = miner.get_patterns()
    
    if patterns:
        print(f"   ✅ Found {len(patterns)} recurring patterns!")
        for p in patterns:
            print(f"\n   🔄 Pattern: {p.name}")
            print(f"      Type: {p.pattern_type}")
            print(f"      Conditions: {p.conditions}")
            print(f"      Success Rate: {p.success_rate:.2f}")
            print(f"      Occurrences: {p.occurrence_count}")
    else:
        print("   No patterns found (need more data or higher frequency).")
        print("   (Note: Pattern miner usually requires >5 events to start finding patterns)")

if __name__ == "__main__":
    main()
