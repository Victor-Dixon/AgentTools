"""Queue bridge adapter — PyAutoGUI transport stays at the adapter boundary.

Agent_Cellphone_V2_Repository remains canonical for PyAutoGUI lane injection.
This module provides a thin interface the toolbelt can call without importing
PyAutoGUI as a core dependency.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Protocol

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
            "Install Agent_Cellphone_V2 transport adapter or run from that repo."
        )
        return 0


def load_queue_processor() -> QueueProcessor:
    """Attempt to load the legacy queue processor from Agent Cellphone transport."""
    try:
        from src.core.legacy_message_queue_processor import MessageQueueProcessor

        return MessageQueueProcessor()
    except ImportError:
        logger.debug("Agent_Cellphone_V2 queue processor not importable")
    return NoOpQueueProcessor()


def deliver_message(message: str, agent_id: str, transport: Optional[Any] = None) -> bool:
    """Deliver a single message via optional PyAutoGUI transport adapter."""
    if transport is None:
        logger.info("No transport adapter bound; message queued for external delivery")
        return False
    try:
        return bool(transport.send(agent_id=agent_id, message=message))
    except Exception:
        logger.exception("Transport delivery failed")
        return False
