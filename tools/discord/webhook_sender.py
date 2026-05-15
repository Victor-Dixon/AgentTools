#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DiscordWebhookResult:
    ok: bool
    status_code: int | None
    message: str


def send_payload(
    payload: dict[str, Any],
    webhook_url: str | None = None,
    timeout: int = 20,
) -> DiscordWebhookResult:
    url = webhook_url or os.environ.get("DISCORD_TRADING_WEBHOOK_URL") or os.environ.get("DISCORD_WEBHOOK_URL")

    if not url:
        return DiscordWebhookResult(False, None, "missing Discord webhook URL env")

    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return DiscordWebhookResult(True, resp.status, "sent")
    except Exception as exc:
        return DiscordWebhookResult(False, None, str(exc))


def send_payload_file(path: str | Path, webhook_url: str | None = None) -> DiscordWebhookResult:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return send_payload(payload, webhook_url=webhook_url)
