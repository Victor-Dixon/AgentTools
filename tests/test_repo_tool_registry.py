from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools_v2.tool_registry import ToolRegistry


EXPECTED = {
    "repo.identity",
    "repo.status",
    "repo.branches",
    "repo.compare",
    "repo.worktrees",
}

ROOT = Path(__file__).resolve().parents[1]


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


def test_repo_registry_does_not_require_optional_requests() -> None:
    """Registry-only consumers must not import unrelated optional dependencies."""
    code = r'''
import builtins

real_import = builtins.__import__


def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "requests" or name.startswith("requests."):
        raise ModuleNotFoundError("requests intentionally blocked by registry isolation test")
    return real_import(name, globals, locals, fromlist, level)


builtins.__import__ = guarded_import

from tools_v2.tool_registry import ToolRegistry

expected = {
    "repo.identity",
    "repo.status",
    "repo.branches",
    "repo.compare",
    "repo.worktrees",
}

registry = ToolRegistry()
assert expected.issubset(set(registry.list_tools()))
for name in expected:
    tool = registry.get_tool(name)
    assert tool.get_spec().name == name

print("REGISTRY_OPTIONAL_DEP_ISOLATION=PASS")
'''

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "REGISTRY_OPTIONAL_DEP_ISOLATION=PASS" in result.stdout
