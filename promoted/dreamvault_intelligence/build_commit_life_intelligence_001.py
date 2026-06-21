#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


PROJECTS_ROOT = Path.home() / "projects"
OUT_DIR = Path("data/reports/intelligence/commit_life")


STOP = {
    "the","and","for","with","into","from","add","fix","update","wire","build",
    "to","a","of","in","on","by","or","as","is","at","readme","initial"
}


def latest_audit_root(root: Path = PROJECTS_ROOT) -> Path | None:
    audits = sorted(root.glob("_git_commit_life_audit_*"))
    return audits[-1] if audits else None


def parse_commits(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.split("|", 4)
        if len(parts) != 5:
            continue
        repo, date, commit, author, subject = parts
        rows.append({
            "repo": repo,
            "date": date,
            "commit": commit,
            "author": author,
            "subject": subject,
        })
    return rows


def tokenize(subject: str) -> list[str]:
    clean = "".join(ch.lower() if ch.isalnum() or ch in "_-" else " " for ch in subject)
    return [w for w in clean.split() if w and w not in STOP and len(w) > 2]


def analyze(rows: list[dict]) -> dict:
    repo_counts = Counter(r["repo"] for r in rows)
    words = Counter()
    repo_words = defaultdict(Counter)

    for r in rows:
        toks = tokenize(r["subject"])
        words.update(toks)
        repo_words[r["repo"]].update(toks)

    top_repos = repo_counts.most_common(20)
    neglected = [repo for repo, count in repo_counts.items() if count <= 5]

    themes = []
    for word, count in words.most_common(40):
        themes.append({"theme": word, "count": count})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_commits": len(rows),
        "repo_count": len(repo_counts),
        "top_repos": [{"repo": r, "commits": c} for r, c in top_repos],
        "low_commit_repos": sorted(neglected),
        "top_themes": themes,
        "operator_readout": {
            "profile": "high-velocity systems founder",
            "strength": "turns intuition into governed runtime, tests, manifests, dashboards, and replayable reports",
            "risk": "creates operational surfaces faster than consolidation lanes close them",
            "best_next_leverage": "weekly commit intelligence review plus promotion/archive queue",
        },
    }


def render_md(payload: dict) -> str:
    lines = [
        "# Commit Life Intelligence",
        "",
        f"generated_at: {payload['generated_at']}",
        f"total_commits: {payload['total_commits']}",
        f"repo_count: {payload['repo_count']}",
        "",
        "## Operator Readout",
        "",
    ]
    for k, v in payload["operator_readout"].items():
        lines.append(f"- **{k}:** {v}")

    lines.extend(["", "## Top Repos", "", "| Repo | Commits |", "|---|---:|"])
    for r in payload["top_repos"]:
        lines.append(f"| {r['repo']} | {r['commits']} |")

    lines.extend(["", "## Top Themes", "", "| Theme | Count |", "|---|---:|"])
    for t in payload["top_themes"][:25]:
        lines.append(f"| {t['theme']} | {t['count']} |")

    lines.extend(["", "## Low Commit Repos", ""])
    for repo in payload["low_commit_repos"]:
        lines.append(f"- {repo}")

    return "\n".join(lines) + "\n"


def main() -> int:
    audit = latest_audit_root()
    if not audit:
        raise SystemExit("NO_GIT_COMMIT_LIFE_AUDIT_FOUND")

    rows = parse_commits(audit / "all_commits_sorted.psv")
    payload = analyze(rows)
    payload["source_audit"] = str(audit)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "latest_commit_life_intelligence.json"
    md_path = OUT_DIR / "latest_commit_life_intelligence.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_md(payload), encoding="utf-8")

    print("COMMIT_LIFE_INTELLIGENCE=PASS")
    print(f"SOURCE_AUDIT={audit}")
    print(f"TOTAL_COMMITS={payload['total_commits']}")
    print(f"REPO_COUNT={payload['repo_count']}")
    print(f"JSON={json_path}")
    print(f"MD={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
