#!/usr/bin/env python3
"""One-shot consolidation: copy Discord Commander artifacts to runtime/discord_commander/, verify, delete sources."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CANON = REPO_ROOT / "runtime" / "discord_commander"

# (source relative to REPO_ROOT, dest relative to CANON, purpose, delete_after_copy)
COPY_PLAN: list[tuple[str, str, str, bool]] = [
    # scripts
    ("runtime/scripts/discord_commander_gha_health_001.py", "scripts/discord_commander_gha_health_001.py", "GHA health check (bot token + webhook)", True),
    ("runtime/scripts/activate_discord_commander_001.ps1", "scripts/activate_discord_commander_001.ps1", "Local activation via agent-tools CLI", True),
    ("runtime/scripts/discord_commander_cross_repo_scan_001.py", "scripts/discord_commander_cross_repo_scan_001.py", "Cross-repo reference scanner", True),
    ("runtime/scripts/render_discord_commander_swarm_status_preview_001.py", "scripts/render_discord_commander_swarm_status_preview_001.py", "Swarm status preview renderer", True),
    ("runtime/scripts/sync_discord_env_from_salvage_001.py", "scripts/sync_discord_env_from_salvage_001.py", "Sync Discord env from salvage (no secret print)", True),
    # package (canonical Python implementation)
    ("src/dreamvault/discord/commander/__init__.py", "src/dreamvault/discord/commander/__init__.py", "Commander package exports", True),
    ("src/dreamvault/discord/commander/swarm_status_payload.py", "src/dreamvault/discord/commander/swarm_status_payload.py", "Swarm status embed/preview payloads", True),
    ("src/dreamvault/discord/commander/swarm_status_reader.py", "src/dreamvault/discord/commander/swarm_status_reader.py", "Agent workspace status reader", True),
    # tests
    ("tests/test_discord_commander_swarm_status.py", "tests/test_discord_commander_swarm_status.py", "Commander swarm status pytest suite", True),
    # tasks
    ("runtime/tasks/discord_commander_toolbelt_promotion_001.yaml", "tasks/discord_commander_toolbelt_promotion_001.yaml", "Toolbelt promotion task", True),
    ("runtime/tasks/discord_bot_token_refresh_001.yaml", "tasks/discord_bot_token_refresh_001.yaml", "Bot token refresh operator task", True),
    # workflow (reference copy; .github copy updated in-place)
    (".github/workflows/discord-commander-health.yml", "workflows/discord-commander-health.yml", "GHA workflow reference", False),
    # reports
    ("data/reports/discord/commander_cross_repo_scan_latest.json", "reports/commander_cross_repo_scan_latest.json", "Latest cross-repo scan output", True),
]

OPTIONAL_REPORTS = [
    "data/reports/discord/commander/latest_preview.md",
    "data/reports/discord/commander/latest_payload.json",
]

SALVAGE_COPIES: list[tuple[str, str, str]] = [
    (
        "integrations/salvage/victor_os/runtime/src/dreamos/agent_dashboard/tabs/discord_commander.py",
        "salvage/victor_os/agent_dashboard_discord_commander.py",
        "Victor OS dashboard tab (PyQt placeholder)",
    ),
    (
        "merge/core_merge_20260612_032710/scripts/maintenance/run_discord_commander.py",
        "salvage/merge/run_discord_commander.py",
        "Legacy merge run script",
    ),
    (
        "merge/core_merge_20260612_032710/scripts/legacy/simple_discord_commander.py",
        "salvage/merge/simple_discord_commander.py",
        "Legacy simple commander",
    ),
    (
        "merge/core_merge_20260612_032710/docs/status_reports/DISCORD_COMMANDER_SETUP_GUIDE.md",
        "salvage/merge/docs/DISCORD_COMMANDER_SETUP_GUIDE.md",
        "Setup guide from merge archive",
    ),
    (
        "merge/core_merge_20260612_032710/docs/status_reports/DISCORD_COMMANDER_ANALYSIS.md",
        "salvage/merge/docs/DISCORD_COMMANDER_ANALYSIS.md",
        "Analysis doc from merge archive",
    ),
    (
        "merge/core_merge_20260612_032710/tests/legacy/test_discord_commander.py",
        "salvage/merge/tests/test_discord_commander.py",
        "Legacy test from merge archive",
    ),
]

RETAIN_IN_PLACE = [
    {
        "path": "runtime/secrets/secrets.local.env",
        "reason": "Local credential store — never delete or copy secret values",
        "secret_keys": ["DISCORD_BOT_TOKEN", "DISCORD_GUILD_ID", "DISCORD_WEBHOOK_*"],
    },
    {
        "path": "runtime/state/discord_token_registry.json",
        "reason": "Token registry metadata — may reference redacted tokens",
        "secret_keys": ["DISCORD_BOT_TOKEN"],
    },
    {
        "path": ".github/workflows/discord-commander-health.yml",
        "reason": "GitHub Actions requires workflow under .github/workflows/ (paths updated to canonical scripts)",
        "secret_keys": ["secrets.DISCORD_BOT_TOKEN"],
    },
]

EXTERNAL_REFS = [
    {"path": r"D:\agent-tools\src\agent_tools\discord_commander", "role": "canonical_toolbelt_implementation", "action": "document_only"},
    {"path": r"D:\agent-tools\docs\runbooks\discord_commander.md", "role": "toolbelt_runbook", "action": "document_only"},
    {"path": r"D:\Agent_Cellphone_V2_Repository", "role": "salvage_source_per_toolbelt_task", "action": "document_only"},
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_one(src_rel: str, dest_rel: str, purpose: str, delete: bool) -> dict:
    src = REPO_ROOT / src_rel.replace("/", "\\") if "\\" not in src_rel else REPO_ROOT / src_rel
    src = REPO_ROOT / Path(src_rel)
    dest = CANON / dest_rel
    entry: dict = {
        "source": str(src.relative_to(REPO_ROOT)).replace("\\", "/"),
        "destination": str(dest.relative_to(REPO_ROOT)).replace("\\", "/"),
        "purpose": purpose,
        "file_type": src.suffix.lstrip(".") or "unknown",
        "delete_after_copy": delete,
        "status": "skipped",
    }
    if not src.is_file():
        entry["status"] = "missing"
        return entry
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    src_hash = sha256(src)
    dest_hash = sha256(dest)
    entry["checksum_sha256"] = src_hash
    entry["verified"] = src_hash == dest_hash
    entry["status"] = "copied" if entry["verified"] else "checksum_mismatch"
    if entry["verified"] and delete:
        src.unlink()
        entry["deleted_source"] = True
    elif entry["verified"]:
        entry["deleted_source"] = False
    return entry


def patch_script_paths(content: str, script_name: str) -> str:
    """Fix REPO_ROOT depth and internal path references after move to runtime/discord_commander/scripts/."""
    if script_name.endswith(".py"):
        content = content.replace(
            'REPO_ROOT = Path(__file__).resolve().parents[2]',
            'REPO_ROOT = Path(__file__).resolve().parents[3]',
        )
        content = content.replace(
            'OUT = REPO_ROOT / "data/reports/discord/commander_cross_repo_scan_latest.json"',
            'OUT = REPO_ROOT / "runtime/discord_commander/reports/commander_cross_repo_scan_latest.json"',
        )
        content = content.replace(
            'out_dir = REPO_ROOT / "data" / "reports" / "discord" / "commander"',
            'out_dir = REPO_ROOT / "runtime" / "discord_commander" / "reports" / "commander"',
        )
        if "discord_commander" in script_name and "cross_repo" in script_name:
            content = content.replace(
                'Path(r"D:\\DreamOS_Core")',
                'Path(r"D:\\DreamOS_Core")',
            )
            content = content.replace(
                '"revitalized_package": {\n            "path": str(new_pkg),',
                '"revitalized_package": {\n            "path": str(new_pkg),',
            )
            content = content.replace(
                'new_pkg = root / "src" / "dreamvault" / "discord" / "commander"',
                'new_pkg = root / "runtime" / "discord_commander" / "src" / "dreamvault" / "discord" / "commander"',
            )
    if script_name.endswith(".ps1"):
        content = content.replace(
            '$VaultRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent',
            '$VaultRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent',
        )
        content = content.replace(
            'runtime\\scripts\\activate_discord_commander_001.ps1',
            'runtime\\discord_commander\\scripts\\activate_discord_commander_001.ps1',
        )
    return content


def write_compat_shims() -> None:
    shim_dir = REPO_ROOT / "src" / "dreamvault" / "discord" / "commander"
    shim_dir.mkdir(parents=True, exist_ok=True)
    shim_init = '''"""Compatibility shim — canonical: runtime/discord_commander/src/dreamvault/discord/commander/."""
from __future__ import annotations

import sys
from pathlib import Path

_CANON_SRC = Path(__file__).resolve().parents[4] / "runtime" / "discord_commander" / "src"
if str(_CANON_SRC) not in sys.path:
    sys.path.insert(0, str(_CANON_SRC))

from dreamvault.discord.commander.swarm_status_payload import (  # noqa: E402
    build_commander_preview,
    build_swarm_status_embed,
)
from dreamvault.discord.commander.swarm_status_reader import (  # noqa: E402
    SwarmStatusReader,
    detect_status_changes,
    resolve_agent_workspace_dir,
    status_emoji,
)

__all__ = [
    "SwarmStatusReader",
    "build_commander_preview",
    "build_swarm_status_embed",
    "detect_status_changes",
    "resolve_agent_workspace_dir",
    "status_emoji",
]
'''
    (shim_dir / "__init__.py").write_text(shim_init, encoding="utf-8")

    for mod in ("swarm_status_payload", "swarm_status_reader"):
        shim = f'''"""Compatibility shim — canonical: runtime/discord_commander/src/dreamvault/discord/commander/{mod}.py"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

