"""
Loading Screen Component
Shows progress during application initialization.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient
import logging

logger = logging.getLogger(__name__)

class LoadingScreen(QWidget):
    """Loading screen with progress bar and status updates."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the loading screen UI."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the main frame
        self.main_frame = QFrame()
        self.main_frame.setObjectName("loadingFrame")
        self.main_frame.setStyleSheet("""
            #loadingFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 15px;
                border: 2px solid #3498db;
            }
        """)
        
        frame_layout = QVBoxLayout(self.main_frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(40, 40, 40, 40)
        
        # App title
        title_label = QLabel("Digital Dreamscape")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ecf0f1; margin-bottom: 10px;")
        frame_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Initializing your digital workspace...")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #bdc3c7; margin-bottom: 20px;")
        frame_layout.addWidget(subtitle_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 8px;
                text-align: center;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 6px;
            }
        """)
        frame_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Starting up...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #95a5a6; margin-top: 10px;")
        frame_layout.addWidget(self.status_label)
        
        # Version info
        version_label = QLabel("v1.0.0 - Digital Dreamscape")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(QFont("Arial", 8))
        version_label.setStyleSheet("color: #7f8c8d; margin-top: 20px;")
        frame_layout.addWidget(version_label)
        
        layout.addWidget(self.main_frame)
        
        # Center the window
        self.center_window()
        
    def center_window(self):
        """Center the loading screen on the screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
        
    def update_progress(self, value: int, status: str = None):
        """Update progress bar and status."""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
        QApplication.processEvents()  # Keep UI responsive
        
    def show_loading(self):
        """Show the loading screen."""
        self.show()
        QApplication.processEvents()
        
    def hide_loading(self):
        """Hide the loading screen."""
        self.hide()
        QApplication.processEvents()

class LoadingManager:
    """Manages the loading screen and initialization progress."""
    
    def __init__(self, parent=None):
        self.loading_screen = LoadingScreen(parent)
        self.current_step = 0
        self.total_steps = 0
        self.step_descriptions = []
        
    def start_loading(self, steps: list):
        """Start loading with the given steps."""
        self.total_steps = len(steps)
        self.step_descriptions = steps
        self.current_step = 0
        self.loading_screen.show_loading()
        self.update_progress()
        
    def next_step(self, custom_status: str = None):
        """Move to the next loading step."""
        self.current_step += 1
        if self.current_step <= self.total_steps:
            self.update_progress(custom_status)
            
    def update_progress(self, custom_status: str = None):
        """Update the progress display."""
        if self.current_step <= self.total_steps:
            progress = int((self.current_step / self.total_steps) * 100)
            status = custom_status or self.step_descriptions[self.current_step - 1]
            self.loading_screen.update_progress(progress, status)
            
    def finish_loading(self):
        """Finish loading and hide the screen."""
        self.loading_screen.update_progress(100, "Ready!")
        QTimer.singleShot(500, self.loading_screen.hide_loading)  # Brief delay to show completion
        
    def show(self):
        """Show the loading manager."""
        self.loading_screen.show_loading()
        
    def hide(self):
        """Hide the loading manager."""
        self.loading_screen.hide_loading() 