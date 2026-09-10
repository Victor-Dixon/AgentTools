"""Copy the handoff to whatever clipboard this environment has."""

from __future__ import annotations

import subprocess

CANDIDATES = (
    ["termux-clipboard-set"],
    ["pbcopy"],
    ["wl-copy"],
    ["xclip", "-selection", "clipboard"],
    ["xsel", "--clipboard", "--input"],
)


def copy(text: str) -> tuple[bool, str]:
    import shutil

    for argv in CANDIDATES:
        if shutil.which(argv[0]) is None:
            continue
        try:
            subprocess.run(argv, input=text, text=True, timeout=5, check=False)
            return True, argv[0]
        except (OSError, subprocess.TimeoutExpired):
            continue
    return False, "no clipboard command available (handoff written to file instead)"
