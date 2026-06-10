"""Lightweight Discord webhook service.

Adapted from Agent_Cellphone_V2_Repository/src/discord_commander/discord_service.py
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests

from .config import DiscordEnvConfig

logger = logging.getLogger(__name__)


class DiscordService:
    """Post notifications to Discord via webhook URL."""

    def __init__(self, webhook_url: Optional[str] = None, config: Optional[DiscordEnvConfig] = None) -> None:
        self.config = config or DiscordEnvConfig.from_environ()
        self.webhook_url = webhook_url or self.config.webhook_url
        self.session = requests.Session()

    def send_embed(self, payload: dict[str, Any], webhook_url: Optional[str] = None) -> bool:
        url = webhook_url or self.webhook_url
        if not url:
            logger.error("No webhook URL configured")
            return False
        try:
            response = self.session.post(url, json=payload, timeout=10)
            return 200 <= response.status_code < 300
        except Exception:
            logger.exception("Failed to send Discord webhook")
            return False

    def test_webhook_connection(self, webhook_url: Optional[str] = None, dry_run: bool = True) -> bool:
        """Validate webhook URL format. When dry_run=True, does not POST."""
        url = webhook_url or self.webhook_url
        if not url:
            return False
        if dry_run:
            return url.startswith("https://discord.com/api/webhooks/") or url.startswith(
                "https://discordapp.com/api/webhooks/"
            )
        return self.send_embed({"content": "Webhook connectivity test"}, webhook_url=url)
