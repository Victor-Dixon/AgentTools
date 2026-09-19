"""Agent message delivery for toolbelt Commander (no GUI dependency).

Delivery order:
1. Optional PyAutoGUI transport via queue_bridge (Agent_Cellphone adapter)
2. Optional UnifiedMessagingService when running beside full repo
3. Outbound webhook router (toolbelt default)
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from .models import CommandResult
from .outbound_router import post_to_discord
from .queue_bridge import deliver_message

logger = logging.getLogger(__name__)

_AGENT_ID_PATTERN = re.compile(r"^agent[- ]?(\d+)$", re.IGNORECASE)


def normalize_agent_id(raw: str) -> Optional[str]:
    """Normalize user input to Agent-N form (1-8)."""
    value = raw.strip()
    if not value:
        return None
    if value.startswith("Agent-") and value[6:].isdigit():
        num = int(value[6:])
        if 1 <= num <= 8:
            return f"Agent-{num}"
        return None
    if value.isdigit():
        num = int(value)
        if 1 <= num <= 8:
            return f"Agent-{num}"
        return None
    match = _AGENT_ID_PATTERN.match(value)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 8:
            return f"Agent-{num}"
    return None


def _format_sender(discord_user: Any | None) -> str:
    if discord_user is None:
        return "Discord Commander"
    name = getattr(discord_user, "display_name", None) or getattr(discord_user, "name", None)
    if name:
        return f"Discord User ({name})"
    return "Discord Commander"


def _try_pyautogui_send(agent_id: str, message: str, transport: Any | None) -> bool:
    if transport is not None:
        return deliver_message(message, agent_id, transport)
    return False


def _try_unified_messaging_send(
    agent_id: str,
    message: str,
    *,
    sender: str,
    discord_user_id: str | None,
    priority: str,
) -> Optional[CommandResult]:
    try:
        from src.services.unified_messaging_service import UnifiedMessagingService  # type: ignore[import-not-found]
    except ImportError:
        return None

    try:
        service = UnifiedMessagingService()
        result = service.send_message(
            agent=agent_id,
            message=message,
            priority=priority,
            use_pyautogui=True,
            wait_for_delivery=False,
            discord_user_id=discord_user_id,
            apply_template=True,
            sender=sender,
        )
        if result.get("success"):
            return CommandResult(
                success=True,
                message=f"Delivered to {agent_id} via PyAutoGUI queue",
                agent=agent_id,
                data={"transport": "unified_messaging_service"},
            )
        return CommandResult(
            success=False,
            message=f"Failed to queue message for {agent_id}",
            agent=agent_id,
            error_code="PYAUTOGUI_QUEUE_FAILED",
        )
    except Exception as exc:
        logger.warning("UnifiedMessagingService send failed: %s", exc)
        return None


def send_agent_message(
    agent_id: str,
    message: str,
    *,
    discord_user: Any | None = None,
    priority: str = "regular",
    transport: Any | None = None,
    dry_run: bool = False,
) -> CommandResult:
    """Send a direct message to an agent using the best available transport."""
    normalized = normalize_agent_id(agent_id)
    if not normalized:
        return CommandResult(
            success=False,
            message=f"Invalid agent id: {agent_id!r}. Use Agent-1 .. Agent-8.",
            agent=agent_id,
            error_code="INVALID_AGENT",
        )

    body = message.strip()
    if not body:
        return CommandResult(
            success=False,
            message="Message body cannot be empty.",
            agent=normalized,
            error_code="EMPTY_MESSAGE",
        )

    sender = _format_sender(discord_user)
    discord_user_id = str(getattr(discord_user, "id", "")) if discord_user else None

    if _try_pyautogui_send(normalized, body, transport):
        return CommandResult(
            success=True,
            message=f"Delivered to {normalized} via transport adapter",
            agent=normalized,
            data={"transport": "queue_bridge"},
        )

    unified = _try_unified_messaging_send(
        normalized,
        body,
        sender=sender,
        discord_user_id=discord_user_id,
        priority=priority,
    )
    if unified is not None:
        return unified

    title = f"Commander → {normalized}"
    routed = post_to_discord(
        agent=normalized,
        title=title,
        message=f"**From:** {sender}\n\n{body}",
        dry_run=dry_run,
    )
    if routed.success:
        routed.data = {**(routed.data or {}), "transport": "outbound_webhook"}
    return routed
