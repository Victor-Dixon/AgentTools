#!/usr/bin/env python3
"""Controlled batch apply: DreamVault intelligence scripts → AgentTools promoted/.

Never copies secret-named modules. Bulk full-tree apply remains deferred while
DreamVault git is dirty — this script only copies bounded batches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/reports/promotions/agenttools_intelligence_operationalization_manifest.json"
TARGET_DIR = Path(r"D:\agent-tools\promoted\dreamvault_intelligence")
SECRET_NAME_RE = re.compile(r"(secret|oauth|token|credential|password|api[_-]?key)", re.I)
BLOCK_NAMES = {"dream_secrets.py"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_blocked(name: str) -> bool:
    return name in BLOCK_NAMES or bool(SECRET_NAME_RE.search(name))


def plan(batch_size: int) -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    existing = {p.name: p for p in TARGET_DIR.glob("*.py")}
    missing: list[dict] = []
    in_sync: list[dict] = []
    drift: list[dict] = []
    blocked: list[dict] = []

    for row in data.get("candidates") or []:
        if not row.get("promote"):
            continue
        src = ROOT / str(row["source_path"]).replace("\\", "/")
        name = src.name
        if _is_blocked(name):
            blocked.append({"name": name, "reason": "secret_or_blocked_name"})
            continue
        if not src.is_file():
            continue
        tgt = TARGET_DIR / name
        entry = {"source": str(src), "target": str(tgt), "name": name}
        if name not in existing:
            missing.append(entry)
        else:
            if _sha256(src) == _sha256(tgt):
                in_sync.append(entry)
            else:
                drift.append(entry)

    sample = missing[:batch_size]
    return {
        "schema": "dreamos.agenttools_promotion_dry_run_apply.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "promote_count": int(data.get("promote_count") or 0),
        "blocked_count": len(blocked),
        "existing_promoted_py": sorted(existing),
        "missing_total": len(missing),
        "in_sync_total": len(in_sync),
        "drift_total": len(drift),
        "batch_size": batch_size,
        "plan": [
            {**e, "status": "MISSING"} for e in sample
        ]
        + [{**e, "status": "IN_SYNC"} for e in in_sync[:5]]
        + [{**e, "status": "DRIFT"} for e in drift[:5]],
        "batch_candidates": sample,
        "blocked": blocked,
    }


def apply_batch(batch: list[dict]) -> dict:
    copied: list[str] = []
    failed: list[dict] = []
    for entry in batch:
        src = Path(entry["source"])
        tgt = Path(entry["target"])
        try:
            if _is_blocked(src.name):
                failed.append({"name": src.name, "error": "blocked_secret_name"})
                continue
            shutil.copy2(src, tgt)
            copied.append(src.name)
        except OSError as exc:
            failed.append({"name": src.name, "error": str(exc)})

    promoted = sorted(p.name for p in TARGET_DIR.glob("*.py"))
    return {
        "schema": "dreamos.agenttools_promotion_controlled_apply.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "copied_count": len(copied),
        "copied": copied,
        "failed": failed,
        "promoted_py_count": len(promoted),
        "secret_named_scripts": [n for n in promoted if _is_blocked(n)],
        "bulk_remaining": max(
            0,
            int(json.loads(MANIFEST.read_text(encoding="utf-8")).get("promote_count") or 0)
            - len(promoted),
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--dry-run-only", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    # Refresh inventory manifest first
    from promote_intelligence_operationalization_into_agenttools_001 import main as refresh

    refresh()

    dry = plan(args.batch_size)
    dry_path = ROOT / "data/reports/promotions/agenttools_intelligence_dry_run_apply_latest.json"
    dry_path.write_text(json.dumps(dry, indent=2) + "\n", encoding="utf-8")
    print(f"DRY_RUN missing_total={dry['missing_total']} batch={len(dry['batch_candidates'])}")
    print(f"DRY_RUN_JSON={dry_path}")

    if args.dry_run_only or not args.apply:
        print("MODE=dry_run")
        return 0

    result = apply_batch(dry["batch_candidates"])
    apply_path = ROOT / "data/reports/promotions/agenttools_intelligence_controlled_apply_latest.json"
    apply_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"APPLY copied={result['copied_count']} remaining≈{result['bulk_remaining']}")
    print(f"APPLY_JSON={apply_path}")
    print("CONTROLLED_APPLY=PASS" if not result["failed"] else "CONTROLLED_APPLY=PARTIAL")
    return 0 if not result["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
