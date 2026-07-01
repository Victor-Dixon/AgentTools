"""Tests for MaskZeroConnectView panel."""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent_tools.discord_commander.views import maskzero_connect_view as mcv


def test_connect_page_url():
    assert mcv.CONNECT_PAGE_URL.endswith("/discord/connect/")


def test_view_source_has_custom_ids():
    src = inspect.getsource(mcv.MaskZeroConnectView)
    assert "mz_connect_enter_code" in src
    assert "mz_connect_help" in src


def test_view_source_has_link_button():
    src = inspect.getsource(mcv)
    assert mcv.CONNECT_PAGE_URL in src
    assert "ButtonStyle.link" in src
