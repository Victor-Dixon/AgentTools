#!/usr/bin/env python3
"""Simple test to check if the consensus engine works"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from swarm_mcp.core.consensus import ConsensusEngine, VoteType, ConsensusRule

    print("Testing ConsensusEngine...")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        engine = ConsensusEngine(storage_dir=tmp_dir)

        # Create proposal
        proposal = engine.propose(
            proposer="agent-1",
            title="Use Python",
            description="Python is good",
            category="tech",
            rule=ConsensusRule.MAJORITY
        )

        print(f"✅ Proposal created: {proposal.id}")
        print(f"   Status: {proposal.status}")
        print(f"   Proposer: {proposal.proposer}")

        # Vote
        engine.vote(proposal.id, "agent-2", VoteType.APPROVE, "I like it")
        engine.vote(proposal.id, "agent-3", VoteType.REJECT, "I prefer Go")

        # Check tally
        tally = engine.get_tally(proposal.id)
        print(f"✅ Votes recorded: {tally['tally']['approve']['count']} approve, {tally['tally']['reject']['count']} reject")

        print("✅ ConsensusEngine test passed!")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()