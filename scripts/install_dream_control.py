#!/usr/bin/env python3
"""One-shot Termux/Linux installer for the Dream.OS control-plane client.

Discovery first: this installer inspects what already exists (DreamVault,
ProjectScanner, AgentTools, CPC/cliprun, gh, the VPS SSH key, VPS
reachability) and only creates what is genuinely missing.  It never replaces
an existing system.

    python3 scripts/install_dream_control.py [--bin-dir ~/bin] [--no-vps-probe]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dream_control.config import (  # noqa: E402
    DEFAULT_REPOS,
    DEFAULT_VPS,
    OperatorConfig,
    detect_environment,
    paths,
    tool_available,
)
from dream_control.policy.publish import DEFAULT_POLICY  # noqa: E402

SHIMS = {
    "passdown": "passdown",
    "dreamstate": "state",
    "dreamevent": "event",
    "agentstart": "agent-start",
    "agentstatus": "agent-status",
    "dreamagents": "agents",
    "dreamscan": "scan",
    "dreamcap": "cap",
    "dreamlane": "lane",
    "dreamctl": "",
}

SHIM_TEMPLATE = """#!/usr/bin/env bash
# Installed by dream_control installer. Do not edit; re-run the installer.
export PYTHONPATH="{repo_root}${{PYTHONPATH:+:$PYTHONPATH}}"
exec python3 -m dream_control.cli {subcommand} "$@"
"""


def discover_repos(projects_root: Path) -> dict[str, dict[str, object]]:
    """Find existing portfolio checkouts before assuming anything is missing."""
    found: dict[str, dict[str, object]] = {}
    search_roots = [projects_root, Path.home(), REPO_ROOT.parent]
    for repo, meta in DEFAULT_REPOS.items():
        record = {**meta, "path": None, "present": False}
        for root in search_roots:
            candidate = root / repo
            if (candidate / ".git").exists():
                record["path"] = str(candidate.resolve())
                record["present"] = True
                break
        found[repo] = record
    return found


def discover_cpc(repos: dict[str, dict[str, object]]) -> dict[str, object]:
    cliprun = Path.home() / "bin" / "cliprun"
    dv_path = repos.get("DreamVault", {}).get("path")
    cpc_dir = Path(str(dv_path)) / "runtime" / "tools" / "cpc" if dv_path else None
    return {
        "cliprun": str(cliprun),
        "cliprun_present": cliprun.exists(),
        "cpc_tools_dir": str(cpc_dir) if cpc_dir else None,
        "cpc_tools_present": bool(cpc_dir and cpc_dir.is_dir()),
    }


def probe_vps(identity: Path, timeout: int = 12) -> dict[str, object]:
    if not identity.exists():
        return {"probed": False, "reason": f"identity file missing: {identity}"}
    if not tool_available("ssh"):
        return {"probed": False, "reason": "ssh client not available"}
    argv = [
        "ssh", "-i", str(identity),
        "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes", "-o", "ConnectTimeout=10",
        f"{DEFAULT_VPS['user']}@{DEFAULT_VPS['host']}", "hostname",
    ]
    try:
        proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"probed": True, "reachable": False, "reason": str(exc)}
    return {
        "probed": True,
        "reachable": proc.returncode == 0,
        "hostname": proc.stdout.strip(),
        "reason": proc.stderr.strip() if proc.returncode else "",
    }


def write_configs(repos: dict[str, dict[str, object]], projects_root: Path, force: bool) -> list[str]:
    p = paths().ensure()
    written: list[str] = []

    if force or not p.operator_file.exists():
        config = OperatorConfig(
            projects_root=str(projects_root),
            repos={k: v for k, v in repos.items()},
            vps=dict(DEFAULT_VPS),
            notes=[
                "Important work is executed from Android Termux via CPC/cliprun.",
                "Internal event recording is automatic; external publishing is opt-in.",
            ],
        )
        config.save(p)
        written.append(str(p.operator_file))

    if force or not p.environments_file.exists():
        p.environments_file.write_text(
            json.dumps(
                {
                    "detected": detect_environment(),
                    "known": [
                        "android_termux", "dreamos_vps", "windows_desktop",
                        "claude", "linux", "local_model",
                    ],
                },
                indent=2, sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        written.append(str(p.environments_file))

    if force or not p.policies_file.exists():
        policies = dict(DEFAULT_POLICY)
        policies["preservation_holds"] = {
            "feat/captain-governance-mvp-001": "HOLD_SALVAGE_ARCHAEOLOGY",
            "polish/product-surface-001": "HOLD_FORENSIC",
            "reconcile/k2-last-copy-salvage-001": "HOLD_PRESERVE",
        }
        p.policies_file.write_text(
            json.dumps(policies, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        written.append(str(p.policies_file))

    p.event_log.touch(exist_ok=True)
    return written


def install_shims(bin_dir: Path) -> list[str]:
    bin_dir.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    for name, subcommand in SHIMS.items():
        target = bin_dir / name
        target.write_text(
            SHIM_TEMPLATE.format(repo_root=REPO_ROOT, subcommand=subcommand), encoding="utf-8"
        )
        target.chmod(0o755)
        installed.append(str(target))
    return installed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install the Dream.OS control-plane client")
    parser.add_argument("--bin-dir", default=str(Path.home() / "bin"))
    parser.add_argument("--projects-root", default=str(Path.home() / "projects"))
    parser.add_argument("--no-vps-probe", action="store_true")
    parser.add_argument("--force", action="store_true", help="overwrite existing config files")
    parser.add_argument("--no-selftest", action="store_true")
    args = parser.parse_args(argv)

    projects_root = Path(args.projects_root).expanduser()
    bin_dir = Path(args.bin_dir).expanduser()

    print("== discovery ==")
    repos = discover_repos(projects_root)
    for repo, record in sorted(repos.items()):
        print(f"  {repo:<18} {'found  ' + str(record['path']) if record['present'] else 'MISSING'}")

    cpc = discover_cpc(repos)
    print(f"  cliprun            {'found  ' + cpc['cliprun'] if cpc['cliprun_present'] else 'MISSING'}")
    print(f"  CPC toolchain      {'found  ' + str(cpc['cpc_tools_dir']) if cpc['cpc_tools_present'] else 'MISSING'}")
    for tool in ("git", "gh", "ssh", "python3"):
        print(f"  {tool:<18} {'found' if tool_available(tool) else 'MISSING'}")

    identity = Path(str(DEFAULT_VPS["identity_file"])).expanduser()
    print(f"  VPS ssh key        {'found  ' + str(identity) if identity.exists() else 'MISSING'}")
    if not args.no_vps_probe:
        vps = probe_vps(identity)
        state = "reachable" if vps.get("reachable") else f"not reachable ({vps.get('reason')})"
        print(f"  VPS {DEFAULT_VPS['host']:<14} {state}")

    print("\n== config/state ==")
    written = write_configs(repos, projects_root, args.force)
    for path in written:
        print(f"  wrote {path}")
    if not written:
        print("  existing config preserved (use --force to overwrite)")
    print(f"  control home: {paths().home}")

    print("\n== commands ==")
    for path in install_shims(bin_dir):
        print(f"  installed {path}")
    if str(bin_dir) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"\n  NOTE: {bin_dir} is not on PATH. Add to your shell profile:")
        print(f'    export PATH="{bin_dir}:$PATH"')

    if args.no_selftest:
        return 0
    print("\n== selftest ==")
    selftest = [sys.executable, "-m", "dream_control.cli", "passdown", "selftest"]
    if args.no_vps_probe:
        selftest.append("--no-vps")
    env = {**os.environ, "PYTHONPATH": f"{REPO_ROOT}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"}
    return subprocess.run(selftest, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
