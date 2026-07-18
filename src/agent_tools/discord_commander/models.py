"""Data models for Discord Commander operations.

Adapted from Agent_Cellphone_V2_Repository/src/discord_commander/discord_models.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Delivery lifecycle for bus / PyAutoGUI paths (Discord must not collapse these).
DELIVERY_QUEUED = "QUEUED"
DELIVERY_DISPATCHING = "DISPATCHING"
DELIVERY_LIVE_SENT = "LIVE_SENT"
DELIVERY_DELIVERED = "DELIVERED"
DELIVERY_FAILED = "FAILED"
DELIVERY_UNKNOWN = "UNKNOWN"


@dataclass
class CommandResult:
    success: bool
    message: str
    data: Optional[dict[str, Any]] = None
    agent: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: str = field(default_factory=_utc_now_iso)
    error_code: Optional[str] = None


@dataclass
class DeliveryResult:
    """Outcome of a transport / bus attempt.

    Distinguishes accepted/queued from live dispatch confirmation so a Discord
    reconnect cannot turn a successful enqueue into a user-visible failure.
    Legacy callers may pass only ``success`` / ``error_code`` / ``detail``.
    """

    success: bool = False
    transport: str = "pyautogui"
    error_code: Optional[str] = None
    detail: Optional[str] = None
    accepted: bool = False
    queued: bool = False
    live_dispatched: bool = False
    confirmed: bool = False
    message_id: str = ""
    error: Optional[str] = None
    status: str = DELIVERY_UNKNOWN

    def __post_init__(self) -> None:
        if self.error is None and self.error_code:
            self.error = self.error_code
        # Legacy: success-only constructors mean confirmed delivery.
        if self.success and not (self.accepted or self.queued or self.confirmed or self.live_dispatched):
            self.accepted = True
            self.confirmed = True
            if self.status == DELIVERY_UNKNOWN:
                self.status = DELIVERY_DELIVERED
        if self.accepted and self.queued and not self.confirmed and self.status == DELIVERY_UNKNOWN:
            self.status = DELIVERY_QUEUED
        if self.live_dispatched and not self.confirmed and self.status == DELIVERY_UNKNOWN:
            self.status = DELIVERY_LIVE_SENT
        if not self.success and self.status == DELIVERY_UNKNOWN and (self.error or self.error_code):
            self.status = DELIVERY_FAILED

    @classmethod
    def already_claimed(cls, message_id: str) -> "DeliveryResult":
        return cls(
            success=True,
            accepted=True,
            queued=True,
            live_dispatched=False,
            confirmed=False,
            message_id=message_id,
            transport="message_bus",
            detail="dispatch already claimed or completed",
            status=DELIVERY_QUEUED,
            error_code="ALREADY_CLAIMED",
        )


@dataclass
class BroadcastResult:
    """Outcome of fan-out messaging to multiple agents."""

    success: bool
    message: str
    delivered: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    results: list[CommandResult] = field(default_factory=list)
    error_code: Optional[str] = None


@dataclass
class OnboardResult:
    """Outcome of a local PyAutoGUI onboard operation."""

    success: bool
    message: str
    action: str
    data: Optional[dict[str, Any]] = None
    error_code: Optional[str] = None


@dataclass
class PostMessage:
    agent: str
    title: str
    message: str
    dry_run: bool = False

    def to_embed_payload(self) -> dict[str, Any]:
        return {
            "embeds": [
                {
                    "title": self.title,
                    "description": self.message,
                    "fields": [
                        {"name": "Agent", "value": self.agent, "inline": True},
                    ],
                }
            ],
        }
