import subprocess
from mcp_servers.git_operations_server import verify_git_work


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def test_git_evidence_is_not_authenticated_completion(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Agent-10")
    (tmp_path / "sample.txt").write_text("observed\n")
    git(tmp_path, "add", "sample.txt")
    git(tmp_path, "commit", "-qm", "unrelated description")
    sha = git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path)
    for agent in ("Agent-1", "Agent-10"):
        result = verify_git_work(agent, "sample.txt", "claimed semantic repair")
        assert result["success"] is True, result
        assert result["verified"] is False
        assert result["evidence"]["commit_hash"] == sha
        assert result["evidence"]["files_changed"] == ["sample.txt"]
        assert result["identity_verified"] is False


def test_invalid_file_scope_rejected_before_git(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("invalid input reached Git")
    monkeypatch.setattr(subprocess, "run", forbidden)
    for path in ("../outside", "/etc/passwd", ":(glob)**", "", "."):
        assert verify_git_work("Agent-1", path, "claim")["success"] is False
    assert verify_git_work("Agent-1", "sample.txt", "claim", True)["success"] is False


def test_subdirectory_evidence_and_utc(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Agent-10")
    monkeypatch.setenv("TZ", "UTC")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "file.txt").write_text("observed\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "nested change")
    monkeypatch.chdir(nested)
    result = verify_git_work("Agent-10", "file.txt", "claim")
    assert result["success"] is True, result
    assert result["evidence"]["files_changed"] == ["file.txt"]
    assert result["verified"] is False
