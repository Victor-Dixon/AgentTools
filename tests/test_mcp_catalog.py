"""Validate MCP server catalog targets resolve to importable modules or scripts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "mcp_servers" / "all_mcp_servers.json"


def _target_from_args(args: list[str]) -> tuple[str, str]:
    """Return (target_kind, target_value) for a catalog args list."""
    if "-m" in args:
        module_index = args.index("-m")
        return "module", args[module_index + 1]

    for arg in args:
        if arg.endswith(".py"):
            return "script", arg

    raise ValueError(f"Unsupported MCP catalog args: {args!r}")


def _target_exists(target_kind: str, target_value: str) -> bool:
    if target_kind == "module":
        return importlib.util.find_spec(target_value) is not None

    script_path = REPO_ROOT / target_value
    return script_path.is_file()


def _collect_missing_targets() -> list[str]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    missing: list[str] = []

    for name, config in catalog.get("mcpServers", {}).items():
        args = config.get("args", [])
        try:
            target_kind, target_value = _target_from_args(args)
        except ValueError as exc:
            missing.append(f"{name}: {exc}")
            continue

        if not _target_exists(target_kind, target_value):
            missing.append(f"{name}: missing {target_kind} {target_value}")

    return missing


def test_mcp_catalog_file_exists() -> None:
    assert CATALOG_PATH.is_file(), f"Missing catalog file: {CATALOG_PATH}"


def test_mcp_catalog_targets_resolve() -> None:
    missing = _collect_missing_targets()
    assert not missing, "Broken MCP catalog targets:\n" + "\n".join(missing)
