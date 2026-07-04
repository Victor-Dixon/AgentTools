"""Basic application menu bar."""

from PyQt6.QtWidgets import QMenuBar, QApplication, QMessageBox
from PyQt6.QtGui import QAction


class MenuBar(QMenuBar):
    """Application menu bar with simple File and Help menus."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_menus()

    # ------------------------------------------------------------------
    def _create_menus(self) -> None:
        """Set up the File and Help menus."""
        file_menu = self.addMenu("&File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._exit_app)
        file_menu.addAction(exit_action)

        help_menu = self.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # ------------------------------------------------------------------
    def _exit_app(self) -> None:
        QApplication.instance().quit()

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About",
            "Digital Dreamscape\nModular GUI Prototype",
        )

