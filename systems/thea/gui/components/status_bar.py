"""Thin wrapper around :class:`QStatusBar`."""

from PyQt6.QtWidgets import QStatusBar


class StatusBar(QStatusBar):
    """Application status bar with helper method."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def update_status(self, message: str, timeout: int = 0) -> None:
        """Show a message in the status bar."""
        self.showMessage(message, timeout)

