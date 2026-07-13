#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

TREE = Path("data/reports/projectscanner/github_tree/latest_tree_inventory.json")
OUT_JSON = Path("data/reports/projectscanner/cloud_duplicate_scan/latest_v2.json")
OUT_MD = Path("data/reports/projectscanner/cloud_duplicate_scan/latest_v2.md")

def ext(path: str) -> str:
    return Path(path).suffix.lower() or "NO_EXT"

def main() -> int:
    payload = json.loads(TREE.read_text(encoding="utf-8"))
    repos = payload.get("repos", [])

    by_sha = defaultdict(list)
    repo_exts = {}

    for repo in repos:
        name = repo.get("repo")
        files = repo.get("files", [])
        exts = set()
        for f in files:
            path = f.get("path", "")
            sha = f.get("sha")
            if not sha:
                continue
            exts.add(ext(path))
            by_sha[sha].append({"repo": name, "path": path, "size": f.get("size", 0)})
        repo_exts[name] = exts

    duplicate_files = [
        {"sha": sha, "occurrences": vals}
        for sha, vals in by_sha.items()
        if len({v["repo"] for v in vals}) > 1
    ]

    repo_similarity = []
    for a, b in combinations(sorted(repo_exts), 2):
        left = repo_exts[a]
        right = repo_exts[b]
        score = 0.0 if not left or not right else len(left & right) / len(left | right)
        if score >= 0.50:
            repo_similarity.append({"left": a, "right": b, "extension_similarity": round(score, 3)})

    result = {
        "repo_count": len(repos),
        "duplicate_file_groups": len(duplicate_files),
        "repo_extension_similarity_groups": len(repo_similarity),
        "duplicate_files": duplicate_files[:100],
        "repo_similarity": repo_similarity[:100],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# ProjectScanner Cloud Duplicate Scan V2",
        "",
        f"repo_count: {result['repo_count']}",
        f"duplicate_file_groups: {result['duplicate_file_groups']}",
        f"repo_extension_similarity_groups: {result['repo_extension_similarity_groups']}",
        "",
        "## Duplicate File Groups",
    ]
    for g in duplicate_files[:25]:
        lines.append(f"### {g['sha']}")
        for o in g["occurrences"]:
            lines.append(f"- {o['repo']}: {o['path']} ({o['size']})")
        lines.append("")
    lines += ["## Repo Extension Similarity", "", "| Score | Left | Right |", "|---:|---|---|"]
    for g in repo_similarity[:50]:
        lines.append(f"| {g['extension_similarity']} | {g['left']} | {g['right']} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PROJECTSCANNER_CLOUD_DUPLICATE_SCAN_V2=PASS")
    print(f"REPOS={result['repo_count']}")
    print(f"DUPLICATE_FILE_GROUPS={result['duplicate_file_groups']}")
    print(f"REPO_EXTENSION_SIMILARITY_GROUPS={result['repo_extension_similarity_groups']}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
