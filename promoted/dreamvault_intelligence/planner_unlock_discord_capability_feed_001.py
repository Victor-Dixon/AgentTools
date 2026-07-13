#!/usr/bin/env python3
"""Emit Discord capability evolution feed for planner unlock priority engine."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "planner_unlock_priority_engine_001"
TASK_FILE = ROOT / "runtime/tasks/planner_unlock_priority_engine_001.yaml"
OUT_DIR = ROOT / "data/reports/discord/capability_evolution_feed"
PAYLOAD = OUT_DIR / "latest_capability_evolution_event.json"
CARD = OUT_DIR / "latest_capability_evolution_card.md"
OVERLAY = ROOT / "data/reports/planner/unlock_priority_navigation_overlay.json"
PREVIEW = ROOT / "data/reports/planner_unlock_priority/discord_unlock_priority_preview.md"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def git_head() -> tuple[str, str]:
    try:
        sha = subprocess.check_output(
            ["git", "log", "--format=%H", "-1"],
            cwd=ROOT,
            text=True,
            timeout=15,
        ).strip()
        msg = subprocess.check_output(
            ["git", "log", "--format=%s", "-1"],
            cwd=ROOT,
            text=True,
            timeout=15,
        ).strip()
        return sha, msg
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return "", ""


def load_task() -> dict:
    if not TASK_FILE.is_file():
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML required")
    return yaml.safe_load(TASK_FILE.read_text(encoding="utf-8")) or {}


def load_overlay() -> dict:
    if not OVERLAY.is_file():
        return {}
    try:
        return json.loads(OVERLAY.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def main() -> int:
    if not OVERLAY.is_file():
        sync = subprocess.run(
            [sys.executable, str(ROOT / "runtime/scripts/planner_unlock_priority_sync_navigation_001.py")],
            cwd=ROOT,
            timeout=120,
            check=False,
        )
        if sync.returncode != 0:
            print("OVERLAY_SYNC_FAILED")
            return 1

    task = load_task()
    if not task:
        print(f"TASK_FILE_NOT_FOUND={TASK_ID}")
        return 1

    overlay = load_overlay()
    commit_sha, commit_msg = git_head()

    capability_unlocks = list(task.get("capability_unlocks") or [])
    following = list(task.get("unlocks_following_tasks") or [])
    why = str(task.get("why_this_matters") or "Capability metadata not yet populated.").strip()
    title = str(task.get("title") or TASK_ID)
    closeout = task.get("discord_closeout") or {}

    top_lanes = overlay.get("top_lanes") or []
    self_lane = next((r for r in top_lanes if r.get("task_id") == TASK_ID), None)

    payload = {
        "schema": "dreamvault.discord.capability_evolution_event.v1",
        "generated_at": utc_now(),
        "event_type": "capability_evolution_closeout",
        "channel_key": closeout.get("channel") or "master-task-log",
        "source_task": TASK_ID,
        "source_task_file": str(TASK_FILE.relative_to(ROOT)),
        "title": title,
        "commit": commit_sha,
        "commit_message": commit_msg,
        "capability_unlocks": capability_unlocks,
        "why_this_matters": why,
        "unlocks_following_tasks": following,
        "showcase": list(closeout.get("showcase") or []),
        "planner_context": {
            "engine_score": (self_lane or {}).get("score"),
            "top_lane": top_lanes[0]["task_id"] if top_lanes else None,
            "top_lanes": top_lanes[:5],
            "overlay_source": str(OVERLAY.relative_to(ROOT)) if OVERLAY.is_file() else None,
        },
    }

    lines = [
        "# Capability Unlocked",
        "",
        f"**{title}**",
        "",
        "## Source",
        "",
        f"- Task: `{TASK_ID}`",
        f"- File: `{TASK_FILE.relative_to(ROOT)}`",
        f"- Commit: `{commit_sha or 'unknown'}`",
        "",
        "## Why This Matters",
        "",
        why,
        "",
        "## Capability Unlocks",
        "",
    ]
    for item in capability_unlocks:
        lines.append(f"- {item}")
    lines += ["", "## Unlocks Next", ""]
    for item in following:
        lines.append(f"- {item}")
    if top_lanes:
        lines += ["", "## Top Planner Lanes (unlock engine)", ""]
        for idx, row in enumerate(top_lanes[:5], 1):
            lines.append(
                f"{idx}. `{row.get('task_id')}` score={row.get('score')} — "
                + ", ".join((row.get("reasons") or [])[:2])
            )
    lines += [
        "",
        "## Discord Route",
        "",
        "- Channel: `master-task-log`",
        "- Event: `capability_evolution_closeout`",
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PAYLOAD.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    CARD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok = (
        PAYLOAD.is_file()
        and PAYLOAD.stat().st_size > 0
        and CARD.is_file()
        and "Capability Unlocked" in CARD.read_text(encoding="utf-8")
        and "master-task-log" in PAYLOAD.read_text(encoding="utf-8")
    )
    print(f"CAPABILITY_EVOLUTION_PAYLOAD={PAYLOAD}")
    print(f"CAPABILITY_EVOLUTION_CARD={CARD}")
    print(f"DISCORD_CAPABILITY_EVOLUTION_FEED={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
