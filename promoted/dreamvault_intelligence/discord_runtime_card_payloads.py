#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

STATUS_COLORS = {
    "PASS": 0x2ECC71,
    "WARN": 0xF1C40F,
    "FAIL": 0xE74C3C,
    "BLOCKED": 0xE67E22,
    "INFO": 0x3498DB,
}

REQUIRED = {"event_type", "title", "status"}

def validate_event(event):
    missing = sorted(REQUIRED - set(event))
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    return True

def event_to_embed(event):
    validate_event(event)
    status = str(event["status"]).upper()
    return {
        "title": event["title"],
        "description": event.get("summary", ""),
        "color": STATUS_COLORS.get(status, STATUS_COLORS["INFO"]),
        "fields": [
            {"name": "Type", "value": str(event["event_type"]), "inline": True},
            {"name": "Status", "value": status, "inline": True},
            {"name": "Created", "value": str(event.get("created_at", "unknown")), "inline": False},
        ],
        "footer": {"text": "Dream.OS Runtime Cockpit"},
    }

def load_events(path):
    events = []
    if not path.exists():
        return events
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid jsonl line {idx}: {exc}") from exc
        validate_event(event)
        events.append(event)
    return events

def render_payloads(bus_path, out_path):
    events = load_events(bus_path)
    payloads = [{"embeds": [event_to_embed(event)]} for event in events]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payloads, indent=2, ensure_ascii=False), encoding="utf-8")
    return payloads

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bus", default="data/reports/discord_runtime/events.jsonl")
    parser.add_argument("--out", default="data/reports/discord_runtime/discord_payloads.json")
    args = parser.parse_args()

    payloads = render_payloads(Path(args.bus), Path(args.out))
    print(f"PAYLOAD_COUNT={len(payloads)}")
    print(f"PAYLOADS={args.out}")
    print("STATUS=PASS")

if __name__ == "__main__":
    main()
