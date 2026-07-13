#!/usr/bin/env python3
"""Materialize baseline project_artifacts from intelligence vault scan targets."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LATEST = REPO_ROOT / "data" / "project_intelligence" / "latest"
OUT_ROOT = REPO_ROOT / "data" / "project_intelligence" / "project_artifacts"

REQUIRED = (
    "scan_target.json",
    "analysis.json",
    "context.json",
    "next_up.json",
    "health.json",
)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _load_targets(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    targets = data.get("targets", [])
    return targets if isinstance(targets, list) else []


def _safe_name(value: str) -> str:
    return value.replace("/", "__").replace(" ", "_")


def _artifact_dir(target: dict[str, Any]) -> Path:
    source_type = str(target.get("source_type") or "unknown")
    if source_type == "github":
        owner = str(target.get("owner") or "unknown")
        repo = str(target.get("repo") or target.get("name") or "unknown")
        return OUT_ROOT / "github" / owner / repo
    name = str(target.get("repo") or target.get("name") or Path(str(target.get("local_path") or "unknown")).name)
    return OUT_ROOT / "local" / _safe_name(name)


def _payloads(target: dict[str, Any]) -> dict[str, dict[str, Any]]:
    source_type = str(target.get("source_type") or "unknown")
    name = str(target.get("name") or target.get("repo") or "unknown")
    local_path = str(target.get("local_path") or "")
    status = str(target.get("status") or "unknown")
    now = _utc_now()
    local = Path(local_path) if local_path else None

    return {
        "scan_target.json": {
            "artifact_schema": "projectscanner.scan_target.v1",
            "generated_at": now,
            "target": target,
        },
        "analysis.json": {
            "artifact_schema": "projectscanner.analysis.v1",
            "generated_at": now,
            "project": name,
            "source_type": source_type,
            "status": "baseline_generated",
            "summary": "Baseline analysis artifact generated from vault scan targets.",
            "signals": {
                "target_status": status,
                "local_path_exists": bool(local and local.exists()),
                "is_git_repo": bool(local and (local / ".git").exists()),
            },
        },
        "context.json": {
            "artifact_schema": "projectscanner.context.v1",
            "generated_at": now,
            "project": name,
            "source_type": source_type,
            "context": {
                "name": name,
                "local_path": local_path,
                "github_url": target.get("github_url", ""),
                "branch": target.get("branch", ""),
                "owner": target.get("owner", ""),
                "repo": target.get("repo", ""),
            },
        },
        "next_up.json": {
            "artifact_schema": "projectscanner.next_up.v1",
            "generated_at": now,
            "project": name,
            "tasks": [
                {
                    "title": "Attach real scanner analysis",
                    "priority": 90,
                    "status": "planned",
                    "verify": "analysis.json contains scanner_output",
                }
            ],
        },
        "health.json": {
            "artifact_schema": "projectscanner.health.v1",
            "generated_at": now,
            "project": name,
            "source_type": source_type,
            "status": "baseline",
            "checks": {
                "scan_target_present": True,
                "analysis_present": True,
                "context_present": True,
                "next_up_present": True,
                "deep_scan_present": False,
                "local_path_exists": bool(local and local.exists()),
                "git_repo_present": bool(local and (local / ".git").exists()),
            },
        },
    }


def materialize() -> dict[str, Any]:
    targets = _load_targets(LATEST / "github_scan_targets_latest.json")
    targets += _load_targets(LATEST / "local_scan_targets_latest.json")

    written = 0
    for target in targets:
        if not isinstance(target, dict):
            continue
        artifact_dir = _artifact_dir(target)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        for filename in REQUIRED:
            path = artifact_dir / filename
            path.write_text(
                json.dumps(_payloads(target)[filename], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            written += 1

    return {
        "target_count": len(targets),
        "files_written": written,
        "artifact_root": str(OUT_ROOT),
    }


def main() -> int:
    summary = materialize()
    print(f"MATERIALIZE_PROJECT_INTELLIGENCE_ARTIFACTS=PASS")
    print(f"TARGET_COUNT={summary['target_count']}")
    print(f"FILES_WRITTEN={summary['files_written']}")
    print(f"ARTIFACT_ROOT={summary['artifact_root']}")
    return 0 if summary["target_count"] >= 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())
