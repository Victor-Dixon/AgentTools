import subprocess

import pytest

from mcp_servers.git_operations_server import verify_work_exists_mcp


def test_compatibility_evidence(tmp_path, monkeypatch):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], text=True).strip()

    git("init", "-q")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "user.name", "Agent-1")
    (tmp_path / "sample.txt").write_text("evidence\n")
    git("add", "sample.txt")
    git("commit", "-qm", "fixture")
    sha = git("rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path)
    result = verify_work_exists_mcp(["sample.txt"])
    assert result["success"] and result["verified"], result
    assert result["commits"][0]["commit_hash"] == sha
    assert not verify_work_exists_mcp(["sample.txt"], "Agent-1")["verified"]
    assert not verify_work_exists_mcp(["sample.txt", "missing.txt"])["verified"]
    assert not verify_work_exists_mcp([])["verified"]
    assert not verify_work_exists_mcp([":(glob)**"])["success"]
