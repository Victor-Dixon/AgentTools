"""
Base Panel - Common GUI Panel Functionality
==========================================

This module provides the base class for all GUI panels with common
functionality like initialization, UI setup, progress tracking, and
signal handling.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QGroupBox, QTabWidget, QFrame, QScrollArea,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class BasePanel(QWidget):
    """Base class for all GUI panels with common functionality."""
    
    # Common signals
    data_updated = pyqtSignal(dict)      # Data update signal
    progress_updated = pyqtSignal(int)   # Progress update signal
    status_updated = pyqtSignal(str)     # Status update signal
    error_occurred = pyqtSignal(str)     # Error signal
    
    def __init__(self, title: str = "Panel", description: str = "", parent=None):
        """Initialize the base panel."""
        super().__init__(parent)
        
        # Panel metadata
        self.title = title
        self.description = description
        self.panel_name = self.__class__.__name__
        
        # State management
        self.is_loading = False
        self.is_initialized = False
        self.last_refresh = None
        
        # UI components
        self.tab_widget = None
        self.progress_bar = None
        self.status_label = None
        self.refresh_button = None
        
        # Data storage
        self.panel_data = {}
        self.cache = {}
        
        # Initialize UI
        self.init_ui()
        self.setup_common_ui()
        self.connect_common_signals()
        
        # Mark as initialized
        self.is_initialized = True
        logger.info(f"Initialized {self.panel_name}")
    
    def init_ui(self):
        """Initialize the main user interface. Override in subclasses."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create header
        self.create_header(layout)
        
        # Create main content (to be implemented by subclasses)
        self.create_main_content(layout)
        
        # Create common sections
        self.create_progress_section(layout)
        self.create_status_section(layout)
    
    def setup_common_ui(self):
        """Setup common UI elements."""
        # Create tab widget if not already created
        if not self.tab_widget:
            self.tab_widget = QTabWidget()
        
        # Create progress bar
        if not self.progress_bar:
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
        
        # Create status label
        if not self.status_label:
            self.status_label = QLabel("Ready")
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def create_header(self, layout: QVBoxLayout):
        """Create the panel header with title and description."""
        # Title
        header = QLabel(self.title)
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        if self.description:
            desc = QLabel(self.description)
            desc.setWordWrap(True)
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(desc)
    
    def create_main_content(self, layout: QVBoxLayout):
        """Create the main content area. Override in subclasses."""
        # Default implementation - subclasses should override
        content = QLabel("Main content area - override in subclasses")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
    
    def create_progress_section(self, layout: QVBoxLayout):
        """Create the progress tracking section."""
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress controls
        controls_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        progress_layout.addLayout(controls_layout)
        
        layout.addWidget(progress_group)
    
    def create_status_section(self, layout: QVBoxLayout):
        """Create the status display section."""
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
    
    def connect_common_signals(self):
        """Connect common signal handlers."""
        # Connect refresh button
        if self.refresh_button:
            self.refresh_button.clicked.connect(self.refresh_data)
    
    def refresh_data(self):
        """Refresh panel data. Override in subclasses."""
        self.set_status("Refreshing...")
        self.show_progress(True)
        
        try:
            # Subclasses should override this method
            self.load_data()
            self.set_status("Data refreshed successfully")
        except Exception as e:
            self.set_status(f"Error refreshing data: {e}")
            logger.error(f"Error refreshing {self.panel_name}: {e}")
        finally:
            self.show_progress(False)
    
    def load_data(self):
        """Load panel data. Override in subclasses."""
        # Default implementation - subclasses should override
        logger.info(f"Loading data for {self.panel_name}")
    
    def set_status(self, message: str):
        """Set the status message."""
        if self.status_label:
            self.status_label.setText(message)
        self.status_updated.emit(message)
        logger.info(f"{self.panel_name} status: {message}")
    
    def show_progress(self, show: bool, value: int = 0):
        """Show or hide the progress bar."""
        if self.progress_bar:
            self.progress_bar.setVisible(show)
            if show:
                self.progress_bar.setValue(value)
        self.is_loading = show
    
    def update_progress(self, value: int):
        """Update the progress bar value."""
        if self.progress_bar:
            self.progress_bar.setValue(value)
        self.progress_updated.emit(value)
    
    def add_tab(self, widget: QWidget, title: str):
        """Add a tab to the tab widget."""
        if self.tab_widget:
            self.tab_widget.addTab(widget, title)
    
    def get_tab_widget(self) -> QTabWidget:
        """Get the tab widget."""
        return self.tab_widget
    
    def set_data(self, key: str, value: Any):
        """Set panel data."""
        self.panel_data[key] = value
        self.data_updated.emit({key: value})
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get panel data."""
        return self.panel_data.get(key, default)
    
    def clear_data(self):
        """Clear all panel data."""
        self.panel_data.clear()
        self.cache.clear()
    
    def show_error(self, message: str):
        """Show an error message."""
        QMessageBox.critical(self, "Error", message)
        self.error_occurred.emit(message)
        logger.error(f"{self.panel_name} error: {message}")
    
    def show_info(self, message: str):
        """Show an info message."""
        QMessageBox.information(self, "Information", message)
    
    def show_warning(self, message: str):
        """Show a warning message."""
        QMessageBox.warning(self, "Warning", message)
    
    def closeEvent(self, event):
        """Handle panel close event."""
        logger.info(f"Closing {self.panel_name}")
        super().closeEvent(event) 