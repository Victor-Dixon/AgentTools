"""File-backed dispatch claim ledger — prevents duplicate PyAutoGUI after timeout/reconnect."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _ledger_path() -> Path:
    raw = os.environ.get("DISCORD_COMMANDER_DISPATCH_LEDGER", "").strip()
    if raw:
        return Path(raw)
    log_dir = os.environ.get("DISCORD_COMMANDER_LOG_DIR", "").strip()
    if log_dir:
        return Path(log_dir) / "dispatch_claim_ledger.json"
    return Path.home() / ".dreamvault" / "discord_commander" / "dispatch_claim_ledger.json"


@dataclass(frozen=True)
class ClaimResult:
    acquired: bool
    message_id: str
    status: str
    detail: str = ""


class DeliveryClaimLedger:
    """Atomic-ish queued -> claimed -> live_sent transitions via rename."""

    SUCCESS_STATUSES = frozenset({"live_sent", "delivered", "completed"})

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _ledger_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema": "dreamvault.discord_dispatch_ledger.v1", "messages": {}}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"schema": "dreamvault.discord_dispatch_ledger.v1", "messages": {}}

    def _write_atomic(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, self.path)

    def has_success(self, message_id: str) -> bool:
        row = (self._read().get("messages") or {}).get(message_id) or {}
        return str(row.get("status") or "") in self.SUCCESS_STATUSES

    def get(self, message_id: str) -> dict[str, Any] | None:
        row = (self._read().get("messages") or {}).get(message_id)
        return dict(row) if isinstance(row, dict) else None

    def mark_queued(self, message_id: str, *, extra: dict[str, Any] | None = None) -> None:
        data = self._read()
        messages = data.setdefault("messages", {})
        existing = messages.get(message_id) or {}
        if str(existing.get("status") or "") in self.SUCCESS_STATUSES:
            return
        row = {
            **existing,
            "message_id": message_id,
            "status": "queued",
            "updated_at": time.time(),
        }
        if extra:
            row.update(extra)
        messages[message_id] = row
        self._write_atomic(data)

    def claim_dispatch(self, message_id: str) -> ClaimResult:
        data = self._read()
        messages = data.setdefault("messages", {})
        existing = messages.get(message_id) or {}
        status = str(existing.get("status") or "")
        if status in self.SUCCESS_STATUSES:
            return ClaimResult(
                acquired=False,
                message_id=message_id,
                status=status,
                detail="already_succeeded",
            )
        if status == "claimed":
            return ClaimResult(
                acquired=False,
                message_id=message_id,
                status=status,
                detail="already_claimed",
            )
        messages[message_id] = {
            **existing,
            "message_id": message_id,
            "status": "claimed",
            "claimed_at": time.time(),
            "updated_at": time.time(),
        }
        self._write_atomic(data)
        return ClaimResult(
            acquired=True,
            message_id=message_id,
            status="claimed",
            detail="claim_acquired",
        )

    def mark_live_sent(self, message_id: str, *, detail: str = "") -> None:
        data = self._read()
        messages = data.setdefault("messages", {})
        existing = messages.get(message_id) or {}
        messages[message_id] = {
            **existing,
            "message_id": message_id,
            "status": "live_sent",
            "detail": detail,
            "updated_at": time.time(),
        }
        self._write_atomic(data)


_DEFAULT_LEDGER: DeliveryClaimLedger | None = None


def default_ledger() -> DeliveryClaimLedger:
    global _DEFAULT_LEDGER
    if _DEFAULT_LEDGER is None:
        _DEFAULT_LEDGER = DeliveryClaimLedger()
    return _DEFAULT_LEDGER
