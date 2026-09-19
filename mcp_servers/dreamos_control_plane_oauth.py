"""OAuth helpers for Dream.OS Control Plane MCP (PKCE S256, public client)."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parents[1] / "runtime" / "config" / "dreamos_oauth_scopes.yaml"

DEFAULT_SCOPES = ["dreamos.read", "dreamos.write", "repo.branch.delete"]
DEFAULT_CLIENT_ID = "dreamos-chatgpt-connector"
DEFAULT_CALLBACK = "https://chatgpt.com/connector/oauth/QTOb4VcHdCsWsvg"


def _load_yaml_scopes() -> dict[str, Any]:
    if not CONFIG_PATH.is_file():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def scopes_supported() -> list[str]:
    cfg = _load_yaml_scopes()
    scopes = cfg.get("scopes_supported")
    if isinstance(scopes, list) and scopes:
        return [str(s) for s in scopes]
    return list(DEFAULT_SCOPES)


def default_scopes() -> list[str]:
    cfg = _load_yaml_scopes()
    scopes = cfg.get("default_scopes")
    if isinstance(scopes, list) and scopes:
        return [str(s) for s in scopes]
    return ["dreamos.read"]


def predefined_client_id() -> str:
    cfg = _load_yaml_scopes()
    client = cfg.get("predefined_client") or {}
    if isinstance(client, dict) and client.get("client_id"):
        return str(client["client_id"])
    return os.environ.get("DREAMOS_OAUTH_CLIENT_ID", DEFAULT_CLIENT_ID)


def allowed_client_ids() -> set[str]:
    cfg = _load_yaml_scopes()
    ids: set[str] = {predefined_client_id()}
    extra = cfg.get("allowed_client_ids")
    if isinstance(extra, list):
        ids.update(str(x) for x in extra if x)
    env_extra = os.environ.get("DREAMOS_OAUTH_EXTRA_CLIENT_IDS", "")
    if env_extra.strip():
        ids.update(x.strip() for x in env_extra.split(",") if x.strip())
    return ids


def is_allowed_client(client_id: str, *, strict: bool = False) -> bool:
    """Public User-Defined OAuth: accept configured IDs; authorize may accept any non-empty id."""
    if not client_id:
        return False
    if client_id in allowed_client_ids():
        return True
    if strict:
        return False
    # User-Defined OAuth Client — operator registers the same string in ChatGPT + auth server.
    return len(client_id.strip()) >= 3


def redirect_uris() -> list[str]:
    cfg = _load_yaml_scopes()
    client = cfg.get("predefined_client") or {}
    uris = client.get("redirect_uris") if isinstance(client, dict) else None
    if isinstance(uris, list) and uris:
        return [str(u) for u in uris]
    return [DEFAULT_CALLBACK]


def pkce_s256_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def verify_pkce(code_verifier: str, code_challenge: str, method: str = "S256") -> bool:
    if method != "S256":
        return False
    if not code_verifier or not code_challenge:
        return False
    return secrets.compare_digest(pkce_s256_challenge(code_verifier), code_challenge)


@dataclass
class AuthCode:
    code: str
    client_id: str
    redirect_uri: str
    scopes: list[str]
    code_challenge: str
    code_challenge_method: str
    expires_at: float


@dataclass
class AccessToken:
    token: str
    client_id: str
    scopes: list[str]
    expires_at: float


@dataclass
class OAuthStore:
    auth_codes: dict[str, AuthCode] = field(default_factory=dict)
    access_tokens: dict[str, AccessToken] = field(default_factory=dict)

    def issue_auth_code(
        self,
        *,
        client_id: str,
        redirect_uri: str,
        scopes: list[str],
        code_challenge: str,
        code_challenge_method: str,
        ttl_seconds: int = 300,
    ) -> str:
        code = secrets.token_urlsafe(32)
        self.auth_codes[code] = AuthCode(
            code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_at=time.time() + ttl_seconds,
        )
        return code

    def consume_auth_code(self, code: str) -> AuthCode | None:
        entry = self.auth_codes.pop(code, None)
        if entry is None:
            return None
        if entry.expires_at < time.time():
            return None
        return entry

    def issue_access_token(
        self,
        *,
        client_id: str,
        scopes: list[str],
        ttl_seconds: int = 3600,
    ) -> str:
        token = secrets.token_urlsafe(48)
        self.access_tokens[token] = AccessToken(
            token=token,
            client_id=client_id,
            scopes=scopes,
            expires_at=time.time() + ttl_seconds,
        )
        return token

    def resolve_bearer(self, authorization_header: str | None) -> list[str] | None:
        if not authorization_header:
            return None
        parts = authorization_header.strip().split(None, 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        token = parts[1].strip()
        entry = self.access_tokens.get(token)
        if entry is None:
            return None
        if entry.expires_at < time.time():
            self.access_tokens.pop(token, None)
            return None
        return list(entry.scopes)

    def purge_expired(self) -> None:
        now = time.time()
        for mapping in (self.auth_codes, self.access_tokens):
            expired = [k for k, v in mapping.items() if v.expires_at < now]
            for key in expired:
                mapping.pop(key, None)


def parse_requested_scopes(scope_param: str | None) -> list[str]:
    allowed = set(scopes_supported())
    if not scope_param:
        return default_scopes()
    requested = [s for s in scope_param.split() if s in allowed]
    return requested or default_scopes()


def scopes_allow(required: list[str], granted: list[str] | None) -> bool:
    if granted is None:
        return False
    granted_set = set(granted)
    return all(scope in granted_set for scope in required)


def protected_resource_metadata(base_url: str, mcp_path: str = "/mcp") -> dict[str, Any]:
    resource = base_url.rstrip("/") + mcp_path
    issuer = base_url.rstrip("/")
    return {
        "resource": resource,
        "authorization_servers": [issuer],
        "scopes_supported": scopes_supported(),
    }


def authorization_server_metadata(base_url: str) -> dict[str, Any]:
    root = base_url.rstrip("/")
    return {
        "issuer": root,
        "authorization_endpoint": f"{root}/oauth/authorize",
        "token_endpoint": f"{root}/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": scopes_supported(),
        "authorization_response_iss_parameter_supported": True,
        "registration_endpoint": f"{root}/oauth/register",
    }


def openid_configuration_metadata(base_url: str) -> dict[str, Any]:
    """OIDC discovery mirror — ChatGPT may validate PKCE via this document."""
    meta = authorization_server_metadata(base_url)
    root = base_url.rstrip("/")
    meta.update(
        {
            "jwks_uri": f"{root}/oauth/jwks",
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
    )
    return meta


def www_authenticate_header(resource_metadata_url: str, *, error: str | None = None) -> str:
    parts = [f'Bearer resource_metadata="{resource_metadata_url}"']
    if error:
        parts.append(f'error="{error}"')
        parts.append('error_description="Valid OAuth bearer token required"')
    return ", ".join(parts)


def consent_html(*, client_id: str, scopes: list[str], action_url: str, hidden_fields: dict[str, str]) -> str:
    scope_items = "".join(f"<li><code>{s}</code></li>" for s in scopes)
    hidden = "".join(
        f'<input type="hidden" name="{urllib.parse.quote(k)}" value="{urllib.parse.quote(v)}">'
        for k, v in hidden_fields.items()
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Dream.OS Control Plane</title></head>
<body>
<h1>Authorize Dream.OS Control Plane</h1>
<p>Client: <code>{client_id}</code></p>
<p>Requested scopes:</p><ul>{scope_items}</ul>
<form method="post" action="{action_url}">
{hidden}
<button type="submit" name="approve" value="1">Approve</button>
</form>
</body></html>"""


def json_response_body(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2).encode("utf-8")
