"""
Dream.os-Core BusMessage compatibility marker.

Dream.os-Core owns:
- message envelope schema
- lifecycle state machine
- transport validation
- execution guard

AgentTools currently owns ToolSpec / ToolResult / IToolAdapter primitives.
When AgentTools introduces a BusMessage adapter, that adapter must validate
against Dream.os-Core's canonical schema instead of creating a competing schema.
"""

from __future__ import annotations

from pathlib import Path


def test_no_agenttools_bus_message_adapter_exists_yet() -> None:
    repo = Path(__file__).resolve().parents[2]

    candidates = [
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

    assert candidates == [], (
        "AgentTools appears to have introduced a BusMessage/DreamOS message adapter. "
        "Replace this marker with a schema-validation test against "
        "Dream.os-Core/contracts/message_schema.json or "
        "Dream.os-Core/src/core/schemas/bus_message.schema.json. "
        f"Candidates: {[str(p.relative_to(repo)) for p in candidates]}"
    )
