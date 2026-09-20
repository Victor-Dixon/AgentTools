#!/usr/bin/env python3
"""Tests for dreamos_control_plane_server MCP facade."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp_servers" / "dreamos_control_plane_server.py"
sys.path.insert(0, str(ROOT / "mcp_servers"))

import dreamos_control_plane_server as cps  # noqa: E402

GAB = Path(os.environ.get("GITHUB_ARCHITECT_BOT_ROOT", r"D:\Projects\github-architect-bot"))
MASKZERO = (
    GAB
    / "runtime"
    / "manifests"
    / "branch_delete_requests"
    / "websites_maskzero_salvage_20260813.branch_delete.json"
)


def test_no_raw_github_delete_in_server_source():
    text = SERVER.read_text(encoding="utf-8")
    assert "git/refs" not in text
    assert "-X DELETE" not in text
    assert "approved_branch_delete_lib" in text


def test_tools_list_includes_connector_and_excludes_shell():
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
        "health",
    ):
        assert required in names
    assert "delete_ref" not in names
    assert "shell" not in names
    assert "branch_delete_receipt" not in names


def test_initialize():
    resp = cps.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["serverInfo"]["name"] == "dreamos-control-plane"


def test_malformed_request_fails_closed():
    resp = cps.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "inspect_branch_delete_request",
                "arguments": {"request_path": r"C:\Windows\System32\drivers\etc\hosts"},
            },
        }
    )
    body = json.loads(resp["result"]["content"][0]["text"])
    assert body.get("ok") is False
    assert "must be inside" in str(body.get("error", "")).lower()


def test_execute_without_confirm_fails_closed():
    if not MASKZERO.is_file():
        pytest.skip("MaskZero request missing")
    out = cps.execute_approved_branch_delete(str(MASKZERO), confirm_delete=False)
    assert out["ok"] is False
    assert out["reason"] == "AUTHORITY_MISSING"


def test_maskzero_dry_run_pass():
    gab_lib = GAB / "runtime" / "scripts" / "approved_branch_delete_lib.py"
    if not MASKZERO.is_file() or not gab_lib.is_file():
        pytest.skip("GAB not available")
    manifest = json.loads(MASKZERO.read_text(encoding="utf-8"))
    if manifest.get("status") == "executed":
        receipt = cps.get_branch_delete_receipt()
        assert receipt.get("ok") is True or receipt.get("receipt")
        return
    out = cps.dry_run_approved_branch_delete(str(MASKZERO))
    assert out["status"] == "DRY_RUN_PASS"
    assert out["ok"] is True
    assert "approved_branch_delete_lib.py" in out["delegated_to"].replace("\\", "/")


def test_secret_redaction():
    dirty = {
        "webhook_url": "https://discord.com/api/webhooks/123/abc",
        "token": "supersecret",
        "nested": {"DISCORD_BOT_TOKEN": "tok", "ok": True},
        "text": "key=sk-abcdefghijklmnopqrstuvwxyz012345",
    }
    clean = cps._redact(dirty)
    assert clean["webhook_url"] == "configured"
    assert clean["token"] == "configured"
    assert clean["nested"]["DISCORD_BOT_TOKEN"] == "configured"
    assert "<redacted>" in clean["text"] or "sk-" not in clean["text"]


def test_list_webhooks_never_returns_urls(monkeypatch):
    monkeypatch.setenv(
        "DISCORD_WEBHOOK_URL",
        "https://discord.com/api/webhooks/999/super-secret-token",
    )
    out = cps.list_webhooks()
    blob = json.dumps(out)
    assert "super-secret-token" not in blob
    assert "https://discord.com/api/webhooks" not in blob
    assert out.get("configured") is True
    assert "webhook_env_keys" not in out


def test_discord_send_message_dry_run():
    out = cps.send_message(
        agent="Agent-1",
        title="t",
        message="m",
        dry_run=True,
    )
    assert out.get("dry_run") is True
