#!/usr/bin/env python3
"""Dream.OS Control Plane MCP server (stdio) for OpenAI Secure MCP Tunnel.

Exposes two governed namespaces only:
  - github_architect.*  → GitHub Architect execute_approved_branch_delete
  - discord.*           → AgentTools Discord Commander / tools.discord

Never exposes: shell execution, raw GitHub ref deletion APIs, Discord tokens,
webhook URLs, or API keys.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

UTC = timezone.utc

AGENT_TOOLS_ROOT = Path(__file__).resolve().parents[1]
GITHUB_ARCHITECT_ROOT = Path(
    os.environ.get("GITHUB_ARCHITECT_BOT_ROOT", r"D:\Projects\github-architect-bot")
)
DREAMVAULT_ROOT = Path(os.environ.get("DREAMVAULT_ROOT", r"D:\DreamVault"))

GAB_SCRIPTS = GITHUB_ARCHITECT_ROOT / "runtime" / "scripts"
GAB_LIB = GAB_SCRIPTS / "approved_branch_delete_lib.py"
GAB_REQUESTS = GITHUB_ARCHITECT_ROOT / "runtime" / "manifests" / "branch_delete_requests"
GAB_RECEIPTS = GITHUB_ARCHITECT_ROOT / "data" / "reports" / "github_architect" / "branch_deletes"
MASKZERO_REQUEST = (
    GAB_REQUESTS / "websites_maskzero_salvage_20260813.branch_delete.json"
)

# Import paths for reuse (no duplication of Discord/GitHub logic)
sys.path.insert(0, str(AGENT_TOOLS_ROOT / "src"))
sys.path.insert(0, str(AGENT_TOOLS_ROOT))
if GAB_SCRIPTS.is_dir():
    sys.path.insert(0, str(GAB_SCRIPTS))

SERVER_NAME = "dreamos-control-plane"
SERVER_VERSION = "0.5.0"
PROTOCOL_VERSION = "2024-11-05"

# OAuth scope + MCP tool annotation SSOT (ChatGPT connector discovery)
TOOL_AUTH: dict[str, dict[str, Any]] = {
    "inspect_branch_delete_request": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "dry_run_approved_branch_delete": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "execute_approved_branch_delete": {
        "scopes": ["repo.branch.delete"],
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": True,
            "openWorldHint": True,
            "idempotentHint": True,
        },
    },
    "get_branch_delete_receipt": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "list_bots": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "bot_status": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "list_channels": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "send_message": {
        "scopes": ["dreamos.write"],
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    },
    "send_embed": {
        "scopes": ["dreamos.write"],
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    },
    "send_agent_command": {
        "scopes": ["dreamos.write"],
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    },
    "fleet_status": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "task_status": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "collect_results": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "list_webhooks": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "health": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "recent_delivery_receipts": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "read_channels": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "read_messages": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": True},
    },
    "send_message_allowlisted": {
        "scopes": ["dreamos.write"],
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": False,
            "openWorldHint": True,
        },
    },
    "dispatch_agent_message": {
        "scopes": ["dreamos.write"],
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
    },
    "get_agent_status": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "get_task_receipt": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
    "connector_security_contract": {
        "scopes": ["dreamos.read"],
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    },
}

SECRET_PATTERNS = [
    re.compile(r"https://discord(?:app)?\.com/api/webhooks/[^\s\"']+", re.I),
    re.compile(r"(?i)(DISCORD_BOT_TOKEN|OPENAI_API_KEY|CONTROL_PLANE_API_KEY|OPENAI_ADMIN_KEY|GH_TOKEN|GITHUB_TOKEN)\s*[=:]\s*\S+"),
    re.compile(r"(?i)(sk-[A-Za-z0-9_\-]{20,})"),
    re.compile(r"(?i)(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _redact(value: Any) -> Any:
    """Recursively redact secrets from structures destined for MCP clients."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            key_l = str(key).lower()
            if any(
                s in key_l
                for s in (
                    "token",
                    "webhook_url",
                    "api_key",
                    "password",
                    "authorization",
                    "secret",
                )
            ):
                out[key] = "configured" if item else False
            else:
                out[key] = _redact(item)
        return out
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, str):
        text = value
        for pat in SECRET_PATTERNS:
            text = pat.sub("<redacted>", text)
        return text
    return value


