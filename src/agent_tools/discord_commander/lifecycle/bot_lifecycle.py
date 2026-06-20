"""Bot lifecycle — promoted slice (loads agent-management cog only)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from agent_tools.discord_commander.unified_discord_bot import UnifiedDiscordBot

logger = logging.getLogger(__name__)


class BotLifecycleManager:
    """Toolbelt lifecycle: promote slice cogs only — no GUI/trading/webhook loads."""

    def __init__(self, commander: "UnifiedDiscordBot") -> None:
        self.commander = commander
        self.bot = commander.bot
        self.logger = logging.getLogger(__name__)

    async def setup_hook(self) -> None:
        from agent_tools.discord_commander.commands.agent_management_commands import (
            AgentManagementCommands,
        )

        await self.bot.add_cog(AgentManagementCommands(self.bot, gui_controller=None))
        self.logger.info("Promoted slice: AgentManagementCommands loaded")

    async def send_startup_message(self) -> None:
        channel = self._first_text_channel()
        if not channel:
            self.logger.info("No text channel for startup message (toolbelt mode)")
            return
        embed = discord.Embed(
            title="Discord Commander",
            description="Toolbelt slice active — use `/help` or `!heal status`",
            color=0x5865F2,
        )
        try:
            await channel.send(embed=embed)
        except discord.HTTPException as exc:
            self.logger.warning("Startup message skipped: %s", exc)

    def _first_text_channel(self) -> discord.TextChannel | None:
        for guild in self.bot.guilds:
            for text_channel in guild.text_channels:
                return text_channel
        return None

    async def close(self) -> None:
        self.logger.info("Discord Commander slice lifecycle closing")
        self.commander._intentional_shutdown = True  # type: ignore[attr-defined]
