#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path("runtime/trading/datasets")
DEFAULT_DEST = Path.home() / "projects" / "DreamTradeData"


def now() -> datetime:
    return datetime.now(timezone.utc)


def gzip_copy(src: Path, dst: Path) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)
    raw = src.read_bytes()
    with gzip.open(dst, "wb") as f:
        f.write(raw)
    return len(raw)


def ensure_repo(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        subprocess.run(["git", "init"], cwd=dest, check=True)

    readme = dest / "README.md"
    if not readme.exists():
        readme.write_text(
            "# DreamTradeData\n\n"
            "Private trading research dataset export repository.\n\n"
            "Keep private unless licensing and redistribution rights are cleared.\n",
            encoding="utf-8",
        )


def export_files(dest: Path) -> dict:
    manifest = {
        "generated_at": now().isoformat(),
        "source_repo": str(Path.cwd()),
        "source_dir": str(SOURCE),
        "dest_repo": str(dest),
        "private_by_default": True,
        "files": [],
    }

    candle_root = SOURCE / "candles"
    if candle_root.exists():
        for src in sorted(candle_root.rglob("*.csv")):
            rel = src.relative_to(candle_root)
            dst = dest / "candles" / rel.with_suffix(".csv.gz")
            size = gzip_copy(src, dst)
            manifest["files"].append({
                "kind": "candles",
                "source": str(src),
                "dest": str(dst.relative_to(dest)),
                "raw_bytes": size,
            })

    for name in ["events.jsonl", "features.jsonl"]:
        src = SOURCE / name
        if src.exists():
            day = now().strftime("%Y-%m-%d")
            stem = name.replace(".jsonl", "")
            dst = dest / stem / f"{stem}_{day}.jsonl.gz"
            size = gzip_copy(src, dst)
            manifest["files"].append({
                "kind": stem,
                "source": str(src),
                "dest": str(dst.relative_to(dest)),
                "raw_bytes": size,
            })

    day = now().strftime("%Y-%m-%d")
    manifest_path = dest / "manifests" / f"{day}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def commit_repo(dest: Path) -> bool:
    subprocess.run(["git", "add", "."], cwd=dest, check=True)
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=dest,
        text=True,
        capture_output=True,
        check=True,
    )
    if not status.stdout.strip():
        return False
    subprocess.run(
        ["git", "commit", "-m", f"data: export trading dataset {now().strftime('%Y-%m-%d')}"],
        cwd=dest,
        check=True,
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=str(DEFAULT_DEST))
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    dest = Path(args.dest).expanduser()
    ensure_repo(dest)
    manifest = export_files(dest)

    committed = commit_repo(dest) if args.commit else False

    print(f"DEST_REPO={dest}")
    print(f"MANIFEST={manifest['manifest_path']}")
    print(f"FILES_EXPORTED={len(manifest['files'])}")
    print(f"DATASET_COMMITTED={committed}")
    print("TRADING_DATASET_EXPORT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
