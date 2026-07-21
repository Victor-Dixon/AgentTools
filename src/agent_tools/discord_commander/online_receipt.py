"""State-change-only Discord startup and reconnect receipts."""

from __future__ import annotations

import os
import socket
from datetime import UTC, datetime
from typing import Any


def format_online_receipt(
    *,
    bot_identity: str,
    status: str,
    started_at: str,
    runtime_instance: str,
    guild: str,
    channel: str,
) -> str:
    if status not in {"startup", "reconnected"}:
        raise ValueError(f"unsupported receipt status: {status}")
    fields = {
        "bot_identity": bot_identity,
        "status": status,
        "started_at": started_at,
        "runtime_instance": runtime_instance,
        "guild": guild,
        "channel": f"#{channel.lstrip('#')}",
    }
    if any(not str(value).strip() for value in fields.values()):
        raise ValueError("online receipt fields must be non-empty")
    return "\n".join(
        ["🤖 **Dream.OS bot online**", *(f"{key}={value}" for key, value in fields.items())]
    )


class OnlineReceiptPublisher:
    """Emit one startup receipt and one receipt per observed reconnect."""

    def __init__(self, bot: Any, channel_name: str = "bot-dreamos-commander") -> None:
        self.bot = bot
        self.channel_name = channel_name
        self.started_at = datetime.now(UTC).isoformat()
        self.runtime_instance = (
            f"commander:{socket.gethostname()}:{os.getpid()}:{self.started_at}"
        )
        self.startup_sent = False
        self.disconnected = False
        self.reconnect_sent_for_outage = False

    def mark_disconnected(self) -> None:
        self.disconnected = True
        self.reconnect_sent_for_outage = False

    def _find_channel(self) -> Any | None:
        target = self.channel_name.lower().replace("#", "")
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.name.lower() == target:
                    return channel
        return None

    async def emit_state_change(self) -> dict[str, Any]:
        if not self.startup_sent:
            status = "startup"
        elif self.disconnected and not self.reconnect_sent_for_outage:
            status = "reconnected"
        else:
            return {"status": "skipped", "reason_code": "NO_ONLINE_STATE_CHANGE"}
        channel = self._find_channel()
        if channel is None:
            return {
                "status": "blocked",
                "reason_code": "BOT_RECEIPT_CHANNEL_MISSING",
                "channel": self.channel_name,
            }
        message = format_online_receipt(
            bot_identity=str(self.bot.user),
            status=status,
            started_at=self.started_at,
            runtime_instance=self.runtime_instance,
            guild=str(channel.guild.name or channel.guild.id),
            channel=self.channel_name,
        )
        sent = await channel.send(message)
        if status == "startup":
            self.startup_sent = True
        else:
            self.disconnected = False
            self.reconnect_sent_for_outage = True
        return {
            "status": "sent",
            "online_status": status,
            "channel": self.channel_name,
            "message_id": getattr(sent, "id", None),
        }
