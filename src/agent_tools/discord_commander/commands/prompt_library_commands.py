"""Slash commands for governed DreamVault prompt browsing and rendering."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from agent_tools.discord_commander.agent_message_sender import send_agent_message
from agent_tools.discord_commander.template_bridge import resolve_dreamvault_root

_COMMANDS_FILE = Path("runtime/scripts/verify_vps_discord_prompt_library_parity_001.py")


def prompt_library_enabled() -> bool:
    return os.environ.get("DISCORD_PROMPT_LIBRARY_ENABLED", "1").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _truncate(text: str, limit: int = 1500) -> str:
    return text if len(text) <= limit else text[: limit - 4] + "\n..."


def _dreamvault_root() -> Path:
    root = resolve_dreamvault_root()
    if root is not None:
        return root
    env_root = os.environ.get("DREAMVAULT_ROOT", "").strip()
    if env_root:
        return Path(env_root)
    raise RuntimeError("DreamVault root not found. Set DREAMVAULT_ROOT on the bot host.")


def _ensure_dreamvault_import(root: Path) -> None:
    src = str(root / "src")
    repo = str(root)
    if src not in sys.path:
        sys.path.insert(0, src)
    if repo not in sys.path:
        sys.path.insert(1, repo)


def _resolver(root: Path | None = None):
    vault = root or _dreamvault_root()
    _ensure_dreamvault_import(vault)
    from dreamvault.prompts.token_resolver import PromptTokenResolver

    return PromptTokenResolver(dreamvault_root=vault)


def _verify_module(root: Path):
    script = root / _COMMANDS_FILE
    if not script.is_file():
        raise FileNotFoundError(script)
    spec = importlib.util.spec_from_file_location("verify_prompt_parity", script)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load parity verifier: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def list_prompt_domains(root: Path | None = None) -> dict[str, Any]:
    resolver = _resolver(root)
    return {
        "dreamvault_root": str(resolver.dreamvault_root),
        "prompt_roots": [str(path) for path in resolver.prompt_roots()],
        "domains": resolver.list_domains(),
    }


def show_prompt(domain: str, *, rendered: bool, root: Path | None = None) -> dict[str, Any]:
    resolver = _resolver(root)
    if rendered:
        result = resolver.render_prompt(domain)
        body = result.rendered
        unavailable = result.unavailable_tokens
    else:
        body = resolver.load_prompt(domain)
        unavailable = []
    source = resolver.prompt_source(domain)
    return {
        "domain": domain,
        "source": source,
        "body": body,
        "unavailable_tokens": unavailable,
    }


def prompt_next_steps(domain: str, root: Path | None = None) -> dict[str, Any]:
    resolver = _resolver(root)
    return {
        "domain": domain,
        "next": resolver.next_domains(domain),
    }


def prompt_search(query: str, root: Path | None = None) -> list[dict[str, str]]:
    return _resolver(root).search(query)


def prompt_parity_report(root: Path | None = None, agenttools_root: Path | None = None) -> dict[str, Any]:
    vault = root or _dreamvault_root()
    module = _verify_module(vault)
    return module.build_parity_report(dreamvault_root=vault, agenttools_root=agenttools_root)


class PromptLibraryCommands(commands.Cog):
    """Read-only prompt library slash commands for the promoted Commander slice."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.prompts = app_commands.Group(
            name="prompts",
            description="Browse and render governed DreamVault prompts",
        )
        self._register_slash()

    def _register_slash(self) -> None:
        @self.prompts.command(name="list", description="List available governed prompt domains")
        async def slash_list(interaction: discord.Interaction) -> None:
            if not prompt_library_enabled():
                await interaction.response.send_message("Prompt library is disabled on this bot host.", ephemeral=True)
                return
            info = list_prompt_domains()
            embed = discord.Embed(title="Prompt Domains", color=0x5865F2)
            embed.add_field(name="Domains", value=", ".join(info["domains"]) or "None", inline=False)
            embed.add_field(name="Roots", value="\n".join(info["prompt_roots"]), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.prompts.command(name="show", description="Show the raw prompt template for one domain")
        @app_commands.describe(domain="Prompt domain, for example closeout or swarm")
        async def slash_show(interaction: discord.Interaction, domain: str) -> None:
            payload = show_prompt(domain, rendered=False)
            content = (
                f"**{payload['domain']}** from `{payload['source']['source_root']}`\n"
                f"`{payload['source']['path']}`\n```md\n{_truncate(payload['body'])}\n```"
            )
            await interaction.response.send_message(content, ephemeral=True)

        @self.prompts.command(name="render", description="Render a prompt with live DreamVault tokens")
        @app_commands.describe(domain="Prompt domain, for example closeout or swarm")
        async def slash_render(interaction: discord.Interaction, domain: str) -> None:
            payload = show_prompt(domain, rendered=True)
            warning = ""
            if payload["unavailable_tokens"]:
                warning = "\nUnavailable: " + ", ".join(payload["unavailable_tokens"])
            content = (
                f"**Rendered {payload['domain']}** from `{payload['source']['source_root']}`{warning}\n"
                f"```md\n{_truncate(payload['body'])}\n```"
            )
            await interaction.response.send_message(content, ephemeral=True)

        @self.prompts.command(name="next", description="Show workflow next steps for a prompt domain")
        @app_commands.describe(domain="Prompt domain")
        async def slash_next(interaction: discord.Interaction, domain: str) -> None:
            payload = prompt_next_steps(domain)
            next_steps = ", ".join(payload["next"]) if payload["next"] else "No next steps configured"
            await interaction.response.send_message(
                f"**{payload['domain']}** -> {next_steps}",
                ephemeral=True,
            )

        @self.prompts.command(name="search", description="Search governed prompts by domain or content")
        @app_commands.describe(query="Search text")
        async def slash_search(interaction: discord.Interaction, query: str) -> None:
            rows = prompt_search(query)
            if not rows:
                await interaction.response.send_message("No matching prompts found.", ephemeral=True)
                return
            lines = [
                f"- **{row['domain']}** ({row['source_root']}) — `{row['path']}`"
                for row in rows[:10]
            ]
            await interaction.response.send_message("\n".join(lines), ephemeral=True)

        @self.prompts.command(name="source", description="Show where a prompt currently resolves from")
        @app_commands.describe(domain="Prompt domain")
        async def slash_source(interaction: discord.Interaction, domain: str) -> None:
            payload = show_prompt(domain, rendered=False)
            await interaction.response.send_message(
                f"**{payload['domain']}** resolves from `{payload['source']['source_root']}`\n"
                f"`{payload['source']['path']}`",
                ephemeral=True,
            )

        @self.prompts.command(name="send", description="Render a prompt and send it to an agent")
        @app_commands.describe(
            agent="Agent ID, for example Agent-1",
            domain="Prompt domain",
            note="Optional note appended before the rendered prompt",
        )
        async def slash_send(
            interaction: discord.Interaction,
            agent: str,
            domain: str,
            note: str = "",
        ) -> None:
            payload = show_prompt(domain, rendered=True)
            message = payload["body"] if not note.strip() else note.strip() + "\n\n" + payload["body"]
            result = send_agent_message(
                agent,
                message,
                discord_user=interaction.user,
                source="discord_prompt_library_send",
            )
            if result.success:
                await interaction.response.send_message(
                    f"✅ Rendered `{domain}` and sent it to **{result.agent}**.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(f"❌ {result.message}", ephemeral=True)

        @self.prompts.command(name="parity", description="Run the DreamVault prompt parity self-check")
        async def slash_parity(interaction: discord.Interaction) -> None:
            report = prompt_parity_report()
            embed = discord.Embed(
                title="Prompt Library Parity",
                description=f"Status: **{report['status']}**",
                color=discord.Color.green() if report["status"] == "PASS" else discord.Color.orange(),
            )
            checks = report.get("checks", {})
            embed.add_field(
                name="Checks",
                value="\n".join(
                    f"{name}: {'PASS' if value else 'BLOCKED'}"
                    for name, value in checks.items()
                ),
                inline=False,
            )
            prompt_report = report.get("prompt_report", {})
            embed.add_field(
                name="Domains",
                value=", ".join(prompt_report.get("domains", [])) or "None",
                inline=False,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def cog_load(self) -> None:
        if prompt_library_enabled():
            guild_id = os.environ.get("DISCORD_GUILD_ID", "").strip()
            if guild_id.isdigit():
                self.bot.tree.add_command(self.prompts, guild=discord.Object(id=int(guild_id)))
            else:
                self.bot.tree.add_command(self.prompts)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PromptLibraryCommands(bot))
