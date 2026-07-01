"""Tests for MaskZero discord-link bot client."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent_tools.discord_commander.maskzero_link_client import consume_link_code


class TestMaskZeroLinkClient:
    def test_missing_secret(self, monkeypatch):
        monkeypatch.delenv("MASKZERO_DISCORD_BOT_SECRET", raising=False)
        result = consume_link_code("ABCD1234", "999")
        assert not result.ok
        assert "SECRET" in result.message.upper()

    @patch("agent_tools.discord_commander.maskzero_link_client.requests.post")
    def test_consume_success(self, mock_post, monkeypatch):
        monkeypatch.setenv("MASKZERO_DISCORD_BOT_SECRET", "test-secret")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "ok": True,
            "linked": True,
            "link": {
                "site_user_id": "spark_u1",
                "character_id": "hero_1",
                "discord_user_id": "999",
            },
        }
        mock_post.return_value = mock_resp

        result = consume_link_code("abcd1234", "999", "guild1")
        assert result.ok
        assert result.link["character_id"] == "hero_1"
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["X-MaskZero-Bot-Secret"] == "test-secret"
        assert call_kwargs["json"]["code"] == "ABCD1234"

    @patch("agent_tools.discord_commander.maskzero_link_client.requests.post")
    def test_consume_expired(self, mock_post, monkeypatch):
        monkeypatch.setenv("MASKZERO_DISCORD_BOT_SECRET", "test-secret")
        mock_resp = MagicMock()
        mock_resp.status_code = 410
        mock_resp.json.return_value = {"ok": False, "message": "Code expired."}
        mock_post.return_value = mock_resp

        result = consume_link_code("OLD12345", "999")
        assert not result.ok
        assert "expired" in result.message.lower()
