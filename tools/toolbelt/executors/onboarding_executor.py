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
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class OnboardingExecutor:
    """Execute onboarding commands via messaging CLI."""

    def __init__(self):
        """Initialize onboarding executor."""
        self.soft_onboard_cli = "python tools/soft_onboard_cli.py"

    def _dreamvault_messaging_script(self) -> Path | None:
        for root in (
            Path(os.environ.get("DREAMVAULT_ROOT", "D:/DreamVault")),
            Path("D:/DreamVault"),
        ):
            script = root / "runtime/scripts/agent_messaging_send_001.py"
            if script.is_file():
                return script
        return None

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

        script = self._dreamvault_messaging_script()
        if script is None:
            print("ERROR: DreamVault messaging SSOT not found for hard onboarding")
            return 1

        cmd = [
            sys.executable,
            str(script),
            "--category",
            "s2a",
            "--s2a-variant",
            "onboarding",
            "--agent",
            args.agent,
            "--message",
            args.message,
        ]

        print(f"🚨 Hard onboarding {args.agent} (COMPLETE RESET)...")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _onboarding_status(self, args) -> int:
        """Check onboarding status for an agent.

        Surfaces the canonical readiness paths used by
        ``python -m tools.toolbelt --onboard-status --agent Agent-N``.
        """
        if not args.agent:
            print("❌ --agent required for status check")
            return 1

        for line in format_onboarding_status_lines(args.agent):
            print(line)
        return 0


def format_onboarding_status_lines(agent: str) -> list[str]:
    """Return human-readable onboard-status lines for ``agent`` (no I/O)."""
    return [
        f"📊 Onboarding status for {agent}:",
        f"   Status file: agent_workspaces/{agent}/status.json",
        f"   Inbox: agent_workspaces/{agent}/inbox/",
        f"   Use: cat agent_workspaces/{agent}/status.json | jq",
        "   Canonical: python -m tools.toolbelt --onboard-status --agent " + agent,
    ]


__all__ = ["OnboardingExecutor", "format_onboarding_status_lines"]

