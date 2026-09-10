"""Record shapes shared by the control plane and its clients.

Every record here is serialisable to the ``dreamos-brain`` (dreamosd) HTTP API
without transformation.  ``Event.to_brain_payload`` is the migration seam.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA = "dream_control.v1"

# Event vocabulary. Anything outside this set is accepted but flagged by
# ``dreamevent --strict`` so the taxonomy stays legible across 8+ agents.
EVENT_TYPES = (
    "agent_registered", "agent_started", "agent_stopped", "agent_heartbeat",
    "lane_claimed", "lane_released", "lane_completed",
    "project_scan_completed", "capability_found", "duplicate_detected",
    "canonical_owner_selected",
    "command_executed", "cpc_capture_created",
    "authority_observed",
    "branch_created", "branch_rewritten", "branch_deleted",
    "pr_created", "pr_head_changed", "pr_marked_ready", "pr_merged",
    "pr_closed_superseded",
    "ci_started", "ci_passed", "ci_failed",
    "worktree_created", "worktree_dirty", "worktree_cleaned", "worktree_removed",
    "vps_process_started", "vps_process_stopped", "runner_changed",
    "verification_passed", "verification_failed",
    "passdown_generated",
)

AGENT_STATUSES = ("idle", "active", "blocked", "waiting_ci", "stopped")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class Event:
    """One structured thing that happened, anywhere in the fleet."""

    event: str
    actor: str
    environment: str
    event_id: str = field(default_factory=lambda: new_id("evt"))
    timestamp: str = field(default_factory=utc_now)
    repo: str | None = None
    lane: str | None = None
    task_id: str | None = None
    status: str | None = None
    source: str = "dream_control"
    authority: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["schema"] = SCHEMA
        return data

    def to_brain_payload(self) -> dict[str, Any]:
        """Shape accepted by ``POST /events`` on dreamos-brain."""
        return {
            "event_type": self.event,
            "source": self.source,
            "actor": self.actor,
            "project": self.repo,
            "task_id": self.task_id,
            "repo": self.repo,
            "status": self.status,
            "payload": {
                "event_id": self.event_id,
                "timestamp": self.timestamp,
                "environment": self.environment,
                "lane": self.lane,
                "authority": self.authority,
                "verification": self.verification,
                **self.payload,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Agent:
    """A registered agent, anywhere in the fleet."""

    agent_id: str
    environment: str
    provider: str = "unknown"
    repo: str | None = None
    active_lane: str | None = None
    task_id: str | None = None
    status: str = "idle"
    capabilities: list[str] = field(default_factory=list)
    tool_access: dict[str, bool] = field(default_factory=dict)
    claimed_at: str | None = None
    last_seen: str = field(default_factory=utc_now)
    last_event: str | None = None
    expected_authority: dict[str, Any] = field(default_factory=dict)
    next_action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Agent:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})

    def is_stale(self, max_age_seconds: int = 3600) -> bool:
        try:
            seen = datetime.fromisoformat(self.last_seen.replace("Z", "+00:00"))
        except ValueError:
            return True
        return (datetime.now(timezone.utc) - seen).total_seconds() > max_age_seconds


@dataclass
class Lane:
    """A unit of durable intent, owned by exactly one agent at a time."""

    lane_id: str
    repo: str
    owner: str | None = None
    status: str = "open"
    task_id: str | None = None
    claimed_at: str | None = None
    released_at: str | None = None
    next_action: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lane:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Capability:
    """A capability and the evidence about where it already exists."""

    capability: str
    canonical_owner: str | None = None
    implementations: list[dict[str, Any]] = field(default_factory=list)
    disposition: dict[str, str] = field(default_factory=dict)
    evidence_source: str = "unknown"
    observed_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Capability:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})
