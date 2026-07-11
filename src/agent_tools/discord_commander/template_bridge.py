"""Bridge Discord Commander to DreamVault messaging template SSOT (D2A wrap)."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DREAMVAULT_CANDIDATES = (
    Path(os.environ.get("DREAMVAULT_ROOT", "")),
    Path(r"D:\DreamVault"),
)


def resolve_dreamvault_root() -> Path | None:
    for root in _DREAMVAULT_CANDIDATES:
        if not root or not root.is_dir():
            continue
        registry = root / "runtime" / "messaging" / "templates" / "registry.yaml"
        if registry.is_file():
            return root
    return None


def _ensure_dreamvault_import(root: Path) -> None:
    src = str(root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)


def d2a_template_enabled() -> bool:
    return os.environ.get("DISCORD_COMMANDER_USE_D2A_TEMPLATE", "1").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def wrap_d2a_message(
    *,
    agent_id: str,
    raw_content: str,
    sender: str,
) -> tuple[str, dict[str, Any]]:
    """Wrap operator Discord text in D2A template with agent response policies."""
    if not d2a_template_enabled():
        return raw_content, {"message_template": "raw", "template_category": None}

    root = resolve_dreamvault_root()
    if root is None:
        logger.warning("DreamVault root not found; sending raw !message body")
        return raw_content, {"message_template": "raw", "template_category": None, "template_error": "dreamvault_missing"}

    try:
        _ensure_dreamvault_import(root)
        from dreamvault.agent_cellphone.template_registry import render_d2a

        rendered = render_d2a(
            recipient=agent_id,
            sender=sender,
            content=raw_content,
            interpretation="Execute the user message as an operator directive.",
            actions="Reply in Discord with Task / Actions / Artifacts / Status per policy.",
        )
        return rendered.body, {
            "message_template": "D2A",
            "template_category": "D2A",
            "template_registry": str(root / "runtime" / "messaging" / "templates" / "registry.yaml"),
            "raw_preview": raw_content[:120],
        }
    except Exception as exc:
        logger.exception("D2A template render failed")
        return raw_content, {"message_template": "raw", "template_category": None, "template_error": str(exc)}


def list_template_categories() -> dict[str, Any]:
    """Return template registry summary for status/health checks."""
    root = resolve_dreamvault_root()
    if root is None:
        return {"ok": False, "error": "dreamvault_missing"}
    try:
        _ensure_dreamvault_import(root)
        from dreamvault.agent_cellphone.template_registry import list_templates

        return {"ok": True, "dreamvault_root": str(root), "categories": list_templates()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
