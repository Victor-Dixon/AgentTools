#!/usr/bin/env python3
"""
Validate Closure Next Action - Enforce Singularity Rule
======================================================

Validates that closure ends with exactly one executable next_action OR terminal state.
Part of S2A Onboarding v2.3 closure enforcement.

Singularity Rule:
> Closure MUST end with exactly one executable next_action OR "terminal": true

This guarantees onboarding never has to "decide what's next" - the decision is pre-made.

Usage:
    python tools/validate_closure_next_action.py --agent Agent-X

Exit Codes:
    0 = VALID: next_action singularity enforced
    1 = INVALID: closure violates singularity rule

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-12
"""

import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

class ClosureNextActionValidator:
    """Validates closure next_action singularity."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def load_rehydration_snapshot(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent's rehydration snapshot."""
        snapshot_file = self.project_root / "agent_workspaces" / agent_id / "rehydration.json"
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def validate_singularity_rule(self, agent_id: str) -> Tuple[bool, str]:
        """Validate the next_action singularity rule."""
        snapshot = self.load_rehydration_snapshot(agent_id)

        if not snapshot:
            return False, "rehydration.json missing - cannot validate closure"

        # Check for terminal state
        if snapshot.get('terminal', False):
            # Terminal state is valid - no next action needed
            if snapshot.get('next_action') is None:
                return True, "terminal state valid - no next_action required"
            else:
                return False, "terminal state set but next_action still present"

        # Not terminal - must have exactly one executable next_action
        next_action = snapshot.get('next_action')

        if next_action is None:
            return False, "non-terminal state requires next_action"

        if not isinstance(next_action, dict):
            return False, "next_action must be a dictionary object"

        # Required fields for executable next_action
        required_fields = ['command', 'description', 'expected_output']
        missing_fields = [field for field in required_fields if field not in next_action]

        if missing_fields:
            return False, f"next_action missing required fields: {', '.join(missing_fields)}"

        command = next_action.get('command', '').strip()
        if not command:
            return False, "next_action command cannot be empty"

        description = next_action.get('description', '').strip()
        if not description:
            return False, "next_action description cannot be empty"

        # Additional validation could check command syntax, but keep it simple for now

        return True, "next_action singularity validated"

def main():
    parser = argparse.ArgumentParser(
        description="Validate Closure Next Action - Enforce Singularity Rule",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SINGULARITY RULE:
  Closure MUST end with exactly one executable next_action OR "terminal": true

VALID STATES:
  ✅ {"terminal": true, "next_action": null}  // Terminal state
  ✅ {"terminal": false, "next_action": {...}} // Single executable action
  ❌ {"terminal": false, "next_action": null} // Invalid - no action
  ❌ {"terminal": true, "next_action": {...}} // Invalid - terminal + action
  ❌ Multiple next_actions // Invalid - not singular

EXIT CODES:
  0 = VALID: singularity rule enforced
  1 = INVALID: closure violates singularity rule
        """
    )
    parser.add_argument("--agent", required=True, help="Agent ID to validate")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    validator = ClosureNextActionValidator(project_root)

    valid, message = validator.validate_singularity_rule(args.agent)

    if valid:
        print("✅ CLOSURE VALID:")
        print(f"   {message}")
        exit(0)
    else:
        print("❌ CLOSURE INVALID:")
        print(f"   {message}")
        print("\n🔧 FIX REQUIRED:")
        print("   1. Run: python tools/rehydration_manager.py --agent {args.agent} --snapshot")
        print("   2. Add exactly one next_action OR set 'terminal': true")
        print("   3. Re-run validation")
        exit(1)

if __name__ == "__main__":
    main()