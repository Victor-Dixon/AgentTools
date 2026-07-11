"""Tests for restored Discord Commander tier-1 commands and views."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.commands.restored_legacy_commands import (
    RESTORED_SLASH,
    RestoredLegacyCommands,
)
from agent_tools.discord_commander.unified_discord_bot import PREFIX_COMMANDS, SLASH_COMMANDS
from agent_tools.discord_commander.views.agent_messaging_view import AgentMessagingGUIView
from agent_tools.discord_commander.views.help_view import HelpGUIView


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.latency = 0.05
    return bot


class TestRestoredRegistry:
    def test_restored_slash_count(self):
        assert len(RESTORED_SLASH) == 10

    def test_unified_bot_lists_restored(self):
        for cmd in ("/send", "/swarm", "/gui", "/agents"):
            assert cmd in SLASH_COMMANDS
        assert "!gui" in PREFIX_COMMANDS


class TestRestoredViews:
    def test_swarm_status_helper(self):
        from agent_tools.discord_commander.swarm_status_helper import (
            agent_row,
            list_swarm_agents,
        )

        agents = list_swarm_agents()
        assert len(agents) == 8
        row = agent_row("Agent-3")
        assert row["id"] == "Agent-3"

    @pytest.mark.skipif(
        __import__("importlib").util.find_spec("discord") is None,
        reason="discord.py not installed",
    )
    def test_help_view_main_embed(self):
        embed = HelpGUIView.main_embed()
        assert "Discord Commander Help" in embed.title


class TestRestoredCog:
    def test_cog_imports(self, mock_bot):
        cog = RestoredLegacyCommands(mock_bot)
        assert cog.bot is mock_bot

    @patch("agent_tools.discord_commander.commands.restored_legacy_commands.broadcast_agent_messages")
    def test_broadcast_helper(self, mock_broadcast, mock_bot):
        mock_broadcast.return_value = MagicMock(
            delivered=[f"Agent-{i}" for i in range(1, 9)],
            failed=[],
        )
        cog = RestoredLegacyCommands(mock_bot)
        user = MagicMock()
        import asyncio

        delivered, failed = asyncio.get_event_loop().run_until_complete(
            cog._broadcast("hello", user)
        )
        assert len(delivered) == 8
        assert not failed
        mock_broadcast.assert_called_once()
