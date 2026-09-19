"""Shared subprocess helper with hard timeouts."""

from __future__ import annotations

import subprocess
from pathlib import Path


def run(argv: list[str], *, cwd: Path | None = None, timeout: int = 15) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"command not found: {argv[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s: {' '.join(argv)}"
    except OSError as exc:  # pragma: no cover - platform specific
        return 1, "", str(exc)
