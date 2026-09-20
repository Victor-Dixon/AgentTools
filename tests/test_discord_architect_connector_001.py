#!/usr/bin/env python3
"""Unit tests for Discord Architect Connector allowlist + dry-run defaults."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "mcp_servers"))

from agent_tools.discord_architect_connector import (  # noqa: E402
    LIVE_SEND_ENV,
    read_channels,
    read_messages,
    security_contract,
    send_message_allowlisted,
)
import dreamos_control_plane_server as cps  # noqa: E402


@pytest.fixture
def router_config(tmp_path, monkeypatch):
    cfg = {
        "routes": {
            "smoke_test": {
                "channel_name": "smoke-sessionz",
                "channel_id": "1234567890",
                "description": "fixture smoke channel",
            },
            "cpc_closeout": {
                "channel_name": "cpc-closeout",
                "channel_id": "999",
                "description": "not allowlisted",
            },
        },
        "connector_allowlist": ["smoke_test"],
    }
    path = tmp_path / "discord_router_channels.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setenv("DISCORD_ROUTER_CONFIG", str(path))
    monkeypatch.delenv(LIVE_SEND_ENV, raising=False)
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    return path


def test_read_channels_includes_smoke_allowlist(router_config):
    out = read_channels()
    assert out["ok"] is True
    assert "smoke_test" in out["connector_allowlist"]
    keys = {c["route_key"] for c in out["channels"]}
    assert "smoke_test" in keys
    assert "DISCORD_BOT_TOKEN" not in json.dumps(out)


def test_read_messages_blocks_non_allowlisted(router_config):
    out = read_messages(route_key="cpc_closeout", live=False)
    assert out["ok"] is False
    assert out["reason"] == "ROUTE_NOT_ALLOWLISTED"


def test_read_messages_dry_run_smoke(router_config):
    out = read_messages(route_key="smoke_test", live=False)
    assert out["ok"] is True
    assert out["dry_run"] is True
    assert out["messages"] == []


def test_send_allowlisted_dry_run_default(router_config):
    out = send_message_allowlisted("hello smoke", route_key="smoke_test")
    assert out["ok"] is True
    assert out["dry_run"] is True
    assert out["status"] == "DRY_RUN_PASS"
    assert out["receipt"]["mode"] == "dry_run"
    assert out["receipt"]["client_human_approved_trusted"] is False


def test_send_blocks_non_allowlisted(router_config):
    out = send_message_allowlisted(
        "nope", route_key="blocked_lane", dry_run=False, human_approved=True
    )
    assert out["ok"] is False
    assert out["reason"] == "ROUTE_NOT_ALLOWLISTED"


def test_client_human_approved_is_not_authorization(router_config):
    out = send_message_allowlisted(
        "probe", route_key="smoke_test", dry_run=False, human_approved=True
    )
    assert out["ok"] is False
    assert out["reason"] == "LIVE_SEND_ENV_GATE"
    assert out["client_human_approved_trusted"] is False
    assert out["receipt"]["client_human_approved"] is True
    assert out["receipt"]["client_human_approved_trusted"] is False
    assert out["receipt"]["live_env_gate"] is False


def test_live_send_env_gate_default_off(router_config):
    out = send_message_allowlisted(
        "probe", route_key="smoke_test", dry_run=False, human_approved=False
    )
    assert out["ok"] is False
    assert out["reason"] == "LIVE_SEND_ENV_GATE"


def test_live_send_uses_env_gate_not_client_flag(router_config, monkeypatch):
    monkeypatch.setenv(LIVE_SEND_ENV, "1")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test-token-not-a-secret")
    fake_resp = MagicMock()
    fake_resp.read.return_value = b'{"id": "msg-1"}'
    fake_resp.__enter__.return_value = fake_resp
    fake_resp.__exit__.return_value = False
    with patch(
        "agent_tools.discord_architect_connector.urllib.request.urlopen",
        return_value=fake_resp,
    ) as mocked:
        out = send_message_allowlisted(
            "authorized smoke",
            route_key="smoke_test",
            dry_run=False,
            human_approved=False,
        )
    assert mocked.called
    assert out["ok"] is True
    assert out["status"] == "SENT"
    assert out["message_id"] == "msg-1"
    assert out["receipt"]["mode"] == "live"
    assert out["receipt"]["client_human_approved_trusted"] is False
    assert "test-token-not-a-secret" not in json.dumps(out)


def test_security_contract_forbids_escalation(router_config):
    out = security_contract()
    assert out["ok"] is True
    assert "live_deployment" in out["forbidden_without_authorization"]
    assert out["defaults"]["client_human_approved_trusted"] is False
    assert out["defaults"]["live_env_gate_default"] == "off"


def test_mcp_tools_include_connector_aliases(router_config):
    resp = cps.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {t["name"] for t in resp["result"]["tools"]}
    for required in (
        "read_channels",
        "read_messages",
        "send_message_allowlisted",
        "dispatch_agent_message",
        "get_agent_status",
        "get_task_receipt",
        "connector_security_contract",
    ):
        assert required in names


def test_mcp_read_channels_call(router_config):
    resp = cps.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "read_channels", "arguments": {}},
        }
    )
    body = json.loads(resp["result"]["content"][0]["text"])
    assert body.get("ok") is True
    assert body.get("tool") == "read_channels"
