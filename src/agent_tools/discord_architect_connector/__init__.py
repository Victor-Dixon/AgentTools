#!/usr/bin/env python3
"""Discord Architect Connector — allowlisted ChatGPT MCP helpers.

Reuses DreamVault router config + existing control-plane/A2A surfaces.
Default: read-only / dry_run. Live send only to connector_allowlist channels.
Tokens stay server-side (env); never returned to clients.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DREAMVAULT_ROOT = Path(os.environ.get("DREAMVAULT_ROOT", r"D:\DreamVault"))
ROUTER_CONFIG = DREAMVAULT_ROOT / "runtime" / "config" / "discord_router_channels.json"
DEFAULT_ALLOWLIST = ("smoke_test",)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_router_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or ROUTER_CONFIG
    if not cfg_path.is_file():
        return {"routes": {}, "connector_allowlist": list(DEFAULT_ALLOWLIST)}
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {"routes": {}, "connector_allowlist": list(DEFAULT_ALLOWLIST)}
    if "connector_allowlist" not in data:
        data["connector_allowlist"] = list(DEFAULT_ALLOWLIST)
    return data


def allowlist_route_keys(config: dict[str, Any] | None = None) -> list[str]:
    cfg = config or load_router_config()
    raw = cfg.get("connector_allowlist") or list(DEFAULT_ALLOWLIST)
    return [str(x) for x in raw]


def resolve_route(route_key: str, config: dict[str, Any] | None = None) -> dict[str, Any] | None:
    cfg = config or load_router_config()
    routes = cfg.get("routes") if isinstance(cfg.get("routes"), dict) else {}
    route = routes.get(route_key)
    if not isinstance(route, dict):
        return None
    return {
        "route_key": route_key,
        "channel_name": route.get("channel_name"),
        "channel_id": str(route.get("channel_id") or ""),
        "description": route.get("description"),
        "allowlisted": route_key in allowlist_route_keys(cfg),
    }


def read_channels(*, include_non_allowlisted_metadata: bool = True) -> dict[str, Any]:
    """Config-backed channel inventory (no secrets). Optional REST probe later."""
    cfg = load_router_config()
    routes = cfg.get("routes") if isinstance(cfg.get("routes"), dict) else {}
    allow = set(allowlist_route_keys(cfg))
    channels: list[dict[str, Any]] = []
    for key, meta in sorted(routes.items()):
        if not isinstance(meta, dict):
            continue
        entry = {
            "route_key": key,
            "channel_name": meta.get("channel_name"),
            "channel_id": str(meta.get("channel_id") or ""),
            "description": meta.get("description"),
            "allowlisted_for_connector": key in allow,
        }
        if include_non_allowlisted_metadata or key in allow:
            channels.append(entry)
    return {
        "ok": True,
        "namespace": "discord_architect_connector",
        "tool": "read_channels",
        "mode": "config_router",
        "config_path": str(ROUTER_CONFIG),
        "connector_allowlist": sorted(allow),
        "channel_count": len(channels),
        "channels": channels,
        "bot_token_configured": bool(os.environ.get("DISCORD_BOT_TOKEN")),
        "note": "Channel IDs from DreamVault router SSOT; tokens never returned.",
        "generated_at": _now(),
    }


def read_messages(
    route_key: str = "smoke_test",
    limit: int = 10,
    *,
    live: bool = False,
) -> dict[str, Any]:
    """Read recent messages from an allowlisted channel only."""
    cfg = load_router_config()
    allow = allowlist_route_keys(cfg)
    if route_key not in allow:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "read_messages",
            "status": "BLOCKED",
            "reason": "ROUTE_NOT_ALLOWLISTED",
            "route_key": route_key,
            "connector_allowlist": allow,
        }
    route = resolve_route(route_key, cfg)
    if not route or not route.get("channel_id"):
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "read_messages",
            "status": "BLOCKED",
            "reason": "ROUTE_MISSING",
            "route_key": route_key,
        }
    limit = max(1, min(int(limit or 10), 50))
    if not live:
        return {
            "ok": True,
            "namespace": "discord_architect_connector",
            "tool": "read_messages",
            "dry_run": True,
            "route": route,
            "limit": limit,
            "messages": [],
            "note": "dry_run default — set live=true with server-side DISCORD_BOT_TOKEN to fetch",
            "generated_at": _now(),
        }
    token = os.environ.get("DISCORD_BOT_TOKEN") or ""
    if not token:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "read_messages",
            "status": "BLOCKED",
            "reason": "BOT_TOKEN_MISSING",
            "route": route,
        }
    url = (
        f"https://discord.com/api/v10/channels/{route['channel_id']}/messages"
        f"?limit={limit}"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "DreamOS-DiscordArchitectConnector/0.1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "read_messages",
            "status": "HTTP_ERROR",
            "http_status": exc.code,
            "route": route,
            "error": "discord_api_http_error",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "read_messages",
            "status": "ERROR",
            "route": route,
            "error": type(exc).__name__,
        }
    messages = []
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            author = item.get("author") if isinstance(item.get("author"), dict) else {}
            messages.append(
                {
                    "id": item.get("id"),
                    "content_chars": len(str(item.get("content") or "")),
                    "content_preview": str(item.get("content") or "")[:240],
                    "author_id": author.get("id"),
                    "author_username": author.get("username"),
                    "timestamp": item.get("timestamp"),
                }
            )
    return {
        "ok": True,
        "namespace": "discord_architect_connector",
        "tool": "read_messages",
        "dry_run": False,
        "route": route,
        "limit": limit,
        "message_count": len(messages),
        "messages": messages,
        "generated_at": _now(),
    }


def send_message_allowlisted(
    content: str,
    route_key: str = "smoke_test",
    *,
    dry_run: bool = True,
    human_approved: bool = False,
) -> dict[str, Any]:
    """Send to allowlisted channel only. dry_run default; live needs human_approved."""
    cfg = load_router_config()
    allow = allowlist_route_keys(cfg)
    if route_key not in allow:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "BLOCKED",
            "reason": "ROUTE_NOT_ALLOWLISTED",
            "route_key": route_key,
            "connector_allowlist": allow,
        }
    route = resolve_route(route_key, cfg)
    if not route or not route.get("channel_id"):
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "BLOCKED",
            "reason": "ROUTE_MISSING",
            "route_key": route_key,
        }
    content = (content or "").strip()
    if not content:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "BLOCKED",
            "reason": "EMPTY_CONTENT",
        }
    if len(content) > 1800:
        content = content[:1800]
    if dry_run or not human_approved:
        return {
            "ok": True,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "dry_run": True,
            "human_approved": bool(human_approved),
            "route": route,
            "content_chars": len(content),
            "status": "DRY_RUN_PASS" if dry_run else "BLOCKED_NEEDS_HUMAN_APPROVED",
            "note": "Live send requires dry_run=false AND human_approved=true; no deployment without auth",
            "receipt": {
                "action": "DISCORD_CONNECTOR_SEND",
                "mode": "dry_run",
                "route_key": route_key,
                "generated_at": _now(),
            },
        }
    token = os.environ.get("DISCORD_BOT_TOKEN") or ""
    if not token:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "BLOCKED",
            "reason": "BOT_TOKEN_MISSING",
            "route": route,
        }
    # Explicit operator gate for production-impacting send
    if os.environ.get("DISCORD_CONNECTOR_ALLOW_LIVE_SEND", "").strip() != "1":
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "BLOCKED",
            "reason": "LIVE_SEND_ENV_GATE",
            "route": route,
            "error": "Set DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1 on server for authorized smoke send",
        }
    body = json.dumps({"content": content}).encode("utf-8")
    url = f"https://discord.com/api/v10/channels/{route['channel_id']}/messages"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
            "User-Agent": "DreamOS-DiscordArchitectConnector/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "HTTP_ERROR",
            "http_status": exc.code,
            "route": route,
            "error": "discord_api_http_error",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "ERROR",
            "route": route,
            "error": type(exc).__name__,
        }
    return {
        "ok": True,
        "namespace": "discord_architect_connector",
        "tool": "send_message_allowlisted",
        "dry_run": False,
        "route": route,
        "message_id": raw.get("id") if isinstance(raw, dict) else None,
        "status": "SENT",
        "receipt": {
            "action": "DISCORD_CONNECTOR_SEND",
            "mode": "live",
            "route_key": route_key,
            "message_id": raw.get("id") if isinstance(raw, dict) else None,
            "generated_at": _now(),
        },
    }


def security_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "namespace": "discord_architect_connector",
        "tool": "security_contract",
        "defaults": {
            "read_only_preferred": True,
            "send_dry_run_default": True,
            "human_approved_required_for_live_send": True,
            "live_env_gate": "DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1",
            "tokens_server_side_only": True,
        },
        "forbidden_without_authorization": [
            "guild_admin_mutations",
            "arbitrary_channel_send",
            "permission_escalation",
            "live_deployment",
            "pyautogui_dispatch_from_chatgpt",
        ],
        "preserve": [
            "!message D2A routing",
            "durable bus message IDs",
            "acknowledgments",
            "agent inbox fallback",
            "timeouts",
            "audit receipts",
        ],
        "generated_at": _now(),
    }
