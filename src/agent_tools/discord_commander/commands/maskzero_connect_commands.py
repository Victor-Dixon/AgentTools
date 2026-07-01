"""MaskZero /connect slash command — redeems site link codes via discord-link API."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from agent_tools.discord_commander.maskzero_link_client import consume_link_code

logger = logging.getLogger(__name__)


class MaskZeroConnectCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="connect",
        description="Link your Discord account to your MaskZero site character using a one-time code",
    )
    @app_commands.describe(code="One-time code from maskzero.site/discord/connect")
    async def connect_slash(self, interaction: discord.Interaction, code: str) -> None:
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id or "")
        result = consume_link_code(
            code=code,
            discord_user_id=str(interaction.user.id),
            discord_guild_id=guild_id,
        )
        if not result.ok:
            await interaction.followup.send(f"❌ {result.message}", ephemeral=True)
            return

        link = result.link or {}
        character_id = link.get("character_id") or "default"
        site_user_id = link.get("site_user_id") or "?"
        embed = discord.Embed(
            title="MaskZero account linked",
            description="Your Discord account is now bound to your site character.",
            color=0x57F287,
        )
        embed.add_field(name="Character", value=str(character_id), inline=True)
        embed.add_field(name="Site user", value=f"`{site_user_id}`", inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(
            "maskzero_connect ok discord_user=%s site_user=%s character=%s",
            interaction.user.id,
            site_user_id,
            character_id,
        )
