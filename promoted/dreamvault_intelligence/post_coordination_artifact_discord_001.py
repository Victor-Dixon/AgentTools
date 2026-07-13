#!/usr/bin/env python3
"""Post a coordination artifact summary to an agent Discord webhook via DreamVault secrets."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SECRETS = REPO / "runtime" / "secrets" / "secrets.local.env"
AGENT_TOOLS_SRC = Path(r"D:\agent-tools\src")


def load_secrets() -> None:
    if not SECRETS.exists():
        raise SystemExit(f"MISSING secrets: {SECRETS}")
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip("'").strip('"')


def main() -> int:
    parser = argparse.ArgumentParser(description="Post artifact summary to agent Discord webhook")
    parser.add_argument("--agent", required=True, help="Agent-N")
    parser.add_argument("--title", required=True)
    parser.add_argument("--file", type=Path, required=True, help="Artifact path (relative to repo or absolute)")
    parser.add_argument("--summary", help="Override body; default reads file")
    args = parser.parse_args()

    artifact = args.file if args.file.is_absolute() else REPO / args.file
    if not artifact.exists():
        print(f"FAIL artifact not found: {artifact}")
        return 1

    load_secrets()
    sys.path.insert(0, str(AGENT_TOOLS_SRC))
    from agent_tools.discord_commander.outbound_router import post_to_discord

    body = args.summary or artifact.read_text(encoding="utf-8")
    rel = artifact.relative_to(REPO) if artifact.is_relative_to(REPO) else artifact
    if not args.summary:
        body = f"**{args.title}**\n\n{body[:1800]}\n\n*(truncated — full artifact: `{rel}`)*"

    result = post_to_discord(args.agent, args.title, body)
    print("SUCCESS" if result.success else "FAIL", result.message)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
