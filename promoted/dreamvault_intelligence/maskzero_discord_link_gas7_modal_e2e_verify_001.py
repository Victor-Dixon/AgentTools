#!/usr/bin/env python3
"""Gas 7 — MaskZero Enter Code modal E2E verify (generate gate + consume client path)."""

from __future__ import annotations

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
OUT = ROOT / "data/reports/operator/maskzero_discord_link_gas7_modal_e2e_latest.json"
API = os.getenv("MASKZERO_DISCORD_LINK_API_URL", "https://maskzero.site/api/discord-link.php")
AT_ROOT = Path(os.getenv("AGENT_TOOLS_ROOT", "D:/agent-tools"))
AT_SRC = AT_ROOT / "src"
VPS_HOST = os.getenv("DREAMOS_VPS_HOST", "dreamos@2.25.64.233")


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
) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw[:300]}
        return exc.code, payload


def check_generate_requires_login() -> dict:
    status, body = http_json("POST", f"{API}?action=generate_code", body={})
    ok = status == 401 and "login" in str(body.get("message", "")).lower()
    return {
        "name": "generate_code_requires_login",
        "status": status,
        "expected": 401,
        "pass": ok,
        "message": body.get("message"),
    }


def check_connect_page() -> dict:
    req = urllib.request.Request("https://maskzero.site/discord/connect/")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ok = resp.status == 200
            return {"name": "connect_page_live", "status": resp.status, "pass": ok}
    except urllib.error.HTTPError as exc:
        return {"name": "connect_page_live", "status": exc.code, "pass": False}


def check_modal_client_bad_code(secret: str) -> dict:
    if str(AT_SRC) not in sys.path:
        sys.path.insert(0, str(AT_SRC))
    os.environ.setdefault("MASKZERO_DISCORD_BOT_SECRET", secret)
    os.environ.setdefault("MASKZERO_DISCORD_LINK_API_URL", API)
    from agent_tools.discord_commander.maskzero_link_client import consume_link_code

    result = consume_link_code("ZZZZ9999", "999000777", "1375298054357254257")
    ok = not result.ok and "invalid" in result.message.lower()
    return {
        "name": "modal_client_rejects_bad_code",
        "pass": ok,
        "message": result.message,
        "path": "agent_tools.discord_commander.maskzero_link_client.consume_link_code",
    }


def check_round_trip_if_session(secrets: dict[str, str], bot_secret: str) -> dict:
    session = secrets.get("MASKZERO_E2E_SPARK_SESSION", "").strip()
    if not session:
        return {
            "name": "generate_consume_round_trip",
            "pass": True,
            "skipped": True,
            "reason": "MASKZERO_E2E_SPARK_SESSION not set — login gate verified only",
        }

    cookie = f"maskzero_spark_session={session}"
    status, gen = http_json(
        "POST",
        f"{API}?action=generate_code",
        body={"character_id": "default"},
        cookie=cookie,
    )
    if status != 200 or not gen.get("ok") or not gen.get("code"):
        return {
            "name": "generate_consume_round_trip",
            "pass": False,
            "step": "generate",
            "status": status,
            "message": gen.get("message"),
        }

    code = str(gen["code"])
    if str(AT_SRC) not in sys.path:
        sys.path.insert(0, str(AT_SRC))
    os.environ["MASKZERO_DISCORD_BOT_SECRET"] = bot_secret
    from agent_tools.discord_commander.maskzero_link_client import consume_link_code

    test_discord_id = "888777666555"
    result = consume_link_code(code, test_discord_id, "1375298054357254257")
    return {
        "name": "generate_consume_round_trip",
        "pass": result.ok,
        "code_prefix": code[:2] + "****",
        "discord_user_id": test_discord_id,
        "message": result.message,
        "character_id": (result.link or {}).get("character_id"),
    }


def check_vps_secret_and_view() -> dict:
    cmd = [
        "ssh",
        "-i",
        str(Path.home() / ".ssh" / "dreamos_vps_ed25519"),
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=15",
        VPS_HOST,
        "bash -lc 'set -a; source ~/secrets/swarm-commander.env 2>/dev/null; "
        "secret_ok=0; [ -n \"${MASKZERO_DISCORD_BOT_SECRET:-}\" ] && secret_ok=1; "
        "view_ok=0; journalctl --user -u swarm-commander -n 80 --no-pager 2>/dev/null | "
        "grep -q MaskZeroConnectView && view_ok=1; "
        "echo SECRET_OK=$secret_ok VIEW_OK=$view_ok SERVICE=$(systemctl --user is-active swarm-commander 2>/dev/null)'",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=False)
        out = proc.stdout.strip()
        secret_ok = "SECRET_OK=1" in out
        view_ok = "VIEW_OK=1" in out
        service_active = "SERVICE=active" in out
        return {
            "name": "vps_bot_secret_and_view",
            "pass": secret_ok and view_ok and service_active,
            "secret_configured": secret_ok,
            "maskzero_view_posted": view_ok,
            "service_active": service_active,
            "raw": out[:200],
        }
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"name": "vps_bot_secret_and_view", "pass": False, "error": str(exc)}


def main() -> int:
    secrets = parse_secrets()
    bot_secret = secrets.get("MASKZERO_DISCORD_BOT_SECRET", "")
    checks: list[dict] = []

    checks.append(check_connect_page())
    checks.append(check_generate_requires_login())

    if not bot_secret:
        checks.append(
            {
                "name": "modal_client_rejects_bad_code",
                "pass": False,
                "error": "MASKZERO_DISCORD_BOT_SECRET missing locally",
            }
        )
    else:
        checks.append(check_modal_client_bad_code(bot_secret))
        checks.append(check_round_trip_if_session(secrets, bot_secret))

    checks.append(check_vps_secret_and_view())

    ok = all(c.get("pass") for c in checks if not c.get("skipped"))
    payload = {
        "schema": "dreamvault.maskzero_discord_link_gas7_modal_e2e.v1",
        "generated_at": utc_now(),
        "agent_id": "Agent-3",
        "gas_cycle": "7/10 cycle 44",
        "task_id": "maskzero_discord_account_link_gas4_deploy_verify_001",
        "pass": ok,
        "checks": checks,
        "modal_path": "MaskZeroConnectView Enter Code → consume_link_code",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"MASKZERO_GAS7_MODAL_E2E={'PASS' if ok else 'FAIL'}")
    print(f"OUT={OUT}")
    for row in checks:
        flag = "SKIP" if row.get("skipped") else ("PASS" if row.get("pass") else "FAIL")
        print(f"  [{flag}] {row.get('name')}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
