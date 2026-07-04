"""
Status Controller - GUI Status Management
========================================

This controller handles status bar updates, notifications, and progress
indicators, separated from the main window for better organization.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar, QWidget, QHBoxLayout

logger = logging.getLogger(__name__)


class StatusController(QObject):
    """Controls status bar updates and notifications."""
    
    # Signals for status events
    status_updated = pyqtSignal(str)  # message
    progress_updated = pyqtSignal(int)  # percentage
    system_info_updated = pyqtSignal(str)  # system_info
    
    def __init__(self, status_bar: QStatusBar, parent=None):
        """Initialize the status controller."""
        super().__init__(parent)
        self.status_bar = status_bar
        self.main_window = parent
        
        # Status components
        self.progress_bar = None
        self.system_info_label = None
        self.status_history = []
        
        # Setup status bar components
        self._setup_status_bar()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._update_system_info)
        self.refresh_timer.start(30000)  # Update every 30 seconds
    
    def _setup_status_bar(self):
        """Setup status bar with custom components."""
        try:
            # Create progress bar (initially hidden)
            self.progress_bar = QProgressBar()
            self.progress_bar.setMaximumWidth(200)
            self.progress_bar.setVisible(False)
            self.status_bar.addPermanentWidget(self.progress_bar)
            
            # Create system info label
            self.system_info_label = QLabel("System: Operational")
            self.system_info_label.setStyleSheet("color: #666666; padding: 0 10px;")
            self.status_bar.addPermanentWidget(self.system_info_label)
            
            # Set initial status
            self.show_status("Dreamscape ready", 5000)
            
        except Exception as e:
            logger.error(f"Failed to setup status bar: {e}")
    
    def show_status(self, message: str, timeout: int = 0):
        """Show status message in status bar."""
        try:
            self.status_bar.showMessage(message, timeout)
            
            # Add to history
            self.status_history.append({
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "timeout": timeout
            })
            
            # Keep only last 100 entries
            if len(self.status_history) > 100:
                self.status_history.pop(0)
            
            self.status_updated.emit(message)
            logger.debug(f"Status updated: {message}")
            
        except Exception as e:
            logger.error(f"Failed to show status: {e}")
    
    def show_progress(self, percentage: int, message: str = ""):
        """Show progress indicator."""
        try:
            if self.progress_bar:
                self.progress_bar.setValue(percentage)
                self.progress_bar.setVisible(True)
                
                if message:
                    self.show_status(message)
                
                self.progress_updated.emit(percentage)
                
        except Exception as e:
            logger.error(f"Failed to show progress: {e}")
    
    def hide_progress(self):
        """Hide progress indicator."""
        try:
            if self.progress_bar:
                self.progress_bar.setVisible(False)
                
        except Exception as e:
            logger.error(f"Failed to hide progress: {e}")
    
    def show_workflow_status(self, workflow_name: str, status: str):
        """Show workflow-specific status."""
        status_map = {
            "started": "🚀",
            "running": "🔄", 
            "completed": "✅",
            "failed": "❌",
            "cancelled": "⚠️"
        }
        
        icon = status_map.get(status, "ℹ️")
        message = f"{icon} {workflow_name}: {status}"
        
        timeout = 10000 if status in ["completed", "failed"] else 5000
        self.show_status(message, timeout)
    
    def show_conversation_stats(self, stats: Dict[str, Any]):
        """Show conversation statistics."""
        try:
            total_conversations = stats.get('total_conversations', 0)
            total_messages = stats.get('total_messages', 0)
            
            message = f"📚 {total_conversations:,} conversations • 💬 {total_messages:,} messages"
            self.show_status(message, 8000)
            
        except Exception as e:
            logger.error(f"Failed to show conversation stats: {e}")
    
    def show_mmorpg_stats(self, player_info: Dict[str, Any]):
        """Show MMORPG player statistics."""
        try:
            player_name = player_info.get("name", "Victor")
            level = player_info.get("level", 0)
            skills = len(player_info.get("skills", []))
            
            message = f"🎮 {player_name} - Level {level} • ⚔️ {skills} skills"
            self.show_status(message, 8000)
            
        except Exception as e:
            logger.error(f"Failed to show MMORPG stats: {e}")
    
    def show_error(self, error_message: str):
        """Show error status."""
        message = f"❌ Error: {error_message}"
        self.show_status(message, 15000)  # Longer timeout for errors
    
    def show_warning(self, warning_message: str):
        """Show warning status."""
        message = f"⚠️ Warning: {warning_message}"
        self.show_status(message, 10000)
    
    def show_success(self, success_message: str):
        """Show success status."""
        message = f"✅ {success_message}"
        self.show_status(message, 8000)
    
    def _update_system_info(self):
        """Update system information display."""
        try:
            if not self.system_info_label:
                return
            
            # Get basic system status
            if self.main_window:
                # Try to get memory manager stats
                try:
                    if hasattr(self.main_window, 'memory_manager') and self.main_window.memory_manager:
                        stats = self.main_window.memory_manager.get_conversation_stats()
                        conv_count = stats.get('total_conversations', 0)
                        self.system_info_label.setText(f"System: Active • {conv_count} conversations")
                    else:
                        self.system_info_label.setText("System: Initializing...")
                except Exception:
                    self.system_info_label.setText("System: Operational")
            else:
                self.system_info_label.setText("System: Operational")
            
            self.system_info_updated.emit(self.system_info_label.text())
            
        except Exception as e:
            logger.error(f"Failed to update system info: {e}")
    
    def update_system_health(self, health_status: str):
        """Update system health status."""
        health_colors = {
            "excellent": "#4CAF50",
            "good": "#8BC34A", 
            "fair": "#FFC107",
            "poor": "#FF9800",
            "critical": "#F44336"
        }
        
        color = health_colors.get(health_status.lower(), "#666666")
        
        if self.system_info_label:
            self.system_info_label.setText(f"System: {health_status.title()}")
            self.system_info_label.setStyleSheet(f"color: {color}; padding: 0 10px;")
    
    def get_status_history(self) -> list:
        """Get status message history."""
        return self.status_history.copy()
    
    def clear_status_history(self):
        """Clear status message history."""
        self.status_history.clear()
    
    def shutdown(self):
        """Shutdown status controller."""
        try:
            if self.refresh_timer:
                self.refresh_timer.stop()
            
            self.show_status("Shutting down...", 2000)
            
        except Exception as e:
            logger.error(f"Failed to shutdown status controller: {e}")


class StatusBarEnhanced(QWidget):
    """Enhanced status bar with additional components."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup enhanced status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # System status
        self.system_label = QLabel("System: Ready")
        self.system_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        layout.addWidget(self.system_label)
        
        # Spacer
        layout.addStretch()
        
        # Activity indicator
        self.activity_label = QLabel("💤 Idle")
        layout.addWidget(self.activity_label)
        
        # Performance indicator
        self.performance_label = QLabel("⚡ Normal")
        layout.addWidget(self.performance_label)
    
    def update_system_status(self, status: str, color: str = "#4CAF50"):
        """Update system status."""
        self.system_label.setText(f"System: {status}")
        self.system_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def update_activity(self, activity: str, icon: str = "💤"):
        """Update activity status."""
        self.activity_label.setText(f"{icon} {activity}")
    
    def update_performance(self, performance: str, icon: str = "⚡"):
        """Update performance indicator."""
        self.performance_label.setText(f"{icon} {performance}") 