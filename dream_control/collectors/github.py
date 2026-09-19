"""Live GitHub authority: master head, open PRs, exact-head CI.

Uses the ``gh`` CLI when available (the operator's authenticated surface).
Falls back to local git remote refs so passdown still reports *something*
truthful when offline.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import OperatorConfig, project_root_for, tool_available
from ._run import run


def _gh_json(args: list[str], *, timeout: int = 25) -> tuple[bool, Any, str]:
    code, out, err = run(["gh", *args], timeout=timeout)
    if code != 0:
        return False, None, err or f"gh exited {code}"
    try:
        return True, json.loads(out) if out else None, ""
    except ValueError:
        return False, None, "gh returned non-JSON output"


def collect_authority(repo: str, config: OperatorConfig | None = None) -> dict[str, Any]:
    """Current master head + open PRs + exact-head CI for one repository."""
    config = config or OperatorConfig.load()
    owner = (config.repos.get(repo) or {}).get("owner", "Victor-Dixon")
    slug = f"{owner}/{repo}"
    result: dict[str, Any] = {
        "repo": slug,
        "available": False,
        "source": "none",
        "default_branch": None,
        "master_head": None,
        "open_prs": [],
        "reason": "",
    }

    if tool_available("gh"):
        ok, data, err = _gh_json(
            ["repo", "view", slug, "--json", "defaultBranchRef,name"],
        )
        if ok and isinstance(data, dict):
            branch_ref = data.get("defaultBranchRef") or {}
            result["default_branch"] = branch_ref.get("name")
            result["available"] = True
            result["source"] = "gh"
        else:
            result["reason"] = err

        if result["available"]:
            branch = result["default_branch"] or "master"
            ok, commits, err = _gh_json(
                ["api", f"repos/{slug}/commits/{branch}", "--jq", "{sha:.sha,message:.commit.message}"]
            )
            if ok and isinstance(commits, dict):
                result["master_head"] = commits.get("sha")
                result["master_head_short"] = str(commits.get("sha", ""))[:8]
                result["master_subject"] = (commits.get("message") or "").splitlines()[0:1]

            ok, prs, err = _gh_json(
                [
                    "pr", "list", "--repo", slug, "--state", "open", "--limit", "20",
                    "--json", "number,title,headRefName,headRefOid,isDraft,mergeable",
                ]
            )
            if ok and isinstance(prs, list):
                result["open_prs"] = [
                    {
                        "number": pr.get("number"),
                        "title": pr.get("title"),
                        "head_ref": pr.get("headRefName"),
                        "head": pr.get("headRefOid"),
                        "head_short": str(pr.get("headRefOid") or "")[:8],
                        "draft": pr.get("isDraft"),
                        "mergeable": pr.get("mergeable"),
                    }
                    for pr in prs
                ]
            else:
                result.setdefault("reason", err)
    else:
        result["reason"] = "gh CLI not available"

    if not result["available"]:
        local = _local_authority(repo, config)
        if local:
            result.update(local)
    return result


def _local_authority(repo: str, config: OperatorConfig) -> dict[str, Any] | None:
    root = project_root_for(repo, config)
    if root is None:
        return None
    for branch in ("master", "main"):
        code, sha, _ = run(["git", "rev-parse", f"refs/remotes/origin/{branch}"], cwd=root)
        if code == 0 and sha:
            return {
                "available": True,
                "source": "local_git_remote_ref",
                "default_branch": branch,
                "master_head": sha,
                "master_head_short": sha[:8],
                "reason": "gh unavailable; reporting last fetched origin ref (may be stale)",
                "stale_risk": True,
            }
    return None


def collect_exact_head_ci(repo: str, head_sha: str, config: OperatorConfig | None = None) -> dict[str, Any]:
    """Check runs for one exact commit -- never a branch-level approximation."""
    config = config or OperatorConfig.load()
    owner = (config.repos.get(repo) or {}).get("owner", "Victor-Dixon")
    slug = f"{owner}/{repo}"
    if not head_sha:
        return {"available": False, "reason": "no head sha supplied"}
    if not tool_available("gh"):
        return {"available": False, "reason": "gh CLI not available"}

    ok, data, err = _gh_json(
        ["api", f"repos/{slug}/commits/{head_sha}/check-runs",
         "--jq", "[.check_runs[] | {name:.name, status:.status, conclusion:.conclusion}]"]
    )
    if not ok or not isinstance(data, list):
        return {"available": False, "reason": err or "no check-run data", "head": head_sha}
    checks = {item.get("name"): item.get("conclusion") or item.get("status") for item in data}
    failing = sorted(name for name, state in checks.items() if state in {"failure", "timed_out", "cancelled"})
    pending = sorted(name for name, state in checks.items() if state in {"queued", "in_progress"})
    return {
        "available": True,
        "head": head_sha,
        "head_short": head_sha[:8],
        "checks": checks,
        "failing": failing,
        "pending": pending,
        "green": not failing and not pending and bool(checks),
    }


def cache_path(cache_dir: Path) -> Path:
    return cache_dir / "github.json"
