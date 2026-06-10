"""Environment configuration for Discord Commander (names only, no secret values)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Optional

REQUIRED_ENV_VARS = (
    "DISCORD_BOT_TOKEN",
    "DISCORD_GUILD_ID",
    "DISCORD_WEBHOOK_URL",
)

AGENT_WEBHOOK_ENV_PATTERN = re.compile(r"^DISCORD_WEBHOOK_AGENT_([1-8])$")


@dataclass
class DiscordEnvConfig:
    """Resolved Discord environment configuration."""

    bot_token: Optional[str] = None
    guild_id: Optional[str] = None
    webhook_url: Optional[str] = None
    agent_webhooks: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_environ(cls, environ: Optional[dict[str, str]] = None) -> "DiscordEnvConfig":
        env = environ if environ is not None else os.environ
        agent_webhooks: dict[str, str] = {}
        for key, value in env.items():
            match = AGENT_WEBHOOK_ENV_PATTERN.match(key)
            if match and value:
                agent_webhooks[f"Agent-{match.group(1)}"] = value

        return cls(
            bot_token=env.get("DISCORD_BOT_TOKEN"),
            guild_id=env.get("DISCORD_GUILD_ID"),
            webhook_url=env.get("DISCORD_WEBHOOK_URL"),
            agent_webhooks=agent_webhooks,
        )

    def missing_required(self) -> list[str]:
        missing: list[str] = []
        if not self.bot_token:
            missing.append("DISCORD_BOT_TOKEN")
        if not self.guild_id:
            missing.append("DISCORD_GUILD_ID")
        if not self.webhook_url and not self.agent_webhooks:
            missing.append("DISCORD_WEBHOOK_URL (or DISCORD_WEBHOOK_AGENT_1..8)")
        return missing

    def webhook_for_agent(self, agent: str) -> Optional[str]:
        normalized = agent.strip()
        if normalized in self.agent_webhooks:
            return self.agent_webhooks[normalized]
        if normalized.startswith("Agent-") and normalized[6:].isdigit():
            agent_url = self.agent_webhooks.get(normalized)
            if agent_url:
                return agent_url
        return self.webhook_url


def mask_secret(value: Optional[str], visible: int = 4) -> str:
    """Return a safe display form of a secret (never prints full value)."""
    if not value:
        return "<unset>"
    if len(value) <= visible * 2:
        return "<redacted>"
    return f"{value[:visible]}…{value[-visible:]}"
