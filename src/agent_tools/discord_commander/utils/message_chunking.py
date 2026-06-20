"""Discord message chunking — promoted slice from Agent_Cellphone_V2 Commander."""

from __future__ import annotations

MAX_MESSAGE_LENGTH = 2000
MAX_EMBED_DESCRIPTION = 4096
MAX_FIELD_VALUE = 1024
SAFE_MESSAGE_CHUNK = 1900
SAFE_FIELD_CHUNK = 950
SAFE_EMBED_DESCRIPTION_CHUNK = 4000


def chunk_message(content: str, max_size: int = SAFE_MESSAGE_CHUNK) -> list[str]:
    if len(content) <= max_size:
        return [content]
    chunks: list[str] = []
    current = ""
    for line in content.split("\n"):
        if len(current) + len(line) + 1 > max_size:
            if current:
                chunks.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks if chunks else [content[:max_size]]


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
