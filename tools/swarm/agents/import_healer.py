#!/usr/bin/env python3
"""Import healer with confidence scoring and py_compile safety checks."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Sequence, Tuple

IMPORT_RE = re.compile(r"^(?P<indent>\s*)import\s+(?P<module>[\w\.]+)(?P<tail>\s+as\s+\w+\s*)?$")
FROM_RE = re.compile(
    r"^(?P<indent>\s*)from\s+(?P<module>[\w\.]+)\s+import\s+(?P<tail>.+)$"
)


@dataclass
class RewriteDecision:
    original: str
    replacement: str
    confidence: str
    reason: str


def discover_modules(root: Path) -> set[str]:
    """Discover Python module paths rooted at ``root``."""
    modules: set[str] = set()
    for py_file in root.rglob("*.py"):
        if any(part.startswith(".") for part in py_file.parts):
            continue
        rel = py_file.relative_to(root)
        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            module = ".".join(parts[:-1])
            if module:
                modules.add(module)
            continue
        module = ".".join(parts)
        modules.add(module[:-3])
    return modules


def load_rewrite_map(rewrite_map: Optional[Path]) -> Dict[str, str]:
    if rewrite_map is None:
        return {}
    data = json.loads(rewrite_map.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("rewrite map must be a JSON object")
    cleaned: Dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("rewrite map keys and values must be strings")
        cleaned[key.strip()] = value.strip()
    return cleaned


def resolve_module(
    module: str, discovered: set[str], rewrite_map: Dict[str, str]
) -> Optional[RewriteDecision]:
    mapped = rewrite_map.get(module)
    if mapped:
        if mapped in discovered:
            return RewriteDecision(module, mapped, "high", "exact module match from rewrite map")
        return None

    if module in discovered:
        return None

    suffix_matches = sorted(
        candidate for candidate in discovered if candidate.endswith(f".{module}")
    )
    if len(suffix_matches) == 1:
        return RewriteDecision(module, suffix_matches[0], "medium", "unique suffix match")
    if len(suffix_matches) > 1:
        return RewriteDecision(module, module, "none", "ambiguous suffix matches; skipped")
    return None


def rewrite_line(
    line: str, discovered: set[str], rewrite_map: Dict[str, str]
) -> Tuple[str, Optional[RewriteDecision]]:
    import_match = IMPORT_RE.match(line)
    if import_match:
        module = import_match.group("module")
        decision = resolve_module(module, discovered, rewrite_map)
        if not decision or decision.confidence == "none":
            return line, decision
        new_line = (
            f"{import_match.group('indent')}import {decision.replacement}"
            f"{import_match.group('tail') or ''}"
        )
        return new_line, decision

    from_match = FROM_RE.match(line)
    if from_match:
        module = from_match.group("module")
        decision = resolve_module(module, discovered, rewrite_map)
        if not decision or decision.confidence == "none":
            return line, decision
        new_line = (
            f"{from_match.group('indent')}from {decision.replacement} import "
            f"{from_match.group('tail')}"
        )
        return new_line, decision

    return line, None


def compile_safe(candidate_text: str, source_file: Path) -> Tuple[bool, Optional[str]]:
    with NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(candidate_text)
        tmp_path = Path(tmp.name)
    try:
        py_compile.compile(str(tmp_path), doraise=True)
        return True, None
    except py_compile.PyCompileError as exc:
        return False, str(exc)
    finally:
        tmp_path.unlink(missing_ok=True)


def process_file(
    file_path: Path, discovered: set[str], rewrite_map: Dict[str, str], apply: bool
) -> Dict[str, object]:
    original_text = file_path.read_text(encoding="utf-8")
    lines = original_text.splitlines()

    rewritten_lines: List[str] = []
    rewrites: List[Dict[str, str]] = []
    skipped: List[Dict[str, str]] = []

    for line_no, line in enumerate(lines, start=1):
        updated, decision = rewrite_line(line, discovered, rewrite_map)
        rewritten_lines.append(updated)
        if not decision:
            continue
        payload = {
            "line": str(line_no),
            "original": decision.original,
            "candidate": decision.replacement,
            "confidence": decision.confidence,
            "reason": decision.reason,
        }
        if decision.confidence == "none":
            skipped.append(payload)
        elif updated != line:
            rewrites.append(payload)

    new_text = "\n".join(rewritten_lines) + ("\n" if original_text.endswith("\n") else "")
    changed = new_text != original_text

    compile_ok = True
    compile_error = None
    if changed:
        compile_ok, compile_error = compile_safe(new_text, file_path)
        if compile_ok and apply:
            file_path.write_text(new_text, encoding="utf-8")

    return {
        "file": str(file_path),
        "changed": changed and compile_ok,
        "compile_ok": compile_ok,
        "compile_error": compile_error,
        "rewrites": rewrites if compile_ok else [],
        "skipped": skipped,
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Heal broken imports with confidence scoring")
    parser.add_argument("targets", nargs="+", type=Path, help="Python files to inspect")
    parser.add_argument("--module-root", type=Path, required=True, help="Root for module discovery")
    parser.add_argument("--rewrite-map", type=Path, help="JSON file mapping old module -> new module")
    parser.add_argument("--apply", action="store_true", help="Write safe rewrites to disk")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    discovered = discover_modules(args.module_root)
    rewrite_map = load_rewrite_map(args.rewrite_map)

    results = [
        process_file(target, discovered=discovered, rewrite_map=rewrite_map, apply=args.apply)
        for target in args.targets
    ]

    payload = {
        "module_root": str(args.module_root),
        "total_files": len(results),
        "fixed_files": sum(1 for item in results if item["changed"]),
        "blocked_files": sum(1 for item in results if not item["compile_ok"]),
        "results": results,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
