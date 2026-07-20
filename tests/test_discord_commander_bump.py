"""Unit coverage for Discord Commander !bump bridge (no live PyAutoGUI)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from agent_tools.discord_commander.bump_bridge import bump_agent, bump_quad


def test_bump_agent_invalid():
    with patch(
        "agent_tools.discord_commander.bump_bridge.resolve_dreamvault_root",
        return_value=Path("D:/DreamVault"),
    ), patch(
        "agent_tools.discord_commander.bump_bridge.bootstrap_commander_env"
    ):
        result = bump_agent("not-an-agent", live=False, dry_run=True)
    assert result.success is False
    assert result.error_code == "INVALID_AGENT"


def test_bump_agent_dry_run_pass(tmp_path: Path):
    report = tmp_path / "data" / "reports" / "coordination"
    report.mkdir(parents=True)
    (report / "quad_force_agent_mode_ctrl_i_latest.json").write_text(
        '{"status":"DRY_RUN_PASS"}',
        encoding="utf-8",
    )
    with patch(
        "agent_tools.discord_commander.bump_bridge.resolve_dreamvault_root",
        return_value=tmp_path,
    ), patch(
        "agent_tools.discord_commander.bump_bridge.bootstrap_commander_env"
    ), patch(
        "agent_tools.discord_commander.bump_bridge._run_script",
        return_value=(0, "QUAD_FORCE_AGENT_MODE=DRY_RUN_PASS"),
    ) as run:
        result = bump_agent("Agent-2", live=False, dry_run=True)
    assert result.success is True
    assert result.data["agents"] == ["Agent-2"]
    args = run.call_args[0][1]
    assert "--dry-run" in args
    assert "--target" in args and "starter_location_box" in args
    assert "--enter" in args
    assert "Agent-2" in args


def test_bump_quad_live_blocked_without_env(tmp_path: Path):
    with patch(
        "agent_tools.discord_commander.bump_bridge.resolve_dreamvault_root",
        return_value=tmp_path,
    ), patch(
        "agent_tools.discord_commander.bump_bridge.bootstrap_commander_env"
    ), patch(
        "agent_tools.discord_commander.bump_bridge._live_allowed",
        return_value=False,
    ):
        result = bump_quad(live=True, dry_run=False)
    assert result.success is False
    assert result.error_code == "LIVE_INJECTION_BLOCKED"
