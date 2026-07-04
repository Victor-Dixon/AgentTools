#!/usr/bin/env python3
"""Guarded VPS deploy bridge for Dream.OS agents.

Agents submit deploy request JSON artifacts. An operator-controlled local runner
validates safety rules and either prints planned commands (dry-run) or executes
approved deploys when DREAMOS_DEPLOY_MODE=execute and dry_run is false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRIDGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BRIDGE_DIR.parent.parent
SCHEMA_PATH = BRIDGE_DIR / "deploy_request.schema.json"
REPORTS_DIR = REPO_ROOT / "reports" / "vps_deploy_bridge"

APPROVED_TARGET_PREFIXES = (
    "/opt/dreamos/",
    "/var/www/dreamos-sites/",
    "/tmp/dreamos-deploy/",
)

BLOCKED_TARGET_PREFIXES = (
    "/root/.ssh",
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/var/lib",
    "/home",
)

BLOCKED_COMMAND_PATTERNS = (
    r"rm\s+-rf\s+/",
    r"\bmkfs\b",
    r"dd\s+if=",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\buserdel\b",
    r"\bpasswd\b",
    r"curl\s+[^|]*\|\s*sh",
    r"wget\s+[^|]*\|\s*sh",
)

ALLOWED_SERVICES = frozenset(
    {"swarm-commander", "dreamos-brain", "dreamos-dashboard", "nginx"}
)

VALID_ACTIONS = frozenset(
    {
        "upload_file",
        "upload_dir",
        "run_command",
        "restart_service",
        "healthcheck",
    }
)

VERIFY_DRY_RUN = "VERIFY=PASS_VPS_DEPLOY_BRIDGE_DRY_RUN"
VERIFY_EXECUTED = "VERIFY=PASS_VPS_DEPLOY_BRIDGE_EXECUTED"


class DeployBridgeError(Exception):
    """Validation or execution failure for deploy bridge."""


@dataclass
class DeployReport:
    request_id: str
    status: str
    mode: str
    agent_id: str
    action: str
    target_path: str
    planned_commands: list[str] = field(default_factory=list)
    executed: bool = False
    validation_errors: list[str] = field(default_factory=list)
    verify_line: str = ""
    created_at: str = field(default_factory=lambda: _utc_now())
    completed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_request(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_iso_datetime(value: str) -> bool:
    try:
        normalized = value.replace("Z", "+00:00")
        datetime.fromisoformat(normalized)
        return True
    except ValueError:
        return False


def validate_schema(request: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(request, dict):
        return ["request must be a JSON object"]

    allowed_keys = set(load_schema().get("properties", {}).keys())
    for key in request:
        if key not in allowed_keys:
            errors.append(f"unknown field: {key}")

    required = [
        "request_id",
        "agent_id",
        "repo",
        "source_path",
        "target_path",
        "action",
        "reason",
        "created_at",
        "dry_run",
    ]
    for key in required:
        if key not in request:
            errors.append(f"missing required field: {key}")

    request_id = request.get("request_id")
    if isinstance(request_id, str) and not re.fullmatch(r"[a-zA-Z0-9._-]+", request_id):
        errors.append("request_id must match ^[a-zA-Z0-9._-]+$")

    action = request.get("action")
    if action is not None and action not in VALID_ACTIONS:
        errors.append(f"invalid action: {action}")

    created_at = request.get("created_at")
    if isinstance(created_at, str) and not _is_iso_datetime(created_at):
        errors.append("created_at must be ISO-8601 date-time")

    dry_run = request.get("dry_run")
    if dry_run is not None and not isinstance(dry_run, bool):
        errors.append("dry_run must be boolean")

    checksum = request.get("checksum_sha256")
    if isinstance(checksum, str) and not re.fullmatch(r"[a-f0-9]{64}", checksum):
        errors.append("checksum_sha256 must be 64 lowercase hex chars")

    if action == "run_command" and not request.get("command"):
        errors.append("command is required for run_command action")
    if action in {"restart_service", "healthcheck"} and not request.get("service_name"):
        errors.append(f"service_name is required for {action} action")

    return errors


def normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    if normalized != "/" and normalized.endswith("/"):
        normalized = normalized.rstrip("/")
    return normalized


def validate_target_path(target_path: str) -> list[str]:
    errors: list[str] = []
    path = normalize_path(target_path)

    for blocked in BLOCKED_TARGET_PREFIXES:
        if path == blocked or path.startswith(blocked + "/") or path.startswith(blocked):
            errors.append(f"blocked target path prefix: {blocked}")
            return errors

    if not any(path.startswith(prefix) for prefix in APPROVED_TARGET_PREFIXES):
        errors.append(
            "target_path must start with one of: "
            + ", ".join(APPROVED_TARGET_PREFIXES)
        )

    return errors


def validate_command(command: str) -> list[str]:
    errors: list[str] = []
    lowered = command.lower()
    for pattern in BLOCKED_COMMAND_PATTERNS:
        if re.search(pattern, lowered):
            errors.append(f"blocked command pattern matched: {pattern}")
    return errors


def validate_service_name(service_name: str) -> list[str]:
    if service_name not in ALLOWED_SERVICES:
        return [f"service not in allowlist: {service_name}"]
    return []


def validate_source_path(source_path: str, repo_root: Path) -> list[str]:
    errors: list[str] = []
    candidate = Path(source_path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    if not candidate.exists():
        errors.append(f"source_path does not exist: {candidate}")
    return errors


def validate_upload_constraints(request: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    action = request["action"]
    if action not in {"upload_file", "upload_dir"}:
        return errors

    source = request["source_path"]
    candidate = Path(source)
    if not candidate.is_absolute():
        candidate = repo_root / candidate

    if not candidate.exists():
        errors.append(f"source_path does not exist: {candidate}")
        return errors

    allowed_extensions = request.get("allowed_extensions")
    if allowed_extensions and candidate.is_file():
        if candidate.suffix not in allowed_extensions:
            errors.append(
                f"source extension {candidate.suffix!r} not in allowed_extensions"
            )

    max_bytes = request.get("max_bytes")
    if max_bytes is not None and candidate.is_file():
        size = candidate.stat().st_size
        if size > max_bytes:
            errors.append(f"source file exceeds max_bytes ({size} > {max_bytes})")

    checksum = request.get("checksum_sha256")
    if checksum and candidate.is_file():
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest != checksum:
            errors.append("checksum_sha256 mismatch for source file")

    return errors


def validate_request(request: dict[str, Any], repo_root: Path | None = None) -> list[str]:
    repo_root = repo_root or REPO_ROOT
    errors = validate_schema(request)
    if errors:
        return errors

    action = request["action"]
    target_path = request["target_path"]

    if action in {"upload_file", "upload_dir", "run_command"}:
        errors.extend(validate_target_path(target_path))

    if action == "run_command":
        errors.extend(validate_command(request["command"]))

    if action in {"restart_service", "healthcheck"}:
        errors.extend(validate_service_name(request["service_name"]))

    errors.extend(validate_upload_constraints(request, repo_root))
    return errors


def get_ssh_config() -> dict[str, str]:
    return {
        "host": os.environ.get("DREAMOS_VPS_HOST", ""),
        "user": os.environ.get("DREAMOS_VPS_USER", ""),
        "key": os.environ.get("DREAMOS_VPS_SSH_KEY", ""),
        "port": os.environ.get("DREAMOS_VPS_PORT", "22"),
    }


def _ssh_base(cfg: dict[str, str]) -> list[str]:
    cmd = [
        "ssh",
        "-p",
        cfg["port"],
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]
    if cfg["key"]:
        cmd.extend(["-i", cfg["key"]])
    cmd.append(f"{cfg['user']}@{cfg['host']}")
    return cmd


def _scp_base(cfg: dict[str, str]) -> list[str]:
    cmd = [
        "scp",
        "-P",
        cfg["port"],
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]
    if cfg["key"]:
        cmd.extend(["-i", cfg["key"]])
    return cmd


def build_plan(request: dict[str, Any], repo_root: Path | None = None) -> list[str]:
    repo_root = repo_root or REPO_ROOT
    cfg = get_ssh_config()
    action = request["action"]
    target_path = normalize_path(request["target_path"])
    planned: list[str] = []

    if action == "upload_file":
        source = Path(request["source_path"])
        if not source.is_absolute():
            source = repo_root / source
        remote = f"{cfg['user']}@{cfg['host']}:{target_path}"
        planned.append(" ".join(_scp_base(cfg) + [str(source), remote]))

    elif action == "upload_dir":
        source = Path(request["source_path"])
        if not source.is_absolute():
            source = repo_root / source
        remote = f"{cfg['user']}@{cfg['host']}:{target_path}/"
        planned.append(
            " ".join(
                [
                    "rsync",
                    "-avz",
                    "-e",
                    shlex.join(
                        [
                            "ssh",
                            "-p",
                            cfg["port"],
                            "-o",
                            "BatchMode=yes",
                            "-o",
                            "StrictHostKeyChecking=accept-new",
                        ]
                        + (["-i", cfg["key"]] if cfg["key"] else [])
                    ),
                    f"{source}/",
                    remote,
                ]
            )
        )

    elif action == "run_command":
        remote_cmd = request["command"]
        planned.append(" ".join(_ssh_base(cfg) + [remote_cmd]))

    elif action == "restart_service":
        service = request["service_name"]
        remote_cmd = f"sudo systemctl restart {shlex.quote(service)}"
        planned.append(" ".join(_ssh_base(cfg) + [remote_cmd]))

    elif action == "healthcheck":
        service = request["service_name"]
        remote_cmd = f"systemctl is-active --quiet {shlex.quote(service)}"
        planned.append(" ".join(_ssh_base(cfg) + [remote_cmd]))

    return planned


def should_execute(request: dict[str, Any]) -> bool:
    deploy_mode = os.environ.get("DREAMOS_DEPLOY_MODE", "dry_run")
    return deploy_mode == "execute" and request.get("dry_run") is False


def run_command_line(command_line: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command_line,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )


def execute_plan(planned: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for command_line in planned:
        proc = run_command_line(command_line)
        results.append(
            {
                "command": command_line,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
        if proc.returncode != 0:
            break
    return results


def write_report(report: DeployReport) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{report.request_id}.json"
    path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def process_request(
    request: dict[str, Any],
    *,
    repo_root: Path | None = None,
    runner: Any | None = None,
) -> DeployReport:
    repo_root = repo_root or REPO_ROOT
    request_id = request.get("request_id", "unknown")
    report = DeployReport(
        request_id=request_id,
        status="pending",
        mode="dry_run",
        agent_id=str(request.get("agent_id", "")),
        action=str(request.get("action", "")),
        target_path=str(request.get("target_path", "")),
    )

    validation_errors = validate_request(request, repo_root)
    if validation_errors:
        report.status = "validation_failed"
        report.validation_errors = validation_errors
        report.completed_at = _utc_now()
        write_report(report)
        raise DeployBridgeError("; ".join(validation_errors))

    planned = build_plan(request, repo_root)
    report.planned_commands = planned

    if should_execute(request):
        cfg = get_ssh_config()
        missing = [k for k, v in cfg.items() if k != "port" and not v]
        if missing:
            raise DeployBridgeError(
                "execute mode requires DREAMOS_VPS_HOST, DREAMOS_VPS_USER, "
                "and DREAMOS_VPS_SSH_KEY environment variables"
            )

        report.mode = "execute"
        execute_fn = runner or execute_plan
        results = execute_fn(planned)
        report.executed = True
        failed = [r for r in results if r.get("returncode", 1) != 0]
        if failed:
            report.status = "execution_failed"
            report.validation_errors = [
                f"command failed ({r['returncode']}): {r['command']}" for r in failed
            ]
            report.verify_line = ""
            report.completed_at = _utc_now()
            write_report(report)
            raise DeployBridgeError(report.validation_errors[0])

        report.status = "executed"
        report.verify_line = VERIFY_EXECUTED
    else:
        report.mode = "dry_run"
        report.status = "dry_run"
        report.executed = False
        report.verify_line = VERIFY_DRY_RUN

    report.completed_at = _utc_now()
    write_report(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dream.OS guarded VPS deploy bridge")
    parser.add_argument(
        "request_file",
        type=Path,
        help="Path to deploy request JSON file",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root for resolving relative source_path values",
    )
    args = parser.parse_args(argv)

    try:
        request = load_request(args.request_file)
        report = process_request(request, repo_root=args.repo_root)
    except DeployBridgeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 1

    for line in report.planned_commands:
        print(f"PLAN: {line}")

    if report.verify_line:
        print(report.verify_line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
