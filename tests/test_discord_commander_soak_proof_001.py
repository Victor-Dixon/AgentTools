"""Discord Commander soak proof: 1500-char enqueue, exactly-one live_sent, DISPATCH≠SENT."""

from __future__ import annotations

import asyncio
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent_tools.discord_commander.bilateral_sent_proof import (
    STATUS_DISPATCH_UNCONFIRMED,
    STATUS_NOT_SENT,
    STATUS_SENT,
    classify_bilateral_sent,
    extract_verification_mode,
)
from agent_tools.discord_commander.delivery_claim_ledger import DeliveryClaimLedger
from agent_tools.discord_commander.models import DELIVERY_QUEUED
from agent_tools.discord_commander.utils.message_chunking import (
    MAX_MESSAGE_LENGTH,
    chunk_message,
)


SOAK_BODY = "W" * 1500


def test_1500_char_body_is_one_discord_chunk() -> None:
    chunks = chunk_message(SOAK_BODY)
    assert len(SOAK_BODY) == 1500
    assert len(SOAK_BODY) < MAX_MESSAGE_LENGTH
    assert len(chunks) == 1
    assert chunks[0] == SOAK_BODY


def test_dispatch_only_is_not_sent() -> None:
    proof = classify_bilateral_sent(
        dispatch_success=True,
        verification_mode="dispatch_only",
    )
    assert proof["status"] == STATUS_DISPATCH_UNCONFIRMED
    assert proof["status"] != STATUS_SENT


def test_clipboard_proxy_and_nonce_fail_are_not_sent(tmp_path: Path) -> None:
    inbox = tmp_path / "a2a_from_Agent-4_msg.json"
    inbox.write_text("{}", encoding="utf-8")
    proxy = classify_bilateral_sent(
        dispatch_success=True,
        verification_mode="clipboard_proxy",
        inbox_path=inbox,
    )
    nonce = classify_bilateral_sent(
        dispatch_success=True,
        verification_mode="nonce_verify_failed",
        inbox_path=inbox,
    )
    assert proxy["status"] == STATUS_NOT_SENT
    assert nonce["status"] == STATUS_NOT_SENT


def test_inbox_plus_uia_is_sent(tmp_path: Path) -> None:
    inbox = tmp_path / "a2a_from_Agent-4_msg.json"
    inbox.write_text('{"schema":"dreamvault.a2a_inbox.v1"}', encoding="utf-8")
    proof = classify_bilateral_sent(
        dispatch_success=True,
        verification_mode="uia",
        inbox_path=inbox,
    )
    assert proof["status"] == STATUS_SENT


def test_inbox_plus_partner_reply_is_sent(tmp_path: Path) -> None:
    inbox = tmp_path / "a2a_from_Agent-4_msg.json"
    inbox.write_text("{}", encoding="utf-8")
    proof = classify_bilateral_sent(
        dispatch_success=True,
        verification_mode="dispatch_only",
        inbox_path=inbox,
        partner_reply=True,
    )
    assert proof["status"] == STATUS_SENT


def test_extract_verification_mode_from_detail() -> None:
    assert extract_verification_mode("cursor_gui DISPATCH success=True") == "dispatch_only"
    assert extract_verification_mode("verification_mode=uia paste_landed=true") == "uia"
    assert extract_verification_mode("NONCE_VERIFY_FAILED clipboard_proxy") == "clipboard_proxy"


def test_soak_exactly_one_live_sent_under_claim_race(tmp_path: Path) -> None:
    ledger_path = tmp_path / "dispatch_claim_ledger.json"
    message_id = "soak_1500_msg_001"
    starter = DeliveryClaimLedger(ledger_path)
    starter.mark_queued(message_id, extra={"chars": 1500})

    acquired: list[bool] = []
    lock = threading.Lock()

    def _race() -> None:
        local = DeliveryClaimLedger(ledger_path)
        result = local.claim_dispatch(message_id)
        with lock:
            acquired.append(result.acquired)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_race) for _ in range(8)]
        for fut in futures:
            fut.result(timeout=5)

    assert acquired.count(True) == 1
    assert acquired.count(False) == 7

    winner = DeliveryClaimLedger(ledger_path)
    winner.mark_live_sent(message_id, detail="verification_mode=uia")
    assert winner.live_sent_count() == 1

    restarted = DeliveryClaimLedger(ledger_path)
    assert restarted.live_sent_count() == 1
    assert restarted.has_success(message_id) is True
    third = restarted.claim_dispatch(message_id)
    assert third.acquired is False
    assert third.detail == "already_succeeded"


