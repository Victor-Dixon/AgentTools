from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_toolbelt_surface_audit_is_generated_and_clean() -> None:
    subprocess.run(
        ["python3", "scripts/audit_toolbelt_surfaces.py"],
        cwd=ROOT,
        check=True,
    )

    audit_path = ROOT / "docs" / "TOOLBELT_SURFACE_AUDIT.json"
    records = json.loads(audit_path.read_text(encoding="utf-8"))

    assert records, "toolbelt audit produced no records"

    broken = [r for r in records if not r["syntax_ok"]]
    assert broken == []

    surfaces = {r["path"].split("/", 1)[0] for r in records}
    assert "tools_v2" in surfaces
    assert "swarm_mcp" in surfaces
    assert "mcp_servers" in surfaces


def test_legacy_tools_are_explicitly_classified_not_silent() -> None:
    records = json.loads((ROOT / "docs" / "TOOLBELT_SURFACE_AUDIT.json").read_text(encoding="utf-8"))
    legacy = [r for r in records if r["path"].startswith("tools/")]

    assert legacy, "tools/ has no classified legacy files; remove this test if tools/ is fully retired"
    assert all(r["risk"] == "legacy_review" for r in legacy)
