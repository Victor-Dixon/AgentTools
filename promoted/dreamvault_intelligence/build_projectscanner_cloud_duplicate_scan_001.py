#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

INVENTORY = Path(
    "data/reports/projectscanner/github_cloud/latest_inventory.json"
)

OUT_JSON = Path(
    "data/reports/projectscanner/cloud_duplicate_scan/latest.json"
)

OUT_MD = Path(
    "data/reports/projectscanner/cloud_duplicate_scan/latest.md"
)

TOKEN_SPLIT = ["-", "_", "."]


def tokenize(name: str) -> set[str]:
    tokens = {name.lower()}
    current = [name.lower()]

    for splitter in TOKEN_SPLIT:
        nxt = []
        for item in current:
            nxt.extend(item.split(splitter))
        current = nxt

    tokens.update(
        t for t in current
        if len(t) >= 3
    )

    return tokens


def similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0

    return len(a & b) / len(a | b)


def main() -> int:
    payload = json.loads(
        INVENTORY.read_text(encoding="utf-8")
    )

    repos = payload.get("repos", [])

    rows = []

    for repo in repos:
        rows.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "tokens": tokenize(repo["name"]),
            "language": repo.get("language"),
            "archived": repo.get("archived"),
        })

    groups = []

    for left, right in combinations(rows, 2):
        score = similarity(
            left["tokens"],
            right["tokens"],
        )

        if score >= 0.34:
            groups.append({
                "score": round(score, 3),
                "left": left["full_name"],
                "right": right["full_name"],
                "language_match": (
                    left["language"] == right["language"]
                ),
            })

    groups = sorted(
        groups,
        key=lambda x: x["score"],
        reverse=True,
    )

    result = {
        "repo_count": len(rows),
        "duplicate_groups": len(groups),
        "groups": groups,
    }

    OUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUT_JSON.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    md = [
        "# ProjectScanner Cloud Duplicate Scan",
        "",
        f"repo_count: {len(rows)}",
        f"duplicate_groups: {len(groups)}",
        "",
        "| Score | Left | Right | Lang Match |",
        "|---|---|---|---|",
    ]

    for g in groups:
        md.append(
            f"| {g['score']} | {g['left']} | {g['right']} | {g['language_match']} |"
        )

    OUT_MD.write_text(
        "\n".join(md) + "\n",
        encoding="utf-8",
    )

    print("PROJECTSCANNER_CLOUD_DUPLICATE_SCAN=PASS")
    print(f"REPOS={len(rows)}")
    print(f"DUPLICATE_GROUPS={len(groups)}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
