#!/usr/bin/env python3
"""
Messaging CLI Wrapper for Agent Tools
=====================================

Routes toolbelt --message to DreamVault messaging SSOT
(runtime/scripts/agent_messaging_send_001.py).

Usage:
    python -m tools.toolbelt --message --help
    python -m tools.toolbelt --message --agent Agent-2 --message "task text"
    python -m tools.toolbelt --message --category c2a --agent Agent-2 --task "Do X"
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _dreamvault_roots() -> list[Path]:
    candidates = [
        Path(os.environ.get("DREAMVAULT_ROOT", "")),
        Path("D:/DreamVault"),
        Path(__file__).resolve().parents[2].parent / "DreamVault",
    ]
    seen: set[str] = set()
    roots: list[Path] = []
    for root in candidates:
        key = str(root)
        if key and key not in seen:
            seen.add(key)
            roots.append(root)
    return roots


def _resolve_ssot_script() -> Path | None:
    for root in _dreamvault_roots():
        script = root / "runtime/scripts/agent_messaging_send_001.py"
        if script.is_file():
            return script
    return None


def main() -> int:
    script = _resolve_ssot_script()
    if script is None:
        print(
            "ERROR: DreamVault messaging SSOT not found.\n"
            "Expected: <DreamVault>/runtime/scripts/agent_messaging_send_001.py\n"
            "Set DREAMVAULT_ROOT or clone DreamVault to D:/DreamVault.",
            file=sys.stderr,
        )
        return 1

    cmd = [sys.executable, str(script), *sys.argv[1:]]
    result = subprocess.run(cmd, cwd=str(script.parents[2]))
    return int(result.returncode)


if __name__ == "__main__":
    sys.exit(main())
