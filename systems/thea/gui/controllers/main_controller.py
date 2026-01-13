"""Central controller coordinating the GUI."""

from typing import Dict
from PyQt6.QtWidgets import QWidget

from gui.event_controller import EventController
from gui.panel_controller import PanelController
from gui.viewmodels import MainViewModel


class MainController:
    """Manage high-level GUI actions and state."""

    def __init__(self) -> None:
        self.event_controller = EventController()
        self.panel_controller = PanelController()
        self.view_model = MainViewModel()

    # ------------------------------------------------------------------
    def register_panels(self, panels: Dict[str, QWidget]) -> None:
        """Register available panels with the panel controller."""
        self.panel_controller.set_panels(panels)
        self.view_model.available_panels = list(panels.keys())

    def set_stack(self, stack) -> None:
        """Provide the stacked widget used for panel switching."""
        self.panel_controller.set_stack(stack)

    def switch_panel(self, name: str) -> None:
        """Switch the visible panel and update state."""
        self.panel_controller.switch_panel(name)
        self.view_model.current_panel = name

    def connect_toolbar(self, toolbar) -> None:
        """Wire toolbar signals to controller slots."""
        toolbar.refresh_requested.connect(
            lambda: self.event_controller.emit_event("refresh")
        )
        toolbar.open_settings.connect(lambda: self.switch_panel("settings"))

