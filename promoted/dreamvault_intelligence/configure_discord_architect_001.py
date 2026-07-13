#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from dream_secrets import LOCAL, REPORT_DIR, parse_env_file, set_secret

ROOT = Path.cwd()


def env_value(name: str, local: dict[str, str]) -> str:
    return os.environ.get(name, "").strip() or local.get(name, "").strip()


def create_webhook(bot_token: str, channel_id: str, webhook_name: str) -> str:
    url = f"https://discord.com/api/v10/channels/{channel_id}/webhooks"
    req = urllib.request.Request(
        url,
        data=json.dumps({"name": webhook_name}).encode("utf-8"),
        headers={
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
            "User-Agent": "DreamOS-DiscordArchitect/001",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return f"https://discord.com/api/webhooks/{data['id']}/{data['token']}"


def post_test_card(webhook_url: str) -> bool:
    payload = {
        "username": "Dream.OS Discord Architect",
        "embeds": [{
            "title": "Dream.OS Discord Architect configured",
            "description": "Secret broker + webhook route verified.",
            "fields": [
                {"name": "Status", "value": "PASS", "inline": True},
                {"name": "Secrets", "value": "redacted", "inline": True},
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return 200 <= resp.status < 300


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure Discord Architect through Dream.OS Secret Broker")
    parser.add_argument("--bot", default="discord_architect")
    parser.add_argument("--channel", default="trading")
    parser.add_argument("--create-webhook", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    local = parse_env_file(LOCAL)
    bot_token = env_value("DISCORD_BOT_TOKEN", local)
    app_id = env_value("DISCORD_APPLICATION_ID", local)
    channel_id = env_value("DISCORD_TRADING_CHANNEL_ID", local)
    webhook_url = env_value("DISCORD_TRADING_WEBHOOK_URL", local)
    webhook_name = env_value("DISCORD_TRADING_WEBHOOK_NAME", local) or "Dream.OS Trading Sentinel"

    missing = []
    if not bot_token and args.create_webhook:
        missing.append("DISCORD_BOT_TOKEN")
    if not channel_id:
        missing.append("DISCORD_TRADING_CHANNEL_ID")
    if not app_id:
        missing.append("DISCORD_APPLICATION_ID")

    if missing:
        print("DISCORD_ARCHITECT_CONFIGURE=FAIL")
        print("MISSING=" + ",".join(missing))
        return 2

    created = False
    posted = False

    if args.dry_run:
        status = "DRY_RUN_PASS"
    else:
        if args.create_webhook and not webhook_url:
            webhook_url = create_webhook(bot_token, channel_id, webhook_name)
            set_secret("discord.trading.webhook.url", webhook_url)
            created = True
        if args.test:
            if not webhook_url:
                print("DISCORD_ARCHITECT_CONFIGURE=FAIL")
                print("MISSING=DISCORD_TRADING_WEBHOOK_URL")
                return 3
            posted = post_test_card(webhook_url)
        status = "PASS"

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "status": status,
        "bot": args.bot,
        "channel": args.channel,
        "application_id_set": bool(app_id),
        "channel_id_set": bool(channel_id),
        "bot_token_set": bool(bot_token),
        "webhook_url_set": bool(webhook_url),
        "webhook_created": created,
        "test_posted": posted,
        "secrets_redacted": True,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (REPORT_DIR / "discord_architect_latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("DISCORD_ARCHITECT_CONFIGURE=" + status)
    print(f"BOT={args.bot}")
    print(f"CHANNEL={args.channel}")
    print(f"WEBHOOK_CREATED={created}")
    print(f"TEST_POSTED={posted}")
    print("SECRETS_REDACTED=TRUE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
