from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


DEFAULT_SECRETS = Path.home() / ".config" / "dreamos" / "secrets.env"

TOKEN_NAMES = [
    "DISCORD_BOT_TOKEN",
    "FREERIDEINVESTOR_DISCORD_BOT_TOKEN",
    "DISCORD_FREERIDEINVESTOR_BOT_TOKEN",
    "FREERIDE_DISCORD_BOT_TOKEN",
    "DISCORD_TOKEN",
]

GUILD_NAMES = [
    "DISCORD_GUILD_ID",
    "DISCORD_TARGET_GUILD_ID",
    "FREERIDEINVESTOR_DISCORD_GUILD_ID",
]

DEFAULT_FREERIDE_GUILD_ID = "1375298054357254257"


def parse_export_file(path: Path = DEFAULT_SECRETS) -> dict[str, str]:
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export "):]

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def first_value(names: Iterable[str], file_values: dict[str, str]) -> tuple[str | None, str | None]:
    for name in names:
        value = os.environ.get(name) or file_values.get(name)
        if value:
            return name, value
    return None, None


def resolve_discord_config(secrets_path: Path = DEFAULT_SECRETS) -> dict[str, str | bool | None]:
    file_values = parse_export_file(secrets_path)

    token_name, token = first_value(TOKEN_NAMES, file_values)
    guild_name, guild_id = first_value(GUILD_NAMES, file_values)

    if not guild_id:
        guild_name = "DEFAULT_FREERIDE_GUILD_ID"
        guild_id = DEFAULT_FREERIDE_GUILD_ID

    return {
        "token_present": bool(token),
        "token_env_name": token_name,
        "bot_token": token,
        "guild_id": guild_id,
        "guild_env_name": guild_name,
        "secrets_path": str(secrets_path),
    }
