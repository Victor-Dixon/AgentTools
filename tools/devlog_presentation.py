"""Pure, mobile-first Discord DevLog rendering.

The brief only reflects fields actually present in source. Detail pages carry
the byte-for-byte source text in order; no unsupported completion claims.
"""
from __future__ import annotations

import re

# A page also gets a short label and a Discord embed footer. Stay well under
# the 2,000-character message limit and 4,096-character embed-description limit.
PAGE_LIMIT = 1900
DETAIL_BODY_LIMIT = 1700

_ALIASES = {
    "task": "Mission",
    "mission": "Mission",
    "objective": "Mission",
    "work completed": "Work completed",
    "actions taken": "Work completed",
    "actions": "Work completed",
    "verification": "Verification (as reported)",
    "tests": "Verification (as reported)",
    "ci": "Verification (as reported)",
    "discoveries": "Discoveries",
    "findings": "Discoveries",
    "blockers": "Blockers",
    "blocker": "Blockers",
    "next": "Next move",
    "next action": "Next move",
    "next move": "Next move",
    "status": "Reported status",
}
_ORDER = (
    "Mission", "Work completed", "Verification (as reported)",
    "Discoveries", "Blockers", "Next move", "Reported status",
)
_FIELD = re.compile(r"^([A-Za-z][A-Za-z /_-]{0,34})\s*:\s*(.*)$")


def split_lossless(content: str, max_length: int = DETAIL_BODY_LIMIT) -> list[str]:
    """Split any text (including a single long line) without dropping a byte."""
    if max_length < 1:
        raise ValueError("max_length must be positive")
    chunks: list[str] = []
    while content:
        if len(content) <= max_length:
            chunks.append(content)
            break
        boundary = content.rfind("\n", 0, max_length + 1)
        cut = boundary + 1 if max_length // 3 <= boundary < max_length else max_length
        chunks.append(content[:cut])
        content = content[cut:]
    return chunks


def _clean_label(line: str) -> str:
    line = line.strip()
    if line.startswith("#"):
        line = line.lstrip("#").strip()
    else:
        line = line.lstrip("-* ").strip()
    return line.replace("**", "").strip()


def _brief_fields(source: str) -> dict[str, str]:
    lines = source.splitlines()
    result: dict[str, str] = {}
    for index, line in enumerate(lines):
        cleaned = _clean_label(line)
        matched = _FIELD.match(cleaned)
        if matched:
            key = _ALIASES.get(matched.group(1).strip().lower())
            value = matched.group(2).strip()
        else:
            key = _ALIASES.get(cleaned.lower()) if line.lstrip().startswith(("#", "**")) else None
            value = ""
        if not key or key in result:
            continue
        if not value:
            for following in lines[index + 1:]:
                candidate = _clean_label(following).strip()
                if candidate:
                    value = candidate
                    break
        if value:
            # The complete, unmodified source follows in later detail pages.
            result[key] = value[:210] + ("…" if len(value) > 210 else "")
    return result


def render_devlog_pages(agent_id: str, content: str) -> list[str]:
    """Return one concise source-grounded briefing followed by ALL original text."""
    if not content.strip():
        raise ValueError("devlog is empty")
    display_agent = agent_id.strip()[:50] or "Agent"
    fields = _brief_fields(content)
    lines = [f"**{display_agent} · Engineering DevLog**", "**Mission briefing**"]
    if not fields:
        lines.append("No structured briefing fields found; complete original follows.")
    else:
        for field in _ORDER:
            if field in fields:
                lines.append(f"**{field}:** {fields[field]}")
    lines.append("*Full original follows in the detail pages; claims above are agent-reported.*")
    brief = "\n".join(lines)
    if len(brief) > PAGE_LIMIT:
        raise ValueError("brief exceeds page limit")
    chunks = split_lossless(content, DETAIL_BODY_LIMIT)
    count = len(chunks)
    pages = [brief]
    for index, chunk in enumerate(chunks, 1):
        pages.append(f"**Original devlog · {index}/{count}**\n{chunk}")
    if any(len(page) > PAGE_LIMIT for page in pages):
        raise ValueError("rendered page exceeds Discord safety limit")
    return pages


def devlog_webhook_payload(agent_id: str, page: str, index: int, total: int) -> dict:
    """Build one Discord embed; never ping users or roles from log content."""
    return {
        "username": f"{agent_id[:50]} DevLog",
        "allowed_mentions": {"parse": []},
        "embeds": [{
            "title": f"{agent_id[:50]} | Engineering DevLog",
            "description": page,
            "color": 0x5865F2,
            "footer": {"text": f"Page {index}/{total} · Original preserved"},
        }],
    }
