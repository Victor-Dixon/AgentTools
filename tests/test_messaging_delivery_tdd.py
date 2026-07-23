"""TDD coverage for Discord Commander message delivery + audit logging."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agent_tools.discord_commander.agent_message_sender import send_agent_message
from agent_tools.discord_commander.delivery_preflight import (
    layout_has_in_bounds_agent,
    load_layouts,
    point_in_virtual_screen,
    resolve_layout_for_agent,
    validate_pyautogui_readiness,
)
from agent_tools.discord_commander.messaging_roots import resolve_agent_tools_root
from agent_tools.discord_commander.messaging_delivery_log import delivery_jsonl_path, record_delivery
from agent_tools.discord_commander.models import DeliveryResult
from agent_tools.discord_commander.pyautogui_transport import PyAutoGUITransport
from agent_tools.discord_commander.queue_bridge import deliver_message

VALID_WEBHOOK = "https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz1234567890"


class LiveLikeCursor:
    """Simulates real _Cursor — no .record attribute."""

    def move_click(self, x: int, y: int) -> None:
        pass

    def paste(self, text: str) -> None:
        pass

    def enter(self) -> None:
        pass

    def hotkey(self, *keys: str) -> None:
        pass


class FakeACP:
    def __init__(self) -> None:
        self._cursor = LiveLikeCursor()
        self._coords = {"Agent-1": {"input_box": {"x": 100, "y": 200}}}
        self._layout_mode = "test"
        self.send_called = False

    def _fmt_id(self, agent: str) -> str:
        return agent if agent.startswith("Agent-") else f"Agent-{agent}"

    def _coords_within_bounds(self, agent: str, x: int, y: int, label: str) -> bool:
        return True

    def send(self, agent_id: str, message: str, **kwargs) -> None:
        self.send_called = True


class TestDeliveryPreflight:
    def test_point_in_virtual_screen(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "agent_tools.discord_commander.delivery_preflight.get_virtual_screen",
            lambda: (0, 0, 1920, 1080),
        )
        assert point_in_virtual_screen(684, 429) is True
        assert point_in_virtual_screen(-1399, 486) is False

    def test_resolve_layout_prefers_in_bounds_over_env(self, tmp_path: Path, monkeypatch) -> None:
        coords = {
            "8-agent": {"Agent-1": {"input_box": {"x": -1399, "y": 486}}},
            "4-agent-1monitor": {"Agent-1": {"input_box": {"x": 684, "y": 429}}},
        }
        coords_file = tmp_path / "runtime" / "agent_comms"
        coords_file.mkdir(parents=True)
        (coords_file / "cursor_agent_coords.json").write_text(json.dumps(coords), encoding="utf-8")

        monkeypatch.setenv("AGENT_GAS_LAYOUT_MODE", "8-agent")
        monkeypatch.setattr(
            "agent_tools.discord_commander.delivery_preflight.get_virtual_screen",
            lambda: (0, 0, 1920, 1080),
        )
        layout, warning = resolve_layout_for_agent(tmp_path, "Agent-1")
        assert layout == "4-agent-1monitor"
        assert warning is not None
        assert "8-agent" in warning


class TestPyAutoGUITransportLiveMode:
    def _stub_transport(self) -> PyAutoGUITransport:
        transport = PyAutoGUITransport.__new__(PyAutoGUITransport)
        transport._layout_mode = "test"
        transport._test = True
        transport._use_ssot = False
        transport._root = Path(r"D:\Agent_Cellphone")
        transport._acp = FakeACP()
        return transport

    def test_live_cursor_send_succeeds_without_record_attr(self, monkeypatch) -> None:
        transport = self._stub_transport()
        monkeypatch.setattr(
            "agent_tools.discord_commander.pyautogui_transport.resolve_layout_for_agent",
            lambda root, agent: ("test", None),
        )
        result = transport.send("Agent-1", "hello")
        assert result.success is True
        assert transport._acp.send_called is True

    def test_coords_out_of_bounds_returns_actionable_error(self, monkeypatch) -> None:
        transport = self._stub_transport()
        transport._layout_mode = "8-agent"
        acp = FakeACP()
        acp._coords = {"Agent-1": {"input_box": {"x": -1399, "y": 486}}}
        acp._coords_within_bounds = lambda *args, **kwargs: False  # type: ignore[method-assign]
        transport._acp = acp
        monkeypatch.setattr(
            "agent_tools.discord_commander.pyautogui_transport.resolve_layout_for_agent",
            lambda root, agent: ("8-agent", None),
        )
        result = transport.send("Agent-1", "hello")
        assert result.success is False
        assert result.error_code == "COORDS_OUT_OF_BOUNDS"
        assert "Re-calibrate" in (result.detail or "")


class TestPyAutoGUITransportSSOT:
    def test_ssot_test_mode_send(self, monkeypatch) -> None:
        dv = Path(r"D:\DreamVault")
        if not (dv / "runtime" / "config" / "agent_transport" / "cursor_agent_coords.json").is_file():
            pytest.skip("DreamVault SSOT coords not present")
        monkeypatch.setenv("DREAMVAULT_AGENT_TRANSPORT_SSOT", "1")
        monkeypatch.setenv("DREAMVAULT_REPO_ROOT", str(dv))
        transport = PyAutoGUITransport(test=True)
        assert transport._use_ssot is True
        result = transport.send("Agent-1", "ssot probe", high_priority=True)
        assert result.success is True


class TestSendAgentMessageDelivery:
    def _mock_ready(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.validate_pyautogui_readiness",
            lambda agent_id, coords_root=None: SimpleNamespace(
                ready=True,
                coords_root=Path(r"D:\DreamVault"),
                layout_mode="4-agent-1monitor",
                error_code=None,
                detail=None,
                warnings=[],
            ),
        )

    def test_pyautogui_fail_returns_fail_no_webhook(self, monkeypatch) -> None:
        self._mock_ready(monkeypatch)
        class FailTransport:
            def send(self, agent_id: str, message: str, *, high_priority: bool = False) -> DeliveryResult:
                return DeliveryResult(
                    success=False,
                    error_code="COORDS_OUT_OF_BOUNDS",
                    detail="off screen",
                )

        monkeypatch.setenv("DISCORD_COMMANDER_USE_MESSAGE_BUS", "0")
        monkeypatch.setenv("DISCORD_COMMANDER_WEBHOOK_FALLBACK", "1")
        webhook = MagicMock(return_value=True)
        monkeypatch.setattr("agent_tools.discord_commander.outbound_router.DiscordService.send_embed", webhook)
        result = send_agent_message("Agent-1", "hi", transport=FailTransport())
        assert result.success is False
        assert result.data["final_status"] == "FAILED"
        assert result.error_code == "COORDS_OUT_OF_BOUNDS"
        webhook.assert_not_called()

    def test_pyautogui_success_does_not_hit_webhook(self, monkeypatch) -> None:
        self._mock_ready(monkeypatch)
        class OkTransport:
            def send(self, agent_id: str, message: str, *, high_priority: bool = False) -> DeliveryResult:
                return DeliveryResult(success=True)

        monkeypatch.setenv("DISCORD_COMMANDER_USE_MESSAGE_BUS", "0")
        webhook = MagicMock(return_value=True)
        monkeypatch.setattr("agent_tools.discord_commander.outbound_router.DiscordService.send_embed", webhook)
        result = send_agent_message("Agent-1", "hi", transport=OkTransport())
        assert result.success is True
        assert result.data["final_status"] == "SENT"
        assert result.data["transport"] == "pyautogui"
        webhook.assert_not_called()

    def test_bus_fail_falls_back_to_direct_pyautogui_single_audit(self, monkeypatch, tmp_path: Path) -> None:
        monkeypatch.setenv("DISCORD_COMMANDER_USE_MESSAGE_BUS", "1")
        monkeypatch.setenv("ALLOW_LIVE_CURSOR_INJECTION", "1")
        monkeypatch.setenv("DISCORD_COMMANDER_LOG_DIR", str(tmp_path))

        class OkTransport:
            def send(self, agent_id: str, message: str, *, high_priority: bool = False) -> DeliveryResult:
                return DeliveryResult(success=True)

        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.validate_pyautogui_readiness",
            lambda agent_id, coords_root=None: SimpleNamespace(
                ready=True,
                coords_root=Path(r"D:\DreamVault"),
                layout_mode="4-agent-1monitor",
                error_code=None,
                detail=None,
                warnings=[],
            ),
        )
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.send_via_message_bus",
            lambda **kwargs: (False, "bus failed", {"transport": "message_bus_processor_failed"}),
        )
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.get_transport",
            lambda transport=None: OkTransport(),
        )
        result = send_agent_message("Agent-1", "hi")
        assert result.success is True
        assert result.data["final_status"] == "SENT"
        assert result.data["transport"] == "pyautogui_bus_fallback"
        lines = delivery_jsonl_path().read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        payload = json.loads(lines[0])
        assert payload["success"] is True
        assert payload["extra"]["final_status"] == "SENT"

    def test_processor_timeout_skips_pyautogui_fallback_no_double_paste(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Regression: processor-owned D2A must not fall back to direct PyAutoGUI (double paste)."""
        monkeypatch.setenv("DISCORD_COMMANDER_USE_MESSAGE_BUS", "1")
        monkeypatch.setenv("ALLOW_LIVE_CURSOR_INJECTION", "1")
        monkeypatch.setenv("DISCORD_COMMANDER_LOG_DIR", str(tmp_path))

        class FailTransport:
            def send(self, agent_id: str, message: str, *, high_priority: bool = False) -> DeliveryResult:
                raise AssertionError("PyAutoGUI fallback must not run when processor owns delivery")

        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.validate_pyautogui_readiness",
            lambda agent_id, coords_root=None: SimpleNamespace(
                ready=True,
                coords_root=Path(r"D:\DreamVault"),
                layout_mode="4-agent-1monitor",
                error_code=None,
                detail=None,
                warnings=[],
            ),
        )
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.send_via_message_bus",
            lambda **kwargs: (
                False,
                "D2A enqueued but processor did not complete within 20s",
                {
                    "transport": "message_bus_processor_timeout",
                    "processor_running": True,
                    "bus_message_id": "d2a_discord_test_timeout_001",
                    "bus_final_status": "timeout",
                },
            ),
        )
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender._bus_message_terminal_status",
            lambda bus_message_id: "running",
        )
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.get_transport",
            lambda transport=None: FailTransport(),
        )
        result = send_agent_message("Agent-1", "hi")
        assert result.success is False
        assert result.error_code == "BUS_PROCESSOR_PENDING"
        assert result.data.get("fallback_suppressed") in (
            "processor_owns_delivery_no_fallback",
            "bus_status_running_no_fallback",
        )
        lines = delivery_jsonl_path().read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

    def test_preflight_fail_single_failed_audit(self, monkeypatch, tmp_path: Path) -> None:
        monkeypatch.setenv("DISCORD_COMMANDER_USE_MESSAGE_BUS", "0")
        monkeypatch.setenv("DISCORD_COMMANDER_LOG_DIR", str(tmp_path))
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.validate_pyautogui_readiness",
            lambda agent_id, coords_root=None: SimpleNamespace(
                ready=False,
                coords_root=Path(r"D:\DreamVault"),
                layout_mode="8-agent",
                error_code="COORDS_OUT_OF_BOUNDS",
                detail="off screen",
                warnings=[],
            ),
        )
        result = send_agent_message("Agent-1", "hi")
        assert result.success is False
        assert result.data["final_status"] == "FAILED"
        assert result.error_code == "COORDS_OUT_OF_BOUNDS"
        lines = delivery_jsonl_path().read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["success"] is False

    def test_bus_enqueues_even_when_preflight_not_ready(self, monkeypatch, tmp_path: Path) -> None:
        """Regression: FAILED preflight must not drop D2A before the queue."""
        monkeypatch.setenv("DISCORD_COMMANDER_USE_MESSAGE_BUS", "1")
        monkeypatch.setenv("DISCORD_COMMANDER_LOG_DIR", str(tmp_path))
        monkeypatch.delenv("ALLOW_LIVE_CURSOR_INJECTION", raising=False)
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.bootstrap_commander_env",
            lambda: None,
        )
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.validate_pyautogui_readiness",
            lambda agent_id, coords_root=None: SimpleNamespace(
                ready=False,
                coords_root=Path(r"D:\DreamVault"),
                layout_mode="4-agent-1monitor",
                error_code="LIVE_INJECTION_DISABLED",
                detail="Set ALLOW_LIVE_CURSOR_INJECTION=1 for live PyAutoGUI delivery",
                warnings=[],
            ),
        )
        monkeypatch.setattr(
            "agent_tools.discord_commander.agent_message_sender.send_via_message_bus",
            lambda **kwargs: (
                True,
                "D2A accepted for Agent-1; queued on message bus",
                {
                    "transport": "message_bus_enqueue_only",
                    "delivery_status": "QUEUED",
                    "bus_message_id": "d2a_preflight_bypass_001",
                    "message_id": "d2a_preflight_bypass_001",
                    "queued": True,
                    "confirmed": False,
                },
            ),
        )
        result = send_agent_message("Agent-1", "hi from discord")
        assert result.success is True
        assert result.data["final_status"] == "QUEUED"
        assert result.data["transport"] == "message_bus_enqueue_only"
        assert result.data["bus_message_id"] == "d2a_preflight_bypass_001"
        lines = delivery_jsonl_path().read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["success"] is True