def _configured(env_name: str) -> bool:
    return bool(os.environ.get(env_name))


def _jsonrpc_result(request_id: Any, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [{"type": "text", "text": json.dumps(_redact(payload), indent=2)}]
        },
    }


def _jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _safe_request_path(request_path: str) -> Path:
    path = Path(request_path)
    if not path.is_absolute():
        path = GITHUB_ARCHITECT_ROOT / path
    path = path.resolve()
    allowed = GAB_REQUESTS.resolve()
    if allowed not in path.parents and path.parent != allowed and path != allowed:
        # also allow exact files under allowed
        try:
            path.relative_to(allowed)
        except ValueError as exc:
            raise ValueError(
                "request_path must be inside GitHub Architect branch_delete_requests"
            ) from exc
    if not path.is_file():
        raise ValueError(f"request_path not found: {path}")
    if path.suffix != ".json":
        raise ValueError("request_path must be a .json manifest")
    return path


def _import_gab():
    if not GAB_LIB.is_file():
        raise RuntimeError(f"GitHub Architect lib missing: {GAB_LIB}")
    import approved_branch_delete_lib as gab  # type: ignore  # noqa: WPS433

    return gab


def _import_discord_outbound():
    from agent_tools.discord_commander.outbound_dry_run import (  # type: ignore  # noqa: WPS433
        outbound_dry_run,
    )
    from agent_tools.discord_commander.config import (  # type: ignore  # noqa: WPS433
        DiscordEnvConfig,
    )

    return outbound_dry_run, DiscordEnvConfig


# ---------------------------------------------------------------------------
# GitHub Architect tools
# ---------------------------------------------------------------------------


def inspect_branch_delete_request(request_path: str) -> dict[str, Any]:
    path = _safe_request_path(request_path)
    request = json.loads(path.read_text(encoding="utf-8"))
    authority = request.get("authority") if isinstance(request.get("authority"), dict) else {}
    return {
        "ok": True,
        "namespace": "github_architect",
        "tool": "inspect_branch_delete_request",
        "request_path": str(path),
        "action": request.get("action"),
        "repository": request.get("repository"),
        "branch": request.get("branch"),
        "expected_head": request.get("expected_head"),
        "status": request.get("status"),
        "dry_run": request.get("dry_run"),
        "authority": {
            "approved": bool(authority.get("approved")),
            "human_gate": authority.get("human_gate"),
            "approved_by": authority.get("approved_by"),
            "confirm_delete": bool(authority.get("confirm_delete")),
        },
        "guards": request.get("guards"),
    }


def dry_run_approved_branch_delete(request_path: str) -> dict[str, Any]:
    path = _safe_request_path(request_path)
    request = json.loads(path.read_text(encoding="utf-8"))
    request = dict(request)
    request["dry_run"] = True
    request["confirm_delete"] = False
    gab = _import_gab()
    receipt_dir = GAB_RECEIPTS
    receipt_dir.mkdir(parents=True, exist_ok=True)
    out = receipt_dir / f"mcp_dry_run_{_now().replace(':', '')}.json"
    receipt = gab.execute_approved_branch_delete(request, write_receipt_to=out)
    (receipt_dir / "branch_delete_latest.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "ok": receipt.get("status") in {"DRY_RUN_PASS", "PASS"},
        "namespace": "github_architect",
        "tool": "dry_run_approved_branch_delete",
        "delegated_to": str(GAB_LIB),
        "request_path": str(path),
        "status": receipt.get("status"),
        "reason": receipt.get("reason") or (receipt.get("validation") or {}).get("reason"),
        "receipt_path": str(out),
        "receipt": receipt,
    }


