"""Regression: Swarm Commander messaging outage (MaskZero import + embed 1024)."""

from __future__ import annotations

import inspect

import pytest

from agent_tools.discord_commander.lifecycle import bot_lifecycle as bl
from agent_tools.discord_commander.utils.message_chunking import (
    MAX_FIELD_VALUE,
    chunk_message,
    preview_for_embed,
    truncate_embed_field,
)


class TestMaskZeroKeptOutOfCommander:
    def test_setup_hook_source_excludes_maskzero_command_imports(self) -> None:
        src = inspect.getsource(bl.BotLifecycleManager.setup_hook)
        assert "maskzero_connect_commands" not in src
        assert "maskzero_play_commands" not in src
        assert "MaskZeroConnectCommands" not in src
        assert "MaskZeroPlayCommands" not in src
        assert "from agent_tools.discord_commander.commands.messaging_commands" in src

    def test_startup_source_does_not_import_maskzero_views(self) -> None:
        src = inspect.getsource(bl.BotLifecycleManager.send_startup_message)
        assert "maskzero_connect_view" not in src
        assert "maskzero_play_view" not in src
        assert "_post_maskzero" not in src
        assert "views.maskzero" not in src


class TestEmbedPreviewLimits:
    def test_preview_for_embed_never_exceeds_1024(self) -> None:
        long_body = "X" * 5000
        bus_id = "d2a_discord_20260723_131714_e60bfc23"
        preview = preview_for_embed(long_body, bus_id=bus_id)
        assert len(preview) <= MAX_FIELD_VALUE
        assert "preview truncated" in preview
        assert bus_id in preview
        # Full payload untouched (preview is a new string; body not rewritten in-place).
        assert len(long_body) == 5000

    def test_preview_for_embed_short_message_unchanged(self) -> None:
        msg = "nonce_agent1_smoke_001"
        assert preview_for_embed(msg) == msg

    def test_truncate_embed_field_caps_at_limit(self) -> None:
        assert len(truncate_embed_field("A" * 2000)) <= MAX_FIELD_VALUE

    def test_chunk_message_force_splits_single_oversized_line(self) -> None:
        line = "B" * 2500
        chunks = chunk_message(line, max_size=1024)
        assert all(len(c) <= 1024 for c in chunks)
        assert "".join(chunks) == line

    def test_preview_plus_note_edge_case_long_bus_id(self) -> None:
        body = "C" * 1100
        huge_bus = "bus_" + ("z" * 2000)
        preview = preview_for_embed(body, bus_id=huge_bus)
        assert len(preview) <= MAX_FIELD_VALUE
