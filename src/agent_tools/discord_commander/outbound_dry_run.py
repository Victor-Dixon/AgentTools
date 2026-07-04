"""Outbound Discord dry-run — validates webhook configuration without posting secrets."""

from __future__ import annotations

import os
from typing import Optional

from .config import DiscordEnvConfig, mask_secret
from .models import CommandResult


def outbound_dry_run(environ: Optional[dict[str, str]] = None) -> CommandResult:
    """Validate outbound webhook configuration (no network, no secret printing)."""
    config = DiscordEnvConfig.from_environ(environ or dict(os.environ))

    checks: list[dict[str, str]] = []
    default_ok = False
    if config.webhook_url:
        default_ok = _valid_webhook_format(config.webhook_url)
        checks.append(
            {
                "target": "DISCORD_WEBHOOK_URL",
                "status": "ok" if default_ok else "invalid_format",
                "masked": mask_secret(config.webhook_url),
            }
        )
    else:
        checks.append({"target": "DISCORD_WEBHOOK_URL", "status": "unset", "masked": "<unset>"})

    agent_results: dict[str, str] = {}
    for agent, url in sorted(config.agent_webhooks.items()):
        ok = _valid_webhook_format(url)
        agent_results[agent] = "ok" if ok else "invalid_format"
        env_name = f"DISCORD_WEBHOOK_{agent.upper().replace('-', '_')}"
        checks.append(
            {
                "target": env_name,
                "status": agent_results[agent],
                "masked": mask_secret(url),
            }
        )

    any_ok = default_ok or any(status == "ok" for status in agent_results.values())
    if not any_ok:
        return CommandResult(
            success=False,
            message="No valid outbound webhook configured",
            error_code="WEBHOOK_MISSING",
            data={"checks": checks},
        )

    return CommandResult(
        success=True,
        message="Outbound dry-run passed (configuration valid, no POST performed)",
        data={"checks": checks},
    )


def _valid_webhook_format(url: str) -> bool:
    return url.startswith("https://discord.com/api/webhooks/") or url.startswith(
        "https://discordapp.com/api/webhooks/"
    )
