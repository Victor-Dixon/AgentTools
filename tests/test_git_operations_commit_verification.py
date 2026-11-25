"""Real temporary Git repository regression tests for the legacy toolbelt."""
import subprocess
from mcp_servers.git_operations_server import validate_commit


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def test_commit_verification_reports_real_changes(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Fixture")
    (tmp_path / "sample.txt").write_text("one\ntwo\n")
    git(tmp_path, "add", "sample.txt")
    git(tmp_path, "commit", "-qm", "first")
    sha = git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path)
    result = validate_commit(sha)
    assert result["success"] is True
    assert result["commit_hash"] == sha
    assert (result["files_changed"], result["insertions"], result["deletions"]) == (1, 2, 0)


def test_commit_verification_rejects_non_hash_before_git(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("invalid input reached subprocess")
    monkeypatch.setattr(subprocess, "run", forbidden)
    for value in ("--help", "HEAD", "HEAD~1", "abcd", "a" * 40 + "\n", None):
        result = validate_commit(value)
        assert result == {"success": False, "error": "Invalid commit hash"}


def test_commit_verification_accepts_non_utf8_filename(tmp_path, monkeypatch):
    import os
    import pytest

    if os.name != "posix":
        pytest.skip("byte filenames require POSIX")
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Fixture")
    with open(os.fsencode(tmp_path) + b"/file-\xff.txt", "wb") as stream:
        stream.write(b"one\n")
    git(tmp_path, "add", "--all")
    git(tmp_path, "commit", "-qm", "byte filename")
    sha = git(tmp_path, "rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path)
    result = validate_commit(sha)
    assert result["success"] is True
    assert (result["files_changed"], result["insertions"]) == (1, 1)
