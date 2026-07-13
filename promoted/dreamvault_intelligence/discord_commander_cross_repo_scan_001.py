#!/usr/bin/env python3
"""Cross-repo scan for Discord Commander references and package surfaces."""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "data/reports/discord/commander_cross_repo_scan_latest.json"

ROOTS = [
    REPO_ROOT,
    Path(r"D:\DreamOS_Core"),
    Path(r"D:\projectscanner"),
    Path(r"D:\Projects\github-architect-bot"),
    Path(r"D:\projects\portfolio-review\Victor-Dixon__AutoDream.Os"),
    Path(r"D:\AgentTools"),
    Path(r"D:\Dream.os-Core"),
]

PATTERN = re.compile(r"discord[_-]?commander|Discord Commander|discordcommander", re.I)
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
    ".pytest_cache",
    "archive",
    "data",
    "runtime/project_artifacts",
    "runtime/state",
    "runtime/logs",
}
EXTS = {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".bat", ".ps1", ".ts", ".tsx", ".js"}


def _should_skip(path: Path) -> bool:
    return bool(SKIP_DIRS.intersection(path.parts))


SCAN_SUBDIRS = ("src", "runtime", "tests", "scripts", "docs", "data/registry", "data/reports/discord")


def _iter_files(root: Path):
    for sub in SCAN_SUBDIRS:
        base = root / sub
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and not _should_skip(path):
                yield path


def scan_root(root: Path) -> dict:
    if not root.is_dir():
        return {"root": str(root), "status": "missing", "reference_count": 0, "reference_files": []}

    hits: list[str] = []
    for path in _iter_files(root):
        if path.suffix.lower() not in EXTS and path.name not in {"Dockerfile", "Makefile"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if PATTERN.search(text):
            hits.append(str(path.relative_to(root)))

    pkg = root / "src" / "discord_commander"
    new_pkg = root / "src" / "dreamvault" / "discord" / "commander"
    return {
        "root": str(root),
        "status": "ok",
        "legacy_package": {
            "path": str(pkg),
            "exists": pkg.is_dir(),
            "py_files": len(list(pkg.rglob("*.py"))) if pkg.is_dir() else 0,
        },
        "revitalized_package": {
            "path": str(new_pkg),
            "exists": new_pkg.is_dir(),
            "py_files": len(list(new_pkg.rglob("*.py"))) if new_pkg.is_dir() else 0,
        },
        "reference_count": len(hits),
        "reference_files": sorted(hits)[:50],
    }


def main() -> int:
    report = {
        "schema": "dreamvault.discord_commander_cross_repo_scan.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "destructive_actions": 0,
        "repos": [scan_root(root) for root in ROOTS],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("DISCORD_COMMANDER_CROSS_REPO_SCAN=PASS")
    for row in report["repos"]:
        name = Path(row["root"]).name
        legacy = row.get("legacy_package") or {}
        rev = row.get("revitalized_package") or {}
        print(
            f"REPO={name} refs={row.get('reference_count', 0)} "
            f"legacy_pkg={legacy.get('exists', False)}({legacy.get('py_files', 0)}) "
            f"revitalized={rev.get('exists', False)}({rev.get('py_files', 0)})"
        )
    print(f"REPORT={OUT.relative_to(REPO_ROOT)}")
    print("DESTRUCTIVE_ACTIONS=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
