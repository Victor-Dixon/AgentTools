#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


CLASSIFIER = Path("runtime/scripts/classify_runtime_residue_001.py")
OUT_DIR = Path("data/reports/runtime_residue")

AUTO_DELETE_BUCKETS = {
    "ephemeral_cache",
}

CONDITIONAL_DELETE_BUCKETS = {
    "temporary_commit_helper",
    "temporary_fix_helper",
    "temporary_seed_helper",
}

NEVER_DELETE_BUCKETS = {
    "secret_or_sensitive",
    "durable_script_candidate",
    "durable_task_candidate",
    "durable_test_candidate",
    "durable_doc_candidate",
    "manual_review",
    "generated_report",
    "generated_latest_pointer",
}


def load_classifier():
    spec = importlib.util.spec_from_file_location("runtime_residue_classifier", CLASSIFIER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def is_committed_or_absent(path: str) -> bool:
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode != 0


def decide_action(item: dict, allow_helpers: bool) -> dict:
    bucket = item["bucket"]
    path = item["path"]

    if bucket in AUTO_DELETE_BUCKETS:
        return {**item, "action": "delete", "action_reason": "auto-delete ephemeral cache"}

    if bucket in CONDITIONAL_DELETE_BUCKETS:
        if allow_helpers:
            return {**item, "action": "delete", "action_reason": "temporary helper cleanup allowed"}
        return {**item, "action": "keep", "action_reason": "temporary helper requires --allow-helper-delete"}

    if bucket in NEVER_DELETE_BUCKETS:
        return {**item, "action": "keep", "action_reason": "protected bucket"}

    return {**item, "action": "keep", "action_reason": "unknown bucket protected"}


def build_plan(allow_helpers: bool) -> dict:
    classifier = load_classifier()
    manifest = classifier.build_manifest(classifier.git_status_lines())
    items = [decide_action(i, allow_helpers=allow_helpers) for i in manifest["items"]]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run_default",
        "allow_helpers": allow_helpers,
        "delete_count": sum(1 for i in items if i["action"] == "delete"),
        "keep_count": sum(1 for i in items if i["action"] == "keep"),
        "items": items,
    }


def apply_plan(plan: dict) -> list[str]:
    deleted = []
    for item in plan["items"]:
        if item["action"] != "delete":
            continue
        path = Path(item["path"])
        if not path.exists():
            continue
        if path.is_dir():
            continue
        path.unlink()
        deleted.append(str(path))
    return deleted


def render_md(plan: dict) -> str:
    lines = [
        "# Runtime Residue Cleanup Plan",
        "",
        f"generated_at: {plan['generated_at']}",
        f"allow_helpers: {plan['allow_helpers']}",
        f"delete_count: {plan['delete_count']}",
        f"keep_count: {plan['keep_count']}",
        "",
        "| Action | Bucket | Path | Reason |",
        "|---|---|---|---|",
    ]
    for i in plan["items"]:
        lines.append(f"| {i['action']} | {i['bucket']} | {i['path']} | {i['action_reason']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--allow-helper-delete", action="store_true")
    args = parser.parse_args()

    plan = build_plan(allow_helpers=args.allow_helper_delete)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "latest_runtime_residue_cleanup_plan.json"
    md_path = OUT_DIR / "latest_runtime_residue_cleanup_plan.md"

    if args.apply:
        deleted = apply_plan(plan)
        plan["applied"] = True
        plan["deleted"] = deleted
    else:
        plan["applied"] = False
        plan["deleted"] = []

    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    md_path.write_text(render_md(plan), encoding="utf-8")

    print("CLEANUP_RUNTIME_RESIDUE_APPLY=PASS")
    print(f"APPLIED={plan['applied']}")
    print(f"DELETE_COUNT={plan['delete_count']}")
    print(f"KEEP_COUNT={plan['keep_count']}")
    print(f"JSON={json_path}")
    print(f"MD={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
