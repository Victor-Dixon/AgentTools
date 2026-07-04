"""Inbound Discord dry-run — validates bot token without posting messages.

Adapted from Agent_Cellphone_V2_Repository/scripts/health/discord_dry_run.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Optional

from .config import DiscordEnvConfig
from .models import CommandResult


def _discord_available() -> bool:
    try:
        import discord  # noqa: F401
        from discord.ext import commands  # noqa: F401
        return True
    except ImportError:
        return False


async def _run_inbound_test(token: str) -> CommandResult:
    import discord
    from discord.ext import commands

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
    connected = asyncio.Event()

    @bot.event
    async def on_ready() -> None:
        connected.set()
        await bot.close()

    try:
        await bot.start(token)
    except discord.LoginFailure:
        return CommandResult(
            success=False,
            message="Invalid or expired DISCORD_BOT_TOKEN",
            error_code="LOGIN_FAILURE",
        )
    except discord.PrivilegedIntentsRequired:
        return CommandResult(
            success=False,
            message="Privileged intents required (enable in Discord Developer Portal)",
            error_code="INTENTS_REQUIRED",
        )
    except Exception as exc:
        return CommandResult(
            success=False,
            message=f"Connection test failed: {type(exc).__name__}",
            error_code="CONNECTION_FAILED",
        )

    if connected.is_set():
        return CommandResult(success=True, message="Inbound dry-run passed")
    return CommandResult(success=False, message="Bot did not connect", error_code="NO_CONNECTION")


def inbound_dry_run(environ: Optional[dict[str, str]] = None) -> CommandResult:
    """Run inbound Discord connectivity dry-run."""
    if not _discord_available():
        return CommandResult(
            success=False,
            message="discord.py not installed (pip install discord.py)",
            error_code="DISCORD_PY_MISSING",
        )

    config = DiscordEnvConfig.from_environ(environ or dict(os.environ))
    token = config.bot_token
    if not token:
        return CommandResult(
            success=False,
            message="DISCORD_BOT_TOKEN environment variable not set",
            error_code="TOKEN_MISSING",
        )
    if len(token) < 50:
        return CommandResult(
            success=False,
            message="DISCORD_BOT_TOKEN appears invalid (too short)",
            error_code="TOKEN_INVALID",
        )

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    return asyncio.run(_run_inbound_test(token))
