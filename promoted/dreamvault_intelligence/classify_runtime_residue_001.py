#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


OUT_DIR = Path("data/reports/runtime_residue")


def git_status_lines() -> list[str]:
    out = subprocess.check_output(["git", "status", "--short"], text=True)
    return [x.rstrip() for x in out.splitlines() if x.strip()]


def extract_path(line: str) -> str:
    return line[3:].strip()


def classify_path(path: str) -> tuple[str, str]:
    p = path.lower()

    if "runtime/secrets" in p or "secret" in p or ".env" in p:
        return "secret_or_sensitive", "contains secret/env naming"

    if "__pycache__" in p or p.endswith(".pyc"):
        return "ephemeral_cache", "python cache"

    if "/latest/" in p or "data/reports/cpc/latest" in p:
        return "generated_latest_pointer", "regenerated latest pointer"

    if p.startswith("data/reports/") and (
        "latest_" in p or "cpc_" in p or p.endswith(".json") or p.endswith(".md")
    ):
        return "generated_report", "report artifact"

    if "/commit_" in p or p.startswith("runtime/scripts/commit_"):
        return "temporary_commit_helper", "commit helper script"

    if "/fix_" in p or p.startswith("runtime/scripts/fix_") or "/patch_" in p:
        return "temporary_fix_helper", "one-off patch/fix script"

    if p.startswith("runtime/scripts/seed_"):
        return "temporary_seed_helper", "one-off seed script"

    if p.startswith("runtime/scripts/") and p.endswith(".py"):
        return "durable_script_candidate", "python runtime script"

    if p.startswith("runtime/tasks/") and p.endswith((".yaml", ".yml")):
        return "durable_task_candidate", "task artifact"

    if p.startswith("tests/") and p.endswith(".py"):
        return "durable_test_candidate", "test artifact"

    if p.startswith("docs/"):
        return "durable_doc_candidate", "documentation"

    if p.startswith(".gitignore") or p.endswith(".gitignore"):
        return "manual_review", "gitignore change"

    return "manual_review", "no classifier rule matched"


def build_manifest(lines: list[str]) -> dict:
    items = []
    for line in lines:
        path = extract_path(line)
        bucket, reason = classify_path(path)
        items.append({
            "status": line[:2].strip() or "modified",
            "path": path,
            "bucket": bucket,
            "reason": reason,
        })

    counts = Counter(i["bucket"] for i in items)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "item_count": len(items),
        "bucket_counts": dict(sorted(counts.items())),
        "items": items,
    }


def render_md(payload: dict) -> str:
    lines = [
        "# Runtime Residue Manifest",
        "",
        f"generated_at: {payload['generated_at']}",
        f"item_count: {payload['item_count']}",
        "",
        "## Bucket Counts",
        "",
        "| Bucket | Count |",
        "|---|---:|",
    ]
    for k, v in payload["bucket_counts"].items():
        lines.append(f"| {k} | {v} |")

    lines.extend(["", "## Items", "", "| Bucket | Status | Path | Reason |", "|---|---:|---|---|"])
    for i in payload["items"]:
        lines.append(f"| {i['bucket']} | {i['status']} | {i['path']} | {i['reason']} |")

    lines.extend([
        "",
        "## Policy",
        "",
        "- Auto-delete only ephemeral_cache after review.",
        "- Auto-delete temporary_* helpers only when their durable output is committed.",
        "- Never auto-delete secret_or_sensitive; quarantine or inspect manually.",
        "- Durable candidates should be promoted or committed, not cleaned.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_manifest(git_status_lines())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "latest_runtime_residue_manifest.json"
    md_path = OUT_DIR / "latest_runtime_residue_manifest.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_md(payload), encoding="utf-8")

    print("RUNTIME_RESIDUE_CLASSIFIER=PASS")
    print(f"ITEMS={payload['item_count']}")
    print(f"BUCKETS={payload['bucket_counts']}")
    print(f"JSON={json_path}")
    print(f"MD={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
