"""File + console logging for Discord Commander bot and queue processes."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from .messaging_delivery_log import _log_dir


def configure_discord_commander_logging(component: str, level: int = logging.INFO) -> Path:
    """Attach console + rotating-style file handler for a commander component."""
    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"discord_commander_{component}.log"

    root = logging.getLogger()
    root.setLevel(level)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    stream.setLevel(level)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Avoid duplicate handlers on restart in same interpreter.
    existing_paths = {
        getattr(h, "baseFilename", None) for h in root.handlers if isinstance(h, logging.FileHandler)
    }
    if str(log_path) not in existing_paths:
        root.addHandler(file_handler)
    if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in root.handlers):
        root.addHandler(stream)

    logging.getLogger("agent_tools.discord_commander").setLevel(level)
    return log_path
