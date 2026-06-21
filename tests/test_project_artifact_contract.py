from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def exists_any(*relative_paths: str) -> bool:
    return any((ROOT / path).exists() for path in relative_paths)


def test_agenttools_operator_entrypoints_exist() -> None:
    required = [
        "README.md",
        "AGENTS.md",
        "NEXT_UP.md",
        "PRODUCTION_READINESS.md",
    ]

    missing = [path for path in required if not (ROOT / path).exists()]

    assert missing == []


def test_agenttools_planning_artifacts_are_discoverable() -> None:
    assert exists_any("MASTER_TASK_LIST.md", "docs/root/MASTER_TASK_LIST.md")
    assert exists_any("MASTER_TASK_LOG.md", "docs/root/MASTER_TASK_LOG.md")
    assert exists_any("PRODUCTION_READINESS.md", "docs/root/PRODUCTION_READINESS.md")


def test_agenttools_root_pointer_targets_exist() -> None:
    pointer = ROOT / "PRODUCTION_READINESS.md"
    text = pointer.read_text(encoding="utf-8")

    assert "docs/root/PRODUCTION_READINESS.md" in text
    assert (ROOT / "docs/root/PRODUCTION_READINESS.md").exists()


def test_discord_controller_contract_inputs_are_machine_discoverable() -> None:
    artifacts = {
        "readme": "README.md",
        "agents": "AGENTS.md",
        "next_up": "NEXT_UP.md",
        "production_readiness": "PRODUCTION_READINESS.md",
        "master_task_list": "docs/root/MASTER_TASK_LIST.md",
        "master_task_log": "docs/root/MASTER_TASK_LOG.md",
    }

    missing = {
        name: path
        for name, path in artifacts.items()
        if not (ROOT / path).exists()
    }

    assert missing == {}
