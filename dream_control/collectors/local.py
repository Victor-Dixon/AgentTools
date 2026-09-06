"""Local environment state: machine, tools, repo checkouts, worktrees."""

from __future__ import annotations

import os
import platform
import socket
from pathlib import Path
from typing import Any

from ..config import OperatorConfig, detect_environment, project_root_for, tool_available
from ._run import run


def collect_machine() -> dict[str, Any]:
    return {
        "environment": detect_environment(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
        "cwd": str(Path.cwd()),
        "home": str(Path.home()),
    }


def collect_tools(config: OperatorConfig | None = None) -> dict[str, bool]:
    config = config or OperatorConfig.load()
    cliprun = Path(os.path.expandvars(config.clipboard_command)).expanduser()
    identity = Path(str(config.vps.get("identity_file", ""))).expanduser()
    return {
        "git": tool_available("git"),
        "gh": tool_available("gh"),
        "ssh": tool_available("ssh"),
        "python3": tool_available("python3"),
        "cliprun": cliprun.exists(),
        "termux_clipboard": tool_available("termux-clipboard-set"),
        "vps_key": bool(str(config.vps.get("identity_file")) and identity.exists()),
        "projectscanner": project_root_for("projectscanner", config) is not None,
        "agenttools": project_root_for("AgentTools", config) is not None,
        "dreamvault": project_root_for("DreamVault", config) is not None,
    }


def collect_repo(repo_root: Path) -> dict[str, Any]:
    """Git facts for one checkout."""
    _, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    _, head, _ = run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    _, subject, _ = run(["git", "log", "-1", "--pretty=%s"], cwd=repo_root)
    _, status, _ = run(["git", "status", "--porcelain"], cwd=repo_root)
    _, branches, _ = run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"], cwd=repo_root
    )
    remote_branches = [
        b.replace("origin/", "", 1)
        for b in branches.splitlines()
        if b.strip() and not b.endswith("/HEAD")
    ]
    dirty = [line for line in status.splitlines() if line.strip()]
    return {
        "path": str(repo_root),
        "branch": branch or "unknown",
        "head": head,
        "head_short": head[:8],
        "head_subject": subject,
        "dirty_count": len(dirty),
        "dirty": dirty[:20],
        "remote_branches": sorted(remote_branches),
    }


def collect_worktrees(repo_root: Path) -> list[dict[str, Any]]:
    code, out, _ = run(["git", "worktree", "list", "--porcelain"], cwd=repo_root)
    if code != 0:
        return []
    worktrees: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in out.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "", 1)
        elif line.strip() == "detached":
            current["branch"] = "(detached)"
    if current:
        worktrees.append(current)
    for worktree in worktrees:
        _, status, _ = run(["git", "status", "--porcelain"], cwd=Path(worktree["path"]))
        worktree["dirty"] = bool(status.strip())
    return worktrees


def collect_repositories(config: OperatorConfig | None = None) -> dict[str, Any]:
    """All portfolio repositories that exist on this machine."""
    config = config or OperatorConfig.load()
    found: dict[str, Any] = {}
    for repo in config.repos:
        root = project_root_for(repo, config)
        if root is None:
            found[repo] = {"present": False}
            continue
        record = collect_repo(root)
        record["present"] = True
        record["pillar"] = (config.repos.get(repo) or {}).get("pillar")
        found[repo] = record
    return found
