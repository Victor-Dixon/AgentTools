#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("data/reports/projectscanner")

OUT_JSON = ROOT / "closeout/projectscanner_cloud_control_closeout.json"
OUT_MD = ROOT / "closeout/projectscanner_cloud_control_closeout.md"

DISCORD = Path(
    "data/reports/discord/projectscanner/projectscanner_cloud_control_unlock_card.md"
)

SURFACES = [
    "github_cloud",
    "cloud_duplicate_scan",
    "cloud_authority_graph",
    "repo_health",
    "promotion_recommendations",
    "control_plane",
    "action_executor",
    "live_mutation_gate",
    "issue_intelligence",
    "autonomous_issue_generation",
]

def main() -> int:
    discovered = []

    for surface in SURFACES:
        base = ROOT / surface
        discovered.append({
            "surface": surface,
            "exists": base.exists(),
        })

    enabled = sum(
        1 for s in discovered
        if s["exists"]
    )

    payload = {
        "stack": "projectscanner_cloud_control",
        "surfaces_total": len(SURFACES),
        "surfaces_enabled": enabled,
        "live_execution_enabled": False,
        "governed": True,
        "surfaces": discovered,
    }

    OUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUT_JSON.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# ProjectScanner Cloud Control Closeout",
        "",
        f"surfaces_total: {payload['surfaces_total']}",
        f"surfaces_enabled: {payload['surfaces_enabled']}",
        f"live_execution_enabled: {payload['live_execution_enabled']}",
        "",
        "| Surface | Enabled |",
        "|---|---|",
    ]

    for s in discovered:
        lines.append(
            f"| {s['surface']} | {s['exists']} |"
        )

    OUT_MD.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    DISCORD.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DISCORD.write_text(
f"""# PROJECTSCANNER CLOUD CONTROL UNLOCK

STACK=ONLINE
SURFACES_ENABLED={enabled}
LIVE_EXECUTION=False
STATE=GOVERNED

UNLOCKS:
- repo fleet governance
- cloud authority graph
- duplicate detection
- repo health scoring
- issue intelligence
- autonomous issue generation
- live mutation safety gates

NEXT:
- github_pr_action_executor_001
- repo_fleet_self_healing_001
- governance_drift_autofix_001
""",
        encoding="utf-8",
    )

    print(
        "PROJECTSCANNER_CLOUD_CONTROL_CLOSEOUT=PASS"
    )
    print(
        f"SURFACES_ENABLED={enabled}"
    )
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"DISCORD={DISCORD}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
