"""Structured audit log for Discord Commander message delivery (separate from closeout webhooks)."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_DEFAULT_LOG_DIR = Path(__file__).resolve().parents[3] / "runtime" / "logs"


def _log_dir() -> Path:
    override = os.environ.get("DISCORD_COMMANDER_LOG_DIR", "").strip()
    return Path(override) if override else _DEFAULT_LOG_DIR


def delivery_jsonl_path() -> Path:
    return _log_dir() / "messaging_delivery.jsonl"


def record_delivery(
    *,
    source: str,
    agent_id: str,
    transport: str,
    success: bool,
    message_preview: str = "",
    error_code: Optional[str] = None,
    detail: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    """Append one delivery attempt to JSONL audit log and emit a log line."""
    preview = (message_preview or "")[:120]
    entry: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": source,
        "agent_id": agent_id,
        "transport": transport,
        "success": success,
        "message_preview": preview,
        "error_code": error_code,
        "detail": detail,
    }
    if extra:
        entry["extra"] = extra

    path = delivery_jsonl_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        logger.warning("Failed to write messaging delivery log: %s", exc)

    level = logging.INFO if success else logging.WARNING
    logger.log(
        level,
        "delivery source=%s agent=%s transport=%s success=%s error=%s detail=%s preview=%r",
        source,
        agent_id,
        transport,
        success,
        error_code or "-",
        detail or "-",
        preview,
    )
