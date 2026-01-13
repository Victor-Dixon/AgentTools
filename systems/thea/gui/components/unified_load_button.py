#!/usr/bin/env python3
"""
Unified Load Button Component
A drop-in replacement for individual load buttons that integrates with the Unified Data Loading System.
"""

import time
from typing import Optional, Dict, Any, Callable, List
from PyQt6.QtWidgets import QPushButton, QMenu, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction

class UnifiedLoadButton(QPushButton):
    """Unified Load Button that integrates with the Unified Data Loading System."""
    
    # Signals
    load_requested = pyqtSignal(str, dict)  # data_type, parameters
    load_completed = pyqtSignal(str, bool, str, Any)  # data_type, success, message, result
    load_progress = pyqtSignal(str, int, str)  # data_type, progress, message
    
    def __init__(self, 
                 data_type: str,
                 text: str = None,
                 priority: str = "NORMAL",
                 use_cache: bool = True,
                 background_load: bool = True,
                 parent=None):
        """
        Initialize the Unified Load Button.
        
        Args:
            data_type: Type of data to load (conversations, templates, analytics, etc.)
            text: Button text (defaults to "Load {data_type}")
            priority: Load priority (LOW, NORMAL, HIGH, CRITICAL)
            use_cache: Whether to use cached data if available
            background_load: Whether to load in background
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.data_type = data_type
        self.priority = priority
        self.use_cache = use_cache
        self.background_load = background_load
        self.loading = False
        self.last_load_time = None
        self.cache_duration = 300  # 5 minutes
        
        # Set button text
        if text is None:
            text = f"🔄 Load {data_type.title()}"
        self.setText(text)
        
        # Setup button appearance
        self.setup_appearance()
        
        # Connect signals
        self.clicked.connect(self.on_clicked)
        
        # Setup context menu
        self.setup_context_menu()
        
        # Setup status timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def setup_appearance(self):
        """Setup button appearance."""
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        
        # Set tooltip
        self.setToolTip(f"Load {self.data_type} data (Priority: {self.priority})")
    
    def setup_context_menu(self):
        """Setup context menu for additional options."""
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """Show context menu with additional options."""
        menu = QMenu(self)
        
        # Priority actions
        priority_menu = menu.addMenu("Priority")
        priorities = ["LOW", "NORMAL", "HIGH", "CRITICAL"]
        
        for priority in priorities:
            action = QAction(priority, self)
            action.setCheckable(True)
            action.setChecked(priority == self.priority)
            action.triggered.connect(lambda checked, p=priority: self.set_priority(p))
            priority_menu.addAction(action)
        
        menu.addSeparator()
        
        # Cache options
        cache_action = QAction("Use Cache", self)
        cache_action.setCheckable(True)
        cache_action.setChecked(self.use_cache)
        cache_action.triggered.connect(lambda checked: setattr(self, 'use_cache', checked))
        menu.addAction(cache_action)
        
        # Background load options
        bg_action = QAction("Background Load", self)
        bg_action.setCheckable(True)
        bg_action.setChecked(self.background_load)
        bg_action.triggered.connect(lambda checked: setattr(self, 'background_load', checked))
        menu.addAction(bg_action)
        
        menu.addSeparator()
        
        # Force reload action
        force_reload_action = QAction("Force Reload", self)
        force_reload_action.triggered.connect(self.force_reload)
        menu.addAction(force_reload_action)
        
        # Show cache status
        cache_status_action = QAction("Cache Status", self)
        cache_status_action.triggered.connect(self.show_cache_status)
        menu.addAction(cache_status_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def set_priority(self, priority: str):
        """Set load priority."""
        self.priority = priority
        self.setToolTip(f"Load {self.data_type} data (Priority: {self.priority})")
    
    def force_reload(self):
        """Force reload data ignoring cache."""
        self.use_cache = False
        self.on_clicked()
        self.use_cache = True  # Reset to default
    
    def show_cache_status(self):
        """Show cache status information."""
        if self.last_load_time:
            time_since_load = time.time() - self.last_load_time
            cache_age = f"{time_since_load:.1f} seconds ago"
            cache_valid = time_since_load < self.cache_duration
            status = "Valid" if cache_valid else "Expired"
        else:
            cache_age = "Never"
            status = "None"
        
        QMessageBox.information(
            self, 
            "Cache Status", 
            f"Data Type: {self.data_type}\n"
            f"Last Load: {cache_age}\n"
            f"Cache Status: {status}\n"
            f"Cache Duration: {self.cache_duration} seconds"
        )
    
    def on_clicked(self):
        """Handle button click."""
        if self.loading:
            QMessageBox.information(self, "Loading", f"Already loading {self.data_type} data...")
            return
        
        # Prepare load parameters
        parameters = {
            "data_type": self.data_type,
            "priority": self.priority,
            "use_cache": self.use_cache,
            "background_load": self.background_load,
            "cache_duration": self.cache_duration,
            "timestamp": time.time()
        }
        
        # Emit load request
        self.load_requested.emit(self.data_type, parameters)
        
        # Update button state
        self.set_loading_state(True)
    
    def set_loading_state(self, loading: bool):
        """Set the loading state of the button."""
        self.loading = loading
        
        if loading:
            self.setText(f"⏳ Loading {self.data_type.title()}...")
            self.setEnabled(False)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.setText(f"🔄 Load {self.data_type.title()}")
            self.setEnabled(True)
            self.setup_appearance()
    
    def update_status(self):
        """Update button status based on cache and timing."""
        if self.last_load_time:
            time_since_load = time.time() - self.last_load_time
            if time_since_load < self.cache_duration:
                # Cache is still valid
                remaining = self.cache_duration - time_since_load
                if remaining < 60:
                    self.setToolTip(f"Cache valid for {remaining:.0f}s")
                else:
                    self.setToolTip(f"Cache valid for {remaining/60:.1f}m")
            else:
                # Cache expired
                self.setToolTip(f"Cache expired ({time_since_load/60:.1f}m ago)")
    
    def on_load_completed(self, data_type: str, success: bool, message: str, result: Any):
        """Handle load completion."""
        if data_type == self.data_type:
            self.set_loading_state(False)
            self.last_load_time = time.time()
            
            if success:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                
                # Reset to normal appearance after 2 seconds
                QTimer.singleShot(2000, self.setup_appearance)
            else:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #F44336;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                """)
                
                # Reset to normal appearance after 3 seconds
                QTimer.singleShot(3000, self.setup_appearance)
            
            # Emit completion signal
            self.load_completed.emit(data_type, success, message, result)
    
    def on_load_progress(self, data_type: str, progress: int, message: str):
        """Handle load progress updates."""
        if data_type == self.data_type:
            self.setText(f"⏳ {progress}% - {message}")
            self.load_progress.emit(data_type, progress, message)
    
    def get_load_parameters(self) -> Dict[str, Any]:
        """Get current load parameters."""
        return {
            "data_type": self.data_type,
            "priority": self.priority,
            "use_cache": self.use_cache,
            "background_load": self.background_load,
            "cache_duration": self.cache_duration,
            "last_load_time": self.last_load_time
        }
    
    def set_load_parameters(self, parameters: Dict[str, Any]):
        """Set load parameters."""
        if "data_type" in parameters:
            self.data_type = parameters["data_type"]
        if "priority" in parameters:
            self.priority = parameters["priority"]
        if "use_cache" in parameters:
            self.use_cache = parameters["use_cache"]
        if "background_load" in parameters:
            self.background_load = parameters["background_load"]
        if "cache_duration" in parameters:
            self.cache_duration = parameters["cache_duration"]
        
        # Update button text and tooltip
        self.setText(f"🔄 Load {self.data_type.title()}")
        self.setToolTip(f"Load {self.data_type} data (Priority: {self.priority})")

