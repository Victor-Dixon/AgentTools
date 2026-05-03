from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "README.md",
    "PRODUCTION_READINESS.md",
    "NEXT_UP.md",
    "docs/ARCHIVE_POINTER.md",
    "docs/DOCS_DIGEST.md",
]

def test_required_docs_exist() -> None:
    missing = [path for path in REQUIRED_DOCS if not (ROOT / path).exists()]
    assert missing == []

def test_archive_bulk_not_in_repo() -> None:
    assert not (ROOT / "docs" / "archive").exists()

def test_archive_pointer_mentions_external_archive_location() -> None:
    text = (ROOT / "docs" / "ARCHIVE_POINTER.md").read_text(encoding="utf-8")
    assert "~/archives" in text or "/archives/" in text
    assert "Legacy reports" in text
    assert "kanban-scheduler" in text
