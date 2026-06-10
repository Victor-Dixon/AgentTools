"""Discord Commander status reporting."""

from __future__ import annotations

import os
from typing import Optional

from .config import DiscordEnvConfig, REQUIRED_ENV_VARS, mask_secret
from .models import CommandResult


def collect_status(environ: Optional[dict[str, str]] = None) -> CommandResult:
    """Report configured/missing env vars without printing secret values."""
    config = DiscordEnvConfig.from_environ(environ or dict(os.environ))

    env_status: dict[str, str] = {}
    for var in REQUIRED_ENV_VARS:
        value = (environ or os.environ).get(var)
        env_status[var] = "set" if value else "missing"

    for agent in range(1, 9):
        var = f"DISCORD_WEBHOOK_AGENT_{agent}"
        value = (environ or os.environ).get(var)
        env_status[var] = "set" if value else "missing"

    return CommandResult(
        success=True,
        message="Discord Commander status",
        data={
            "env": env_status,
            "agent_webhooks_configured": sorted(config.agent_webhooks.keys()),
            "default_webhook": mask_secret(config.webhook_url),
            "bot_token": mask_secret(config.bot_token),
            "guild_id": config.guild_id or "<unset>",
        },
    )
