#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.environ.get("DISCORD_TRADING_CHANNEL_ID")
WEBHOOK_NAME = os.environ.get("DISCORD_TRADING_WEBHOOK_NAME", "Dream.OS Trading Bot")

if not TOKEN:
    print("MISSING_DISCORD_BOT_TOKEN")
    sys.exit(2)

if not CHANNEL_ID:
    print("MISSING_DISCORD_TRADING_CHANNEL_ID")
    sys.exit(2)

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json",
}

payload = {
    "name": WEBHOOK_NAME,
}

resp = requests.post(
    f"https://discord.com/api/v10/channels/{CHANNEL_ID}/webhooks",
    headers=headers,
    json=payload,
    timeout=30,
)

if resp.status_code not in (200, 201):
    print("CREATE_WEBHOOK=FAIL")
    print(f"STATUS={resp.status_code}")
    print(resp.text)
    sys.exit(1)

data = resp.json()
url = data.get("url")

if not url:
    print("CREATE_WEBHOOK=FAIL missing_url")
    print(json.dumps(data, indent=2))
    sys.exit(1)

report_dir = Path("data/reports/discord")
report_dir.mkdir(parents=True, exist_ok=True)
(report_dir / "created_trading_webhook_redacted.json").write_text(
    json.dumps(
        {
            "id": data.get("id"),
            "channel_id": data.get("channel_id"),
            "guild_id": data.get("guild_id"),
            "name": data.get("name"),
            "url_present": bool(url),
        },
        indent=2,
    )
)

secrets = Path.home() / ".config" / "dreamos" / "secrets.env"
existing = secrets.read_text() if secrets.exists() else ""

lines = [
    line for line in existing.splitlines()
    if not line.startswith("DISCORD_TRADING_WEBHOOK_URL=")
]

lines.append(f'export DISCORD_TRADING_WEBHOOK_URL="{url}"')
secrets.write_text("\n".join(lines) + "\n")
secrets.chmod(0o600)

print("CREATE_WEBHOOK=PASS")
print(f"WEBHOOK_ID={data.get('id')}")
print(f"CHANNEL_ID={data.get('channel_id')}")
print(f"SECRETS_FILE={secrets}")
print("URL_STORED=PASS")
