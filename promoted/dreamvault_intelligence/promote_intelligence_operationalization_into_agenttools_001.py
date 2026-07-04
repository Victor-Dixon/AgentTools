#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


CANDIDATE_PATTERNS = [
    "runtime/scripts/*intelligence*.py",
    "runtime/scripts/*projectscanner*.py",
    "runtime/scripts/*discord*.py",
    "runtime/scripts/*trading*.py",
    "src/**/*intelligence*.py",
    "src/**/*admission*.py",
    "src/**/*planner*.py",
]

BLOCKED_PARTS = (
    "secrets",
    "reports",
    "__pycache__",
    ".pyc",
    "latest",
)


def classify(path: Path) -> dict:
    s = str(path)
    blocked = [b for b in BLOCKED_PARTS if b in s.lower()]
    reusable = path.suffix == ".py" and not blocked
    return {
        "source_path": s,
        "target_hint": f"agenttools/{path.name}" if reusable else None,
        "promote": reusable,
        "blocked_reasons": blocked,
    }


def main() -> int:
    found = []
    for pattern in CANDIDATE_PATTERNS:
        found.extend(Path(".").glob(pattern))

    rows = [classify(p) for p in sorted(set(found)) if p.is_file()]
    out_dir = Path("data/reports/promotions")
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "manifest_only",
        "promote_count": sum(1 for r in rows if r["promote"]),
        "blocked_count": sum(1 for r in rows if not r["promote"]),
        "candidates": rows,
    }

    json_path = out_dir / "agenttools_intelligence_operationalization_manifest.json"
    md_path = out_dir / "agenttools_intelligence_operationalization_manifest.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# AgentTools Intelligence Operationalization Promotion Manifest",
        "",
        f"generated_at: {payload['generated_at']}",
        f"promote_count: {payload['promote_count']}",
        f"blocked_count: {payload['blocked_count']}",
        "",
        "| Promote | Source | Target Hint | Blocked Reasons |",
        "|---:|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['promote']} | {r['source_path']} | {r['target_hint'] or ''} | {', '.join(r['blocked_reasons'])} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("AGENTTOOLS_PROMOTION_MANIFEST=PASS")
    print(f"PROMOTE_COUNT={payload['promote_count']}")
    print(f"BLOCKED_COUNT={payload['blocked_count']}")
    print(f"JSON={json_path}")
    print(f"MD={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
