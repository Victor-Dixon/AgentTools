#!/usr/bin/env python3
from pathlib import Path
import json
import yaml

TASK_ROOT = Path("runtime/tasks")
OUT_JSON = Path("data/reports/discord/capability_unlocks/latest_task_unlock_payload.json")
OUT_MD = Path("data/reports/discord/capability_unlocks/latest_task_unlock_payload.md")

def load_tasks():
    rows = []
    for p in sorted(TASK_ROOT.rglob("*.yaml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if data.get("capabilities_unlocked") or data.get("discord_closeout"):
            rows.append({
                "id": data.get("id") or p.stem,
                "path": str(p),
                "capabilities_unlocked": data.get("capabilities_unlocked", []),
                "downstream_unlocks": data.get("downstream_unlocks", []),
                "discord_closeout": data.get("discord_closeout", {}),
            })
    return rows

def render_md(rows):
    parts = ["# Discord Capability Closeout Payload", ""]
    for row in rows[-20:]:
        closeout = row.get("discord_closeout") or {}
        parts += [
            f"## {closeout.get('title') or row['id']}",
            "",
            closeout.get("summary", ""),
            "",
            "### Capabilities Unlocked",
        ]
        for item in row["capabilities_unlocked"]:
            parts.append(f"- {item}")
        parts.append("")
        parts.append("### Downstream Unlocks")
        for item in row["downstream_unlocks"]:
            parts.append(f"- {item}")
        parts.append("")
    return "\n".join(parts)

def main():
    rows = load_tasks()
    payload = {"unlock_task_count": len(rows), "tasks": rows[-20:]}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(rows), encoding="utf-8")
    print("DISCORD_CAPABILITY_CLOSEOUT_PAYLOAD=PASS")
    print(f"TASKS={len(rows)}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")

if __name__ == "__main__":
    main()
