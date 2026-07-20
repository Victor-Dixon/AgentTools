"""!bump prefix (+ slash) — force Agent mode via starter Ctrl+I + Enter (local PyAutoGUI)."""

from __future__ import annotations

import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from agent_tools.discord_commander.agent_message_sender import normalize_agent_id
from agent_tools.discord_commander.bump_bridge import bump_agent, bump_quad

logger = logging.getLogger(__name__)


def _format_bump_embed(result, *, title: str) -> discord.Embed:
    color = discord.Color.green() if result.success else discord.Color.red()
    embed = discord.Embed(title=title, description=result.message[:4000], color=color)
    embed.add_field(name="Action", value=result.action, inline=True)
    if result.error_code:
        embed.add_field(name="Error", value=result.error_code, inline=True)
    if result.data:
        agents = result.data.get("agents")
        if agents:
            embed.add_field(name="Agents", value=", ".join(agents), inline=True)
        status = result.data.get("status")
        if status:
            embed.add_field(name="Status", value=str(status), inline=True)
        report = result.data.get("report")
        if report:
            embed.add_field(name="Report", value=str(report), inline=False)
    return embed


class BumpCommands(commands.Cog):
    """Force Cursor Agent mode: starter_location_box → Ctrl+I → Enter."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bump_slash = app_commands.Group(
            name="bump",
            description="Force Agent mode (starter click + Ctrl+I + Enter)",
        )
        self._register_slash()

    def _register_slash(self) -> None:
        @self.bump_slash.command(name="agent", description="Bump one Agent-N into Agent mode")
        @app_commands.describe(agent="Agent ID (Agent-1 .. Agent-4)")
        async def slash_agent(interaction: discord.Interaction, agent: str) -> None:
            await interaction.response.defer(ephemeral=True)
            result = await asyncio.to_thread(bump_agent, agent, live=True)
            await interaction.followup.send(embed=_format_bump_embed(result, title="Bump Agent"))

        @self.bump_slash.command(name="all", description="Bump all four agents into Agent mode")
        @app_commands.describe(dry_run="Plan only — no PyAutoGUI")
        async def slash_all(interaction: discord.Interaction, dry_run: bool = False) -> None:
            await interaction.response.defer(ephemeral=True)
            result = await asyncio.to_thread(bump_quad, live=not dry_run, dry_run=dry_run)
            await interaction.followup.send(embed=_format_bump_embed(result, title="Bump Quad"))

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self.bump_slash)

    @commands.command(name="bump")
    async def bump_prefix(self, ctx: commands.Context, agent_or_all: str = "") -> None:
        """!bump Agent-N | !bump all — starter → Ctrl+I → Enter."""
        raw = (agent_or_all or "").strip()
        if not raw:
            await ctx.send(
                "**Bump (local PyAutoGUI)**\n"
                "`!bump Agent-1` — force Agent mode for one window\n"
                "`!bump all` — force Agent mode for Agent-1..4\n"
                "Slash: `/bump agent` | `/bump all`"
            )
            return

        lower = raw.lower()
        if lower in ("all", "quad", "4"):
            await ctx.send("Bumping **all four** agents (starter → Ctrl+I → Enter)…")
            result = await asyncio.to_thread(bump_quad, live=True)
            await ctx.send(embed=_format_bump_embed(result, title="Bump Quad"))
            return

        if not normalize_agent_id(raw):
            await ctx.send(f"Invalid agent: {raw}. Use `Agent-1`..`Agent-4` or `all`.")
            return

        await ctx.send(f"Bumping **{raw}** (starter → Ctrl+I → Enter)…")
        result = await asyncio.to_thread(bump_agent, raw, live=True)
        await ctx.send(embed=_format_bump_embed(result, title="Bump Agent"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BumpCommands(bot))
