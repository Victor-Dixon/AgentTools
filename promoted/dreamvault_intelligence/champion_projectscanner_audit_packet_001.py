#!/usr/bin/env python3
"""Scan reachable champion repos + assemble ChatGPT audit packet."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PS_ROOT = Path(r"D:\projectscanner")
CLASSIFICATION = ROOT / "data/reports/consolidation/portfolio_champion_classification_latest.json"
CHAMPION_MANIFEST = ROOT / "runtime/manifests/portfolio_champion_repos_24_20260703.yaml"
STAGING_ROOT = ROOT / "data/reports/projectscanner/staging/champions"
PACKET_OUT = ROOT / "data/reports/projectscanner/champion_chatgpt_audit_packet_latest.json"
PACKET_MD = ROOT / "data/reports/projectscanner/champion_chatgpt_audit_packet_latest.md"


def load_reachable() -> list[dict]:
    data = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    return [r for r in data.get("repos", []) if r.get("path_exists") and r.get("local_path")]


def staging_dir(name: str) -> Path:
    return STAGING_ROOT / name.replace("/", "_")


def staging_has_analysis(name: str) -> bool:
    return bool(list(staging_dir(name).glob("project_analysis_*.json")))


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 3600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def scan_champion(entry: dict, *, timeout: int = 3600, skip_scan: bool = False) -> dict:
    name = entry["repo"]
    repo_path = Path(entry["local_path"]).resolve()
    staging = staging_dir(name)
    staging.mkdir(parents=True, exist_ok=True)

    did_skip_scan = skip_scan and staging_has_analysis(name)
    if did_skip_scan:
        scan = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    else:
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
            timeout=timeout,
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
    packet_summary = None
    if packet_path.is_file():
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet_summary = {
            "schema": packet.get("schema"),
            "repo": packet.get("repo"),
            "generated_at": packet.get("generated_at"),
            "risk_level": packet.get("risk_level"),
            "recommended_action": packet.get("recommended_action"),
            "dirty_classes": packet.get("dirty_classes"),
            "candidate_lanes": packet.get("candidate_lanes"),
            "file_count": (packet.get("scan") or {}).get("file_count"),
            "git_dirty": (packet.get("git") or {}).get("dirty_count"),
        }

    analysis_files = sorted(staging.glob("project_analysis_*.json"))
    analysis_stats = None
    if analysis_files:
        analysis = json.loads(analysis_files[0].read_text(encoding="utf-8"))
        langs: dict[str, int] = {}
        for item in analysis.values():
            if isinstance(item, dict):
                lang = item.get("language") or "unknown"
                langs[lang] = langs.get(lang, 0) + 1
        analysis_stats = {
            "path": str(analysis_files[0]),
            "entry_count": len(analysis),
            "top_languages": dict(sorted(langs.items(), key=lambda x: -x[1])[:8]),
        }

    ok = scan.returncode == 0 and emit.returncode == 0 and packet_path.is_file()
    return {
        "repo": name,
        "tier": entry.get("tier"),
        "local_path": str(repo_path),
        "status": "PASS" if ok else "FAIL",
        "skipped_scan": did_skip_scan,
        "scan_exit": scan.returncode,
        "emit_exit": emit.returncode,
        "scan_stderr_tail": (scan.stderr or "")[-300:],
        "emit_stderr_tail": (emit.stderr or "")[-300:],
        "packet_path": str(packet_path) if packet_path.is_file() else None,
        "packet_summary": packet_summary,
        "analysis_stats": analysis_stats,
    }


def assemble_markdown(packet: dict) -> str:
    lines = [
        "# Champion Portfolio — ChatGPT Audit Packet",
        "",
        f"Generated: {packet['generated_at']}",
        f"Champion manifest: `{packet['champion_manifest']}`",
        f"Classification: `{packet['classification_source']}`",
        "",
        "## Summary",
        "",
        f"- Reachable champions scanned: **{packet['reachable_count']}**",
        f"- PASS: **{packet['passed']}** | FAIL: **{packet['failed']}** | Missing paths: **{packet['missing_paths']}**",
        "",
        "## Paste into ChatGPT",
        "",
        "Use this packet for portfolio audit. Each repo includes projectscanner analysis + intelligence_packet summary.",
        "Upload individual `runtime/state/intelligence_packet.v1.json` files for deep dives.",
        "",
        "## Repos",
        "",
    ]
    for repo in packet["repos"]:
        lines.append(f"### {repo['repo']} ({repo.get('status')})")
        lines.append(f"- Path: `{repo.get('local_path')}`")
        lines.append(f"- Tier: {repo.get('tier')}")
        if repo.get("packet_summary"):
            ps = repo["packet_summary"]
            lines.append(f"- Risk: {ps.get('risk_level')} | Action: {ps.get('recommended_action')}")
            lines.append(f"- Files: {ps.get('file_count')} | Git dirty: {ps.get('git_dirty')}")
        if repo.get("analysis_stats"):
            langs = repo["analysis_stats"].get("top_languages") or {}
            lines.append(f"- Analysis entries: {repo['analysis_stats'].get('entry_count')} | Langs: {langs}")
        if repo.get("packet_path"):
            lines.append(f"- Packet: `{repo['packet_path']}`")
        lines.append("")
    if packet.get("missing_repos"):
        lines.extend(["## Missing local paths (not scanned)", ""])
        for m in packet["missing_repos"]:
            lines.append(f"- **{m['repo']}**: {m.get('local_path') or 'unknown'}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", dest="repos", help="Limit to repo name")
    parser.add_argument("--exclude", action="append", dest="excludes", help="Skip repo name")
    parser.add_argument("--skip-existing", action="store_true", help="Skip run_scanner when staging analysis exists")
    parser.add_argument("--timeout", type=int, default=3600, help="Per-repo scan timeout seconds")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    all_repos = json.loads(CLASSIFICATION.read_text(encoding="utf-8")).get("repos", [])
    missing_repos = [
        {"repo": r["repo"], "local_path": r.get("local_path"), "tier": r.get("tier")}
        for r in all_repos
        if not r.get("path_exists")
    ]
    reachable = load_reachable()
    if args.repos:
        wanted = set(args.repos)
        reachable = [r for r in reachable if r["repo"] in wanted]
    if args.excludes:
        excluded = set(args.excludes)
        reachable = [r for r in reachable if r["repo"] not in excluded]

    results: list[dict] = []
    for entry in reachable:
        if args.dry_run:
            results.append({"repo": entry["repo"], "status": "RESOLVED", "local_path": entry["local_path"]})
            continue
        print(f"SCAN {entry['repo']} -> {entry['local_path']}", flush=True)
        results.append(scan_champion(entry, timeout=args.timeout, skip_scan=args.skip_existing))

    passed = sum(1 for r in results if r.get("status") == "PASS")
    packet = {
        "schema": "dreamvault.champion_chatgpt_audit_packet.v1",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "champion_manifest": str(CHAMPION_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "classification_source": str(CLASSIFICATION.relative_to(ROOT)).replace("\\", "/"),
        "reachable_count": len(reachable),
        "missing_paths": len(missing_repos),
        "passed": passed,
        "failed": sum(1 for r in results if r.get("status") == "FAIL"),
        "missing_repos": missing_repos,
        "repos": results,
        "operator_paste": "Upload champion_chatgpt_audit_packet_latest.md + per-repo intelligence_packet.v1.json to ChatGPT for portfolio audit.",
    }
    PACKET_OUT.parent.mkdir(parents=True, exist_ok=True)
    PACKET_OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    PACKET_MD.write_text(assemble_markdown(packet) + "\n", encoding="utf-8")
    print(f"WROTE {PACKET_OUT}")
    print(f"WROTE {PACKET_MD}")
    print(f"PASS={passed} FAIL={packet['failed']} REACHABLE={len(reachable)} MISSING={len(missing_repos)}")
    return 0 if passed == len(reachable) and reachable else 1


if __name__ == "__main__":
    raise SystemExit(main())
