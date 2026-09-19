"""Bot runner service for Discord Commander toolbelt.

Adapted from Agent_Cellphone_V2_Repository/src/discord_commander/bot_runner_service.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import discord

    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False


class BotRunnerService:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def validate_environment(self) -> bool:
        if not DISCORD_AVAILABLE:
            logger.error("discord.py not installed — run: pip install discord.py")
            return False
        issues: list[str] = []
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            issues.append("DISCORD_BOT_TOKEN environment variable not set")
        elif len(token) < 50:
            issues.append("DISCORD_BOT_TOKEN appears invalid (too short)")
        if not os.getenv("DISCORD_GUILD_ID"):
            issues.append("DISCORD_GUILD_ID environment variable not set")
        if issues:
            for issue in issues:
                logger.error("  • %s", issue)
            return False
        return True

    async def run(self) -> int:
        from .unified_discord_bot import UnifiedDiscordBot

        if not self.validate_environment():
            return 1
        bot = UnifiedDiscordBot()
        try:
            await bot.start()
        except discord.LoginFailure:
            logger.error("Invalid Discord token")
            return 1
        except KeyboardInterrupt:
            await bot.close()
        return 0


def create_bot_runner_service(repo_root: Optional[Path] = None) -> BotRunnerService:
    root = repo_root or Path(__file__).resolve().parents[3]
    return BotRunnerService(root)


async def run_bot_service() -> int:
    service = create_bot_runner_service()
    return await service.run()


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    print(f"Discord Commander bot runner — {datetime.now().isoformat()}")
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(run_bot_service())


if __name__ == "__main__":
    raise SystemExit(main())
