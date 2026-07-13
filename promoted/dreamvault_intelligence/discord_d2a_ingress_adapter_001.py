#!/usr/bin/env python3
"""Discord D2A ingress adapter CLI — test without live Discord token."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dreamvault.agent_cellphone.coord_validation import default_layout_mode  # noqa: E402
from dreamvault.discord.d2a_ingress_adapter import ingest_discord_message_command  # noqa: E402
from dreamvault.discord.d2a_transport_bootstrap import bootstrap_d2a_transport_env  # noqa: E402
from dreamvault.message_bus.dispatcher import default_bus_paths  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Discord D2A ingress -> unified message bus")
    parser.add_argument(
        "--command",
        default="!message Agent-4 test",
        help="Discord !message command text (default: !message Agent-4 test)",
    )
    parser.add_argument("--sender", default="DiscordCommander")
    parser.add_argument("--message-id", help="Optional stable bus message id")
    parser.add_argument(
        "--dry-run-dispatch",
        action="store_true",
        help="After enqueue, dispatch via message bus (dry-run, no PyAutoGUI)",
    )
    parser.add_argument("--layout", default=None)
    parser.add_argument("--fixture", type=Path, help="Read command text from fixture file")
    args = parser.parse_args()

    bootstrap_d2a_transport_env(REPO_ROOT)
    layout = args.layout or default_layout_mode()
    os.environ.setdefault("AGENT_GAS_LAYOUT_MODE", layout)

    command_text = args.fixture.read_text(encoding="utf-8").strip() if args.fixture else args.command
    paths = default_bus_paths(REPO_ROOT)

    result = ingest_discord_message_command(
        command_text,
        sender=args.sender,
        paths=paths,
        message_id=args.message_id,
        dry_run_dispatch=args.dry_run_dispatch,
        layout=layout,
    )
    body = result.to_dict()
    print(json.dumps(body, indent=2))
    for marker in result.verify_markers:
        print(marker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
