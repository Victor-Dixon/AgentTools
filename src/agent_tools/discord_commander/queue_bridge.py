"""Queue bridge adapter — PyAutoGUI transport stays at the adapter boundary.

Canonical queue processor lives in agent-tools (`message_queue_processor.py`).
PyAutoGUI delivery delegates to Agent_Cellphone via `pyautogui_transport.py`.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional, Protocol

from .models import DeliveryResult

logger = logging.getLogger(__name__)


class QueueProcessor(Protocol):
    def process_queue(
        self,
        max_messages: Optional[int] = None,
        batch_size: int = 1,
        interval: float = 5.0,
    ) -> int:
        ...


class NoOpQueueProcessor:
    """Fallback when PyAutoGUI transport is not available."""

    def process_queue(
        self,
        max_messages: Optional[int] = None,
        batch_size: int = 1,
        interval: float = 5.0,
    ) -> int:
        logger.warning(
            "PyAutoGUI queue transport not available. "
            "Set AGENT_CELLPHONE_ROOT to D:\\Agent_Cellphone and ensure coordinates exist."
        )
        return 0


def load_queue_processor() -> QueueProcessor:
    """Load the Discord Commander queue processor."""
    try:
        from .message_queue_processor import MessageQueueProcessor

        return MessageQueueProcessor()
    except ImportError:
        logger.debug("Discord Commander queue processor not importable")
    return NoOpQueueProcessor()


def get_transport(transport: Optional[Any] = None) -> Any | None:
    """Resolve an explicit or default PyAutoGUI transport."""
    if transport is not None:
        return transport
    if os.environ.get("DISCORD_COMMANDER_DISABLE_PYAUTOGUI", "").strip() in ("1", "true", "True"):
        return None
    try:
        from .pyautogui_transport import get_default_transport

        return get_default_transport()
    except ImportError:
        return None


def deliver_message(message: str, agent_id: str, transport: Optional[Any] = None) -> DeliveryResult:
    """Deliver a single message via optional PyAutoGUI transport adapter."""
    resolved = get_transport(transport)
    if resolved is None:
        detail = "PyAutoGUI transport not bound — !message requires live PyAutoGUI (no webhook fallback)"
        logger.info("No transport adapter bound for %s — %s", agent_id, detail)
        return DeliveryResult(success=False, transport="none", error_code="NO_TRANSPORT", detail=detail)
    try:
        outcome = resolved.send(agent_id=agent_id, message=message)
        if isinstance(outcome, DeliveryResult):
            return outcome
        ok = bool(outcome)
        return DeliveryResult(success=ok, error_code=None if ok else "TRANSPORT_FALSE")
    except Exception as exc:
        logger.exception("Transport delivery failed for %s", agent_id)
        return DeliveryResult(success=False, error_code="TRANSPORT_EXCEPTION", detail=str(exc))
