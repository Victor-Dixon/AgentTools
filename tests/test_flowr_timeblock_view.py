"""Tests for FlowrTimeblock view controllers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent_tools.discord_commander.views import flowr_timeblock_view as ftv


def test_channel_defaults():
    assert "timeblock-victor" in ftv.CHANNEL_DEFAULTS
    assert "timeblock-aria" in ftv.CHANNEL_DEFAULTS
    assert ftv.CHANNEL_DEFAULTS["timeblock-victor"][0] == "FlowrTimeblockVictorView"


def test_victor_view_custom_ids():
    assert "FlowrTimeblockVictorView" in ftv.VIEW_BY_ID
    assert ftv.VIEW_BY_ID["FlowrTimeblockVictorView"].__name__ == "FlowrTimeblockVictorView"


def test_aria_view_custom_ids():
    assert "FlowrTimeblockAriaView" in ftv.VIEW_BY_ID
    assert ftv.VIEW_BY_ID["FlowrTimeblockAriaView"].__name__ == "FlowrTimeblockAriaView"


def test_flowr_urls():
    assert ftv.FLOWR_POMODORO_URL.endswith("/flowr/")
    assert "github.io" in ftv.FLOWR_MAIN_URL
