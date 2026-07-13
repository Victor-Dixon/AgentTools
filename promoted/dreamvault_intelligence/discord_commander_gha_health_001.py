"""Discord Commander health check for GitHub Actions (no secret printing).

Validates DISCORD_BOT_TOKEN via REST GET /users/@me, optionally confirms guild
membership, and posts a one-shot test message via webhook when --live-post is set.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_discord_module(module_name: str, filename: str):
    import importlib.util

    module_path = REPO_ROOT / "src" / "dreamvault" / "discord" / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_discord_architect = _load_discord_module(
    "dreamvault_discord_architect", "discord_architect.py"
)
_discord_webhook = _load_discord_module(
    "dreamvault_discord_webhook_sender", "discord_webhook_sender.py"
)
DISCORD_API_BASE = _discord_architect.DISCORD_API_BASE
probe_bot_application = _discord_architect.probe_bot_application
send_discord_webhook = _discord_webhook.send_discord_webhook

BOT_TOKEN_ENV_CANDIDATES = (
    "DISCORD_BOT_TOKEN",
    "DISCORD_TOKEN",
)

WEBHOOK_ENV_CANDIDATES = (
    "DISCORD_WEBHOOK_URL",
    "DISCORD_WEBHOOK_CLOSEOUT",
    "DISCORD_CLOSEOUT_WEBHOOK_URL",
    "DISCORD_WEBHOOK_GOVERNANCE_GATES",
    "DISCORD_BLOCKED_LANES_WEBHOOK_URL",
    "DISCORD_WEBHOOK_AGENT_LANES",
    *(f"DISCORD_WEBHOOK_AGENT_{i}" for i in range(1, 9)),
)


def _mask(value: str) -> str:
    if not value:
        return "<unset>"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}…{value[-4:]}"




def _probe_bot_token() -> tuple[str | None, str | None, dict[str, object]]:
    attempts: list[dict[str, object]] = []
    for env_name in BOT_TOKEN_ENV_CANDIDATES:
        token = os.environ.get(env_name, "").strip()
        if not token:
            attempts.append({"env": env_name, "skipped": "unset"})
            continue
        try:
            identity = probe_bot_application(token)
            check: dict[str, object] = {
                "ok": True,
                "env": env_name,
                "username": identity.get("username"),
                "bot_user_id": identity.get("bot_user_id"),
                "application_name": identity.get("application_name"),
                "token_masked": _mask(token),
            }
            if attempts:
                check["attempts"] = attempts
            return env_name, token, check
        except urllib.error.HTTPError as exc:
            attempts.append(
                {
                    "env": env_name,
                    "http_status": exc.code,
                    "token_masked": _mask(token),
                }
            )
            continue
    return None, None, {
        "ok": False,
        "error": "no valid bot token in candidate envs",
        "candidates": list(BOT_TOKEN_ENV_CANDIDATES),
        "attempts": attempts,
    }


def _resolve_webhook_url() -> tuple[str | None, str | None]:
    for env_name in WEBHOOK_ENV_CANDIDATES:
        url = os.environ.get(env_name, "").strip()
        if url:
            return env_name, url
    return None, None


def _bot_in_guild(token: str, guild_id: str) -> tuple[bool | None, int | None]:
    req = urllib.request.Request(
        f"{DISCORD_API_BASE}/users/@me/guilds",
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "DreamVault-DiscordGHAHealth/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            guilds = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return None, exc.code

    for guild in guilds:
        if str(guild.get("id") or "") == guild_id:
            return True, 200
    return False, 200


def _append_summary(lines: list[str]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Discord Commander GHA health check")
    parser.add_argument(
        "--live-post",
        action="store_true",
        help="POST a test message to the configured webhook (default: dry-run only)",
    )
    parser.add_argument(
        "--webhook-only",
        action="store_true",
        help="Overall PASS if webhook check passes; bot/guild failures are non-blocking",
    )
    args = parser.parse_args()

    results: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {},
    }
    failures: list[str] = []

    _token_env, token, bot_check = _probe_bot_token()
    guild_id = os.environ.get("DISCORD_GUILD_ID", "").strip()
    webhook_env, webhook_url = _resolve_webhook_url()

    # --- inbound: bot token ---
    results["checks"]["bot_token"] = bot_check
    if not bot_check.get("ok"):
        failures.append("bot_token")

    # --- guild membership (optional when guild id set) ---
    if guild_id and token and "bot_token" in results["checks"] and results["checks"]["bot_token"].get("ok"):
        in_guild, http_status = _bot_in_guild(token, guild_id)
        guild_check: dict[str, object] = {
            "ok": in_guild is True,
            "guild_id": guild_id,
            "in_guild": in_guild,
        }
        if http_status is not None:
            guild_check["http_status"] = http_status
        if in_guild is False:
            failures.append("guild_membership")
        results["checks"]["guild_membership"] = guild_check
    elif guild_id:
        results["checks"]["guild_membership"] = {
            "ok": False,
            "guild_id": guild_id,
            "skipped": "bot token probe failed or token missing",
        }

    # --- outbound: webhook ---
    if not webhook_url:
        results["checks"]["webhook"] = {
            "ok": False,
            "error": "no webhook env configured",
            "candidates": list(WEBHOOK_ENV_CANDIDATES),
        }
        failures.append("webhook")
    else:
        payload = {
            "content": (
                "DreamVault GHA health check — "
                f"{'live post' if args.live_post else 'dry-run'} "
                f"({results['timestamp']})"
            )
        }
        send_result = send_discord_webhook(
            webhook_url,
            payload,
            live=args.live_post,
        )
        results["checks"]["webhook"] = {
            "ok": send_result.ok,
            "env": webhook_env,
            "webhook_masked": _mask(webhook_url),
            "dry_run": send_result.dry_run,
            "status_code": send_result.status_code,
            "message": send_result.message,
        }
        if not send_result.ok:
            failures.append("webhook")

    mode = "webhook_only" if args.webhook_only else "full"
    results["mode"] = mode

    if args.webhook_only:
        webhook_check = results["checks"].get("webhook", {})
        webhook_ok = isinstance(webhook_check, dict) and webhook_check.get("ok") is True
        overall_ok = webhook_ok
        results["overall"] = "PASS" if overall_ok else "FAIL"
        results["failed_checks"] = [] if overall_ok else ["webhook"]
        non_blocking = [name for name in failures if name != "webhook"]
        if non_blocking:
            results["non_blocking_failures"] = non_blocking
    else:
        overall_ok = not failures
        results["overall"] = "PASS" if overall_ok else "FAIL"
        results["failed_checks"] = failures

    print(json.dumps(results, indent=2))

    summary_lines = [
        "## Discord Commander Health",
        "",
        f"**Mode:** {mode}",
        f"**Overall:** {results['overall']}",
        "",
    ]
    for name, check in results["checks"].items():
        ok = check.get("ok") if isinstance(check, dict) else False
        line = f"- **{name}:** {'PASS' if ok else 'FAIL'}"
        if args.webhook_only and name in ("bot_token", "guild_membership") and not ok:
            line += " (non-blocking in webhook-only mode)"
        summary_lines.append(line)
    if results.get("non_blocking_failures"):
        summary_lines.append("")
        summary_lines.append(
            f"Non-blocking: {', '.join(results['non_blocking_failures'])}"
        )
    if results["failed_checks"]:
        summary_lines.append("")
        summary_lines.append(f"Failed: {', '.join(results['failed_checks'])}")
    _append_summary(summary_lines)

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
