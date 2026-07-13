#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

TREE = Path(
    "data/reports/projectscanner/github_tree/latest_tree_inventory.json"
)

HEALTH = Path(
    "data/reports/projectscanner/repo_health/latest.json"
)

OUT_JSON = Path(
    "data/reports/projectscanner/issue_intelligence/latest.json"
)

OUT_MD = Path(
    "data/reports/projectscanner/issue_intelligence/latest.md"
)

KEYWORDS = [
    "TODO",
    "FIXME",
    "HACK",
]

def load(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8")
    )

def detect_issues(repo: dict) -> list[dict]:
    issues = []

    raw_files = repo.get("files", [])
    files = [
        f.get("path", "") if isinstance(f, dict) else str(f)
        for f in raw_files
    ]
    repo_name = repo.get("repo")

    readme_present = any(
        "README" in f
        for f in files
    )

    tests_present = any(
        "test" in f.lower()
        for f in files
    )

    runtime_density = sum(
        1 for f in files
        if "runtime/" in f
    )

    if not readme_present:
        issues.append({
            "repo": repo_name,
            "severity": "medium",
            "type": "missing_readme",
        })

    if not tests_present:
        issues.append({
            "repo": repo_name,
            "severity": "high",
            "type": "missing_tests",
        })

    if runtime_density > 40:
        issues.append({
            "repo": repo_name,
            "severity": "medium",
            "type": "runtime_complexity_pressure",
        })

    duplicate_names = {}

    for f in files:
        name = Path(f).name

        duplicate_names.setdefault(
            name,
            0,
        )

        duplicate_names[name] += 1

    duplicate_hits = [
        k for k, v in duplicate_names.items()
        if v > 1
    ]

    if duplicate_hits:
        issues.append({
            "repo": repo_name,
            "severity": "medium",
            "type": "duplicate_logic_risk",
            "count": len(duplicate_hits),
        })

    return issues

def main() -> int:
    tree = load(TREE)
    health = load(HEALTH)

    repos = tree.get("repos", [])

    findings = []

    for repo in repos:
        findings.extend(
            detect_issues(repo)
        )

    severity_order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    findings.sort(
        key=lambda x: severity_order.get(
            x["severity"],
            0,
        ),
        reverse=True,
    )

    payload = {
        "repos": len(repos),
        "issues_detected": len(findings),
        "top_repo": health.get("top_repo"),
        "findings": findings,
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
        "# ProjectScanner Issue Intelligence",
        "",
        f"repos: {payload['repos']}",
        f"issues_detected: {payload['issues_detected']}",
        f"top_repo: {payload['top_repo']}",
        "",
        "| Repo | Severity | Issue Type |",
        "|---|---|---|",
    ]

    for finding in findings:
        lines.append(
            f"| {finding['repo']} "
            f"| {finding['severity']} "
            f"| {finding['type']} |"
        )

    OUT_MD.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(
        "PROJECTSCANNER_ISSUE_INTELLIGENCE=PASS"
    )
    print(
        f"REPOS={payload['repos']}"
    )
    print(
        f"ISSUES={payload['issues_detected']}"
    )
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
