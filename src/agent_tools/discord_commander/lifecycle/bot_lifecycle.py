"""Bot lifecycle — promoted slice (loads agent-management cog only)."""

from __future__ import annotations

import logging
import os
from pathlib import Path
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
        from agent_tools.discord_commander.commands.bump_commands import BumpCommands
        from agent_tools.discord_commander.commands.messaging_commands import (
            MessagingCommands,
        )
        from agent_tools.discord_commander.commands.maskzero_connect_commands import (
            MaskZeroConnectCommands,
        )
        from agent_tools.discord_commander.commands.maskzero_play_commands import (
            MaskZeroPlayCommands,
        )
        from agent_tools.discord_commander.commands.onboarding_commands import (
            OnboardingCommands,
        )
        from agent_tools.discord_commander.commands.prompt_library_commands import (
            PromptLibraryCommands,
        )
        from agent_tools.discord_commander.commands.restored_legacy_commands import (
            RestoredLegacyCommands,
        )

        await self.bot.add_cog(AgentManagementCommands(self.bot, gui_controller=None))
        await self.bot.add_cog(MessagingCommands(self.bot, gui_controller=None))
        await self.bot.add_cog(RestoredLegacyCommands(self.bot))
        await self.bot.add_cog(OnboardingCommands(self.bot))
        await self.bot.add_cog(BumpCommands(self.bot))
        await self.bot.add_cog(PromptLibraryCommands(self.bot))
        await self.bot.add_cog(MaskZeroConnectCommands(self.bot))
        await self.bot.add_cog(MaskZeroPlayCommands(self.bot))
        self.logger.info(
            "Promoted slice: AgentManagement + Messaging + RestoredLegacy + Onboarding + Bump + PromptLibrary + MaskZeroConnect + MaskZeroPlay loaded (focus=core bot command)"
        )

    def _views_approved(self, view_id: str) -> bool:
        dv_root = os.getenv("DREAMVAULT_ROOT", "").strip()
        if not dv_root:
            return False
        registry = Path(dv_root) / "data/registry/discord_view_controllers_approved.json"
        if not registry.is_file():
            self.logger.warning("View registry missing: %s", registry)
            return False
        try:
            import json

            data = json.loads(registry.read_text(encoding="utf-8"))
            for row in data.get("controllers", []):
                if row.get("id") == view_id:
                    return bool(row.get("approved"))
        except Exception as exc:
            self.logger.warning("View approval read failed: %s", exc)
        return False

    async def send_startup_message(self) -> None:
        channel = self._resolve_commander_channel()
        if not channel:
            self.logger.info("No commander channel for startup message (toolbelt mode)")
            return

        if self._views_approved("MaskZeroConnectView"):
            await self._post_maskzero_connect_panel(channel)

        if self._views_approved("MaskZeroPlayView"):
            await self._post_maskzero_play_panel(channel)

        if self._views_approved("AgentMessagingGUIView"):
            await self._post_agent_messaging_panel(channel)
        elif not self._views_approved("MaskZeroConnectView") and not self._views_approved(
            "MaskZeroPlayView"
        ):
            self.logger.warning(
                "No approved startup views — check discord_view_controllers_approved.json"
            )

        await self._post_timeblock_panels()
        await self._post_planner_cockpit_panel()

    async def _post_timeblock_panels(self) -> None:
        from agent_tools.discord_commander.views.flowr_timeblock_view import (
            CHANNEL_DEFAULTS,
            VIEW_BY_ID,
        )

        for channel_name, (view_id, owner) in CHANNEL_DEFAULTS.items():
            if not self._views_approved(view_id):
                continue
            target = self._resolve_channel_by_name(channel_name)
            if target is None:
                self.logger.warning("Timeblock channel missing: #%s", channel_name)
                continue
            await self._post_flowr_timeblock_panel(target, view_id, owner)

    async def _post_planner_cockpit_panel(self) -> None:
        if not self._views_approved("DailyCommandHubView"):
            return
        channel = self._resolve_channel_by_name(
            os.getenv("DISCORD_PLANNER_CHANNEL_NAME", "planner-cockpit").strip()
        )
        if channel is None:
            self.logger.warning("Planner cockpit channel missing")
            return
        await self._post_daily_command_hub_panel(channel)

    async def _post_flowr_timeblock_panel(
        self,
        channel: discord.TextChannel,
        view_id: str,
        owner: str,
    ) -> None:
        from agent_tools.discord_commander.views.flowr_timeblock_view import VIEW_BY_ID

        view_cls = VIEW_BY_ID.get(view_id)
        if view_cls is None:
            return
        view = view_cls()
        self.bot.add_view(view)
        try:
            summary = self._flowr_panel_summary(owner)
        except Exception as exc:
            self.logger.warning("Flowr summary failed owner=%s: %s", owner, exc)
            summary = f"Flowr timeblock panel for **{owner.title()}**."
        embed = discord.Embed(
            title=f"Flowr Timeblock — {owner.title()}",
            description=summary,
            color=0xA78BFA,
        )
        embed.set_footer(text="Persistent panel — planner + pomodoro blocks")
        try:
            await channel.send(embed=embed, view=view)
            self.logger.info("%s posted to #%s", view_id, channel.name)
        except discord.HTTPException as exc:
            self.logger.warning("%s skipped: %s", view_id, exc)

    async def _post_daily_command_hub_panel(self, channel: discord.TextChannel) -> None:
        try:
            from agent_tools.discord_commander.dreamvault_discord_loader import (
                load_daily_command_hub_live,
            )

            hub_live = load_daily_command_hub_live()
        except Exception as exc:
            self.logger.warning("DailyCommandHubView import failed: %s", exc)
            return
        message = hub_live.build_daily_command_hub_message()
        if not message.get("available"):
            self.logger.warning("DailyCommandHubView unavailable (discord.py)")
            return
        view = hub_live.DailyCommandHubView(message)
        self.bot.add_view(view)
        embed = discord.Embed.from_dict(message["main_embed"])
        embed.set_footer(text="Persistent planner cockpit — daily command hub")
        try:
            await channel.send(content=message.get("content"), embed=embed, view=view)
            self.logger.info("DailyCommandHubView posted to #%s", channel.name)
        except discord.HTTPException as exc:
            self.logger.warning("DailyCommandHubView skipped: %s", exc)

    def _flowr_panel_summary(self, owner: str) -> str:
        from agent_tools.discord_commander.dreamvault_discord_loader import load_flowr_store

        return load_flowr_store()["build_panel_summary"](owner)

    def _resolve_channel_by_name(self, channel_name: str) -> discord.TextChannel | None:
        target = channel_name.lower().replace("#", "").strip()
        if not target:
            return None
        channel_id = os.getenv(f"DISCORD_{target.upper().replace('-', '_')}_CHANNEL_ID", "").strip()
        if channel_id.isdigit():
            for guild in self.bot.guilds:
                ch = guild.get_channel(int(channel_id))
                if isinstance(ch, discord.TextChannel):
                    return ch
        for guild in self.bot.guilds:
            for text_channel in guild.text_channels:
                if text_channel.name.lower() == target:
                    return text_channel
        return None

    async def _post_maskzero_connect_panel(self, channel: discord.TextChannel) -> None:
        from agent_tools.discord_commander.views.maskzero_connect_view import (
            CONNECT_PAGE_URL,
            MaskZeroConnectView,
        )

        view = MaskZeroConnectView()
        self.bot.add_view(view)
        embed = discord.Embed(
            title="MaskZero Account Link",
            description=(
                "Link your Discord to your MaskZero site character.\n"
                f"Site panel: {CONNECT_PAGE_URL}"
            ),
            color=0x57F287,
        )
        embed.set_footer(text="Persistent panel — survives bot restarts")
        try:
            await channel.send(embed=embed, view=view)
            self.logger.info("MaskZeroConnectView posted to #%s", channel.name)
        except discord.HTTPException as exc:
            self.logger.warning("MaskZeroConnectView skipped: %s", exc)

    async def _post_maskzero_play_panel(self, channel: discord.TextChannel) -> None:
        from agent_tools.discord_commander.views.maskzero_play_view import (
            PIN_FALLBACK_TEXT,
            PLAY_CAMPAIGN_URL,
            MaskZeroPlayView,
        )

        view = MaskZeroPlayView()
        self.bot.add_view(view)
        embed = discord.Embed(
            title="MaskZero — Play Campaign",
            description=PIN_FALLBACK_TEXT,
            color=0x7DFFBE,
            url=PLAY_CAMPAIGN_URL,
        )
        embed.set_footer(text="Persistent panel — distribution.discord canonical /play only")
        try:
            await channel.send(embed=embed, view=view)
            self.logger.info("MaskZeroPlayView posted to #%s url=%s", channel.name, PLAY_CAMPAIGN_URL)
        except discord.HTTPException as exc:
            self.logger.warning("MaskZeroPlayView skipped: %s", exc)

    async def _post_agent_messaging_panel(self, channel: discord.TextChannel) -> None:
        from agent_tools.discord_commander.views.agent_messaging_view import (
            AgentMessagingGUIView,
        )

        view = AgentMessagingGUIView()
        self.bot.add_view(view)
        embed = discord.Embed(
            title="Discord Commander",
            description=(
                "Swarm Commander — `/gui`, `/help`, `!message Agent-1 <msg>`, `!heal status`"
            ),
            color=0x5865F2,
        )
        embed.set_footer(text=f"channel={channel.name}")
        try:
            await channel.send(embed=embed, view=view)
            self.logger.info("AgentMessagingGUIView posted to #%s", channel.name)
        except discord.HTTPException as exc:
            self.logger.warning("AgentMessagingGUIView skipped: %s", exc)

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
