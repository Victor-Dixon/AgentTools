"""Restored legacy slash/prefix commands — verified tier-1 from V2 Commander."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from agent_tools.discord_commander.agent_message_sender import (
    broadcast_agent_messages,
    normalize_agent_id,
    send_agent_message,
)
from agent_tools.discord_commander.swarm_status_helper import (
    agent_row,
    list_swarm_agents,
    read_swarm_statuses,
    status_emoji,
    vault_root,
)
from agent_tools.discord_commander.views.agent_messaging_view import AgentMessagingGUIView
from agent_tools.discord_commander.views.help_view import HelpGUIView
from agent_tools.discord_commander.views.message_modals import QuickSendModal

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

RESTORED_SLASH = (
    "/send",
    "/swarm",
    "/broadcast",
    "/agents",
    "/agent-status",
    "/commands",
    "/swarm-help",
    "/info",
    "/gui",
    "/onboard",
)


class RestoredLegacyCommands(commands.Cog):
    """Tier-1 restored commands from Agent_Cellphone_V2 Discord Commander."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _broadcast(self, message: str, user: discord.abc.User) -> tuple[list[str], list[str]]:
        import asyncio

        result = await asyncio.to_thread(
            broadcast_agent_messages,
            message,
            discord_user=user,
            source="discord_slash_swarm",
        )
        return result.delivered, result.failed

    @app_commands.command(name="send", description="Send message to a specific agent")
    @app_commands.describe(agent="Agent ID (Agent-1 .. Agent-8)", message="Message body")
    async def send_slash(self, interaction: discord.Interaction, agent: str, message: str) -> None:
        normalized = normalize_agent_id(agent)
        if not normalized:
            await interaction.response.send_message(f"Invalid agent: {agent}", ephemeral=True)
            return
        result = send_agent_message(
            normalized,
            message,
            discord_user=interaction.user,
            source="discord_slash_send",
        )
        if result.success:
            await interaction.response.send_message(
                f"✅ Sent to **{normalized}** ({result.data.get('transport', '?')})",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(f"❌ {result.message}", ephemeral=True)

    @app_commands.command(name="swarm", description="Broadcast message to all agents")
    @app_commands.describe(message="Message for the swarm")
    async def swarm_slash(self, interaction: discord.Interaction, message: str) -> None:
        await interaction.response.defer(ephemeral=True)
        delivered, failed = await self._broadcast(message, interaction.user)
        text = f"Delivered: {len(delivered)}/{len(list_swarm_agents())}"
        if failed:
            text += f"\nFailed: {', '.join(failed)}"
        await interaction.followup.send(text, ephemeral=True)

    @app_commands.command(name="broadcast", description="Alias for /swarm — broadcast to all agents")
    @app_commands.describe(message="Message for the swarm")
    async def broadcast_slash(self, interaction: discord.Interaction, message: str) -> None:
        await self.swarm_slash(interaction, message)

    @app_commands.command(name="agents", description="List all swarm agents")
    async def agents_slash(self, interaction: discord.Interaction) -> None:
        statuses = read_swarm_statuses()
        embed = discord.Embed(title="Swarm Agents", color=0x5865F2)
        for agent_id in list_swarm_agents():
            row = agent_row(agent_id, statuses)
            embed.add_field(
                name=f"{status_emoji(row['status'])} {agent_id}",
                value=row["mission"] or row["status"],
                inline=True,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="agent-status", description="Detailed status for one agent")
    @app_commands.describe(agent="Agent ID")
    async def agent_status_slash(self, interaction: discord.Interaction, agent: str) -> None:
        normalized = normalize_agent_id(agent)
        if not normalized:
            await interaction.response.send_message("Invalid agent ID.", ephemeral=True)
            return
        statuses = read_swarm_statuses()
        row = agent_row(normalized, statuses)
        embed = discord.Embed(title=f"{normalized} Status", color=0x5865F2)
        embed.add_field(name="Status", value=row["status"], inline=True)
        embed.add_field(name="Task", value=row["task"] or "—", inline=True)
        embed.add_field(name="Mission", value=row["mission"] or "—", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="commands", description="List restored Discord Commander commands")
    async def commands_slash(self, interaction: discord.Interaction) -> None:
        body = (
            "**Restored (tier 1):** " + ", ".join(RESTORED_SLASH) + "\n"
            "**Existing:** /ping /status /help /swarm-status /fleet-audit /prompts\n"
            "**Onboard:** /onboard status|soft|hard|quad\n"
            "**Prefix:** !message !broadcast !onboard !heal !gui"
        )
        await interaction.response.send_message(body, ephemeral=True)

    @app_commands.command(name="swarm-help", description="Swarm coordination help")
    async def swarm_help_slash(self, interaction: discord.Interaction) -> None:
        embed = HelpGUIView.main_embed()
        await interaction.response.send_message(embed=embed, view=HelpGUIView(), ephemeral=True)

    @app_commands.command(name="info", description="Discord Commander build info")
    async def info_slash(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(title="Discord Commander", color=0x5865F2)
        embed.add_field(name="Vault", value=f"`{vault_root()}`", inline=False)
        embed.add_field(name="Restored tier", value=str(len(RESTORED_SLASH)), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="gui", description="Open agent messaging control panel")
    async def gui_slash(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Agent Messaging Control Panel",
            description="Select an agent, broadcast, or view swarm status.",
            color=0x5865F2,
        )
        await interaction.response.send_message(
            embed=embed,
            view=AgentMessagingGUIView(),
            ephemeral=True,
        )

    @commands.command(name="gui", description="Open messaging GUI (prefix)")
    async def gui_prefix(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title="Agent Messaging Control Panel",
            description="Restored V2 view — select agent or broadcast.",
            color=0x5865F2,
        )
        await ctx.send(embed=embed, view=AgentMessagingGUIView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RestoredLegacyCommands(bot))
