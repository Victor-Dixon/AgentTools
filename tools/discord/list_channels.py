#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

if not TOKEN:
    print("MISSING_DISCORD_BOT_TOKEN")
    sys.exit(1)

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json",
}

out = []

guilds_resp = requests.get(
    "https://discord.com/api/v10/users/@me/guilds",
    headers=headers,
    timeout=30,
)

guilds_resp.raise_for_status()

guilds = guilds_resp.json()

for guild in guilds:
    guild_id = guild["id"]
    guild_name = guild["name"]

    channels_resp = requests.get(
        f"https://discord.com/api/v10/guilds/{guild_id}/channels",
        headers=headers,
        timeout=30,
    )

    if channels_resp.status_code != 200:
        continue

    channels = channels_resp.json()

    out.append({
        "guild_name": guild_name,
        "guild_id": guild_id,
        "channels": [
            {
                "id": c.get("id"),
                "name": c.get("name"),
                "type": c.get("type"),
            }
            for c in channels
        ],
    })

report_dir = Path("data/reports/discord")
report_dir.mkdir(parents=True, exist_ok=True)

json_path = report_dir / "discord_channel_inventory.json"
md_path = report_dir / "discord_channel_inventory.md"

json_path.write_text(json.dumps(out, indent=2))

lines = ["# Discord Channel Inventory", ""]

for guild in out:
    lines.append(f"## {guild['guild_name']}")
    lines.append("")

    for ch in guild["channels"]:
        lines.append(
            f"- {ch['name']} | id={ch['id']} | type={ch['type']}"
        )

    lines.append("")

md_path.write_text("\n".join(lines))

print(f"GUILDS={len(out)}")
print(f"REPORT_JSON={json_path}")
print(f"REPORT_MD={md_path}")

matches = []

for guild in out:
    for ch in guild["channels"]:
        name = (ch.get("name") or "").lower()

        if "freeride" in name or "investor" in name:
            matches.append((guild["guild_name"], ch["name"], ch["id"]))

print(f"MATCHES={len(matches)}")

for guild_name, ch_name, ch_id in matches:
    print(f"MATCH={guild_name} :: {ch_name} :: {ch_id}")
