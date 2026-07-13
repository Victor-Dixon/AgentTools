#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

AGENTTOOLS = Path.home() / "projects" / "AgentTools"
sys.path.insert(0, str(AGENTTOOLS))

from tools.discord.config import resolve_discord_config  # noqa: E402

OUT = Path("data/reports/discord/discord_structure.json")
OUT_MD = Path("data/reports/discord/discord_structure.md")


def api(path: str, token: str):
    r = requests.get(
        f"https://discord.com/api/v10{path}",
        headers={"Authorization": f"Bot {token}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def main() -> int:
    config = resolve_discord_config()

    if not config["token_present"]:
        print(f"SECRETS_PATH={config['secrets_path']}")
        print("TOKEN_PRESENT=FAIL")
        print("EXPECTED_ONE_OF=DISCORD_BOT_TOKEN,FREERIDEINVESTOR_DISCORD_BOT_TOKEN,DISCORD_FREERIDEINVESTOR_BOT_TOKEN,FREERIDE_DISCORD_BOT_TOKEN,DISCORD_TOKEN")
        raise SystemExit("MISSING_DISCORD_TOKEN")

    token = str(config["bot_token"])
    guild_id = str(config["guild_id"])

    guild = api(f"/guilds/{guild_id}", token)
    channels = api(f"/guilds/{guild_id}/channels", token)

    categories = {
        ch["id"]: ch["name"]
        for ch in channels
        if ch.get("type") == 4
    }

    data = {
        "guild": {
            "id": guild["id"],
            "name": guild["name"],
        },
        "config": {
            "token_env_name": config["token_env_name"],
            "guild_env_name": config["guild_env_name"],
            "guild_id": guild_id,
        },
        "channels": [],
    }

    lines = [
        "# Discord Structure",
        "",
        f"Guild: {guild['name']}",
        f"Guild ID: {guild_id}",
        f"Token Env: {config['token_env_name']}",
        "",
    ]

    for ch in sorted(channels, key=lambda x: x.get("position", 0)):
        if ch.get("type") == 4:
            lines.append(f"## {ch['name']}")
            continue

        parent = categories.get(ch.get("parent_id"), "UNCATEGORIZED")

        data["channels"].append({
            "id": ch.get("id"),
            "name": ch.get("name"),
            "type": ch.get("type"),
            "category": parent,
            "position": ch.get("position"),
        })

        lines.append(f"- [{parent}] #{ch.get('name')} | id={ch.get('id')} | type={ch.get('type')}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"GUILD={guild['name']}")
    print(f"CHANNELS={len(channels)}")
    print(f"JSON={OUT}")
    print(f"MD={OUT_MD}")
    print("DISCORD_STRUCTURE_EXPORT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