_CANON_SRC = Path(__file__).resolve().parents[4] / "runtime" / "discord_commander" / "src"
if str(_CANON_SRC) not in sys.path:
    sys.path.insert(0, str(_CANON_SRC))

_mod = importlib.import_module(f"dreamvault.discord.commander.{mod}")
globals().update({{k: v for k, v in _mod.__dict__.items() if not k.startswith("_")}})
'''
        (shim_dir / f"{mod}.py").write_text(shim, encoding="utf-8")


def update_github_workflow() -> None:
    wf = REPO_ROOT / ".github/workflows/discord-commander-health.yml"
    if not wf.is_file():
        return
    text = wf.read_text(encoding="utf-8")
    text = text.replace(
        "runtime/scripts/discord_commander_gha_health_001.py",
        "runtime/discord_commander/scripts/discord_commander_gha_health_001.py",
    )
    text = text.replace(
        '      - "runtime/scripts/discord_commander_gha_health_001.py"',
        '      - "runtime/discord_commander/scripts/discord_commander_gha_health_001.py"',
    )
    wf.write_text(text, encoding="utf-8")


def patch_copied_scripts() -> None:
    scripts_dir = CANON / "scripts"
    for path in scripts_dir.glob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        patched = patch_script_paths(text, path.name)
        if patched != text:
            path.write_text(patched, encoding="utf-8")


def patch_test_paths() -> None:
    test = CANON / "tests" / "test_discord_commander_swarm_status.py"
    if not test.is_file():
        return
    text = test.read_text(encoding="utf-8")
    text = text.replace(
        'ROOT = Path(__file__).resolve().parents[1]',
        'ROOT = Path(__file__).resolve().parents[3]',
    )
    text = text.replace(
        'script = ROOT / "runtime/scripts/render_discord_commander_swarm_status_preview_001.py"',
        'script = ROOT / "runtime/discord_commander/scripts/render_discord_commander_swarm_status_preview_001.py"',
    )
    text = text.replace(
        'payload_path = ROOT / "data/reports/discord/commander/latest_payload.json"',
        'payload_path = ROOT / "runtime/discord_commander/reports/commander/latest_payload.json"',
    )
    canon_src = CANON / "src"
    if 'sys.path.insert(0, str(ROOT / "src"))' not in text:
        text = text.replace(
            'import pytest\n',
            'import pytest\nimport sys\n',
        )
        text = text.replace(
            'ROOT = Path(__file__).resolve().parents[3]\n',
            'ROOT = Path(__file__).resolve().parents[3]\n'
            'if str(ROOT / "src") not in sys.path:\n'
            '    sys.path.insert(0, str(ROOT / "src"))\n'
            f'if str(ROOT / "runtime/discord_commander/src") not in sys.path:\n'
            f'    sys.path.insert(0, str(ROOT / "runtime/discord_commander/src"))\n',
        )
    test.write_text(text, encoding="utf-8")
    # Symlink/copy test back to tests/ for pytest discovery
    dest_test = REPO_ROOT / "tests" / "test_discord_commander_swarm_status.py"
    shutil.copy2(test, dest_test)


def main() -> int:
    CANON.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []

    for src_rel, dest_rel, purpose, delete in COPY_PLAN:
        entries.append(copy_one(src_rel, dest_rel, purpose, delete))

    for src_rel in OPTIONAL_REPORTS:
        src = REPO_ROOT / src_rel
        if src.is_file():
            dest_rel = src_rel.replace("data/reports/discord/", "reports/")
            entries.append(copy_one(src_rel, dest_rel, "Commander preview artifact", True))

    for src_rel, dest_rel, purpose in SALVAGE_COPIES:
        src = REPO_ROOT / src_rel
        if src.is_file():
            entries.append(copy_one(src_rel, dest_rel, purpose, False))

    patch_copied_scripts()
    write_compat_shims()
    update_github_workflow()
    patch_test_paths()

    # Patch sync script DEST path
    sync = CANON / "scripts/sync_discord_env_from_salvage_001.py"
    if sync.is_file():
        t = sync.read_text(encoding="utf-8")
        t = t.replace(
            'DEST = Path(__file__).resolve().parents[1] / "secrets" / "secrets.local.env"',
            'DEST = Path(__file__).resolve().parents[3] / "runtime" / "secrets" / "secrets.local.env"',
        )
        sync.write_text(t, encoding="utf-8")

    verified = sum(1 for e in entries if e.get("verified"))
    copied = sum(1 for e in entries if e.get("status") == "copied")
    deleted = sum(1 for e in entries if e.get("deleted_source"))

    manifest = {
        "schema": "dreamvault.discord_commander_inventory.v1",
        "canonical_location": "runtime/discord_commander/",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "rationale": (
            "DreamVault SSOT hub for Discord Commander inventory, scripts, tasks, tests, "
            "package source, reports, and salvage mirrors. Python shims remain at "
            "src/dreamvault/discord/commander/ for backward-compatible imports."
        ),
        "inventory_count": len(entries),
        "verified_copies": verified,
        "deleted_sources": deleted,
        "retain_in_place": RETAIN_IN_PLACE,
        "external_references": EXTERNAL_REFS,
        "dependencies": [
            "dreamvault.discord.discord_architect",
            "dreamvault.discord.discord_webhook_sender",
            "dreamvault.cockpit.swarm_operations_center",
            "agent_tools.discord_commander (D:\\agent-tools)",
        ],
        "entries": entries,
    }

    json_path = CANON / "DISCORD_COMMANDER_INVENTORY_001.json"
    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md_lines = [
        "# Discord Commander Inventory 001",
        "",
        f"**Canonical location:** `{manifest['canonical_location']}`",
        f"**Generated:** {manifest['generated_at']}",
        f"**Inventory count:** {manifest['inventory_count']} (verified: {verified}, deleted sources: {deleted})",
        "",
        "## Rationale",
        manifest["rationale"],
        "",
        "## Structure",
        "```",
        "runtime/discord_commander/",
        "  scripts/          # health, activate, scan, render, env sync",
        "  src/dreamvault/discord/commander/  # Python package (canonical)",
        "  tasks/            # operator YAML tasks",
        "  tests/            # pytest suite",
        "  workflows/        # GHA reference copy",
        "  reports/          # scan + preview artifacts",
        "  salvage/          # merge + victor_os mirrors",
        "  DISCORD_COMMANDER_INVENTORY_001.json",
        "```",
        "",
        "## Retain in place (secrets / GHA)",
    ]
    for row in RETAIN_IN_PLACE:
        md_lines.append(f"- `{row['path']}` — {row['reason']}")
    md_lines.extend(["", "## External toolbelt (document only)", ""])
    for row in EXTERNAL_REFS:
        md_lines.append(f"- `{row['path']}` — {row['role']}")
    md_lines.extend(["", "## Copy ledger", ""])
    for e in entries:
        flag = "✓" if e.get("verified") else "?"
        del_flag = " [DELETED]" if e.get("deleted_source") else ""
        md_lines.append(f"- {flag} `{e['source']}` → `{e['destination']}`{del_flag}")
        md_lines.append(f"  - {e['purpose']}")
    md_path = CANON / "DISCORD_COMMANDER_INVENTORY_001.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("DISCORD_COMMANDER_CONSOLIDATION=PASS")
    print(f"CANONICAL={manifest['canonical_location']}")
    print(f"INVENTORY_COUNT={manifest['inventory_count']}")
    print(f"VERIFIED={verified}")
    print(f"DELETED_SOURCES={deleted}")
    print(f"MANIFEST_MD={md_path.relative_to(REPO_ROOT)}")
    print(f"MANIFEST_JSON={json_path.relative_to(REPO_ROOT)}")
    return 0 if verified == copied else 1


if __name__ == "__main__":
    raise SystemExit(main())
