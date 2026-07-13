#!/usr/bin/env python3
"""Full Discord fleet inventory — pattern scan across repos (no secret values)."""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_ROOTS = [
    r"D:\DreamVault",
    r"D:\AgentTools",
    r"D:\agent-tools",
    r"D:\Agent_Cellphone",
    r"D:\Agent_Cellphone_V2",
    r"D:\Agent_Cellphone_V2_Repository",
    r"D:\github-architect-bot",
    r"D:\Projects\github-architect-bot",
    r"D:\projectscanner",
    r"D:\DreamOS_Core",
    r"D:\Dream.os-Core",
    r"D:\websites",
    r"D:\projects\portfolio-review",
    r"D:\projects\portfolio-review\Victor-Dixon__Agent_Cellphone_V2_Repository",
    r"D:\projects\portfolio-review\Victor-Dixon__AutoDream.Os",
]

OUT_DIR = Path(os.environ.get("USERPROFILE", ".")) / ".dreamos" / "reports" / "discord_fleet_inventory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".next",
    "Cache",
    "GPUCache",
    "selenium_session",
    "coverage",
    "archive",
    "data",
    "merge",
    "salvage",
    "integrations",
    ".worktrees",
    "runtime/project_artifacts",
    "runtime/logs",
    "runtime/state",
}

EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".ps1",
    ".sh",
    ".env",
    ".example",
    ".toml",
    ".ini",
}

SCAN_SUBDIRS = (
    "src",
    "runtime",
    "tests",
    "scripts",
    "docs",
    "tools",
    ".github",
    "config",
    "agent_workspaces",
)

MAX_FILE_BYTES = 1_000_000

PATTERNS = {
    "discord_commander": r"\bdiscord_commander\b|Commander|unified_discord_bot",
    "discord_architect": r"discord[_-]?architect|architect.*discord|Discord Architect",
    "discord_libraries": r"discord\.py|discord\.js|@discordjs|nextcord|disnake|py-cord|interactions\.py|hikari|discord\.Client|commands\.Bot",
    "discord_tokens_env": r"DISCORD(_BOT)?_TOKEN|DISCORD_CLIENT_ID|DISCORD_GUILD_ID|DISCORD_PUBLIC_KEY|DISCORD_APPLICATION_ID",
    "discord_webhooks": r"DISCORD_WEBHOOK|discord_webhook|webhook_url|WEBHOOK_URL|discord\.com/api/webhooks",
    "closeout_discord": r"closeout.*discord|discord.*closeout|dispatch_cpc_closeout|CPC_ROUTER|cpc.*discord",
    "github_actions_discord": r"\.github/workflows|actions.*discord|discord.*actions|workflow.*webhook",
    "fleet_routing": r"fleet|lane_|Agent-[0-9]+|agent[_-]?status|a2a|transport",
}

SECRET_VALUE_PATTERNS = [
    re.compile(r"(discord\.com/api/webhooks/)[^\s\"'>)]+", re.I),
    re.compile(r"((?:DISCORD|WEBHOOK|TOKEN|SECRET|KEY)[A-Z0-9_]*\s*[:=]\s*)[^\s\"']+", re.I),
    re.compile(r"(Bot\s+)[A-Za-z0-9._-]+", re.I),
]

compiled = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}


def redact(text: str) -> str:
    out = text.strip()
    for pat in SECRET_VALUE_PATTERNS:
        out = pat.sub(lambda m: m.group(1) + "<redacted>", out)
    if len(out) > 220:
        out = out[:220] + "..."
    return out


def repo_label(root: Path, path: Path) -> str:
    try:
        rel = path.relative_to(root)
    except Exception:
        return root.name
    if root.name.lower() == "portfolio-review" and rel.parts:
        return rel.parts[0]
    return root.name


def should_skip_dir(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def should_scan_file(path: Path) -> bool:
    if should_skip_dir(path):
        return False
    if path.suffix.lower() not in EXTENSIONS and path.name not in {".env", ".env.example"}:
        return False
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return False
    except OSError:
        return False
    return True


def iter_files(root: Path):
    """Prefer focused subdirs for large repos; fall back to shallow root scan."""
    yielded = False
    for sub in SCAN_SUBDIRS:
        base = root / sub
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and should_scan_file(path):
                yielded = True
                yield path
    if not yielded:
        for path in root.rglob("*"):
            if path.is_file() and should_scan_file(path):
                yield path


def main() -> int:
    roots = [Path(r) for r in DEFAULT_ROOTS if Path(r).exists()]
    inventory: dict = {
        "id": "discord_fleet_inventory_001",
        "created": datetime.now(UTC).isoformat(),
        "destructive_actions": 0,
        "roots": [str(r) for r in roots],
        "patterns": list(PATTERNS.keys()),
        "repos": {},
        "totals": defaultdict(int),
    }

    for root in roots:
        print(f"SCAN_ROOT={root.name}", flush=True)
        for path in iter_files(root):
            repo = repo_label(root, path)
            entry = inventory["repos"].setdefault(
                repo,
                {
                    "root": str(root),
                    "files_scanned": 0,
                    "category_counts": defaultdict(int),
                    "matches": [],
                },
            )
            entry["files_scanned"] += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = str(path)
            for idx, line in enumerate(text.splitlines(), start=1):
                for category, pattern in compiled.items():
                    if pattern.search(line) or pattern.search(rel):
                        entry["category_counts"][category] += 1
                        inventory["totals"][category] += 1
                        if len(entry["matches"]) < 80:
                            entry["matches"].append(
                                {
                                    "category": category,
                                    "path": rel,
                                    "line": idx,
                                    "snippet": redact(line),
                                }
                            )

    inventory["totals"] = dict(inventory["totals"])
    for entry in inventory["repos"].values():
        entry["category_counts"] = dict(entry["category_counts"])

    latest_json = OUT_DIR / "discord_fleet_inventory_latest.json"
    stamp_json = OUT_DIR / f"discord_fleet_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    latest_md = OUT_DIR / "discord_fleet_inventory_latest.md"

    latest_json.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    stamp_json.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Discord Fleet Inventory",
        "",
        f"Created: `{inventory['created']}`",
        "",
        f"Destructive actions: `{inventory['destructive_actions']}`",
        "",
        "## Totals",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for k, v in sorted(inventory["totals"].items()):
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Repo Summary", "", "| Repo | Files scanned | Categories |", "|---|---:|---|"]
    for repo, entry in sorted(inventory["repos"].items()):
        cats = ", ".join(f"{k}:{v}" for k, v in sorted(entry["category_counts"].items()))
        lines.append(f"| {repo} | {entry['files_scanned']} | {cats} |")
    latest_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("STATUS=PASS")
    print("DESTRUCTIVE_ACTIONS=0")
    print(f"ROOTS_SCANNED={len(roots)}")
    print(f"REPOS_WITH_MATCHES={len(inventory['repos'])}")
    print(f"REPORT_JSON={latest_json}")
    print(f"REPORT_MD={latest_md}")
    for k, v in sorted(inventory["totals"].items()):
        print(f"TOTAL_{k.upper()}={v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
