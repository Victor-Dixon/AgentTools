"""ProjectScanner-derived discovery evidence.

This module does NOT scan.  ProjectScanner owns discovery; we consume the
artifacts and CLI it already publishes:

  * ``<repo>/runtime/state/intelligence_packet.v1.json``  (per-repo packet)
  * ``projectscanner/runtime/state/repo_graph.json``      (portfolio graph)
  * ``projectscanner/runtime/project_artifacts/``         (ecosystem artifacts)
  * ``projectscanner scan|export|history`` CLI
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config import OperatorConfig, project_root_for, read_json
from ._run import run

PACKET_RELPATH = Path("runtime") / "state" / "intelligence_packet.v1.json"
REPO_GRAPH_RELPATH = Path("runtime") / "state" / "repo_graph.json"
ARTIFACTS_RELPATH = Path("runtime") / "project_artifacts"


def scanner_root(config: OperatorConfig | None = None) -> Path | None:
    return project_root_for("projectscanner", config or OperatorConfig.load())


def available(config: OperatorConfig | None = None) -> dict[str, Any]:
    """Whether ProjectScanner is usable from this environment, and how."""
    root = scanner_root(config)
    if root is None:
        return {"available": False, "reason": "projectscanner checkout not found on this machine"}
    code, out, _ = run(["python3", "-c", "import projectscanner; print(projectscanner.__file__)"])
    return {
        "available": True,
        "root": str(root),
        "importable": code == 0,
        "cli": "projectscanner",
        "commands": ["scan", "export", "planning", "ingest", "history"],
        "artifacts_dir": str(root / ARTIFACTS_RELPATH),
        "repo_graph": str(root / REPO_GRAPH_RELPATH),
    }


def load_packet(repo: str, config: OperatorConfig | None = None) -> dict[str, Any]:
    """Per-repo ProjectScanner intelligence packet, if one has been generated."""
    root = project_root_for(repo, config or OperatorConfig.load())
    if root is None:
        return {"available": False, "reason": f"{repo} not present locally"}
    packet_path = root / PACKET_RELPATH
    if not packet_path.is_file():
        return {
            "available": False,
            "reason": f"no intelligence packet at {packet_path}; run: projectscanner scan {root}",
        }
    packet = read_json(packet_path, {})
    return {"available": True, "path": str(packet_path), "packet": packet}


def load_repo_graph(config: OperatorConfig | None = None) -> dict[str, Any]:
    root = scanner_root(config)
    if root is None:
        return {"available": False, "reason": "projectscanner checkout not found"}
    graph_path = root / REPO_GRAPH_RELPATH
    if not graph_path.is_file():
        return {"available": False, "reason": f"no repo graph at {graph_path}"}
    return {"available": True, "path": str(graph_path), "graph": read_json(graph_path, {})}


def collect(config: OperatorConfig | None = None) -> dict[str, Any]:
    """Discovery evidence summary for passdown."""
    config = config or OperatorConfig.load()
    state = available(config)
    if not state.get("available"):
        return state
    graph = load_repo_graph(config)
    packets = {repo: load_packet(repo, config).get("available", False) for repo in config.repos}
    state.update(
        {
            "repo_graph_available": graph.get("available", False),
            "packets_present": sorted(repo for repo, present in packets.items() if present),
            "packets_missing": sorted(repo for repo, present in packets.items() if not present),
        }
    )
    return state


def _iter_evidence_sources(config: OperatorConfig) -> list[tuple[str, dict[str, Any]]]:
    sources: list[tuple[str, dict[str, Any]]] = []
    graph = load_repo_graph(config)
    if graph.get("available"):
        sources.append(("repo_graph", graph.get("graph", {})))
    for repo in config.repos:
        packet = load_packet(repo, config)
        if packet.get("available"):
            sources.append((f"packet:{repo}", packet.get("packet", {}) or {}))
    return sources


def _hits_in(blob: Any, needle: str) -> bool:
    if isinstance(blob, str):
        return needle in blob.lower()
    if isinstance(blob, dict):
        return any(_hits_in(k, needle) or _hits_in(v, needle) for k, v in blob.items())
    if isinstance(blob, list):
        return any(_hits_in(item, needle) for item in blob)
    return False


def capability_search(capability: str, config: OperatorConfig | None = None) -> dict[str, Any]:
    """Find where a capability already exists, using ProjectScanner evidence.

    Returns ``{"capability", "implementations": [{repo, kind, evidence}], ...}``
    suitable for ``policy.duplication.check_duplication``.
    """
    config = config or OperatorConfig.load()
    needle = capability.strip().lower().replace("-", "_")
    implementations: list[dict[str, Any]] = []
    searched: list[str] = []

    for label, blob in _iter_evidence_sources(config):
        searched.append(label)
        if _hits_in(blob, needle) or _hits_in(blob, needle.replace("_", " ")):
            repo = label.split(":", 1)[1] if ":" in label else "portfolio"
            implementations.append(
                {"repo": repo, "kind": "projectscanner_evidence", "evidence": label}
            )

    return {
        "capability": capability,
        "implementations": implementations,
        "sources_searched": searched,
        "evidence_source": "projectscanner",
        "complete": bool(searched),
        "reason": "" if searched else "no ProjectScanner artifacts available; evidence incomplete",
    }
