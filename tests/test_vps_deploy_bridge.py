"""Tests for guarded VPS deploy bridge."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BRIDGE = ROOT / "tools" / "vps_deploy_bridge"
MODULE_PATH = BRIDGE / "vps_deploy_bridge.py"

spec = importlib.util.spec_from_file_location("vps_deploy_bridge", MODULE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["vps_deploy_bridge"] = bridge
spec.loader.exec_module(bridge)


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    source = tmp_path / "artifacts" / "config.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}\n', encoding="utf-8")
    return tmp_path


def _base_request(**overrides) -> dict:
    req = {
        "request_id": "test-deploy-001",
        "agent_id": "Agent-Test",
        "repo": "agent-tools",
        "source_path": "artifacts/config.json",
        "target_path": "/opt/dreamos/swarm-commander/config.json",
        "action": "upload_file",
        "reason": "test upload",
        "created_at": "2025-06-21T12:00:00Z",
        "dry_run": True,
    }
    req.update(overrides)
    return req


class TestValidation:
    def test_valid_upload_request_passes(self, repo_root: Path):
        request = _base_request()
        errors = bridge.validate_request(request, repo_root)
        assert errors == []

    def test_invalid_target_path_fails(self, repo_root: Path):
        request = _base_request(target_path="/srv/forbidden/app.conf")
        errors = bridge.validate_request(request, repo_root)
        assert any("target_path must start with" in e for e in errors)

    def test_dangerous_command_fails(self, repo_root: Path):
        request = _base_request(
            action="run_command",
            target_path="/opt/dreamos/scripts/run.sh",
            command="rm -rf / && echo done",
        )
        errors = bridge.validate_request(request, repo_root)
        assert any("blocked command pattern" in e for e in errors)

    def test_root_ssh_path_write_fails(self, repo_root: Path):
        request = _base_request(target_path="/root/.ssh/authorized_keys")
        errors = bridge.validate_request(request, repo_root)
        assert any("blocked target path prefix" in e for e in errors)

    def test_service_restart_allowlist_works(self, repo_root: Path):
        allowed = _base_request(
            action="restart_service",
            target_path="/opt/dreamos/swarm-commander/",
            service_name="swarm-commander",
        )
        assert bridge.validate_request(allowed, repo_root) == []

        denied = _base_request(
            action="restart_service",
            target_path="/opt/dreamos/swarm-commander/",
            service_name="docker",
        )
        errors = bridge.validate_request(denied, repo_root)
        assert any("service not in allowlist" in e for e in errors)


class TestExecutionModes:
    def test_dry_run_does_not_execute(self, repo_root: Path, monkeypatch: pytest.MonkeyPatch):
        executed: list[str] = []

        def fake_execute(planned: list[str]) -> list[dict]:
            executed.extend(planned)
            return [{"command": c, "returncode": 0, "stdout": "", "stderr": ""} for c in planned]

        monkeypatch.delenv("DREAMOS_DEPLOY_MODE", raising=False)
        request = _base_request(dry_run=True)
        report = bridge.process_request(request, repo_root=repo_root, runner=fake_execute)

        assert executed == []
        assert report.executed is False
        assert report.mode == "dry_run"
        assert report.verify_line == bridge.VERIFY_DRY_RUN

    def test_execute_mode_requires_deploy_mode_execute(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch
    ):
        executed: list[str] = []

        def fake_execute(planned: list[str]) -> list[dict]:
            executed.extend(planned)
            return [{"command": c, "returncode": 0, "stdout": "", "stderr": ""} for c in planned]

        monkeypatch.setenv("DREAMOS_DEPLOY_MODE", "dry_run")
        request = _base_request(dry_run=False)
        report = bridge.process_request(request, repo_root=repo_root, runner=fake_execute)

        assert executed == []
        assert report.mode == "dry_run"

        monkeypatch.setenv("DREAMOS_DEPLOY_MODE", "execute")
        monkeypatch.setenv("DREAMOS_VPS_HOST", "vps.example.com")
        monkeypatch.setenv("DREAMOS_VPS_USER", "deploy")
        monkeypatch.setenv("DREAMOS_VPS_SSH_KEY", "/tmp/fake_key")
        report = bridge.process_request(request, repo_root=repo_root, runner=fake_execute)

        assert executed
        assert report.mode == "execute"
        assert report.verify_line == bridge.VERIFY_EXECUTED


class TestSecretsAndExamples:
    SECRET_PATTERNS = [
        re.compile(r"-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"password\s*=\s*[^\s\"']+", re.I),
        re.compile(r"DISCORD_BOT_TOKEN\s*=\s*\S+"),
        re.compile(r"ssh-rsa\s+[A-Za-z0-9+/=]{20,}"),
    ]

    def test_no_secrets_in_example_files(self):
        example = BRIDGE / "examples" / "deploy_request.example.json"
        text = example.read_text(encoding="utf-8")
        for pattern in self.SECRET_PATTERNS:
            assert not pattern.search(text), f"secret pattern found in example: {pattern.pattern}"

        data = json.loads(text)
        for key in ("password", "private_key", "ssh_key", "token", "secret"):
            assert key not in data


class TestReports:
    def test_report_written_on_dry_run(
        self, repo_root: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        reports_dir = tmp_path / "reports" / "vps_deploy_bridge"
        monkeypatch.setattr(bridge, "REPORTS_DIR", reports_dir)
        request = _base_request()
        report = bridge.process_request(request, repo_root=repo_root)

        report_path = reports_dir / f"{report.request_id}.json"
        assert report_path.is_file()
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert payload["status"] == "dry_run"
        assert payload["planned_commands"]
