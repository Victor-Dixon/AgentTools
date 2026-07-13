#!/usr/bin/env python3
"""Bridge capability graph runtime → Discord capability evolution feed (unlock-chain slice)."""

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
TASK_ID = "discord_capability_evolution_feed_001"
TASK_FILE = ROOT / "runtime/tasks/discord/discord_capability_evolution_feed_001.yaml"
GRAPH = ROOT / "data/reports/capability_graph/capability_graph_runtime_latest.json"
SCORING = ROOT / "data/reports/infra/autonomous_priority_rebalancer_scoring_loop_latest.json"
OUT_DIR = ROOT / "data/reports/discord/capability_evolution_feed"
PAYLOAD = OUT_DIR / "latest_capability_evolution_event.json"
CARD = OUT_DIR / "latest_capability_evolution_card.md"


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
    if not TASK_FILE.is_file() or yaml is None:
        return {}
    return yaml.safe_load(TASK_FILE.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def main() -> int:
    if not GRAPH.is_file():
        print(f"DISCORD_CAPABILITY_EVOLUTION_FEED=FAIL missing={GRAPH}", file=sys.stderr)
        return 1

    task = load_task()
    if not task:
        print(f"TASK_FILE_NOT_FOUND={TASK_ID}")
        return 1

    graph = load_json(GRAPH)
    scoring = load_json(SCORING)
    commit_sha, commit_msg = git_head()

    unlock_chain = graph.get("recommended_unlock_chain") or []
    recommended_wip = scoring.get("recommended_wip") or []
    capability_unlocks = list(task.get("capability_unlocks") or [])
    following = list(task.get("unlocks_following_tasks") or [])
    why = str(task.get("why_this_matters") or "").strip() or "Capability metadata not yet populated."
    title = str(task.get("title") or TASK_ID)
    closeout = task.get("discord_closeout") or {}

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
        "runtime_context": {
            "capability_graph_runtime": str(GRAPH.relative_to(ROOT)),
            "unlock_chain": unlock_chain,
            "recommended_wip": recommended_wip[:5],
            "ready_for_downstream": graph.get("ready_for_downstream"),
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
    if unlock_chain:
        lines += ["", "## Runtime Unlock Chain", ""]
        for i, tid in enumerate(unlock_chain, 1):
            lines.append(f"{i}. `{tid}`")
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
        and payload.get("channel_key") == "master-task-log"
        and TASK_ID in unlock_chain
    )
    print(f"CAPABILITY_EVOLUTION_PAYLOAD={PAYLOAD}")
    print(f"CAPABILITY_EVOLUTION_CARD={CARD}")
    print(f"DISCORD_CAPABILITY_EVOLUTION_FEED={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
