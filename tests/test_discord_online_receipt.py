from __future__ import annotations

import asyncio
from types import SimpleNamespace

from agent_tools.discord_commander.online_receipt import OnlineReceiptPublisher


class FakeChannel:
    def __init__(self) -> None:
        self.name = "bot-dreamos-commander"
        self.guild = SimpleNamespace(name="Dream.OS", id=1)
        self.messages: list[str] = []

    async def send(self, message: str) -> SimpleNamespace:
        self.messages.append(message)
        return SimpleNamespace(id=len(self.messages))


def test_startup_and_reconnect_receipts_are_idempotent() -> None:
    channel = FakeChannel()
    guild = SimpleNamespace(text_channels=[channel])
    bot = SimpleNamespace(guilds=[guild], user="DreamOS Commander#0001")
    publisher = OnlineReceiptPublisher(bot)

    first = asyncio.run(publisher.emit_state_change())
    duplicate = asyncio.run(publisher.emit_state_change())
    publisher.mark_disconnected()
    reconnect = asyncio.run(publisher.emit_state_change())
    duplicate_reconnect = asyncio.run(publisher.emit_state_change())

    assert first["online_status"] == "startup"
    assert duplicate["reason_code"] == "NO_ONLINE_STATE_CHANGE"
    assert reconnect["online_status"] == "reconnected"
    assert duplicate_reconnect["reason_code"] == "NO_ONLINE_STATE_CHANGE"
    assert len(channel.messages) == 2
    assert all("token" not in message.lower() for message in channel.messages)


def test_missing_owned_channel_blocks_without_fallback_send() -> None:
    bot = SimpleNamespace(guilds=[], user="DreamOS Commander#0001")
    publisher = OnlineReceiptPublisher(bot)
    result = asyncio.run(publisher.emit_state_change())
    assert result["status"] == "blocked"
    assert result["reason_code"] == "BOT_RECEIPT_CHANNEL_MISSING"
