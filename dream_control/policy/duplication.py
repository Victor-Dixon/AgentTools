"""Duplication policy.

Core Dream.OS rule: before an agent creates something new, it must prove the
capability does not already exist.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

NOT_AUTHORIZED = "NOT_AUTHORIZED"
AUTHORIZED = "AUTHORIZED"
RISK = "DUPLICATE_IMPLEMENTATION_RISK"


@dataclass
class DuplicationVerdict:
    capability: str
    verdict: str
    canonical_owner: str | None
    implementations: list[dict[str, Any]] = field(default_factory=list)
    warning: str | None = None
    directive: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_duplication(
    capability: str,
    *,
    evidence: dict[str, Any] | None = None,
    requesting_repo: str | None = None,
) -> DuplicationVerdict:
    """Decide whether a new implementation of ``capability`` is authorised.

    ``evidence`` is the merged capability record assembled by
    ``collectors.projectscanner`` and ``integrations.dreamvault``:
    ``{"canonical_owner": str|None, "implementations": [{repo, kind, ...}]}``.
    """
    evidence = evidence or {}
    owner = evidence.get("canonical_owner")
    implementations = [i for i in evidence.get("implementations", []) if isinstance(i, dict)]

    if not implementations and not owner:
        return DuplicationVerdict(
            capability=capability,
            verdict=AUTHORIZED,
            canonical_owner=None,
            implementations=[],
            directive="No existing implementation found. Creating a new one is authorized; "
            "register it as the canonical owner when complete.",
        )

    if owner and requesting_repo and owner == requesting_repo:
        return DuplicationVerdict(
            capability=capability,
            verdict=AUTHORIZED,
            canonical_owner=owner,
            implementations=implementations,
            directive=f"{requesting_repo} is the canonical owner. Extend in place; do not fork.",
        )

    where = ", ".join(sorted({str(i.get("repo", "?")) for i in implementations})) or owner
    return DuplicationVerdict(
        capability=capability,
        verdict=NOT_AUTHORIZED,
        canonical_owner=owner,
        implementations=implementations,
        warning=f"{RISK}: '{capability}' already implemented in {where}.",
        directive=(
            f"Reuse or extend the implementation in {owner or where}. "
            "If a change is genuinely needed, make it there and depend on it."
        ),
    )
