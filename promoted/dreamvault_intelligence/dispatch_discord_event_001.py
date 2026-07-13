from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
import sys as _sys_for_dreamvault_import
from pathlib import Path as _PathForDreamVaultImport
_DREAMVAULT_REPO_ROOT_FOR_IMPORT = _PathForDreamVaultImport(__file__).resolve().parents[2]
if str(_DREAMVAULT_REPO_ROOT_FOR_IMPORT) not in _sys_for_dreamvault_import.path:
    _sys_for_dreamvault_import.path.insert(0, str(_DREAMVAULT_REPO_ROOT_FOR_IMPORT))

from dreamvault.discord.xthunder_cards import build_all_xthunder_payloads

REPORT_PATH = Path("data/reports/discord/event_routing/discord_event_dispatch_report_001.json")

DEFAULT_CLOSEOUT_CHANNEL_ID = "1507178844870934629"

EVENT_DEFAULTS = {
    "trading_alert": {
        "channel_env": "DISCORD_TRADING_CHANNEL_ID",
        "title": "DreamOS.ai Trading Alert Smoke",
        "description": "Trading alert route verification for freerideinvestor.",
        "fields": [
            {"name": "Route", "value": "trading_alert -> Discord", "inline": False},
            {"name": "Status", "value": "Smoke test payload only.", "inline": False},
        ],
    },
    "closeout": {
        "channel_env": "DISCORD_CLOSEOUT_CHANNEL_ID",
        "title": "DreamOS.ai Closeout Smoke",
        "description": "Closeout route verification for Dream.OS operator reports.",
        "fields": [
            {"name": "Route", "value": "closeout -> Discord", "inline": False},
            {"name": "Status", "value": "Smoke test payload only.", "inline": False},
        ],
    },
    "marketing_calendar": {
        "channel_env": "DISCORD_MARKETING_CALENDAR_CHANNEL_ID",
        "title": "DreamOS.ai Marketing Calendar Smoke",
        "description": "Marketing calendar route verification.",
        "fields": [
            {"name": "Route", "value": "marketing_calendar -> Discord", "inline": False},
            {"name": "Status", "value": "Smoke test payload only.", "inline": False},
        ],
    },
}


# XTHUNDER_EVENT_DEFAULTS_012
for _xthunder_event_type in (
    "xthunder_cards",
    "xthunder_weekly_plan",
    "xthunder_playtest",
    "xthunder_content_queue",
):
    if _xthunder_event_type not in EVENT_DEFAULTS:
        _xthunder_defaults = dict(EVENT_DEFAULTS.get("closeout", {}))
        _xthunder_defaults["channel_env"] = "DISCORD_XTHUNDER_CHANNEL_ID"
        EVENT_DEFAULTS[_xthunder_event_type] = _xthunder_defaults

DISPATCHABLE_EVENT_ROOTS = (
    "runtime/discord/events/",
    "runtime/events/discord/",
    "runtime/dreamsync/inbox/",
    "data/reports/discord/event_routing/",
)

BLOCKED_EVENT_SOURCE_PARTS = (
    "/data/reports/cpc/",
    "data/reports/cpc/",
    "/data/reports/discord/duplication_scan/",
    "data/reports/discord/duplication_scan/",
)

REQUIRED_EVENT_FIELDS = ("event_type", "payload")


def is_dispatchable_event_source(source_path: str, event: dict) -> tuple[bool, str]:
    """Return whether a source path is eligible for live Discord dispatch."""
    normalized = str(source_path).replace("\\", "/")

    for blocked in BLOCKED_EVENT_SOURCE_PARTS:
        if blocked in normalized:
            return False, "blocked_historical_or_scan_source"

    if not any(root in normalized or normalized.startswith(root) for root in DISPATCHABLE_EVENT_ROOTS):
        return False, "source_root_not_dispatchable"

    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        return False, "missing_required_event_fields:" + ",".join(missing)

    payload = event.get("payload")
    if not isinstance(payload, dict):
        return False, "payload_not_object"

    return True, "dispatchable"


def token() -> str:
    return (
        os.environ.get("DISCORD_BOT_TOKEN")
        or os.environ.get("DREAMOS_DISCORD_BOT_TOKEN")
        or ""
    ).strip()


def channel_id(event_type: str) -> str:
    preferred = EVENT_DEFAULTS[event_type]["channel_env"]
    return (
        os.environ.get(preferred)
        or os.environ.get("DISCORD_TARGET_CHANNEL_ID")
        or os.environ.get("TARGET_CHANNEL_ID")
        or ""
    ).strip()




def resolve_channel_id(event_type: str) -> str:
    """Resolve Discord channel.

    Closeouts route to DISCORD_CLOSEOUT_CHANNEL_ID when explicitly set;
    otherwise they always use DEFAULT_CLOSEOUT_CHANNEL_ID.
    """
    preferred_env = EVENT_DEFAULTS[event_type]["channel_env"]
    preferred = os.environ.get(preferred_env, "").strip()
    if preferred:
        return preferred

    if event_type == "closeout":
        return DEFAULT_CLOSEOUT_CHANNEL_ID

    return (
        os.environ.get("TARGET_CHANNEL_ID", "")
        or os.environ.get("DISCORD_CHANNEL_ID", "")
    ).strip()


