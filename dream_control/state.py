"""Durable state projection: agents, lanes, repositories, capabilities."""

from __future__ import annotations

from typing import Any

from .config import Paths, paths, read_json, write_json
from .models import Agent, Capability, Lane, utc_now


def _load(name: str, p: Paths | None = None) -> dict[str, Any]:
    p = p or paths()
    data = read_json(p.state / name, {})
    return data if isinstance(data, dict) else {}


def _save(name: str, data: dict[str, Any], p: Paths | None = None) -> None:
    p = (p or paths()).ensure()
    write_json(p.state / name, data)


# --------------------------------------------------------------------- agents

def load_agents(p: Paths | None = None) -> dict[str, Agent]:
    raw = _load("agents.json", p).get("agents", {})
    return {key: Agent.from_dict(value) for key, value in raw.items() if isinstance(value, dict)}


def save_agents(agents: dict[str, Agent], p: Paths | None = None) -> None:
    _save(
        "agents.json",
        {"updated_at": utc_now(), "agents": {k: v.to_dict() for k, v in agents.items()}},
        p,
    )


def upsert_agent(agent: Agent, p: Paths | None = None) -> Agent:
    agents = load_agents(p)
    existing = agents.get(agent.agent_id)
    if existing:
        merged = existing.to_dict()
        for key, value in agent.to_dict().items():
            if value not in (None, [], {}):
                merged[key] = value
        agent = Agent.from_dict(merged)
    agent.last_seen = utc_now()
    agents[agent.agent_id] = agent
    save_agents(agents, p)
    return agent


# ---------------------------------------------------------------------- lanes

def load_lanes(p: Paths | None = None) -> dict[str, Lane]:
    raw = _load("active_lanes.json", p).get("lanes", {})
    return {key: Lane.from_dict(value) for key, value in raw.items() if isinstance(value, dict)}


def save_lanes(lanes: dict[str, Lane], p: Paths | None = None) -> None:
    _save(
        "active_lanes.json",
        {"updated_at": utc_now(), "lanes": {k: v.to_dict() for k, v in lanes.items()}},
        p,
    )


class LaneConflict(RuntimeError):  # noqa: N818 - domain name reads better
    """Raised when an agent claims a lane another live agent already owns."""


def claim_lane(lane_id: str, repo: str, owner: str, *, task_id: str | None = None,
               force: bool = False, p: Paths | None = None) -> Lane:
    lanes = load_lanes(p)
    existing = lanes.get(lane_id)
    if existing and existing.owner and existing.owner != owner and existing.status == "claimed" and not force:
        raise LaneConflict(f"lane {lane_id} already claimed by {existing.owner}")
    lane = Lane(
        lane_id=lane_id,
        repo=repo,
        owner=owner,
        status="claimed",
        task_id=task_id,
        claimed_at=utc_now(),
        notes=existing.notes if existing else [],
    )
    lanes[lane_id] = lane
    save_lanes(lanes, p)
    return lane


def release_lane(lane_id: str, *, completed: bool = False, p: Paths | None = None) -> Lane | None:
    lanes = load_lanes(p)
    lane = lanes.get(lane_id)
    if lane is None:
        return None
    lane.status = "completed" if completed else "open"
    lane.owner = None if not completed else lane.owner
    lane.released_at = utc_now()
    lanes[lane_id] = lane
    save_lanes(lanes, p)
    return lane


def lane_owner(lane_id: str, p: Paths | None = None) -> str | None:
    lane = load_lanes(p).get(lane_id)
    return lane.owner if lane else None


# --------------------------------------------------------------- capabilities

def load_capabilities(p: Paths | None = None) -> dict[str, Capability]:
    raw = _load("capabilities.json", p).get("capabilities", {})
    return {k: Capability.from_dict(v) for k, v in raw.items() if isinstance(v, dict)}


def save_capabilities(caps: dict[str, Capability], p: Paths | None = None) -> None:
    _save(
        "capabilities.json",
        {"updated_at": utc_now(), "capabilities": {k: v.to_dict() for k, v in caps.items()}},
        p,
    )


def upsert_capability(cap: Capability, p: Paths | None = None) -> Capability:
    caps = load_capabilities(p)
    caps[cap.capability] = cap
    save_capabilities(caps, p)
    return cap


# -------------------------------------------------------------- repositories

def load_repositories(p: Paths | None = None) -> dict[str, Any]:
    return _load("repositories.json", p).get("repositories", {})


def save_repositories(repos: dict[str, Any], p: Paths | None = None) -> None:
    _save("repositories.json", {"updated_at": utc_now(), "repositories": repos}, p)
