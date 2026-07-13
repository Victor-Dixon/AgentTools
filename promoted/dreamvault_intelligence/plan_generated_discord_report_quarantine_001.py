#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


SRC = Path("data/reports/trading/discord_architect_cleanup_manifest_001.json")
OUT_MD = Path("data/reports/trading/generated_discord_report_quarantine_plan_001.md")
OUT_JSON = Path("data/reports/trading/generated_discord_report_quarantine_plan_001.json")

QUARANTINE_ROOT = Path("runtime/quarantine/generated_discord_reports_001")


def is_safe_report_path(path: str) -> bool:
    if not path.startswith("data/reports/"):
        return False
    blocked = [
        "runtime/scripts/",
        "runtime/secrets/",
        "runtime/tasks/",
        "dreamvault/",
        "src/",
        ".env",
    ]
    return not any(token in path for token in blocked)


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    candidates = data.get("safe_report_trash", [])

    selected = []
    rejected = []

    for item in candidates:
        src = item["path"]
        if is_safe_report_path(src):
            selected.append({
                "source": src,
                "target": str(QUARANTINE_ROOT / src),
                "reasons": item.get("reasons", []),
                "score": item.get("score"),
                "duplicate_count": item.get("duplicate_count"),
            })
        else:
            rejected.append(item)

    out = {
        "status": "PASS",
        "mode": "PLAN_ONLY_NO_MOVES",
        "source_manifest": str(SRC),
        "quarantine_root": str(QUARANTINE_ROOT),
        "safe_report_trash_count": len(candidates),
        "selected_count": len(selected),
        "rejected_count": len(rejected),
        "selected": selected,
        "rejected": rejected,
        "policy": "No files moved. No runtime scripts, secrets, source code, or active providers selected.",
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# Generated Discord Report Quarantine Plan",
        "",
        "Status: `PASS`",
        "Mode: `PLAN_ONLY_NO_MOVES`",
        f"Source manifest: `{SRC}`",
        f"Quarantine root: `{QUARANTINE_ROOT}`",
        "",
        "## Counts",
        f"- safe_report_trash_count: `{len(candidates)}`",
        f"- selected_count: `{len(selected)}`",
        f"- rejected_count: `{len(rejected)}`",
        "",
        "## Policy",
        "- No files moved.",
        "- Only `data/reports/` candidates selected.",
        "- Runtime scripts, secrets, source code, and active providers excluded.",
        "",
        "## Selected Sample",
    ]

    for item in selected[:120]:
        lines.append(f"- `{item['source']}` → `{item['target']}`")

    if len(selected) > 120:
        lines.append(f"- ... {len(selected) - 120} more in JSON artifact")

    lines += ["", "## Rejected Sample"]
    for item in rejected[:80]:
        lines.append(f"- `{item['path']}` reasons={', '.join(item.get('reasons', []))}")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("MODE=PLAN_ONLY_NO_MOVES")
    print("SAFE_REPORT_TRASH_COUNT=" + str(len(candidates)))
    print("SELECTED_COUNT=" + str(len(selected)))
    print("REJECTED_COUNT=" + str(len(rejected)))
    print("PLAN_MD=" + str(OUT_MD))
    print("PLAN_JSON=" + str(OUT_JSON))
    print("STATUS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
