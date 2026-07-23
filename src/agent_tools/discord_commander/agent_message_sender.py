"""Agent message delivery for toolbelt Commander (no GUI dependency).

Delivery order:
1. DreamVault unified message bus — enqueue-and-observe (processor owns live paste)
2. Direct PyAutoGUI fallback only when bus is disabled/fails and processor does not own delivery
3. PyAutoGUI readiness is required for direct paste only — never block bus enqueue

Discord commands must call ``send_agent_message_async`` so sync work never blocks
the gateway heartbeat. !message is PyAutoGUI/bus-only — no Discord webhook fallback.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Optional

from .delivery_preflight import validate_pyautogui_readiness
from .env_bootstrap import bootstrap_commander_env
from .messaging_delivery_log import record_delivery
from .messaging_roots import apply_messaging_roots
from .models import (
    DELIVERY_QUEUED,
    BroadcastResult,
    CommandResult,
    DeliveryResult,
)
from .message_bus_bridge import message_bus_enabled, send_via_message_bus
from .queue_bridge import deliver_message, get_transport
from .template_bridge import resolve_dreamvault_root, wrap_d2a_message

logger = logging.getLogger(__name__)

_AGENT_ID_PATTERN = re.compile(r"^agent[- ]?(\d+)$", re.IGNORECASE)


def normalize_agent_id(raw: str) -> Optional[str]:
    """Normalize user input to Agent-N form (1-8)."""
    value = raw.strip()
    if not value:
        return None
    if value.startswith("Agent-") and value[6:].isdigit():
        num = int(value[6:])
        if 1 <= num <= 8:
            return f"Agent-{num}"
        return None
    if value.isdigit():
        num = int(value)
        if 1 <= num <= 8:
            return f"Agent-{num}"
        return None
    match = _AGENT_ID_PATTERN.match(value)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 8:
            return f"Agent-{num}"
    return None


def _format_sender(discord_user: Any | None) -> str:
    if discord_user is None:
        return "Discord Commander"
    name = getattr(discord_user, "display_name", None) or getattr(discord_user, "name", None)
    if name:
        return f"Discord User ({name})"
    return "Discord Commander"


def _final_status(success: bool, *, delivery_status: str | None = None) -> str:
    if delivery_status in (
        DELIVERY_QUEUED,
        "DISPATCHING",
        "LIVE_SENT",
        "DELIVERED",
        "FAILED",
        "UNKNOWN",
        "SENT",
    ):
        if delivery_status == "DELIVERED":
            return "SENT"
        if delivery_status == DELIVERY_QUEUED:
            return DELIVERY_QUEUED
        if delivery_status == "LIVE_SENT":
            return "SENT"
        if delivery_status == "FAILED":
            return "FAILED"
        if delivery_status == "SENT":
            return "SENT"
    return "SENT" if success else "FAILED"


DISCORD_SEND_TIMEOUT_SEC = 8.0


def _record_final_delivery(
    *,
    source: str,
    agent_id: str,
    success: bool,
    transport: str,
    message_preview: str,
    error_code: str | None,
    detail: str | None,
    extra: dict[str, Any],
) -> None:
    """One audit line per !message — final outcome only."""
    record_delivery(
        source=source,
        agent_id=agent_id,
        transport=transport,
        success=success,
        message_preview=message_preview,
        error_code=error_code,
        detail=detail,
        extra={
            **extra,
            "final_status": _final_status(
                success,
                delivery_status=str(extra.get("delivery_status") or "") or None,
            ),
        },
    )


def _bus_message_terminal_status(bus_message_id: str | None) -> str | None:
    """Read unified bus row status when bridge result is ambiguous (anti double-paste)."""
    if not bus_message_id:
        return None
    try:
        from dreamvault.message_bus.dispatcher import default_bus_paths
        from dreamvault.runtime_bus import get_message

        root = resolve_dreamvault_root()
        if root is None:
            return None
        paths = default_bus_paths(root)
        row = get_message(message_id=bus_message_id, state_path=paths.state_path)
        return str(row.get("status") or "") or None
    except Exception:
        return None


def _skip_pyautogui_bus_fallback(bus_meta: dict[str, Any]) -> tuple[bool, str]:
    """Skip direct PyAutoGUI when bus already owns or completed delivery (prevents double D2A)."""
    transport = str(bus_meta.get("transport") or "")
    if bus_meta.get("ok"):
        return True, "bus_delivery_already_succeeded"
    if transport in (
        "message_bus_processor_live",
        "message_bus_enqueue_and_live_dispatch",
        "message_bus_processor_pending",
    ):
        return True, "bus_delivery_already_succeeded"
    terminal = _bus_message_terminal_status(str(bus_meta.get("bus_message_id") or "") or None)
    if terminal in ("completed", "delivered", "running", "claimed"):
        return True, f"bus_status_{terminal}_no_fallback"
    if bus_meta.get("processor_running") and transport.startswith("message_bus_processor"):
        return True, "processor_owns_delivery_no_fallback"
    return False, ""


def _build_command_result(
    *,
    success: bool,
    agent: str,
    transport: str,
    message: str,
    error_code: str | None = None,
    extra: dict[str, Any] | None = None,
) -> CommandResult:
    data = dict(extra or {})
    data["transport"] = transport
    data["final_status"] = _final_status(
        success,
        delivery_status=str(data.get("delivery_status") or "") or None,
    )
    return CommandResult(
        success=success,
        message=message,
        agent=agent,
        error_code=error_code,
        data=data,
    )


def send_agent_message(
    agent_id: str,
    message: str,
    *,
    discord_user: Any | None = None,
    priority: str = "regular",
    transport: Any | None = None,
    dry_run: bool = False,
    source: str = "discord_commander",
) -> CommandResult:
    """Send a direct message to an agent via message bus (preferred) or PyAutoGUI."""
    roots = apply_messaging_roots()
    bootstrap_commander_env()
    normalized = normalize_agent_id(agent_id)
    if not normalized:
        return CommandResult(
            success=False,
            message=f"Invalid agent id: {agent_id!r}. Use Agent-1 .. Agent-8.",
            agent=agent_id,
            error_code="INVALID_AGENT",
            data={"final_status": "FAILED"},
        )

    body = message.strip()
    if not body:
        return CommandResult(
            success=False,
            message="Message body cannot be empty.",
            agent=normalized,
            error_code="EMPTY_MESSAGE",
            data={"final_status": "FAILED"},
        )

    sender = _format_sender(discord_user)
    # Advisory for layout / dry-run. Must NOT block bus enqueue (processor owns paste).
    readiness = validate_pyautogui_readiness(normalized)
    if readiness.ready and readiness.layout_mode:
        os.environ["AGENT_GAS_LAYOUT_MODE"] = readiness.layout_mode

    if dry_run:
        return CommandResult(
            success=True,
            message=f"Dry-run: would deliver D2A to {normalized} via PyAutoGUI",
            agent=normalized,
            data={
                "transport": "pyautogui_dry_run",
                "final_status": "SENT",
                "messaging_roots": roots,
                "readiness": readiness.ready,
                "layout_mode": readiness.layout_mode,
            },
        )

    bus_attempt: dict[str, Any] | None = None

    if message_bus_enabled():
        # Enqueue first — never require live PyAutoGUI readiness to accept D2A.
        bus_ok, bus_detail, bus_meta = send_via_message_bus(
            agent_id=normalized,
            raw_content=body,
            sender=sender,
            live=True,
        )
        bus_attempt = {"ok": bus_ok, "detail": bus_detail, **bus_meta}
        if bus_ok:
            delivery_status = str(bus_meta.get("delivery_status") or DELIVERY_QUEUED)
            # Enqueue-ack is success even when live paste is still pending.
            label = "QUEUED" if delivery_status == DELIVERY_QUEUED and not bus_meta.get("confirmed") else "SENT"
            _record_final_delivery(
                source=source,
                agent_id=normalized,
                success=True,
                transport=str(bus_meta.get("transport", "message_bus")),
                message_preview=bus_meta.get("body_preview") or body,
                error_code=None,
                detail=bus_detail,
                extra={
                    "messaging_roots": roots,
                    "bus_attempt": bus_attempt,
                    "delivery_status": delivery_status,
                    "preflight_ready": readiness.ready,
                    "preflight_detail": readiness.detail,
                },
            )
            return _build_command_result(
                success=True,
                agent=normalized,
                transport=str(bus_meta.get("transport", "message_bus")),
                message=f"{label}: {bus_detail}",
                extra={**bus_meta, "messaging_roots": roots, "delivery_status": delivery_status},
            )
        skip_fallback, skip_reason = _skip_pyautogui_bus_fallback(bus_meta)
        if skip_fallback:
            terminal = _bus_message_terminal_status(str(bus_meta.get("bus_message_id") or "") or None)
            treated_success = terminal == "completed"
            transport = str(bus_meta.get("transport", "message_bus"))
            detail = bus_detail if not treated_success else f"D2A delivered via bus ({terminal})"
            _record_final_delivery(
                source=source,
                agent_id=normalized,
                success=treated_success,
                transport=transport,
                message_preview=bus_meta.get("body_preview") or body,
                error_code=None if treated_success else "BUS_PROCESSOR_PENDING",
                detail=detail,
                extra={
                    "messaging_roots": roots,
                    "bus_attempt": bus_attempt,
                    "fallback_suppressed": skip_reason,
                },
            )
            if treated_success:
                return _build_command_result(
                    success=True,
                    agent=normalized,
                    transport=transport,
                    message=f"SENT: {detail}",
                    extra={**bus_meta, "messaging_roots": roots, "fallback_suppressed": skip_reason},
                )
            return _build_command_result(
                success=False,
                agent=normalized,
                transport=transport,
                message=f"FAILED: {detail} (no PyAutoGUI fallback — {skip_reason})",
                error_code="BUS_PROCESSOR_PENDING",
                extra={**bus_meta, "messaging_roots": roots, "fallback_suppressed": skip_reason},
            )
        logger.warning("Message bus delivery failed (%s) — trying direct PyAutoGUI once", bus_detail)

    # Direct paste path (bus off or bus failed without processor ownership).
    if not readiness.ready:
        detail = readiness.detail or "PyAutoGUI not ready"
        _record_final_delivery(
            source=source,
            agent_id=normalized,
            success=False,
            transport="preflight_blocked",
            message_preview=body,
            error_code=readiness.error_code,
            detail=detail,
            extra={
                "messaging_roots": roots,
                "layout_mode": readiness.layout_mode,
                "bus_attempt": bus_attempt,
            },
        )
        return _build_command_result(
            success=False,
            agent=normalized,
            transport="preflight_blocked",
            message=f"FAILED: {detail}",
            error_code=readiness.error_code,
            extra={
                "messaging_roots": roots,
                "layout_mode": readiness.layout_mode,
                "readiness_warnings": readiness.warnings,
                "bus_attempt": bus_attempt,
            },
        )

    body, template_meta = wrap_d2a_message(agent_id=normalized, raw_content=body, sender=sender)

    resolved_transport = transport if transport is not None else get_transport(None)
    if resolved_transport is None:
        detail = (
            "PyAutoGUI transport unavailable after preflight. Check AGENT_CELLPHONE_ROOT / "
            "DREAMVAULT_AGENT_TRANSPORT_SSOT and coords calibration."
        )
        _record_final_delivery(
            source=source,
            agent_id=normalized,
            success=False,
            transport="none",
            message_preview=body,
            error_code="NO_TRANSPORT",
            detail=detail,
            extra={**template_meta, "messaging_roots": roots, "bus_attempt": bus_attempt},
        )
        return _build_command_result(
            success=False,
            agent=normalized,
            transport="none",
            message=f"FAILED: {detail}",
            error_code="NO_TRANSPORT",
            extra={**template_meta, "messaging_roots": roots, "bus_attempt": bus_attempt},
        )

    py_result = deliver_message(body, normalized, resolved_transport)
    if py_result.success:
        transport_name = "pyautogui_bus_fallback" if bus_attempt else "pyautogui"
        data: dict[str, Any] = {
            **template_meta,
            "messaging_roots": roots,
            "layout_mode": readiness.layout_mode,
        }
        if bus_attempt:
            data["bus_attempt"] = bus_attempt
        if py_result.detail:
            data["layout_note"] = py_result.detail
        if readiness.warnings:
            data["readiness_warnings"] = readiness.warnings
        _record_final_delivery(
            source=source,
            agent_id=normalized,
            success=True,
            transport=transport_name,
            message_preview=body,
            error_code=None,
            detail=py_result.detail,
            extra=data,
        )
        note = " (bus timeout fallback)" if bus_attempt else ""
        return _build_command_result(
            success=True,
            agent=normalized,
            transport=transport_name,
            message=f"SENT: Delivered to {normalized} via PyAutoGUI{note}",
            extra=data,
        )

    detail = py_result.detail or "PyAutoGUI delivery failed"
    code = py_result.error_code or "PYAUTOGUI_FAILED"
    _record_final_delivery(
        source=source,
        agent_id=normalized,
        success=False,
        transport="pyautogui",
        message_preview=body,
        error_code=code,
        detail=detail,
        extra={**template_meta, "messaging_roots": roots, "bus_attempt": bus_attempt},
    )
    logger.error("PyAutoGUI failed for %s (%s): %s", normalized, code, detail)
    return _build_command_result(
        success=False,
        agent=normalized,
        transport="pyautogui",
        message=f"FAILED: {detail}",
        error_code=code,
        extra={
            "pyautogui_error": detail,
            **template_meta,
            "messaging_roots": roots,
            "bus_attempt": bus_attempt,
        },
    )


async def send_agent_message_async(
    agent_id: str,
    message: str,
    *,
    discord_user: Any | None = None,
    priority: str = "regular",
    transport: Any | None = None,
    dry_run: bool = False,
    source: str = "discord_commander",
    timeout: float = DISCORD_SEND_TIMEOUT_SEC,
) -> CommandResult:
    """Offload sync delivery work off the Discord event loop with a hard timeout.

    Timeout does not cancel a queued bus message — persistence happens before
    any confirmation wait (enqueue-only by default).
    """
    import asyncio

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(
                send_agent_message,
                agent_id,
                message,
                discord_user=discord_user,
                priority=priority,
                transport=transport,
                dry_run=dry_run,
                source=source,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        normalized = normalize_agent_id(agent_id) or agent_id
        return CommandResult(
            success=True,
            message="Message accepted, but live delivery confirmation is still pending.",
            agent=normalized,
            error_code="DELIVERY_CONFIRMATION_PENDING",
            data={
                "final_status": DELIVERY_QUEUED,
                "delivery_status": DELIVERY_QUEUED,
                "accepted": True,
                "queued": True,
                "confirmed": False,
                "transport": "message_bus_timeout_pending",
            },
        )


def broadcast_agent_messages(
    message: str,
    *,
    agents: list[str] | None = None,
    discord_user: Any | None = None,
    source: str = "discord_broadcast",
    transport: Any | None = None,
    dry_run: bool = False,
) -> BroadcastResult:
    """Send the same D2A message to each agent sequentially (message bus / PyAutoGUI)."""
    from agent_tools.discord_commander.swarm_status_helper import list_swarm_agents

    body = message.strip()
    if not body:
        return BroadcastResult(
            success=False,
            message="Message body cannot be empty.",
            error_code="EMPTY_MESSAGE",
        )

    targets = list(agents) if agents else list_swarm_agents()
    if not targets:
        return BroadcastResult(
            success=False,
            message="No agents configured for broadcast.",
            error_code="NO_AGENTS",
        )

    delivered: list[str] = []
    failed: list[str] = []
    results: list[CommandResult] = []

    for agent_id in targets:
        result = send_agent_message(
            agent_id,
            body,
            discord_user=discord_user,
            transport=transport,
            dry_run=dry_run,
            source=source,
        )
        results.append(result)
        agent = result.agent or agent_id
        if result.success:
            delivered.append(agent)
        else:
            failed.append(agent)

    ok = bool(delivered) and not failed
    partial = bool(delivered) and bool(failed)
    if ok:
        msg = f"SENT: Broadcast delivered to {len(delivered)}/{len(targets)} agents"
    elif partial:
        msg = f"FAILED: Broadcast partial {len(delivered)}/{len(targets)}; failed: {', '.join(failed)}"
    else:
        msg = f"FAILED: Broadcast failed for all {len(targets)} agents"

    return BroadcastResult(
        success=ok,
        message=msg,
        delivered=delivered,
        failed=failed,
        results=results,
        error_code=None if ok else ("PARTIAL_BROADCAST" if partial else "BROADCAST_FAILED"),
    )
