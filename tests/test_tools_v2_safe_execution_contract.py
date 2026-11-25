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


def test_coverage_adapter_enforces_contract(monkeypatch, tmp_path):
    import subprocess
    import sys
    from tools_v2.categories.testing_tools import CoverageReportTool

    monkeypatch.chdir(tmp_path)
    (tmp_path / "tests").mkdir()
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 1, "coverage failed", "")

    monkeypatch.setattr(subprocess, "run", run)
    tool = CoverageReportTool()
    result = tool.execute({"path": "tests", "min_coverage": 91})
    assert not result.success
    assert result.exit_code == 1
    cmd, kwargs = calls[0]
    assert cmd[:3] == [sys.executable, "-m", "pytest"]
    assert "--cov-fail-under=91" in cmd
    assert "tests" in cmd
    assert kwargs["timeout"] > 0
    for params in ({"path": "../outside"}, {"path": str(tmp_path)}, {"min_coverage": 101}, {"min_coverage": True}, {"path": "-k"}):
        assert not tool.validate(params)[0]
        assert not tool.execute(params).success
    assert len(calls) == 1
