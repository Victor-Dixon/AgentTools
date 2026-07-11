#!/usr/bin/env python3
"""Tests for D2A template bridge consolidation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.template_bridge import (
    resolve_dreamvault_root,
    wrap_d2a_message,
)


class TestTemplateBridge:
    def test_resolve_dreamvault_root(self) -> None:
        root = resolve_dreamvault_root()
        if Path(r"D:\DreamVault\runtime\messaging\templates\registry.yaml").is_file():
            assert root is not None

    def test_wrap_d2a_includes_reply_policy(self, monkeypatch) -> None:
        if resolve_dreamvault_root() is None:
            pytest.skip("DreamVault not available")
        monkeypatch.setenv("DISCORD_COMMANDER_USE_D2A_TEMPLATE", "1")
        body, meta = wrap_d2a_message(
            agent_id="Agent-1",
            raw_content="Check your inbox",
            sender="Discord User (test)",
        )
        assert meta.get("message_template") == "D2A"
        assert "Preferred Reply Format" in body or "Actions Taken" in body
        assert "#DISCORD #D2A" in body
        assert "Check your inbox" in body

    def test_wrap_raw_when_disabled(self, monkeypatch) -> None:
        monkeypatch.setenv("DISCORD_COMMANDER_USE_D2A_TEMPLATE", "0")
        body, meta = wrap_d2a_message(agent_id="Agent-1", raw_content="plain", sender="x")
        assert body == "plain"
        assert meta.get("message_template") == "raw"