def execute_approved_branch_delete(
    request_path: str,
    confirm_delete: bool = False,
) -> dict[str, Any]:
    if not confirm_delete:
        return {
            "ok": False,
            "namespace": "github_architect",
            "tool": "execute_approved_branch_delete",
            "status": "BLOCKED",
            "reason": "AUTHORITY_MISSING",
            "error": "confirm_delete must be true; call dry_run_approved_branch_delete first",
        }
    path = _safe_request_path(request_path)
    request = json.loads(path.read_text(encoding="utf-8"))
    request = dict(request)
    request["dry_run"] = False
    request["confirm_delete"] = True
    authority = dict(request.get("authority") or {})
    if not authority.get("approved") and not request.get("approved_by") and not authority.get("approved_by"):
        return {
            "ok": False,
            "namespace": "github_architect",
            "tool": "execute_approved_branch_delete",
            "status": "BLOCKED",
            "reason": "AUTHORITY_MISSING",
            "error": "request.authority.approved / approved_by required for live delete",
        }
    gab = _import_gab()
    receipt_dir = GAB_RECEIPTS
    receipt_dir.mkdir(parents=True, exist_ok=True)
    out = receipt_dir / f"mcp_live_{_now().replace(':', '')}.json"
    receipt = gab.execute_approved_branch_delete(request, write_receipt_to=out)
    (receipt_dir / "branch_delete_latest.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "ok": receipt.get("status") == "PASS",
        "namespace": "github_architect",
        "tool": "execute_approved_branch_delete",
        "delegated_to": str(GAB_LIB),
        "request_path": str(path),
        "status": receipt.get("status"),
        "reason": receipt.get("reason") or (receipt.get("validation") or {}).get("reason"),
        "receipt_path": str(out),
        "receipt": receipt,
    }


def get_branch_delete_receipt(receipt_path: str = "") -> dict[str, Any]:
    path = Path(receipt_path) if receipt_path else GAB_RECEIPTS / "branch_delete_latest.json"
    if not path.is_absolute():
        path = GITHUB_ARCHITECT_ROOT / path
    path = path.resolve()
    allowed = GAB_RECEIPTS.resolve()
    try:
        path.relative_to(allowed)
    except ValueError:
        return {
            "ok": False,
            "error": "receipt_path must be under GitHub Architect branch_deletes reports",
        }
    if not path.is_file():
        return {"ok": False, "error": f"receipt not found: {path}"}
    receipt = json.loads(path.read_text(encoding="utf-8"))
    return {
        "ok": True,
        "namespace": "github_architect",
        "tool": "get_branch_delete_receipt",
        "receipt_path": str(path),
        "receipt": receipt,
    }


# ---------------------------------------------------------------------------
# Discord tools (reuse AgentTools)
# ---------------------------------------------------------------------------


def list_bots() -> dict[str, Any]:
    _, DiscordEnvConfig = _import_discord_outbound()
    cfg = DiscordEnvConfig.from_environ()
    bots = [
        {
            "bot_id": "commander",
            "mode": "inbound",
            "configured": _configured("DISCORD_BOT_TOKEN"),
            "guild_configured": _configured("DISCORD_GUILD_ID"),
        }
    ]
    for i in range(1, 9):
        env = f"DISCORD_WEBHOOK_AGENT_{i}"
        bots.append(
            {
                "bot_id": f"Agent-{i}",
                "mode": "outbound",
                "configured": _configured(env),
            }
        )
    bots.append(
        {
            "bot_id": "fleet_default_webhook",
            "mode": "outbound",
            "configured": bool(cfg.webhook_url),
        }
    )
    bots.append(
        {
            "bot_id": "trading",
            "mode": "outbound",
            "configured": _configured("DISCORD_TRADING_WEBHOOK_URL"),
        }
    )
    return {
        "ok": True,
        "namespace": "discord",
        "tool": "list_bots",
        "bots": bots,
        "reused": "agent_tools.discord_commander.config.DiscordEnvConfig",
    }


def bot_status(agent: str = "") -> dict[str, Any]:
    outbound_dry_run, DiscordEnvConfig = _import_discord_outbound()
    cfg = DiscordEnvConfig.from_environ()
    dry = outbound_dry_run()
    missing = cfg.missing_required()
    return {
        "ok": bool(dry.success),
        "namespace": "discord",
        "tool": "bot_status",
        "agent": agent or None,
        "inbound_bot_configured": bool(cfg.bot_token),
        "guild_configured": bool(cfg.guild_id),
        "outbound_dry_run": {
            "success": dry.success,
            "message": dry.message,
            "error_code": dry.error_code,
            # checks include masked secrets only from commander
            "checks": _redact(dry.data.get("checks") if dry.data else []),
        },
        "missing_required_env_names": missing,
        "reused": "agent_tools.discord_commander.outbound_dry_run",
    }


