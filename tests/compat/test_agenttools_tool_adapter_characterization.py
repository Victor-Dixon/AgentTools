"""
Characterization tests for AgentTools tool adapter primitives.

These tests lock the current AgentTools-owned behavior before any
Dream.os-Core BusMessage compatibility adapter is introduced.
"""

from __future__ import annotations

from tools_v2.adapters.base_adapter import ToolResult, ToolSpec


def test_tool_result_to_dict_preserves_current_public_shape() -> None:
    result = ToolResult(
        success=True,
        output={"value": 42},
        exit_code=0,
        error_message=None,
        execution_time=0.25,
    )

    assert result.to_dict() == {
        "success": True,
        "output": {"value": 42},
        "exit_code": 0,
        "error_message": None,
        "execution_time": 0.25,
    }


def test_tool_spec_validate_params_reports_missing_required_params() -> None:
    spec = ToolSpec(
        name="demo_tool",
        version="1.0.0",
        category="demo",
        summary="Demo tool.",
        required_params=["query", "limit"],
        optional_params={"timeout": 30},
    )

    valid, missing = spec.validate_params({"query": "hello"})

    assert valid is False
    assert missing == ["limit"]


def test_tool_spec_validate_params_accepts_required_params() -> None:
    spec = ToolSpec(
        name="demo_tool",
        version="1.0.0",
        category="demo",
        summary="Demo tool.",
        required_params=["query", "limit"],
        optional_params={"timeout": 30},
    )

    valid, missing = spec.validate_params({"query": "hello", "limit": 5})

    assert valid is True
    assert missing == []
