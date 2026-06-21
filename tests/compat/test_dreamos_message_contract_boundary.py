"""
Compatibility boundary test for Dream.os-Core message contracts.

Dream.os-Core owns the canonical message schema and lifecycle contract.
AgentTools must not define a competing message contract SSOT.
"""

from __future__ import annotations

import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _projects_root() -> Path:
    # AgentTools/tests/compat/test_x.py -> AgentTools -> projects
    return _repo_root().parent


def test_dreamos_core_schema_sources_exist() -> None:
    projects_root = _projects_root()
    core = projects_root / "Dream.os-Core"

    expected = [
        core / "contracts" / "message_schema.json",
        core / "src" / "core" / "schemas" / "bus_message.schema.json",
    ]

    existing = [path for path in expected if path.exists()]

    assert existing, (
        "No Dream.os-Core canonical message schema found. "
        "Expected one of: "
        + ", ".join(str(path) for path in expected)
    )

    for path in existing:
        json.loads(path.read_text(encoding="utf-8"))


def test_agenttools_does_not_define_competing_message_schema() -> None:
    repo = _repo_root()

    forbidden_names = {
        "message_schema.json",
        "bus_message.schema.json",
        "bus_message_schema.json",
    }

    offenders = []
    for path in repo.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts or "node_modules" in path.parts:
            continue
        if path.is_file() and path.name in forbidden_names:
            # Contract snapshots are allowed only under tests/compat/snapshots if added later.
            rel = path.relative_to(repo)
            if rel.parts[:3] == ("tests", "compat", "snapshots"):
                continue
            offenders.append(str(rel))

    assert not offenders, (
        "AgentTools must not define a competing message contract schema. "
        f"Offenders: {offenders}"
    )
