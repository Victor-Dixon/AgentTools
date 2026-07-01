"""HTTP client for MaskZero discord-link API (phase 1 account bridge)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import requests


DEFAULT_API_URL = "https://maskzero.site/api/discord-link.php"


@dataclass(frozen=True)
class LinkConsumeResult:
    ok: bool
    message: str
    link: dict[str, Any] | None = None


def api_url() -> str:
    return os.getenv("MASKZERO_DISCORD_LINK_API_URL", DEFAULT_API_URL).strip() or DEFAULT_API_URL


def bot_secret() -> str:
    return os.getenv("MASKZERO_DISCORD_BOT_SECRET", "").strip()


def consume_link_code(
    code: str,
    discord_user_id: str,
    discord_guild_id: str = "",
    *,
    timeout: float = 15.0,
) -> LinkConsumeResult:
    secret = bot_secret()
    if not secret:
        return LinkConsumeResult(ok=False, message="MASKZERO_DISCORD_BOT_SECRET not configured")

    code = code.strip().upper()
    if not code:
        return LinkConsumeResult(ok=False, message="Link code required")

    url = f"{api_url()}?{urlencode({'action': 'consume'})}"
    payload = {
        "code": code,
        "discord_user_id": str(discord_user_id),
        "discord_guild_id": str(discord_guild_id or ""),
    }
    headers = {
        "Content-Type": "application/json",
        "X-MaskZero-Bot-Secret": secret,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        return LinkConsumeResult(ok=False, message=f"MaskZero API unreachable: {exc}")

    try:
        data = resp.json()
    except ValueError:
        return LinkConsumeResult(ok=False, message=f"Invalid API response (HTTP {resp.status_code})")

    if not isinstance(data, dict):
        return LinkConsumeResult(ok=False, message="Invalid API payload")

    if data.get("ok") and data.get("linked"):
        link = data.get("link")
        return LinkConsumeResult(
            ok=True,
            message="Account linked",
            link=link if isinstance(link, dict) else None,
        )

    msg = str(data.get("message") or f"Link failed (HTTP {resp.status_code})")
    return LinkConsumeResult(ok=False, message=msg)
