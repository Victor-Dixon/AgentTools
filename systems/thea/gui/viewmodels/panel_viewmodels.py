"""Container for per-panel view models."""

from typing import Any, Dict


class PanelViewModels:
    """Manage individual panel view models."""

    def __init__(self) -> None:
        self._models: Dict[str, Any] = {}

    def add(self, name: str, model: Any) -> None:
        self._models[name] = model

    def get(self, name: str) -> Any:
        return self._models.get(name)

