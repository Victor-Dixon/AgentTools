"""
Thea GUI Debug Handler
Agent-4 Strategic Implementation for Deployment Coordination

Provides debug functionality for Thea MMORPG GUI components.
"""

import logging
from typing import Any, Dict, List
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QPushButton

logger = logging.getLogger(__name__)

class GUIDebugHandler(QObject):
    """Handles debug operations for GUI components."""

    # Signals for debug events
    button_clicked = pyqtSignal(str, dict)  # button_name, metadata
    operation_started = pyqtSignal(str, dict)  # operation_name, metadata
    operation_completed = pyqtSignal(str, dict)  # operation_name, metadata
    error_occurred = pyqtSignal(str, dict)  # error_message, metadata

    def __init__(self):
        super().__init__()
        self.debug_operations: List[Dict[str, Any]] = []
        self.error_count = 0
        self.operation_count = 0

    def log_button_click(self, button_name: str, metadata: Dict[str, Any] = None):
        """Log button click event."""
        metadata = metadata or {}
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'event_type': 'button_click',
            'button_name': button_name
        })

        self.debug_operations.append(metadata)
        self.button_clicked.emit(button_name, metadata)
        logger.debug(f"Button clicked: {button_name}")

    def log_operation_start(self, operation_name: str, metadata: Dict[str, Any] = None):
        """Log operation start event."""
        metadata = metadata or {}
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'event_type': 'operation_start',
            'operation_name': operation_name
        })

        self.debug_operations.append(metadata)
        self.operation_count += 1
        self.operation_started.emit(operation_name, metadata)
        logger.debug(f"Operation started: {operation_name}")

    def log_operation_complete(self, operation_name: str, metadata: Dict[str, Any] = None):
        """Log operation completion event."""
        metadata = metadata or {}
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'event_type': 'operation_complete',
            'operation_name': operation_name
        })

        self.debug_operations.append(metadata)
        self.operation_completed.emit(operation_name, metadata)
        logger.debug(f"Operation completed: {operation_name}")

    def log_error(self, error_message: str, metadata: Dict[str, Any] = None):
        """Log error event."""
        metadata = metadata or {}
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'event_type': 'error',
            'error_message': error_message
        })

        self.debug_operations.append(metadata)
        self.error_count += 1
        self.error_occurred.emit(error_message, metadata)
        logger.error(f"Debug error: {error_message}")

    def get_debug_statistics(self) -> Dict[str, Any]:
        """Get debug statistics."""
        return {
            'total_operations': len(self.debug_operations),
            'error_count': self.error_count,
            'operation_count': self.operation_count,
            'button_clicks': len([op for op in self.debug_operations if op.get('event_type') == 'button_click']),
            'last_operation': self.debug_operations[-1] if self.debug_operations else None
        }

    def clear_debug_history(self):
        """Clear debug operation history."""
        self.debug_operations.clear()
        self.error_count = 0
        self.operation_count = 0
        logger.info("Debug history cleared")

def debug_button(button: QPushButton, button_name: str = None, debug_handler: GUIDebugHandler = None) -> QPushButton:
    """
    Add debug functionality to a button.

    Args:
        button: The QPushButton to enhance
        button_name: Optional name for the button (defaults to object name)
        debug_handler: Optional debug handler instance

    Returns:
        The enhanced button
    """
    if debug_handler is None:
        debug_handler = GUIDebugHandler()

    button_name = button_name or button.objectName() or "unnamed_button"

    # Connect debug logging to button click
    def on_click():
        debug_handler.log_button_click(button_name, {
            'button_text': button.text(),
            'button_enabled': button.isEnabled(),
            'button_visible': button.isVisible()
        })

    button.clicked.connect(on_click)
    return button