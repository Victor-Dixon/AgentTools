from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT_ROOT = Path("/home/dreamos/audits") / f"discord_logic_inventory_{STAMP}"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

SCAN_ROOTS = [
    Path("/home/dreamos"),
    Path("/opt/dreamos"),
]

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "audits",
}

TEXT_SUFFIXES = {
    ".py", ".sh", ".bash", ".ps1", ".js", ".ts", ".mjs", ".cjs",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".service", ".timer", ".env", ".md", ".txt",
}

DISCORD_PATTERNS = {
    "discord_sdk": re.compile(r"\bdiscord(?:\.py)?\b|from\s+discord|import\s+discord", re.I),
    "discord_webhook": re.compile(r"discord(?:app)?\.com/api/webhooks|webhook", re.I),
    "bot_token_reference": re.compile(r"(?:DISCORD|BOT).*TOKEN|TOKEN.*(?:DISCORD|BOT)", re.I),
    "discord_gateway": re.compile(r"gateway|on_ready|on_message|slash_command|commands\.Bot", re.I),
    "discord_rest": re.compile(r"discord(?:app)?\.com/api|/channels/|/guilds/", re.I),
    "discord_channel": re.compile(r"channel[_-]?id|guild[_-]?id", re.I),
}

GUI_PATTERNS = {
    "pyautogui": re.compile(r"\bpyautogui\b", re.I),
    "pynput": re.compile(r"\bpynput\b", re.I),
    "gui_display": re.compile(r"\b(?:tkinter|pyqt|pyside|wxpython|DISPLAY|xvfb|xdotool)\b", re.I),
    "screen_coordinates": re.compile(r"\b(?:click|moveTo|position)\s*\(\s*\d+\s*,\s*\d+", re.I),
}

SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b([A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|WEBHOOK_URL|API_KEY)[A-Z0-9_]*)"
    r"\s*[:=]\s*([^\s#]+)"
)

def run(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }

def redact(text: str) -> str:
    text = SECRET_ASSIGNMENT.sub(r"\1=<REDACTED>", text)
    text = re.sub(
        r"https://(?:canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9._-]+",
        "https://discord.com/api/webhooks/<REDACTED>",
        text,
        flags=re.I,
    )
    return text

def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIR_NAMES for part in path.parts)

def classify_role(text: str, path: Path) -> list[str]:
    roles: set[str] = set()
    lower = text.lower()
    name = path.name.lower()

    if "commands.bot" in lower or "discord.client" in lower or "on_message" in lower:
        roles.add("INBOUND_BOT")
    if "webhook" in lower:
        roles.add("WEBHOOK_PUBLISHER")
    if "send_message" in lower or "/channels/" in lower:
        roles.add("REST_PUBLISHER")
    if "scheduler" in lower or "cron" in lower or "schedule." in lower:
        roles.add("SCHEDULER")
    if "alert" in lower or "pager" in lower:
        roles.add("ALERT_ROUTER")
    if "embed" in lower:
        roles.add("EMBED_RENDERER")
    if "discord" in name and not roles:
        roles.add("DISCORD_SUPPORT")
    if any(pattern.search(text) for pattern in GUI_PATTERNS.values()):
        roles.add("GUI_AUTOMATION_VIOLATION")

    return sorted(roles)

def safe_preview(text: str, line_numbers: set[int], radius: int = 1) -> list[str]:
    lines = text.splitlines()
    selected: set[int] = set()
    for number in line_numbers:
        for candidate in range(max(1, number - radius), min(len(lines), number + radius) + 1):
            selected.add(candidate)

    output = []
    for number in sorted(selected):
        output.append(f"{number}: {redact(lines[number - 1])[:500]}")
    return output

records: list[dict[str, Any]] = []
errors: list[dict[str, str]] = []

for root in SCAN_ROOTS:
    if not root.exists():
        continue

    for path in root.rglob("*"):
        if not path.is_file() or is_skipped(path):
            continue

        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "Dockerfile", "crontab", "Procfile"
        }:
            continue

        try:
            if path.stat().st_size > 2_000_000:
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError) as exc:
            errors.append({"path": str(path), "error": str(exc)})
            continue

        discord_hits: dict[str, list[int]] = {}
        gui_hits: dict[str, list[int]] = {}

        for line_no, line in enumerate(raw.splitlines(), start=1):
            for name, pattern in DISCORD_PATTERNS.items():
                if pattern.search(line):
                    discord_hits.setdefault(name, []).append(line_no)

            for name, pattern in GUI_PATTERNS.items():
                if pattern.search(line):
                    gui_hits.setdefault(name, []).append(line_no)

        if not discord_hits and not gui_hits:
            continue

        all_lines = {
            line
            for numbers in [*discord_hits.values(), *gui_hits.values()]
            for line in numbers
        }

        records.append({
            "path": str(path),
            "size": path.stat().st_size,
            "sha256": hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest(),
            "discord_hits": discord_hits,
            "gui_hits": gui_hits,
            "roles": classify_role(raw, path),
            "preview": safe_preview(raw, all_lines),
        })

systemd = run([
    "systemctl",
    "list-unit-files",
    "--type=service",
    "--type=timer",
    "--no-pager",
    "--no-legend",
])

systemd_candidates = [
    line.split()[0]
    for line in systemd["stdout"].splitlines()
    if re.search(r"discord|dream|bot|report|commander|publisher", line, re.I)
]