def list_channels() -> dict[str, Any]:
    channel_keys = sorted(
        k for k in os.environ if k.startswith("DISCORD_") and k.endswith("_CHANNEL_ID")
    )
    config_path = DREAMVAULT_ROOT / "runtime" / "config" / "discord_router_channels.json"
    config_channels: list[dict[str, Any]] = []
    if config_path.is_file():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if isinstance(config, dict):
            raw_channels = config.get("channels")
            if isinstance(raw_channels, dict):
                config_channels = [
                    {"name": str(name), "configured": bool(value)}
                    for name, value in sorted(raw_channels.items())
                ]
    return {
        "ok": True,
        "namespace": "discord",
        "tool": "list_channels",
        "configured": bool(channel_keys or config_channels),
        "env_channel_count": len(channel_keys),
        "config_present": config_path.is_file(),
        "channels": config_channels,
        "redaction_applied": True,
    }


def list_webhooks() -> dict[str, Any]:
    keys = sorted(k for k in os.environ if k.startswith("DISCORD") and "WEBHOOK" in k)
    return {
        "ok": True,
        "namespace": "discord",
        "tool": "list_webhooks",
        "configured": bool(keys),
        "webhook_count": len(keys),
        "redaction_applied": True,
        "note": "URLs and credential names are never returned.",
    }


def health() -> dict[str, Any]:
    gab_ok = GAB_LIB.is_file()
    discord_ok = False
    outbound = None
    try:
        outbound_dry_run, _ = _import_discord_outbound()
        result = outbound_dry_run()
        discord_ok = True
        outbound = {
            "success": result.success,
            "message": result.message,
            "error_code": result.error_code,
        }
    except Exception as exc:  # noqa: BLE001
        outbound = {"success": False, "error": str(exc)}

    return {
        "ok": gab_ok and discord_ok,
        "namespace": "discord",
        "tool": "health",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "generated_at": _now(),
        "github_architect": {
            "root": str(GITHUB_ARCHITECT_ROOT),
            "root_exists": GITHUB_ARCHITECT_ROOT.is_dir(),
            "lib_exists": gab_ok,
            "maskzero_request_exists": MASKZERO_REQUEST.is_file(),
        },
        "discord": {
            "agent_tools_root": str(AGENT_TOOLS_ROOT),
            "import_ok": discord_ok,
            "outbound_dry_run": outbound,
            "bot_token_configured": _configured("DISCORD_BOT_TOKEN"),
            "webhook_configured": _configured("DISCORD_WEBHOOK_URL")
            or any(_configured(f"DISCORD_WEBHOOK_AGENT_{i}") for i in range(1, 9)),
        },
        "forbidden_surfaces": [
            "shell_execution",
            "raw_github_ref_delete_api",
            "raw_tokens",
            "webhook_urls",
        ],
    }


