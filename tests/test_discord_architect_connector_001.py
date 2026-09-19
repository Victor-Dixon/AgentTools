#!/usr/bin/env python3
"""Unit tests for Discord Architect Connector allowlist + dry-run defaults."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "mcp_servers"))

from agent_tools.discord_architect_connector import (  # noqa: E402
    read_channels,
    read_messages,
    security_contract,
    send_message_allowlisted,
)
import dreamos_control_plane_server as cps  # noqa: E402


def test_read_channels_includes_smoke_allowlist():
    out = read_channels()
    assert out["ok"] is True
    assert "smoke_test" in out["connector_allowlist"]
    keys = {c["route_key"] for c in out["channels"]}
    assert "smoke_test" in keys


def test_read_messages_blocks_non_allowlisted():
    out = read_messages(route_key="cpc_closeout", live=False)
    assert out["ok"] is False
    assert out["reason"] == "ROUTE_NOT_ALLOWLISTED"


def test_read_messages_dry_run_smoke():
    out = read_messages(route_key="smoke_test", live=False)
    assert out["ok"] is True
    assert out["dry_run"] is True
    assert out["messages"] == []


def test_send_allowlisted_dry_run_default():
    out = send_message_allowlisted("hello smoke", route_key="smoke_test")
    assert out["ok"] is True
    assert out["dry_run"] is True
    assert out["status"] == "DRY_RUN_PASS"


def test_send_blocks_non_allowlisted():
    out = send_message_allowlisted("nope", route_key="blocked_lane", dry_run=False, human_approved=True)
    assert out["ok"] is False
    assert out["reason"] == "ROUTE_NOT_ALLOWLISTED"


def test_send_live_without_human_approved_stays_dry():
    out = send_message_allowlisted(
        "probe", route_key="smoke_test", dry_run=False, human_approved=False
    )
    assert out["ok"] is True
    assert out["dry_run"] is True
    assert out["status"] == "BLOCKED_NEEDS_HUMAN_APPROVED"


def test_security_contract_forbids_escalation():
    out = security_contract()
    assert out["ok"] is True
    assert "live_deployment" in out["forbidden_without_authorization"]


def test_mcp_tools_include_connector_aliases():
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


def test_mcp_read_channels_call():
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
