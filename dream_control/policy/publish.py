"""Publishing policy: internal recording is not external publishing.

Recording a control-plane event is always allowed.  Posting to Discord, Slack,
or X is a separate authorisation, defaulting to OFF.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any

from ..config import Paths, paths, read_json

DEFAULT_POLICY: dict[str, Any] = {
    "local_capture": True,
    "control_plane_event": True,
    "cockpit_feed": True,
    "discord_publish": False,
    "slack_publish": False,
    "x_publish": False,
}


@dataclass
class PublishDecision:
    channel: str
    allowed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_policy(*, p: Paths | None = None) -> dict[str, Any]:
    policy = dict(DEFAULT_POLICY)
    stored = read_json((p or paths()).policies_file, {})
    if isinstance(stored, dict):
        for key in DEFAULT_POLICY:
            if key in stored:
                policy[key] = bool(stored[key])
    return policy


def publish_allowed(channel: str, *, p: Paths | None = None) -> PublishDecision:
    """Gate one external publishing channel.

    An explicit per-invocation override is honoured only when it is an opt-in
    environment variable set by the operator (e.g. ``DREAMOS_PUBLISH_DISCORD=1``).
    """
    key = f"{channel}_publish"
    policy = load_policy(p=p)
    if key not in policy:
        return PublishDecision(channel, False, f"unknown channel '{channel}'; denied by default")

    override = os.environ.get(f"DREAMOS_PUBLISH_{channel.upper()}")
    if override is not None:
        allowed = override.strip() in {"1", "true", "TRUE", "yes"}
        return PublishDecision(
            channel, allowed, f"operator override DREAMOS_PUBLISH_{channel.upper()}={override}"
        )

    allowed = bool(policy[key])
    return PublishDecision(
        channel,
        allowed,
        f"policy {key}={allowed}" + ("" if allowed else " (external publishing is opt-in)"),
    )
