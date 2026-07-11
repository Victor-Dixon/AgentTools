"""Messaging prefix commands — promoted slice (toolbelt-adapted)."""

from __future__ import annotations

import logging
from typing import Any

import discord
from discord.ext import commands

from agent_tools.discord_commander.agent_message_sender import (
    broadcast_agent_messages,
    send_agent_message,
)
from agent_tools.discord_commander.messaging_delivery_log import delivery_jsonl_path
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
            logger.info(
                "!message invoked by=%s agent=%s len=%d",
                getattr(ctx.author, "name", "unknown"),
                agent_id,
                len(message),
            )
            result = send_agent_message(
                agent_id=agent_id,
                message=message,
                discord_user=ctx.author,
                priority="regular",
                source="discord_bot_command",
            )

            data = result.data or {}
            final_status = str(data.get("final_status") or ("SENT" if result.success else "FAILED"))
            agent = result.agent or agent_id
            transport = data.get("transport", "unknown")
            template_cat = data.get("message_template") or data.get("template_category") or "raw"
            color = discord.Color.green() if final_status == "SENT" else discord.Color.red()

            embed = discord.Embed(
                title=f"!message {final_status}",
                description=result.message[:2000],
                color=color,
            )
            embed.add_field(name="Target", value=f"**{agent}**", inline=True)
            embed.add_field(name="Transport", value=str(transport), inline=True)
            embed.add_field(name="Template", value=str(template_cat), inline=True)
            roots = data.get("messaging_roots")
            if isinstance(roots, dict):
                embed.add_field(
                    name="Roots",
                    value=(
                        f"agent-tools: `{roots.get('agent_tools_root', '?')}`\n"
                        f"coords: `{roots.get('coords_root', '?')}`"
                    )[:900],
                    inline=False,
                )
            layout_note = data.get("layout_note")
            if layout_note:
                embed.add_field(name="Layout note", value=str(layout_note)[:900], inline=False)
            bus_attempt = data.get("bus_attempt")
            if isinstance(bus_attempt, dict) and not bus_attempt.get("ok"):
                embed.add_field(
                    name="Bus note",
                    value=str(bus_attempt.get("detail") or "bus unavailable")[:900],
                    inline=False,
                )
            if result.error_code:
                embed.add_field(name="Error", value=str(result.error_code), inline=True)
            embed.add_field(
                name="Audit log",
                value=f"`{delivery_jsonl_path()}`",
                inline=False,
            )
            message_chunks = chunk_field_value(message)
            embed.add_field(name="Message", value=message_chunks[0], inline=False)
            for index, chunk in enumerate(message_chunks[1:], start=2):
                embed.add_field(
                    name=f"Message (continued {index}/{len(message_chunks)})",
                    value=chunk,
                    inline=False,
                )
            await ctx.send(embed=embed)
            if final_status == "FAILED":
                logger.warning(
                    "!message failed agent=%s error=%s detail=%s",
                    agent_id,
                    result.error_code,
                    result.message,
                )
        except Exception as exc:
            self.logger.error("message command failed: %s", exc, exc_info=True)
            await ctx.send(f"Error: {exc}")

    @commands.command(name="broadcast", aliases=["swarm"], description="Broadcast message to all agents")
    async def broadcast(self, ctx: commands.Context, *, message: str) -> None:
        """Broadcast to Agent-1..8: `!broadcast Check your inboxes`."""
        import asyncio

        try:
            logger.info(
                "!broadcast invoked by=%s len=%d",
                getattr(ctx.author, "name", "unknown"),
                len(message),
            )
            await ctx.send("Broadcasting to swarm via PyAutoGUI (sequential)…")
            result = await asyncio.to_thread(
                broadcast_agent_messages,
                message,
                discord_user=ctx.author,
                source="discord_bot_broadcast",
            )
            lines = [result.message]
            if result.delivered:
                lines.append(f"✅ {', '.join(result.delivered)}")
            if result.failed:
                lines.append(f"❌ {', '.join(result.failed)}")
            lines.append(f"Log: `{delivery_jsonl_path()}`")
            await ctx.send("\n".join(lines))
        except Exception as exc:
            self.logger.error("broadcast command failed: %s", exc, exc_info=True)
            await ctx.send(f"Error: {exc}")


async def setup(bot: commands.Bot, gui_controller: Any | None = None) -> None:
    await bot.add_cog(MessagingCommands(bot, gui_controller))
