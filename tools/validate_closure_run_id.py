#!/usr/bin/env python3
"""
Validate Closure Run ID Format - SSOT
======================================

🟢 SINGLE SOURCE OF TRUTH (SSOT) - Canonical run ID validation utility

Utility tool to validate closure run ID format before cycle accomplishment logging.
Prevents format errors that could cause cycle logging failures.

Usage:
    python tools/validate_closure_run_id.py --run-id "Agent-X:abc1234:2026-01-12T08:30:00Z"

Format: {agent_id}:{git_sha}:{UTC_timestamp}
- agent_id: Agent-[1-8]
- git_sha: 40-character hex string
- UTC_timestamp: ISO 8601 format with Z suffix

Exit Codes:
    0 = VALID: Run ID format is correct
    1 = INVALID: Run ID format is incorrect
"""

import argparse
import re
from pathlib import Path

def validate_run_id(run_id: str) -> tuple[bool, str]:
    """
    Validate closure run ID format.

    Args:
        run_id: Run ID to validate

    Returns:
        (is_valid, error_message)
    """
    # Expected format: Agent-X:40char_hex:ISO8601_with_Z
    pattern = r'^Agent-[1-8]:[a-f0-9]{40}:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'

    if not re.match(pattern, run_id):
        return False, f"Invalid format. Expected: Agent-X:40char_hex:2026-01-12T08:30:00Z"

    # Additional validation
    parts = run_id.split(':')
    if len(parts) != 3:
        return False, "Must have exactly 3 parts separated by colons"

    agent_id, git_sha, timestamp = parts

    # Validate agent ID
    if not re.match(r'^Agent-[1-8]$', agent_id):
        return False, f"Invalid agent ID: {agent_id}. Must be Agent-1 through Agent-8"

    # Validate git SHA (already checked by regex, but let's be explicit)
    if len(git_sha) != 40 or not all(c in '0123456789abcdef' for c in git_sha):
        return False, f"Invalid git SHA: {git_sha}. Must be 40 hex characters"

    # Validate timestamp format (basic check)
    if not timestamp.endswith('Z'):
        return False, f"Timestamp must end with Z: {timestamp}"

    return True, "Valid closure run ID format"

def get_current_git_sha() -> str:
    """Get current git SHA for reference."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"

def main():
    parser = argparse.ArgumentParser(
        description="Validate Closure Run ID Format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python tools/validate_closure_run_id.py --run-id "Agent-3:b09e8eea9e7462abf2dfc2fd67d5d7e13c6ddd45:2026-01-12T08:30:00Z"

FORMAT: Agent-X:40char_hex:2026-01-12T08:30:00Z
  - Agent-X: Agent-1 through Agent-8
  - 40char_hex: Full git SHA
  - ISO8601: Date/time with Z suffix

CURRENT GIT SHA: """ + get_current_git_sha()
    )

    parser.add_argument(
        "--run-id",
        required=True,
        help="Closure run ID to validate"
    )

    args = parser.parse_args()

    is_valid, message = validate_run_id(args.run_id)

    if is_valid:
        print("✅ VALID: " + message)
        print(f"   Run ID: {args.run_id}")
        return 0
    else:
        print("❌ INVALID: " + message)
        print(f"   Run ID: {args.run_id}")
        print("\n💡 TIP: Use this format:")
        print("   Agent-X:" + get_current_git_sha() + ":2026-01-12T08:30:00Z")
        return 1

if __name__ == "__main__":
    exit(main())