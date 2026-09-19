"""Collectors turn live systems into normalized control-plane evidence.

Each collector is offline-safe: when its source is unreachable it returns a
record with ``available: False`` and a reason, never an exception.
"""

from . import github, local, projectscanner, vps  # noqa: F401

__all__ = ["github", "local", "projectscanner", "vps"]
