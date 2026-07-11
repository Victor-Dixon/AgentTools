"""Restored message modals — toolbelt-adapted (no V2 messaging service)."""

from __future__ import annotations

import logging
from typing import Any

import discord

from agent_tools.discord_commander.agent_message_sender import (
    broadcast_agent_messages,
    normalize_agent_id,
    send_agent_message,
)
from agent_tools.discord_commander.onboard_bridge import quad_onboard_status

logger = logging.getLogger(__name__)


class AgentMessageModal(discord.ui.Modal, title="Send Agent Message"):
    def __init__(self, agent_id: str) -> None:
        super().__init__()
        self.agent_id = agent_id
        self.message_input = discord.ui.TextInput(
            label=f"Message to {agent_id}",
            style=discord.TextStyle.paragraph,
            placeholder="Enter message for the agent...",
            required=True,
            max_length=2000,
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        body = self.message_input.value.strip()
        result = send_agent_message(
            self.agent_id,
            body,
            discord_user=interaction.user,
            source="discord_gui_modal",
        )
        if result.success:
            await interaction.response.send_message(
                f"✅ Message sent to **{result.agent}** via {result.data.get('transport', 'unknown')}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"❌ Failed: {result.message}",
                ephemeral=True,
            )


class BroadcastMessageModal(discord.ui.Modal, title="Broadcast to Swarm"):
    def __init__(self) -> None:
        super().__init__()
        self.message_input = discord.ui.TextInput(
            label="Broadcast message",
            style=discord.TextStyle.paragraph,
            placeholder="Message for all agents...",
            required=True,
            max_length=2000,
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        import asyncio

        body = self.message_input.value.strip()
        await interaction.response.defer(ephemeral=True)
        result = await asyncio.to_thread(
            broadcast_agent_messages,
            body,
            discord_user=interaction.user,
            source="discord_broadcast_modal",
        )
        lines = [result.message]
        if result.delivered:
            lines.append(f"✅ {', '.join(result.delivered)}")
        if result.failed:
            lines.append(f"❌ {', '.join(result.failed)}")
        await interaction.followup.send("\n".join(lines), ephemeral=True)


class QuickSendModal(discord.ui.Modal, title="Send to Agent"):
    """Modal with agent picker field for slash /send flow."""

    def __init__(self, default_agent: str = "Agent-1") -> None:
        super().__init__()
        self.agent_field = discord.ui.TextInput(
            label="Agent ID",
            default=default_agent,
            placeholder="Agent-1",
            required=True,
            max_length=20,
        )
        self.message_field = discord.ui.TextInput(
            label="Message",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000,
        )
        self.add_item(self.agent_field)
        self.add_item(self.message_field)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        agent = normalize_agent_id(self.agent_field.value)
        if not agent:
            await interaction.response.send_message("Invalid agent ID.", ephemeral=True)
            return
        result = send_agent_message(
            agent,
            self.message_field.value,
            discord_user=interaction.user,
            source="discord_quick_send_modal",
        )
        if result.success:
            await interaction.response.send_message(f"✅ Sent to **{agent}**", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {result.message}", ephemeral=True)
