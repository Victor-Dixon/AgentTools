"""Deterministic, read-only Git repository inspection primitives.

These functions deliberately stop at facts. They do not classify branch lifecycle,
choose cleanup actions, delete refs, prune worktrees, or apply policy.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


class GitRepoToolError(RuntimeError):
    """Raised when a Git inspection command cannot be completed safely."""


def _run_git(
    repo: Path | str,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    path = Path(repo).expanduser().resolve()
    env = os.environ.copy()
    # Prevent optional Git index refreshes/locks during observational scans.
    env["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitRepoToolError(f"git {' '.join(args)} failed for {path}: {exc}") from exc

    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit={proc.returncode}"
        raise GitRepoToolError(f"git {' '.join(args)} failed for {path}: {detail}")
    return proc


def _git_text(repo: Path | str, *args: str, check: bool = True) -> str:
    return _run_git(repo, *args, check=check).stdout.strip()


def repo_root(repo: Path | str) -> Path:
    """Resolve a path inside a worktree to its Git toplevel."""
    root = _git_text(repo, "rev-parse", "--show-toplevel")
    if not root:
        raise GitRepoToolError(f"not a Git worktree: {Path(repo).expanduser().resolve()}")
    return Path(root).resolve()


def repo_identity(repo: Path | str) -> dict[str, Any]:
    """Return stable identity facts for one Git worktree."""
    root = repo_root(repo)
    return {
        "path": str(root),
        "name": root.name,
        "git_dir": _git_text(root, "rev-parse", "--git-dir"),
        "head": _git_text(root, "rev-parse", "HEAD"),
        "current_branch": _git_text(root, "branch", "--show-current", check=False),
        "origin": _git_text(root, "remote", "get-url", "origin", check=False),
        "is_inside_work_tree": _git_text(root, "rev-parse", "--is-inside-work-tree") == "true",
    }


def repo_status(repo: Path | str) -> dict[str, Any]:
    """Return normalized porcelain status without interpreting file meaning."""
    root = repo_root(repo)
    proc = _run_git(root, "status", "--porcelain=v1", "--untracked-files=all")

    entries: list[dict[str, Any]] = []
    dirty_count = 0
    untracked_count = 0

    for raw in proc.stdout.splitlines():
        if len(raw) < 3:
            continue
        index = raw[:2]
        payload = raw[3:]
        old_path = ""
        path = payload
        if " -> " in payload:
            old_path, path = payload.split(" -> ", 1)

        untracked = index == "??"
        if untracked:
            untracked_count += 1
        else:
            dirty_count += 1

        entries.append(
            {
                "index": index,
                "path": path,
                "old_path": old_path,
                "untracked": untracked,
            }
        )

    return {
        "repo": str(root),
        "dirty_count": dirty_count,
        "untracked_count": untracked_count,
        "total": dirty_count + untracked_count,
        "entries": entries,
    }


def list_branches(repo: Path | str, *, remote: str = "origin") -> dict[str, Any]:
    """List local and one remote's tracking refs as JSON-ready facts."""
    root = repo_root(repo)
    fmt = "%(refname)%00%(objectname)%00%(committerdate:unix)%00%(upstream:short)"

    locals_raw = _git_text(root, "for-each-ref", f"--format={fmt}", "refs/heads", check=False)
    remotes_raw = _git_text(
        root,
        "for-each-ref",
        f"--format={fmt}",
        f"refs/remotes/{remote}",
        check=False,
    )

    def parse(raw: str, prefix: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for line in raw.splitlines():
            parts = line.split("\x00")
            if len(parts) != 4:
                continue
            ref, sha, timestamp, upstream = parts
            if ref == f"refs/remotes/{remote}/HEAD":
                continue
            name = ref.removeprefix(prefix)
            rows.append(
                {
                    "name": name,
                    "ref": ref,
                    "sha": sha,
                    "commit_timestamp": int(timestamp) if timestamp.isdigit() else None,
                    "upstream": upstream,
                }
            )
        rows.sort(key=lambda row: row["name"])
        return rows

    local = parse(locals_raw, "refs/heads/")
    remote_rows = parse(remotes_raw, f"refs/remotes/{remote}/")
    return {
        "repo": str(root),
        "remote": remote,
        "local_count": len(local),
        "remote_count": len(remote_rows),
        "local": local,
        "remote_branches": remote_rows,
    }


def compare_refs(repo: Path | str, *, base: str, head: str) -> dict[str, Any]:
    """Compare two refs and report ahead/behind plus ancestor containment."""
    root = repo_root(repo)
    counts = _git_text(root, "rev-list", "--left-right", "--count", f"{base}...{head}")
    try:
        left_only, right_only = (int(value) for value in counts.split())
    except (TypeError, ValueError) as exc:
        raise GitRepoToolError(f"unexpected rev-list count output: {counts!r}") from exc

    ancestor = _run_git(root, "merge-base", "--is-ancestor", head, base, check=False)
    if ancestor.returncode not in (0, 1):
        detail = ancestor.stderr.strip() or ancestor.stdout.strip() or f"exit={ancestor.returncode}"
        raise GitRepoToolError(f"git merge-base --is-ancestor failed: {detail}")

    return {
        "repo": str(root),
        "base": base,
        "head": head,
        "base_sha": _git_text(root, "rev-parse", base),
        "head_sha": _git_text(root, "rev-parse", head),
        "ahead": right_only,
        "behind": left_only,
        "head_is_ancestor_of_base": ancestor.returncode == 0,
    }


def parse_worktree_porcelain(raw: str) -> list[dict[str, Any]]:
    """Parse ``git worktree list --porcelain`` into normalized records."""
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}

    def flush() -> None:
        nonlocal current
        if current:
            records.append(current)
            current = {}

    for line in raw.splitlines():
        if not line.strip():
            flush()
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            if current:
                flush()
            current["path"] = value
        elif key == "HEAD":
            current["head"] = value
        elif key == "branch":
            current["branch_ref"] = value
            current["branch"] = value.removeprefix("refs/heads/")
        elif key == "detached":
            current["detached"] = True
        elif key == "bare":
            current["bare"] = True
        elif key == "locked":
            current["locked"] = True
            current["locked_reason"] = value
        elif key == "prunable":
            current["prunable"] = True
            current["prunable_reason"] = value

    flush()
    return records


