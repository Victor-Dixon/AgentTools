#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUTBOX = ROOT / "runtime/dreamsync/outbox"
REPORT_DIR = ROOT / "data/reports/dreamsync"
REPORT_JSON = REPORT_DIR / "dreamsync_projectscanner_context_bridge_001.json"
REPORT_MD = REPORT_DIR / "dreamsync_projectscanner_context_bridge_001.md"

SOURCES = {
    "runtime_reality": ROOT / "data/reports/runtime/runtime_reality_packet_001.json",
    "agent_context": ROOT / "data/reports/agent_context/agent_context_packet.json",
    "task_intelligence": ROOT / "data/reports/task_intelligence/task_lifecycle_intelligence_001.json",
    "weighted_cognition": ROOT / "data/reports/weighted_cognition/weighted_cognition_001.json",
    "capability_index": ROOT / "data/reports/relevance/capability_index_001.json",
    "branch_divergence": ROOT / "data/reports/branch_divergence/projectscanner_branch_divergence_map_001.json",
}

def main() -> int:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    packet_dir = OUTBOX / f"projectscanner_context_{stamp}"
    packet_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    missing = []

    for name, src in SOURCES.items():
        if src.exists():
            dest = packet_dir / src.name
            shutil.copy2(src, dest)
            copied.append({"name": name, "source": str(src), "dest": str(dest)})
        else:
            missing.append({"name": name, "source": str(src)})

    manifest = {
        "schema": "dreamsync.projectscanner_context_packet.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "packet_dir": str(packet_dir),
        "routing": {
            "producer": "projectscanner",
            "transport": "dreamsync",
            "consumers": ["desktop", "mobile", "agent_review"],
        },
        "copied": copied,
        "missing": missing,
        "next_actions": [
            "sync packet to desktop worker",
            "upload packet to review agents",
            "ingest returned recommendations as runtime/tasks",
        ],
        "status": "pass" if copied else "fail",
    }

    manifest_path = packet_dir / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    REPORT_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# DreamSync ProjectScanner Context Bridge",
        "",
        f"- Status: `{manifest['status'].upper()}`",
        f"- Packet: `{packet_dir}`",
        f"- Copied: `{len(copied)}`",
        f"- Missing: `{len(missing)}`",
        "",
        "## Copied Sources",
        "",
    ]

    for item in copied:
        lines.append(f"- `{item['name']}` → `{item['dest']}`")

    if missing:
        lines.extend(["", "## Missing Sources", ""])
        for item in missing:
            lines.append(f"- `{item['name']}` → `{item['source']}`")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if manifest["status"] != "pass":
        print("DREAMSYNC_PROJECTSCANNER_BRIDGE=FAIL")
        print("CONTEXT_OUTBOX_PACKET=FAIL")
        return 1

    print("DREAMSYNC_PROJECTSCANNER_BRIDGE=PASS")
    print("CONTEXT_OUTBOX_PACKET=PASS")
    print(f"PACKET={packet_dir}")
    print(f"MANIFEST={manifest_path}")
    print(f"REPORT={REPORT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
