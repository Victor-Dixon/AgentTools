#!/usr/bin/env python3
"""Gas 9 — MaskZero verify endpoint linked=true + link persistence across logout/login."""

from __future__ import annotations

import http.cookiejar
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "runtime/secrets/secrets.local.env"
OUT = ROOT / "data/reports/operator/maskzero_discord_link_gas9_verify_persistence_latest.json"
API = os.getenv("MASKZERO_DISCORD_LINK_API_URL", "https://maskzero.site/api/discord-link.php")
AUTH_API = os.getenv("MASKZERO_SPARK_AUTH_API_URL", "https://maskzero.site/api/spark-auth.php")
AT_ROOT = Path(os.getenv("AGENT_TOOLS_ROOT", "D:/agent-tools"))
AT_SRC = AT_ROOT / "src"
GUILD_ID = "1375298054357254257"
TEST_DISCORD_USER = "777666555444"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def parse_secret() -> str:
    if not SECRETS.is_file():
        return ""
    for raw in SECRETS.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if line.startswith("MASKZERO_DISCORD_BOT_SECRET="):
            return line.split("=", 1)[1].strip().strip("'").strip('"')
    return ""


def cookie_header(jar: http.cookiejar.CookieJar) -> str:
    parts = [f"{c.name}={c.value}" for c in jar if c.name == "maskzero_spark_session"]
    return "; ".join(parts)


def auth_opener(jar: http.cookiejar.CookieJar | None = None):
    jar = jar or http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)), jar


def auth_json(
    opener,
    method: str,
    url: str,
    body: dict | None = None,
) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with opener.open(req, timeout=25) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"message": raw[:200]}
        return exc.code, payload


def verify_discord(discord_user_id: str) -> tuple[int, dict]:
    url = f"{API}?{urlencode({'action': 'verify', 'discord_user_id': discord_user_id})}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw[:200]}


def verify_session(session_token: str) -> tuple[int, dict]:
    url = f"{API}?{urlencode({'action': 'verify'})}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Cookie", f"maskzero_spark_session={session_token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"raw": raw[:200]}


def register_ephemeral(opener, jar: http.cookiejar.CookieJar) -> tuple[bool, str, str, str, dict]:
    email = f"e2e-gas9-{int(time.time())}@dreamvault.test"
    password = f"E2ePass{int(time.time()) % 100000:05d}!"
    status, body = auth_json(
        opener,
        "POST",
        f"{AUTH_API}?action=register",
        {"email": email, "password": password, "username": "E2EGas9"},
    )
    if status != 200 or not body.get("ok"):
        return False, "", email, password, body
    user = body.get("user") or {}
    site_user_id = str(user.get("id") or "")
    jar_cookie = ""
    for c in jar:
        if c.name == "maskzero_spark_session":
            jar_cookie = c.value
    return bool(jar_cookie and site_user_id), jar_cookie, email, password, body


