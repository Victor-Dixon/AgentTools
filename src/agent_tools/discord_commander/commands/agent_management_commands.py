"""
Agent Management Commands — promoted slice (toolbelt-adapted).
"""

from __future__ import annotations

import logging
from typing import Any

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class AgentManagementCommands(commands.Cog):
    """Agent management prefix commands for operator health checks."""

    def __init__(self, bot: commands.Bot, gui_controller: Any | None = None) -> None:
        self.bot = bot
        self.gui_controller = gui_controller
        self.logger = logging.getLogger(__name__)

    @commands.command(name="heal", aliases=["self_heal", "healing"], description="Self-healing status")
    async def heal(self, ctx: commands.Context, action: str = "status", agent_id: str | None = None) -> None:
        try:
            from src.core.agent_self_healing_system import (  # type: ignore[import-not-found]
                get_self_healing_system,
                heal_stalled_agents_now,
            )
        except ImportError:
            await ctx.send(
                "Self-healing system not available in toolbelt mode. "
                "Use `/swarm-status` or outbound `post` for agent ops."
            )
            return

        try:
            system = get_self_healing_system()
            if action.lower() in {"status", "stats"}:
                stats = system.get_healing_stats()
                embed = discord.Embed(
                    title="Self-Healing System Status",
                    description="Agent stall detection statistics",
                    color=discord.Color.blue(),
                )
                embed.add_field(
                    name="Overall",
                    value=(
                        f"Total: {stats.get('total_actions', 0)}\n"
                        f"Success rate: {stats.get('success_rate', 0):.1f}%"
                    ),
                    inline=False,
                )
                await ctx.send(embed=embed)
            elif action.lower() in {"check", "heal"}:
                await ctx.send("Checking for stalled agents...")
                results = await heal_stalled_agents_now()
                await ctx.send(
                    f"Healing check: stalled={results.get('stalled_agents_found', 0)} "
                    f"healed={len(results.get('agents_healed', []))}"
                )
            elif action.lower() in {"cancel_count", "cancellations"}:
                if agent_id:
                    count = system.get_cancellation_count_today(agent_id)
                    await ctx.send(f"Terminal cancellations today for {agent_id}: {count}")
                else:
                    counts = system.get_healing_stats().get("terminal_cancellations_today", {})
                    await ctx.send(f"Terminal cancellations today: {sum(counts.values())}")
            elif action.lower() == "agent" and agent_id:
                stats = system.get_healing_stats()
                agent_stats = stats.get("by_agent", {}).get(agent_id, {})
                await ctx.send(
                    f"Agent {agent_id}: total={agent_stats.get('total', 0)} "
                    f"ok={agent_stats.get('successful', 0)} fail={agent_stats.get('failed', 0)}"
                )
            else:
                await ctx.send("Usage: `!heal [status|check|cancel_count|agent] [Agent-X]`")
        except Exception as exc:
            self.logger.error("heal command failed: %s", exc, exc_info=True)
            await ctx.send(f"Error: {exc}")


async def setup(bot: commands.Bot, gui_controller: Any | None = None) -> None:
    await bot.add_cog(AgentManagementCommands(bot, gui_controller))
