#!/usr/bin/env python3
"""Discord Architect Connector — allowlisted ChatGPT MCP helpers.

Reuses DreamVault router config. Default: read-only / dry_run.
Live send is authorized only by the server-side env gate
``DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1``. A client-supplied
``human_approved=true`` flag is recorded on receipts and is never
treated as trusted authorization.

Tokens stay server-side (env) and are never returned to clients.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
DEFAULT_ALLOWLIST = ("smoke_test",)
LIVE_SEND_ENV = "DISCORD_CONNECTOR_ALLOW_LIVE_SEND"


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _router_config_path(path: Path | None = None) -> Path:
    if path is not None:
        return path
    override = (os.environ.get("DISCORD_ROUTER_CONFIG") or "").strip()
    if override:
        return Path(override)
    root = Path(os.environ.get("DREAMVAULT_ROOT", r"D:\DreamVault"))
    return root / "runtime" / "config" / "discord_router_channels.json"


def _live_send_authorized() -> bool:
    return os.environ.get(LIVE_SEND_ENV, "").strip() == "1"


def load_router_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = _router_config_path(path)
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


def _receipt(
    *,
    mode: str,
    route_key: str,
    human_approved: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "action": "DISCORD_CONNECTOR_SEND",
        "mode": mode,
        "route_key": route_key,
        "client_human_approved": bool(human_approved),
        "client_human_approved_trusted": False,
        "live_env_gate": _live_send_authorized(),
        "generated_at": _now(),
    }
    if extra:
        payload.update(extra)
    return payload


def read_channels(*, include_non_allowlisted_metadata: bool = True) -> dict[str, Any]:
    """Config-backed channel inventory (no secrets)."""
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
        "config_path": str(_router_config_path()),
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
    """Send to an allowlisted channel only.

    ``human_approved`` is client metadata and never authorizes a live send.
    Live send requires ``dry_run=false`` and server-side
    ``DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1``.
    """
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
            "receipt": _receipt(mode="blocked", route_key=route_key, human_approved=human_approved),
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
            "receipt": _receipt(mode="blocked", route_key=route_key, human_approved=human_approved),
        }
    content = (content or "").strip()
    if not content:
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "BLOCKED",
            "reason": "EMPTY_CONTENT",
            "receipt": _receipt(mode="blocked", route_key=route_key, human_approved=human_approved),
        }
    if len(content) > 1800:
        content = content[:1800]
    if dry_run:
        return {
            "ok": True,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "dry_run": True,
            "human_approved": bool(human_approved),
            "client_human_approved_trusted": False,
            "route": route,
            "content_chars": len(content),
            "status": "DRY_RUN_PASS",
            "note": (
                "Client human_approved is not authorization. "
                "Live send requires dry_run=false and server-side "
                f"{LIVE_SEND_ENV}=1."
            ),
            "receipt": _receipt(mode="dry_run", route_key=route_key, human_approved=human_approved),
        }
    if not _live_send_authorized():
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "dry_run": False,
            "human_approved": bool(human_approved),
            "client_human_approved_trusted": False,
            "status": "BLOCKED",
            "reason": "LIVE_SEND_ENV_GATE",
            "route": route,
            "error": f"Set {LIVE_SEND_ENV}=1 on the server for an authorized smoke send",
            "receipt": _receipt(mode="blocked", route_key=route_key, human_approved=human_approved),
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
            "receipt": _receipt(mode="blocked", route_key=route_key, human_approved=human_approved),
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
            "receipt": _receipt(mode="blocked", route_key=route_key, human_approved=human_approved),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "namespace": "discord_architect_connector",
            "tool": "send_message_allowlisted",
            "status": "ERROR",
            "route": route,
            "error": type(exc).__name__,
            "receipt": _receipt(mode="blocked", route_key=route_key, human_approved=human_approved),
        }
    message_id = raw.get("id") if isinstance(raw, dict) else None
    return {
        "ok": True,
        "namespace": "discord_architect_connector",
        "tool": "send_message_allowlisted",
        "dry_run": False,
        "route": route,
        "message_id": message_id,
        "status": "SENT",
        "receipt": _receipt(
            mode="live",
            route_key=route_key,
            human_approved=human_approved,
            extra={"message_id": message_id},
        ),
    }


def security_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "namespace": "discord_architect_connector",
        "tool": "security_contract",
        "defaults": {
            "read_only_preferred": True,
            "send_dry_run_default": True,
            "client_human_approved_trusted": False,
            "live_env_gate": f"{LIVE_SEND_ENV}=1",
            "live_env_gate_default": "off",
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
