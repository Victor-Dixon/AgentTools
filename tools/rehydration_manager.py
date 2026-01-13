#!/usr/bin/env python3
"""
Rehydration Manager - Agent State Persistence
===========================================

Creates and manages rehydration snapshots for seamless agent resume.
Part of the S2A Onboarding v2.2 (Rehydrate → Resume) system.

Features:
- Automatic snapshot creation from current state
- Resume gate validation
- Idempotent operations
- Single source of truth for agent state

Usage:
    # Create/update snapshot
    python tools/rehydration_manager.py --agent Agent-X --snapshot --next-action "python tools/task.py"

    # Validate resume gates
    python tools/rehydration_manager.py --agent Agent-X --validate-gates

    # Show current state
    python tools/rehydration_manager.py --agent Agent-X --status

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-12
"""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class RehydrationManager:
    """Manages agent rehydration snapshots for seamless resume."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def get_current_git_sha(self) -> str:
        """Get current git SHA."""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                  capture_output=True, text=True, cwd=self.project_root)
            return result.stdout.strip()[:7]  # Short SHA
        except Exception:
            return "unknown"

    def load_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load current agent status."""
        status_file = self.project_root / "agent_workspaces" / agent_id / "status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def load_inbox_messages(self, agent_id: str) -> list:
        """Load recent inbox messages."""
        inbox_dir = self.project_root / "agent_workspaces" / agent_id / "inbox"
        messages = []

        if inbox_dir.exists():
            for md_file in inbox_dir.glob("*.md"):
                try:
                    content = md_file.read_text()
                    messages.append({
                        "filename": md_file.name,
                        "content": content[:500] + "..." if len(content) > 500 else content
                    })
                except Exception:
                    continue

        return messages

    def create_rehydration_snapshot(self, agent_id: str, next_action: Optional[str] = None) -> Dict[str, Any]:
        """Create a rehydration snapshot from current agent state."""
        status = self.load_agent_status(agent_id) or {}
        inbox_messages = self.load_inbox_messages(agent_id)

        # Extract current task info
        current_task = status.get('current_task', {})
        if not current_task and inbox_messages:
            # Infer from latest inbox message
            latest_message = inbox_messages[0]['content']
            current_task = {
                "id": f"inferred-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "description": "Resume from latest inbox message",
                "status": "pending"
            }

        # Create next action if provided
        next_action_data = None
        if next_action:
            next_action_data = {
                "command": next_action,
                "description": f"Execute: {next_action}",
                "expected_output": "Command completed successfully",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        snapshot = {
            "agent_id": agent_id,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "git_sha": self.get_current_git_sha(),
            "cycle_id": status.get('cycle_id', f"CYCLE-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"),
            "current_task": current_task,
            "next_action": next_action_data,
            "inbox_summary": {
                "message_count": len(inbox_messages),
                "latest_message": inbox_messages[0] if inbox_messages else None
            },
            "validation_gates": {
                "git_sha_matches": True,  # Will be validated on resume
                "cycle_id_matches": True,
                "task_still_valid": True
            },
            "blockers": status.get('blockers', []),
            "resume_ready": bool(next_action_data or current_task)
        }

        return snapshot

    def save_rehydration_snapshot(self, agent_id: str, snapshot: Dict[str, Any]) -> Path:
        """Save rehydration snapshot to agent's workspace."""
        snapshot_file = self.project_root / "agent_workspaces" / agent_id / "rehydration.json"
        snapshot_file.parent.mkdir(parents=True, exist_ok=True)

        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)

        return snapshot_file

    def validate_resume_gates(self, agent_id: str) -> Dict[str, Any]:
        """Validate all resume gates for safe continuation."""
        snapshot_file = self.project_root / "agent_workspaces" / agent_id / "rehydration.json"

        if not snapshot_file.exists():
            return {
                "gates": {"snapshot_exists": False},
                "all_passed": False,
                "blockers": ["rehydration.json missing - create snapshot first"]
            }

        try:
            with open(snapshot_file, 'r') as f:
                snapshot = json.load(f)
        except Exception as e:
            return {
                "gates": {"snapshot_valid": False},
                "all_passed": False,
                "blockers": [f"rehydration.json corrupted: {e}"]
            }

        # Check gates
        current_sha = self.get_current_git_sha()
        git_sha_matches = snapshot.get('git_sha') == current_sha

        current_status = self.load_agent_status(agent_id) or {}
        cycle_id_matches = snapshot.get('cycle_id') == current_status.get('cycle_id')

        # Task validation (simplified - could be more sophisticated)
        task_still_valid = True  # Assume valid unless we implement task completion tracking

        gates = {
            "git_sha_matches": git_sha_matches,
            "cycle_id_matches": cycle_id_matches,
            "task_still_valid": task_still_valid,
            "snapshot_exists": True,
            "snapshot_valid": True
        }

        all_passed = all(gates.values())

        result = {
            "gates": gates,
            "all_passed": all_passed,
            "snapshot_fresh": all_passed,
            "current_sha": current_sha,
            "snapshot_sha": snapshot.get('git_sha'),
            "blockers": []
        }

        if not all_passed:
            blockers = []
            if not git_sha_matches:
                blockers.append(f"Git SHA mismatch: snapshot has {snapshot.get('git_sha')}, current is {current_sha}")
            if not cycle_id_matches:
                blockers.append(f"Cycle ID mismatch: snapshot has {snapshot.get('cycle_id')}, current has {current_status.get('cycle_id')}")
            result["blockers"] = blockers

        return result

    def get_status_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive status summary for the agent."""
        snapshot_file = self.project_root / "agent_workspaces" / agent_id / "rehydration.json"
        status = self.load_agent_status(agent_id)
        inbox_messages = self.load_inbox_messages(agent_id)

        summary = {
            "agent_id": agent_id,
            "rehydration_exists": snapshot_file.exists(),
            "status_exists": status is not None,
            "inbox_message_count": len(inbox_messages),
            "current_git_sha": self.get_current_git_sha()
        }

        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r') as f:
                    snapshot = json.load(f)
                summary.update({
                    "snapshot_git_sha": snapshot.get('git_sha'),
                    "cycle_id": snapshot.get('cycle_id'),
                    "has_next_action": snapshot.get('next_action') is not None,
                    "resume_ready": snapshot.get('resume_ready', False),
                    "last_updated": snapshot.get('last_updated'),
                    "current_task": snapshot.get('current_task', {}).get('description', 'None')
                })
            except Exception as e:
                summary["snapshot_error"] = str(e)

        if status:
            summary.update({
                "status_cycle_id": status.get('cycle_id'),
                "status_current_task": status.get('current_task', {}).get('description', 'None') if status.get('current_task') else 'None'
            })

        return summary

def main():
    parser = argparse.ArgumentParser(
        description="Rehydration Manager - Agent State Persistence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Create snapshot with next action
  python tools/rehydration_manager.py --agent Agent-2 --snapshot --next-action "python tools/task.py --run"

  # Validate resume gates
  python tools/rehydration_manager.py --agent Agent-2 --validate-gates

  # Show status summary
  python tools/rehydration_manager.py --agent Agent-2 --status
        """
    )
    parser.add_argument("--agent", required=True, help="Agent ID (e.g., Agent-1, Agent-2)")
    parser.add_argument("--snapshot", action="store_true", help="Create/update rehydration snapshot")
    parser.add_argument("--next-action", help="Next executable action command for the snapshot")
    parser.add_argument("--validate-gates", action="store_true", help="Validate resume gates")
    parser.add_argument("--status", action="store_true", help="Show comprehensive status summary")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    manager = RehydrationManager(project_root)

    if args.snapshot:
        print(f"📸 Creating rehydration snapshot for {args.agent}...")
        snapshot = manager.create_rehydration_snapshot(args.agent, args.next_action)
        snapshot_file = manager.save_rehydration_snapshot(args.agent, snapshot)

        print(f"✅ Snapshot saved: {snapshot_file}")
        print(f"   Next action: {snapshot.get('next_action', {}).get('command', 'None')}")
        print(f"   Resume ready: {snapshot.get('resume_ready', False)}")

    elif args.validate_gates:
        print(f"🔍 Validating resume gates for {args.agent}...")
        validation = manager.validate_resume_gates(args.agent)

        print(f"📊 Gate Status: {'✅ ALL PASSED' if validation['all_passed'] else '❌ GATES FAILED'}")

        for gate, passed in validation['gates'].items():
            status = "✅" if passed else "❌"
            print(f"   {status} {gate}")

        if validation.get('blockers'):
            print("\n🚫 BLOCKERS:")
            for blocker in validation['blockers']:
                print(f"   • {blocker}")

    elif args.status:
        print(f"📋 Status summary for {args.agent}:")
        summary = manager.get_status_summary(args.agent)

        print(f"   Rehydration exists: {'✅' if summary['rehydration_exists'] else '❌'}")
        print(f"   Status exists: {'✅' if summary['status_exists'] else '❌'}")
        print(f"   Inbox messages: {summary['inbox_message_count']}")
        print(f"   Current git SHA: {summary['current_git_sha']}")

        if summary['rehydration_exists']:
            print(f"   Resume ready: {'✅' if summary.get('resume_ready') else '❌'}")
            print(f"   Has next action: {'✅' if summary.get('has_next_action') else '❌'}")
            print(f"   Current task: {summary.get('current_task', 'None')}")
            print(f"   Last updated: {summary.get('last_updated', 'Unknown')}")

            if summary.get('snapshot_git_sha') != summary['current_git_sha']:
                print(f"   ⚠️  Git SHA drift: snapshot={summary.get('snapshot_git_sha')}, current={summary['current_git_sha']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()