def send_message(
    agent: str,
    title: str,
    message: str,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Governed Discord send via tools.discord.webhook_sender (content only; URL from env)."""
    if dry_run:
        outbound_dry_run, DiscordEnvConfig = _import_discord_outbound()
        cfg = DiscordEnvConfig.from_environ()
        target_configured = bool(cfg.webhook_for_agent(agent) or cfg.webhook_url)
        dry = outbound_dry_run()
        return {
            "ok": bool(dry.success and target_configured),
            "namespace": "discord",
            "tool": "send_message",
            "dry_run": True,
            "agent": agent,
            "title": title,
            "message_chars": len(message or ""),
            "target_configured": target_configured,
            "outbound_dry_run_ok": dry.success,
            "receipt": {
                "action": "DISCORD_SEND_MESSAGE",
                "mode": "dry_run",
                "generated_at": _now(),
            },
            "reused": "agent_tools.discord_commander.outbound_dry_run",
        }

    # Live: reuse tools.discord.webhook_sender without echoing URL
    sys.path.insert(0, str(AGENT_TOOLS_ROOT / "tools"))
    from discord.webhook_sender import send_payload  # type: ignore  # noqa: WPS433
    from agent_tools.discord_commander.config import DiscordEnvConfig  # type: ignore

    cfg = DiscordEnvConfig.from_environ()
    url = cfg.webhook_for_agent(agent)
    if not url:
        return {
            "ok": False,
            "namespace": "discord",
            "tool": "send_message",
            "status": "BLOCKED",
            "reason": "WEBHOOK_NOT_CONFIGURED",
            "agent": agent,
        }
    payload = {
        "content": f"**{title}**\n{message}" if title else message,
        "username": "Dream.OS Control Plane",
    }
    result = send_payload(payload, webhook_url=url)
    return {
        "ok": bool(result.ok),
        "namespace": "discord",
        "tool": "send_message",
        "dry_run": False,
        "agent": agent,
        "status_code": result.status_code,
        "message": result.message if result.ok else "send_failed",
        "receipt": {
            "action": "DISCORD_SEND_MESSAGE",
            "mode": "live",
            "generated_at": _now(),
            "ok": result.ok,
        },
        "reused": "tools.discord.webhook_sender.send_payload",
        "redaction_applied": True,
    }


def send_embed(
    agent: str,
    title: str,
    description: str,
    dry_run: bool = True,
) -> dict[str, Any]:
    if dry_run:
        return send_message(agent=agent, title=title, message=description, dry_run=True)

    sys.path.insert(0, str(AGENT_TOOLS_ROOT / "tools"))
    from discord.webhook_sender import send_payload  # type: ignore
    from agent_tools.discord_commander.config import DiscordEnvConfig  # type: ignore

    cfg = DiscordEnvConfig.from_environ()
    url = cfg.webhook_for_agent(agent)
    if not url:
        return {
            "ok": False,
            "namespace": "discord",
            "tool": "send_embed",
            "status": "BLOCKED",
            "reason": "WEBHOOK_NOT_CONFIGURED",
        }
    payload = {
        "embeds": [{"title": title, "description": description}],
        "username": "Dream.OS Control Plane",
    }
    result = send_payload(payload, webhook_url=url)
    return {
        "ok": bool(result.ok),
        "namespace": "discord",
        "tool": "send_embed",
        "dry_run": False,
        "agent": agent,
        "status_code": result.status_code,
        "receipt": {
            "action": "DISCORD_SEND_EMBED",
            "mode": "live",
            "generated_at": _now(),
            "ok": result.ok,
        },
        "reused": "tools.discord.webhook_sender.send_payload",
        "redaction_applied": True,
    }


def _import_thea_a2a_bridge():
    """Reuse DreamVault THEA-A2A-BRIDGE (canonical message bus) — no parallel stack."""
    dv_src = DREAMVAULT_ROOT / "src"
    if dv_src.is_dir() and str(dv_src) not in sys.path:
        sys.path.insert(0, str(dv_src))
    from dreamvault.control_plane import thea_a2a_bridge as bridge  # type: ignore  # noqa: WPS433

    return bridge


def fleet_status() -> dict[str, Any]:
    bridge = _import_thea_a2a_bridge()
    out = bridge.fleet_status(repo_root=DREAMVAULT_ROOT)
    out["namespace"] = "dreamos_a2a"
    out["tool"] = "fleet_status"
    out["reused"] = "dreamvault.control_plane.thea_a2a_bridge.fleet_status"
    return out


def task_status(correlation_id: str) -> dict[str, Any]:
    bridge = _import_thea_a2a_bridge()
    out = bridge.task_status(correlation_id, repo_root=DREAMVAULT_ROOT)
    out["namespace"] = "dreamos_a2a"
    out["tool"] = "task_status"
    out["reused"] = "dreamvault.control_plane.thea_a2a_bridge.task_status"
    return out


def collect_results(correlation_id: str) -> dict[str, Any]:
    bridge = _import_thea_a2a_bridge()
    out = bridge.collect_results(correlation_id, repo_root=DREAMVAULT_ROOT)
    out["namespace"] = "dreamos_a2a"
    out["tool"] = "collect_results"
    out["reused"] = "dreamvault.control_plane.thea_a2a_bridge.collect_results"
    return out


def send_agent_command(
    agent: str,
    command: str,
    dry_run: bool = True,
    correlation_id: str | None = None,
    transport: str = "a2a",
) -> dict[str, Any]:
    """Route agent commands.

    Default transport=a2a uses DreamVault canonical message bus (THEA-A2A-BRIDGE-001).
    transport=discord keeps legacy Discord webhook path.
    """
    mode = str(transport or "a2a").strip().lower()
    if mode == "discord":
        return send_message(
            agent=agent,
            title="Dream.OS Agent Command",
            message=command,
            dry_run=dry_run,
        )
    bridge = _import_thea_a2a_bridge()
    out = bridge.send_agent_command(
        target=agent,
        message=command,
        correlation_id=correlation_id,
        dry_run=dry_run,
        live_dispatch=False,
        repo_root=DREAMVAULT_ROOT,
    )
    out["namespace"] = "dreamos_a2a"
    out["tool"] = "send_agent_command"
    out["reused"] = "dreamvault.message_bus.dispatcher.enqueue_category_message"
    return out


def recent_delivery_receipts(limit: int = 10) -> dict[str, Any]:
    roots = [
        GAB_RECEIPTS,
        DREAMVAULT_ROOT / "data" / "reports" / "discord",
        DREAMVAULT_ROOT / "agent_workspaces",
    ]
    paths: list[Path] = []
    for root in roots:
        if root.is_dir():
            paths.extend(root.rglob("*receipt*.json"))
            paths.extend(root.glob("*.json"))
    # Prefer GAB branch deletes + discord reports
    unique = {p.resolve() for p in paths if p.is_file()}
    recent = sorted(unique, key=lambda p: p.stat().st_mtime, reverse=True)[
        : max(1, min(int(limit or 10), 50))
    ]
    return {
        "ok": True,
        "namespace": "discord",
        "tool": "recent_delivery_receipts",
        "limit": limit,
        "receipts": [
            {
                "path": str(p),
                "modified": datetime.fromtimestamp(p.stat().st_mtime, UTC).isoformat(),
            }
            for p in recent
        ],
    }


def _import_discord_architect_connector():
    from agent_tools.discord_architect_connector import (  # type: ignore  # noqa: WPS433
        read_channels as connector_read_channels,
        read_messages as connector_read_messages,
        security_contract as connector_security_contract,
        send_message_allowlisted as connector_send_message_allowlisted,
    )

    return (
        connector_read_channels,
        connector_read_messages,
        connector_send_message_allowlisted,
        connector_security_contract,
    )


def read_channels() -> dict[str, Any]:
    """Discord Architect Connector: router allowlist channel inventory."""
    connector_read_channels, _, _, _ = _import_discord_architect_connector()
    out = connector_read_channels()
    out["reused"] = "agent_tools.discord_architect_connector.read_channels"
    return out


def read_messages(
    route_key: str = "smoke_test",
    limit: int = 10,
    live: bool = False,
) -> dict[str, Any]:
    """Allowlisted channel message read (dry_run/live=false default)."""
    _, connector_read_messages, _, _ = _import_discord_architect_connector()
    out = connector_read_messages(route_key=route_key, limit=limit, live=live)
    out["reused"] = "agent_tools.discord_architect_connector.read_messages"
    return out


def send_message_allowlisted(
    content: str,
    route_key: str = "smoke_test",
    dry_run: bool = True,
    human_approved: bool = False,
) -> dict[str, Any]:
    """Allowlisted smoke-channel send; dry_run default; live needs server-side env gate."""
    _, _, connector_send, _ = _import_discord_architect_connector()
    out = connector_send(
        content,
        route_key=route_key,
        dry_run=dry_run,
        human_approved=human_approved,
    )
    out["reused"] = "agent_tools.discord_architect_connector.send_message_allowlisted"
    return out


def dispatch_agent_message(
    target: str,
    message: str,
    correlation_id: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Alias → existing send_agent_command (A2A bus; preserves durable IDs)."""
    out = send_agent_command(
        target=target,
        message=message,
        correlation_id=correlation_id,
        dry_run=dry_run,
    )
    out["tool"] = "dispatch_agent_message"
    out["alias_of"] = "send_agent_command"
    return out


def get_agent_status() -> dict[str, Any]:
    """Alias → fleet_status (status.json inventory)."""
    out = fleet_status()
    out["tool"] = "get_agent_status"
    out["alias_of"] = "fleet_status"
    return out


def get_task_receipt(correlation_id: str) -> dict[str, Any]:
    """Alias → task_status + collect_results by correlation_id."""
    status = task_status(correlation_id)
    collected = collect_results(correlation_id)
    return {
        "ok": bool(status.get("ok", True) or collected.get("ok")),
        "namespace": "discord",
        "tool": "get_task_receipt",
        "alias_of": ["task_status", "collect_results"],
        "correlation_id": correlation_id,
        "task_status": status,
        "collect_results": collected,
        "generated_at": _now(),
    }


def connector_security_contract() -> dict[str, Any]:
    _, _, _, contract = _import_discord_architect_connector()
    out = contract()
    out["reused"] = "agent_tools.discord_architect_connector.security_contract"
    return out


# ---------------------------------------------------------------------------
# MCP protocol
# ---------------------------------------------------------------------------

TOOLS: dict[str, Callable[..., dict[str, Any]]] = {
    "inspect_branch_delete_request": inspect_branch_delete_request,
    "dry_run_approved_branch_delete": dry_run_approved_branch_delete,
    "execute_approved_branch_delete": execute_approved_branch_delete,
    "get_branch_delete_receipt": get_branch_delete_receipt,
    "list_bots": list_bots,
    "bot_status": bot_status,
    "list_channels": list_channels,
    "send_message": send_message,
    "send_embed": send_embed,
    "send_agent_command": send_agent_command,
    "fleet_status": fleet_status,
    "task_status": task_status,
    "collect_results": collect_results,
    "list_webhooks": list_webhooks,
    "health": health,
    "recent_delivery_receipts": recent_delivery_receipts,
    "read_channels": read_channels,
    "read_messages": read_messages,
    "send_message_allowlisted": send_message_allowlisted,
    "dispatch_agent_message": dispatch_agent_message,
    "get_agent_status": get_agent_status,
    "get_task_receipt": get_task_receipt,
    "connector_security_contract": connector_security_contract,
}

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "inspect_branch_delete_request": {
        "description": "Inspect a governed GitHub Architect DELETE_BRANCH request manifest.",
        "inputSchema": {
            "type": "object",
            "properties": {"request_path": {"type": "string"}},
            "required": ["request_path"],
        },
    },
    "dry_run_approved_branch_delete": {
        "description": "Revalidate branch-delete guards via execute_approved_branch_delete (dry-run).",
        "inputSchema": {
            "type": "object",
            "properties": {"request_path": {"type": "string"}},
            "required": ["request_path"],
        },
    },
    "execute_approved_branch_delete": {
        "description": "Live governed branch delete via GitHub Architect (requires confirm_delete + authority).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "request_path": {"type": "string"},
                "confirm_delete": {"type": "boolean", "default": False},
            },
            "required": ["request_path", "confirm_delete"],
        },
    },
    "get_branch_delete_receipt": {
        "description": "Read a GitHub Architect BRANCH_DELETE receipt.",
        "inputSchema": {
            "type": "object",
            "properties": {"receipt_path": {"type": "string"}},
        },
    },
    "list_bots": {
        "description": "List Discord bot identities (configured: true|false only).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "bot_status": {
        "description": "Discord Commander / outbound configuration status (secrets redacted).",
        "inputSchema": {
            "type": "object",
            "properties": {"agent": {"type": "string"}},
        },
    },
    "list_channels": {
        "description": "List configured Discord channel metadata (no secrets).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "send_message": {
        "description": "Send or dry-run a Discord message via AgentTools webhook sender.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "title": {"type": "string"},
                "message": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["agent", "title", "message"],
        },
    },
    "send_embed": {
        "description": "Send or dry-run a Discord embed via AgentTools webhook sender.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["agent", "title", "description"],
        },
    },
    "send_agent_command": {
        "description": (
            "Send agent command via DreamVault A2A message bus (default) or Discord webhook. "
            "Pass correlation_id to track task_status/collect_results."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "command": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
                "correlation_id": {"type": "string"},
                "transport": {
                    "type": "string",
                    "enum": ["a2a", "discord"],
                    "default": "a2a",
                },
            },
            "required": ["agent", "command"],
        },
    },
    "fleet_status": {
        "description": "Read-only fleet snapshot from DreamVault agent status.json files.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "task_status": {
        "description": "Lookup THEA-A2A-BRIDGE command status by correlation_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"correlation_id": {"type": "string"}},
            "required": ["correlation_id"],
        },
    },
    "collect_results": {
        "description": "Collect delivery ACK / result for a correlation_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"correlation_id": {"type": "string"}},
            "required": ["correlation_id"],
        },
    },
    "list_webhooks": {
        "description": "Report Discord webhook configuration status without credential names or URLs.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "health": {
        "description": "Control-plane health (GAB lib + Discord reuse).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "recent_delivery_receipts": {
        "description": "List recent delivery/branch-delete receipt paths.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 10}},
        },
    },
    "read_channels": {
        "description": "Discord Architect Connector: list router channels + connector allowlist (no secrets).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "read_messages": {
        "description": "Read messages from an allowlisted channel only (live=false dry-run default).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "route_key": {"type": "string", "default": "smoke_test"},
                "limit": {"type": "integer", "default": 10},
                "live": {"type": "boolean", "default": False},
            },
        },
    },
    "send_message_allowlisted": {
        "description": "Send to connector-allowlisted channel only; dry_run default. Client human_approved is not authorization; live needs server-side DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "route_key": {"type": "string", "default": "smoke_test"},
                "dry_run": {"type": "boolean", "default": True},
                "human_approved": {"type": "boolean", "default": False},
            },
            "required": ["content"],
        },
    },
    "dispatch_agent_message": {
        "description": "Alias of send_agent_command — durable A2A bus dispatch with correlation IDs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string"},
                "message": {"type": "string"},
                "correlation_id": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["target", "message"],
        },
    },
    "get_agent_status": {
        "description": "Alias of fleet_status — Agent-N status.json inventory.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "get_task_receipt": {
        "description": "Alias wrapping task_status + collect_results by correlation_id.",
        "inputSchema": {
            "type": "object",
            "properties": {"correlation_id": {"type": "string"}},
            "required": ["correlation_id"],
        },
    },
    "connector_security_contract": {
        "description": "Discord Architect Connector security defaults and forbidden actions.",
        "inputSchema": {"type": "object", "properties": {}},
    },
}


