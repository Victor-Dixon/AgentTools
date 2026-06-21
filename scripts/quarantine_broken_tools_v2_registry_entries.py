from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "tools_v2" / "tool_registry.lock.json"
REPORT = ROOT / "docs" / "TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md"

BROKEN = {
    "agent.points": "Missing class: tools_v2.categories.session_tools.PointsCalculatorTool",
    "brain.get": "Abstract adapter missing get_spec/validate",
    "brain.note": "Abstract adapter missing get_spec/validate",
    "brain.search": "Abstract adapter missing get_spec/validate",
    "brain.session": "Abstract adapter missing get_spec/validate",
    "brain.share": "Abstract adapter missing get_spec/validate",
    "discord.health": "Abstract adapter missing get_spec/validate",
    "discord.start": "Abstract adapter missing get_spec/validate",
    "discord.test": "Abstract adapter missing get_spec/validate",
    "infra.roi_calc": "Missing class: tools_v2.categories.infrastructure_tools.ROICalculatorTool",
    "mem.imports": "Missing class: tools_v2.categories.memory_safety_adapters.ImportValidatorTool",
    "msgtask.fingerprint": "Abstract adapter missing get_spec/validate",
    "msgtask.ingest": "Abstract adapter missing get_spec/validate",
    "msgtask.parse": "Abstract adapter missing get_spec/validate",
    "obs.get": "Abstract adapter missing get_spec/validate",
    "obs.health": "Abstract adapter missing get_spec/validate",
    "obs.metrics": "Abstract adapter missing get_spec/validate",
    "obs.slo": "Abstract adapter missing get_spec/validate",
}

data = json.loads(LOCK.read_text(encoding="utf-8"))
tools = data.setdefault("tools", {})
disabled = data.setdefault("disabled_tools", {})

moved = {}

for name, reason in BROKEN.items():
    if name in tools:
        disabled[name] = {
            "registry_entry": tools.pop(name),
            "disabled_reason": reason,
            "restore_policy": "Restore only after adapter instantiates and exposes ToolSpec/get_spec/validate.",
        }
        moved[name] = reason
    elif name in disabled:
        moved[name] = disabled[name].get("disabled_reason", reason)

LOCK.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

lines = [
    "# tools_v2 Disabled Registry Entries",
    "",
    "These entries were removed from the active `tools_v2` registry because the registry contract test proved they do not instantiate cleanly.",
    "",
    "Active registry policy:",
    "",
    "- `ToolRegistry.list_tools()` must return only loadable tools.",
    "- `ToolRegistry.get_tool()` must instantiate the adapter.",
    "- Each active adapter must expose a valid `ToolSpec`.",
    "- Broken or incomplete adapters stay in `disabled_tools` until fixed.",
    "",
    "## Disabled Entries",
    "",
]

for name in sorted(moved):
    lines.append(f"- `{name}` — {moved[name]}")

REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"UPDATED: {LOCK}")
print(f"WROTE: {REPORT}")
print(f"disabled_count={len(moved)}")
