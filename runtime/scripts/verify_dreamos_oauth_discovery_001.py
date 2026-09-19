#!/usr/bin/env python3
"""Verify Dream.OS Control Plane OAuth discovery endpoints (local HTTP MCP)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mcp_servers"))

import dreamos_control_plane_oauth as oauth  # noqa: E402
import dreamos_control_plane_server as cps  # noqa: E402

DEFAULT_BASE = "http://127.0.0.1:59134"
OUT = (
    Path(r"D:\DreamVault")
    / "data"
    / "reports"
    / "control_plane"
    / "oauth_discovery_gate_latest.json"
)


def fetch_json(url: str) -> tuple[int, dict | None, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body), None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
            payload = json.loads(body) if body.strip().startswith("{") else None
        except Exception:  # noqa: BLE001
            payload = None
        return exc.code, payload, body
    except Exception as exc:  # noqa: BLE001
        return 0, None, str(exc)


def main() -> int:
    import os

    base = os.environ.get("DREAMOS_MCP_HTTP_BASE", DEFAULT_BASE).rstrip("/")
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    prm_url = f"{base}/.well-known/oauth-protected-resource/mcp"
    as_url = f"{base}/.well-known/oauth-authorization-server"
    mcp_url = f"{base}/mcp"

    prm_status, prm, prm_err = fetch_json(prm_url)
    as_status, asm, as_err = fetch_json(as_url)

    mcp_401 = False
    www_auth = None
    try:
        req = urllib.request.Request(mcp_url, method="POST", data=b"{}")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as exc:
        mcp_401 = exc.code == 401
        www_auth = exc.headers.get("WWW-Authenticate")
    except Exception as exc:  # noqa: BLE001
        prm_err = prm_err or str(exc)

    tools = cps.build_tools_list()
    delete_tool = next(t for t in tools if t["name"] == "execute_approved_branch_delete")
    has_delete_scope = any(
        s.get("scopes") == ["repo.branch.delete"]
        for s in delete_tool.get("securitySchemes", [])
        if isinstance(s, dict)
    )
    destructive = delete_tool.get("annotations", {}).get("destructiveHint") is True

    pkce_ok = isinstance(asm, dict) and "S256" in (asm.get("code_challenge_methods_supported") or [])
    token_none_ok = isinstance(asm, dict) and "none" in (
        asm.get("token_endpoint_auth_methods_supported") or []
    )
    scopes_ok = isinstance(asm, dict) and set(oauth.scopes_supported()).issubset(
        set(asm.get("scopes_supported") or [])
    )

    checks = {
        "protected_resource_200": prm_status == 200,
        "authorization_server_200": as_status == 200,
        "resource_present": bool(isinstance(prm, dict) and prm.get("resource")),
        "authorization_servers_present": bool(
            isinstance(prm, dict) and prm.get("authorization_servers")
        ),
        "auth_endpoint_present": bool(isinstance(asm, dict) and asm.get("authorization_endpoint")),
        "token_endpoint_present": bool(isinstance(asm, dict) and asm.get("token_endpoint")),
        "pkce_s256": pkce_ok,
        "token_auth_none": token_none_ok,
        "scopes_discovered": scopes_ok,
        "mcp_unauth_401": mcp_401,
        "www_authenticate_resource_metadata": bool(
            www_auth and "oauth-protected-resource" in (www_auth or "")
        ),
        "delete_tool_scope": has_delete_scope,
        "delete_tool_destructive_hint": destructive,
    }

    passed = all(checks.values())
    report = {
        "schema": "dreamvault.dreamos_oauth_discovery_gate.v1",
        "generated_at": now,
        "status": "PASS" if passed else "FAIL",
        "base_url": base,
        "urls": {
            "protected_resource": prm_url,
            "authorization_server": as_url,
            "mcp": mcp_url,
        },
        "checks": checks,
        "protected_resource": prm,
        "authorization_server": asm,
        "errors": {"prm": prm_err, "as": as_err},
        "chatgpt_connector": {
            "registration": "USER_DEFINED",
            "client_id": oauth.predefined_client_id(),
            "callback_uri": oauth.redirect_uris()[0],
            "token_endpoint_auth_method": "none",
            "base_scopes": [],
            "default_scopes": oauth.default_scopes(),
        },
        "next": [
            "Ensure HTTP MCP server running: python mcp_servers/dreamos_control_plane_http_server.py",
            "Restart tunnel with --mcp-server-url http://127.0.0.1:59134/mcp",
            "ChatGPT Scan/Review — verify Auth URL, Token URL, Resource populated before Create",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"STATUS={report['status']}")
    print(f"OUT={OUT}")
    print(json.dumps({"checks": checks, "status": report["status"]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
