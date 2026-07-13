#!/usr/bin/env python3
"""Run projectscanner across Victor-Dixon portfolio repos; emit intelligence library JSON."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PS_ROOT = Path(r"D:\projectscanner")
CLASSIFICATION = ROOT / "data/reports/portfolio/portfolio_25_repo_classification_20260704.json"
LIBRARY_OUT = ROOT / "data/reports/projectscanner/portfolio_intelligence_library_latest.json"
MANIFEST_OUT = ROOT / "data/reports/projectscanner/portfolio_scan_manifest_latest.json"
CLONE_ROOT = Path(r"D:\repos")

PATH_ROOTS = [
    CLONE_ROOT,
    Path(r"D:\DreamVault"),
    Path(r"D:\websites"),
    Path(r"D:\agent-tools"),
    Path(r"D:\projectscanner"),
]

SPECIAL_PATHS: dict[str, list[Path]] = {
    "websites": [CLONE_ROOT / "websites", Path(r"D:\websites")],
    "AgentTools": [CLONE_ROOT / "AgentTools", Path(r"D:\agent-tools")],
    "projectscanner": [CLONE_ROOT / "projectscanner", Path(r"D:\projectscanner")],
    "DreamVault": [CLONE_ROOT / "DreamVault", Path(r"D:\DreamVault")],
}


def load_repos() -> list[str]:
    data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    return [r["repo"] for r in data.get("repos", [])]


def resolve_repo_path(name: str) -> Path | None:
    for candidate in SPECIAL_PATHS.get(name, []):
        if (candidate / ".git").exists():
            return candidate.resolve()
    for root in PATH_ROOTS:
        candidate = root if root.name == name else root / name
        if (candidate / ".git").exists():
            return candidate.resolve()
    return None


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 3600) -> subprocess.CompletedProcess[str]:
    env = dict(**__import__("os").environ)
    env.pop("GH_TOKEN", None)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env=env,
    )


def clone_repo(name: str) -> Path | None:
    dest = CLONE_ROOT / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if (dest / ".git").exists():
        return dest.resolve()
    proc = run(
        ["gh", "repo", "clone", f"Victor-Dixon/{name}", str(dest), "--", "--depth", "1"],
        timeout=600,
    )
    if proc.returncode != 0:
        return None
    return dest.resolve()


def scan_repo(name: str, repo_path: Path, *, packet_only: bool = True) -> dict:
    staging = ROOT / "data/reports/projectscanner/staging" / name
    staging.mkdir(parents=True, exist_ok=True)

    scan = run(
        [
            sys.executable,
            str(PS_ROOT / "src/utils/run_scanner.py"),
            "--target",
            str(repo_path),
            "--output",
            str(staging),
            "--mode",
            "nightly",
        ],
        cwd=PS_ROOT,
    )

    emit = run(
        [
            sys.executable,
            str(PS_ROOT / "scripts/intelligence/emit_intelligence.py"),
            str(repo_path),
            "--packet-only",
        ],
        cwd=PS_ROOT,
    )

    packet_path = repo_path / "runtime/state/intelligence_packet.v1.json"
    analysis_files = sorted(staging.glob("project_analysis_*.json"))
    analysis_path = analysis_files[0] if analysis_files else None

    packet_summary: dict | None = None
    if packet_path.exists():
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet_summary = {
            "schema": packet.get("schema"),
            "repo": packet.get("repo"),
            "generated_at": packet.get("generated_at"),
            "risk_level": packet.get("risk_level"),
            "recommended_action": packet.get("recommended_action"),
            "dirty_classes": packet.get("dirty_classes"),
            "candidate_lanes": packet.get("candidate_lanes"),
            "file_count": packet.get("scan", {}).get("file_count"),
        }

    analysis_stats: dict | None = None
    if analysis_path and analysis_path.exists():
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        langs: dict[str, int] = {}
        for entry in analysis.values():
            if isinstance(entry, dict):
                lang = entry.get("language") or "unknown"
                langs[lang] = langs.get(lang, 0) + 1
        analysis_stats = {
            "path": str(analysis_path),
            "entry_count": len(analysis),
            "languages": dict(sorted(langs.items(), key=lambda x: -x[1])[:12]),
        }

    ok = scan.returncode == 0 and emit.returncode == 0 and packet_path.exists()
    return {
        "repo": name,
        "path": str(repo_path),
        "status": "PASS" if ok else "FAIL",
        "scan_exit": scan.returncode,
        "emit_exit": emit.returncode,
        "scan_stderr_tail": (scan.stderr or "")[-400:],
        "emit_stderr_tail": (emit.stderr or "")[-400:],
        "packet_path": str(packet_path) if packet_path.exists() else None,
        "packet_summary": packet_summary,
        "analysis_stats": analysis_stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Portfolio projectscanner batch")
    parser.add_argument("--clone-missing", action="store_true", help="Shallow-clone missing repos to D:\\repos")
    parser.add_argument("--repo", action="append", dest="repos", help="Limit to specific repo name")
    parser.add_argument("--dry-run", action="store_true", help="Resolve paths only")
    args = parser.parse_args()

    names = args.repos or load_repos()
    results: list[dict] = []
    missing: list[str] = []

    for name in names:
        path = resolve_repo_path(name)
        if path is None and args.clone_missing:
            path = clone_repo(name)
        if path is None:
            missing.append(name)
            results.append({"repo": name, "status": "MISSING", "path": None})
            continue
        if args.dry_run:
            results.append({"repo": name, "status": "RESOLVED", "path": str(path)})
            continue
        print(f"SCAN {name} -> {path}", flush=True)
        results.append(scan_repo(name, path))

    passed = sum(1 for r in results if r.get("status") == "PASS")
    library = {
        "schema": "dreamvault.portfolio_intelligence_library.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_count": len(names),
        "passed": passed,
        "failed": sum(1 for r in results if r.get("status") == "FAIL"),
        "missing": missing,
        "repos": results,
    }
    LIBRARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    LIBRARY_OUT.write_text(json.dumps(library, indent=2), encoding="utf-8")
    MANIFEST_OUT.write_text(json.dumps(library, indent=2), encoding="utf-8")
    print(f"WROTE {LIBRARY_OUT}")
    print(f"PASS={passed} FAIL={library['failed']} MISSING={len(missing)}")
    return 0 if not missing and passed == len(names) else 1


if __name__ == "__main__":
    raise SystemExit(main())
