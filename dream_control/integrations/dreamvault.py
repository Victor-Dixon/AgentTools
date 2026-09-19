"""DreamVault adapter: durable intent, authority, and governance.

DreamVault already publishes the registries we need; we read them rather than
maintaining a competing copy:

  * ``governance/canonical_authority_registry.yaml``
  * ``data/registry/capability_authority_registry.json``
  * ``data/registry/repo_governance.yaml``
  * ``data/registry/agenttools_capability_registry.json``
  * ``runtime/state/planner/``
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..config import OperatorConfig, project_root_for, read_json

AUTHORITY_YAML = Path("governance") / "canonical_authority_registry.yaml"
CAPABILITY_JSON = Path("data") / "registry" / "capability_authority_registry.json"
REPO_GOVERNANCE_YAML = Path("data") / "registry" / "repo_governance.yaml"
PLANNER_STATE = Path("runtime") / "state" / "planner"


def root(config: OperatorConfig | None = None) -> Path | None:
    return project_root_for("DreamVault", config or OperatorConfig.load())


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Minimal indentation-aware YAML reader for the flat registries we read.

    DreamVault's registries are plain nested mappings and string lists; a full
    YAML dependency is not warranted for a Termux-first client.  Used only when
    PyYAML is unavailable.
    """
    root_node: dict[str, Any] = {}
    # stack entries: (indent, container, parent, key) -- parent/key let an
    # empty mapping be promoted to a list when its first child is "- item".
    stack: list[tuple[int, Any, Any, str | None]] = [(-2, root_node, None, None)]

    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        line = raw.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        _, container, parent, key = stack[-1]

        if stripped.startswith("- "):
            value = stripped[2:].strip().strip('"').strip("'")
            if isinstance(container, dict) and not container and parent is not None and key is not None:
                container = []
                parent[key] = container
                stack[-1] = (stack[-1][0], container, parent, key)
            if isinstance(container, list):
                container.append(value)
            continue

        match = re.match(r'^([\w.\-/]+):\s*(.*)$', stripped)
        if not match or not isinstance(container, dict):
            continue
        child_key, value = match.group(1), match.group(2).strip()
        if value == "":
            child: Any = {}
            container[child_key] = child
            stack.append((indent, child, container, child_key))
        else:
            container[child_key] = value.strip('"').strip("'")

    return root_node


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        return _parse_simple_yaml(text)


def collect_authority(config: OperatorConfig | None = None) -> dict[str, Any]:
    """Canonical ownership: who owns which capability domain."""
    config = config or OperatorConfig.load()
    dv_root = root(config)
    if dv_root is None:
        return {"available": False, "reason": "DreamVault checkout not found on this machine"}

    authorities = _load_yaml(dv_root / AUTHORITY_YAML).get("authorities", {})
    capabilities = read_json(dv_root / CAPABILITY_JSON, {})
    governance = _load_yaml(dv_root / REPO_GOVERNANCE_YAML).get("repos", {})

    owners: dict[str, str] = {}
    for domain, entry in (authorities or {}).items():
        if isinstance(entry, dict) and entry.get("canonical_repo"):
            owners[domain] = str(entry["canonical_repo"])
    for domain, entry in (capabilities or {}).items():
        if isinstance(entry, dict) and entry.get("canonical_owner"):
            owners.setdefault(domain, str(entry["canonical_owner"]))

    return {
        "available": True,
        "root": str(dv_root),
        "canonical_owners": owners,
        "capability_registry": capabilities,
        "repo_governance": governance,
        "protected_repos": sorted(
            repo for repo, entry in (governance or {}).items()
            if isinstance(entry, dict) and entry.get("destructive_cleanup") == "protected"
        ),
    }


def canonical_owner(capability: str, config: OperatorConfig | None = None) -> str | None:
    """Governance answer for 'who owns this capability?'."""
    authority = collect_authority(config)
    if not authority.get("available"):
        return None
    owners = authority["canonical_owners"]
    key = capability.strip().lower().replace("-", "_").replace(" ", "_")
    if key in owners:
        return owners[key]
    for domain, owner in owners.items():
        if key in domain or domain in key:
            return owner

    # Fall back to the per-repo `owns:` declarations in repo_governance.yaml.
    for repo, entry in (authority.get("repo_governance") or {}).items():
        if not isinstance(entry, dict):
            continue
        owned = entry.get("owns")
        owned = owned if isinstance(owned, list) else []
        for domain in owned:
            domain_key = str(domain).strip().lower()
            if key == domain_key or key in domain_key or domain_key in key:
                return repo
    return None


def collect_planner(config: OperatorConfig | None = None) -> dict[str, Any]:
    """Current durable intent: active lane and next action, per DreamVault."""
    dv_root = root(config)
    if dv_root is None:
        return {"available": False, "reason": "DreamVault checkout not found"}
    planner_dir = dv_root / PLANNER_STATE
    packet: dict[str, Any] = {}
    for candidate in ("latest_next_lane.json", "planner_packet.json", "next_lane.json"):
        path = planner_dir / candidate
        if path.is_file():
            packet = read_json(path, {})
            break
    if not packet:
        outbox = dv_root / "runtime" / "outbox" / "planner" / "latest_next_lane.json"
        if outbox.is_file():
            packet = read_json(outbox, {})
    if not packet:
        return {"available": False, "reason": f"no planner packet under {planner_dir}"}
    return {
        "available": True,
        "next_lane": packet.get("next_lane"),
        "next_task": packet.get("next_task"),
        "packet": packet,
    }


def dump(config: OperatorConfig | None = None) -> str:
    return json.dumps(collect_authority(config), indent=2, sort_keys=True)
