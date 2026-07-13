#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HEALTH = Path("data/reports/projectscanner/repo_health/latest.json")
AUTHORITY = Path("data/reports/projectscanner/cloud_authority_graph/latest.json")
OUT_JSON = Path("data/reports/projectscanner/promotion_recommendations/latest.json")
OUT_MD = Path("data/reports/projectscanner/promotion_recommendations/latest.md")

def classify(score: int, duplicate_pressure: int, authority: str) -> tuple[str, list[str]]:
    reasons = []
    if duplicate_pressure:
        reasons.append("duplicate_pressure")
    if authority == "unknown":
        reasons.append("unknown_authority")
    if score >= 75 and duplicate_pressure == 0:
        return "promote_or_showcase", ["high_health", *reasons]
    if score >= 55:
        return "keep_and_harden", ["moderate_health", *reasons]
    if score >= 35:
        return "review_for_merge_or_archive", ["low_health", *reasons]
    return "archive_candidate", ["very_low_health", *reasons]

def main() -> int:
    health = json.loads(HEALTH.read_text(encoding="utf-8"))
    authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))

    auth_lookup = {}
    for repo in authority.get("repos", []):
        auth = repo.get("authority") or []
        auth_lookup[repo["repo"]] = auth[0][0] if auth else "unknown"

    rows = []
    for repo in health.get("scored_repos", []):
        auth = auth_lookup.get(repo["repo"], "unknown")
        action, reasons = classify(repo["score"], repo.get("duplicate_pressure", 0), auth)
        rows.append({
            "repo": repo["repo"],
            "score": repo["score"],
            "authority": auth,
            "duplicate_pressure": repo.get("duplicate_pressure", 0),
            "recommendation": action,
            "reasons": reasons,
        })

    payload = {
        "repo_count": len(rows),
        "recommendations": rows,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# ProjectScanner Promotion Recommendations",
        "",
        f"repo_count: {len(rows)}",
        "",
        "| Repo | Score | Authority | Duplicate Pressure | Recommendation | Reasons |",
        "|---|---:|---|---:|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['repo']} | {r['score']} | {r['authority']} | "
            f"{r['duplicate_pressure']} | {r['recommendation']} | {', '.join(r['reasons'])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PROJECTSCANNER_PROMOTION_RECOMMENDATION_ENGINE=PASS")
    print(f"REPOS={len(rows)}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
