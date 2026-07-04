"""
Refactored Main Window
=====================

A clean, modular main window that uses focused components instead of the monolithic approach.
This replaces the large main_window.py file with a more maintainable architecture.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# Import modular components
from .components.system_initializer import SystemInitializer
from .components.ui_builder import UIBuilder

logger = logging.getLogger(__name__)

# Export the main window class
__all__ = ["TheaMainWindow", "main"]


class TheaMainWindow(QMainWindow):
    """
    Refactored Main Window using modular components.
    
    This window uses focused components instead of monolithic methods,
    making it more maintainable and easier to extend.
    """
    
    # Signals
    initialization_completed = pyqtSignal(dict)  # Emitted when initialization is complete
    initialization_failed = pyqtSignal(str)      # Emitted when initialization fails
    
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("🌌 Dreamscape - AI-Powered Development Platform")
        self.setGeometry(100, 100, 1400, 900)
        
        # Modular components
        self.system_initializer: Optional[SystemInitializer] = None
        self.ui_builder: Optional[UIBuilder] = None
        
        # System references
        self.memory_manager = None
        self.mmorpg_engine = None
        self.discord_manager = None
        self.scraping_manager = None
        self.resume_tracker = None
        self.enhanced_skill_system = None
        
        # Status
        self._is_initialized = False
        
        # Setup UI and initialize
        self._setup_ui()
        self._initialize_systems()
    
    def _setup_ui(self):
        """Setup the main window UI."""
        try:
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create UI builder
            self.ui_builder = UIBuilder()
            main_layout.addWidget(self.ui_builder)
            
            # Connect UI builder signals
            self.ui_builder.panel_switched.connect(self._on_panel_switched)
            self.ui_builder.sidebar_button_clicked.connect(self._on_sidebar_button_clicked)
            
            # Apply initial styling
            self._apply_initial_styling()
            
            logger.info("✅ Main window UI setup completed")
            
        except Exception as e:
            logger.error(f"❌ Main window UI setup failed: {str(e)}")
            raise
    
    def _initialize_systems(self):
        """Initialize all core systems using the system initializer."""
        try:
            logger.info("🚀 Starting system initialization...")
            
            # Create system initializer
            self.system_initializer = SystemInitializer()
            
            # Connect system initializer signals
            self.system_initializer.systems_initialized.connect(self._on_systems_initialized)
            self.system_initializer.system_error.connect(self._on_system_error)
            self.system_initializer.initialization_progress.connect(self._on_initialization_progress)
            
            # Start initialization
            systems_data = self.system_initializer.initialize_systems()
            
            # Store system references
            self._store_system_references(systems_data)
            
            # Update UI builder with system references
            self.ui_builder.set_system_references(systems_data)
            
            # Create actual panels
            self.ui_builder.create_actual_panels()
            
            # Mark as initialized
            self._is_initialized = True
            
            # Emit completion signal
            self.initialization_completed.emit(systems_data)
            
            logger.info("✅ System initialization completed successfully")
            
        except Exception as e:
            error_msg = f"System initialization failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.initialization_failed.emit(error_msg)
            self._show_error_dialog("Initialization Error", error_msg)
    
    def _store_system_references(self, systems_data: Dict[str, Any]):
        """Store system references from the system initializer."""
        try:
            systems = systems_data.get("systems", {})
            
            self.memory_manager = systems.get("memory_manager")
            self.mmorpg_engine = systems.get("mmorpg_engine")
            self.discord_manager = systems.get("discord_manager")
            self.scraping_manager = systems.get("scraping_manager")
            self.resume_tracker = systems.get("resume_tracker")
            self.enhanced_skill_system = systems.get("enhanced_skill_system")
            
            logger.info("✅ System references stored")
            
        except Exception as e:
            logger.error(f"❌ Storing system references failed: {str(e)}")
    
    def _on_systems_initialized(self, systems_data: Dict[str, Any]):
        """Handle systems initialization completion."""
        try:
            logger.info("🎉 Systems initialization completed")
            
            # Update status indicators
            self._update_status_indicators(systems_data)
            
            # Start background refresh timer
            self._start_background_refresh()
            
        except Exception as e:
            logger.error(f"❌ Handling systems initialization completion failed: {str(e)}")
    
    def _on_system_error(self, system_name: str, error_message: str):
        """Handle system initialization errors."""
        try:
            logger.error(f"❌ System error in {system_name}: {error_message}")
            
            # Update status indicator for failed system
            self.ui_builder.update_status_indicator(system_name, "Error", "#e74c3c")
            
        except Exception as e:
            logger.error(f"❌ Handling system error failed: {str(e)}")
    
    def _on_initialization_progress(self, progress: int, message: str):
        """Handle initialization progress updates."""
        try:
            logger.info(f"📊 Initialization progress: {progress}% - {message}")
            
            # Update status bar if available
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(f"Initializing... {progress}% - {message}")
            
        except Exception as e:
            logger.error(f"❌ Handling initialization progress failed: {str(e)}")
    
    def _update_status_indicators(self, systems_data: Dict[str, Any]):
        """Update status indicators based on system status."""
        try:
            status = systems_data.get("status", {})
            
            # Update each system indicator
            for system_name, is_available in status.items():
                if is_available:
                    self.ui_builder.update_status_indicator(system_name, "Ready", "#27ae60")
                else:
                    self.ui_builder.update_status_indicator(system_name, "Error", "#e74c3c")
            
            logger.info("✅ Status indicators updated")
            
        except Exception as e:
            logger.error(f"❌ Updating status indicators failed: {str(e)}")
    
    def _on_panel_switched(self, panel_name: str):
        """Handle panel switching events."""
        try:
            logger.info(f"🔄 Panel switched to: {panel_name}")
            
            # Update window title
            self.setWindowTitle(f"🌌 Dreamscape - {panel_name.replace('_', ' ').title()}")
            
            # Additional panel-specific logic can be added here
            
        except Exception as e:
            logger.error(f"❌ Handling panel switch failed: {str(e)}")
    
    def _on_sidebar_button_clicked(self, panel_name: str):
        """Handle sidebar button click events."""
        try:
            logger.info(f"🖱️ Sidebar button clicked: {panel_name}")
            
            # Additional sidebar-specific logic can be added here
            
        except Exception as e:
            logger.error(f"❌ Handling sidebar button click failed: {str(e)}")
    
    def _start_background_refresh(self):
        """Start background refresh timer."""
        try:
            # Create background refresh timer
            self.background_timer = QTimer()
            self.background_timer.timeout.connect(self._background_refresh)
            self.background_timer.start(30000)  # Refresh every 30 seconds
            
            logger.info("✅ Background refresh timer started")
            
        except Exception as e:
            logger.error(f"❌ Starting background refresh failed: {str(e)}")
    
    def _background_refresh(self):
        """Perform background refresh operations."""
        try:
            # Refresh current panel if it has a refresh method
            current_panel_name = self.ui_builder.get_current_panel()
            current_panel = self.ui_builder.get_panel(current_panel_name)
            
            if current_panel and hasattr(current_panel, 'refresh'):
                current_panel.refresh()
            
            # Update status indicators
            if self.system_initializer:
                status_data = self.system_initializer.get_system_status()
                self._update_status_indicators({"status": status_data.get("status", {})})
            
        except Exception as e:
            logger.error(f"❌ Background refresh failed: {str(e)}")
    
    def _apply_initial_styling(self):
        """Apply initial styling to the main window."""
        try:
            # Set window style
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ecf0f1;
                }
                QStatusBar {
                    background-color: #2c3e50;
                    color: white;
                    padding: 5px;
                }
            """)
            
            logger.info("✅ Initial styling applied")
            
        except Exception as e:
            logger.error(f"❌ Applying initial styling failed: {str(e)}")
    
    def _show_error_dialog(self, title: str, message: str):
        """Show an error dialog."""
        try:
            QMessageBox.critical(self, title, message)
        except Exception as e:
            logger.error(f"❌ Showing error dialog failed: {str(e)}")
    
    def show(self):
        """Show the main window."""
        try:
            super().show()
            self.center_window()
            logger.info("✅ Main window displayed")
        except Exception as e:
            logger.error(f"❌ Showing main window failed: {str(e)}")
    
    def center_window(self):
        """Center the window on the screen."""
        try:
            screen = self.screen()
            if screen:
                screen_geometry = screen.geometry()
                window_geometry = self.geometry()
                
                x = (screen_geometry.width() - window_geometry.width()) // 2
                y = (screen_geometry.height() - window_geometry.height()) // 2
                
                self.move(x, y)
                
        except Exception as e:
            logger.error(f"❌ Centering window failed: {str(e)}")
    
    def get_system(self, system_name: str) -> Optional[Any]:
        """Get a specific system by name."""
        if self.system_initializer:
            return self.system_initializer.get_system(system_name)
        return None
    
    def is_system_available(self, system_name: str) -> bool:
        """Check if a specific system is available."""
        if self.system_initializer:
            return self.system_initializer.is_system_available(system_name)
        return False
    
    def get_current_panel(self) -> str:
        """Get the name of the currently active panel."""
        return self.ui_builder.get_current_panel()
    
    def switch_to_panel(self, panel_name: str):
        """Programmatically switch to a specific panel."""
        self.ui_builder.switch_to_panel(panel_name)
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            logger.info("🔄 Main window closing...")
            
            # Cleanup systems
            if self.system_initializer:
                self.system_initializer.cleanup_systems()
            
            # Stop background timer
            if hasattr(self, 'background_timer'):
                self.background_timer.stop()
            
            logger.info("✅ Main window cleanup completed")
            event.accept()
            
        except Exception as e:
            logger.error(f"❌ Main window cleanup failed: {str(e)}")
            event.accept()


def main():
    """Main function for testing the refactored main window."""
    try:
        # Create application
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = TheaMainWindow()
        window.show()
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 