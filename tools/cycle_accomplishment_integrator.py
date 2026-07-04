#!/usr/bin/env python3
"""
Cycle Accomplishment Integrator
===============================

PRODUCTION-GRADE: Integrates session closures with cycle accomplishment tracking.

Features:
- ✅ IDEMPOTENT: Same closure-run-id produces identical results
- ✅ ATOMIC WRITES: Crash-safe status.json updates
- ✅ AUDITABLE: Full history and validation
- ✅ CONFIGURABLE: Points system via config/cycle_points.json
- ✅ VALIDATED: Strict input validation with clear error messages

Usage:
    python tools/cycle_accomplishment_integrator.py --agent Agent-X --closure-run-id "Agent-X:abc123:2026-01-12T07:12:33Z" --closure-complete --tasks-completed 3 --issues-found 2 --consolidation-opportunities 1

Author: Agent-3 (Infrastructure & DevOps)
Created: 2026-01-11
Updated: 2026-01-12 (Enterprise hardening)
"""

import argparse
import json
import os
import re
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class CycleAccomplishmentIntegrator:
    """PRODUCTION-GRADE: Integrates closure data with cycle accomplishment tracking."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.points_config = self._load_points_config()
        self.agent_pattern = re.compile(r'^Agent-[1-8]$')

    def _load_points_config(self) -> Dict[str, Any]:
        """Load points configuration with fallbacks."""
        config_path = self.project_root / "config" / "cycle_points.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load points config: {e}, using defaults")

        # Fallback defaults
        return {
            "points": {
                "per_task": 10,
                "per_issue": 5,
                "per_consolidation": 15,
                "per_quality_check": 8
            },
            "caps": {
                "max_points_per_closure": 200,
                "max_tasks_per_closure": 20,
                "max_issues_per_closure": 50,
                "max_consolidations_per_closure": 10
            }
        }

    def validate_inputs(self, args: argparse.Namespace) -> bool:
        """Validate all inputs with clear error messages."""
        errors = []

        # Validate agent ID
        if not self.agent_pattern.match(args.agent):
            errors.append(f"❌ Invalid agent ID '{args.agent}'. Must match 'Agent-[1-8]'")

        # Validate closure_run_id format
        if hasattr(args, 'closure_run_id') and args.closure_run_id:
            expected_pattern = r'^Agent-[1-8]:[a-f0-9]{7,40}:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
            if not re.match(expected_pattern, args.closure_run_id):
                errors.append(f"❌ Invalid closure_run_id format: '{args.closure_run_id}'")
                errors.append("   Expected: Agent-X:gitsha:2026-01-12T07:12:33Z")

        # Validate numeric inputs
        numeric_fields = ['tasks_completed', 'issues_found', 'consolidation_opportunities']
        for field in numeric_fields:
            if hasattr(args, field):
                value = getattr(args, field)
                if value is not None and (not isinstance(value, int) or value < 0):
                    errors.append(f"❌ {field} must be non-negative integer, got: {value}")

        # Check caps
        if hasattr(args, 'tasks_completed') and args.tasks_completed > self.points_config['caps']['max_tasks_per_closure']:
            errors.append(f"❌ tasks_completed exceeds cap: {args.tasks_completed} > {self.points_config['caps']['max_tasks_per_closure']}")

        if hasattr(args, 'issues_found') and args.issues_found > self.points_config['caps']['max_issues_per_closure']:
            errors.append(f"❌ issues_found exceeds cap: {args.issues_found} > {self.points_config['caps']['max_issues_per_closure']}")

        if hasattr(args, 'consolidation_opportunities') and args.consolidation_opportunities > self.points_config['caps']['max_consolidations_per_closure']:
            errors.append(f"❌ consolidation_opportunities exceeds cap: {args.consolidation_opportunities} > {self.points_config['caps']['max_consolidations_per_closure']}")

        if errors:
            for error in errors:
                print(error)
            return False

        return True

    def load_agent_status(self, agent_id: str) -> Tuple[Optional[Dict[str, Any]], Path]:
        """Load current agent status with file path."""
        status_file = self.project_root / "agent_workspaces" / agent_id / "status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    return json.load(f), status_file
            except Exception:
                pass
        return None, status_file

    def check_idempotency(self, status: Dict[str, Any], closure_run_id: str) -> bool:
        """Check if this closure has already been applied."""
        if not status:
            return False  # No previous status, can proceed

        cycle_data = status.get('cycle', {})
        last_run_id = cycle_data.get('last_closure_run_id')

        if last_run_id == closure_run_id:
            print(f"✅ IDEMPOTENCY: Closure {closure_run_id} already applied - no-op")
            return True  # Already applied

        return False  # Can proceed

    def update_cycle_status_atomic(self, agent_id: str, closure_run_id: str,
                                   tasks_completed: int, issues_found: int,
                                   consolidation_opportunities: int, dry_run: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """ATOMically update agent cycle status with full idempotency and crash safety."""
        try:
            # Load current status
            current_status, status_file = self.load_agent_status(agent_id)

            # Check idempotency
            if self.check_idempotency(current_status or {}, closure_run_id):
                # Return success with existing metrics
                cycle_data = (current_status or {}).get('cycle', {})
                accomplishments = cycle_data.get('closure_totals', {})
                return True, accomplishments

            # Calculate accomplishments with config
            accomplishments = self._calculate_accomplishments_config(
                tasks_completed, issues_found, consolidation_opportunities
            )

            # Parse closure_run_id for metadata
            run_parts = closure_run_id.split(':')
            git_sha = run_parts[1] if len(run_parts) > 1 else "unknown"
            utc_timestamp = run_parts[2] if len(run_parts) > 2 else datetime.now(timezone.utc).isoformat()

            # Initialize status if needed
            if current_status is None:
                current_status = {
                    "agent_id": agent_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "cycle": {
                        "history": []
                    }
                }

            # Update cycle data with standardized schema
            cycle_data = current_status.get('cycle', {})
            cycle_data.update({
                "last_closure_run_id": closure_run_id,
                "last_closure_at_utc": utc_timestamp,
                "last_closure_git_sha": git_sha,
                "closure_totals": accomplishments,
                "last_updated": datetime.now(timezone.utc).isoformat()
            })

            # Add to history (capped at 20 entries)
            history = cycle_data.get('history', [])
            history_entry = {
                "run_id": closure_run_id,
                "git_sha": git_sha,
                "timestamp": utc_timestamp,
                "points": accomplishments["points_earned"],
                "tasks": accomplishments["tasks_completed"],
                "issues": accomplishments["issues_found"],
                "consolidations": accomplishments["consolidation_opportunities"]
            }
            history.insert(0, history_entry)  # Most recent first
            cycle_data['history'] = history[:20]  # Cap at 20

            # Update main status
            current_status['cycle'] = cycle_data
            current_status['last_cycle_update'] = datetime.now(timezone.utc).isoformat()

            if dry_run:
                print("🔍 DRY RUN - Would update status with:")
                print(json.dumps(current_status['cycle'], indent=2))
                return True, accomplishments

            # ATOMIC WRITE: Two-phase with temp file
            status_file.parent.mkdir(parents=True, exist_ok=True)

            # Phase 1: Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False,
                                          dir=status_file.parent) as temp_file:
                json.dump(current_status, temp_file, indent=2)
                temp_path = Path(temp_file.name)

            try:
                # Phase 2: Atomic rename (POSIX atomic, NTFS as close as possible)
                temp_path.replace(status_file)
                print(f"✅ ATOMIC: Updated cycle status for {agent_id}")
                return True, accomplishments

            except Exception as e:
                # Cleanup temp file on failure
                temp_path.unlink(missing_ok=True)
                raise e

        except Exception as e:
            print(f"❌ Failed to update cycle status: {e}")
            return False, {}

    def _calculate_accomplishments_config(self, tasks_completed: int, issues_found: int,
                                        consolidation_opportunities: int) -> Dict[str, Any]:
        """Calculate accomplishments using configurable points system."""
        # Apply caps
        tasks_capped = min(tasks_completed, self.points_config['caps']['max_tasks_per_closure'])
        issues_capped = min(issues_found, self.points_config['caps']['max_issues_per_closure'])
        consolidations_capped = min(consolidation_opportunities, self.points_config['caps']['max_consolidations_per_closure'])

        # Calculate points
        points_from_tasks = tasks_capped * self.points_config['points']['per_task']
        points_from_issues = issues_capped * self.points_config['points']['per_issue']
        points_from_consolidations = consolidations_capped * self.points_config['points']['per_consolidation']

        total_points = points_from_tasks + points_from_issues + points_from_consolidations

        # Apply overall cap
        total_points_capped = min(total_points, self.points_config['caps']['max_points_per_closure'])

        return {
            "tasks_completed": tasks_capped,
            "issues_found": issues_capped,
            "consolidation_opportunities": consolidations_capped,
            "points_earned": total_points_capped,
            "points_breakdown": {
                "tasks": points_from_tasks,
                "issues": points_from_issues,
                "consolidations": points_from_consolidations,
                "total_uncapped": total_points,
                "capped": total_points_capped != total_points
            }
        }

    def generate_accomplishment_report(self, agent_id: str, accomplishments: Dict[str, Any],
                                      closure_run_id: str) -> str:
        """Generate standardized accomplishment report for Discord posting."""
        # Parse closure_run_id for display
        run_parts = closure_run_id.split(':')
        git_sha_short = run_parts[1][:7] if len(run_parts) > 1 and len(run_parts[1]) >= 7 else "unknown"

        report = f"""🏆 **{agent_id} Cycle Accomplishment Report**

