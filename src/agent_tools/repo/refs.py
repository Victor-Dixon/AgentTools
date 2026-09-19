"""Read-only Git ref helpers shared by repository consumers."""

from __future__ import annotations

from pathlib import Path

from .git import _git_text, repo_root


def remote_default_branch(repo: Path | str, *, remote: str = "origin") -> dict[str, str]:
    """Return the remote-tracking default branch when ``<remote>/HEAD`` is configured.

    This is a fact-only helper. It does not guess a policy default when the symbolic
    remote HEAD is unavailable; callers may apply their own fallback rules.
    """

    root = repo_root(repo)
    symbolic = _git_text(
        root,
        "symbolic-ref",
        "--quiet",
        "--short",
        f"refs/remotes/{remote}/HEAD",
        check=False,
    )
    prefix = f"{remote}/"
    branch = symbolic.removeprefix(prefix) if symbolic.startswith(prefix) else ""
    return {
        "repo": str(root),
        "remote": remote,
        "symbolic_ref": symbolic,
        "branch": branch,
    }
