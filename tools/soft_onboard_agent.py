#!/usr/bin/env python3
"""
Soft Onboard Agent - Integrated S2A v2.3 + PyAutoGUI Visual Onboarding
======================================================================

CLI tool that combines S2A v2.3 rehydration logic with the real PyAutoGUI-based
soft onboarding service for complete visual automation with animations.

This tool connects to the REAL soft onboarding system in Agent_Cellphone_V2_Repository
that uses PyAutoGUI for visual chat interactions and animations.

Usage:
    python tools/soft_onboard_agent.py --agent Agent-X

Process:
1. S2A v2.3: Load/create rehydration snapshot + force-multiplier gate check
2. PyAutoGUI: Execute 6-step visual soft onboarding protocol with animations
3. Validation: Confirm onboarding completed successfully

Exit Codes:
    0 = SUCCESS: Agent successfully soft onboarded with animations
    1 = S2A GATE FAIL: Force-multiplier gate blocked execution
    2 = PYAUTOGUI FAIL: Visual onboarding encountered error
    3 = VALIDATION FAIL: Could not confirm successful onboarding

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-12
Updated: Connected to real PyAutoGUI soft onboarding system
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

class SoftOnboardAgent:
    """Orchestrates integrated S2A v2.3 + PyAutoGUI visual onboarding."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.project_root = Path(__file__).parent.parent
        # Path to the real soft onboarding system
        self.cellphone_repo = Path("D:/Agent_Cellphone_V2_Repository")

    def run_command(self, cmd: str, description: str) -> tuple[int, str, str]:
        """Run a command and return (exit_code, stdout, stderr)."""
        print(f"🔧 {description}")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def run_command_live(self, cmd: str) -> int:
        """Run a command with live output (no capture) for visual feedback."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.project_root
            )
            return result.returncode
        except Exception as e:
            print(f"❌ Command execution error: {e}")
            return 1

    def step_load_state(self) -> bool:
        """Step 1: Load/create rehydration snapshot (S2A v2.3 logic)."""
        print("\n📂 STEP 1: LOAD STATE (S2A v2.3)")

        # Check if rehydration snapshot exists
        snapshot_file = self.project_root / "agent_workspaces" / self.agent_id / "rehydration.json"
        inbox_dir = self.project_root / "agent_workspaces" / self.agent_id / "inbox"

        if snapshot_file.exists():
            print(f"✅ Rehydration snapshot found: {snapshot_file}")
            return True
        else:
            print(f"⚠️  No rehydration snapshot found for {self.agent_id}")

            # Check if inbox exists
            if not inbox_dir.exists():
                print(f"❌ No inbox directory found. Creating basic snapshot...")
                # Create a basic snapshot for agents with no prior state
                cmd = f"python tools/rehydration_manager.py --agent {self.agent_id} --snapshot --next-action \"echo '{self.agent_id} soft onboarded successfully'\""
                exit_code, stdout, stderr = self.run_command(cmd, "Creating basic rehydration snapshot")

                if exit_code != 0:
                    print(f"❌ Failed to create basic snapshot: {stderr}")
                    return False

                print("✅ Basic rehydration snapshot created")
                return True
            else:
                print(f"ℹ️  Inbox exists but no snapshot. Agent needs manual setup.")
                return False

    def step_evaluate_gate(self) -> int:
        """Step 2: Evaluate force-multiplier gate (S2A v2.3 logic)."""
        print("\n🚪 STEP 2: EVALUATE FORCE-MULTIPLIER GATE (S2A v2.3)")

        cmd = f"python tools/force_multiplier_gate.py --agent {self.agent_id}"
        exit_code, stdout, stderr = self.run_command(cmd, "Evaluating force-multiplier gate")

        if exit_code == 0:
            print("✅ GATE PASS — PROCEED TO VISUAL ONBOARDING")
            return 0
        elif exit_code == 1:
            print("❌ GATE FAIL — BLOCKER:")
            # Extract blocker message from stderr
            lines = stderr.strip().split('\n')
            for line in lines:
                if line.startswith('❌') or line.startswith('⚠️'):
                    print(f"   {line}")
            return 1
        else:
            print(f"❌ Gate evaluation error (exit code {exit_code}): {stderr}")
            return 1

    def step_execute_visual_onboarding(self) -> int:
        """Step 3: Execute PyAutoGUI visual soft onboarding with animations."""
        print("\n🎭 STEP 3: EXECUTE VISUAL SOFT ONBOARDING (PyAutoGUI)")
        print("🎬 Connecting to real soft onboarding service with animations...")

        # Execute the real soft onboarding service via subprocess
        print(f"🤖 Executing 6-step PyAutoGUI soft onboarding protocol for {self.agent_id}...")

        # Create the onboarding message
        onboarding_message = f"S2A ONBOARDING (SOFT) — v2.3 Force-Multiplier Gate + One-Screen Loop\\n\\n{self.agent_id}, execute your soft onboarding protocol."

        # Run a Python script that imports and calls the real soft onboarding service
        script_content = f'''
import sys
sys.path.insert(0, "src")
from src.services.soft_onboarding_service import soft_onboard_agent

print("🎭 Starting PyAutoGUI soft onboarding with animations...")
success = soft_onboard_agent(
    "{self.agent_id}",
    """{onboarding_message}"""
)
print(f"🎭 Soft onboarding completed: {{'SUCCESS' if success else 'FAILED'}}")
sys.exit(0 if success else 1)
'''

        # Write and execute the script
        script_path = self.cellphone_repo / f"temp_onboard_{self.agent_id}.py"
        try:
            script_path.write_text(script_content)

            cmd = f"python temp_onboard_{self.agent_id}.py"
            print(f"🎭 Running PyAutoGUI soft onboarding for {self.agent_id}...")

            # Use subprocess to execute with live output for animations
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=False,  # Show live output for animations
                text=True,
                cwd=self.cellphone_repo
            )

            if result.returncode == 0:
                print("✅ VISUAL SOFT ONBOARDING COMPLETED WITH ANIMATIONS")
                print("🎭 PyAutoGUI animations executed successfully")
                return 0
            else:
                print(f"❌ VISUAL SOFT ONBOARDING FAILED (exit code: {result.returncode})")
                print("🎭 PyAutoGUI animations encountered an error")
                return 2

        except Exception as e:
            print(f"❌ Failed to execute visual onboarding: {e}")
            print("💡 Make sure Agent_Cellphone_V2_Repository is accessible")
            return 2
        finally:
            # Clean up temp script
            if script_path.exists():
                script_path.unlink(missing_ok=True)

    def step_validate_closure(self) -> int:
        """Step 4: Validate closure next action singularity."""
        print("\n🔒 STEP 4: VALIDATE CLOSURE")

        cmd = f"python tools/validate_closure_next_action.py --agent {self.agent_id}"
        exit_code, stdout, stderr = self.run_command(cmd, "Validating closure next action singularity")

        if exit_code == 0:
            print("✅ CLOSURE VALID")
            return 0
        else:
            print("❌ CLOSURE INVALID")
            # Extract validation message
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.startswith('❌') or line.startswith('✅'):
                    print(f"   {line}")
            return 3

    def onboard_agent(self) -> int:
        """Run the complete soft onboarding process."""
        print(f"🚀 SOFT ONBOARDING AGENT: {self.agent_id}")
        print("=" * 60)

        # Step 1: Load State
        if not self.step_load_state():
            print("❌ SOFT ONBOARDING FAILED: Cannot load/create agent state")
            return 1

        # Step 2: Evaluate Gate
        gate_result = self.step_evaluate_gate()
        if gate_result != 0:
            print("❌ SOFT ONBOARDING BLOCKED: Force-multiplier gate failed")
            return gate_result

        # Step 3: Execute Visual Onboarding (PyAutoGUI)
        visual_result = self.step_execute_visual_onboarding()
        if visual_result != 0:
            print("❌ SOFT ONBOARDING FAILED: Visual onboarding encountered error")
            return visual_result

        # Step 4: Validate Closure
        validation_result = self.step_validate_closure()
        if validation_result != 0:
            print("❌ SOFT ONBOARDING INVALID: Closure validation failed")
            return validation_result

        print("\n" + "=" * 60)
        print(f"✅ SOFT ONBOARDING COMPLETED: {self.agent_id}")
        print("🎯 Agent ready for next assignment or closure transition")
        return 0

def main():
    parser = argparse.ArgumentParser(
        description="Soft Onboard Agent - Complete S2A v2.3 Process",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
S2A v2.3 PROCESS:
  1. LOAD STATE     → Check/create rehydration snapshot
  2. EVALUATE GATE  → Force-multiplier gate (pass/fail)
  3. EXECUTE LOOP   → One-screen execution (success/blocker)
  4. VALIDATE CLOSURE → Next action singularity check

EXAMPLES:
  python tools/soft_onboard_agent.py --agent Agent-2
  python tools/soft_onboard_agent.py --agent Agent-3

EXIT CODES:
  0 = SUCCESS: Agent successfully soft onboarded
  1 = GATE FAIL: Force-multiplier gate blocked execution
  2 = EXECUTION FAIL: One-screen loop encountered blocker
  3 = VALIDATION FAIL: Closure validation failed
        """
    )
    parser.add_argument("--agent", required=True,
                       help="Agent ID to soft onboard (e.g., Agent-2, Agent-3)")

    args = parser.parse_args()

    onboarder = SoftOnboardAgent(args.agent)
    exit_code = onboarder.onboard_agent()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()