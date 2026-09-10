"""Worktree governance: dirty worktrees are evidence, not garbage."""

from __future__ import annotations

from typing import Any


def worktree_disposition(worktree: dict[str, Any]) -> dict[str, Any]:
    """Decide whether a worktree may be cleaned automatically.

    ``worktree`` is a record produced by ``collectors.local.collect_worktrees``.
    """
    branch = worktree.get("branch") or ""
    dirty = bool(worktree.get("dirty"))
    from .branch import branch_disposition

    branch_state = branch_disposition(branch)
    if branch_state["preserved"]:
        return {
            **worktree,
            "cleanup_allowed": False,
            "reason": f"branch under {branch_state['hold']}",
        }
    if dirty:
        return {
            **worktree,
            "cleanup_allowed": False,
            "reason": "worktree has uncommitted changes; salvage before removal",
        }
    return {**worktree, "cleanup_allowed": True, "reason": "clean worktree, no hold"}
