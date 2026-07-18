"""Route Discord Commander !message through DreamVault unified message bus (D2A template SSOT).

Discord is an enqueue-and-observe client: it must not block the gateway loop on
PyAutoGUI paste, bus polling, or time.sleep. Live dispatch belongs to the
standalone message-bus processor.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

from .delivery_claim_ledger import default_ledger
from .env_bootstrap import bootstrap_commander_env, message_bus_processor_running
from .messaging_roots import apply_messaging_roots
from .template_bridge import resolve_dreamvault_root

logger = logging.getLogger(__name__)

POLL_INTERVAL_SEC = 0.5
PROCESSOR_DELIVERY_TIMEOUT_SEC = 20.0
PROCESSOR_GRACE_POLL_SEC = 10.0

# Discord default: do not wait for live delivery (0 = enqueue-only).
# Set DISCORD_COMMANDER_DELIVERY_WAIT_SEC>0 only for explicit wait/legacy tooling.
_STATUS_CACHE: dict[str, tuple[float, int, dict[str, Any]]] = {}


def message_bus_enabled() -> bool:
    return os.environ.get("DISCORD_COMMANDER_USE_MESSAGE_BUS", "1").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _delivery_wait_requested(wait_for_delivery: bool | None) -> bool:
    if wait_for_delivery is not None:
        return bool(wait_for_delivery)
    raw = os.environ.get("DISCORD_COMMANDER_DELIVERY_WAIT_SEC", "0").strip()
    try:
        return float(raw) > 0
    except ValueError:
        return False


def _ensure_import(root: Path) -> None:
    src = str(root / "src")
    scripts = str(root / "runtime" / "scripts")
    for path in (src, scripts):
        if path not in sys.path:
            sys.path.insert(0, path)


def get_message_status(message_id: str, state_path: Path) -> dict[str, Any] | None:
    """Cached bus row lookup — avoids re-reading full state on every poll tick."""
    try:
        st = state_path.stat()
    except OSError:
        return None
    key = str(state_path.resolve())
    cached = _STATUS_CACHE.get(key)
    if cached and cached[0] == st.st_mtime and cached[1] == st.st_size:
        index = cached[2]
    else:
        from dreamvault.runtime_bus import get_message

        # Build a thin index for the requested id; cache the whole last-known map entry.
        try:
            row = get_message(message_id=message_id, state_path=state_path)
        except Exception:
            row = {}
        index = {message_id: row}
        # Merge with prior index so other ids remain available until mtime changes.
        if cached:
            merged = dict(cached[2])
            merged[message_id] = row
            index = merged
        _STATUS_CACHE[key] = (st.st_mtime, st.st_size, index)
    row = index.get(message_id)
    return dict(row) if row else None


def _poll_bus_message(
    *,
    paths,
    message_id: str,
    timeout_sec: float = PROCESSOR_DELIVERY_TIMEOUT_SEC,
) -> tuple[str, dict[str, Any]]:
    deadline = time.monotonic() + timeout_sec
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last = get_message_status(message_id, paths.state_path) or {}
        status = str(last.get("status") or "")
        if status in ("completed", "failed"):
            return status, last
        time.sleep(POLL_INTERVAL_SEC)
    return "timeout", last


def _inline_dispatch_with_claim(
    *,
    paths,
    bus_message_id: str,
    agent_id: str,
    meta: dict[str, Any],
) -> tuple[bool, str, dict[str, Any]]:
    """Legacy wait path: claim once, then dispatch_next (never double-paste)."""
    from dreamvault.message_bus.dispatcher import dispatch_next
    from dreamvault.runtime_bus import RuntimeBusError

    ledger = default_ledger()
    if ledger.has_success(bus_message_id):
        meta["transport"] = "message_bus_already_sent"
        meta["delivery_status"] = "LIVE_SENT"
        meta["accepted"] = True
        meta["queued"] = True
        meta["live_dispatched"] = True
        meta["confirmed"] = True
        return True, f"D2A already live-sent for {agent_id} (idempotent)", meta

    claim = ledger.claim_dispatch(bus_message_id)
    if not claim.acquired:
        meta["transport"] = "message_bus_claim_skipped"
        meta["delivery_status"] = "QUEUED"
        meta["accepted"] = True
        meta["queued"] = True
        meta["claim_detail"] = claim.detail
        return True, f"D2A dispatch already claimed for {agent_id}", meta

    dispatch_result = None
    last_error = ""
    for attempt in range(4):
        try:
            dispatch_result = dispatch_next(paths=paths, live=True, message_id=bus_message_id)
            break
        except RuntimeBusError as exc:
            last_error = str(exc)
            if "delivery in flight" in last_error.lower() and attempt < 3:
                time.sleep(1.5)
                continue
            meta["transport"] = "message_bus_dispatch_error"
            meta["dispatch_error"] = last_error
            meta["delivery_status"] = "FAILED"
            return False, f"D2A dispatch blocked: {last_error}", meta
        except Exception as exc:
            logger.exception("inline live dispatch failed")
            meta["transport"] = "message_bus_dispatch_error"
            meta["dispatch_error"] = str(exc)
            meta["delivery_status"] = "FAILED"
            return False, f"D2A dispatch failed for {agent_id}: {exc}", meta

    if dispatch_result and dispatch_result.success:
        ledger.mark_live_sent(bus_message_id, detail=str(dispatch_result.detail or ""))
        meta["transport"] = "message_bus_enqueue_and_live_dispatch"
        meta["dispatch_target"] = dispatch_result.target_agent
        meta["dispatch_detail"] = dispatch_result.detail
        meta["delivery_status"] = "LIVE_SENT"
        meta["accepted"] = True
        meta["queued"] = True
        meta["live_dispatched"] = True
        meta["confirmed"] = True
        return (
            True,
            f"D2A delivered to {dispatch_result.target_agent} via PyAutoGUI ({dispatch_result.detail})",
            meta,
        )
    if dispatch_result and not dispatch_result.success:
        meta["transport"] = "message_bus_dispatch_failed"
        meta["dispatch_detail"] = dispatch_result.detail
        meta["delivery_status"] = "FAILED"
        return False, f"D2A dispatch failed for {agent_id}: {dispatch_result.detail}", meta
    meta["dispatch_error"] = last_error or "no queued message after enqueue"
    meta["delivery_status"] = "FAILED"
    return False, f"D2A enqueued but live dispatch did not run for {agent_id}", meta


def send_via_message_bus(
    *,
    agent_id: str,
    raw_content: str,
    sender: str,
    live: bool = False,
    wait_for_delivery: bool | None = None,
) -> tuple[bool, str, dict[str, Any]]:
    """Enqueue D2A on unified bus.

    Default (wait_for_delivery=False): enqueue and return immediately. The
    message-bus processor owns live PyAutoGUI. Discord must not poll or dispatch.
    """
    bootstrap_commander_env()
    apply_messaging_roots()
    root = resolve_dreamvault_root()
    if root is None:
        return False, "DreamVault root not found", {"message_bus": "skipped", "reason": "dreamvault_missing"}

    try:
        _ensure_import(root)
        os.environ.setdefault("DREAMVAULT_ROOT", str(root))
        from dreamvault.discord.d2a_transport_bootstrap import bootstrap_d2a_transport_env

        bootstrap_d2a_transport_env(root)
        from dreamvault.discord.d2a_ingress_adapter import ingest_discord_message_command
        from dreamvault.message_bus.dispatcher import default_bus_paths

        command = f"!message {agent_id} {raw_content}"
        paths = default_bus_paths(root)
        result = ingest_discord_message_command(
            command,
            sender=sender,
            paths=paths,
        )
        bus_message_id = result.bus_message.id
        default_ledger().mark_queued(bus_message_id, extra={"agent_id": agent_id})
        meta: dict[str, Any] = {
            "message_bus": "enqueued",
            "bus_message_id": bus_message_id,
            "message_id": bus_message_id,
            "category": result.bus_message.category.value,
            "message_template": "D2A",
            "template_category": "D2A",
            "verify_markers": list(result.verify_markers),
            "body_preview": (result.bus_message.body or "")[:160],
            "transport": "message_bus_enqueue_only",
            "delivery_status": "QUEUED",
            "accepted": True,
            "queued": True,
            "live_dispatched": False,
            "confirmed": False,
        }
        processor_up = message_bus_processor_running(root)
        meta["processor_running"] = processor_up
        live = live or os.environ.get("ALLOW_LIVE_CURSOR_INJECTION", "").strip() == "1"

        # Primary path: acknowledge after enqueue — never block Discord on UI delivery.
        if not _delivery_wait_requested(wait_for_delivery):
            meta["transport"] = "message_bus_enqueue_only"
            detail = (
                f"D2A accepted for {agent_id}; queued on message bus "
                f"(processor_running={processor_up}; processor owns live delivery)"
            )
            return True, detail, meta

        # Legacy / explicit wait path (opt-in via wait_for_delivery or env).
        if not live:
            return (
                False,
                "ALLOW_LIVE_CURSOR_INJECTION=1 required for PyAutoGUI delivery",
                meta,
            )

        if processor_up:
            status, row = _poll_bus_message(paths=paths, message_id=bus_message_id)
            if status == "timeout":
                status, row = _poll_bus_message(
                    paths=paths,
                    message_id=bus_message_id,
                    timeout_sec=PROCESSOR_GRACE_POLL_SEC,
                )
                meta["bus_grace_poll"] = True
            meta["bus_final_status"] = status
            if status == "completed":
                meta["transport"] = "message_bus_processor_live"
                meta["delivery_status"] = "DELIVERED"
                meta["live_dispatched"] = True
                meta["confirmed"] = True
                default_ledger().mark_live_sent(bus_message_id, detail="processor_completed")
                return (
                    True,
                    f"D2A delivered to {agent_id} via message bus processor (PyAutoGUI)",
                    meta,
                )
            if status == "failed":
                meta["transport"] = "message_bus_processor_failed"
                meta["delivery_status"] = "FAILED"
                return (
                    False,
                    f"D2A processor delivery failed for {agent_id} (bus status=failed)",
                    meta,
                )
            bus_status = str(row.get("status") or "")
            if status == "timeout" and bus_status in ("queued", "claimed", "running", "delivered", ""):
                meta["transport"] = "message_bus_processor_pending"
                meta["bus_final_status"] = bus_status or "queued"
                meta["delivery_status"] = "QUEUED"
                return (
                    True,
                    f"D2A enqueued for {agent_id}; processor owns delivery (poll timeout ok)",
                    meta,
                )
            meta["transport"] = "message_bus_processor_timeout"
            meta["delivery_status"] = "FAILED"
            return (
                False,
                f"D2A enqueued but processor did not complete within {PROCESSOR_DELIVERY_TIMEOUT_SEC:.0f}s",
                meta,
            )

        return _inline_dispatch_with_claim(
            paths=paths,
            bus_message_id=bus_message_id,
            agent_id=agent_id,
            meta=meta,
        )
    except Exception as exc:
        logger.exception("message bus send failed")
        return False, str(exc), {"message_bus": "error", "error": str(exc), "delivery_status": "FAILED"}
