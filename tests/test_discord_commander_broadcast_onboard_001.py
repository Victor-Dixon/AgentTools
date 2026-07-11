"""Tests for broadcast + onboard Discord Commander bridges."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


class TestBroadcastAgentMessages:
    @patch("agent_tools.discord_commander.swarm_status_helper.list_swarm_agents")
    @patch("agent_tools.discord_commander.agent_message_sender.send_agent_message")
    def test_broadcast_all_success(self, mock_send, mock_agents):
        from agent_tools.discord_commander.agent_message_sender import broadcast_agent_messages

        mock_agents.return_value = ["Agent-1", "Agent-2"]
        mock_send.return_value = MagicMock(success=True, agent="Agent-1", data={"transport": "pyautogui"})

        result = broadcast_agent_messages("hello", source="test")

        assert result.success is True
        assert len(result.delivered) == 2
        assert not result.failed
        assert mock_send.call_count == 2

    @patch("agent_tools.discord_commander.swarm_status_helper.list_swarm_agents")
    @patch("agent_tools.discord_commander.agent_message_sender.send_agent_message")
    def test_broadcast_empty_body(self, mock_send, mock_agents):
        from agent_tools.discord_commander.agent_message_sender import broadcast_agent_messages

        result = broadcast_agent_messages("  ", source="test")
        assert result.success is False
        assert result.error_code == "EMPTY_MESSAGE"
        mock_send.assert_not_called()
        mock_agents.assert_not_called()


class TestOnboardBridge:
    @patch("agent_tools.discord_commander.onboard_bridge.resolve_dreamvault_root")
    @patch("agent_tools.discord_commander.onboard_bridge.bootstrap_commander_env")
    def test_quad_status_missing_root(self, _boot, mock_root):
        from agent_tools.discord_commander.onboard_bridge import quad_onboard_status

        mock_root.return_value = None
        result = quad_onboard_status()
        assert result.success is False
        assert result.error_code == "DREAMVAULT_MISSING"
