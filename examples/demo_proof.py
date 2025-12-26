#!/usr/bin/env python3
"""
Work Proof Demo
===============

Demonstrates the WorkProof System.
Scenario: An agent claims to have fixed a bug, but must prove it.

Usage:
    python examples/demo_proof.py
"""

import sys
import time
from pathlib import Path

# Ensure we can import swarm_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.core.work_proof import WorkProofSystem

def main():
    print("📜 Initializing Work Proof System...")
    proof_sys = WorkProofSystem()
    
    # 1. Agent claims work
    print("\n🐺 Agent-1 starts task: Fix Issue #123...")
    
    try:
        # Step 1: Commit to the work
        commitment = proof_sys.commit(
            agent_id="Agent-1",
            task="Fix authentication bug",
            files=["examples/demo_proof.py"]
        )
        print(f"   ✅ Commitment Created: {commitment.id}")
        
        # Step 2: Simulate work (we'll just wait a second)
        print("   🔨 Agent-1 is working...")
        time.sleep(1)
        
        # Step 3: Generate proof
        print("   📝 Generating proof...")
        proof = proof_sys.prove(commitment.id)
        
        print("   ✅ Proof Generated!")
        print(f"      ID: {proof.commitment_id}")
        print(f"      Duration: {proof.duration_seconds:.2f}s")
        print(f"      Hash: {proof.proof_hash[:10]}...")
        print(f"      Valid: {proof.valid}")
        if not proof.valid:
            print(f"      Issues: {proof.validation_notes}")
        
        # 2. Verify proof
        print("\n🔍 Verifying proof (Public Verification)...")
        is_valid, issues = proof_sys.verify(proof)
        
        if is_valid:
            print("   ✅ Proof Verified: Files exist and hash matches.")
        else:
            print(f"   ❌ Proof Invalid: {issues}")
            
    except Exception as e:
        print(f"   ⚠️  Demo error: {e}")

if __name__ == "__main__":
    main()
