#!/usr/bin/env python3
"""Tests for the thin Dream.OS Control Plane MCP facade."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_servers"))

import dreamos_control_plane_server as server  # noqa: E402


APPROVED_TOOLS = {
    "inspect_branch_delete_request",
    "dry_run_approved_branch_delete",
    "execute_approved_branch_delete",
    "get_branch_delete_receipt",
    "list_bots",
    "bot_status",
    "list_channels",
    "send_message",
    "send_embed",
    "send_agent_command",
    "fleet_status",
    "task_status",
    "collect_results",
    "list_webhooks",
    "health",
    "recent_delivery_receipts",
}


def _call(name: str, arguments: dict | None = None) -> dict:
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        }
    )
    assert response is not None
    text = response["result"]["content"][0]["text"]
    return json.loads(text)


def test_initialize_succeeds():
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert response is not None
    assert response["result"]["serverInfo"]["name"] == "dreamos-control-plane"


def test_tools_list_exposes_only_approved_tools():
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    assert response is not None
    tools = {tool["name"] for tool in response["result"]["tools"]}
    assert tools == APPROVED_TOOLS
    assert "delete_ref" not in tools
    assert "shell" not in tools
    assert "branch_delete_receipt" not in tools


def test_malformed_branch_delete_request_fails_closed():
    result = _call("inspect_branch_delete_request", {"request_path": r"D:\not-allowed.json"})
    assert result["ok"] is False
    assert "branch_delete_requests" in result["error"]


def test_destructive_call_without_confirm_fails_closed():
    result = _call(
        "execute_approved_branch_delete",
        {"request_path": "runtime/manifests/branch_delete_requests/websites_maskzero_salvage_20260813.branch_delete.json"},
    )
    assert result["ok"] is False
    assert "confirm_delete" in result["error"]


def test_config_responses_do_not_return_secrets(monkeypatch):
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/secret/token")
    monkeypatch.setenv("DISCORD_AGENT_1_CHANNEL_ID", "123456789")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "bot-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("GITHUB_TOKEN", "github-secret")

    for result in [_call("list_webhooks"), _call("list_channels")]:
        text = json.dumps(result)
        assert "secret/token" not in text
        assert "bot-secret" not in text
        assert "openai-secret" not in text
        assert "github-secret" not in text
        assert "123456789" not in text
        assert "DISCORD_WEBHOOK_URL" not in text
