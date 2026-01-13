"""Data model representing main window state."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MainViewModel:
    """View model for top-level window state."""

    current_panel: Optional[str] = None
    available_panels: List[str] = field(default_factory=list)

