from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_legacy_tool_migration_matrix_generates() -> None:
    subprocess.run(
        ["python3", "scripts/build_legacy_tool_migration_matrix.py"],
        cwd=ROOT,
        check=True,
    )

    records = json.loads((ROOT / "docs" / "LEGACY_TOOL_MIGRATION_MATRIX.json").read_text())
    assert records
    assert all(r["path"].startswith("tools/") for r in records)
    assert all(r["suggested_status"] for r in records)


def test_tools_v2_is_the_only_active_registry_surface() -> None:
    lock = json.loads((ROOT / "tools_v2" / "tool_registry.lock.json").read_text())
    active_entries = lock.get("tools", {})
    assert active_entries

    bad = [
        name
        for name, entry in active_entries.items()
        if isinstance(entry, list) and entry and str(entry[0]).startswith("tools.")
    ]

    assert bad == []
