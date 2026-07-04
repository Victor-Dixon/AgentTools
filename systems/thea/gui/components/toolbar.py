"""Reusable toolbar component."""

from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal


class ToolBar(QToolBar):
    """Toolbar with common actions and signals."""

    refresh_requested = pyqtSignal()
    open_settings = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_actions()

    # ------------------------------------------------------------------
    def _create_actions(self) -> None:
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_requested.emit)
        self.addAction(refresh_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings.emit)
        self.addAction(settings_action)

