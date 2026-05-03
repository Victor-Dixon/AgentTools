from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "TOOLBELT_SURFACE_AUDIT.json"
MD = ROOT / "docs" / "TOOLBELT_SURFACE_AUDIT.md"

SURFACES = ["tools", "tools_v2", "mcp_servers", "swarm_mcp"]


def py_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(
        p for p in base.rglob("*.py")
        if "__pycache__" not in p.parts
        and "deprecated" not in p.parts
        and "quarantine" not in p.parts
    )


def summarize_py(path: Path) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    item = {
        "path": rel,
        "syntax_ok": False,
        "classes": [],
        "functions": [],
        "imports": [],
        "has_main_guard": False,
        "risk": "unknown",
    }

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=rel)
        item["syntax_ok"] = True
    except Exception as exc:
        item["error"] = f"{type(exc).__name__}: {exc}"
        item["risk"] = "broken"
        return item

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            item["classes"].append(node.name)
        elif isinstance(node, ast.FunctionDef):
            item["functions"].append(node.name)
        elif isinstance(node, ast.Import):
            item["imports"].extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                item["imports"].append(node.module)
        elif isinstance(node, ast.If):
            test = ast.unparse(node.test) if hasattr(ast, "unparse") else ""
            if "__name__" in test and "__main__" in test:
                item["has_main_guard"] = True

    if rel.startswith("tools_v2/"):
        item["risk"] = "keep_active"
    elif rel.startswith("swarm_mcp/"):
        item["risk"] = "keep_active"
    elif rel.startswith("mcp_servers/"):
        item["risk"] = "adapter_surface"
    elif rel.startswith("tools/"):
        item["risk"] = "legacy_review"

    return item


def main() -> None:
    records = []
    for surface in SURFACES:
        for path in py_files(ROOT / surface):
            records.append(summarize_py(path))

    by_surface = {}
    for r in records:
        top = r["path"].split("/", 1)[0]
        by_surface.setdefault(top, []).append(r)

    OUT.write_text(json.dumps(records, indent=2), encoding="utf-8")

    lines = [
        "# Toolbelt Surface Audit",
        "",
        "## Summary",
        "",
    ]

    for surface in SURFACES:
        rows = by_surface.get(surface, [])
        lines.append(f"- `{surface}`: {len(rows)} Python files")

    lines.extend([
        "",
        "## Classification Policy",
        "",
        "- `keep_active`: canonical runtime/toolbelt code.",
        "- `adapter_surface`: MCP wrapper/server layer requiring registry tests.",
        "- `legacy_review`: old toolbelt surface requiring migration or archive decision.",
        "- `broken`: syntax or parse failure.",
        "",
        "## Files",
        "",
    ])

    for r in records:
        lines.append(f"### `{r['path']}`")
        lines.append("")
        lines.append(f"- risk: `{r['risk']}`")
        lines.append(f"- syntax_ok: `{r['syntax_ok']}`")
        lines.append(f"- classes: `{', '.join(r['classes'][:12]) if r['classes'] else 'none'}`")
        lines.append(f"- functions: `{', '.join(r['functions'][:18]) if r['functions'] else 'none'}`")
        if r.get("error"):
            lines.append(f"- error: `{r['error']}`")
        lines.append("")

    MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"WROTE: {OUT}")
    print(f"WROTE: {MD}")
    print(json.dumps({k: len(v) for k, v in by_surface.items()}, indent=2))


if __name__ == "__main__":
    main()
