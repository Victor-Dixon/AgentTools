from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "DOCS_DIGEST.md"

DOCS = [
    ROOT / "README.md",
    ROOT / "PRODUCTION_READINESS.md",
    ROOT / "PROJECT_REVIEW.md",
    ROOT / "NEXT_UP.md",
    ROOT / "TOOLBELT_UNIFICATION_PLAN.md",
    ROOT / "TOOLS_CONSOLIDATION_PLAN.md",
    ROOT / "TOOLS_FLATTENING_PLAN.md",
    ROOT / "TOOLS_RANKING_REPORT.md",
    ROOT / "TOOLS_USAGE_GUIDE.md",
    ROOT / "docs" / "TOOL_SURFACES_AND_OVERLAP.md",
    ROOT / "docs" / "CODEBASE_RECON_AND_EXECUTION_PLAN.md",
    ROOT / "docs" / "MCP_TOOLS_ROADMAP.md",
    ROOT / "docs" / "architecture" / "CODE_INVENTORY.md",
    ROOT / "docs" / "architecture" / "DOMAIN_MODEL_DISCOVERY.md",
    ROOT / "docs" / "architecture" / "adr" / "0001-production-architecture.md",
]

def extract_headings(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.startswith("#")][:40]

def main() -> None:
    lines: list[str] = []
    lines.append("# AgentTools Docs Digest")
    lines.append("")
    lines.append("Generated from current repository docs after legacy archive extraction.")
    lines.append("")
    lines.append("## Documents Reviewed")
    lines.append("")

    for path in DOCS:
        rel = path.relative_to(ROOT)
        if not path.exists():
            lines.append(f"- MISSING: `{rel}`")
            continue
        lines.append(f"- `{rel}`")

    lines.append("")
    lines.append("## Heading Inventory")
    lines.append("")

    for path in DOCS:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8", errors="replace")
        headings = extract_headings(text)
        lines.append(f"### `{rel}`")
        lines.append("")
        if headings:
            for heading in headings:
                lines.append(f"- {heading}")
        else:
            lines.append("- No markdown headings found.")
        lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE: {OUT}")

if __name__ == "__main__":
    main()
