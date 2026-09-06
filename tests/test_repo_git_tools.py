from __future__ import annotations

import subprocess
from pathlib import Path

from agent_tools.repo import compare_refs, list_branches, list_worktrees, repo_identity, repo_status


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def _init_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init", "-b", "master", str(path)], check=True, capture_output=True, text=True)
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Repo Tools Test")
    (path / "README.md").write_text("base\n", encoding="utf-8")
    _git(path, "add", "README.md")
    _git(path, "commit", "-m", "base")
    return path


def test_repo_identity_resolves_nested_path(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)

    row = repo_identity(nested)

    assert row["path"] == str(repo.resolve())
    assert row["name"] == "repo"
    assert row["current_branch"] == "master"
    assert len(row["head"]) == 40
    assert row["is_inside_work_tree"] is True


def test_repo_status_separates_tracked_and_untracked(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    (repo / "new.txt").write_text("new\n", encoding="utf-8")

    row = repo_status(repo)

    assert row["dirty_count"] == 1
    assert row["untracked_count"] == 1
    assert row["total"] == 2
    assert {item["path"] for item in row["entries"]} == {"README.md", "new.txt"}


def test_branch_inventory_and_compare_are_fact_only(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    _git(repo, "checkout", "-b", "feat/demo")
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")

    inventory = list_branches(repo)
    comparison = compare_refs(repo, base="master", head="feat/demo")

    assert inventory["local_count"] == 2
    assert [row["name"] for row in inventory["local"]] == ["feat/demo", "master"]
    assert inventory["remote_count"] == 0
    assert comparison["ahead"] == 1
    assert comparison["behind"] == 0
    assert comparison["head_is_ancestor_of_base"] is False


def test_worktree_inventory_reports_detached_and_dirty_facts(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path / "repo")
    detached = tmp_path / "detached"
    _git(repo, "worktree", "add", "--detach", str(detached), "HEAD")
    (detached / "scratch.txt").write_text("scratch\n", encoding="utf-8")

    row = list_worktrees(repo)

    assert row["count"] == 2
    assert row["detached_count"] == 1
    assert row["dirty_count"] == 1
    detached_row = next(item for item in row["items"] if item["path"] == str(detached.resolve()))
    assert detached_row["detached"] is True
    assert detached_row["untracked_count"] == 1
    assert detached_row["prunable"] is False
