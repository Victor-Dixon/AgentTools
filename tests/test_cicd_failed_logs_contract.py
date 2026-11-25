from mcp_servers import cicd_helper_server as ci


def test_invalid_inputs_do_not_execute(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("invalid input reached command")
    monkeypatch.setattr(ci, "_run_command", forbidden)
    for kwargs in ({"run_id": "-1"}, {"run_id": True}, {"run_id": 0},
                   {"limit_lines": 0}, {"limit_lines": 501},
                   {"job_name": "x" * 201}):
        assert ci.get_failed_logs(**kwargs)["success"] is False


def test_failed_log_error_never_fetches_complete_logs(monkeypatch):
    calls = []
    def fake(cmd, cwd):
        calls.append(cmd)
        return {"success": False, "stderr": "private detail"}
    monkeypatch.setattr(ci, "_run_command", fake)
    result = ci.get_failed_logs(run_id=123)
    assert result == {"success": False, "error": "Failed to retrieve failed job logs"}
    assert calls == [["gh", "run", "view", "123", "--log-failed"]]


def test_failed_log_tail_is_bounded(monkeypatch):
    logs = "\n".join("build\tstep\t" + str(i) for i in range(10))
    monkeypatch.setattr(ci, "_run_command", lambda *a: {"success": True, "stdout": logs})
    result = ci.get_failed_logs(run_id=123, limit_lines=2)
    assert result["success"] is True
    assert result["jobs"] == {"build": ["step\t8", "step\t9"]}


def test_output_bounds_even_for_oversize_lines(monkeypatch):
    logs = "build\tstep\t" + "a" * 10000
    monkeypatch.setattr(ci, "_run_command", lambda *a: {"success": True, "stdout": logs})
    result = ci.get_failed_logs(run_id=123)
    assert result["success"] is True
    assert len(result["jobs"]["build"][0]) <= 2048
    assert result["truncated"] is True
