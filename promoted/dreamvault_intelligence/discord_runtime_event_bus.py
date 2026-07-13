#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = {"event_type", "title", "status"}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def validate_event(event):
    missing = sorted(REQUIRED - set(event))
    if missing:
        raise ValueError(f"missing required fields: {missing}")
    return True

def append_event(bus_path, event):
    validate_event(event)
    event = dict(event)
    event.setdefault("created_at", now_iso())
    bus_path.parent.mkdir(parents=True, exist_ok=True)
    with bus_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event

def render_preview(bus_path, out_path):
    events = []
    if bus_path.exists():
        for line in bus_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Discord Runtime Event Bus Preview", ""]
    lines.append(f"EVENT_COUNT={len(events)}")
    lines.append("")
    for event in events[-25:]:
        lines.append(f"## {event['title']}")
        lines.append(f"- type: {event['event_type']}")
        lines.append(f"- status: {event['status']}")
        lines.append(f"- created_at: {event.get('created_at', '')}")
        if event.get("summary"):
            lines.append(f"- summary: {event['summary']}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bus", default="data/reports/discord_runtime/events.jsonl")
    parser.add_argument("--preview", default="data/reports/discord_runtime/events_preview.md")
    parser.add_argument("--emit-fixture", action="store_true")
    args = parser.parse_args()

    bus = Path(args.bus)
    preview = Path(args.preview)

    if args.emit_fixture:
        append_event(bus, {
            "event_type": "governance",
            "title": "Discord runtime cockpit initialized",
            "status": "PASS",
            "summary": "Append-only event bus and preview renderer online."
        })

    render_preview(bus, preview)
    print(f"EVENT_BUS={bus}")
    print(f"PREVIEW={preview}")
    print("STATUS=PASS")

if __name__ == "__main__":
    main()
