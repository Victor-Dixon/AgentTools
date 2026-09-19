#!/usr/bin/env python3
"""Dream.OS Control Plane — Streamable HTTP MCP + OAuth discovery (tunnel-client compatible).

Exposes:
  POST /mcp
  GET  /.well-known/oauth-protected-resource/mcp
  GET  /.well-known/oauth-authorization-server
  GET  /oauth/authorize
  POST /oauth/token
  GET  /readyz

Stdio MCP remains in dreamos_control_plane_server.py for legacy paths; tunnel should use
--mcp-server-url pointing at this HTTP listener once OAuth discovery is required.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

MCP_DIR = os.path.dirname(os.path.abspath(__file__))
if MCP_DIR not in sys.path:
    sys.path.insert(0, MCP_DIR)

import dreamos_control_plane_oauth as oauth  # noqa: E402
import dreamos_control_plane_server as cps  # noqa: E402

MCP_PATH = "/mcp"
PRM_SUFFIX = "/.well-known/oauth-protected-resource/mcp"
PRM_ROOT_SUFFIX = "/.well-known/oauth-protected-resource"
AS_SUFFIX = "/.well-known/oauth-authorization-server"
OIDC_SUFFIX = "/.well-known/openid-configuration"

STORE = oauth.OAuthStore()
SERVER_STATE: dict[str, Any] = {"base_url": "", "listen_addr": ""}


class DreamOSControlPlaneHandler(BaseHTTPRequestHandler):
    server_version = "DreamOSControlPlaneHTTP/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        if os.environ.get("DREAMOS_MCP_HTTP_QUIET") == "1":
            return
        super().log_message(fmt, *args)

    @property
    def base_url(self) -> str:
        return SERVER_STATE.get("base_url") or f"http://{self.headers.get('Host', '127.0.0.1')}"

    @property
    def resource_metadata_url(self) -> str:
        return self.base_url.rstrip("/") + PRM_SUFFIX

    def _send_json(self, status: int, payload: dict[str, Any], extra_headers: dict[str, str] | None = None) -> None:
        body = oauth.json_response_body(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status: int, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status: int, text: str, extra_headers: dict[str, str] | None = None) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return b""
        return self.rfile.read(length)

    def _parse_form(self, raw: bytes) -> dict[str, str]:
        text = raw.decode("utf-8", errors="replace")
        parsed = urllib.parse.parse_qs(text, keep_blank_values=True)
        return {k: (v[0] if v else "") for k, v in parsed.items()}

    def _client_id_from_request(self, form: dict[str, str]) -> str:
        client_id = form.get("client_id", "").strip()
        if client_id:
            return client_id
        auth_header = self.headers.get("Authorization", "")
        if auth_header.lower().startswith("basic "):
            import base64

            try:
                decoded = base64.b64decode(auth_header.split(" ", 1)[1]).decode("utf-8")
                client_id = decoded.split(":", 1)[0]
            except Exception:  # noqa: BLE001
                return ""
        return client_id.strip()

    def _oauth_log(self, event: str, **fields: Any) -> None:
        if os.environ.get("DREAMOS_OAUTH_DEBUG") == "1":
            print(json.dumps({"event": event, **fields}), flush=True)

    def do_GET(self) -> None:  # noqa: N802
        STORE.purge_expired()
        path = urllib.parse.urlparse(self.path).path

        if path == "/readyz":
            self._send_text(200, "ready\n")
            return

        if path == PRM_SUFFIX or path == PRM_ROOT_SUFFIX:
            self._send_json(200, oauth.protected_resource_metadata(self.base_url, MCP_PATH))
            return

        if path == AS_SUFFIX:
            self._send_json(200, oauth.authorization_server_metadata(self.base_url))
            return

        if path == OIDC_SUFFIX:
            self._send_json(200, oauth.openid_configuration_metadata(self.base_url))
            return

        if path == "/oauth/jwks":
            self._send_json(200, {"keys": []})
            return

        if path == "/oauth/authorize":
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query, keep_blank_values=True)
            client_id = (query.get("client_id") or [""])[0]
            redirect_uri = (query.get("redirect_uri") or [""])[0]
            scope_param = (query.get("scope") or [""])[0]
            state = (query.get("state") or [""])[0]
            code_challenge = (query.get("code_challenge") or [""])[0]
            code_challenge_method = (query.get("code_challenge_method") or ["S256"])[0]

            if not oauth.is_allowed_client(client_id):
                self._oauth_log("authorize_reject_client", client_id=client_id)
                self._send_text(400, "unsupported client_id\n")
                return
            if redirect_uri not in oauth.redirect_uris():
                self._send_text(400, "unsupported redirect_uri\n")
                return
            if code_challenge_method != "S256" or not code_challenge:
                self._send_text(400, "PKCE S256 required\n")
                return

            scopes = oauth.parse_requested_scopes(scope_param or None)
            auto = os.environ.get("DREAMOS_OAUTH_AUTO_APPROVE", "1") == "1"
            if auto:
                code = STORE.issue_auth_code(
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    scopes=scopes,
                    code_challenge=code_challenge,
                    code_challenge_method=code_challenge_method,
                )
                location = f"{redirect_uri}?code={urllib.parse.quote(code)}"
                if state:
                    location += f"&state={urllib.parse.quote(state)}"
                self.send_response(302)
                self.send_header("Location", location)
                self.end_headers()
                return

            hidden = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": " ".join(scopes),
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method,
            }
            html = oauth.consent_html(
                client_id=client_id,
                scopes=scopes,
                action_url="/oauth/authorize",
                hidden_fields=hidden,
            )
            self._send_html(200, html)
            return

        if path == MCP_PATH:
            self._send_text(
                401,
                "Unauthorized\n",
                extra_headers={
                    "WWW-Authenticate": oauth.www_authenticate_header(
                        self.resource_metadata_url, error="invalid_token"
                    )
                },
            )
            return

        self._send_text(404, "not found\n")

    def do_POST(self) -> None:  # noqa: N802
        STORE.purge_expired()
        path = urllib.parse.urlparse(self.path).path

        if path == "/oauth/authorize":
            form = self._parse_form(self._read_body())
            if form.get("approve") != "1":
                self._send_text(400, "approval required\n")
                return

            client_id = form.get("client_id", "")
            redirect_uri = form.get("redirect_uri", "")
            state = form.get("state", "")
            code_challenge = form.get("code_challenge", "")
            code_challenge_method = form.get("code_challenge_method", "S256")
            scopes = oauth.parse_requested_scopes(form.get("scope") or None)

            if not oauth.is_allowed_client(client_id) or redirect_uri not in oauth.redirect_uris():
                self._oauth_log("authorize_post_reject", client_id=client_id, redirect_uri=redirect_uri)
                self._send_text(400, "invalid client\n")
                return
            if code_challenge_method != "S256" or not code_challenge:
                self._send_text(400, "PKCE S256 required\n")
                return

            code = STORE.issue_auth_code(
                client_id=client_id,
                redirect_uri=redirect_uri,
                scopes=scopes,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
            )
            location = f"{redirect_uri}?code={urllib.parse.quote(code)}"
            if state:
                location += f"&state={urllib.parse.quote(state)}"
            self.send_response(302)
            self.send_header("Location", location)
            self.end_headers()
            return

        if path == "/oauth/register":
            body = self._read_body()
            form = self._parse_form(body) if body else {}
            client_id = form.get("client_name") or form.get("client_id") or oauth.predefined_client_id()
            if not oauth.is_allowed_client(client_id):
                client_id = oauth.predefined_client_id()
            self._send_json(
                201,
                {
                    "client_id": client_id,
                    "client_id_issued_at": int(__import__("time").time()),
                    "redirect_uris": oauth.redirect_uris(),
                    "token_endpoint_auth_method": "none",
                    "grant_types": ["authorization_code"],
                    "response_types": ["code"],
                },
            )
            return

        if path == "/oauth/token":
            form = self._parse_form(self._read_body())
            grant_type = form.get("grant_type", "")
            if grant_type != "authorization_code":
                self._send_json(400, {"error": "unsupported_grant_type"})
                return

            code = form.get("code", "")
            redirect_uri = form.get("redirect_uri", "")
            client_id = self._client_id_from_request(form)
            code_verifier = form.get("code_verifier", "")

            auth_code = STORE.consume_auth_code(code)
            if auth_code is None:
                self._send_json(400, {"error": "invalid_grant"})
                return

            if not client_id:
                client_id = auth_code.client_id
            if client_id != auth_code.client_id:
                self._oauth_log(
                    "token_client_mismatch",
                    received=client_id,
                    expected=auth_code.client_id,
                )
                self._send_json(400, {"error": "invalid_client"})
                return
            if redirect_uri and auth_code.redirect_uri != redirect_uri:
                self._send_json(400, {"error": "invalid_grant", "error_description": "redirect_uri mismatch"})
                return
            if not oauth.verify_pkce(code_verifier, auth_code.code_challenge, auth_code.code_challenge_method):
                self._send_json(400, {"error": "invalid_grant", "error_description": "PKCE verification failed"})
                return

            access_token = STORE.issue_access_token(client_id=client_id, scopes=auth_code.scopes)
            self._send_json(
                200,
                {
                    "access_token": access_token,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": " ".join(auth_code.scopes),
                },
            )
            return

        if path == MCP_PATH:
            auth_header = self.headers.get("Authorization")
            granted = STORE.resolve_bearer(auth_header)
            if granted is None:
                self._send_text(
                    401,
                    "Unauthorized\n",
                    extra_headers={
                        "WWW-Authenticate": oauth.www_authenticate_header(
                            self.resource_metadata_url, error="invalid_token"
                        )
                    },
                )
                return

            raw = self._read_body()
            if not raw:
                self._send_text(400, "empty body\n")
                return

            try:
                request = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                self._send_text(400, f"malformed json: {exc}\n")
                return

            method = request.get("method")
            enforce = method == "tools/call"
            response = cps.handle(request, granted_scopes=granted, enforce_oauth=enforce)
            if response is None:
                self.send_response(202)
                self.end_headers()
                return

            self._send_json(200, response)
            return

        self._send_text(404, "not found\n")


def run_server(listen_addr: str, *, tls_cert: Path | None = None, tls_key: Path | None = None) -> ThreadingHTTPServer:
    host, _, port_text = listen_addr.rpartition(":")
    if not host:
        host, port_text = "127.0.0.1", listen_addr
    port = int(port_text)
    httpd = ThreadingHTTPServer((host, port), DreamOSControlPlaneHandler)
    scheme = "http"
    if tls_cert and tls_key:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=str(tls_cert), keyfile=str(tls_key))
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
        scheme = "https"
    actual_host, actual_port = httpd.server_address[:2]
    base = f"{scheme}://{actual_host}:{actual_port}"
    SERVER_STATE["base_url"] = base
    SERVER_STATE["listen_addr"] = f"{actual_host}:{actual_port}"
    SERVER_STATE["scheme"] = scheme
    return httpd


def main() -> int:
    parser = argparse.ArgumentParser(description="Dream.OS Control Plane HTTP MCP + OAuth discovery")
    parser.add_argument(
        "--listen-addr",
        default=os.environ.get("DREAMOS_MCP_HTTP_ADDR", "127.0.0.1:59134"),
        help="Listen address (default 127.0.0.1:59134 or DREAMOS_MCP_HTTP_ADDR)",
    )
    parser.add_argument("--tls", action="store_true", help="Serve HTTPS (required for tunnel OAuth/harpoon registration)")
    parser.add_argument("--tls-cert", default=os.environ.get("DREAMOS_MCP_TLS_CERT", ""))
    parser.add_argument("--tls-key", default=os.environ.get("DREAMOS_MCP_TLS_KEY", ""))
    args = parser.parse_args()

    tls_cert = Path(args.tls_cert) if args.tls_cert else None
    tls_key = Path(args.tls_key) if args.tls_key else None
    if args.tls and (not tls_cert or not tls_key):
        default_dir = Path.home() / ".local" / "state" / "tunnel-client" / "tls"
        tls_cert = default_dir / "dreamos-mcp-local.crt"
        tls_key = default_dir / "dreamos-mcp-local.key"

    httpd = run_server(args.listen_addr, tls_cert=tls_cert if args.tls else None, tls_key=tls_key if args.tls else None)
    base = SERVER_STATE["base_url"]
    print(f"MCP listening on {base}", flush=True)
    print(f"MCP URL: {base}{MCP_PATH}", flush=True)
    print(f"Protected resource metadata: {base}{PRM_SUFFIX}", flush=True)
    print(f"Authorization server metadata: {base}{AS_SUFFIX}", flush=True)
    print(
        "ChatGPT predefined client_id: "
        f"{oauth.predefined_client_id()} (token_endpoint_auth_method=none, PKCE S256)",
        flush=True,
    )

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
