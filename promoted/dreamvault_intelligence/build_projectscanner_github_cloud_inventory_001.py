#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

OUT_JSON = Path("data/reports/projectscanner/github_cloud/latest_inventory.json")
OUT_MD = Path("data/reports/projectscanner/github_cloud/latest_inventory.md")

DEFAULT_OWNER = "Victor-Dixon"

def github_get(url: str, token: str | None) -> object:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "DreamOS-ProjectScanner-GitHub-Inventory")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def build_inventory(owner: str, token: str | None) -> dict:
    url = f"https://api.github.com/users/{owner}/repos?per_page=100&type=owner&sort=updated"
    repos = github_get(url, token)
    rows = []
    for repo in repos:
        rows.append({
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "private": repo.get("private"),
            "default_branch": repo.get("default_branch"),
            "language": repo.get("language"),
            "updated_at": repo.get("updated_at"),
            "pushed_at": repo.get("pushed_at"),
            "html_url": repo.get("html_url"),
            "archived": repo.get("archived"),
            "fork": repo.get("fork"),
        })
    return {
        "owner": owner,
        "repo_count": len(rows),
        "mode": "github_readonly_inventory",
        "token_used": bool(token),
        "repos": rows,
    }

def render_md(payload: dict) -> str:
    lines = [
        "# ProjectScanner GitHub Cloud Inventory",
        "",
        f"owner: {payload['owner']}",
        f"repo_count: {payload['repo_count']}",
        f"token_used: {payload['token_used']}",
        "",
        "| Repo | Branch | Language | Updated | Archived | Fork |",
        "|---|---|---|---|---:|---:|",
    ]
    for r in payload["repos"]:
        lines.append(
            f"| {r['full_name']} | {r['default_branch']} | {r['language']} | "
            f"{r['updated_at']} | {r['archived']} | {r['fork']} |"
        )
    return "\n".join(lines) + "\n"

def main() -> int:
    owner = os.environ.get("GITHUB_OWNER", DEFAULT_OWNER)
    token = os.environ.get("GITHUB_TOKEN")

    payload = build_inventory(owner, token)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")

    print("PROJECTSCANNER_GITHUB_CLOUD_INVENTORY=PASS")
    print(f"OWNER={owner}")
    print(f"REPOS={payload['repo_count']}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
