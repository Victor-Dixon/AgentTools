"""Resolve onboarding/messaging CLI commands via DreamVault SSOT or V2 unified fallback."""

from __future__ import annotations

import os
from pathlib import Path


def dreamvault_root() -> Path:
    override = os.environ.get("DREAMVAULT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    for candidate in (Path("D:/DreamVault"), Path.home() / "projects" / "DreamVault"):
        if (candidate / "runtime/scripts/agent_messaging_send_001.py").is_file():
            return candidate.resolve()
    return Path("D:/DreamVault")


def v2_repo_root() -> Path:
    override = os.environ.get("AGENT_CELLPHONE_V2_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path("D:/Agent_Cellphone_V2_Repository")


def dreamvault_send_cli() -> Path:
    return dreamvault_root() / "runtime/scripts/agent_messaging_send_001.py"


def v2_unified_cli() -> Path:
    return v2_repo_root() / "messaging_cli_unified.py"


def _missing_ssot_error() -> FileNotFoundError:
    return FileNotFoundError(
        "No messaging SSOT found: need DreamVault runtime/scripts/agent_messaging_send_001.py "
        "or Agent_Cellphone_V2_Repository/messaging_cli_unified.py"
    )


def build_hard_onboard_cmd(agent_id: str, message: str) -> list[str]:
    send = dreamvault_send_cli()
    if send.is_file():
        return [
            "python",
            str(send),
            "--category",
            "s2a",
            "--agent",
            agent_id,
            "--s2a-variant",
            "onboarding",
            "--context",
            message,
            "--live",
        ]
    unified = v2_unified_cli()
    if unified.is_file():
        return ["python", str(unified), "--hard-onboard-lite", agent_id]
    raise _missing_ssot_error()


def build_soft_onboard_cmd(agent_id: str, message: str) -> list[str]:
    send = dreamvault_send_cli()
    if send.is_file():
        return [
            "python",
            str(send),
            "--category",
            "s2a",
            "--agent",
            agent_id,
            "--s2a-variant",
            "onboarding",
            "--context",
            message,
            "--live",
        ]
    unified = v2_unified_cli()
    if unified.is_file():
        return ["python", str(unified), "--soft-onboard-lite", agent_id]
    raise _missing_ssot_error()


def live_injection_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("ALLOW_LIVE_CURSOR_INJECTION", "1")
    return env
