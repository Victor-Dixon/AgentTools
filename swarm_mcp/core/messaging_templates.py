"""SSOT messaging templates used by Swarm messaging systems."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MessageTemplateCategory(str, Enum):
    """Supported message template categories."""

    S2A = "S2A"
    D2A = "D2A"
    C2A = "C2A"
    A2A = "A2A"


@dataclass(frozen=True)
class MessageTemplateInput:
    """Input payload for rendering message templates."""

    category: MessageTemplateCategory
    sender: str
    recipient: str
    body: str
    priority: str = "regular"
    context: str = "N/A"
    action: str = "Review and execute the request."


def _coerce_category(category: str | MessageTemplateCategory) -> MessageTemplateCategory:
    if isinstance(category, MessageTemplateCategory):
        return category
    return MessageTemplateCategory[category.upper()]


def render_message_template(
    category: str | MessageTemplateCategory,
    sender: str,
    recipient: str,
    body: str,
    *,
    priority: str = "regular",
    context: Optional[str] = None,
    action: Optional[str] = None,
) -> str:
    """Render an SSOT message template across A2A/C2A/D2A/S2A channels."""

    payload = MessageTemplateInput(
        category=_coerce_category(category),
        sender=sender,
        recipient=recipient,
        body=body,
        priority=priority.upper(),
        context=context or "N/A",
        action=action or "Review and execute the request.",
    )

    common_header = (
        f"[HEADER] {payload.category.value}\n"
        f"From: {payload.sender}\n"
        f"To: {payload.recipient}\n"
        f"Priority: {payload.priority}\n"
    )

    if payload.category is MessageTemplateCategory.S2A:
        return (
            f"{common_header}"
            "Context:\n"
            f"{payload.context}\n\n"
            "Action Required:\n"
            f"{payload.action}\n\n"
            "Agent Operating Cycle\n"
            "Cycle Checklist:\n"
            "- Read message\n"
            "- Execute task\n"
            "- Report completion\n\n"
            f"Message:\n{payload.body}\n"
        )

    if payload.category is MessageTemplateCategory.D2A:
        return (
            f"{common_header}"
            "Origin: Discord/User relay\n"
            "User Message:\n"
            f"{payload.body}\n\n"
            "Interpretation (agent):\n"
            f"{payload.context}\n\n"
            "Proposed Action:\n"
            f"{payload.action}\n\n"
            "Devlog Command:\n"
            "python tools/captain/session_transition_automator.py --create-devlog\n"
            "#DISCORD\n"
        )

    if payload.category is MessageTemplateCategory.C2A:
        return (
            f"{common_header}"
            "Identity: Captain-to-Agent instruction\n"
            "No-Ack Policy: Begin work immediately; no acknowledgement needed.\n"
            "Cycle Checklist:\n"
            "- Understand objective\n"
            "- Implement change\n"
            "- Validate and report\n\n"
            "Task:\n"
            f"{payload.body}\n\n"
            "Context:\n"
            f"{payload.context}\n\n"
            "Operating Procedures\n"
            "- Keep SSOT intact\n"
            "- Keep edits scoped\n\n"
            "Deliverable:\n"
            f"{payload.action}\n"
            "If blocked:\n"
            "- Report blocker with attempted remediation.\n"
        )

    return (
        f"{common_header}"
        "Identity: Agent-to-Agent coordination\n"
        "No-Ack Policy: Execute/answer directly unless clarification is required.\n"
        "Cycle Checklist:\n"
        "- Read ask\n"
        "- Act or answer\n"
        "- Return result\n\n"
        "Ask/Offer:\n"
        f"{payload.body}\n\n"
        "Context:\n"
        f"{payload.context}\n\n"
        "Next Step:\n"
        f"{payload.action}\n"
        "If blocked:\n"
        "- Share blocker + preferred unblocking option.\n"
        "How to respond:\n"
        "- Reply with outcomes and evidence.\n"
        "#A2A\n"
    )
