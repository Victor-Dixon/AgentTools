#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DISCOVERY_MD = Path("data/reports/trading/discord_architect_webhook_discovery_001.md")
OUT_MD = Path("data/reports/trading/discord_architect_candidate_dedupe_001.md")
OUT_JSON = Path("data/reports/trading/discord_architect_candidate_dedupe_001.json")


def parse_paths(text: str) -> list[Path]:
    paths: list[Path] = []
    for line in text.splitlines():
        match = re.search(r"path=`([^`]+)`", line)
        if match:
            paths.append(Path(match.group(1)))
    return sorted(set(paths), key=lambda p: str(p))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return "MISSING"
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(262144), b""):
                h.update(chunk)
    except Exception:
        return "READ_ERROR"
    return h.hexdigest()


def score(path: Path, text: str) -> int:
    hay = f"{path}\n{text[:12000]}".lower()
    score_value = 0
    weights = [
        ("send_latest_closeout_to_discord", 35),
        ("discord_webhook_url", 30),
        ("runtime/scripts", 18),
        ("requests.post", 14),
        ("urllib.request", 14),
        ("webhook", 12),
        ("discord", 10),
        ("def ", 6),
        ("#!/usr/bin/env bash", 6),
        ("runtime/tasks", -6),
        ("tests/", -8),
        ("data/reports", -15),
        ("archive/", -18),
        ("runtime/archive", -22),
        ("temp_run_scripts", -25),
        ("task_inventory_bundle", -30),
    ]
    for needle, weight in weights:
        if needle in hay:
            score_value += weight
    return score_value


def classify(path: Path, text: str, digest_count: int) -> tuple[str, list[str], int]:
    p = str(path)
    hay = f"{p}\n{text[:12000]}".lower()
    s = score(path, text)
    reasons: list[str] = []

    if digest_count > 1:
        reasons.append(f"duplicate_hash_group={digest_count}")

    if "task_inventory_bundle" in p or "data/reports/" in p:
        reasons.append("generated_report_or_bundle")
        return "TRASHABLE_REVIEW", reasons, s

    if "runtime/archive" in p or p.startswith("archive/") or "temp_run_scripts" in p:
        reasons.append("archive_or_temp_script")
        return "TRASHABLE_REVIEW", reasons, s

    if p.startswith("tests/") or "/test" in p.lower():
        reasons.append("test_reference")
        return "KEEP_REFERENCE", reasons, s

    if "runtime/tasks/" in p:
        reasons.append("task_record_reference")
        return "KEEP_REFERENCE", reasons, s

    if "send_latest_closeout_to_discord" in hay:
        reasons.append("existing_closeout_sender")
        return "KEEP_PRIMARY_CANDIDATE", reasons, s

    if "runtime/scripts/" in p and "discord_webhook_url" in hay and ("urllib.request" in hay or "requests.post" in hay or "curl" in hay):
        reasons.append("runtime_webhook_sender_candidate")
        return "KEEP_PRIMARY_CANDIDATE", reasons, s

    if "runtime/scripts/" in p and "discord" in hay and "webhook" in hay:
        reasons.append("runtime_discord_webhook_related")
        return "QUARANTINE_REVIEW", reasons, s

    if digest_count > 1:
        reasons.append("identical_content_duplicate")
        return "DUPLICATE_REVIEW", reasons, s

    if "discord" in hay and "webhook" in hay:
        reasons.append("discord_webhook_related_low_confidence")
        return "QUARANTINE_REVIEW", reasons, s

    reasons.append("low_signal")
    return "TRASHABLE_REVIEW", reasons, s


def main() -> int:
    discovery = DISCOVERY_MD.read_text(encoding="utf-8", errors="ignore")
    paths = parse_paths(discovery)

    raw: list[dict[str, Any]] = []
    digest_counts: Counter[str] = Counter()

    for path in paths:
        digest = sha256(path)
        if digest not in {"MISSING", "READ_ERROR"}:
            digest_counts[digest] += 1
        raw.append({
            "path": path,
            "text": read_text(path),
            "sha256": digest,
            "exists": path.exists(),
        })

    records: list[dict[str, Any]] = []
    for item in raw:
        path = item["path"]
        digest = item["sha256"]
        count = digest_counts.get(digest, 0)
        cls, reasons, s = classify(path, item["text"], count)
        records.append({
            "path": str(path),
            "class": cls,
            "score": s,
            "sha256": digest,
            "duplicate_count": count,
            "exists": item["exists"],
            "reasons": reasons,
        })

    records.sort(key=lambda r: (-int(r["score"]), r["class"], r["path"]))
    counts = Counter(r["class"] for r in records)

    duplicate_groups: dict[str, list[str]] = defaultdict(list)
    for r in records:
        digest = r["sha256"]
        if digest not in {"MISSING", "READ_ERROR"} and int(r["duplicate_count"]) > 1:
            duplicate_groups[digest].append(r["path"])

    output = {
        "status": "PASS",
        "policy": "No deletion performed. Review manifest before prune/quarantine.",
        "total_candidates": len(records),
        "counts": dict(counts),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_groups": duplicate_groups,
        "records": records,
    }
    OUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        "# Discord Architect Candidate Dedupe",
        "",
        "Status: `PASS`",
        f"Total candidates: `{len(records)}`",
        f"Duplicate hash groups: `{len(duplicate_groups)}`",
        "",
        "## Counts",
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"- {key}: `{value}`")

    lines += ["", "## Keep Primary Candidates"]
    primaries = [r for r in records if r["class"] == "KEEP_PRIMARY_CANDIDATE"]
    if primaries:
        for r in primaries:
            lines.append(f"- score={r['score']} path=`{r['path']}` reasons={', '.join(r['reasons'])}")
    else:
        lines.append("- None found.")

    lines += ["", "## Keep References"]
    for r in [x for x in records if x["class"] == "KEEP_REFERENCE"][:60]:
        lines.append(f"- score={r['score']} path=`{r['path']}` reasons={', '.join(r['reasons'])}")

    lines += ["", "## Duplicate Groups"]
    if duplicate_groups:
        for digest, group in list(duplicate_groups.items())[:50]:
            lines.append(f"- sha256={digest[:12]} count={len(group)}")
            for path in group[:20]:
                lines.append(f"  - `{path}`")
    else:
        lines.append("- No identical hash groups found.")

    lines += ["", "## Trashable Review"]
    for r in [x for x in records if x["class"] == "TRASHABLE_REVIEW"][:120]:
        lines.append(f"- score={r['score']} path=`{r['path']}` reasons={', '.join(r['reasons'])}")

    lines += ["", "## Quarantine Review"]
    for r in [x for x in records if x["class"] == "QUARANTINE_REVIEW"][:120]:
        lines.append(f"- score={r['score']} path=`{r['path']}` reasons={', '.join(r['reasons'])}")

    lines += [
        "",
        "## Policy",
        "- No deletion performed.",
        "- Primary should be selected from KEEP_PRIMARY_CANDIDATE only.",
        "- Generated reports and task bundles are trashable only after dependency check.",
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
