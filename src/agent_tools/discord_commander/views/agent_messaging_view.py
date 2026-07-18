"""Restored Agent Messaging GUI view — toolbelt-adapted from V2."""

from __future__ import annotations

import logging

import discord

from agent_tools.discord_commander.swarm_status_helper import (
    agent_row,
    list_swarm_agents,
    read_swarm_statuses,
    status_emoji,
)
from agent_tools.discord_commander.views.message_modals import (
    AgentMessageModal,
    BroadcastMessageModal,
)

logger = logging.getLogger(__name__)

class AgentMessagingGUIView(discord.ui.View):
    """Interactive control panel: agent select, broadcast, status, refresh.

    Persistent view: timeout=None + stable custom_id on every item (required for
    bot.add_view registration across restarts).
    """

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.statuses = read_swarm_statuses()
        self.agents = [agent_row(a, self.statuses) for a in list_swarm_agents()]
        self.agent_select = discord.ui.Select(
            placeholder="Select agent to message...",
            options=self._agent_options(),
            custom_id="dc_agent_select",
        )
        self.agent_select.callback = self.on_agent_select
        self.add_item(self.agent_select)

        broadcast_btn = discord.ui.Button(
            label="Broadcast",
            style=discord.ButtonStyle.primary,
            emoji="📢",
            custom_id="dc_broadcast",
        )
        broadcast_btn.callback = self.on_broadcast
        self.add_item(broadcast_btn)

        status_btn = discord.ui.Button(
            label="Swarm Status",
            style=discord.ButtonStyle.secondary,
            emoji="📊",
            custom_id="dc_status",
        )
        status_btn.callback = self.on_status
        self.add_item(status_btn)

        refresh_btn = discord.ui.Button(
            label="Refresh",
            style=discord.ButtonStyle.secondary,
            emoji="🔄",
            custom_id="dc_refresh",
        )
        refresh_btn.callback = self.on_refresh
        self.add_item(refresh_btn)

        quad_btn = discord.ui.Button(
            label="Quad Onboard",
            style=discord.ButtonStyle.secondary,
            emoji="🚀",
            custom_id="dc_quad_onboard_status",
        )
        quad_btn.callback = self.on_quad_onboard_status
        self.add_item(quad_btn)

    def _agent_options(self) -> list[discord.SelectOption]:
        options: list[discord.SelectOption] = []
        for agent in self.agents:
            emoji = status_emoji(agent["status"])
            options.append(
                discord.SelectOption(
                    label=agent["id"],
                    description=(agent["mission"] or agent["status"])[:100],
                    emoji=emoji,
                    value=agent["id"],
                )
            )
        return options

    async def on_agent_select(self, interaction: discord.Interaction) -> None:
        agent_id = self.agent_select.values[0]
        await interaction.response.send_modal(AgentMessageModal(agent_id))

    async def on_broadcast(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(BroadcastMessageModal())

    async def on_status(self, interaction: discord.Interaction) -> None:
        embed = self.build_status_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_refresh(self, interaction: discord.Interaction) -> None:
        self.statuses = read_swarm_statuses()
        self.agents = [agent_row(a, self.statuses) for a in list_swarm_agents()]
        self.agent_select.options = self._agent_options()
        await interaction.response.send_message("Agent list refreshed.", ephemeral=True)

    async def on_quad_onboard_status(self, interaction: discord.Interaction) -> None:
        import asyncio

        await interaction.response.defer(ephemeral=True)
        result = await asyncio.to_thread(quad_onboard_status)
        embed = discord.Embed(
            title="Quad Onboard Status",
            description=result.message,
            color=0x57F287 if result.success else 0xED4245,
        )
        if result.data:
            embed.add_field(
                name="Threshold",
                value=f"{result.data.get('tasks_before_rollover', '?')}/{result.data.get('tasks_before_rollover', '?')} gas",
                inline=True,
            )
            embed.add_field(
                name="All ready",
                value=str(result.data.get("all_ready", False)),
                inline=True,
            )
        embed.set_footer(text="Live: /onboard quad or !onboard quad")
        await interaction.followup.send(embed=embed, ephemeral=True)

    def build_status_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Swarm Status",
            description="Agent workspace status from DreamVault",
            color=0x5865F2,
        )
        active = 0
        for agent in self.agents:
            emoji = status_emoji(agent["status"])
            if emoji == "🟢":
                active += 1
            embed.add_field(
                name=f"{emoji} {agent['id']}",
                value=agent["mission"] or agent["status"],
                inline=True,
            )
        embed.set_footer(text=f"Active-ish: {active}/{len(self.agents)}")
        return embed
