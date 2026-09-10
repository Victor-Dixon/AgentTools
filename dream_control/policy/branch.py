"""Branch governance: preservation doctrine beats automated cleanup."""

from __future__ import annotations

from typing import Any

from ..config import Paths, paths, read_json

# Branches under an active preservation hold. These are NOT stale branches;
# no automatic cleanup process may delete them.
PRESERVATION_HOLDS: dict[str, str] = {
    "feat/captain-governance-mvp-001": "HOLD_SALVAGE_ARCHAEOLOGY",
    "polish/product-surface-001": "HOLD_FORENSIC",
    "reconcile/k2-last-copy-salvage-001": "HOLD_PRESERVE",
}

HOLD_PREFIX = "HOLD_"


def _configured_holds(p: Paths | None = None) -> dict[str, str]:
    """Operator-configured holds merged over the built-in doctrine."""
    policies = read_json((p or paths()).policies_file, {})
    holds = dict(PRESERVATION_HOLDS)
    configured = policies.get("preservation_holds") if isinstance(policies, dict) else None
    if isinstance(configured, dict):
        holds.update({str(k): str(v) for k, v in configured.items()})
    return holds


def branch_disposition(branch: str, *, p: Paths | None = None) -> dict[str, Any]:
    """Classify a branch for cleanup purposes."""
    holds = _configured_holds(p)
    hold = holds.get(branch)
    return {
        "branch": branch,
        "hold": hold,
        "preserved": hold is not None,
        "cleanup_allowed": hold is None,
        "reason": (
            f"{hold}: preservation doctrine forbids automated deletion"
            if hold
            else "no preservation hold recorded"
        ),
    }


def cleanup_allowed(branch: str, *, p: Paths | None = None) -> bool:
    """Hard gate for any automated branch deletion."""
    return branch_disposition(branch, p=p)["cleanup_allowed"]


def preserved_branches(*, p: Paths | None = None) -> dict[str, str]:
    return _configured_holds(p)
