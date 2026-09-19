#!/usr/bin/env python3
"""OAuth discovery + HTTP MCP tests for Dream.OS Control Plane."""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_servers"))

import dreamos_control_plane_http_server as http_srv  # noqa: E402
import dreamos_control_plane_oauth as oauth  # noqa: E402
import dreamos_control_plane_server as cps  # noqa: E402


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture()
def http_base():
    port = _free_port()
    httpd = http_srv.run_server(f"127.0.0.1:{port}")
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    yield base
    httpd.shutdown()
    httpd.server_close()


def test_tools_include_security_schemes_and_delete_hints():
    tools = cps.build_tools_list()
    delete_tool = next(t for t in tools if t["name"] == "execute_approved_branch_delete")
    assert delete_tool["annotations"]["destructiveHint"] is True
    assert delete_tool["securitySchemes"][0]["scopes"] == ["repo.branch.delete"]
    health = next(t for t in tools if t["name"] == "health")
    assert health["securitySchemes"][0]["scopes"] == ["dreamos.read"]
    assert health["annotations"]["readOnlyHint"] is True


def test_oauth_metadata_endpoints(http_base):
    with urllib.request.urlopen(f"{http_base}/.well-known/oauth-protected-resource/mcp") as resp:
        prm = json.loads(resp.read().decode())
    assert prm["resource"] == f"{http_base}/mcp"
    assert prm["authorization_servers"] == [http_base]
    assert "dreamos.read" in prm["scopes_supported"]

    with urllib.request.urlopen(f"{http_base}/.well-known/oauth-authorization-server") as resp:
        asm = json.loads(resp.read().decode())
    assert asm["authorization_endpoint"] == f"{http_base}/oauth/authorize"
    assert asm["token_endpoint"] == f"{http_base}/oauth/token"
    assert "S256" in asm["code_challenge_methods_supported"]
    assert "none" in asm["token_endpoint_auth_methods_supported"]


def test_mcp_unauthenticated_returns_401_with_resource_metadata(http_base):
    req = urllib.request.Request(
        f"{http_base}/mcp",
        data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == 401
    www = exc.value.headers.get("WWW-Authenticate", "")
    assert "oauth-protected-resource" in www


def test_pkce_token_flow_and_scoped_tool_call(http_base, monkeypatch):
    monkeypatch.setenv("DREAMOS_OAUTH_AUTO_APPROVE", "1")
    code_verifier = "test-verifier-0123456789012345678901234567890"
    challenge = oauth.pkce_s256_challenge(code_verifier)
    client_id = oauth.predefined_client_id()
    redirect_uri = oauth.redirect_uris()[0]

    auth_url = (
        f"{http_base}/oauth/authorize?"
        f"response_type=code&client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope=dreamos.read&code_challenge={challenge}&code_challenge_method=S256"
    )

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ARG002
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        opener.open(auth_url)
    except urllib.error.HTTPError as exc:
        assert exc.code == 302
        location = exc.headers.get("Location", "")
    else:
        raise AssertionError("expected redirect")

    assert "code=" in location
    parsed = urllib.parse.urlparse(location)
    code = urllib.parse.parse_qs(parsed.query)["code"][0]

    token_body = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": code_verifier,
        }
    ).encode()
    token_req = urllib.request.Request(
        f"{http_base}/oauth/token",
        data=token_body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(token_req) as resp:
        token_payload = json.loads(resp.read().decode())
    access_token = token_payload["access_token"]

    mcp_req = urllib.request.Request(
        f"{http_base}/mcp",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode(),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    with urllib.request.urlopen(mcp_req) as resp:
        payload = json.loads(resp.read().decode())
    assert payload["result"]["tools"]
    names = {t["name"] for t in payload["result"]["tools"]}
    assert "health" in names


def test_enforce_oauth_blocks_delete_without_scope():
    resp = cps.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "execute_approved_branch_delete",
                "arguments": {"request_path": "x", "confirm_delete": False},
            },
        },
        granted_scopes=["dreamos.read"],
        enforce_oauth=True,
    )
    assert "error" in resp
    assert "Insufficient OAuth scope" in resp["error"]["message"]
