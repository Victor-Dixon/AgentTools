#!/usr/bin/env python3
"""Tests for tools.toolbelt --onboard-status docs/handler contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.toolbelt.cli import onboarding_cli
from tools.toolbelt_registry import ToolRegistry

_EXECUTOR_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "toolbelt"
    / "executors"
    / "onboarding_executor.py"
)


def _load_onboarding_executor():
    """Load onboarding_executor.py without package __init__ circular imports."""
    spec = importlib.util.spec_from_file_location(
        "onboarding_executor_under_test", _EXECUTOR_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_registry_exposes_onboard_status_flag() -> None:
    registry = ToolRegistry()
    tool = registry.get_tool_for_flag("--onboard-status")
    assert tool is not None
    assert tool["module"] == "tools.toolbelt.cli.onboarding_cli"
    assert tool["main_function"] == "cmd_status"
    assert "--onboard-status" in tool["flags"]


def test_validate_agent_accepts_agent_range() -> None:
    onboarding_cli._validate_agent("Agent-2")
    onboarding_cli._validate_agent("Agent-8")


def test_validate_agent_rejects_bad_ids() -> None:
    with pytest.raises(ValueError):
        onboarding_cli._validate_agent("Agent-0")
    with pytest.raises(ValueError):
        onboarding_cli._validate_agent("bot-2")
    with pytest.raises(ValueError):
        onboarding_cli._validate_agent("")


def test_format_onboarding_status_lines_include_canonical_paths() -> None:
    mod = _load_onboarding_executor()
    lines = mod.format_onboarding_status_lines("Agent-2")
    blob = "\n".join(lines)
    assert "agent_workspaces/Agent-2/status.json" in blob
    assert "agent_workspaces/Agent-2/inbox/" in blob
    assert "python -m tools.toolbelt --onboard-status --agent Agent-2" in blob


def test_onboarding_status_executor_prints_and_exits_zero(capsys) -> None:
    mod = _load_onboarding_executor()
    rc = mod.OnboardingExecutor()._onboarding_status(SimpleNamespace(agent="Agent-2"))
    captured = capsys.readouterr().out
    assert rc == 0
    assert "agent_workspaces/Agent-2/status.json" in captured
    assert "--onboard-status" in captured


def test_cmd_status_docstring_mentions_canonical_flag() -> None:
    doc = onboarding_cli.cmd_status.__doc__ or ""
    assert "--onboard-status" in doc
    assert "python -m tools.toolbelt" in doc


def test_cmd_status_requires_agent() -> None:
    with pytest.raises(SystemExit) as exc:
        onboarding_cli.cmd_status([])
    assert exc.value.code == 2