systemd_details: list[dict[str, Any]] = []
for unit in systemd_candidates:
    show = run([
        "systemctl",
        "show",
        unit,
        "--no-pager",
        "--property=Id,Description,LoadState,ActiveState,SubState,FragmentPath,ExecStart,EnvironmentFiles",
    ])
    systemd_details.append({
        "unit": unit,
        "details": redact(show["stdout"]),
        "returncode": show["returncode"],
    })

user_cron = run(["crontab", "-l"])
root_cron = run(["sudo", "-n", "crontab", "-l"])

processes = run(["ps", "-eo", "pid,ppid,user,lstart,args", "--sort=pid"])
discord_processes = [
    redact(line)
    for line in processes["stdout"].splitlines()
    if re.search(r"discord|webhook|commander|publisher|morning.report|bot", line, re.I)
]

docker_files = [
    str(record["path"])
    for record in records
    if Path(record["path"]).name.lower() in {
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
        "dockerfile",
    }
]

env_files: list[str] = []
for root in SCAN_ROOTS:
    if not root.exists():
        continue
    for path in root.rglob("*"):
        if path.is_file() and not is_skipped(path):
            lowered = path.name.lower()
            if (
                lowered.endswith(".env")
                or "discord" in lowered
                or "webhook" in lowered
                or "token" in lowered
            ):
                env_files.append(str(path))

role_counts = Counter(
    role
    for record in records
    for role in record["roles"]
)

gui_violations = [
    record
    for record in records
    if record["gui_hits"]
]

report = {
    "schema": "dreamos.discord_logic_inventory.v1",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "host": os.uname().nodename,
    "scan_roots": [str(path) for path in SCAN_ROOTS],
    "records": records,
    "role_counts": dict(sorted(role_counts.items())),
    "gui_violations": gui_violations,
    "systemd_candidates": systemd_details,
    "user_crontab": redact(user_cron["stdout"]),
    "user_crontab_rc": user_cron["returncode"],
    "root_crontab": redact(root_cron["stdout"]),
    "root_crontab_rc": root_cron["returncode"],
    "discord_processes": discord_processes,
    "docker_files": sorted(set(docker_files)),
    "candidate_secret_or_config_files": sorted(set(env_files)),
    "read_errors": errors,
}

json_path = OUT_ROOT / "discord_logic_inventory.json"
json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "# VPS Discord Logic Inventory",
    "",
    f"- Generated: `{report['generated_at']}`",
    f"- Host: `{report['host']}`",
    f"- Matching files: **{len(records)}**",
    f"- GUI/PyAutoGUI candidates: **{len(gui_violations)}**",
    f"- Systemd candidates: **{len(systemd_details)}**",
    f"- Discord-related processes: **{len(discord_processes)}**",
    "",
    "## Role Counts",
    "",
]

for role, count in sorted(role_counts.items()):
    lines.append(f"- `{role}`: {count}")

lines.extend([
    "",
    "## File Inventory",
    "",
    "| Path | Roles | Discord signals | GUI signals |",
    "|---|---|---|---|",
])

for record in sorted(records, key=lambda item: item["path"]):
    lines.append(
        f"| `{record['path']}` "
        f"| {', '.join(record['roles']) or '-'} "
        f"| {', '.join(record['discord_hits']) or '-'} "
        f"| {', '.join(record['gui_hits']) or '-'} |"
    )

lines.extend([
    "",
    "## Systemd Candidates",
    "",
])

for item in systemd_details:
    lines.append(f"### `{item['unit']}`")
    lines.append("```text")
    lines.append(item["details"].strip())
    lines.append("```")

lines.extend([
    "",
    "## Candidate Secret/Configuration Files",
    "",
])

for path in sorted(set(env_files)):
    lines.append(f"- `{path}`")

lines.extend([
    "",
    "## Running Discord-Related Processes",
    "",
    "```text",
    *discord_processes,
    "```",
    "",
    "## GUI Automation Violations",
    "",
])

if gui_violations:
    for record in gui_violations:
        lines.append(
            f"- `{record['path']}` — {', '.join(record['gui_hits'])}"
        )
else:
    lines.append("- None detected.")

lines.extend([
    "",
    "## Next Classification",
    "",
    "Each matching file must be assigned exactly one disposition:",
    "",
    "- `KEEP_VPS_API_NATIVE`",
    "- `CONSOLIDATE_INTO_DISCORD_SERVICE`",
    "- `MOVE_TO_DESKTOP_ADAPTER`",
    "- `ARCHIVE_SUPERSEDED`",
    "- `SECRET_OR_CONFIG_ONLY`",
    "- `INVESTIGATE_UNKNOWN`",
])

md_path = OUT_ROOT / "discord_logic_inventory.md"
md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("VPS_DISCORD_LOGIC_AUDIT")
print(f"STATUS=PASS")
print(f"REPORT_DIR={OUT_ROOT}")
print(f"JSON={json_path}")
print(f"MARKDOWN={md_path}")
print(f"MATCHING_FILES={len(records)}")
print(f"GUI_VIOLATION_FILES={len(gui_violations)}")
print(f"SYSTEMD_CANDIDATES={len(systemd_details)}")
print(f"DISCORD_PROCESSES={len(discord_processes)}")
print("")
print("ROLE_COUNTS")
for role, count in sorted(role_counts.items()):
    print(f"{role}={count}")
print("")
print("TOP_FILES")
for record in sorted(
    records,
    key=lambda item: (
        "GUI_AUTOMATION_VIOLATION" not in item["roles"],
        item["path"],
    ),
)[:30]:
    print(
        f"FILE={record['path']} "
        f"ROLES={','.join(record['roles']) or 'UNKNOWN'}"
    )