class TestMessagingRoots:
    def test_resolve_agent_tools_root_from_package(self) -> None:
        root = resolve_agent_tools_root()
        assert (root / "src" / "agent_tools").is_dir()


class TestPyAutoGUIReadinessGate:
    def test_live_injection_required(self, monkeypatch) -> None:
        monkeypatch.delenv("ALLOW_LIVE_CURSOR_INJECTION", raising=False)
        result = validate_pyautogui_readiness("Agent-1")
        assert result.ready is False
        assert result.error_code == "LIVE_INJECTION_DISABLED"


class TestMessagingDeliveryLog:
    def test_record_delivery_writes_jsonl(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("DISCORD_COMMANDER_LOG_DIR", str(tmp_path))
        record_delivery(
            source="test",
            agent_id="Agent-1",
            transport="pyautogui",
            success=False,
            message_preview="hello",
            error_code="COORDS_OUT_OF_BOUNDS",
            detail="off screen",
        )
        lines = delivery_jsonl_path().read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        payload = json.loads(lines[0])
        assert payload["success"] is False
        assert payload["error_code"] == "COORDS_OUT_OF_BOUNDS"


class TestMessagingRootsCoordsSSOT:
    def test_apply_messaging_roots_prefers_dreamvault_over_legacy_pollution(self, monkeypatch) -> None:
        """AgentTools = code root; DreamVault = coords SSOT even if legacy env was forced."""
        from agent_tools.discord_commander.messaging_roots import apply_messaging_roots

        dv = Path(r"D:\DreamVault")
        if not (dv / "runtime" / "config" / "agent_transport" / "cursor_agent_coords.json").is_file():
            pytest.skip("DreamVault SSOT coords not present")
        monkeypatch.setenv("AGENT_CELLPHONE_ROOT", r"D:\repos\Agent_Cellphone")
        monkeypatch.setenv("DREAMVAULT_ROOT", str(dv))
        roots = apply_messaging_roots()
        assert Path(roots["agent_tools_root"]).name.lower() in {"agent-tools", "agent_tools"} or "agent-tools" in roots[
            "agent_tools_root"
        ].lower()
        assert Path(roots["coords_root"]).resolve() == dv.resolve()
        assert Path(os.environ["AGENT_CELLPHONE_ROOT"]).resolve() == dv.resolve()
        assert roots["transport_ssot"] is True


class TestQueueBridgeDeliveryResult:
    def test_deliver_message_returns_delivery_result(self, monkeypatch) -> None:
        monkeypatch.setenv("DISCORD_COMMANDER_DISABLE_PYAUTOGUI", "1")
        result = deliver_message("x", "Agent-1", None)
        assert isinstance(result, DeliveryResult)
        assert result.error_code == "NO_TRANSPORT"
        assert "pyautogui" in (result.detail or "").lower()
