"""Tests for consolidated PyAutoGUI transport and queue processor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.message_queue_processor import (
    MessageQueueProcessor,
    MessageQueueStore,
)
from agent_tools.discord_commander.pyautogui_transport import (
    PyAutoGUITransport,
    resolve_agent_cellphone_root,
)
from agent_tools.discord_commander.queue_bridge import deliver_message, load_queue_processor


class FakeTransport:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send(self, agent_id: str, message: str, *, high_priority: bool = False) -> bool:
        self.sent.append((agent_id, message))
        return True


class TestMessageQueueProcessor:
    def test_process_one_delivers_pending(self, tmp_path: Path) -> None:
        store = MessageQueueStore(tmp_path / "queue.json")
        store.enqueue("Agent-1", "hello")
        transport = FakeTransport()
        processor = MessageQueueProcessor(store=store, transport=transport)

        assert processor.process_one() is True
        assert transport.sent == [("Agent-1", "hello")]

        items = json.loads(store.path.read_text(encoding="utf-8"))
        assert items[0]["status"] == "sent"

    def test_load_queue_processor_returns_processor(self) -> None:
        processor = load_queue_processor()
        assert hasattr(processor, "process_queue")


class TestPyAutoGUITransport:
    def test_resolve_agent_cellphone_root(self) -> None:
        root = resolve_agent_cellphone_root()
        if (Path(r"D:\Agent_Cellphone") / "src" / "services" / "agent_cell_phone.py").is_file():
            assert root is not None
            assert (root / "src" / "services" / "agent_cell_phone.py").is_file()

    @pytest.mark.skipif(
        not (Path(r"D:\Agent_Cellphone") / "src" / "services" / "agent_cell_phone.py").is_file(),
        reason="Agent_Cellphone not installed",
    )
    def test_test_mode_send_records(self, monkeypatch) -> None:
        transport = PyAutoGUITransport(test=True)
        monkeypatch.setattr(transport._acp, "_coords_within_bounds", lambda *args, **kwargs: True)
        result = transport.send("Agent-1", "ping")
        assert result.success is True
        assert transport._acp._cursor.record


class TestQueueBridge:
    def test_deliver_without_transport_returns_false(self, monkeypatch) -> None:
        monkeypatch.setenv("DISCORD_COMMANDER_DISABLE_PYAUTOGUI", "1")
        result = deliver_message("hi", "Agent-1", None)
        assert result.success is False
        assert result.error_code == "NO_TRANSPORT"

    def test_deliver_with_fake_transport(self) -> None:
        transport = FakeTransport()
        result = deliver_message("hi", "Agent-2", transport)
        assert result.success is True
        assert transport.sent == [("Agent-2", "hi")]
