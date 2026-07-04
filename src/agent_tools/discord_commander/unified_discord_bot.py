"""Discord Commander bot — prefix + slash commands for operator control.

Promotion target: VPS long-running inbound bot. Slash commands sync to DISCORD_GUILD_ID on ready.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SLASH_COMMANDS = (
    "/ping",
    "/status",
    "/help",
    "/swarm-status",
    "/fleet-audit",
)
PREFIX_COMMANDS = ("!ping", "!status", "!help", "!swarm-status", "!message", "!heal")


def _require_discord():
    try:
        import discord
        from discord import app_commands
        from discord.ext import commands
        return discord, commands, app_commands
    except ImportError:
        print("discord.py not installed. Run: pip install discord.py", file=sys.stderr)
        sys.exit(1)


def _vault_root() -> Path:
    raw = os.getenv("DREAMVAULT_ROOT", "D:\\DreamVault").strip()
    return Path(raw)


def _try_swarm_statuses() -> dict[str, dict[str, Any]]:
    vault = _vault_root()
    if not vault.is_dir():
        return {}
    src = vault / "src"
    commander_src = vault / "runtime" / "discord_commander" / "src"
    for path in (src, commander_src):
        if path.is_dir() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    try:
        from dreamvault.discord.commander.swarm_status_reader import (
            SwarmStatusReader,
            resolve_agent_workspace_dir,
        )

        workspace = resolve_agent_workspace_dir(vault)
        reader = SwarmStatusReader(workspace)
        return reader.read_all_statuses()
    except Exception as exc:
        logger.warning("swarm status unavailable: %s", exc)
        return {}


def _try_fleet_audit() -> dict[str, Any]:
    vault = _vault_root()
    src = vault / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from dreamvault.discord.discord_architect import audit_dreamos_guild_bot_roster

        return audit_dreamos_guild_bot_roster()
    except Exception as exc:
        logger.warning("fleet audit unavailable: %s", exc)
        return {"error": str(exc)}


class UnifiedDiscordBot:
    """Operator Discord bot with slash + prefix command surfaces."""

    def __init__(self, token: str | None = None, guild_id: str | None = None) -> None:
        discord, commands, app_commands = _require_discord()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        self.token = token or os.getenv("DISCORD_BOT_TOKEN", "")
        self.guild_id = guild_id or os.getenv("DISCORD_GUILD_ID", "")
        self.bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
        self._discord = discord
        self._app_commands = app_commands
        self.connection_healthy = False
        self.last_heartbeat = 0.0
        self._startup_sent = False
        self._intentional_shutdown = False
        self._slice_loaded = False
        self._register_events()
        self._register_prefix_commands()
        self._register_slash_commands()

    def _register_events(self) -> None:
        @self.bot.event
        async def on_ready() -> None:
            logger.info("Discord Commander bot ready as %s", self.bot.user)
            synced_count = 0
            try:
                if self.guild_id:
                    guild = self._discord.Object(id=int(self.guild_id))
                    pending = self.bot.tree.get_commands(guild=guild)
                    logger.info("Guild tree pending commands: %d", len(pending))
                    synced = await self.bot.tree.sync(guild=guild)
                else:
                    pending = self.bot.tree.get_commands()
                    logger.info("Global tree pending commands: %d", len(pending))
                    synced = await self.bot.tree.sync()
                synced_count = len(synced)
                names = ", ".join(c.name for c in synced) if synced else "(none)"
                logger.info("Synced %d slash commands to guild: %s", synced_count, names)
            except Exception as exc:
                logger.error("Slash command sync failed: %s", exc)
            logger.info(
                "Commands: prefix %s | slash %s",
                ", ".join(PREFIX_COMMANDS),
                ", ".join(SLASH_COMMANDS),
            )
            await self._load_promoted_slice()

    async def _load_promoted_slice(self) -> None:
        if self._slice_loaded:
            return
        try:
            from .lifecycle.bot_lifecycle import BotLifecycleManager

            lifecycle = BotLifecycleManager(self)
            await lifecycle.setup_hook()
            self._slice_loaded = True
            logger.info("Promoted Commander slice loaded")
        except Exception as exc:
            logger.warning("Promoted slice not loaded: %s", exc)

    def _register_prefix_commands(self) -> None:
        @self.bot.command(name="ping")
        async def ping_prefix(ctx) -> None:
            latency = round(self.bot.latency * 1000)
            await ctx.send(f"Discord Commander: pong ({latency}ms)")

        @self.bot.command(name="status")
        async def status_prefix(ctx) -> None:
            from .status import collect_status

            result = collect_status()
            await ctx.send(result.message)

        @self.bot.command(name="help")
        async def help_prefix(ctx) -> None:
            await ctx.send(
                "**Discord Commander**\n"
                "Prefix: `!ping` `!status` `!help` `!swarm-status` `!message <agent> <msg>` `!heal`\n"
                "Slash: `/ping` `/status` `/help` `/swarm-status` `/fleet-audit`"
            )

        @self.bot.command(name="swarm-status")
        async def swarm_status_prefix(ctx) -> None:
            embed = self._build_swarm_embed()
            await ctx.send(embed=embed)

    def _register_slash_commands(self) -> None:
        guild_obj = None
        if self.guild_id:
            guild_obj = self._discord.Object(id=int(self.guild_id))

        def slash(**kwargs):
            if guild_obj is not None:
                kwargs.setdefault("guild", guild_obj)
            return self.bot.tree.command(**kwargs)

        @slash(name="ping", description="Test bot responsiveness")
        async def ping_slash(interaction) -> None:
            latency = round(self.bot.latency * 1000)
            await interaction.response.send_message(f"Discord Commander: pong ({latency}ms)")

        @slash(name="status", description="Discord Commander configuration status")
        async def status_slash(interaction) -> None:
            from .status import collect_status

            result = collect_status()
            await interaction.response.send_message(result.message)

        @slash(name="help", description="List Discord Commander commands")
        async def help_slash(interaction) -> None:
            await interaction.response.send_message(
                "**Discord Commander**\n"
                "Prefix: `!ping` `!status` `!help` `!swarm-status` `!message <agent> <msg>` `!heal`\n"
                "Slash: `/ping` `/status` `/help` `/swarm-status` `/fleet-audit`"
            )

        @slash(name="swarm-status", description="Agent workspace status from status.json")
        async def swarm_status_slash(interaction) -> None:
            embed = self._build_swarm_embed()
            await interaction.response.send_message(embed=embed)

        @slash(name="fleet-audit", description="Audit Dream.OS guild bot roster (masked)")
        async def fleet_audit_slash(interaction) -> None:
            audit = _try_fleet_audit()
            discord = self._discord
            embed = discord.Embed(
                title="Dream.OS Bot Fleet Audit",
                description="Masked token audit for VPS prep",
                color=0x5865F2,
            )
            if audit.get("error"):
                embed.add_field(name="Error", value=str(audit["error"]), inline=False)
            else:
                embed.add_field(
                    name="Guild",
                    value=str(audit.get("guild_id", self.guild_id)),
                    inline=True,
                )
                bots = audit.get("bots") or audit.get("roster") or []
                if isinstance(bots, list):
                    lines = []
                    for row in bots[:12]:
                        if isinstance(row, dict):
                            name = row.get("username") or row.get("env") or "bot"
                            status = row.get("in_guild") or row.get("status") or "?"
                            lines.append(f"{name}: {status}")
                    embed.add_field(
                        name="Bots",
                        value="\n".join(lines) if lines else "No roster data",
                        inline=False,
                    )
                else:
                    embed.add_field(name="Audit", value=str(audit)[:900], inline=False)
            await interaction.response.send_message(embed=embed)

    def _build_swarm_embed(self):
        discord = self._discord
        statuses = _try_swarm_statuses()
        embed = discord.Embed(
            title="Swarm Status",
            description=f"Vault: `{_vault_root()}`",
            color=0x5865F2,
        )
        if not statuses:
            embed.add_field(
                name="No data",
                value="Set DREAMVAULT_ROOT or initialize agent_workspaces.",
                inline=False,
            )
            return embed
        for agent_id in sorted(statuses):
            row = statuses[agent_id]
            status = str(row.get("status", "UNKNOWN"))
            mission = str(row.get("current_mission") or row.get("current_task") or "")[:80]
            embed.add_field(
                name=agent_id,
                value=f"{status}\n{mission}",
                inline=True,
            )
        return embed

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
