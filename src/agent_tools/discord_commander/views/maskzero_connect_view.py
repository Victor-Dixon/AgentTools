"""Persistent MaskZero account-link panel for #command-controller."""

from __future__ import annotations

import os

import discord

from agent_tools.discord_commander.maskzero_link_client import consume_link_code

CONNECT_PAGE_URL = "https://maskzero.site/discord/connect/"


def _persistent_timeout() -> float | None:
    if os.environ.get("DISCORD_PERSISTENT_VIEWS", "").strip().lower() in {"1", "true", "yes"}:
        return None
    return 300


class MaskZeroConnectCodeModal(discord.ui.Modal, title="Link MaskZero Account"):
    code = discord.ui.TextInput(
        label="One-time code",
        placeholder="From maskzero.site/discord/connect",
        min_length=4,
        max_length=32,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        result = consume_link_code(
            code=str(self.code.value or ""),
            discord_user_id=str(interaction.user.id),
            discord_guild_id=str(interaction.guild_id or ""),
        )
        if not result.ok:
            await interaction.followup.send(f"❌ {result.message}", ephemeral=True)
            return
        link = result.link or {}
        embed = discord.Embed(
            title="MaskZero account linked",
            description="Your Discord account is bound to your site character.",
            color=0x57F287,
        )
        embed.add_field(name="Character", value=str(link.get("character_id") or "default"), inline=True)
        embed.add_field(name="Site user", value=f"`{link.get('site_user_id') or '?'}`", inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)


class MaskZeroConnectView(discord.ui.View):
    """Always-on MaskZero link panel — complements /connect slash command."""

    def __init__(self) -> None:
        super().__init__(timeout=_persistent_timeout())
        self.add_item(
            discord.ui.Button(
                label="Get Link Code",
                style=discord.ButtonStyle.link,
                url=CONNECT_PAGE_URL,
                row=0,
            )
        )

    @discord.ui.button(
        label="Enter Code",
        custom_id="mz_connect_enter_code",
        style=discord.ButtonStyle.primary,
        emoji="🔗",
        row=0,
    )
    async def enter_code(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(MaskZeroConnectCodeModal())

    @discord.ui.button(
        label="How It Works",
        custom_id="mz_connect_help",
        style=discord.ButtonStyle.secondary,
        row=0,
    )
    async def how_it_works(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        steps = (
            "1. Log in or create a Spark account at maskzero.site\n"
            "2. Open **Get Link Code** → generate a one-time code\n"
            "3. Return here and click **Enter Code** (or use `/connect <code>`)\n"
            "4. Your Discord binds to your site character"
        )
        await interaction.response.send_message(steps, ephemeral=True)
