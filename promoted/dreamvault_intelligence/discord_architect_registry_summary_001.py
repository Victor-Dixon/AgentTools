#!/usr/bin/env python3

import json
from pathlib import Path

registry = Path("discord_architect/config/server_registry.json")
report = Path("data/reports/discord_architect/server_registry_summary.md")

data = json.loads(registry.read_text(encoding="utf-8"))

servers = data.get("servers", [])

lines = [
    "# Discord Architect Server Registry",
    "",
    f"Registered servers: {len(servers)}",
    "",
    "| Key | Guild ID | Environment | Managed | Protected |",
    "|---|---|---|---|---|"
]

for s in servers:
    lines.append(
        f"| `{s.get('server_key')}` | "
        f"`{s.get('guild_id')}` | "
        f"{s.get('environment')} | "
        f"{s.get('managed')} | "
        f"{s.get('protected')} |"
    )

report.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"REGISTERED_SERVERS={len(servers)}")
print("REPORT=data/reports/discord_architect/server_registry_summary.md")