def list_worktrees(repo: Path | str) -> dict[str, Any]:
    """List registered Git worktrees and attach raw status counts when available."""
    root = repo_root(repo)
    raw = _git_text(root, "worktree", "list", "--porcelain")
    records = parse_worktree_porcelain(raw)
    items: list[dict[str, Any]] = []

    for record in records:
        path = Path(str(record.get("path", ""))).expanduser().resolve()
        exists = path.exists()
        bare = bool(record.get("bare", False))
        status: dict[str, Any] = {
            "dirty_count": 0,
            "untracked_count": 0,
            "total": 0,
            "entries": [],
        }
        if exists and not bare:
            status = repo_status(path)

        items.append(
            {
                "path": str(path),
                "head": str(record.get("head", "")),
                "branch": str(record.get("branch", "")),
                "branch_ref": str(record.get("branch_ref", "")),
                "exists": exists,
                "detached": bool(record.get("detached", False)),
                "bare": bare,
                "locked": bool(record.get("locked", False)),
                "locked_reason": str(record.get("locked_reason", "")),
                "prunable": bool(record.get("prunable", False)),
                "prunable_reason": str(record.get("prunable_reason", "")),
                "dirty_count": int(status["dirty_count"]),
                "untracked_count": int(status["untracked_count"]),
                "dirty_total": int(status["total"]),
                "status_entries": status["entries"],
            }
        )

    items.sort(key=lambda row: row["path"])
    return {
        "repo": str(root),
        "count": len(items),
        "dirty_count": sum(1 for row in items if row["dirty_total"] > 0),
        "detached_count": sum(1 for row in items if row["detached"]),
        "locked_count": sum(1 for row in items if row["locked"]),
        "prunable_count": sum(1 for row in items if row["prunable"]),
        "items": items,
    }
