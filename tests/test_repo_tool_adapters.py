from __future__ import annotations

import subprocess
from pathlib import Path

from tools_v2.categories.repo_tools import (
    RepoBranchesTool,
    RepoCompareTool,
    RepoIdentityTool,
    RepoStatusTool,
    RepoWorktreesTool,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(
        ["git", "init", "-b", "master", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    _git(path, "config", "user.email", "repo-adapter@example.invalid")
    _git(path, "config", "user.name", "Repo Adapter Test")
    (path / "README.md").write_text("base\n", encoding="utf-8")
    _git(path, "add", "README.md")
    _git(path, "commit", "-m", "base")
    return path


def test_repo_adapters_expose_expected_specs() -> None:
    tools = [
        RepoIdentityTool(),
        RepoStatusTool(),
        RepoBranchesTool(),
        RepoCompareTool(),
        RepoWorktreesTool(),
    ]

    assert [tool.get_spec().name for tool in tools] == [
        "repo.identity",
        "repo.status",
        "repo.branches",
        "repo.compare",
        "repo.worktrees",
    ]
    assert all(tool.get_spec().category == "repo" for tool in tools)


def test_repo_adapters_delegate_to_shared_python_contract(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")

    identity = RepoIdentityTool().execute({"path": str(repo)})
    assert identity.success is True
    assert identity.output["path"] == str(repo.resolve())

    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    status = RepoStatusTool().execute({"path": str(repo)})
    assert status.success is True
    assert status.output["dirty_count"] == 1

    _git(repo, "checkout", "-b", "feat/demo")
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")

    branches = RepoBranchesTool().execute({"path": str(repo)})
    assert branches.success is True
    assert branches.output["local_count"] == 2

    comparison = RepoCompareTool().execute(
        {
            "path": str(repo),
            "base": "master",
            "head": "feat/demo",
        }
    )
    assert comparison.success is True
    assert comparison.output["ahead"] == 1
    assert comparison.output["behind"] == 0

    detached = tmp_path / "detached"
    _git(repo, "worktree", "add", "--detach", str(detached), "HEAD")

    worktrees = RepoWorktreesTool().execute({"path": str(repo)})
    assert worktrees.success is True
    assert worktrees.output["count"] == 2
    assert worktrees.output["detached_count"] == 1


def test_repo_adapter_failure_is_structured(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()

    result = RepoIdentityTool().execute({"path": str(plain)})

    assert result.success is False
    assert result.exit_code == 1
    assert result.output is None
    assert result.error_message
