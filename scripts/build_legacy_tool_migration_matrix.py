from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TOOLS_V2 = ROOT / "tools_v2"
OUT_JSON = ROOT / "docs" / "LEGACY_TOOL_MIGRATION_MATRIX.json"
OUT_MD = ROOT / "docs" / "LEGACY_TOOL_MIGRATION_MATRIX.md"

SKIP_PARTS = {"deprecated", "__pycache__", "quarantine"}


def collect_py(base: Path) -> list[Path]:
    return sorted(
        p for p in base.rglob("*.py")
        if not any(part in SKIP_PARTS for part in p.parts)
    )


def parse_symbols(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    item = {
        "path": rel,
        "classes": [],
        "functions": [],
        "has_main_guard": False,
        "suggested_status": "legacy_review",
        "suggested_target": None,
    }

    text = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text, filename=rel)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            item["classes"].append(node.name)
        elif isinstance(node, ast.FunctionDef):
            item["functions"].append(node.name)
        elif isinstance(node, ast.If):
            try:
                expr = ast.unparse(node.test)
            except Exception:
                expr = ""
            if "__name__" in expr and "__main__" in expr:
                item["has_main_guard"] = True

    name = path.stem.lower()
    v2_names = {p.stem.lower(): p.relative_to(ROOT).as_posix() for p in collect_py(TOOLS_V2)}
    if name in v2_names:
        item["suggested_status"] = "possible_duplicate"
        item["suggested_target"] = v2_names[name]
    elif item["has_main_guard"]:
        item["suggested_status"] = "script_candidate"
    elif item["classes"] or item["functions"]:
        item["suggested_status"] = "salvage_candidate"

    return item


def main() -> None:
    records = [parse_symbols(path) for path in collect_py(TOOLS)]

    OUT_JSON.write_text(json.dumps(records, indent=2), encoding="utf-8")

    counts: dict[str, int] = {}
    for r in records:
        counts[r["suggested_status"]] = counts.get(r["suggested_status"], 0) + 1

    lines = [
        "# Legacy Tool Migration Matrix",
        "",
        "Purpose: classify `tools/` modules before porting, archiving, or deleting.",
        "",
        "## Summary",
        "",
    ]

    for key in sorted(counts):
        lines.append(f"- `{key}`: {counts[key]}")

    lines.extend(["", "## Records", ""])

    for r in records:
        lines.append(f"### `{r['path']}`")
        lines.append("")
        lines.append(f"- status: `{r['suggested_status']}`")
        if r["suggested_target"]:
            lines.append(f"- possible target: `{r['suggested_target']}`")
        lines.append(f"- classes: `{', '.join(r['classes'][:10]) if r['classes'] else 'none'}`")
        lines.append(f"- functions: `{', '.join(r['functions'][:12]) if r['functions'] else 'none'}`")
        lines.append(f"- has_main_guard: `{r['has_main_guard']}`")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE: {OUT_JSON}")
    print(f"WROTE: {OUT_MD}")
    print(json.dumps(counts, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
