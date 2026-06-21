from __future__ import annotations

from tools_v2.adapters.base_adapter import ToolResult
from tools_v2.tool_registry import ToolRegistry


SAFE_TOOL_PARAMS = {
    "health.ping": {},
    "health.snapshot": {},
    "v2.check": {"path": "."},
    "v2.report": {},
    "comp.check": {"path": "."},
    "config.list-sources": {},
}


def test_safe_tools_validate_and_execute_without_crashing() -> None:
    registry = ToolRegistry()
    available = set(registry.list_tools())

    selected = {
        name: params
        for name, params in SAFE_TOOL_PARAMS.items()
        if name in available
    }

    assert selected, "No expected safe tools are currently registered"

    failures: list[str] = []

    for name, params in selected.items():
        try:
            tool = registry.get_tool(name)
            valid, missing = tool.validate(params)
            if not valid:
                failures.append(f"{name}: validate failed, missing/invalid={missing}")
                continue

            result = tool.execute(params, context={"test_mode": True})
            if not isinstance(result, ToolResult):
                failures.append(f"{name}: execute did not return ToolResult: {type(result)!r}")
                continue

            output = result.to_dict()
            for key in ["success", "output", "exit_code", "error_message", "execution_time"]:
                if key not in output:
                    failures.append(f"{name}: missing ToolResult key {key}")

        except Exception as exc:
            failures.append(f"{name}: crashed: {type(exc).__name__}: {exc}")

    assert not failures, "Safe tool execution failures:\n" + "\n".join(failures)
