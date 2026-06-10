"""Outbound Discord router — routes agent posts to per-agent or default webhooks.

Built for agent-tools toolbelt (salvage lineage: discord_service + post_to_discord_router).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .config import DiscordEnvConfig, mask_secret
from .discord_service import DiscordService
from .models import CommandResult, PostMessage

logger = logging.getLogger(__name__)


class OutboundRouter:
    """Route outbound Discord messages to the correct webhook."""

    def __init__(self, config: Optional[DiscordEnvConfig] = None) -> None:
        self.config = config or DiscordEnvConfig.from_environ()
        self.service = DiscordService(config=self.config)

    def resolve_webhook(self, agent: str) -> Optional[str]:
        return self.config.webhook_for_agent(agent)

    def post(self, post: PostMessage) -> CommandResult:
        webhook = self.resolve_webhook(post.agent)
        if not webhook:
            return CommandResult(
                success=False,
                message=f"No webhook configured for {post.agent}",
                agent=post.agent,
                error_code="WEBHOOK_MISSING",
            )

        payload = post.to_embed_payload()
        if post.dry_run:
            return CommandResult(
                success=True,
                message="Dry-run: message would be posted",
                agent=post.agent,
                data={
                    "webhook": mask_secret(webhook),
                    "title": post.title,
                    "message_length": len(post.message),
                },
            )

        ok = self.service.send_embed(payload, webhook_url=webhook)
        return CommandResult(
            success=ok,
            message="Posted to Discord" if ok else "Discord webhook POST failed",
            agent=post.agent,
            error_code=None if ok else "POST_FAILED",
        )

    def post_from_file(
        self,
        agent: str,
        title: str,
        message_file: Path,
        dry_run: bool = False,
    ) -> CommandResult:
        if not message_file.exists():
            return CommandResult(
                success=False,
                message=f"Message file not found: {message_file}",
                agent=agent,
                error_code="FILE_NOT_FOUND",
            )
        body = message_file.read_text(encoding="utf-8")
        return self.post(PostMessage(agent=agent, title=title, message=body, dry_run=dry_run))


def post_to_discord(
    agent: str,
    title: str,
    message: str,
    *,
    dry_run: bool = False,
    message_file: Optional[Path] = None,
) -> CommandResult:
    """Convenience entry point used by CLI and tools/post_to_discord_router.py."""
    router = OutboundRouter()
    if message_file is not None:
        return router.post_from_file(agent, title, message_file, dry_run=dry_run)
    return router.post(PostMessage(agent=agent, title=title, message=message, dry_run=dry_run))
