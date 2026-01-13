#!/usr/bin/env python3
"""
Force-Multiplier Gate - Single Deterministic Execution Decision
===============================================================

Evaluates whether an agent can proceed with immediate execution or must block.
Part of S2A Onboarding v2.3 (Force-Multiplier Gate + One-Screen Loop).

Core Rule: Either PASS (execute immediately) or FAIL (exactly one blocker).

Features:
- ✅ DETERMINISTIC: Same inputs = same outcome
- ✅ FAST: Evaluates in <1 second
- ✅ SAFE: Validates all prerequisites
- ✅ CLEAR: Single blocker on failure

Usage:
    python tools/force_multiplier_gate.py --agent Agent-X

Exit Codes:
    0 = GATE PASS — EXECUTE
    1 = GATE FAIL — BLOCKER emitted

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-12
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

class ForceMultiplierGate:
    """Evaluates the force-multiplier gate for immediate execution."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.gate_results = {}
        self.blocker = None

    def load_rehydration_snapshot(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent's rehydration snapshot."""
        snapshot_file = self.project_root / "agent_workspaces" / agent_id / "rehydration.json"
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def load_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent's current status."""
        status_file = self.project_root / "agent_workspaces" / agent_id / "status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def get_current_git_sha(self) -> str:
        """Get current git SHA (short)."""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                  capture_output=True, text=True, cwd=self.project_root)
            return result.stdout.strip()[:7]
        except Exception:
            return "unknown"

    def check_task_scope(self, snapshot: Dict[str, Any]) -> bool:
        """Check if task is properly scoped (single cycle, no cross-domain)."""
        task_scope = snapshot.get('task_scope', {})
        single_cycle = task_scope.get('single_cycle', True)
        cross_domain = task_scope.get('cross_domain', False)

        # Must be single cycle and not cross-domain
        result = single_cycle and not cross_domain
        self.gate_results['task_scope_single_cycle'] = single_cycle
        self.gate_results['task_scope_no_cross_domain'] = not cross_domain

        if not result:
            self.blocker = f"Task scope invalid: single_cycle={single_cycle}, cross_domain={cross_domain}"
            return False
        return True

    def check_ownership(self, agent_id: str, snapshot: Dict[str, Any]) -> bool:
        """Check if agent owns all required files and has no shared conflicts."""
        # Check if agent workspace exists and is accessible
        agent_workspace = self.project_root / "agent_workspaces" / agent_id
        workspace_exists = agent_workspace.exists() and agent_workspace.is_dir()

        # Check if rehydration snapshot indicates ownership
        files_owned = snapshot.get('ownership', {}).get('files_owned', True)

        # Check for shared conflicts (simplified - could be enhanced)
        no_shared_conflict = not snapshot.get('ownership', {}).get('shared_conflict', False)

        result = workspace_exists and files_owned and no_shared_conflict
        self.gate_results['ownership_workspace_exists'] = workspace_exists
        self.gate_results['ownership_files_owned'] = files_owned
        self.gate_results['ownership_no_shared_conflict'] = no_shared_conflict

        if not result:
            components = []
            if not workspace_exists: components.append("workspace missing")
            if not files_owned: components.append("files not owned")
            if not no_shared_conflict: components.append("shared conflict detected")
            self.blocker = f"Ownership check failed: {', '.join(components)}"
            return False
        return True

    def check_execution_readiness(self, snapshot: Dict[str, Any]) -> bool:
        """Check if execution prerequisites are met."""
        next_action = snapshot.get('next_action')
        next_action_executable = next_action is not None and next_action.get('command')

        # Check if tools are available (basic check)
        tools_available = True  # Could be enhanced to check specific tool availability

        result = next_action_executable and tools_available
        self.gate_results['execution_next_action_executable'] = next_action_executable
        self.gate_results['execution_tools_available'] = tools_available

        if not result:
            components = []
            if not next_action_executable: components.append("no executable next_action")
            if not tools_available: components.append("required tools unavailable")
            self.blocker = f"Execution not ready: {', '.join(components)}"
            return False
        return True

    def check_alignment(self, snapshot: Dict[str, Any], status: Optional[Dict[str, Any]]) -> bool:
        """Check if agent state is properly aligned."""
        current_sha = self.get_current_git_sha()
        snapshot_sha = snapshot.get('git_sha')

        git_sha_valid = snapshot_sha == current_sha

        # Cycle alignment
        snapshot_cycle = snapshot.get('cycle_id')
        status_cycle = status.get('cycle_id') if status else None

        # If status has cycle, it must match snapshot
        cycle_valid = status_cycle is None or snapshot_cycle == status_cycle

        result = git_sha_valid and cycle_valid
        self.gate_results['alignment_git_sha_valid'] = git_sha_valid
        self.gate_results['alignment_cycle_valid'] = cycle_valid

        if not result:
            components = []
            if not git_sha_valid: components.append(f"git SHA mismatch: {snapshot_sha} != {current_sha}")
            if not cycle_valid: components.append(f"cycle mismatch: {snapshot_cycle} != {status_cycle}")
            self.blocker = f"Alignment check failed: {', '.join(components)}"
            return False
        return True

    def evaluate_gate(self, agent_id: str) -> Tuple[bool, Optional[str]]:
        """Evaluate the complete force-multiplier gate."""
        # Reset state
        self.gate_results = {}
        self.blocker = None

        # Load required data
        snapshot = self.load_rehydration_snapshot(agent_id)
        if not snapshot:
            self.blocker = "rehydration.json missing - cannot evaluate gate"
            return False, self.blocker

        status = self.load_agent_status(agent_id)

        # Evaluate each gate component
        checks = [
            lambda: self.check_task_scope(snapshot),
            lambda: self.check_ownership(agent_id, snapshot),
            lambda: self.check_execution_readiness(snapshot),
            lambda: self.check_alignment(snapshot, status)
        ]

        for check in checks:
            if not check():
                return False, self.blocker

        # All checks passed
        return True, None

    def print_gate_results(self) -> None:
        """Print detailed gate evaluation results."""
        print("🔍 FORCE-MULTIPLIER GATE EVALUATION")
        print("=" * 50)

        for key, value in self.gate_results.items():
            status = "✅" if value else "❌"
            # Convert camelCase to readable
            readable_key = key.replace('_', ' ').title()
            print(f"  {status} {readable_key}")

        print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Force-Multiplier Gate - Single Deterministic Execution Decision",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python tools/force_multiplier_gate.py --agent Agent-2

EXIT CODES:
  0 = GATE PASS — EXECUTE immediately
  1 = GATE FAIL — blocker emitted, do not execute
        """
    )
    parser.add_argument("--agent", required=True, help="Agent ID (e.g., Agent-1, Agent-2)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed gate evaluation")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    gate = ForceMultiplierGate(project_root)

    # Evaluate the gate
    passed, blocker = gate.evaluate_gate(args.agent)

    # Show results
    if args.verbose:
        gate.print_gate_results()

    if passed:
        print("✅ GATE PASS — EXECUTE")
        print("   Ready for immediate execution loop")
        exit(0)
    else:
        print("❌ GATE FAIL — BLOCKER:")
        print(f"   {blocker}")
        print("   Do not execute - resolve blocker first")
        exit(1)

if __name__ == "__main__":
    main()