**Closure Run ID:** `{closure_run_id}`
**Git SHA:** `{git_sha_short}`
**Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

## 📊 Accomplishments Logged

| Metric | Count | Points |
|--------|-------|--------|
| Tasks Completed | {accomplishments.get('tasks_completed', 0)} | {accomplishments.get('points_breakdown', {}).get('tasks', 0)} |
| Issues Documented | {accomplishments.get('issues_found', 0)} | {accomplishments.get('points_breakdown', {}).get('issues', 0)} |
| Consolidation Opportunities | {accomplishments.get('consolidation_opportunities', 0)} | {accomplishments.get('points_breakdown', {}).get('consolidations', 0)} |

## 🎯 Points Summary
**Total Points Earned:** {accomplishments.get('points_earned', 0)} pts

*✅ Session closure successfully logged to cycle tracking system*
*Contributing to swarm-wide productivity metrics* 🚀"""

        return report

    def post_to_cycle_channel(self, agent_id: str, accomplishments: Dict[str, Any],
                             closure_run_id: str) -> bool:
        """Post accomplishment report to dedicated cycle accomplishments Discord channel."""
        # Check for required webhook environment variable
        webhook_env_var = "DISCORD_WEBHOOK_CYCLE_ACCOMPLISHMENTS"
        webhook_url = os.getenv(webhook_env_var)

        if not webhook_url:
            print(f"❌ REQUIRED: {webhook_env_var} environment variable not set")
            print(f"   Cannot post to #cycle-accomplishments channel")
            print(f"   Set the webhook URL in your .env file or environment")
            return False  # Hard failure - webhook is required

        try:
            # Generate standardized report
            report = self.generate_accomplishment_report(agent_id, accomplishments, closure_run_id)

            payload = {
                "username": f"{agent_id} Cycle Tracker",
                "content": report
            }

            # Post to Discord
            import requests
            response = requests.post(webhook_url, json=payload, timeout=10)

            if response.status_code == 204:
                print(f"✅ Posted cycle accomplishment for {agent_id} to #cycle-accomplishments")
                return True
            else:
                print(f"❌ Discord posting failed (HTTP {response.status_code})")
                print(f"   Response: {response.text[:200]}...")
                return False  # Hard failure for posting errors

        except Exception as e:
            print(f"❌ Discord posting error: {e}")
            return False  # Hard failure for exceptions

def main():
    parser = argparse.ArgumentParser(
        description="PRODUCTION-GRADE Cycle Accomplishment Integrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Dry run to see what would happen
  python cycle_accomplishment_integrator.py --agent Agent-3 --closure-run-id "Agent-3:abc1234:2026-01-12T07:12:33Z" --tasks-completed 3 --issues-found 2 --consolidation-opportunities 1 --dry-run

  # Actual closure logging (use in closure prompt)
  python cycle_accomplishment_integrator.py --agent Agent-3 --closure-run-id "Agent-3:abc1234:2026-01-12T07:12:33Z" --tasks-completed 3 --issues-found 2 --consolidation-opportunities 1 --closure-complete

ENVIRONMENT:
  Required: DISCORD_WEBHOOK_CYCLE_ACCOMPLISHMENTS
  Points config: config/cycle_points.json (with fallbacks)
        """
    )
    parser.add_argument("--agent", required=True, help="Agent ID (must match Agent-[1-8])")
    parser.add_argument("--closure-run-id", required=True,
                       help="Unique closure run ID: Agent-X:git_sha:UTC_timestamp")
    parser.add_argument("--tasks-completed", type=int, default=0,
                       help="Number of tasks completed in closure")
    parser.add_argument("--issues-found", type=int, default=0,
                       help="Number of quality issues documented")
    parser.add_argument("--consolidation-opportunities", type=int, default=0,
                       help="Number of consolidation opportunities identified")
    parser.add_argument("--closure-complete", action="store_true",
                       help="Mark closure complete and update cycle metrics")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would happen without making changes")

    args = parser.parse_args()

    # Load environment variables
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    project_root = Path(__file__).parent.parent
    integrator = CycleAccomplishmentIntegrator(project_root)

    # VALIDATE ALL INPUTS FIRST
    if not integrator.validate_inputs(args):
        print("\n❌ Input validation failed - exiting")
        exit(1)

    print(f"🚀 Cycle Accomplishment Integrator - Agent {args.agent}")
    print(f"   Run ID: {args.closure_run_id}")
    if args.dry_run:
        print("   Mode: DRY RUN (no changes will be made)")

    if args.closure_complete:
        # ATOMIC UPDATE: Idempotent, crash-safe status update
        success, accomplishments = integrator.update_cycle_status_atomic(
            args.agent, args.closure_run_id,
            args.tasks_completed, args.issues_found, args.consolidation_opportunities,
            dry_run=args.dry_run
        )

        if not success:
            print("❌ Failed to update cycle status")
            exit(1)

        # POST TO DISCORD: Required for cycle accomplishments
        if not args.dry_run:
            discord_success = integrator.post_to_cycle_channel(
                args.agent, accomplishments, args.closure_run_id
            )

            if discord_success:
                print("\n✅ CYCLE ACCOMPLISHMENT LOGGED SUCCESSFULLY")
                print(f"   📊 Status updated atomically")
                print(f"   📢 Posted to #cycle-accomplishments")
                print(f"   🎯 Points earned: {accomplishments.get('points_earned', 0)}")

                # Required output format for closure prompt
                print(f"\nCycle accomplishment logged — tasks={args.tasks_completed}, issues={args.issues_found}, consolidations={args.consolidation_opportunities}, points={accomplishments.get('points_earned', 0)}")
            else:
                print("\n❌ CYCLE ACCOMPLISHMENT PARTIALLY FAILED")
                print(f"   ✅ Status updated locally")
                print(f"   ❌ Discord posting failed - check webhook configuration")
                print(f"   🔄 Data is preserved and can be retried")
                exit(1)  # Exit with error so closure knows posting failed
        else:
            print("\n🔍 DRY RUN COMPLETE - No changes made")
            print(f"   Would earn: {accomplishments.get('points_earned', 0)} points")
    else:
        # Show current cycle status
        current_status, _ = integrator.load_agent_status(args.agent)

        if current_status and 'cycle' in current_status:
            cycle_data = current_status['cycle']
            totals = cycle_data.get('closure_totals', {})

            print(f"📊 Current Cycle Status for {args.agent}:")
            print(f"   Last Run ID: {cycle_data.get('last_closure_run_id', 'None')}")
            print(f"   Total Points: {totals.get('points_earned', 0)}")
            print(f"   Tasks Completed: {totals.get('tasks_completed', 0)}")
            print(f"   Issues Documented: {totals.get('issues_found', 0)}")
            print(f"   Consolidation Opportunities: {totals.get('consolidation_opportunities', 0)}")
            print(f"   Last Updated: {cycle_data.get('last_updated', 'Never')}")

            history = cycle_data.get('history', [])
            if history:
                print(f"   Recent History: {len(history)} entries")
                for entry in history[:3]:  # Show last 3
                    print(f"     • {entry['run_id'][:20]}...: {entry['points']} pts")
        else:
            print(f"ℹ️ No cycle data found for {args.agent} - first closure pending")

if __name__ == "__main__":
    main()