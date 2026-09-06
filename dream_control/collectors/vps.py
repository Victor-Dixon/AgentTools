"""Dream.OS VPS runtime node: reachability, runner, daemon, checkouts.

The VPS is a first-class runtime node, not just an SSH destination.  This
collector is strictly *read-only*: it never re-registers or restarts the
self-hosted runner.
"""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from ..config import OperatorConfig, tool_available
from ._run import run

# Read-only probes only. Nothing here mutates VPS state.
_PROBE = (
    "hostname; "
    "echo '---RUNNER_PROC---'; pgrep -af 'Runner.Listener|run.sh' 2>/dev/null | head -5; "
    "echo '---RUNNER_FILES---'; ls -1a {runner_dir} 2>/dev/null | head -20; "
    "echo '---BRAIN---'; pgrep -af 'uvicorn|dreamosd|dreamos-brain' 2>/dev/null | head -5; "
    "echo '---SYSTEMD---'; systemctl is-active dreamos-brain 2>/dev/null; "
    "echo '---REPOS---'; ls -1 ~/projects 2>/dev/null | head -20; "
    "echo '---UPTIME---'; uptime -p 2>/dev/null"
)


def ssh_argv(config: OperatorConfig, command: str) -> list[str]:
    """Canonical Dream.OS SSH invocation."""
    vps = config.vps
    identity = str(Path(str(vps.get("identity_file", ""))).expanduser())
    return [
        "ssh",
        "-i", identity,
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "ConnectTimeout=10",
        f"{vps.get('user')}@{vps.get('host')}",
        command,
    ]


def ssh_command_hint(config: OperatorConfig, command: str = "COMMAND") -> str:
    """Paste-ready SSH line for the receiving agent."""
    vps = config.vps
    return (
        "ssh \\\n"
        f"  -i \"{vps.get('identity_file')}\" \\\n"
        "  -o BatchMode=yes \\\n"
        "  -o IdentitiesOnly=yes \\\n"
        "  -o ConnectTimeout=10 \\\n"
        f"  {vps.get('user')}@{vps.get('host')} \\\n"
        f"  '{command}'" if command == "COMMAND" else f"  {shlex.quote(command)}"
    )


def _split_sections(out: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"HOSTNAME": []}
    current = "HOSTNAME"
    for line in out.splitlines():
        stripped = line.strip()
        if stripped.startswith("---") and stripped.endswith("---"):
            current = stripped.strip("-")
            sections[current] = []
            continue
        if stripped:
            sections.setdefault(current, []).append(stripped)
    return sections


def collect(config: OperatorConfig | None = None, *, timeout: int = 20) -> dict[str, Any]:
    """Live VPS state, or an explicit unreachable record."""
    config = config or OperatorConfig.load()
    vps = config.vps
    record: dict[str, Any] = {
        "host": vps.get("host"),
        "user": vps.get("user"),
        "runner_name": vps.get("runner_name"),
        "runner_dir": vps.get("runner_dir"),
        "runner_labels": vps.get("runner_labels", []),
        "reachable": False,
        "healthy": False,
        "reason": "",
    }

    identity = Path(str(vps.get("identity_file", ""))).expanduser()
    if not tool_available("ssh"):
        record["reason"] = "ssh client not available in this environment"
        return record
    if not identity.exists():
        record["reason"] = f"SSH identity not present: {identity}"
        return record

    probe = _PROBE.format(runner_dir=shlex.quote(str(vps.get("runner_dir"))))
    code, out, err = run(ssh_argv(config, probe), timeout=timeout)
    if code != 0:
        record["reason"] = err or f"ssh exited {code}"
        return record

    sections = _split_sections(out)
    runner_procs = sections.get("RUNNER_PROC", [])
    runner_files = sections.get("RUNNER_FILES", [])
    brain_procs = sections.get("BRAIN", [])
    record.update(
        {
            "reachable": True,
            "hostname": (sections.get("HOSTNAME") or ["unknown"])[0],
            "uptime": (sections.get("UPTIME") or [""])[0],
            "runner_alive": bool(runner_procs),
            "runner_processes": runner_procs,
            "runner_registration_files": [f for f in runner_files if f in {".runner", ".credentials", ".credentials_rsaparams", "run.sh", "config.sh"}],
            "runner_registered": ".runner" in runner_files,
            "daemon_alive": bool(brain_procs),
            "daemon_processes": brain_procs,
            "daemon_systemd": (sections.get("SYSTEMD") or ["unknown"])[0],
            "repo_checkouts": sections.get("REPOS", []),
        }
    )
    record["healthy"] = bool(record["runner_alive"] and record["runner_registered"])
    if not record["healthy"]:
        problems = []
        if not record["runner_alive"]:
            problems.append(f"runner {vps.get('runner_name')} process not running")
        if not record["runner_registered"]:
            problems.append("runner registration (.runner) missing")
        record["reason"] = "; ".join(problems)
    # The runner has been running under temporary nohup execution; a
    # reboot-persistent systemd unit is a separate, unclaimed lane.
    record["runner_persistence"] = (
        "systemd" if record.get("daemon_systemd") == "active" else "temporary_nohup_or_unknown"
    )
    return record
