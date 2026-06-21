from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PYTHON_SURFACES = [
    "swarm_mcp",
    "tools_v2",
    "tools",
    "mcp_servers",
]

SKIP_PARTS = {
    "__pycache__",
    "deprecated",
    "quarantine",
}

SKIP_FILES = {
    # Script-style files may require CLI/env context; these are covered by direct tests later.
    "auth_github.ps1",
}

def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for surface in PYTHON_SURFACES:
        base = ROOT / surface
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            rel = path.relative_to(ROOT)
            if any(part in SKIP_PARTS for part in rel.parts):
                continue
            if path.name in SKIP_FILES:
                continue
            files.append(path)
    return sorted(files)

def test_remaining_python_files_are_syntax_loadable() -> None:
    failures: list[str] = []

    for path in iter_python_files():
        rel = path.relative_to(ROOT)
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            compile(source, str(rel), "exec")
        except Exception as exc:
            failures.append(f"{rel}: {type(exc).__name__}: {exc}")

    assert not failures, "Python syntax/load failures:\n" + "\n".join(failures[:80])

def test_python_cache_dirs_are_not_tracked() -> None:
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "*__pycache__*", "*.pyc"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    tracked_caches = [line for line in result.stdout.splitlines() if line.strip()]
    assert tracked_caches == []
