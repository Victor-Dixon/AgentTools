"""Data models for Discord Commander operations.

Adapted from Agent_Cellphone_V2_Repository/src/discord_commander/discord_models.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
