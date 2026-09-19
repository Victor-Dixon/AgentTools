"""Regression tests for the hidden GitHub runner registration file."""

from __future__ import annotations

import shlex
import subprocess

import pytest

from dream_control.collectors import vps as vps_collector
from dream_control.config import OperatorConfig


@pytest.mark.parametrize(
    ("registered", "alive", "expected_healthy"),
    [(True, True, True), (False, True, False), (True, False, False)],
)
def test_runner_registration_listing_and_health(
    tmp_path, monkeypatch, registered, alive, expected_healthy
):
    """Exercise the actual ls flags against a disposable runner directory."""
    runner = tmp_path / "runner"
    runner.mkdir()
    if registered:
        (runner / ".runner").write_text("fixture", encoding="utf-8")
    (runner / "run.sh").write_text("fixture", encoding="utf-8")
    identity = tmp_path / "identity"
    identity.write_text("fixture", encoding="utf-8")
    config = OperatorConfig()
    config.vps = {**config.vps, "identity_file": str(identity), "runner_dir": str(runner)}
    monkeypatch.setattr(vps_collector, "tool_available", lambda name: name == "ssh")

    def fake_run(argv, *, timeout):
        assert argv[0] == "ssh"
        # Only the listing command is executed, on our local fixture.
        # No SSH connection, runner command, or service operation occurs.
        command = argv[-1]
        listing = command.split("echo '---RUNNER_FILES---'; ", 1)[1]
        listing = listing.split("2>/dev/null", 1)[0].strip()
        names = subprocess.run(
            shlex.split(listing), capture_output=True, text=True, check=True
        ).stdout
        output = (
            "fixture-host\n---RUNNER_PROC---\n"
            + ("123 Runner.Listener\n" if alive else "")
            + "---RUNNER_FILES---\n" + names
            + "---BRAIN---\n---SYSTEMD---\ninactive\n"
            + "---REPOS---\n---UPTIME---\nup 1 hour\n"
        )
        return 0, output, ""

    monkeypatch.setattr(vps_collector, "run", fake_run)
    result = vps_collector.collect(config)
    assert result["reachable"] is True
    assert result["runner_registered"] is registered
    assert result["runner_alive"] is alive
    assert result["healthy"] is expected_healthy
    if registered:
        assert ".runner" in result["runner_registration_files"]
    else:
        assert "registration (.runner) missing" in result["reason"]
