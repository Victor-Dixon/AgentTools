#!/usr/bin/env python3
"""
Swarm Voting Example (Consensus)
================================

Demonstrates the Consensus Engine:
1. An agent proposes a decision.
2. The pack votes on it.
3. The engine determines the outcome based on rules.

Usage:
    python examples/swarm_voting.py
"""

import sys
from pathlib import Path

# Ensure we can import swarm_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.core.consensus import ConsensusEngine, VoteType, ConsensusRule

def main():
    print("🗳️  Initializing Consensus Engine...")
    engine = ConsensusEngine()
    
    # 1. Propose a vote
    proposal = engine.propose(
        proposer="Agent-Architect",
        title="Consolidate all database adapters",
        description="Merge pg_adapter.py and mysql_adapter.py into unified_db.py",
        rule=ConsensusRule.MAJORITY,
        category="architecture"
    )
    proposal_id = proposal.id
    
    print(f"✅ Proposal Created: {proposal_id}")
    print("   Topic: Consolidate all database adapters")
    print("   Rule: Majority Wins")

    # 2. Cast Votes
    print("\n🗳️  Casting Votes...")
    
    # Agent-1 likes it
    engine.vote(
        proposal_id=proposal_id,
        agent_id="Agent-1",
        vote=VoteType.APPROVE,
        reasoning="Reduces code duplication"
    )
    print("   Agent-1 voted YES (Reduces code duplication)")

    # Agent-2 dislikes it
    engine.vote(
        proposal_id=proposal_id,
        agent_id="Agent-2",
        vote=VoteType.REJECT,
        reasoning="Too risky right now"
    )
    print("   Agent-2 voted NO (Too risky right now)")

    # Agent-3 is the tie-breaker
    engine.vote(
        proposal_id=proposal_id,
        agent_id="Agent-3",
        vote=VoteType.APPROVE,
        reasoning="Long term benefit"
    )
    print("   Agent-3 voted YES (Long term benefit)")

    # 3. Check Result
    print("\n📊 Tallying Results...")
    result = engine.resolve(proposal_id)
    
    print(f"   Status: {result['status']}")
    tally = result['tally']
    yes_votes = tally.get('approve', {}).get('count', 0)
    no_votes = tally.get('reject', {}).get('count', 0)
    
    print(f"   YES: {yes_votes}")
    print(f"   NO:  {no_votes}")
    
    if result['status'] == "passed":
        print("\n✅ Motion PASSED! The pack proceeds.")
    else:
        print("\n❌ Motion FAILED or PENDING.")

if __name__ == "__main__":
    main()
