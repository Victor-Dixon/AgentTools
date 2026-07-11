"""Minimal Discord bot — !message + !ping only (backup router when GUI/views fail).

Uses DISCORD_MESSAGE_ROUTER_BOT_TOKEN when set, else DISCORD_BOT_TOKEN.
No slash commands, no views, no GUI panels — prefix intake only.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Any

logger = logging.getLogger(__name__)


def _require_discord():
    try:
        import discord
        from discord.ext import commands
        return discord, commands
    except ImportError:
        print("discord.py not installed. Run: pip install discord.py", file=sys.stderr)
        sys.exit(1)


class MessageRouterDiscordBot:
    """Backup operator bot: !message routes D2A through unified message bus only."""

    def __init__(self, token: str | None = None) -> None:
        discord, commands = _require_discord()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        self.token = (
            token
            or os.getenv("DISCORD_MESSAGE_ROUTER_BOT_TOKEN", "").strip()
            or os.getenv("DISCORD_BOT_TOKEN", "")
        )
        self.bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
        self._discord = discord
        self._register_commands()

    def _register_commands(self) -> None:
        @self.bot.event
        async def on_ready() -> None:
            logger.info("Message router bot ready as %s (prefix-only)", self.bot.user)
            await self._load_messaging_cog()

        @self.bot.command(name="ping")
        async def ping(ctx) -> None:
            latency = round(self.bot.latency * 1000)
            await ctx.send(f"Message router: pong ({latency}ms) — prefix !message only")

        @self.bot.command(name="help")
        async def help_cmd(ctx) -> None:
            await ctx.send(
                "**Dream.OS Message Router (backup)**\n"
                "`!message Agent-N <text>` — D2A → message bus → PyAutoGUI\n"
                "`!ping` — health check\n"
                "No slash/GUI — use when Commander views fail."
            )

    async def _load_messaging_cog(self) -> None:
        from agent_tools.discord_commander.commands.messaging_commands import MessagingCommands

        await self.bot.add_cog(MessagingCommands(self.bot, gui_controller=None))
        logger.info("MessagingCommands cog loaded (message-only router)")

    async def start(self) -> None:
        if not self.token:
            raise RuntimeError("DISCORD_MESSAGE_ROUTER_BOT_TOKEN or DISCORD_BOT_TOKEN not set")
        await self.bot.start(self.token)

    async def close(self) -> None:
        await self.bot.close()


async def main() -> int:
    from agent_tools.discord_commander.env_bootstrap import bootstrap_commander_env
    from agent_tools.discord_commander.logging_config import configure_discord_commander_logging

    bootstrap_commander_env()
    configure_discord_commander_logging("message_router_bot")
    bot = MessageRouterDiscordBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.close()
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(asyncio.run(main()))
