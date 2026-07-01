"""Bot lifecycle — promoted slice (loads agent-management cog only)."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from agent_tools.discord_commander.unified_discord_bot import UnifiedDiscordBot

logger = logging.getLogger(__name__)

DEFAULT_COMMANDER_CHANNEL_NAME = "command-controller"


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
        from agent_tools.discord_commander.commands.messaging_commands import (
            MessagingCommands,
        )
        from agent_tools.discord_commander.commands.maskzero_connect_commands import (
            MaskZeroConnectCommands,
        )
        from agent_tools.discord_commander.commands.restored_legacy_commands import (
            RestoredLegacyCommands,
        )

        await self.bot.add_cog(AgentManagementCommands(self.bot, gui_controller=None))
        await self.bot.add_cog(MessagingCommands(self.bot, gui_controller=None))
        await self.bot.add_cog(RestoredLegacyCommands(self.bot))
        await self.bot.add_cog(MaskZeroConnectCommands(self.bot))
        self.logger.info(
            "Promoted slice: AgentManagement + Messaging + RestoredLegacyCommands + MaskZeroConnect loaded"
        )

    async def send_startup_message(self) -> None:
        channel = self._resolve_commander_channel()
        if not channel:
            self.logger.info("No commander channel for startup message (toolbelt mode)")
            return
        from agent_tools.discord_commander.views.agent_messaging_view import (
            AgentMessagingGUIView,
        )

        embed = discord.Embed(
            title="Discord Commander",
            description=(
                "Swarm Commander online — use `/gui`, `/help`, `!message Agent-1 <msg>`, or `!heal status`"
            ),
            color=0x5865F2,
        )
        embed.set_footer(text=f"channel={channel.name}")
        try:
            await channel.send(embed=embed, view=AgentMessagingGUIView())
            self.logger.info("Startup GUI posted to #%s (%s)", channel.name, channel.id)
        except discord.HTTPException as exc:
            self.logger.warning("Startup message skipped: %s", exc)

    def _resolve_commander_channel(self) -> discord.TextChannel | None:
        channel_id = os.getenv("DISCORD_COMMANDER_CHANNEL_ID", "").strip()
        if channel_id.isdigit():
            for guild in self.bot.guilds:
                ch = guild.get_channel(int(channel_id))
                if isinstance(ch, discord.TextChannel):
                    return ch
        channel_name = os.getenv(
            "DISCORD_COMMANDER_CHANNEL_NAME", DEFAULT_COMMANDER_CHANNEL_NAME
        ).strip()
        if channel_name:
            for guild in self.bot.guilds:
                for text_channel in guild.text_channels:
                    if text_channel.name == channel_name:
                        return text_channel
        return self._first_text_channel()

    def _first_text_channel(self) -> discord.TextChannel | None:
        for guild in self.bot.guilds:
            for text_channel in guild.text_channels:
                return text_channel
        return None

    async def close(self) -> None:
        self.logger.info("Discord Commander slice lifecycle closing")
        self.commander._intentional_shutdown = True  # type: ignore[attr-defined]
