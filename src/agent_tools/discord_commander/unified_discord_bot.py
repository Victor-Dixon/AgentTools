"""Minimal unified Discord bot for toolbelt operations.

Slim promotion from Agent_Cellphone_V2_Repository/src/discord_commander/unified_discord_bot.py.
Full GUI/messaging surface remains in Agent Cellphone; this bot handles health and operator pings.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

logger = logging.getLogger(__name__)


def _require_discord():
    try:
        import discord
        from discord.ext import commands
        return discord, commands
    except ImportError:
        print("discord.py not installed. Run: pip install discord.py", file=sys.stderr)
        sys.exit(1)


class UnifiedDiscordBot:
    """Lightweight Discord bot for toolbelt start-bot command."""

    def __init__(self, token: str | None = None, guild_id: str | None = None) -> None:
        discord, commands = _require_discord()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        self.token = token or os.getenv("DISCORD_BOT_TOKEN", "")
        self.guild_id = guild_id or os.getenv("DISCORD_GUILD_ID")
        self.bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
        self._register_events()

    def _register_events(self) -> None:
        @self.bot.event
        async def on_ready() -> None:
            logger.info("Discord Commander bot ready as %s", self.bot.user)

        @self.bot.command(name="ping")
        async def ping(ctx) -> None:
            await ctx.send("Discord Commander toolbelt: pong")

        @self.bot.command(name="status")
        async def status_cmd(ctx) -> None:
            from .status import collect_status

            result = collect_status()
            await ctx.send(result.message)

    async def start(self) -> None:
        if not self.token:
            raise RuntimeError("DISCORD_BOT_TOKEN not set")
        await self.bot.start(self.token)

    async def close(self) -> None:
        await self.bot.close()


async def main() -> int:
    logging.basicConfig(level=logging.INFO)
    bot = UnifiedDiscordBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
