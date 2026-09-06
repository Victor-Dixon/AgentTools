from __future__ import annotations

from tools_v2.tool_registry import ToolRegistry


EXPECTED = {
    "repo.identity",
    "repo.status",
    "repo.branches",
    "repo.compare",
    "repo.worktrees",
}


def test_repo_tools_are_registered_and_loadable() -> None:
    registry = ToolRegistry()

    assert EXPECTED.issubset(set(registry.list_tools()))

    loaded = {name: registry.get_tool(name) for name in EXPECTED}

    assert set(loaded) == EXPECTED
    assert all(tool.get_spec().name == name for name, tool in loaded.items())
    assert all(tool.get_spec().category == "repo" for tool in loaded.values())


def test_repo_registry_category_is_complete() -> None:
    registry = ToolRegistry()

    assert set(registry.list_by_category("repo")) == EXPECTED
