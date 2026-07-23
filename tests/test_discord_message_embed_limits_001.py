"""Focused regression: Discord !message embed limits + MaskZero isolation."""

from __future__ import annotations

import ast
from pathlib import Path

from agent_tools.discord_commander.utils.message_chunking import (
    MAX_FIELD_VALUE,
    preview_for_embed,
    truncate_embed_field,
)


def test_preview_for_embed_never_exceeds_1024_with_truncation_note():
    long_msg = "A" * 5000
    preview = preview_for_embed(long_msg, bus_id="d2a_discord_20260723_131714_e60bfc23")
    assert len(preview) <= MAX_FIELD_VALUE
    assert "truncated" in preview
    assert "d2a_discord_20260723_131714_e60bfc23" in preview
    # Original long body is NOT what we return (preview only).
    assert preview != long_msg
    assert len(long_msg) > MAX_FIELD_VALUE


def test_preview_plus_note_edge_case_exact_budget():
    # Reproduce prior bug: truncate-to-budget then append note could exceed 1024
    # if marker math was wrong. Final hard-cap must hold.
    msg = "x" * 2000
    for bus_id in (None, "bus_" + "y" * 80):
        out = preview_for_embed(msg, bus_id=bus_id)
        assert len(out) <= 1024


def test_truncate_embed_field_hard_cap():
    assert len(truncate_embed_field("z" * 10000)) <= 1024


def test_setup_hook_ast_has_no_maskzero_command_imports():
    root = Path(__file__).resolve().parents[1]
    path = root / "src" / "agent_tools" / "discord_commander" / "lifecycle" / "bot_lifecycle.py"
    text = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(text)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                imported.add(alias.name)
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
    assert "MaskZeroConnectCommands" not in imported
    assert "MaskZeroPlayCommands" not in imported
    assert "MaskZeroConnectCommands" not in text
    assert "MaskZeroPlayCommands" not in text
    # Startup must not call MaskZero panels (Emergence owns those).
    assert "_post_maskzero_connect_panel" not in text
    assert "_post_maskzero_play_panel" not in text


def test_messaging_commands_module_isolates_maskzero():
    import agent_tools.discord_commander.commands.messaging_commands as mod

    assert hasattr(mod, "MessagingCommands")
    assert not hasattr(mod, "MaskZeroConnectCommands")
    assert not hasattr(mod, "MaskZeroPlayCommands")
    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "preview_for_embed" in src
    assert "MaskZero" not in src
    assert "set_field_at" in src


def test_embed_proxy_mutation_noop_requires_set_field_at():
    """Regression: assigning EmbedProxy.value does not shrink the field for Discord."""
    import discord

    embed = discord.Embed(title="!message QUEUED")
    embed.add_field(name="Message preview", value="Z" * 1500, inline=False)
    proxy = embed.fields[0]
    proxy.value = truncate_embed_field(proxy.value, MAX_FIELD_VALUE)
    # Mutation must not be trusted — length can remain >1024.
    assert len(embed.fields[0].value) > MAX_FIELD_VALUE
    embed.set_field_at(
        0,
        name="Message preview",
        value=truncate_embed_field(embed.fields[0].value, MAX_FIELD_VALUE),
        inline=False,
    )
    assert len(embed.fields[0].value) <= MAX_FIELD_VALUE