class UnifiedLoadButtonManager:
    """Manager for Unified Load Buttons across the application."""
    
    def __init__(self, data_loader=None):
        """
        Initialize the Unified Load Button Manager.
        
        Args:
            data_loader: Reference to the UnifiedDataLoader instance
        """
        self.data_loader = data_loader
        self.buttons = {}
        self.load_callbacks = {}
        
    def create_button(self, 
                     data_type: str,
                     text: str = None,
                     priority: str = "NORMAL",
                     use_cache: bool = True,
                     background_load: bool = True,
                     parent=None) -> UnifiedLoadButton:
        """
        Create a new Unified Load Button.
        
        Args:
            data_type: Type of data to load
            text: Button text
            priority: Load priority
            use_cache: Whether to use cache
            background_load: Whether to load in background
            parent: Parent widget
            
        Returns:
            UnifiedLoadButton instance
        """
        button = UnifiedLoadButton(
            data_type=data_type,
            text=text,
            priority=priority,
            use_cache=use_cache,
            background_load=background_load,
            parent=parent
        )
        
        # Connect to data loader if available
        if self.data_loader:
            button.load_requested.connect(self.on_load_requested)
            self.data_loader.operation_completed.connect(button.on_load_completed)
            self.data_loader.progress_updated.connect(button.on_load_progress)
        
        # Store button reference
        button_id = f"{data_type}_{id(button)}"
        self.buttons[button_id] = button
        
        return button
    
    def on_load_requested(self, data_type: str, parameters: Dict[str, Any]):
        """Handle load request from buttons."""
        if self.data_loader:
            # Create load operation
            from gui.unified_data_loader import LoadOperation, LoadPriority
            
            operation = LoadOperation(
                id=f"button_load_{data_type}_{int(time.time())}",
                name=f"Button Load {data_type.title()}",
                description=f"Load {data_type} requested by button",
                priority=LoadPriority[parameters.get("priority", "NORMAL")],
                data_type=data_type,
                source="unified_button",
                target_panel="button_request",
                parameters=parameters
            )
            
            # Start operation
            self.data_loader.start_operation(operation)
    
    def set_data_loader(self, data_loader):
        """Set the data loader reference."""
        self.data_loader = data_loader
        
        # Connect existing buttons (only if they still exist)
        buttons_to_remove = []
        for button_id, button in self.buttons.items():
            try:
                # Check if button still exists
                if button and not button.isHidden():
                    button.load_requested.connect(self.on_load_requested)
                    self.data_loader.operation_completed.connect(button.on_load_completed)
                    self.data_loader.progress_updated.connect(button.on_load_progress)
                else:
                    buttons_to_remove.append(button_id)
            except RuntimeError:
                # Button has been deleted
                buttons_to_remove.append(button_id)
        
        # Remove deleted buttons
        for button_id in buttons_to_remove:
            self.buttons.pop(button_id, None)
    
    def get_button(self, button_id: str) -> Optional[UnifiedLoadButton]:
        """Get button by ID."""
        return self.buttons.get(button_id)
    
    def get_buttons_by_type(self, data_type: str) -> List[UnifiedLoadButton]:
        """Get all buttons for a specific data type."""
        return [btn for btn in self.buttons.values() if btn.data_type == data_type]
    
    def update_all_buttons(self, data_type: str, parameters: Dict[str, Any]):
        """Update all buttons for a specific data type."""
        for button in self.get_buttons_by_type(data_type):
            button.set_load_parameters(parameters)
    
    def clear_buttons(self):
        """Clear all button references."""
        self.buttons.clear()

# Global manager instance
_global_button_manager = UnifiedLoadButtonManager()

def get_unified_load_button_manager() -> UnifiedLoadButtonManager:
    """Get the global Unified Load Button Manager."""
    return _global_button_manager

def create_unified_load_button(data_type: str, **kwargs) -> UnifiedLoadButton:
    """Create a Unified Load Button using the global manager."""
    return _global_button_manager.create_button(data_type, **kwargs) 