def generate_code(session_token: str) -> tuple[bool, str, dict]:
    payload = json.dumps({"character_id": "default"}).encode()
    req = urllib.request.Request(
        f"{API}?action=generate_code",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Cookie": f"maskzero_spark_session={session_token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode())
            if body.get("ok") and body.get("code"):
                return True, str(body["code"]), body
            return False, "", body
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            return False, "", json.loads(raw)
        except json.JSONDecodeError:
            return False, "", {"message": raw[:200]}


def consume_code(code: str, bot_secret: str, discord_user_id: str) -> dict:
    if str(AT_SRC) not in sys.path:
        sys.path.insert(0, str(AT_SRC))
    os.environ["MASKZERO_DISCORD_BOT_SECRET"] = bot_secret
    os.environ.setdefault("MASKZERO_DISCORD_LINK_API_URL", API)
    from agent_tools.discord_commander.maskzero_link_client import consume_link_code

    result = consume_link_code(code, discord_user_id, GUILD_ID)
    return {
        "ok": result.ok,
        "message": result.message,
        "link": result.link or {},
    }


def main() -> int:
    bot_secret = parse_secret()
    checks: list[dict] = []
    ok = True

    if not bot_secret:
        checks.append({"name": "bot_secret_configured", "pass": False})
        ok = False
    else:
        checks.append({"name": "bot_secret_configured", "pass": True})

    opener, jar = auth_opener()
    reg_ok, session, email, password, reg_body = register_ephemeral(opener, jar)
    site_user_id = str((reg_body.get("user") or {}).get("id") or "")
    checks.append(
        {
            "name": "ephemeral_register",
            "pass": reg_ok,
            "site_user_id": site_user_id[:20] + "..." if site_user_id else None,
        }
    )
    if not reg_ok:
        ok = False
    else:
        gen_ok, code, gen_body = generate_code(session)
        checks.append(
            {
                "name": "generate_code",
                "pass": gen_ok,
                "character_id": gen_body.get("character_id"),
            }
        )
        if not gen_ok:
            ok = False
        else:
            consume = consume_code(code, bot_secret, TEST_DISCORD_USER)
            checks.append(
                {
                    "name": "consume_link",
                    "pass": consume["ok"],
                    "character_id": consume["link"].get("character_id"),
                }
            )
            ok = ok and consume["ok"]

            if consume["ok"]:
                st_d, body_d = verify_discord(TEST_DISCORD_USER)
                linked_d = body_d.get("linked") is True and body_d.get("ok") is True
                char_d = (body_d.get("link") or {}).get("character_id")
                checks.append(
                    {
                        "name": "verify_by_discord_user_id",
                        "pass": linked_d and char_d == "default",
                        "status": st_d,
                        "linked": body_d.get("linked"),
                        "character_id": char_d,
                    }
                )
                ok = ok and linked_d and char_d == "default"

                st_s, body_s = verify_session(session)
                linked_s = body_s.get("linked") is True
                site_match = (body_s.get("link") or {}).get("site_user_id") == site_user_id
                checks.append(
                    {
                        "name": "verify_by_site_session",
                        "pass": linked_s and site_match,
                        "status": st_s,
                        "linked": body_s.get("linked"),
                    }
                )
                ok = ok and linked_s and site_match

                # Logout
                logout_status, logout_body = auth_json(
                    opener, "POST", f"{AUTH_API}?action=logout", {}
                )
                logout_ok = logout_status == 200 and logout_body.get("ok")
                checks.append(
                    {
                        "name": "spark_logout",
                        "pass": logout_ok,
                        "status": logout_status,
                    }
                )
                ok = ok and logout_ok

                # Re-login same account
                login_status, login_body = auth_json(
                    opener,
                    "POST",
                    f"{AUTH_API}?action=login",
                    {"username": email, "password": password},
                )
                new_session = ""
                for c in jar:
                    if c.name == "maskzero_spark_session":
                        new_session = c.value
                login_ok = login_status == 200 and login_body.get("ok") and bool(new_session)
                checks.append(
                    {
                        "name": "spark_relogin",
                        "pass": login_ok,
                        "status": login_status,
                    }
                )
                ok = ok and login_ok

                if login_ok:
                    st_s2, body_s2 = verify_session(new_session)
                    linked_s2 = body_s2.get("linked") is True
                    char_s2 = (body_s2.get("link") or {}).get("character_id")
                    checks.append(
                        {
                            "name": "verify_session_after_relogin",
                            "pass": linked_s2 and char_s2 == "default",
                            "linked": body_s2.get("linked"),
                            "character_id": char_s2,
                        }
                    )
                    ok = ok and linked_s2 and char_s2 == "default"

                    st_d2, body_d2 = verify_discord(TEST_DISCORD_USER)
                    linked_d2 = body_d2.get("linked") is True
                    checks.append(
                        {
                            "name": "verify_discord_after_relogin",
                            "pass": linked_d2,
                            "linked": body_d2.get("linked"),
                        }
                    )
                    ok = ok and linked_d2

    # Unlinked discord id should return linked=false
    st_u, body_u = verify_discord("000000000001")
    unlinked_ok = body_u.get("linked") is False and body_u.get("ok") is True
    checks.append(
        {
            "name": "verify_unlinked_discord_returns_false",
            "pass": unlinked_ok,
            "linked": body_u.get("linked"),
        }
    )
    ok = ok and unlinked_ok

    payload = {
        "schema": "dreamvault.maskzero_discord_link_gas9_verify_persistence.v1",
        "generated_at": utc_now(),
        "agent_id": "Agent-3",
        "gas_cycle": "9/10 cycle 44",
        "task_id": "maskzero_discord_account_link_gas4_deploy_verify_001",
        "pass": ok,
        "checks": checks,
        "character_card_rule": "link.character_id persists across spark logout/login",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"MASKZERO_GAS9_VERIFY_PERSISTENCE={'PASS' if ok else 'FAIL'}")
    print(f"OUT={OUT}")
    for row in checks:
        print(f"  [{'PASS' if row.get('pass') else 'FAIL'}] {row.get('name')}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
