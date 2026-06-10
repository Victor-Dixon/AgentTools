"""Discord Commander CLI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .inbound_dry_run import inbound_dry_run
from .outbound_dry_run import outbound_dry_run
from .outbound_router import post_to_discord
from .status import collect_status


def _print_result(result, as_json: bool = False) -> int:
    if as_json:
        print(json.dumps({"success": result.success, "message": result.message, "data": result.data}, indent=2))
    else:
        print(result.message)
        if result.data and not result.success:
            for key, value in (result.data or {}).items():
                print(f"  {key}: {value}")
    return 0 if result.success else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="discord_commander",
        description="Discord Commander toolbelt — inbound/outbound Discord ↔ agent bridge",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("inbound-dry-run", help="Validate DISCORD_BOT_TOKEN (no posts)")
    sub.add_parser("outbound-dry-run", help="Validate webhook config (no posts, no secrets)")
    sub.add_parser("status", help="Show configuration status")

    post = sub.add_parser("post", help="Post a message to an agent webhook")
    post.add_argument("--agent", required=True, help="Target agent (e.g. Agent-1)")
    post.add_argument("--title", required=True, help="Embed title")
    post.add_argument("--message", help="Message body")
    post.add_argument("--message-file", type=Path, help="Read message body from file")
    post.add_argument("--dry-run", action="store_true", help="Validate without posting")

    sub.add_parser("start-bot", help="Start the unified Discord bot")
    sub.add_parser("start-queue", help="Start the message queue processor (PyAutoGUI adapter)")

    return parser


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def cmd_start_bot() -> int:
    script = _repo_root() / "tools" / "discord_commander" / "run_unified_discord_bot_with_restart.py"
    if not script.exists():
        from .bot_runner_service import main as bot_main

        return bot_main()
    return subprocess.call([sys.executable, str(script)])


def cmd_start_queue() -> int:
    script = _repo_root() / "tools" / "discord_commander" / "start_message_queue_processor.py"
    if not script.exists():
        print("Queue processor script not found", file=sys.stderr)
        return 1
    return subprocess.call([sys.executable, str(script)])


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inbound-dry-run":
        return _print_result(inbound_dry_run(), as_json=args.json)
    if args.command == "outbound-dry-run":
        return _print_result(outbound_dry_run(), as_json=args.json)
    if args.command == "status":
        return _print_result(collect_status(), as_json=args.json)
    if args.command == "post":
        if not args.message and not args.message_file:
            print("Provide --message or --message-file", file=sys.stderr)
            return 2
        result = post_to_discord(
            agent=args.agent,
            title=args.title,
            message=args.message or "",
            dry_run=args.dry_run,
            message_file=args.message_file,
        )
        return _print_result(result, as_json=args.json)
    if args.command == "start-bot":
        return cmd_start_bot()
    if args.command == "start-queue":
        return cmd_start_queue()
    parser.print_help()
    return 2
