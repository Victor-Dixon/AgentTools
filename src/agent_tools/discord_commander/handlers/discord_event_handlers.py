"""Discord event handlers — promoted slice (toolbelt-slim)."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

import discord

if TYPE_CHECKING:
    from agent_tools.discord_commander.unified_discord_bot import UnifiedDiscordBot

logger = logging.getLogger(__name__)


class DiscordEventHandlers:
    """Lightweight on_ready / reconnect handlers without GUI coupling."""

    def __init__(self, commander: "UnifiedDiscordBot") -> None:
        self.commander = commander
        self.bot = commander.bot
        self.logger = logging.getLogger(__name__)

    async def handle_on_ready(self) -> None:
        if not hasattr(self.commander, "connection_healthy"):
            self.commander.connection_healthy = True  # type: ignore[attr-defined]
        else:
            self.commander.connection_healthy = True
        self.commander.last_heartbeat = time.time()  # type: ignore[attr-defined]

        if not getattr(self.commander, "_startup_sent", False):
            self.logger.info("Discord Commander ready: %s", self.bot.user)
            self.logger.info("Guilds: %d", len(self.bot.guilds))
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name="Dream.OS swarm")
            )
            self.commander._startup_sent = True  # type: ignore[attr-defined]
        else:
            self.logger.info("Discord Commander reconnected: %s", self.bot.user)

    async def handle_on_disconnect(self) -> None:
        self.commander.connection_healthy = False  # type: ignore[attr-defined]
        self.logger.warning("Discord Commander disconnected")

    async def handle_on_resume(self) -> None:
        self.commander.connection_healthy = True  # type: ignore[attr-defined]
        self.commander.last_heartbeat = time.time()  # type: ignore[attr-defined]
        self.logger.info("Discord Commander resumed session")
