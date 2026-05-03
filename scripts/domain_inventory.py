#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

ROOTS = [
    Path("swarm_mcp"),
    Path("mcp_servers"),
    Path("tools_v2"),
    Path("tests"),
]

def iter_py_files():
    for root in ROOTS:
        if root.exists():
            yield from sorted(root.rglob("*.py"))

def module_name(path: Path) -> str:
    return str(path.with_suffix("")).replace("/", ".")

def summarize_file(path: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"## {path}\n\nPARSE_ERROR: {exc}\n"

    classes = []
    functions = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append((node.name, methods))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

    lines = [f"## `{path}`", ""]
    if classes:
        lines.append("### Classes")
        for cls, methods in classes:
            lines.append(f"- `{cls}`")
            for method in methods:
                lines.append(f"  - `{method}()`")
        lines.append("")
    if functions:
        lines.append("### Functions")
        for fn in functions:
            lines.append(f"- `{fn}()`")
        lines.append("")
    if not classes and not functions:
        lines.append("_No top-level classes or functions._")
        lines.append("")
    return "\n".join(lines)

def main() -> None:
    out = Path("docs/architecture/CODE_INVENTORY.md")
    parts = [
        "# AgentTools Code Inventory",
        "",
        "Generated inventory of Python classes and functions for domain discovery.",
        "",
    ]

    for path in iter_py_files():
        if "__pycache__" in path.parts:
            continue
        parts.append(summarize_file(path))

    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
