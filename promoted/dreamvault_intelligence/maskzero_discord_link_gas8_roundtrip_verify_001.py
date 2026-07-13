#!/usr/bin/env python3
"""Gas 8 — MaskZero generate→consume round-trip (Enter Code /connect path).

Requires one of:
  MASKZERO_E2E_SPARK_SESSION  — session cookie value (manual browser capture)
  MASKZERO_E2E_LINK_CODE        — operator-generated code from live site
  MASKZERO_E2E_USERNAME + MASKZERO_E2E_PASSWORD — spark-auth login → auto generate

Without any of the above the script exits BLOCKED (exit 2) with operator instructions.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "runtime/secrets/secrets.local.env"
OUT = ROOT / "data/reports/operator/maskzero_discord_link_gas8_roundtrip_latest.json"
API = os.getenv("MASKZERO_DISCORD_LINK_API_URL", "https://maskzero.site/api/discord-link.php")
AUTH_API = os.getenv("MASKZERO_SPARK_AUTH_API_URL", "https://maskzero.site/api/spark-auth.php")
AT_ROOT = Path(os.getenv("AGENT_TOOLS_ROOT", "D:/agent-tools"))
AT_SRC = AT_ROOT / "src"
VPS_HOST = os.getenv("DREAMOS_VPS_HOST", "dreamos@2.25.64.233")
GUILD_ID = "1375298054357254257"
TEST_DISCORD_USER = "888777666555"


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def parse_secrets() -> dict[str, str]:
    values: dict[str, str] = {}
    if not SECRETS.is_file():
        return values
    for raw in SECRETS.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def http_json(
    method: str,
    url: str,
    *,
    body: dict | None = None,
    headers: dict[str, str] | None = None,
    cookie: str = "",
) -> tuple[int, dict, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            set_cookie = resp.headers.get("Set-Cookie", "")
            return resp.status, json.loads(resp.read().decode()), set_cookie
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        set_cookie = exc.headers.get("Set-Cookie", "") if exc.headers else ""
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw[:300]}
        return exc.code, payload, set_cookie


def spark_register_ephemeral() -> tuple[bool, str, str]:
    """Create disposable Spark user for automated E2E (no secrets required)."""
    import time

    email = f"e2e-agent3-{int(time.time())}@dreamvault.test"
    password = f"E2ePass{int(time.time()) % 100000:05d}!"
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    payload = json.dumps(
        {"email": email, "password": password, "username": "E2EAgent3"}
    ).encode()
    req = urllib.request.Request(
        f"{AUTH_API}?action=register",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with opener.open(req, timeout=25) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"message": raw[:200]}
        return False, "", str(body.get("message") or f"HTTP {exc.code}")

    if not body.get("ok"):
        return False, "", str(body.get("message") or "Register failed")

    for cookie in jar:
        if cookie.name == "maskzero_spark_session":
            return True, cookie.value, f"ephemeral register {email}"
    return False, "", "Register OK but maskzero_spark_session cookie missing"


def spark_login(username: str, password: str) -> tuple[bool, str, str]:
    """Return (ok, session_token, message)."""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    payload = json.dumps({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        f"{AUTH_API}?action=login",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with opener.open(req, timeout=25) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"message": raw[:200]}
        return False, "", str(body.get("message") or f"HTTP {exc.code}")

    if not body.get("ok"):
        return False, "", str(body.get("message") or "Login failed")

    for cookie in jar:
        if cookie.name == "maskzero_spark_session":
            return True, cookie.value, "Login OK"
    return False, "", "Login response OK but maskzero_spark_session cookie missing"


def generate_code(session: str, character_id: str = "default") -> tuple[bool, str, dict]:
    cookie = f"maskzero_spark_session={session}"
    status, body, _ = http_json(
        "POST",
        f"{API}?action=generate_code",
        body={"character_id": character_id},
        cookie=cookie,
    )
    if status == 200 and body.get("ok") and body.get("code"):
        return True, str(body["code"]), body
    return False, "", {"status": status, "message": body.get("message"), "body": body}


def consume_code(code: str, bot_secret: str, discord_user_id: str = TEST_DISCORD_USER) -> dict:
    if str(AT_SRC) not in sys.path:
        sys.path.insert(0, str(AT_SRC))
    os.environ["MASKZERO_DISCORD_BOT_SECRET"] = bot_secret
    os.environ.setdefault("MASKZERO_DISCORD_LINK_API_URL", API)
    from agent_tools.discord_commander.maskzero_link_client import consume_link_code

    result = consume_link_code(code, discord_user_id, GUILD_ID)
    return {
        "ok": result.ok,
        "message": result.message,
        "character_id": (result.link or {}).get("character_id"),
        "site_user_id": (result.link or {}).get("site_user_id"),
    }


def check_vps_connect_cog() -> dict:
    cmd = [
        "ssh",
        "-i",
        str(Path.home() / ".ssh" / "dreamos_vps_ed25519"),
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=15",
        VPS_HOST,
        "bash -lc 'cog=0; grep -rq MaskZeroConnectCommands ~/projects/agent-tools 2>/dev/null && cog=1; "
        "slash=0; journalctl --user -u swarm-commander -n 120 --no-pager 2>/dev/null | "
        "grep -qi connect && slash=1; "
        "echo COG=$cog SLASH_LOG=$slash SERVICE=$(systemctl --user is-active swarm-commander 2>/dev/null)'",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
        out = proc.stdout.strip()
        return {
            "name": "vps_connect_cog_and_service",
            "pass": "COG=1" in out and "SERVICE=active" in out,
            "raw": out[:240],
        }
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"name": "vps_connect_cog_and_service", "pass": False, "error": str(exc)}


def resolve_session_and_source(secrets: dict[str, str], code_arg: str) -> tuple[str, str, list[dict]]:
    """Return (session_token, source_label, prelude_checks)."""
    checks: list[dict] = []

    session = secrets.get("MASKZERO_E2E_SPARK_SESSION", "").strip()
    if session:
        return session, "MASKZERO_E2E_SPARK_SESSION", checks

    user = secrets.get("MASKZERO_E2E_USERNAME", "").strip() or secrets.get(
        "MASKZERO_E2E_TEST_USER", ""
    ).strip()
    password = secrets.get("MASKZERO_E2E_PASSWORD", "").strip() or secrets.get(
        "MASKZERO_E2E_TEST_PASSWORD", ""
    ).strip()
    if user and password:
        ok, token, msg = spark_login(user, password)
        checks.append(
            {
                "name": "spark_auth_login",
                "pass": ok,
                "message": msg if not ok else "session acquired",
            }
        )
        if ok and token:
            return token, "MASKZERO_E2E_USERNAME/PASSWORD login", checks
        return "", "login_failed", checks

    if code_arg or secrets.get("MASKZERO_E2E_LINK_CODE", "").strip():
        return "", "operator_link_code", checks

    ok, token, msg = spark_register_ephemeral()
    checks.append(
        {
            "name": "spark_auth_ephemeral_register",
            "pass": ok,
            "message": msg if ok else msg,
        }
    )
    if ok and token:
        return token, "ephemeral spark register (automated E2E)", checks

    return "", "none", checks


def main() -> int:
    parser = argparse.ArgumentParser(description="MaskZero gas8 round-trip verify")
    parser.add_argument("--code", help="One-time link code from maskzero.site/discord/connect")
    args = parser.parse_args()

    secrets = parse_secrets()
    bot_secret = secrets.get("MASKZERO_DISCORD_BOT_SECRET", "").strip()
    checks: list[dict] = []
    blocked_reason = ""

    if not bot_secret:
        checks.append(
            {
                "name": "bot_secret_configured",
                "pass": False,
                "error": "MASKZERO_DISCORD_BOT_SECRET missing locally",
            }
        )
        blocked_reason = "bot_secret_missing"
    else:
        checks.append({"name": "bot_secret_configured", "pass": True})

    session, source, prelude = resolve_session_and_source(secrets, (args.code or "").strip())
    checks.extend(prelude)

    operator_code = (args.code or secrets.get("MASKZERO_E2E_LINK_CODE", "")).strip().upper()
    round_trip: dict

    if operator_code and source in {"operator_link_code", "none"}:
        consume = consume_code(operator_code, bot_secret)
        round_trip = {
            "name": "generate_consume_round_trip",
            "pass": consume["ok"],
            "source": "MASKZERO_E2E_LINK_CODE or --code",
            "path": "Enter Code modal / /connect consume_link_code",
            "code_prefix": operator_code[:2] + "****",
            **consume,
        }
        checks.append(round_trip)
    elif session:
        gen_ok, code, gen_body = generate_code(session)
        checks.append(
            {
                "name": "generate_code_authenticated",
                "pass": gen_ok,
                "source": source,
                "message": gen_body.get("message") if not gen_ok else "code issued",
                "site_user_id": gen_body.get("site_user_id") if gen_ok else None,
            }
        )
        if gen_ok and bot_secret:
            consume = consume_code(code, bot_secret)
            round_trip = {
                "name": "generate_consume_round_trip",
                "pass": consume["ok"],
                "source": source,
                "path": "site generate_code → bot consume_link_code",
                "code_prefix": code[:2] + "****",
                **consume,
            }
            checks.append(round_trip)
        else:
            round_trip = {
                "name": "generate_consume_round_trip",
                "pass": False,
                "source": source,
                "error": "generate_code failed",
            }
            checks.append(round_trip)
    else:
        blocked_reason = blocked_reason or "operator_gate"
        checks.append(
            {
                "name": "generate_consume_round_trip",
                "pass": False,
                "blocked": True,
                "reason": (
                    "Set one of: MASKZERO_E2E_SPARK_SESSION, "
                    "MASKZERO_E2E_USERNAME+MASKZERO_E2E_PASSWORD, "
                    "MASKZERO_E2E_LINK_CODE (or --code after live site generate)"
                ),
                "operator_steps": [
                    "1. Log in at https://maskzero.site/spark-login/",
                    "2. Open https://maskzero.site/discord/connect/ and generate a code",
                    "3. Add MASKZERO_E2E_LINK_CODE=<code> to runtime/secrets/secrets.local.env",
                    "   OR capture maskzero_spark_session cookie as MASKZERO_E2E_SPARK_SESSION",
                    "4. Re-run: python runtime/scripts/maskzero_discord_link_gas8_roundtrip_verify_001.py",
                ],
            }
        )

    checks.append(check_vps_connect_cog())

    round_trip_blocked = any(
        c.get("name") == "generate_consume_round_trip" and c.get("blocked") for c in checks
    )
    round_trip_pass = any(
        c.get("name") == "generate_consume_round_trip" and c.get("pass") for c in checks
    )
    ancillary_ok = all(
        c.get("pass")
        for c in checks
        if c.get("name") != "generate_consume_round_trip" and "pass" in c
    )

    if round_trip_pass:
        ok = ancillary_ok and round_trip_pass
        blocked = False
    elif round_trip_blocked:
        ok = False
        blocked = True
        blocked_reason = blocked_reason or "operator_gate"
    else:
        ok = ancillary_ok and round_trip_pass
        blocked = bool(blocked_reason) and not ok

    payload = {
        "schema": "dreamvault.maskzero_discord_link_gas8_roundtrip.v1",
        "generated_at": utc_now(),
        "agent_id": "Agent-3",
        "gas_cycle": "8/10 cycle 44",
        "task_id": "maskzero_discord_account_link_gas4_deploy_verify_001",
        "pass": ok,
        "blocked": blocked,
        "blocked_reason": blocked_reason or None,
        "checks": checks,
        "modal_path": "MaskZeroConnectView Enter Code → consume_link_code (same as /connect)",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if blocked and not ok:
        print("MASKZERO_GAS8_ROUNDTRIP=BLOCKED")
    else:
        print(f"MASKZERO_GAS8_ROUNDTRIP={'PASS' if ok else 'FAIL'}")
    print(f"OUT={OUT}")
    for row in checks:
        if row.get("blocked"):
            flag = "BLOCKED"
        else:
            flag = "PASS" if row.get("pass") else "FAIL"
        print(f"  [{flag}] {row.get('name')}")
    return 0 if ok else (2 if blocked else 1)


if __name__ == "__main__":
    raise SystemExit(main())
