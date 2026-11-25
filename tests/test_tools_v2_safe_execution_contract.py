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


def test_coverage_timeout_returns_structured_failure(monkeypatch, tmp_path):
    import subprocess
    from tools_v2.categories.testing_tools import CoverageReportTool

    monkeypatch.chdir(tmp_path)
    (tmp_path / "tests").mkdir()

    def run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", run)
    result = CoverageReportTool().execute({})
    assert not result.success
    assert result.exit_code == 124
    assert result.output is None


def test_mutation_gate_unavailable_fails_closed(monkeypatch):
    import subprocess
    from tools_v2.categories.testing_tools import MutationGateTool

    def unexpected(*args, **kwargs):
        raise AssertionError("Unavailable backend must not execute")

    monkeypatch.setattr(subprocess, "run", unexpected)
    tool = MutationGateTool()
    for threshold in (-1, 101, True, "80"):
        assert not tool.validate({"threshold": threshold})[0]
        assert tool.execute({"threshold": threshold}).exit_code == 2
    assert tool.validate({"threshold": 80})[0]
    result = tool.execute({"threshold": 80})
    assert not result.success
    assert result.exit_code == 69
    assert "unavailable" in result.error_message.lower()


def test_coverage_real_backend_enforces_threshold(monkeypatch, tmp_path):
    from tools_v2.categories.testing_tools import CoverageReportTool

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    (tmp_path / "sample.py").write_text("def choose(flag):\n    if flag:\n        return 1\n    return 0\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_sample.py").write_text(
        "from sample import choose\n\ndef test_choose():\n    assert choose(True) == 1\n"
    )
    tool = CoverageReportTool()
    passing = tool.execute({"path": "tests", "min_coverage": 0})
    assert passing.success, passing.error_message
    failing = tool.execute({"path": "tests", "min_coverage": 100})
    assert not failing.success
    assert failing.exit_code != 0
    assert "Required test coverage" in failing.output


def test_mutation_score_rejects_incomplete_and_empty_results():
    import pytest
    from tools_v2.categories.testing_tools import evaluate_mutation_counts

    assert evaluate_mutation_counts({"killed": 8, "survived": 1, "timeout": 1}, 80).success
    assert not evaluate_mutation_counts({"killed": 8, "survived": 1, "timeout": 1}, 81).success
    for counts in ({}, {"killed": 0, "survived": 0, "timeout": 0},
                   {"killed": True, "survived": 1, "timeout": 0},
                   {"killed": 8, "survived": -1, "timeout": 0},
                   {"killed": 8, "survived": 0, "timeout": 0, "unknown": 1}):
        assert not evaluate_mutation_counts(counts, 0).success
    assert not evaluate_mutation_counts({"killed": 8, "survived": 0, "timeout": 0}, True).success


def test_testing_mcp_discovery_protocol():
    import json
    import subprocess
    import sys
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "run_mutation_tests"}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "run_coverage_analysis", "arguments": {"min_coverage": -1}}},
    ]
    result = subprocess.run([sys.executable, "mcp_servers/testing_server.py"],
                            input="".join(json.dumps(r) + "\n" for r in requests),
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    assert [r["id"] for r in responses] == [1, 2, 3, 4]
    assert responses[0]["result"]["capabilities"] == {"tools": {}}
    assert [t["name"] for t in responses[1]["result"]["tools"]] == ["run_coverage_analysis"]
    assert responses[2]["error"]["code"] == -32602
    assert responses[3]["result"]["isError"] is True
