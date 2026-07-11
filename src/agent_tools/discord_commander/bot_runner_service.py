"""Bot runner service for Discord Commander toolbelt.

Adapted from Agent_Cellphone_V2_Repository/src/discord_commander/bot_runner_service.py
"""

from __future__ import annotations
# C2A_SELF_GAS_ROOT_DEFAULTS_041
# Canonical desktop roots for C2A/S2A hard onboard and self-gas routes.
import os as _c2a_self_gas_env_041
_c2a_self_gas_env_041.environ["DREAMVAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["DREAMOS_VAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["VAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["AGENT_CELLPHONE_ROOT"] = r"D:\repos\Agent_Cellphone"
_c2a_self_gas_env_041.environ.setdefault("ALLOW_LIVE_CURSOR_INJECTION", "1")
_c2a_self_gas_env_041.environ.setdefault("DEFAULT_MODE", "pyautogui")
_c2a_self_gas_env_041.environ.setdefault("COORDINATE_MODE", "4-agent-1monitor")
_c2a_self_gas_env_041.environ.setdefault("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor")
_c2a_self_gas_env_041.environ.setdefault("DREAMOS_ALLOW_PYAUTOGUI_FAILSAFE_OVERRIDE", "1")

# D2A_AGENTTOOLS_BRIDGE_ENV_DEFAULTS_035
# Canonical visible-session D2A delivery defaults.
import os as _dreamos_d2a_env_035
_dreamos_d2a_env_035.environ["AGENT_CELLPHONE_ROOT"] = r"D:\repos\Agent_Cellphone"
_dreamos_d2a_env_035.environ.setdefault("ALLOW_LIVE_CURSOR_INJECTION", "1")
_dreamos_d2a_env_035.environ.setdefault("DEFAULT_MODE", "pyautogui")
_dreamos_d2a_env_035.environ.setdefault("COORDINATE_MODE", "4-agent-1monitor")
_dreamos_d2a_env_035.environ.setdefault("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor")
_dreamos_d2a_env_035.environ.setdefault("DREAMOS_ALLOW_PYAUTOGUI_FAILSAFE_OVERRIDE", "1")
_dreamos_d2a_env_035.environ.setdefault("PYTHONPATH", r"D:\agent-tools\src;D:\DreamVault\src")

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
    from .env_bootstrap import bootstrap_commander_env
    from .logging_config import configure_discord_commander_logging

    bootstrap_commander_env()
    log_path = configure_discord_commander_logging("bot")
    print(f"Discord Commander bot runner — {datetime.now().isoformat()}")
    print(f"LOG_FILE={log_path}")
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    return asyncio.run(run_bot_service())


if __name__ == "__main__":
    raise SystemExit(main())
