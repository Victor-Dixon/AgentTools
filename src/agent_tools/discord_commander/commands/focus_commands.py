"""!focus — TODAY_FOCUS from DreamVault SSOT."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

QUAD_AGENTS = tuple(f"Agent-{i}" for i in range(1, 5))


def _vault_root() -> Path:
    env = os.getenv("DREAMVAULT_ROOT", "").strip()
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "agent_workspaces").is_dir():
            return parent
    return Path("D:/DreamVault")


def _ensure_dreamvault_import() -> None:
    root = _vault_root()
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _build_focus_message() -> str:
    _ensure_dreamvault_import()
    from dreamvault.discord.commander.focus_payload import (
        build_and_publish_focus,
        format_focus_discord_message,
    )

    payload = build_and_publish_focus(_vault_root())
    return format_focus_discord_message(payload)


class FocusCommands(commands.Cog):
    """TODAY_FOCUS for operator — reads DreamVault planner + agent status SSOT."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="focus",
        description="TODAY_FOCUS — planner headline, quad tasks, blockers, next command",
    )
    async def focus(self, ctx: commands.Context) -> None:
        try:
            message = _build_focus_message()
        except Exception as exc:
            logger.exception("focus command failed")
            err = f"focus error: {exc}"
            if ctx.interaction and not ctx.interaction.response.is_done():
                await ctx.send(err, ephemeral=True)
            else:
                await ctx.send(err)
            return
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()
        await ctx.send(message)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FocusCommands(bot))
