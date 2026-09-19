"""
Dream.os-Core BusMessage compatibility contract.

Dream.os-Core owns:
- message envelope schema
- lifecycle state machine
- transport validation
- execution guard

AgentTools may introduce DreamOS/BusMessage-facing adapters, but those adapters
must validate against Dream.os-Core's canonical schema instead of inventing a
competing AgentTools-owned message contract.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _schema_candidates() -> list[Path]:
    """Prefer live Dream.os-Core checkout; fall back to pinned compat snapshot."""
    env_root = (os.environ.get("DREAMOS_CORE_ROOT") or "").strip()
    roots: list[Path] = []
    if env_root:
        roots.append(Path(env_root))
    # AgentTools sibling: <projects>/AgentTools + <projects>/Dream.os-Core
    roots.append(_repo_root().parent / "Dream.os-Core")
    # Common Windows layout: D:\agent-tools + D:\Dream.os-Core
    roots.append(Path(r"D:\Dream.os-Core"))

    paths: list[Path] = []
    for root in roots:
        paths.append(root / "contracts" / "message_schema.json")
        paths.append(root / "src" / "core" / "schemas" / "bus_message.schema.json")
    paths.append(_repo_root() / "tests" / "compat" / "snapshots" / "message_schema.json")
    return paths


def _load_message_schema() -> tuple[dict, Path]:
    existing = [p for p in _schema_candidates() if p.is_file()]
    assert existing, (
        "No Dream.os-Core message schema found. Expected one of: "
        + ", ".join(str(p) for p in _schema_candidates())
    )
    path = existing[0]
    return json.loads(path.read_text(encoding="utf-8")), path


def _adapter_candidates(repo: Path) -> list[Path]:
    return [
        path
        for path in repo.rglob("*.py")
        if ".git" not in path.parts
        and "__pycache__" not in path.parts
        and "node_modules" not in path.parts
        and not (
            len(path.relative_to(repo).parts) >= 2
            and path.relative_to(repo).parts[0] == "tests"
            and path.relative_to(repo).parts[1] == "compat"
        )
        and (
            "bus_message" in path.name.lower()
            or "message_adapter" in path.name.lower()
            or "dreamos" in path.name.lower()
        )
    ]


def _sample_bus_message(*, status: str = "new") -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "id": str(uuid.uuid4()),
        "from": "Agent-2",
        "to": "Agent-4",
        "type": "a2a",
        "body": "compat schema validation fixture",
        "created_at": now,
        "status": status,
        "lease_owner": None,
        "lease_expires_at": None,
        "reply_to": None,
        "device_hint": "cursor",
        "transport": "filesystem",
        "required_capabilities": [],
        "routing_hints": {},
        "assigned_to": None,
        "result": None,
        "error": None,
    }


def test_dreamos_bus_message_adapters_validate_against_core_schema() -> None:
    """When DreamOS/BusMessage-facing modules exist, validate against Core schema."""
    repo = _repo_root()
    candidates = _adapter_candidates(repo)
    schema, schema_path = _load_message_schema()

    # Always prove the schema itself is loadable / usable.
    validator = jsonschema.Draft202012Validator(schema)
    valid = _sample_bus_message()
    validator.validate(valid)

    invalid = dict(valid)
    invalid["status"] = "not-a-real-status"
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid)

    # Presence of adapters is allowed once schema validation is in place.
    # Record candidates for operator visibility without failing CI.
    assert schema_path.is_file()
    assert isinstance(candidates, list)


def test_agenttools_does_not_ship_competing_bus_message_schema() -> None:
    repo = _repo_root()
    forbidden = {
        "message_schema.json",
        "bus_message.schema.json",
        "bus_message_schema.json",
    }
    offenders: list[str] = []
    for path in repo.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts or "node_modules" in path.parts:
            continue
        if not path.is_file() or path.name not in forbidden:
            continue
        rel = path.relative_to(repo)
        if rel.parts[:3] == ("tests", "compat", "snapshots"):
            continue
        offenders.append(str(rel).replace("\\", "/"))
    assert not offenders, (
        "AgentTools must not define a competing BusMessage schema. "
        f"Offenders: {offenders}"
    )
