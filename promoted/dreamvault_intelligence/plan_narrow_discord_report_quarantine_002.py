#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


SRC = Path("data/reports/trading/discord_architect_cleanup_manifest_001.json")
OUT_MD = Path("data/reports/trading/generated_discord_report_quarantine_plan_002.md")
OUT_JSON = Path("data/reports/trading/generated_discord_report_quarantine_plan_002.json")
QUARANTINE_ROOT = Path("runtime/quarantine/generated_discord_reports_002")


BLOCKED_SUBSTRINGS = [
    "data/reports/trading/scheduled_snapshots/",
    "data/reports/trading/discord_architect_",
    "data/reports/trading/generated_discord_report_quarantine_plan_",
    "data/reports/ops/",
    "data/reports/discord/event_routing/",
    "runtime/",
    "dreamvault/",
    "src/",
    "tests/",
    "docs/",
    ".env",
    "secrets",
]


def is_narrow_safe(path: str, reasons: list[str]) -> bool:
    if not path.startswith("data/reports/"):
        return False

    if any(token in path for token in BLOCKED_SUBSTRINGS):
        return False

    # First safe class: generated task inventory bundles.
    if "data/reports/task_inventory_bundle/" in path:
        return True

    # Second safe class: old duplicated CPC/runtime packet artifacts only.
    if path.startswith("data/reports/cpc/") and "duplicate_hash_group" in ",".join(reasons):
        return True

    return False


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    candidates = data.get("safe_report_trash", [])

    selected = []
    rejected = []

    for item in candidates:
        src = item["path"]
        reasons = item.get("reasons", [])
        if is_narrow_safe(src, reasons):
            selected.append({
                "source": src,
                "target": str(QUARANTINE_ROOT / src),
                "reasons": reasons,
                "score": item.get("score"),
                "duplicate_count": item.get("duplicate_count"),
            })
        else:
            rejected.append({
                "source": src,
                "reasons": reasons,
                "blocked": True,
            })

    out = {
        "status": "PASS",
        "mode": "PLAN_ONLY_NO_MOVES",
        "source_manifest": str(SRC),
        "quarantine_root": str(QUARANTINE_ROOT),
        "input_safe_report_trash_count": len(candidates),
        "selected_count": len(selected),
        "rejected_count": len(rejected),
        "selected": selected,
        "rejected_sample": rejected[:200],
        "policy": "No files moved. Narrow plan only selects task inventory bundles and duplicated old CPC artifacts.",
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# Narrow Generated Discord Report Quarantine Plan",
        "",
        "Status: `PASS`",
        "Mode: `PLAN_ONLY_NO_MOVES`",
        f"Source manifest: `{SRC}`",
        f"Quarantine root: `{QUARANTINE_ROOT}`",
        "",
        "## Counts",
        f"- input_safe_report_trash_count: `{len(candidates)}`",
        f"- selected_count: `{len(selected)}`",
        f"- rejected_count: `{len(rejected)}`",
        "",
        "## Scope",
        "- Selected: `data/reports/task_inventory_bundle/` generated bundles.",
        "- Selected: old duplicated `data/reports/cpc/` artifacts only when duplicate-hash tagged.",
        "- Excluded: current trading scheduled snapshots.",
        "- Excluded: Discord Architect audit artifacts.",
        "- Excluded: ops/event-routing reports.",
        "- Excluded: runtime scripts, secrets, source, docs, tests.",
        "",
        "## Selected",
    ]

    for item in selected[:200]:
        lines.append(f"- `{item['source']}` → `{item['target']}`")

    if len(selected) > 200:
        lines.append(f"- ... {len(selected) - 200} more in JSON artifact")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("MODE=PLAN_ONLY_NO_MOVES")
    print("INPUT_SAFE_REPORT_TRASH_COUNT=" + str(len(candidates)))
    print("SELECTED_COUNT=" + str(len(selected)))
    print("REJECTED_COUNT=" + str(len(rejected)))
    print("PLAN_MD=" + str(OUT_MD))
    print("PLAN_JSON=" + str(OUT_JSON))
    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