def load_event_envelope(source_path: str) -> dict | None:
    """Load a dispatchable event envelope from source_path when present."""
    if not source_path:
        return None

    path = Path(source_path)
    if not path.is_absolute():
        path = Path.cwd() / path

    if not path.exists() or not path.is_file():
        return None

    try:
        event = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    if isinstance(event, dict) and "event_type" in event and "payload" in event:
        return event
    return None


def payload_for(event_type: str, source_path: str | None = None) -> dict:
    spec = EVENT_DEFAULTS[event_type]
    fields = list(spec["fields"])

    if source_path:
        fields.append({"name": "Source", "value": source_path[:1024], "inline": False})

    return {
        "content": "",
        "embeds": [
            {
                "title": spec["title"],
                "description": spec["description"],
                "fields": fields,
                "footer": {"text": "Generated by dispatch_discord_event_001.py"},
            }
        ],
    }


def send(token_value: str, channel: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"https://discord.com/api/v10/channels/{channel}/messages",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bot {token_value}",
            "Content-Type": "application/json",
            "User-Agent": "DreamOS.ai event dispatcher",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8")
            return {"ok": True, "status_code": response.status, "response": json.loads(body)}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status_code": exc.code,
            "error": exc.read().decode("utf-8", errors="replace"),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-type", choices=sorted(EVENT_DEFAULTS), required=True)
    parser.add_argument("--source-path", default="")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.4)
    args, _unknown = parser.parse_known_args()

    event_type = args.event_type
    # XTHUNDER_DIRECT_ROUTE_014
    if str(event_type).strip().lower().replace('-', '_').startswith('xthunder_') and not args.live:
        return print_xthunder_dry_run_payloads(str(event_type))
    tok = token()
    chan = resolve_channel_id(event_type)
    source_event = load_event_envelope(args.source_path)
    if source_event:
        event_type = source_event.get("event_type", event_type)
        payload = source_event["payload"]
    else:
        payload = payload_for(event_type, args.source_path or None)

    if args.source_path:
        eligibility_event = source_event if source_event else {"event_type": event_type, "payload": payload}
        eligible, eligibility_reason = is_dispatchable_event_source(str(args.source_path), eligibility_event)
        if not eligible:
            report = {
                "status": "REJECTED",
                "reason": eligibility_reason,
                "source_path": str(args.source_path),
                "event_type": event_type,
            }
            print(json.dumps(report, indent=2))
            return 2


    report = {
        "status": "DRY_RUN",
        "event_type": event_type,
        "preferred_channel_env": EVENT_DEFAULTS[event_type]["channel_env"],
        "token_present": bool(tok),
        "channel_id_present": bool(chan),
        "source_path": args.source_path,
        "payload": payload,
        "result": None,
    }

    if not args.live:
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("DISCORD_EVENT_DISPATCH=DRY_RUN")
        print("EVENT_TYPE=" + event_type)
        print("PREFERRED_CHANNEL_ENV=" + EVENT_DEFAULTS[event_type]["channel_env"])
        print("REPORT=" + str(REPORT_PATH))
        return

    if not tok:
        report["status"] = "BLOCKED"
        report["result"] = {"ok": False, "error": "missing Discord bot token"}
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("DISCORD_EVENT_DISPATCH_BLOCKED=NO_TOKEN")

    if not chan:
        report["status"] = "BLOCKED"
        report["result"] = {"ok": False, "error": "missing channel id"}
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("DISCORD_EVENT_DISPATCH_BLOCKED=NO_CHANNEL")

    result = send(tok, chan, payload)
    report["result"] = result
    report["status"] = "PASS" if result["ok"] else "FAIL"
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if not result["ok"]:
        raise SystemExit("DISCORD_EVENT_DISPATCH=FAIL")

    time.sleep(args.sleep)
    print("DISCORD_EVENT_DISPATCH=PASS")
    print("EVENT_TYPE=" + event_type)
    print("REPORT=" + str(REPORT_PATH))



def build_xthunder_dispatch_payloads(event_type: str) -> list[dict]:
    """Return Discord payloads for supported XThunder dispatcher events."""
    normalized = (event_type or "").strip().lower().replace("-", "_")
    payloads = build_all_xthunder_payloads()

    if normalized == "xthunder_cards":
        return payloads
    if normalized == "xthunder_weekly_plan":
        return payloads[:1]
    if normalized == "xthunder_playtest":
        return payloads[1:2]
    if normalized == "xthunder_content_queue":
        return payloads[2:3]
    return []


def print_xthunder_dry_run_payloads(event_type: str) -> int:
    """Print XThunder Discord payloads as JSON lines for CLI dry-run verification."""
    import json

    payloads = build_xthunder_dispatch_payloads(event_type)
    if not payloads:
        return 1
    for payload in payloads:
        print(json.dumps(payload, sort_keys=True))
    return 0

if __name__ == "__main__":
    main()
