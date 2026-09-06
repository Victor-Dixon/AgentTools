"""dreamos-brain (dreamosd) adapter.

``dreamos-brain`` is the durable control-plane service this client is a
projection of.  dream_control keeps filesystem JSON/JSONL for V1 and syncs to
the service when an endpoint is configured, using its native record shapes.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from ..config import OperatorConfig, paths
from ..events import export_brain_payloads, mark_synced, sync_state


def endpoint(config: OperatorConfig | None = None) -> str:
    config = config or OperatorConfig.load()
    return (
        os.environ.get("DREAMOS_BRAIN_URL")
        or str(config.vps.get("brain_url") or "")
    ).rstrip("/")


def _request(url: str, *, method: str = "GET", body: dict[str, Any] | None = None,
             timeout: int = 10) -> tuple[bool, Any, str]:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    token = os.environ.get("DREAMOS_BRAIN_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            payload = response.read().decode()
        return True, (json.loads(payload) if payload else None), ""
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return False, None, str(exc)


def health(config: OperatorConfig | None = None) -> dict[str, Any]:
    url = endpoint(config)
    if not url:
        return {
            "configured": False,
            "reachable": False,
            "reason": "no dreamosd endpoint configured (set DREAMOS_BRAIN_URL or vps.brain_url)",
            "local_store": sync_state(),
        }
    ok, data, err = _request(f"{url}/health")
    return {
        "configured": True,
        "endpoint": url,
        "reachable": ok,
        "reason": "" if ok else err,
        "health": data,
        "local_store": sync_state(),
    }


def push_events(config: OperatorConfig | None = None, *, dry_run: bool = False) -> dict[str, Any]:
    """Push locally recorded events to dreamosd ``POST /events``."""
    url = endpoint(config)
    state = sync_state()
    pending = export_brain_payloads(since_index=state["pushed_to_dreamosd"])
    if dry_run or not url:
        return {
            "pushed": 0,
            "pending": len(pending),
            "endpoint": url,
            "dry_run": True,
            "reason": "" if url else "no dreamosd endpoint configured",
            "sample": pending[:3],
        }
    pushed = 0
    for payload in pending:
        ok, _, err = _request(f"{url}/events", method="POST", body=payload)
        if not ok:
            return {
                "pushed": pushed,
                "pending": len(pending) - pushed,
                "endpoint": url,
                "error": err,
            }
        pushed += 1
    mark_synced(state["pushed_to_dreamosd"] + pushed, url, p=paths())
    return {"pushed": pushed, "pending": 0, "endpoint": url}
