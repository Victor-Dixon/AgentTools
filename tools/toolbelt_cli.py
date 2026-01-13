#!/usr/bin/env python3
"""
Toolbelt CLI Router - Onboarding Commands
==========================================

Unified router for onboarding commands.
Provides consistent CLI interface: python tools/toolbelt_cli.py <command> [args...]

Supported commands:
- onboard:soft --agent Agent-X
- onboard:status --agent Agent-X
- onboard:hard --agent Agent-X --yes

Exit codes follow standard: 0=success, 1=blocked/fail, 2=invalid args/unsafe
"""

import sys
import subprocess

# Direct command mapping to avoid import issues
COMMANDS = {
    "onboard:soft": ["python", "tools/toolbelt/cli/onboarding_cli.py", "onboard:soft"],
    "onboard:status": ["python", "tools/toolbelt/cli/onboarding_cli.py", "onboard:status"],
    "onboard:hard": ["python", "tools/toolbelt/cli/onboarding_cli.py", "onboard:hard"],
}

def main(argv):
    """Main CLI dispatcher."""
    if not argv:
        print("Missing command. Try: onboard:soft | onboard:status | onboard:hard", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  python tools/toolbelt_cli.py onboard:soft --agent Agent-5", file=sys.stderr)
        print("  python tools/toolbelt_cli.py onboard:status --agent Agent-5", file=sys.stderr)
        print("  python tools/toolbelt_cli.py onboard:hard --agent Agent-5 --yes", file=sys.stderr)
        return 2

    cmd = argv[0]
    cmd_args = COMMANDS.get(cmd)
    if not cmd_args:
        print(f"Unknown command '{cmd}'. Available: {', '.join(COMMANDS.keys())}", file=sys.stderr)
        return 2

    # Execute as subprocess to avoid import issues
    full_cmd = cmd_args + argv[1:]
    result = subprocess.run(full_cmd, capture_output=False)
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))