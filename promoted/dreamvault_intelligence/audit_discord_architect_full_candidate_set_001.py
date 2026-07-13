#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(".")
OUT_MD = Path("data/reports/trading/discord_architect_full_candidate_audit_001.md")
OUT_JSON = Path("data/reports/trading/discord_architect_full_candidate_audit_001.json")

TEXT_EXTS = {
    ".py", ".sh", ".yaml", ".yml", ".md", ".txt", ".json", ".env", ".toml", ".ini"
}

SKIP_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
}


def is_text_candidate(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    if not path.is_file():
        return False
    if path.suffix.lower() in TEXT_EXTS:
        return True
    return "discord" in path.name.lower() or "webhook" in path.name.lower()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(262144), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "READ_ERROR"


def discover() -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if not is_text_candidate(path):
            continue
        p = str(path)
        name = path.name.lower()
        text = read_text(path)[:20000].lower()
        hay = f"{p.lower()}\n{name}\n{text}"

        if "discord_webhook_url" in hay:
            paths.append(path)
        elif "discord" in hay and "webhook" in hay:
            paths.append(path)
        elif "send_discord" in hay:
            paths.append(path)
        elif "closeout" in hay and "discord" in hay:
            paths.append(path)

    return sorted(set(paths), key=lambda p: str(p))


def score(path: Path, text: str) -> int:
    hay = f"{path}\n{text[:16000]}".lower()
    value = 0
    weights = [
        ("send_latest_closeout_to_discord", 45),
        ("send_discord_paper_trade_payload", 40),
        ("discord_webhook_url", 35),
        ("runtime/scripts/", 24),
        ("requests.post", 18),
        ("urllib.request", 18),
        ("webhook", 14),
        ("discord", 12),
        ("def ", 8),
        ("#!/usr/bin/env bash", 8),
        ("runtime/tasks/", -8),
        ("tests/", -10),
        ("data/reports/", -18),
        ("archive/", -22),
        ("runtime/archive/", -25),
        ("temp_run_scripts", -28),
        ("task_inventory_bundle", -35),
        (".cache", -40),
    ]
    for needle, weight in weights:
        if needle in hay:
            value += weight
    return value


def classify(path: Path, text: str, duplicate_count: int) -> tuple[str, list[str], int]:
    p = str(path)
    hay = f"{p}\n{text[:16000]}".lower()
    s = score(path, text)
    reasons: list[str] = []

    if duplicate_count > 1:
        reasons.append(f"duplicate_hash_group={duplicate_count}")

    if p.startswith("tests/") or "/tests/" in p or "test_" in path.name:
        reasons.append("test_reference")
        return "KEEP_REFERENCE", reasons, s

    if "runtime/tasks/" in p:
        reasons.append("task_record_reference")
        return "KEEP_REFERENCE", reasons, s

    if "data/reports/" in p or "task_inventory_bundle" in p:
        reasons.append("generated_report_or_bundle")
        return "TRASHABLE_REVIEW", reasons, s

    if ".cache" in p or "runtime/archive/" in p or p.startswith("archive/") or "temp_run_scripts" in p:
        reasons.append("cache_archive_or_temp")
        return "TRASHABLE_REVIEW", reasons, s

    if "runtime/generated_scripts/" in p:
        reasons.append("generated_script_review")
        return "QUARANTINE_REVIEW", reasons, s

    if "runtime/scripts/" in p and "send_discord_paper_trade_payload" in p:
        reasons.append("current_best_primary_provider")
        return "KEEP_PRIMARY_CANDIDATE", reasons, s

    if "runtime/scripts/" in p and "send_latest_closeout_to_discord" in hay:
        reasons.append("existing_closeout_sender")
        return "KEEP_PRIMARY_CANDIDATE", reasons, s

    if "runtime/scripts/" in p and "discord_webhook_url" in hay and (
        "requests.post" in hay or "urllib.request" in hay or "curl" in hay
    ):
        reasons.append("runtime_webhook_sender_candidate")
        return "QUARANTINE_REVIEW", reasons, s

    if duplicate_count > 1:
        reasons.append("identical_content_duplicate")
        return "DUPLICATE_REVIEW", reasons, s

    if "discord" in hay and "webhook" in hay:
        reasons.append("discord_webhook_related_low_confidence")
        return "QUARANTINE_REVIEW", reasons, s

    reasons.append("low_signal")
    return "TRASHABLE_REVIEW", reasons, s


def main() -> int:
    paths = discover()

    digests: dict[str, str] = {}
    texts: dict[str, str] = {}
    digest_counts: Counter[str] = Counter()

    for path in paths:
        digest = sha256(path)
        text = read_text(path)
        digests[str(path)] = digest
        texts[str(path)] = text
        if digest not in {"READ_ERROR"}:
            digest_counts[digest] += 1

    records: list[dict[str, Any]] = []
    for path in paths:
        key = str(path)
        digest = digests[key]
        duplicate_count = digest_counts[digest]
        cls, reasons, s = classify(path, texts[key], duplicate_count)
        records.append({
            "path": key,
            "class": cls,
            "score": s,
            "sha256": digest,
            "duplicate_count": duplicate_count,
            "reasons": reasons,
        })

    records.sort(key=lambda r: (-int(r["score"]), r["class"], r["path"]))
    counts = Counter(r["class"] for r in records)

    duplicate_groups: dict[str, list[str]] = defaultdict(list)
    for record in records:
        if int(record["duplicate_count"]) > 1:
            duplicate_groups[record["sha256"]].append(record["path"])

    output = {
        "status": "PASS",
        "policy": "No deletion performed. Review before prune/quarantine.",
        "total_candidates": len(records),
        "counts": dict(counts),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_groups": duplicate_groups,
        "records": records,
    }
    OUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        "# Full Discord Architect Candidate Audit",
        "",
        "Status: `PASS`",
        f"Total candidates: `{len(records)}`",
        f"Duplicate hash groups: `{len(duplicate_groups)}`",
        "",
        "## Counts",
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"- {key}: `{value}`")

    for title, cls, limit in [
        ("Keep Primary Candidates", "KEEP_PRIMARY_CANDIDATE", 30),
        ("Keep References", "KEEP_REFERENCE", 60),
        ("Quarantine Review", "QUARANTINE_REVIEW", 120),
        ("Duplicate Review", "DUPLICATE_REVIEW", 120),
        ("Trashable Review", "TRASHABLE_REVIEW", 200),
    ]:
        lines += ["", f"## {title}"]
        subset = [r for r in records if r["class"] == cls]
        if not subset:
            lines.append("- None.")
        else:
            for r in subset[:limit]:
                lines.append(
                    f"- score={r['score']} dup={r['duplicate_count']} "
                    f"path=`{r['path']}` reasons={', '.join(r['reasons'])}"
                )

    lines += ["", "## Duplicate Groups"]
    if duplicate_groups:
        for digest, group in list(duplicate_groups.items())[:80]:
            lines.append(f"- sha256={digest[:12]} count={len(group)}")
            for path in group[:30]:
                lines.append(f"  - `{path}`")
    else:
        lines.append("- None.")

    lines += [
        "",
        "## Policy",
        "- No deletion performed.",
        "- Promote one runtime/scripts provider only.",
        "- Delete/archive generated reports only after dependency check.",
        "- Never commit webhook values.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"TOTAL_CANDIDATES={len(records)}")
    print(f"DUPLICATE_GROUPS={len(duplicate_groups)}")
    for key, value in sorted(counts.items()):
        print(f"CLASS_{key}={value}")
    print(f"REPORT_MD={OUT_MD}")
    print(f"REPORT_JSON={OUT_JSON}")
    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
