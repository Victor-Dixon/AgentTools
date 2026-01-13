#!/usr/bin/env python3
"""Simple DataLoader utility with caching and error recovery."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

class DataLoader:
    """Lightweight data loader with caching and error recovery."""

    def __init__(self, cache_duration: int = 300) -> None:
        self.cache_duration = timedelta(seconds=cache_duration)
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}

    def load(self, key: str, loader: Callable[[], Any], force_reload: bool = False) -> Any:
        if not force_reload and key in self._cache:
            ts = self._timestamps.get(key)
            if ts and datetime.now() - ts < self.cache_duration:
                return self._cache[key]
        try:
            data = loader()
            self._cache[key] = data
            self._timestamps[key] = datetime.now()
            return data
        except Exception as exc:
            logger.error("DataLoader failed for %s: %s", key, exc)
            raise

    def clear(self, key: Optional[str] = None) -> None:
        if key:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._timestamps.clear()
