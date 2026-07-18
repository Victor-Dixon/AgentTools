"""Enqueue-and-observe: Discord must not wait on PyAutoGUI / bus poll by default."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent_tools.discord_commander.delivery_claim_ledger import DeliveryClaimLedger
from agent_tools.discord_commander.message_bus_bridge import send_via_message_bus
from agent_tools.discord_commander.models import DELIVERY_QUEUED, DeliveryResult


def test_delivery_result_legacy_success_compat() -> None:
    result = DeliveryResult(success=True)
    assert result.accepted is True
    assert result.confirmed is True
    assert result.status == "DELIVERED"


def test_delivery_result_queued_fields() -> None:
    result = DeliveryResult(
        success=True,
        accepted=True,
        queued=True,
        confirmed=False,
        message_id="msg_1",
        transport="message_bus_enqueue_only",
        detail="queued",
        status=DELIVERY_QUEUED,
    )
    assert result.live_dispatched is False
    assert result.status == DELIVERY_QUEUED


def test_claim_ledger_idempotent(tmp_path: Path) -> None:
    ledger = DeliveryClaimLedger(tmp_path / "ledger.json")
    ledger.mark_queued("m1")
    first = ledger.claim_dispatch("m1")
    assert first.acquired is True
    second = ledger.claim_dispatch("m1")
    assert second.acquired is False
    ledger.mark_live_sent("m1", detail="ok")
    assert ledger.has_success("m1") is True
    third = ledger.claim_dispatch("m1")
    assert third.acquired is False
    assert third.detail == "already_succeeded"


def test_send_via_message_bus_enqueue_only_no_dispatch(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DISCORD_COMMANDER_DELIVERY_WAIT_SEC", "0")
    monkeypatch.setenv("DISCORD_COMMANDER_DISPATCH_LEDGER", str(tmp_path / "ledger.json"))
    monkeypatch.setenv("ALLOW_LIVE_CURSOR_INJECTION", "1")

    bus_msg = SimpleNamespace(
        id="bus_msg_enqueue_only_001",
        category=SimpleNamespace(value="D2A"),
        body="hello",
    )
    ingest_result = SimpleNamespace(bus_message=bus_msg, verify_markers=["D2A"])

    monkeypatch.setattr(
        "agent_tools.discord_commander.message_bus_bridge.resolve_dreamvault_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "agent_tools.discord_commander.message_bus_bridge.bootstrap_commander_env",
        lambda: None,
    )
    monkeypatch.setattr(
        "agent_tools.discord_commander.message_bus_bridge.apply_messaging_roots",
        lambda: {},
    )
    monkeypatch.setattr(
        "agent_tools.discord_commander.message_bus_bridge.message_bus_processor_running",
        lambda root: True,
    )

    dispatch_mock = MagicMock(side_effect=AssertionError("dispatch_next must not run"))

    with patch.dict("sys.modules", {}):
        # Patch after import path setup inside function via monkeypatch on imported symbols.
        import agent_tools.discord_commander.message_bus_bridge as bridge

        monkeypatch.setattr(bridge, "_ensure_import", lambda root: None)

        class FakeIngress:
            @staticmethod
            def ingest_discord_message_command(*args, **kwargs):
                return ingest_result

        class FakeDispatcher:
            @staticmethod
            def default_bus_paths(root):
                return SimpleNamespace(state_path=tmp_path / "bus_state.json", repo_root=root)

            dispatch_next = staticmethod(dispatch_mock)

        class FakeBootstrap:
            @staticmethod
            def bootstrap_d2a_transport_env(root):
                return None

        monkeypatch.setitem(
            sys.modules,
            "dreamvault.discord.d2a_transport_bootstrap",
            FakeBootstrap,
        )
        monkeypatch.setitem(
            sys.modules,
            "dreamvault.discord.d2a_ingress_adapter",
            FakeIngress,
        )
        monkeypatch.setitem(
            sys.modules,
            "dreamvault.message_bus.dispatcher",
            FakeDispatcher,
        )

        ok, detail, meta = send_via_message_bus(
            agent_id="Agent-1",
            raw_content="hello from discord",
            sender="test",
            live=True,
        )

    assert ok is True
    assert meta["delivery_status"] == "QUEUED"
    assert meta["accepted"] is True
    assert meta["queued"] is True
    assert meta["confirmed"] is False
    assert meta["transport"] == "message_bus_enqueue_only"
    assert "queued on message bus" in detail.lower() or "accepted" in detail.lower()
    dispatch_mock.assert_not_called()


def test_send_agent_message_async_timeout_does_not_fail_accept(monkeypatch) -> None:
    import asyncio

    from agent_tools.discord_commander.agent_message_sender import send_agent_message_async

    def slow_send(*args, **kwargs):
        import time

        time.sleep(2.0)
        raise AssertionError("should have timed out before completion")

    monkeypatch.setattr(
        "agent_tools.discord_commander.agent_message_sender.send_agent_message",
        slow_send,
    )
    result = asyncio.run(send_agent_message_async("Agent-1", "hi", timeout=0.1))
    assert result.success is True
    assert result.error_code == "DELIVERY_CONFIRMATION_PENDING"
    assert result.data["final_status"] == DELIVERY_QUEUED