def build_tool_descriptor(name: str, schema: dict[str, Any]) -> dict[str, Any]:
    """Merge MCP tool schema with OAuth securitySchemes and annotations."""
    auth = TOOL_AUTH.get(name, {"scopes": ["dreamos.read"], "annotations": {"readOnlyHint": True}})
    scopes = auth.get("scopes") or ["dreamos.read"]
    descriptor: dict[str, Any] = {
        "name": name,
        **schema,
        "securitySchemes": [{"type": "oauth2", "scopes": scopes}],
    }
    annotations = auth.get("annotations")
    if annotations:
        descriptor["annotations"] = dict(annotations)
    return descriptor


def build_tools_list() -> list[dict[str, Any]]:
    return [
        build_tool_descriptor(name, TOOL_SCHEMAS[name])
        for name in sorted(TOOL_SCHEMAS)
    ]


def required_scopes_for_tool(name: str) -> list[str]:
    auth = TOOL_AUTH.get(name, {})
    return list(auth.get("scopes") or ["dreamos.read"])


def handle(
    request: dict[str, Any],
    *,
    granted_scopes: list[str] | None = None,
    enforce_oauth: bool = False,
) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": build_tools_list()},
        }
    if method == "tools/call":
        params = request.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name not in TOOLS:
            return _jsonrpc_error(request_id, -32601, f"Unknown tool: {name}")
        if enforce_oauth:
            from dreamos_control_plane_oauth import scopes_allow

            required = required_scopes_for_tool(str(name))
            if not scopes_allow(required, granted_scopes):
                return _jsonrpc_error(
                    request_id,
                    -32001,
                    f"Insufficient OAuth scope for {name}; required: {required}",
                )
        try:
            result = TOOLS[name](**arguments)
        except Exception as exc:  # noqa: BLE001
            result = {
                "ok": False,
                "tool": name,
                "status": "BLOCKED",
                "error": str(exc),
            }
        return _jsonrpc_result(request_id, result)
    return _jsonrpc_error(request_id, -32601, f"Unknown method: {method}")


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = handle(request)
        except Exception as exc:  # noqa: BLE001
            response = _jsonrpc_error(None, -32700, str(exc))
        if response is not None:
            print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
