#!/usr/bin/env python3
"""
One-Screen Execution Loop - Automated Task Execution
===================================================

Implements the v2.3 execution loop: RUN → VALIDATE → UPDATE → LOOP.
Part of S2A Onboarding v2.3 (Force-Multiplier Gate + One-Screen Loop).

Features:
- ✅ AUTOMATED: Executes until completion or blocker
- ✅ SAFE: Validates each step before proceeding
- ✅ ATOMIC: Updates state after each successful execution
- ✅ TERMINAL: Transitions to closure when done

Execution Loop:
RUN next_action.command
↓
VALIDATE expected_outcome
↓
UPDATE rehydration.json
↓
IF next_action exists → LOOP
ELSE → TRANSITION TO CLOSURE

Usage:
    python tools/one_screen_execution_loop.py --agent Agent-X

Exit Codes:
    0 = EXECUTION COMPLETE → ready for closure
    1 = BLOCKER ENCOUNTERED → escalation needed
    2 = EXECUTION FAILED → manual intervention required

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-12
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class OneScreenExecutionLoop:
    """Implements the automated one-screen execution loop."""

    def __init__(self, project_root: Path, agent_id: str):
        self.project_root = project_root
        self.agent_id = agent_id
        self.execution_count = 0
        self.max_executions = 10  # Safety limit

    def load_rehydration_snapshot(self) -> Optional[Dict[str, Any]]:
        """Load current rehydration snapshot."""
        snapshot_file = self.project_root / "agent_workspaces" / self.agent_id / "rehydration.json"
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Failed to load rehydration snapshot: {e}")
                return None
        print("❌ Rehydration snapshot not found")
        return None

    def save_rehydration_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Save updated rehydration snapshot."""
        snapshot_file = self.project_root / "agent_workspaces" / self.agent_id / "rehydration.json"
        try:
            snapshot_file.parent.mkdir(parents=True, exist_ok=True)
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to save rehydration snapshot: {e}")
            return False

    def execute_command(self, command: str, timeout: int = 300) -> Tuple[bool, str, str]:
        """Execute a command and capture output."""
        try:
            print(f"🏃 Executing: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )

            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if success:
                print(f"✅ Command succeeded")
                if stdout:
                    print(f"📄 Output: {stdout[:200]}{'...' if len(stdout) > 200 else ''}")
            else:
                print(f"❌ Command failed (exit code: {result.returncode})")
                if stderr:
                    print(f"🚨 Error: {stderr[:200]}{'...' if len(stderr) > 200 else ''}")

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            print(f"⏰ {error_msg}")
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Command execution error: {e}"
            print(f"💥 {error_msg}")
            return False, "", error_msg

    def validate_output(self, stdout: str, stderr: str, expected_output: str) -> bool:
        """Validate command output against expected pattern."""
        if not expected_output:
            # If no expected output specified, any success is valid
            return True

        # Simple string matching (could be enhanced with regex)
        output_combined = (stdout + " " + stderr).lower()
        expected_lower = expected_output.lower()

        # Check if expected output appears in combined output
        if expected_lower in output_combined:
            print(f"✅ Validation passed: found '{expected_output}' in output")
            return True
        else:
            print(f"❌ Validation failed: expected '{expected_output}' not found in output")
            print(f"   Actual output: {output_combined[:200]}...")
            return False

    def update_snapshot_after_execution(self, snapshot: Dict[str, Any],
                                      command: str, success: bool) -> Dict[str, Any]:
        """Update rehydration snapshot after command execution."""
        from datetime import datetime, timezone

        # Update execution tracking
        if 'execution_history' not in snapshot:
            snapshot['execution_history'] = []

        execution_record = {
            'command': command,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'success': success,
            'sequence': self.execution_count
        }

        snapshot['execution_history'].append(execution_record)

        # Update task progress
        current_task = snapshot.get('current_task', {})
        if current_task:
            if 'execution_count' not in current_task:
                current_task['execution_count'] = 0
            current_task['execution_count'] += 1

            if success:
                current_task['last_success'] = datetime.now(timezone.utc).isoformat()
            else:
                current_task['last_failure'] = datetime.now(timezone.utc).isoformat()
                current_task['consecutive_failures'] = current_task.get('consecutive_failures', 0) + 1

        # Check if we need a new next_action
        if success and snapshot.get('next_action'):
            # This is where you would determine the next action
            # For now, we'll clear it to indicate completion
            # In a real implementation, this would be determined by the task logic
            snapshot['next_action'] = None
            snapshot['resume_ready'] = False
            snapshot['terminal'] = True

        snapshot['last_updated'] = datetime.now(timezone.utc).isoformat()
        return snapshot

    def run_execution_loop(self) -> int:
        """Run the complete one-screen execution loop."""
        print("🎯 ONE-SCREEN EXECUTION LOOP STARTED")
        print("=" * 50)

        # Load initial state
        snapshot = self.load_rehydration_snapshot()
        if not snapshot:
            print("❌ Cannot start execution loop - no rehydration snapshot")
            return 1  # Blocker

        # Check if there's a next action to execute
        next_action = snapshot.get('next_action')
        if not next_action:
            print("✅ No next action found - execution loop complete")
            print("   Ready for closure transition")
            return 0  # Complete

        print(f"📋 Current task: {snapshot.get('current_task', {}).get('description', 'Unknown')}")
        print(f"🎬 Next action: {next_action.get('description', 'Execute command')}")

        # Execute the loop
        while next_action and self.execution_count < self.max_executions:
            self.execution_count += 1

            print(f"\n🔄 EXECUTION STEP {self.execution_count}")
            print("-" * 30)

            command = next_action.get('command')
            expected_output = next_action.get('expected_output', '')
            timeout = next_action.get('timeout_seconds', 300)

            if not command:
                print("❌ No command specified in next_action")
                return 2  # Execution failed

            # EXECUTE
            success, stdout, stderr = self.execute_command(command, timeout)

            # VALIDATE
            if success:
                validation_passed = self.validate_output(stdout, stderr, expected_output)
                if not validation_passed:
                    success = False

            # UPDATE
            snapshot = self.update_snapshot_after_execution(snapshot, command, success)
            saved = self.save_rehydration_snapshot(snapshot)

            if not saved:
                print("❌ Failed to save execution state - manual intervention required")
                return 2  # Execution failed

            if not success:
                print("❌ Execution step failed - blocker encountered")
                print("   Check rehydration snapshot for failure details")
                return 1  # Blocker

            # Check for next action
            next_action = snapshot.get('next_action')
            if not next_action:
                print("✅ Execution loop complete - no more actions")
                break

        # Check termination conditions
        if self.execution_count >= self.max_executions:
            print(f"⚠️ Execution loop terminated after {self.max_executions} steps (safety limit)")
            return 2  # Execution failed

        print("\n🎉 EXECUTION LOOP COMPLETED SUCCESSFULLY")
        print("=" * 50)
        print("📋 Ready for closure transition")
        print("💡 Run session closure next")

        return 0  # Complete

def main():
    parser = argparse.ArgumentParser(
        description="One-Screen Execution Loop - Automated Task Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXECUTION LOOP:
  RUN next_action.command
  ↓
  VALIDATE expected_outcome
  ↓
  UPDATE rehydration.json
  ↓
  IF next_action exists → LOOP
  ELSE → TRANSITION TO CLOSURE

EXIT CODES:
  0 = EXECUTION COMPLETE → ready for closure
  1 = BLOCKER ENCOUNTERED → escalation needed
  2 = EXECUTION FAILED → manual intervention required
        """
    )
    parser.add_argument("--agent", required=True, help="Agent ID (e.g., Agent-1, Agent-2)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    execution_loop = OneScreenExecutionLoop(project_root, args.agent)

    exit_code = execution_loop.run_execution_loop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()