def test_inline_dispatch_success_without_inbox_is_unconfirmed(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DISCORD_COMMANDER_DISPATCH_LEDGER", str(tmp_path / "ledger.json"))

    import agent_tools.discord_commander.message_bus_bridge as bridge

    monkeypatch.setattr(bridge, "default_ledger", lambda: DeliveryClaimLedger(tmp_path / "ledger.json"))

    class FakeDispatcher:
        @staticmethod
        def dispatch_next(*, paths, live, message_id):
            return SimpleNamespace(
                success=True,
                target_agent="Agent-1",
                detail="cursor_gui_adapter DISPATCHED submit=enter",
            )

    monkeypatch.setitem(
        sys.modules,
        "dreamvault.message_bus.dispatcher",
        FakeDispatcher,
    )
    monkeypatch.setitem(
        sys.modules,
        "dreamvault.runtime_bus",
        SimpleNamespace(RuntimeBusError=RuntimeError),
    )

    ok, detail, meta = bridge._inline_dispatch_with_claim(
        paths=SimpleNamespace(),
        bus_message_id="bus_soak_unconfirmed_001",
        agent_id="Agent-1",
        meta={},
    )
    assert ok is True
    assert meta["delivery_status"] == "DISPATCH_UNCONFIRMED"
    assert meta["confirmed"] is False
    assert meta["live_dispatched"] is True
    assert "DISPATCH" in detail
    assert DeliveryClaimLedger(tmp_path / "ledger.json").live_sent_count() == 0


def test_inline_dispatch_uia_inbox_marks_live_sent(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DISCORD_COMMANDER_DISPATCH_LEDGER", str(tmp_path / "ledger.json"))
    inbox = tmp_path / "inbox.json"
    inbox.write_text('{"schema":"dreamvault.a2a_inbox.v1"}', encoding="utf-8")

    import agent_tools.discord_commander.message_bus_bridge as bridge

    monkeypatch.setattr(bridge, "default_ledger", lambda: DeliveryClaimLedger(tmp_path / "ledger.json"))

    class FakeDispatcher:
        @staticmethod
        def dispatch_next(*, paths, live, message_id):
            return SimpleNamespace(
                success=True,
                target_agent="Agent-3",
                detail="verification_mode=uia paste_landed=true",
            )

    monkeypatch.setitem(sys.modules, "dreamvault.message_bus.dispatcher", FakeDispatcher)
    monkeypatch.setitem(
        sys.modules,
        "dreamvault.runtime_bus",
        SimpleNamespace(RuntimeBusError=RuntimeError),
    )

    ok, detail, meta = bridge._inline_dispatch_with_claim(
        paths=SimpleNamespace(),
        bus_message_id="bus_soak_sent_001",
        agent_id="Agent-3",
        meta={"inbox_path": str(inbox)},
    )
    assert ok is True
    assert meta["delivery_status"] == "LIVE_SENT"
    assert meta["confirmed"] is True
    assert "SENT" in detail
    assert DeliveryClaimLedger(tmp_path / "ledger.json").live_sent_count() == 1


def test_async_1500_char_timeout_still_accepts(monkeypatch) -> None:
    from agent_tools.discord_commander.agent_message_sender import send_agent_message_async

    def slow_send(*args, **kwargs):
        import time

        time.sleep(2.0)
        raise AssertionError("should have timed out before completion")

    monkeypatch.setattr(
        "agent_tools.discord_commander.agent_message_sender.send_agent_message",
        slow_send,
    )
    result = asyncio.run(send_agent_message_async("Agent-1", SOAK_BODY, timeout=0.1))
    assert result.success is True
    assert result.error_code == "DELIVERY_CONFIRMATION_PENDING"
    assert result.data["final_status"] == DELIVERY_QUEUED
