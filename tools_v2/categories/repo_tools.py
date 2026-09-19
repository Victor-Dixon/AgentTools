"""Thin ToolRegistry adapters for deterministic repository inspection.

The adapters in this module delegate to :mod:`agent_tools.repo`. They must not
reimplement Git subprocess logic or add lifecycle/policy decisions.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agent_tools.repo import (
    compare_refs,
    list_branches,
    list_worktrees,
    repo_identity,
    repo_status,
)

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec


class _RepoAdapter(IToolAdapter):
    """Shared validation/result wrapper for read-only repo tools."""

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)

    def _execute_fact(
        self,
        func: Callable[..., dict[str, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> ToolResult:
        try:
            return ToolResult(success=True, output=func(*args, **kwargs), exit_code=0)
        except Exception as exc:
            return ToolResult(
                success=False,
                output=None,
                exit_code=1,
                error_message=str(exc),
            )


class RepoIdentityTool(_RepoAdapter):
    """Resolve one path to its authoritative Git worktree identity."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="repo.identity",
            version="1.0.0",
            category="repo",
            summary="Resolve repository root, HEAD, branch, Git dir, and origin",
            required_params=["path"],
            optional_params={},
        )

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        return self._execute_fact(repo_identity, params["path"])


class RepoStatusTool(_RepoAdapter):
    """Return tracked-dirty and untracked status facts."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="repo.status",
            version="1.0.0",
            category="repo",
            summary="Return read-only porcelain status facts for a repository",
            required_params=["path"],
            optional_params={},
        )

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        return self._execute_fact(repo_status, params["path"])


class RepoBranchesTool(_RepoAdapter):
    """Return local and remote-tracking branch facts."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="repo.branches",
            version="1.0.0",
            category="repo",
            summary="List local and remote-tracking branches without mutation",
            required_params=["path"],
            optional_params={"remote": "origin"},
        )

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        return self._execute_fact(
            list_branches,
            params["path"],
            remote=params.get("remote", "origin"),
        )


class RepoCompareTool(_RepoAdapter):
    """Compare two refs using ahead/behind and ancestor facts."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="repo.compare",
            version="1.0.0",
            category="repo",
            summary="Compare two Git refs without changing repository state",
            required_params=["path", "base", "head"],
            optional_params={},
        )

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        return self._execute_fact(
            compare_refs,
            params["path"],
            base=params["base"],
            head=params["head"],
        )


class RepoWorktreesTool(_RepoAdapter):
    """Return registered Git worktree facts."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="repo.worktrees",
            version="1.0.0",
            category="repo",
            summary="List registered worktrees with detached/dirty/prunable facts",
            required_params=["path"],
            optional_params={},
        )

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        return self._execute_fact(list_worktrees, params["path"])
