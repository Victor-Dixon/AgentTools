from __future__ import annotations

from tools_v2.adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from tools_v2.tool_registry import ToolRegistry


def test_tools_v2_registry_loads() -> None:
    registry = ToolRegistry()
    assert registry is not None


def test_tools_v2_registered_tools_have_valid_specs() -> None:
    registry = ToolRegistry()

    tools = registry.list_tools()
    assert tools, "tools_v2 registry returned no tools"

    failures: list[str] = []

    for name in tools:
        try:
            adapter = registry.get_tool(name)
        except Exception as exc:
            failures.append(f"{name}: get_tool failed: {type(exc).__name__}: {exc}")
            continue

        if not isinstance(adapter, IToolAdapter):
            failures.append(f"{name}: adapter is not IToolAdapter: {type(adapter)!r}")
            continue

        try:
            spec = adapter.get_spec()
        except Exception as exc:
            failures.append(f"{name}: get_spec failed: {type(exc).__name__}: {exc}")
            continue

        if not isinstance(spec, ToolSpec):
            failures.append(f"{name}: spec is not ToolSpec: {type(spec)!r}")
            continue

        if not spec.name:
            failures.append(f"{name}: empty spec.name")
        if not spec.version:
            failures.append(f"{name}: empty spec.version")
        if not spec.category:
            failures.append(f"{name}: empty spec.category")
        if not spec.summary:
            failures.append(f"{name}: empty spec.summary")
        if not isinstance(spec.required_params, list):
            failures.append(f"{name}: required_params is not list")
        if not isinstance(spec.optional_params, dict):
            failures.append(f"{name}: optional_params is not dict")

    assert not failures, "tools_v2 registry contract failures:\n" + "\n".join(failures[:100])


def test_tool_result_public_shape_remains_stable() -> None:
    result = ToolResult(success=False, output=None, exit_code=7, error_message="boom", execution_time=1.5)

    assert result.to_dict() == {
        "success": False,
        "output": None,
        "exit_code": 7,
        "error_message": "boom",
        "execution_time": 1.5,
    }
