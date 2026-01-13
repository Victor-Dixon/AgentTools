"""Simple event dispatch system for the GUI."""

from typing import Callable, Dict, List, Any


class EventController:
    """Register callbacks for named events and emit them."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def on(self, event_name: str, handler: Callable[..., Any]) -> None:
        """Register an event handler."""
        self._listeners.setdefault(event_name, []).append(handler)

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        """Emit an event to all registered handlers."""
        for handler in self._listeners.get(event_name, []):
            handler(*args, **kwargs)

