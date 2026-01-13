#!/usr/bin/env python3
"""
Onboarding Executor - Agent Toolbelt V2
======================================

Handles agent onboarding operations:
- Soft onboarding (session cleanup)
- Hard onboarding (complete reset)
- Onboarding status checks

Author: Agent-8 (SSOT & Documentation Specialist)
Created: 2025-10-15
Mission: Toolbelt expansion Phase 1
V2 Compliance: <100 lines, focused executor
"""

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class OnboardingExecutor:
    """Execute onboarding commands via messaging CLI."""

    def __init__(self):
        """Initialize onboarding executor."""
        self.soft_onboard_cli = "python tools/soft_onboard_cli.py"

    def execute(self, args) -> int:
        """
        Execute onboarding command.

        Args:
            args: Parsed arguments with onboard_action

        Returns:
            Exit code (0 for success)
        """
        action = args.onboard_action

        if action == "soft":
            return self._soft_onboarding(args)
        elif action == "hard":
            return self._hard_onboarding(args)
        elif action == "status":
            return self._onboarding_status(args)
        else:
            print(f"❌ Unknown onboarding action: {action}")
            return 1

    def _soft_onboarding(self, args) -> int:
        """Execute soft onboarding with integrated S2A v2.3 + PyAutoGUI."""
        if not args.agent:
            print("❌ --agent required for soft onboarding")
            return 1

        cmd = [
            "python",
            "tools/soft_onboard_cli.py",
            "--agent",
            args.agent,
        ]

        print(f"🚀 Soft onboarding {args.agent} with S2A v2.3 + PyAutoGUI...")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _hard_onboarding(self, args) -> int:
        """Execute hard onboarding (complete reset)."""
        if not args.agent or not args.message:
            print("❌ --agent and --message required for hard onboarding")
            return 1

        if not args.yes:
            print("⚠️  Hard onboarding is a DESTRUCTIVE operation!")
            print("    Use --yes to confirm")
            return 1

        cmd = [
            "python",
            "-m",
            "src.services.messaging_cli",
            "--hard-onboarding",
            "--agent",
            args.agent,
            "--message",
            args.message,
            "--yes",
        ]

        print(f"🚨 Hard onboarding {args.agent} (COMPLETE RESET)...")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _onboarding_status(self, args) -> int:
        """Check onboarding status for an agent."""
        if not args.agent:
            print("❌ --agent required for status check")
            return 1

        print(f"📊 Onboarding status for {args.agent}:")
        print(f"   Status file: agent_workspaces/{args.agent}/status.json")
        print(f"   Inbox: agent_workspaces/{args.agent}/inbox/")
        print(f"   Use: cat agent_workspaces/{args.agent}/status.json | jq")
        return 0


__all__ = ["OnboardingExecutor"]

