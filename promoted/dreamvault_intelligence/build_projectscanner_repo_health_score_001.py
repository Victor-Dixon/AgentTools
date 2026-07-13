#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

INV = Path("data/reports/projectscanner/github_cloud/latest_inventory.json")
TREE = Path("data/reports/projectscanner/github_tree/latest_tree_inventory.json")
DUP = Path("data/reports/projectscanner/cloud_duplicate_scan/latest_v2.json")

OUT_JSON = Path("data/reports/projectscanner/repo_health/latest.json")
OUT_MD = Path("data/reports/projectscanner/repo_health/latest.md")

WEIGHTS = {
    "has_files": 20,
    "has_python": 15,
    "has_javascript": 10,
    "has_tests": 20,
    "has_docs": 15,
    "recent_update": 10,
    "not_archived": 10,
    "duplicate_penalty": -15,
}

def parse_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None

def recent(value: str | None, days: int = 180) -> bool:
    dt = parse_dt(value)
    if not dt:
        return False
    return (datetime.now(timezone.utc) - dt).days <= days

def repo_duplicate_pressure(repo: str, dup: dict) -> int:
    count = 0
    for group in dup.get("duplicate_files", []):
        repos = {o.get("repo") for o in group.get("occurrences", [])}
        if repo in repos:
            count += 1
    return count

def score_repo(repo: dict, tree: dict, dup: dict) -> dict:
    full = repo["full_name"]
    files = tree.get(full, [])
    paths = [f.get("path", "").lower() for f in files]

    reasons = []
    score = 0

    if files:
        score += WEIGHTS["has_files"]
        reasons.append("has_files")

    if any(p.endswith(".py") for p in paths):
        score += WEIGHTS["has_python"]
        reasons.append("has_python")

    if any(p.endswith((".js", ".ts", ".jsx", ".tsx")) for p in paths):
        score += WEIGHTS["has_javascript"]
        reasons.append("has_javascript")

    if any("test" in p or "tests/" in p for p in paths):
        score += WEIGHTS["has_tests"]
        reasons.append("has_tests")

    if any(p.endswith("readme.md") or "/docs/" in p or p.startswith("docs/") for p in paths):
        score += WEIGHTS["has_docs"]
        reasons.append("has_docs")

    if recent(repo.get("updated_at")):
        score += WEIGHTS["recent_update"]
        reasons.append("recent_update")

    if not repo.get("archived"):
        score += WEIGHTS["not_archived"]
        reasons.append("not_archived")

    duplicate_pressure = repo_duplicate_pressure(full, dup)
    if duplicate_pressure:
        score += WEIGHTS["duplicate_penalty"] * duplicate_pressure
        reasons.append(f"duplicate_pressure={duplicate_pressure}")

    return {
        "repo": full,
        "score": max(score, 0),
        "reasons": reasons,
        "file_count": len(files),
        "language": repo.get("language"),
        "updated_at": repo.get("updated_at"),
        "archived": repo.get("archived"),
        "duplicate_pressure": duplicate_pressure,
    }

def main() -> int:
    inv = json.loads(INV.read_text(encoding="utf-8"))
    tree_payload = json.loads(TREE.read_text(encoding="utf-8"))
    dup = json.loads(DUP.read_text(encoding="utf-8"))

    tree_lookup = {
        r.get("repo"): r.get("files", [])
        for r in tree_payload.get("repos", [])
    }

    rows = [
        score_repo(repo, tree_lookup, dup)
        for repo in inv.get("repos", [])
    ]

    rows = sorted(rows, key=lambda r: (-r["score"], r["repo"]))

    payload = {
        "repo_count": len(rows),
        "scored_repos": rows,
        "top_repo": rows[0]["repo"] if rows else None,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# ProjectScanner Repo Health Score",
        "",
        f"repo_count: {payload['repo_count']}",
        f"top_repo: {payload['top_repo']}",
        "",
        "| Score | Repo | Files | Language | Duplicate Pressure | Reasons |",
        "|---:|---|---:|---|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['score']} | {r['repo']} | {r['file_count']} | "
            f"{r['language']} | {r['duplicate_pressure']} | {', '.join(r['reasons'])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PROJECTSCANNER_REPO_HEALTH_SCORE=PASS")
    print(f"REPOS={payload['repo_count']}")
    print(f"TOP_REPO={payload['top_repo']}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
