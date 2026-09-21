"""Mobile Discord devlog presentation: no network or production workspace writes."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import devlog_poster
from tools.devlog_presentation import render_devlog_pages, split_lossless


def test_long_single_line_is_paginated_without_loss():
    source = "X" * 9500 + "\nlast line"
    chunks = split_lossless(source, 1700)
    assert len(chunks) >= 6
    assert all(0 < len(chunk) <= 1700 for chunk in chunks)
    assert "".join(chunks) == source


def test_mission_brief_is_source_based_and_full_source_is_preserved():
    source = (
        "Task: Repair Discord delivery\n"
        "Actions Taken: Added receipt tracking.\n"
        "Verification: Tests reported PASS; GitHub CI not run.\n"
        "Blockers: Waiting for independent review.\n"
        "Next: Run exact-head CI.\n"
        + "technical details " * 200
    )
    pages = render_devlog_pages("Agent-2", source)
    assert len(pages) > 1
    assert all(len(page) <= 1900 for page in pages)
    assert "Repair Discord delivery" in pages[0]
    assert "GitHub CI not run" in pages[0]
    assert "Waiting for independent review" in pages[0]
    assert "Run exact-head CI" in pages[0]
    assert "independently verified" not in pages[0].lower()
    assert "".join(page.split("\n", 1)[1] for page in pages[1:]) == source


def test_unstructured_input_does_not_invent_success():
    pages = render_devlog_pages("Agent-4", "Investigated one queue. No conclusion yet.")
    assert "no structured briefing fields" in pages[0].lower()
    assert "PASS" not in pages[0]
    assert all(len(page) <= 1900 for page in pages)


def test_empty_devlog_is_not_publishable():
    with pytest.raises(ValueError):
        render_devlog_pages("Agent-2", "  \n  ")


def test_webhook_payloads_are_mobile_embeds_and_suppress_mentions(tmp_path, monkeypatch):
    monkeypatch.setattr(devlog_poster, "project_root", tmp_path)
    monkeypatch.setenv("DISCORD_WEBHOOK_AGENT_2", "https://example.invalid/webhook")
    monkeypatch.setitem(sys.modules, "dotenv", SimpleNamespace(load_dotenv=lambda *a, **k: None))
    captured = []
    def fake_post(url, json, timeout):
        captured.append(json)
        return SimpleNamespace(status_code=204)
    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=fake_post))
    source = tmp_path / "devlog.md"
    source.write_text("Task: Ship safe cards\nVerification: local only\n" + "A" * 3600, encoding="utf-8")
    assert devlog_poster.post_devlog_to_discord("Agent-2", str(source)) is True
    assert len(captured) > 2
    assert all(msg["allowed_mentions"] == {"parse": []} for msg in captured)
    assert all(len(msg["embeds"][0]["description"]) <= 1900 for msg in captured)
    assert all("Page " in msg["embeds"][0]["footer"]["text"] for msg in captured)
    assert json.loads((tmp_path / "website_data/agent_activity/Agent-2_latest_devlog.json").read_text())["content"] == source.read_text()


def test_failed_webhook_page_reports_failure_not_success(tmp_path, monkeypatch):
    monkeypatch.setattr(devlog_poster, "project_root", tmp_path)
    monkeypatch.setenv("DISCORD_WEBHOOK_AGENT_2", "https://example.invalid/webhook")
    monkeypatch.setitem(sys.modules, "dotenv", SimpleNamespace(load_dotenv=lambda *a, **k: None))
    monkeypatch.setitem(
        sys.modules, "requests",
        SimpleNamespace(post=lambda *a, **k: SimpleNamespace(status_code=500)),
    )
    source = tmp_path / "devlog.md"
    source.write_text("Task: Check failure reporting\n", encoding="utf-8")
    assert devlog_poster.post_devlog_to_discord("Agent-2", str(source)) is False
    assert (tmp_path / "website_data/agent_activity/Agent-2_latest_devlog.md").read_text() == source.read_text()
