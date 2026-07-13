#!/usr/bin/env python3
"""E2E verify maskzero discord-link consume auth (no secrets printed)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "runtime/secrets/secrets.local.env"
OUT = ROOT / "data/reports/operator/maskzero_discord_link_e2e_verify_latest.json"
API = os.getenv("MASKZERO_DISCORD_LINK_API_URL", "https://maskzero.site/api/discord-link.php")


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


def post_consume(secret: str, code: str = "ZZZZ9999") -> tuple[int, dict]:
    url = f"{API}?action=consume"
    payload = json.dumps(
        {"code": code, "discord_user_id": "999000111", "discord_guild_id": "0"}
    ).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    if secret:
        req.add_header("X-MaskZero-Bot-Secret", secret)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"raw": body[:200]}
        return exc.code, data


def main() -> int:
    secret = parse_secret()
    checks: list[dict] = []
    ok = True

    status_no_secret, body_no = post_consume("")
    pass_no = status_no_secret == 403
    ok = ok and pass_no
    checks.append(
        {
            "name": "consume_rejects_missing_secret",
            "status": status_no_secret,
            "expected": 403,
            "pass": pass_no,
        }
    )

    if not secret:
        checks.append(
            {
                "name": "consume_with_valid_secret",
                "pass": False,
                "error": "MASKZERO_DISCORD_BOT_SECRET missing locally",
            }
        )
        ok = False
    else:
        status_yes, body_yes = post_consume(secret)
        pass_yes = status_yes == 404 and "Invalid" in str(body_yes.get("message", ""))
        ok = ok and pass_yes
        checks.append(
            {
                "name": "consume_accepts_secret_rejects_bad_code",
                "status": status_yes,
                "expected": 404,
                "pass": pass_yes,
                "message": body_yes.get("message"),
            }
        )

    payload = {
        "schema": "dreamvault.maskzero_discord_link_e2e_verify.v1",
        "generated_at": utc_now(),
        "agent_id": "Agent-3",
        "api": API,
        "pass": ok,
        "checks": checks,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"MASKZERO_DISCORD_LINK_E2E={'PASS' if ok else 'FAIL'}")
    print(f"OUT={OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
