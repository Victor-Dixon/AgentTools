#!/usr/bin/env python3
"""Toolbelt Onboarding CLI - Soft/Hard/Status Commands.

Provides standardized CLI interface for agent onboarding operations.
Wraps OnboardingExecutor methods with safety rails and validation.
"""

import argparse
import sys
import subprocess
from dataclasses import dataclass


def _validate_agent(agent: str) -> None:
    """Validate agent ID format and range."""
    if not agent or not agent.startswith("Agent-"):
        raise ValueError(f"Invalid --agent '{agent}'. Expected Agent-X.")
    # Optional: enforce range Agent-1..Agent-8
    try:
        n = int(agent.split("-")[1])
        if n < 1 or n > 8:
            raise ValueError
    except Exception:
        raise ValueError(f"Invalid --agent '{agent}'. Expected Agent-1..Agent-8.")


@dataclass
class Args:
    """Standardized args for onboarding operations."""
    agent: str
    message: str | None = None
    yes: bool = False
    force: bool = False


def cmd_soft(argv: list[str]) -> int:
    """Execute soft onboarding (S2A v2.3 + PyAutoGUI)."""
    p = argparse.ArgumentParser(prog="onboard:soft")
    p.add_argument("--agent", required=True, help="Agent ID (Agent-1..Agent-8)")
    ns = p.parse_args(argv)
    _validate_agent(ns.agent)

    # Use subprocess to avoid import issues
    cmd = ["python", "-c", f"""
import sys
sys.path.append('tools/toolbelt/executors')
from onboarding_executor import OnboardingExecutor

class MockArgs:
    def __init__(self):
        self.agent = '{ns.agent}'

args = MockArgs()
ex = OnboardingExecutor()
exit(ex._soft_onboarding(args))
"""]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def cmd_status(argv: list[str]) -> int:
    """Show onboarding status for an agent."""
    p = argparse.ArgumentParser(prog="onboard:status")
    p.add_argument("--agent", required=True, help="Agent ID (Agent-1..Agent-8)")
    ns = p.parse_args(argv)
    _validate_agent(ns.agent)

    # Use subprocess to avoid import issues
    cmd = ["python", "-c", f"""
import sys
sys.path.append('tools/toolbelt/executors')
from onboarding_executor import OnboardingExecutor

class MockArgs:
    def __init__(self):
        self.agent = '{ns.agent}'

args = MockArgs()
ex = OnboardingExecutor()
exit(ex._onboarding_status(args))
"""]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def cmd_hard(argv: list[str]) -> int:
    """Execute hard onboarding (DESTRUCTIVE - requires --yes)."""
    p = argparse.ArgumentParser(prog="onboard:hard")
    p.add_argument("--agent", required=True, help="Agent ID (Agent-1..Agent-8)")
    p.add_argument("--yes", action="store_true",
                   help="Required for destructive operations")
    p.add_argument("--force", action="store_true",
                   help="Optional: bypass extra safety prompts (still requires --yes)")
    p.add_argument("--message", default="Hard reset onboarding message",
                   help="Custom onboarding message")
    ns = p.parse_args(argv)
    _validate_agent(ns.agent)

    if not ns.yes:
        print("REFUSED: hard onboarding is destructive. Re-run with --yes.", file=sys.stderr)
        return 2

    force_flag = "--force" if ns.force else ""
    message_arg = f"--message \"{ns.message}\"" if ns.message != "Hard reset onboarding message" else ""

    # Use subprocess to avoid import issues
    script = f"""
import sys
sys.path.append('tools/toolbelt/executors')
from onboarding_executor import OnboardingExecutor

class MockArgs:
    def __init__(self):
        self.agent = '{ns.agent}'
        self.message = '''{ns.message}'''
        self.yes = True
        self.force = {str(ns.force).lower()}

args = MockArgs()
ex = OnboardingExecutor()
exit(ex._hard_onboarding(args))
"""
    cmd = ["python", "-c", script]
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


COMMANDS = {
    "onboard:soft": cmd_soft,
    "onboard:status": cmd_status,
    "onboard:hard": cmd_hard,
}


def main(argv: list[str]) -> int:
    """Main CLI dispatcher."""
    if not argv:
        print("Missing command. Try: onboard:soft | onboard:status | onboard:hard",
              file=sys.stderr)
        return 2
    cmd = argv[0]
    fn = COMMANDS.get(cmd)
    if not fn:
        print(f"Unknown command '{cmd}'.", file=sys.stderr)
        return 2
    return fn(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))