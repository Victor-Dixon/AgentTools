"""Messaging prefix commands — promoted slice (toolbelt-adapted)."""

from __future__ import annotations

import logging
from typing import Any

import discord
from discord.ext import commands

from agent_tools.discord_commander.agent_message_sender import send_agent_message
from agent_tools.discord_commander.utils.message_chunking import chunk_field_value

logger = logging.getLogger(__name__)


class MessagingCommands(commands.Cog):
    """Direct agent messaging for operator control."""

    def __init__(self, bot: commands.Bot, gui_controller: Any | None = None) -> None:
        self.bot = bot
        self.gui_controller = gui_controller
        self.logger = logging.getLogger(__name__)

    @commands.command(name="message", description="Send message to agent")
    async def message(self, ctx: commands.Context, agent_id: str, *, message: str) -> None:
        """Send direct message to agent: `!message Agent-1 Check your inbox`."""
        try:
            result = send_agent_message(
                agent_id=agent_id,
                message=message,
                discord_user=ctx.author,
                priority="regular",
            )

            if result.success:
                agent = result.agent or agent_id
                embed = discord.Embed(
                    title="Message Sent",
                    description=f"Delivered to **{agent}**",
                    color=discord.Color.green(),
                )
                transport = (result.data or {}).get("transport", "unknown")
                embed.add_field(name="Transport", value=str(transport), inline=True)
                message_chunks = chunk_field_value(message)
                embed.add_field(name="Message", value=message_chunks[0], inline=False)
                for index, chunk in enumerate(message_chunks[1:], start=2):
                    embed.add_field(
                        name=f"Message (continued {index}/{len(message_chunks)})",
                        value=chunk,
                        inline=False,
                    )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Failed to send message to {agent_id}: {result.message}")
        except Exception as exc:
            self.logger.error("message command failed: %s", exc, exc_info=True)
            await ctx.send(f"Error: {exc}")


async def setup(bot: commands.Bot, gui_controller: Any | None = None) -> None:
    await bot.add_cog(MessagingCommands(bot, gui_controller))
