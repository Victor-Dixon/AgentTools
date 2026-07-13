#!/usr/bin/env python3
"""
@file Discord bot logic bundle builder
@summary Collects Discord-related logic into a review zip and manifest.
@registry docs/recovery/recovery_registry.yaml#discord-bot-logic-bundle
"""

from __future__ import annotations

import fnmatch
import os
import zipfile
from pathlib import Path

ROOT = Path.cwd()
OUTDIR = ROOT / "data" / "reports" / "discord_bot_bundle"
ZIP_PATH = OUTDIR / "discord_bot_logic_bundle.zip"
MANIFEST_PATH = OUTDIR / "discord_bot_logic_manifest.md"

INCLUDE_HINTS = (
    "discord",
    "webhook",
    "channel",
    "view",
    "bot",
)

EXCLUDE_PARTS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".zip",
}


def is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_PARTS:
        return True
    return path.suffix in EXCLUDE_SUFFIXES


def is_relevant(path: Path) -> bool:
    rel = path.as_posix().lower()
    if rel.startswith("discord_architect/"):
        return True
    return any(hint in rel for hint in INCLUDE_HINTS)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if is_excluded(rel):
            continue
        if is_relevant(rel):
            files.append(rel)
    return sorted(files, key=lambda p: p.as_posix())


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    files = iter_files()

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            zf.write(ROOT / rel, rel.as_posix())

    lines = [
        "# Discord Bot Logic Bundle Manifest",
        "",
        f"Total files: {len(files)}",
        f"Bundle: `{ZIP_PATH}`",
        "",
        "## Files",
        "",
    ]
    lines.extend(f"- `{path.as_posix()}`" for path in files)
    MANIFEST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("DISCORD_BOT_LOGIC_BUNDLE=PASS")
    print(f"FILES={len(files)}")
    print(f"MANIFEST={MANIFEST_PATH}")
    print(f"ZIP={ZIP_PATH}")


if __name__ == "__main__":
    main()
