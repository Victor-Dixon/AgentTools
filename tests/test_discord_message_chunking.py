from agent_tools.discord_commander.utils.message_chunking import (
    MAX_FIELD_VALUE,
    SAFE_FIELD_CHUNK,
    chunk_field_value,
)


def test_long_single_line_field_chunks_stay_within_discord_limit():
    message = "x" * 2500

    chunks = chunk_field_value(message)

    assert len(chunks) == 3
    assert all(len(chunk) <= SAFE_FIELD_CHUNK for chunk in chunks)
    assert all(len(chunk) <= MAX_FIELD_VALUE for chunk in chunks)
    assert "".join(chunks) == message


def test_field_chunking_prefers_word_boundaries_without_losing_words():
    message = " ".join(["planner"] * 300)

    chunks = chunk_field_value(message)

    assert len(chunks) > 1
    assert all(len(chunk) <= SAFE_FIELD_CHUNK for chunk in chunks)
    assert " ".join(chunks).split() == message.split()
