#!/usr/bin/env python3
"""Post to Discord router CLI shim.

Built for agent-tools toolbelt (salvage lineage: Victor-Dixon__AutoDream.Os post_to_discord_router — not found; implemented here).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.outbound_router import post_to_discord


def main() -> int:
    parser = argparse.ArgumentParser(description="Route outbound Discord posts to agent webhooks")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--message")
    parser.add_argument("--message-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = post_to_discord(
        agent=args.agent,
        title=args.title,
        message=args.message or "",
        dry_run=args.dry_run,
        message_file=args.message_file,
    )
    print(result.message)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
