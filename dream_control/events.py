"""Append-only event store (JSONL) with a dreamosd sync seam.

Recording is *internal* and always safe.  Publishing anywhere external
(Discord, Slack, X) is a separate, policy-gated decision -- see
``dream_control.policy.publish``.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from .config import Paths, paths
from .models import EVENT_TYPES, Event


class UnknownEventType(ValueError):  # noqa: N818 - domain name reads better
    """Raised by ``record(..., strict=True)`` for an out-of-vocabulary event."""


def record(event: Event, *, p: Paths | None = None, strict: bool = False) -> Event:
    """Append one event to the local store. Never publishes externally."""
    if strict and event.event not in EVENT_TYPES:
        raise UnknownEventType(f"unknown event type: {event.event}")
    p = (p or paths()).ensure()
    line = json.dumps(event.to_dict(), sort_keys=True)
    with p.event_log.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return event


def iter_events(*, p: Paths | None = None) -> Iterator[Event]:
    p = p or paths()
    if not p.event_log.is_file():
        return
    with p.event_log.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield Event.from_dict(json.loads(line))
            except (ValueError, TypeError):
                continue


def recent(
    limit: int = 25,
    *,
    p: Paths | None = None,
    repo: str | None = None,
    actor: str | None = None,
    lane: str | None = None,
    event_types: Iterable[str] | None = None,
) -> list[Event]:
    """Most recent events first, optionally filtered."""
    wanted = set(event_types) if event_types else None
    selected = [
        event
        for event in iter_events(p=p)
        if (repo is None or event.repo == repo)
        and (actor is None or event.actor == actor)
        and (lane is None or event.lane == lane)
        and (wanted is None or event.event in wanted)
    ]
    selected.sort(key=lambda e: (e.timestamp, e.event_id), reverse=True)
    return selected[:limit]


def last_of_type(event_type: str, *, p: Paths | None = None, repo: str | None = None) -> Event | None:
    found = recent(1, p=p, repo=repo, event_types=[event_type])
    return found[0] if found else None


def sync_state(*, p: Paths | None = None) -> dict[str, Any]:
    """Where local events stand relative to dreamosd (dreamos-brain)."""
    p = p or paths()
    marker = p.cache / "brain_sync.json"
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    total = sum(1 for _ in iter_events(p=p))
    pushed = int(data.get("pushed", 0))
    return {
        "total_events": total,
        "pushed_to_dreamosd": pushed,
        "pending": max(total - pushed, 0),
        "last_sync": data.get("last_sync"),
        "endpoint": data.get("endpoint") or os.environ.get("DREAMOS_BRAIN_URL", ""),
    }


def mark_synced(count: int, endpoint: str, *, p: Paths | None = None) -> dict[str, Any]:
    from .models import utc_now

    p = (p or paths()).ensure()
    payload = {"pushed": count, "endpoint": endpoint, "last_sync": utc_now()}
    (p.cache / "brain_sync.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def export_brain_payloads(*, p: Paths | None = None, since_index: int = 0) -> list[dict[str, Any]]:
    """Events rendered in dreamos-brain ``POST /events`` shape, for sync."""
    return [event.to_brain_payload() for event in list(iter_events(p=p))[since_index:]]


def log_path(*, p: Paths | None = None) -> Path:
    return (p or paths()).event_log
