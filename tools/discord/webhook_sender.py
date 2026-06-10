#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


@dataclass
class DiscordWebhookResult:
    ok: bool
    status_code: int | None
    message: str


def _resolve_webhook_url(webhook_url: str | None = None) -> str | None:
    return (
        webhook_url
        or os.environ.get("DISCORD_TRADING_WEBHOOK_URL")
        or os.environ.get("DISCORD_WEBHOOK_URL")
    )


def send_payload(
    payload: dict[str, Any],
    webhook_url: str | None = None,
    timeout: int = 20,
) -> DiscordWebhookResult:
    url = _resolve_webhook_url(webhook_url)

    if not url:
        return DiscordWebhookResult(False, None, "missing Discord webhook URL env")

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
    except Exception as exc:
        return DiscordWebhookResult(False, None, str(exc))

    if 200 <= resp.status_code < 300:
        return DiscordWebhookResult(True, resp.status_code, "sent")

    return DiscordWebhookResult(False, resp.status_code, resp.text[:500])


def send_payload_file(path: str | Path, webhook_url: str | None = None) -> DiscordWebhookResult:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return send_payload(payload, webhook_url=webhook_url)
