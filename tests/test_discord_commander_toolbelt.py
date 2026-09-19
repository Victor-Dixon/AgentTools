"""Tests for Discord Commander toolbelt promotion."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.agent_message_sender import (
    normalize_agent_id,
    send_agent_message,
)
from agent_tools.discord_commander.cli import build_parser, main
from agent_tools.discord_commander.config import DiscordEnvConfig, mask_secret
from agent_tools.discord_commander.inbound_dry_run import inbound_dry_run
from agent_tools.discord_commander.outbound_dry_run import outbound_dry_run
from agent_tools.discord_commander.outbound_router import post_to_discord
from agent_tools.discord_commander.unified_discord_bot import PREFIX_COMMANDS


VALID_WEBHOOK = "https://discord.com/api/webhooks/123456789/abcdefghijklmnop"
VALID_TOKEN = "x" * 59


class TestImportsWithoutToken:
    def test_cli_help_imports(self):
        parser = build_parser()
        assert "inbound-dry-run" in parser.format_help()

    def test_module_import(self):
        import agent_tools.discord_commander  # noqa: F401


class TestOutboundDryRun:
    def test_no_webhook_reports_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            result = outbound_dry_run({})
        assert not result.success
        assert "WEBHOOK_MISSING" == result.error_code

    def test_does_not_print_full_webhook(self, capsys):
        env = {"DISCORD_WEBHOOK_URL": VALID_WEBHOOK}
        result = outbound_dry_run(env)
        captured = capsys.readouterr()
        assert result.success
        assert VALID_WEBHOOK not in captured.out
        assert VALID_WEBHOOK not in str(result.data)

    def test_agent_webhooks_validated(self):
        env = {
            "DISCORD_WEBHOOK_AGENT_1": VALID_WEBHOOK,
            "DISCORD_WEBHOOK_AGENT_2": "not-a-url",
        }
        result = outbound_dry_run(env)
        assert result.success
        assert result.data["checks"]


class TestInboundDryRun:
    def test_missing_token_clean(self):
        with patch.dict(os.environ, {}, clear=True):
            result = inbound_dry_run({})
        assert not result.success
        assert result.error_code == "TOKEN_MISSING"
        assert "DISCORD_BOT_TOKEN" in result.message

    def test_invalid_token_length(self):
        result = inbound_dry_run({"DISCORD_BOT_TOKEN": "short"})
        assert not result.success
        assert result.error_code == "TOKEN_INVALID"

    def test_discord_py_missing(self):
        with patch("agent_tools.discord_commander.inbound_dry_run._discord_available", return_value=False):
            result = inbound_dry_run({"DISCORD_BOT_TOKEN": VALID_TOKEN})
        assert not result.success
        assert result.error_code == "DISCORD_PY_MISSING"


class TestPostDryRun:
    def test_post_dry_run(self):
        env = {"DISCORD_WEBHOOK_AGENT_1": VALID_WEBHOOK}
        with patch.dict(os.environ, env, clear=True):
            result = post_to_discord(
                agent="Agent-1",
                title="Dry Run",
                message="DISCORD_COMMANDER_TOOLBELT=PASS",
                dry_run=True,
            )
        assert result.success
        assert "Dry-run" in result.message
        assert VALID_WEBHOOK not in str(result.data)

    def test_post_message_file(self, tmp_path: Path):
        msg_file = tmp_path / "msg.txt"
        msg_file.write_text("hello from file", encoding="utf-8")
        env = {"DISCORD_WEBHOOK_URL": VALID_WEBHOOK}
        with patch.dict(os.environ, env, clear=True):
            result = post_to_discord(
                agent="Agent-1",
                title="File",
                message="",
                dry_run=True,
                message_file=msg_file,
            )
        assert result.success


class TestMaskSecret:
    def test_mask_secret_redacts(self):
        assert mask_secret(VALID_WEBHOOK) != VALID_WEBHOOK
        assert "<unset>" == mask_secret(None)


class TestCli:
    def test_help_exits_zero(self):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_outbound_dry_run_cli(self):
        env = {"DISCORD_WEBHOOK_URL": VALID_WEBHOOK}
        with patch.dict(os.environ, env, clear=True):
            assert main(["outbound-dry-run"]) == 0

    def test_post_dry_run_cli(self):
        env = {"DISCORD_WEBHOOK_AGENT_1": VALID_WEBHOOK}
        with patch.dict(os.environ, env, clear=True):
            code = main(
                [
                    "post",
                    "--agent",
                    "Agent-1",
                    "--title",
                    "Dry Run",
                    "--message",
                    "DISCORD_COMMANDER_TOOLBELT=PASS",
                    "--dry-run",
                ]
            )
        assert code == 0


class TestAgentMessageSender:
    def test_normalize_agent_id(self):
        assert normalize_agent_id("Agent-1") == "Agent-1"
        assert normalize_agent_id("agent-3") == "Agent-3"
        assert normalize_agent_id("3") == "Agent-3"
        assert normalize_agent_id("Agent-9") is None
        assert normalize_agent_id("unknown") is None

    def test_send_agent_message_dry_run(self):
        env = {"DISCORD_WEBHOOK_AGENT_1": VALID_WEBHOOK}
        with patch.dict(os.environ, env, clear=True):
            result = send_agent_message(
                "Agent-1",
                "Check your inbox",
                dry_run=True,
            )
        assert result.success
        assert result.agent == "Agent-1"
        assert result.data["transport"] == "outbound_webhook"

    def test_send_agent_message_invalid_agent(self):
        result = send_agent_message("Captain", "hello")
        assert not result.success
        assert result.error_code == "INVALID_AGENT"

    def test_send_agent_message_empty_body(self):
        result = send_agent_message("Agent-1", "   ")
        assert not result.success
        assert result.error_code == "EMPTY_MESSAGE"

    def test_send_agent_message_transport_adapter(self):
        class FakeTransport:
            def send(self, agent_id: str, message: str) -> bool:
                assert agent_id == "Agent-2"
                assert message == "ping"
                return True

        result = send_agent_message(
            "agent-2",
            "ping",
            transport=FakeTransport(),
        )
        assert result.success
        assert result.data["transport"] == "queue_bridge"


class TestPrefixCommands:
    def test_message_in_prefix_commands(self):
        assert "!message" in PREFIX_COMMANDS
