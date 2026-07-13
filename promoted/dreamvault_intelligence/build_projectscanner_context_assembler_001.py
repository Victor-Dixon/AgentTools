#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

OUTPUT_MD = Path(
    "data/reports/projectscanner/projectscanner_context_packet.md"
)

OUTPUT_JSON = Path(
    "data/reports/projectscanner/projectscanner_context_packet.json"
)

SOURCES = [
    Path("data/reports/governance"),
    Path("data/reports/planner"),
]

SUPPRESS = [
    "complete",
    "completed",
    "superseded",
]

MAX_DOCS = 25
MAX_CHARS = 4000


def should_include(text: str) -> bool:
    lowered = text.lower()

    return not any(
        token in lowered
        for token in SUPPRESS
    )


def collect():
    docs = []

    for root in SOURCES:
        if not root.exists():
            continue

        for path in sorted(
            root.glob("*.md")
        ):
            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                continue

            if not should_include(text):
                continue

            docs.append(
                {
                    "path": str(path),
                    "content": text[:MAX_CHARS],
                }
            )

    return docs[:MAX_DOCS]


def render_md(docs):
    parts = [
        "# ProjectScanner Context Packet",
        "",
        "Purpose:",
        "- authoritative context assembly",
        "- duplicate suppression",
        "- planner compression",
        "- agent-ready operational truth",
        "",
    ]

    for doc in docs:
        parts += [
            f"## {doc['path']}",
            "",
            doc["content"],
            "",
        ]

    return "\n".join(parts)


def main():
    docs = collect()

    payload = {
        "documents": len(docs),
        "sources": docs,
    }

    OUTPUT_MD.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_MD.write_text(
        render_md(docs),
        encoding="utf-8",
    )

    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    print(
        "PROJECTSCANNER_CONTEXT_ASSEMBLER=PASS"
    )

    print(
        f"DOCUMENTS={len(docs)}"
    )

    print(f"MD={OUTPUT_MD}")
    print(f"JSON={OUTPUT_JSON}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
