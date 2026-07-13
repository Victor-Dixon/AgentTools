#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dreamvault.discord_journal_cards import build_discord_webhook_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export Dream.OS journal closeout cards as Discord webhook JSON."
    )
    parser.add_argument(
        "--journal",
        default=str(REPO_ROOT / "runtime/events/execution_journal.jsonl"),
        help="Path to execution journal JSONL.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of embeds to export.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_discord_webhook_payload(args.journal, limit=max(0, args.limit))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
