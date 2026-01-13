#!/usr/bin/env python3
"""
Integration tests for swarm-mcp package
Tests end-to-end functionality of the swarm coordination system
"""

import tempfile
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_full_swarm_workflow():
    """Test a complete swarm workflow from task assignment to completion"""

    with tempfile.TemporaryDirectory() as temp_dir:
        print("🧪 Testing full swarm workflow...")

        try:
            # Import all components
            from swarm_mcp.core.coordinator import PackCoordinator
            from swarm_mcp.core.consensus import ConsensusEngine, VoteType, ConsensusRule
            from swarm_mcp.core.conflict import ConflictDetector
            from swarm_mcp.core.agent_dna import AgentDNA
            from swarm_mcp.core.work_proof import WorkProofSystem
            from swarm_mcp.core.pattern_miner import PatternMiner

            print("✅ All core modules imported")

            # Initialize components
            coordinator = PackCoordinator(wolves=["agent-1", "agent-2", "agent-3"], den=temp_dir)
            consensus = ConsensusEngine(storage_dir=os.path.join(temp_dir, "consensus"))
            detector = ConflictDetector(storage_dir=os.path.join(temp_dir, "conflicts"))
            dna = AgentDNA(storage_dir=os.path.join(temp_dir, "dna"))
            proof_system = WorkProofSystem(storage_dir=os.path.join(temp_dir, "proofs"))
            miner = PatternMiner(storage_dir=os.path.join(temp_dir, "patterns"))

            print("✅ All components initialized")

            # Test workflow: Agent declares intent, gets task, works on it, proves completion

            # Step 1: Agent declares what they're working on
            intent, conflicts = detector.declare_intent(
                agent_id="agent-1",
                description="Fix authentication bug",
                files=["src/auth.py", "src/login.py"],
                keywords=["auth", "login", "token"]
            )
            assert len(conflicts) == 0, "Should be no conflicts for new work"
            print("✅ Conflict detection works")

            # Step 2: Get consensus on approach
            proposal = consensus.propose(
                proposer="agent-1",
                title="Use JWT tokens for auth",
                description="JWT provides stateless authentication",
                category="security",
                rule=ConsensusRule.MAJORITY
            )

            # Other agents vote
            consensus.vote(proposal.id, "agent-2", VoteType.APPROVE, "Good choice")
            consensus.vote(proposal.id, "agent-3", VoteType.APPROVE, "Agreed")

            result = consensus.resolve(proposal.id, force=True)
            assert result["passed"] == True, "Majority vote should pass"
            print("✅ Consensus voting works")

            # Step 3: Record work in AgentDNA
            dna.record_task(
                agent_id="agent-1",
                category="security",
                description="Implemented JWT authentication",
                files=["src/auth.py", "src/tokens.py"],
                duration_minutes=45,
                success=True,
                quality_score=0.95
            )

            # Check if agent-1 is now recognized as good at security
            best_agent, confidence = dna.find_best_agent(category="security")
            assert best_agent == "agent-1", "Should find agent-1 as best for security"
            assert confidence > 0.5, "Should have reasonable confidence"
            print("✅ Agent DNA learning works")

            # Step 4: Create work proof
            commitment = proof_system.commit(
                agent_id="agent-1",
                task="Implement JWT auth",
                files=["src/auth.py", "src/tokens.py"]
            )

            # Simulate work by creating dummy files
            os.makedirs(os.path.join(temp_dir, "src"), exist_ok=True)
            with open(os.path.join(temp_dir, "src", "auth.py"), "w") as f:
                f.write("# JWT Authentication implemented")
            with open(os.path.join(temp_dir, "src", "tokens.py"), "w") as f:
                f.write("# Token management")

            proof = proof_system.prove(commitment.id)
            assert proof.valid == True, "Proof should be valid"
            print("✅ Work proof system works")

            # Step 5: Record pattern for future use
            miner.record_event(
                event_type="task_complete",
                agents=["agent-1"],
                context={"category": "security", "approach": "jwt"},
                outcome="success",
                duration_minutes=45,
                quality_score=0.95
            )

            suggestions = miner.suggest(context={"category": "security"})
            assert len(suggestions) > 0, "Should find suggestions"
            print("✅ Pattern mining works")

            # Step 6: Complete work and free conflict lock
            detector.complete_work("agent-1")
            print("✅ Conflict resolution works")

            print("🎉 Full swarm workflow test PASSED!")
            return True

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_mcp_server_integration():
    """Test MCP server basic functionality"""

    print("\n🔌 Testing MCP server integration...")

    try:
        # Test that all MCP servers can be imported
        from swarm_mcp.servers import messaging, memory, tasks, control, tools

        # Test that they have the required MCP interface
        servers = [messaging, memory, tasks, control, tools]
        for server in servers:
            assert hasattr(server, 'main'), f"Server {server.__name__} missing main function"

        print("✅ All MCP servers have required interface")
        return True

    except Exception as e:
        print(f"❌ MCP server integration failed: {e}")
        return False

def test_cli_integration():
    """Test CLI basic functionality"""

    print("\n🖥️  Testing CLI integration...")

    try:
        from swarm_mcp.cli import main

        # CLI should be importable
        assert callable(main), "CLI main should be callable"

        print("✅ CLI is importable and callable")
        return True

    except Exception as e:
        print(f"❌ CLI integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Swarm MCP Integration Tests")
    print("=" * 50)

    tests = [
        test_full_swarm_workflow,
        test_mcp_server_integration,
        test_cli_integration
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Integration Test Results: {passed}/{len(tests)} passed")

    if passed == len(tests):
        print("✅ ALL INTEGRATION TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME INTEGRATION TESTS FAILED!")
        sys.exit(1)