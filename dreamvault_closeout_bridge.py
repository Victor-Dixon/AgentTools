from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def dreamvault_root() -> Path:
    override = os.environ.get("DREAMVAULT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / "projects" / "DreamVault"


def closeouts_dir() -> Path:
    return dreamvault_root() / "data" / "closeouts"


def latest_closeout_path() -> Path:
    return closeouts_dir() / "latest.json"


def work_log_dir() -> Path:
    return dreamvault_root() / "data" / "work_log"


def skills_path() -> Path:
    return dreamvault_root() / "data" / "skills" / "skill_tree.json"


def resume_bullets_path() -> Path:
    return dreamvault_root() / "data" / "resume" / "resume_bullets.md"


def portfolio_candidates_path() -> Path:
    return dreamvault_root() / "data" / "portfolio" / "publish_candidates.json"


def load_json(path: Path, default: Any | None = None) -> Any:
    if default is None:
        default = {}
    if not path.exists():
        return {
            "ok": False,
            "missing": True,
            "path": str(path),
            "data": default,
        }
    return {
        "ok": True,
        "missing": False,
        "path": str(path),
        "data": json.loads(path.read_text(encoding="utf-8")),
    }


def load_text(path: Path, default: str = "") -> dict[str, Any]:
    if not path.exists():
        return {
            "ok": False,
            "missing": True,
            "path": str(path),
            "data": default,
        }
    return {
        "ok": True,
        "missing": False,
        "path": str(path),
        "data": path.read_text(encoding="utf-8"),
    }


def load_latest_closeout() -> dict[str, Any]:
    return load_json(latest_closeout_path(), default={})


def load_skill_tree() -> dict[str, Any]:
    return load_json(skills_path(), default={})


def load_resume_bullets() -> dict[str, Any]:
    return load_text(resume_bullets_path(), default="")


def load_portfolio_candidates() -> dict[str, Any]:
    return load_json(portfolio_candidates_path(), default=[])


def passing_verification_items(closeout: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in closeout.get("verification", [])
        if isinstance(item, dict) and item.get("exit_code") == 0
    ]


def summarize_tests(closeout: dict[str, Any]) -> str:
    passing = passing_verification_items(closeout)
    if not passing:
        return "No passing verification recorded"

    summaries = [
        str(item.get("result_summary", "")).strip()
        for item in passing
        if str(item.get("result_summary", "")).strip()
    ]
    return "; ".join(summaries) if summaries else f"{len(passing)} passing verification command(s)"


def compact_actions(closeout: dict[str, Any], limit: int = 5) -> list[str]:
    return [str(item) for item in closeout.get("actions_taken", [])[:limit]]


def compact_files(closeout: dict[str, Any], limit: int = 8) -> list[str]:
    files = []
    for item in closeout.get("files_touched", [])[:limit]:
        if isinstance(item, dict):
            files.append(str(item.get("path", "")))
        else:
            files.append(str(item))
    return [item for item in files if item]


def compact_next_up(closeout: dict[str, Any], limit: int = 3) -> list[dict[str, Any]]:
    items = []
    for item in closeout.get("next_up", [])[:limit]:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "title": item.get("title", ""),
                "repo": item.get("repo", ""),
                "priority": item.get("priority", "P3"),
                "reason": item.get("reason", ""),
            }
        )
    return items


def build_closeout_card_payload(closeout: dict[str, Any] | None = None) -> dict[str, Any]:
    source = None
    if closeout is None:
        loaded = load_latest_closeout()
        source = loaded.get("path")
        if not loaded.get("ok"):
            return {
                "ok": False,
                "missing": True,
                "source": source,
                "title": "No closeout found",
                "description": "DreamVault closeout source is missing.",
            }
        closeout = loaded["data"]

    score = closeout.get("score", {})
    if isinstance(score, dict):
        score_value = score.get("score")
        accepted = score.get("accepted")
    else:
        score_value = score
        accepted = None

    commit = closeout.get("commit", {})
    final_status = closeout.get("final_status", {})

    return {
        "ok": True,
        "missing": False,
        "source": source,
        "schema": closeout.get("schema"),
        "task_id": closeout.get("task_id"),
        "title": closeout.get("title"),
        "repo": closeout.get("repo"),
        "agent": closeout.get("owner_agent"),
        "branch": closeout.get("branch"),
        "status": closeout.get("status"),
        "closed": final_status.get("closed"),
        "score": score_value,
        "accepted": accepted,
        "tests_summary": summarize_tests(closeout),
        "commit_hash": commit.get("commit_hash"),
        "commit_message": commit.get("commit_message"),
        "pushed": commit.get("pushed"),
        "actions": compact_actions(closeout),
        "files": compact_files(closeout),
        "next_up": compact_next_up(closeout),
        "evidence_count": len(closeout.get("evidence", [])),
        "risk_count": len(closeout.get("risks", [])),
    }


def render_closeout_card_text(payload: dict[str, Any]) -> str:
    if not payload.get("ok"):
        return f"⚠️ CLOSEOUT: {payload.get('title', 'Missing')}\n{payload.get('description', '')}"

    lines = [
        f"✅ CLOSEOUT: {payload.get('title')}",
        "",
        f"Repo: {payload.get('repo')}",
        f"Agent: {payload.get('agent')}",
        f"Status: {payload.get('status')}",
        f"Score: {payload.get('score')}",
        f"Tests: {payload.get('tests_summary')}",
        f"Commit: {payload.get('commit_hash')}",
    ]

    actions = payload.get("actions", [])
    if actions:
        lines += ["", "Actions:"]
        lines += [f"- {item}" for item in actions]

    next_up = payload.get("next_up", [])
    if next_up:
        lines += ["", "Next:"]
        for item in next_up:
            lines.append(f"- {item.get('priority')} {item.get('repo')}: {item.get('title')}")

    return "\n".join(lines)
