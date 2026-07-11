"""Onboard prefix + slash commands — local PyAutoGUI only (DreamVault SSOT)."""

from __future__ import annotations
# C2A_SELF_GAS_ROOT_DEFAULTS_041
# Canonical desktop roots for C2A/S2A hard onboard and self-gas routes.
import os as _c2a_self_gas_env_041
_c2a_self_gas_env_041.environ["DREAMVAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["DREAMOS_VAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["VAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["AGENT_CELLPHONE_ROOT"] = r"D:\repos\Agent_Cellphone"
_c2a_self_gas_env_041.environ.setdefault("ALLOW_LIVE_CURSOR_INJECTION", "1")
_c2a_self_gas_env_041.environ.setdefault("DEFAULT_MODE", "pyautogui")
_c2a_self_gas_env_041.environ.setdefault("COORDINATE_MODE", "4-agent-1monitor")
_c2a_self_gas_env_041.environ.setdefault("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor")
_c2a_self_gas_env_041.environ.setdefault("DREAMOS_ALLOW_PYAUTOGUI_FAILSAFE_OVERRIDE", "1")

import asyncio
import logging
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from agent_tools.discord_commander.agent_message_sender import normalize_agent_id
from agent_tools.discord_commander.onboard_bridge import (
    hard_onboard_agent,
    quad_group_onboard,
    quad_onboard_status,
    soft_onboard_agent,
)

logger = logging.getLogger(__name__)


def _format_onboard_embed(result, *, title: str) -> discord.Embed:
    color = discord.Color.green() if result.success else discord.Color.red()
    embed = discord.Embed(title=title, description=result.message[:4000], color=color)
    embed.add_field(name="Action", value=result.action, inline=True)
    if result.error_code:
        embed.add_field(name="Error", value=result.error_code, inline=True)
    if result.data:
        agent = result.data.get("agent")
        if agent:
            embed.add_field(name="Agent", value=str(agent), inline=True)
        readiness = result.data.get("ready_count")
        if readiness is not None:
            total = result.data.get("total_agents", 4)
            embed.add_field(name="Quad ready", value=f"{readiness}/{total}", inline=True)
    return embed


class OnboardingCommands(commands.Cog):
    """Soft/hard/quad onboard from Discord (Windows desktop + Cursor required)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.onboard = app_commands.Group(
            name="onboard",
            description="Local PyAutoGUI onboard (soft / hard / quad group)",
        )
        self._register_slash()

    def _register_slash(self) -> None:
        @self.onboard.command(name="status", description="Quad gas readiness for group onboard")
        async def slash_status(interaction: discord.Interaction) -> None:
            await interaction.response.defer(ephemeral=True)
            result = await asyncio.to_thread(quad_onboard_status)
            await interaction.followup.send(embed=_format_onboard_embed(result, title="Quad Onboard Status"))

        @self.onboard.command(name="soft", description="Soft onboard one agent (session rehydrate + PyAutoGUI)")
        @app_commands.describe(agent="Agent ID (Agent-1 .. Agent-8)")
        async def slash_soft(interaction: discord.Interaction, agent: str) -> None:
            await interaction.response.defer(ephemeral=True)
            result = await asyncio.to_thread(soft_onboard_agent, agent, live=True)
            await interaction.followup.send(embed=_format_onboard_embed(result, title="Soft Onboard"))

        @self.onboard.command(name="hard", description="Hard onboard: closeout old chat → new chat + S2A")
        @app_commands.describe(agent="Agent ID (Agent-1 .. Agent-8)")
        async def slash_hard(interaction: discord.Interaction, agent: str) -> None:
            await interaction.response.defer(ephemeral=True)
            result = await asyncio.to_thread(hard_onboard_agent, agent, live=True)
            await interaction.followup.send(embed=_format_onboard_embed(result, title="Hard Onboard"))

        @self.onboard.command(name="quad", description="Group onboard all quad agents when 4/4 ready")
        @app_commands.describe(
            force="Run even if quad not all ready (operator override)",
            dry_run="Inspect plan only — no PyAutoGUI",
        )
        async def slash_quad(
            interaction: discord.Interaction,
            force: bool = False,
            dry_run: bool = False,
        ) -> None:
            await interaction.response.defer(ephemeral=True)
            result = await asyncio.to_thread(
                quad_group_onboard,
                live=not dry_run,
                dry_run=dry_run,
                force=force,
            )
            await interaction.followup.send(embed=_format_onboard_embed(result, title="Quad Group Onboard"))

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self.onboard)

    @commands.group(name="onboard", invoke_without_command=True)
    async def onboard_prefix(self, ctx: commands.Context) -> None:
        await ctx.send(
            "**Onboard (local PyAutoGUI only)**\n"
            "`!onboard status` — quad readiness\n"
            "`!onboard soft Agent-1` — soft onboard\n"
            "`!onboard hard Agent-1` — hard onboard\n"
            "`!onboard quad` — group onboard when 4/4 ready\n"
            "`!onboard quad force` — operator override\n"
            "Slash: `/onboard status|soft|hard|quad`"
        )

    @onboard_prefix.command(name="status")
    async def prefix_status(self, ctx: commands.Context) -> None:
        result = await asyncio.to_thread(quad_onboard_status)
        await ctx.send(embed=_format_onboard_embed(result, title="Quad Onboard Status"))

    @onboard_prefix.command(name="soft")
    async def prefix_soft(self, ctx: commands.Context, agent_id: str) -> None:
        if not normalize_agent_id(agent_id):
            await ctx.send(f"Invalid agent: {agent_id}")
            return
        await ctx.send(f"Soft onboarding **{agent_id}** via PyAutoGUI…")
        result = await asyncio.to_thread(soft_onboard_agent, agent_id, live=True)
        await ctx.send(embed=_format_onboard_embed(result, title="Soft Onboard"))

    @onboard_prefix.command(name="hard")
    async def prefix_hard(self, ctx: commands.Context, agent_id: str) -> None:
        if not normalize_agent_id(agent_id):
            await ctx.send(f"Invalid agent: {agent_id}")
            return
        await ctx.send(f"Hard onboarding **{agent_id}** (closeout → new chat)…")
        result = await asyncio.to_thread(hard_onboard_agent, agent_id, live=True)
        await ctx.send(embed=_format_onboard_embed(result, title="Hard Onboard"))

    @onboard_prefix.command(name="quad")
    async def prefix_quad(self, ctx: commands.Context, *, flags: str = "") -> None:
        flag_text = flags.lower()
        force = "force" in flag_text
        dry_run = "dry" in flag_text
        label = "dry-run" if dry_run else ("force" if force else "live")
        await ctx.send(f"Quad group onboard ({label})…")
        result = await asyncio.to_thread(
            quad_group_onboard,
            live=not dry_run,
            dry_run=dry_run,
            force=force,
        )
        await ctx.send(embed=_format_onboard_embed(result, title="Quad Group Onboard"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnboardingCommands(bot))
