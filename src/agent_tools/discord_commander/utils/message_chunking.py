"""Discord message chunking — promoted slice from Agent_Cellphone_V2 Commander."""

from __future__ import annotations

MAX_MESSAGE_LENGTH = 2000
MAX_EMBED_DESCRIPTION = 4096
MAX_FIELD_VALUE = 1024
SAFE_MESSAGE_CHUNK = 1900
SAFE_FIELD_CHUNK = 950
SAFE_EMBED_DESCRIPTION_CHUNK = 4000


def chunk_message(content: str, max_size: int = SAFE_MESSAGE_CHUNK) -> list[str]:
    """Split display content without ever exceeding the requested Discord limit.

    This is presentation-only chunking. Callers must deliver the underlying
    logical message before using these chunks to render an acknowledgement.
    """
    if max_size <= 0:
        raise ValueError("max_size must be positive")
    if len(content) <= max_size:
        return [content]

    chunks: list[str] = []
    remaining = content
    while remaining:
        if len(remaining) <= max_size:
            chunks.append(remaining)
            break

        window = remaining[: max_size + 1]
        split_at = max(window.rfind("\n", 0, max_size + 1), window.rfind(" ", 0, max_size + 1))
        if split_at <= 0:
            split_at = max_size

        chunk = remaining[:split_at].strip()
        if not chunk:
            chunk = remaining[:max_size]
            split_at = max_size

        chunks.append(chunk)
        remaining = remaining[split_at:].lstrip()

    return chunks


def chunk_field_value(value: str, max_size: int = SAFE_FIELD_CHUNK) -> list[str]:
    return chunk_message(value, max_size)


def chunk_embed_description(description: str, max_size: int = SAFE_EMBED_DESCRIPTION_CHUNK) -> list[str]:
    return chunk_message(description, max_size)


def format_chunk_header(chunk_num: int, total_chunks: int) -> str:
    return f"**Part {chunk_num}/{total_chunks}**\n\n"


__all__ = [
    "chunk_message",
    "chunk_field_value",
    "chunk_embed_description",
    "format_chunk_header",
    "MAX_MESSAGE_LENGTH",
    "MAX_FIELD_VALUE",
    "MAX_EMBED_DESCRIPTION",
    "SAFE_MESSAGE_CHUNK",
    "SAFE_FIELD_CHUNK",
]
