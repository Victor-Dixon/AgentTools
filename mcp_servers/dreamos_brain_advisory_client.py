#!/usr/bin/env python3
"""Read-only client for dreamos-brain advisory API (canonical corpus proxy)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_SECONDS = 10


def get_base_url() -> str:
    return os.environ.get("DREAMOS_BRAIN_URL", DEFAULT_BASE_URL).rstrip("/")


def _get(path: str) -> dict[str, Any]:
    url = f"{get_base_url()}{path}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def health_check() -> dict[str, Any]:
    return _get("/advisory/health")


def search_advisory(query: str, limit: int = 10) -> dict[str, Any]:
    params = urllib.parse.urlencode({"q": query, "limit": limit})
    return _get(f"/advisory/search?{params}")


def get_entry(entry_id: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(entry_id, safe="")
    return _get(f"/advisory/entries/{encoded}")


def is_api_available() -> bool:
    try:
        payload = health_check()
        return bool(payload.get("ok"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return False


def map_search_results(api_payload: dict[str, Any], agent_id: str, query: str) -> dict[str, Any]:
    raw_results = api_payload.get("results") or []
    results_dict = []
    for row in raw_results:
        results_dict.append(
            {
                "id": row.get("id"),
                "title": row.get("title"),
                "content": row.get("content_preview") or row.get("content") or "",
                "author": row.get("author"),
                "category": row.get("category"),
                "tags": row.get("tags") or [],
                "source": row.get("source"),
                "path": row.get("path"),
                "score": row.get("score"),
            }
        )
    return {
        "success": True,
        "agent_id": agent_id,
        "query": query,
        "results_count": len(results_dict),
        "results": results_dict,
        "non_canonical": True,
        "source": "dreamos-brain-advisory-api",
        "api_base": get_base_url(),
    }
