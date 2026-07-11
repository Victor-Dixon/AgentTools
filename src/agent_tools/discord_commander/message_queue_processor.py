"""Persistent message queue processor for Discord Commander → Cursor delivery."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from .messaging_delivery_log import record_delivery
from .models import DeliveryResult

logger = logging.getLogger(__name__)

DEFAULT_QUEUE_PATH = Path(
    os.environ.get(
        "DISCORD_COMMANDER_QUEUE_PATH",
        str(Path(__file__).resolve().parents[3] / "data" / "message_queue.json"),
    )
)


@dataclass
class QueuedMessage:
    id: str
    agent_id: str
    message: str
    priority: int = 1
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    attempts: int = 0
    last_error: str | None = None


class MessageQueueStore:
    """JSON-backed queue store for cross-process message delivery."""

    def __init__(self, path: Path = DEFAULT_QUEUE_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, items: list[dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def enqueue(self, agent_id: str, message: str, priority: int = 1) -> str:
        items = self._load()
        msg_id = str(uuid.uuid4())
        items.append(
            asdict(
                QueuedMessage(
                    id=msg_id,
                    agent_id=agent_id,
                    message=message,
                    priority=priority,
                )
            )
        )
        self._save(items)
        logger.info("Queued message id=%s agent=%s priority=%s", msg_id, agent_id, priority)
        return msg_id

    def pending(self) -> list[QueuedMessage]:
        items = self._load()
        pending = [QueuedMessage(**item) for item in items if item.get("status") == "pending"]
        return sorted(pending, key=lambda msg: (-msg.priority, msg.created_at))

    def failed(self) -> list[QueuedMessage]:
        items = self._load()
        return [QueuedMessage(**item) for item in items if item.get("status") == "failed"]

    def update(self, msg_id: str, **fields: Any) -> None:
        items = self._load()
        for item in items:
            if item["id"] == msg_id:
                item.update(fields)
        self._save(items)

    def pending_count(self) -> int:
        return len(self.pending())


class MessageQueueProcessor:
    """Drain queued messages via PyAutoGUI transport."""

    def __init__(
        self,
        store: MessageQueueStore | None = None,
        transport: Any | None = None,
    ) -> None:
        self.store = store or MessageQueueStore()
        self._transport = transport

    def _get_transport(self) -> Any | None:
        if self._transport is not None:
            return self._transport
        from .pyautogui_transport import get_default_transport

        return get_default_transport()

    def queue_message(self, agent_id: str, message: str, priority: int = 1) -> bool:
        self.store.enqueue(agent_id, message, priority)
        return True

    def process_one(self) -> bool:
        pending = self.store.pending()
        if not pending:
            return False

        msg = pending[0]
        transport = self._get_transport()
        if transport is None:
            logger.warning(
                "Queue drain blocked: no PyAutoGUI transport (pending=%d msg_id=%s agent=%s)",
                len(pending),
                msg.id,
                msg.agent_id,
            )
            return False

        self.store.update(msg.id, status="processing", attempts=msg.attempts + 1)
        high_priority = msg.priority >= 3
        outcome = transport.send(msg.agent_id, msg.message, high_priority=high_priority)
        if isinstance(outcome, DeliveryResult):
            ok = outcome.success
            err_detail = outcome.detail
            err_code = outcome.error_code
        else:
            ok = bool(outcome)
            err_detail = None if ok else "transport returned false"
            err_code = None if ok else "TRANSPORT_FALSE"

        self.store.update(
            msg.id,
            status="sent" if ok else "failed",
            last_error=err_detail if not ok else None,
        )
        record_delivery(
            source="message_queue_processor",
            agent_id=msg.agent_id,
            transport="pyautogui",
            success=ok,
            message_preview=msg.message,
            error_code=err_code,
            detail=err_detail,
            extra={"queue_msg_id": msg.id, "attempts": msg.attempts + 1},
        )
        if ok:
            logger.info("Queue delivered msg_id=%s agent=%s", msg.id, msg.agent_id)
        else:
            logger.warning(
                "Queue delivery FAILED msg_id=%s agent=%s error=%s detail=%s",
                msg.id,
                msg.agent_id,
                err_code,
                err_detail,
            )
        return ok

    def process_queue(
        self,
        max_messages: Optional[int] = None,
        batch_size: int = 1,
        interval: float = 5.0,
    ) -> int:
        processed = 0
        logger.info(
            "Queue processor loop started path=%s interval=%.1fs",
            self.store.path,
            interval,
        )
        while True:
            pending_count = self.store.pending_count()
            failed_count = len(self.store.failed())
            if pending_count:
                logger.info("Queue heartbeat pending=%d failed=%d", pending_count, failed_count)

            batch_count = 0
            while batch_count < batch_size:
                if max_messages is not None and processed >= max_messages:
                    return processed
                if not self.process_one():
                    batch_count = batch_size
                    break
                processed += 1
                batch_count += 1

            if max_messages is not None and processed >= max_messages:
                return processed
            time.sleep(interval)
