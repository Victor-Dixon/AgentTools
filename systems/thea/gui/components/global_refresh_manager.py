#!/usr/bin/env python3
"""
Global Refresh Manager
Consolidates all refresh/update functionality across the GUI into a single, intelligent system.
Reduces 91 refresh buttons to a unified interface with smart updates and background refresh.
"""

import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import queue

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QProgressBar, QTextEdit, QGroupBox, QCheckBox, QSpinBox,
    QComboBox, QListWidget, QListWidgetItem, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QFont, QIcon, QAction

from gui.components.refresh_types import RefreshType, RefreshPriority
from gui.components.refresh_integration_manager import UnifiedRefreshButton


@dataclass
class RefreshRequest:
    """Represents a refresh request"""
    refresh_type: RefreshType
    priority: RefreshPriority
    callback: Optional[Callable] = None
    timestamp: datetime = None
    status: str = "pending"
    duration: float = 0.0
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class RefreshWorker(QThread):
    """Background worker for refresh operations"""
    refresh_started = pyqtSignal(str)
    refresh_progress = pyqtSignal(int)
    refresh_completed = pyqtSignal(str, bool, str)
    
    def __init__(self, refresh_request: RefreshRequest):
        super().__init__()
        self.refresh_request = refresh_request
        self._stop_requested = False
    
    def run(self):
        """Execute the refresh operation"""
        try:
            self.refresh_started.emit(f"Starting {self.refresh_request.refresh_type.value} refresh...")
            self.refresh_progress.emit(10)
            
            start_time = time.time()
            
            # Simulate refresh operation based on type
            if self.refresh_request.refresh_type == RefreshType.CONVERSATIONS:
                success = self._refresh_conversations()
            elif self.refresh_request.refresh_type == RefreshType.ANALYTICS:
                success = self._refresh_analytics()
            elif self.refresh_request.refresh_type == RefreshType.TEMPLATES:
                success = self._refresh_templates()
            elif self.refresh_request.refresh_type == RefreshType.MEMORY:
                success = self._refresh_memory()
            elif self.refresh_request.refresh_type == RefreshType.MMORPG:
                success = self._refresh_mmorpg()
            elif self.refresh_request.refresh_type == RefreshType.SETTINGS:
                success = self._refresh_settings()
            elif self.refresh_request.refresh_type == RefreshType.UI:
                success = self._refresh_ui()
            elif self.refresh_request.refresh_type == RefreshType.ALL:
                success = self._refresh_all()
            else:
                raise ValueError(f"Unknown refresh type: {self.refresh_request.refresh_type}")
            
            duration = time.time() - start_time
            self.refresh_request.duration = duration
            
            if success:
                self.refresh_progress.emit(100)
                self.refresh_completed.emit(
                    self.refresh_request.refresh_type.value,
                    True,
                    f"Completed in {duration:.2f}s"
                )
            else:
                self.refresh_completed.emit(
                    self.refresh_request.refresh_type.value,
                    False,
                    "Refresh failed"
                )
                
        except Exception as e:
            self.refresh_request.error = str(e)
            self.refresh_completed.emit(
                self.refresh_request.refresh_type.value,
                False,
                f"Error: {str(e)}"
            )
    
    def _refresh_conversations(self) -> bool:
        """Refresh conversation data"""
        self.refresh_progress.emit(30)
        time.sleep(0.5)  # Simulate work
        self.refresh_progress.emit(60)
        time.sleep(0.3)  # Simulate work
        return True
    
    def _refresh_analytics(self) -> bool:
        """Refresh analytics data"""
        self.refresh_progress.emit(25)
        time.sleep(0.8)  # Simulate work
        self.refresh_progress.emit(70)
        time.sleep(0.4)  # Simulate work
        return True
    
    def _refresh_templates(self) -> bool:
        """Refresh template data"""
        self.refresh_progress.emit(40)
        time.sleep(0.3)  # Simulate work
        self.refresh_progress.emit(80)
        time.sleep(0.2)  # Simulate work
        return True
    
    def _refresh_memory(self) -> bool:
        """Refresh memory data"""
        self.refresh_progress.emit(20)
        time.sleep(1.0)  # Simulate work
        self.refresh_progress.emit(60)
        time.sleep(0.5)  # Simulate work
        return True
    
    def _refresh_mmorpg(self) -> bool:
        """Refresh MMORPG data"""
        self.refresh_progress.emit(35)
        time.sleep(0.6)  # Simulate work
        self.refresh_progress.emit(75)
        time.sleep(0.3)  # Simulate work
        return True
    
    def _refresh_settings(self) -> bool:
        """Refresh settings data"""
        self.refresh_progress.emit(50)
        time.sleep(0.2)  # Simulate work
        self.refresh_progress.emit(90)
        time.sleep(0.1)  # Simulate work
        return True
    
    def _refresh_ui(self) -> bool:
        """Refresh UI components"""
        self.refresh_progress.emit(60)
        time.sleep(0.4)  # Simulate work
        self.refresh_progress.emit(85)
        time.sleep(0.2)  # Simulate work
        return True
    
    def _refresh_all(self) -> bool:
        """Refresh all data types"""
        refresh_types = [
            RefreshType.CONVERSATIONS,
            RefreshType.ANALYTICS,
            RefreshType.TEMPLATES,
            RefreshType.MEMORY,
            RefreshType.MMORPG,
            RefreshType.SETTINGS,
            RefreshType.UI
        ]
        
        total_progress = 0
        for i, refresh_type in enumerate(refresh_types):
            if self._stop_requested:
                return False
            
            # Update progress for this refresh type
            progress_per_type = 100 // len(refresh_types)
            current_progress = i * progress_per_type
            self.refresh_progress.emit(current_progress)
            
            # Simulate refresh for this type
            time.sleep(0.3)
            
            total_progress = (i + 1) * progress_per_type
            self.refresh_progress.emit(total_progress)
        
        return True


class GlobalRefreshManager(QWidget):
    """
    Global Refresh Manager - Consolidates all refresh functionality
    
    Replaces 91 individual refresh buttons with a single, intelligent interface
    that provides smart updates, background refresh, and status tracking.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.refresh_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.active_workers: List[RefreshWorker] = []
        self.refresh_history: List[RefreshRequest] = []
        self.auto_refresh_timer: Optional[QTimer] = None
        self.max_concurrent_refreshes = 3
        
        self._setup_ui()
        self._setup_auto_refresh()
    
    def _setup_ui(self):
        """Setup the refresh manager UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🔄 Global Refresh Manager")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self._create_quick_refresh_tab()
        self._create_advanced_refresh_tab()
        self._create_auto_refresh_tab()
        self._create_history_tab()
        
        # Status section
        self._create_status_section(layout)
        
        self.setLayout(layout)
        self.setWindowTitle("Global Refresh Manager")
        self.resize(700, 600)
    
    def _create_quick_refresh_tab(self):
        """Create the quick refresh tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Quick refresh buttons
        quick_group = QGroupBox("⚡ Quick Refresh")
        quick_layout = QVBoxLayout()
        
        # Create quick refresh buttons for each type
        refresh_types = [
            ("💬 Conversations", RefreshType.CONVERSATIONS),
            ("📊 Analytics", RefreshType.ANALYTICS),
            ("📝 Templates", RefreshType.TEMPLATES),
            ("🧠 Memory", RefreshType.MEMORY),
            ("🎮 MMORPG", RefreshType.MMORPG),
            ("⚙️ Settings", RefreshType.SETTINGS),
            ("🖥️ UI", RefreshType.UI)
        ]
        
        for label, refresh_type in refresh_types:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, rt=refresh_type: self._quick_refresh(rt))
            quick_layout.addWidget(btn)
        
        # Refresh all button
        refresh_all_btn = QPushButton("🔄 Refresh All")
        refresh_all_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        refresh_all_btn.clicked.connect(lambda: self._quick_refresh(RefreshType.ALL))
        quick_layout.addWidget(refresh_all_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Quick Refresh")
    
    def _create_advanced_refresh_tab(self):
        """Create the advanced refresh tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Refresh type selection
        type_group = QGroupBox("🎯 Refresh Type")
        type_layout = QVBoxLayout()
        
        self.refresh_type_combo = QComboBox()
        for refresh_type in RefreshType:
            self.refresh_type_combo.addItem(refresh_type.value.title(), refresh_type)
        type_layout.addWidget(self.refresh_type_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Priority selection
        priority_group = QGroupBox("🚨 Priority")
        priority_layout = QVBoxLayout()
        
        self.priority_combo = QComboBox()
        for priority in RefreshPriority:
            self.priority_combo.addItem(priority.name.title(), priority)
        self.priority_combo.setCurrentText("Normal")
        priority_layout.addWidget(self.priority_combo)
        priority_group.setLayout(priority_layout)
        layout.addWidget(priority_group)
        
        # Advanced options
        options_group = QGroupBox("⚙️ Options")
        options_layout = QVBoxLayout()
        
        self.force_refresh_cb = QCheckBox("Force refresh (ignore cache)")
        options_layout.addWidget(self.force_refresh_cb)
        
        self.background_refresh_cb = QCheckBox("Background refresh (non-blocking)")
        self.background_refresh_cb.setChecked(True)
        options_layout.addWidget(self.background_refresh_cb)
        
        self.notify_completion_cb = QCheckBox("Notify on completion")
        self.notify_completion_cb.setChecked(True)
        options_layout.addWidget(self.notify_completion_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Advanced refresh button
        self.advanced_refresh_btn = QPushButton("🔧 Advanced Refresh")
        self.advanced_refresh_btn.clicked.connect(self._advanced_refresh)
        layout.addWidget(self.advanced_refresh_btn)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Advanced Refresh")
    
    def _create_auto_refresh_tab(self):
        """Create the auto refresh tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Auto refresh settings
        auto_group = QGroupBox("⏰ Auto Refresh Settings")
        auto_layout = QVBoxLayout()
        
        # Enable auto refresh
        self.auto_refresh_cb = QCheckBox("Enable auto refresh")
        self.auto_refresh_cb.toggled.connect(self._toggle_auto_refresh)
        auto_layout.addWidget(self.auto_refresh_cb)
        
        # Refresh interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Refresh interval:"))
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(300)  # 5 minutes default
        self.interval_spin.setSuffix(" seconds")
        interval_layout.addWidget(self.interval_spin)
        
        auto_layout.addLayout(interval_layout)
        
        # Auto refresh types
        self.auto_refresh_types = {}
        for refresh_type in RefreshType:
            if refresh_type != RefreshType.ALL:  # Don't auto-refresh "all"
                cb = QCheckBox(f"Auto refresh {refresh_type.value}")
                cb.setChecked(refresh_type in [RefreshType.CONVERSATIONS, RefreshType.ANALYTICS])
                self.auto_refresh_types[refresh_type] = cb
                auto_layout.addWidget(cb)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Auto refresh status
        status_group = QGroupBox("📊 Auto Refresh Status")
        status_layout = QVBoxLayout()
        
        self.auto_refresh_status = QLabel("Auto refresh disabled")
        status_layout.addWidget(self.auto_refresh_status)
        
        self.next_auto_refresh = QLabel("Next refresh: N/A")
        status_layout.addWidget(self.next_auto_refresh)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Auto Refresh")
    
    def _create_history_tab(self):
        """Create the refresh history tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # History list
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        # Clear history button
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Refresh History")
        
        self._update_history_display()
    
    def _create_status_section(self, parent_layout):
        """Create the status section"""
        status_group = QGroupBox("📈 Refresh Status")
        status_layout = QVBoxLayout()
        
        # Active refreshes
        self.active_refreshes_label = QLabel("Active refreshes: 0")
        status_layout.addWidget(self.active_refreshes_label)
        
        # Queue status
        self.queue_status_label = QLabel("Queue: 0 pending")
        status_layout.addWidget(self.queue_status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QLabel("Ready")
        status_layout.addWidget(self.status_text)
        
        status_group.setLayout(status_layout)
        parent_layout.addWidget(status_group)
    
    def _quick_refresh(self, refresh_type: RefreshType):
        """Handle quick refresh"""
        request = RefreshRequest(
            refresh_type=refresh_type,
            priority=RefreshPriority.NORMAL
        )
        
        self._queue_refresh(request)
    
    def _advanced_refresh(self):
        """Handle advanced refresh"""
        refresh_type = self.refresh_type_combo.currentData()
        priority = self.priority_combo.currentData()
        
        request = RefreshRequest(
            refresh_type=refresh_type,
            priority=priority
        )
        
        self._queue_refresh(request)
    
    def _queue_refresh(self, request: RefreshRequest):
        """Add refresh request to queue"""
        # Add to history
        self.refresh_history.append(request)
        self._update_history_display()
        
        # Add to queue with priority
        priority_value = (request.priority.value, request.timestamp.timestamp())
        self.refresh_queue.put((priority_value, request))
        
        # Update status
        self._update_status()
        
        # Process queue if not at max capacity
        if len(self.active_workers) < self.max_concurrent_refreshes:
            self._process_queue()
    
    def _process_queue(self):
        """Process the refresh queue"""
        while not self.refresh_queue.empty() and len(self.active_workers) < self.max_concurrent_refreshes:
            try:
                priority, request = self.refresh_queue.get_nowait()
                self._start_refresh_worker(request)
            except queue.Empty:
                break
    
    def _start_refresh_worker(self, request: RefreshRequest):
        """Start a refresh worker"""
        worker = RefreshWorker(request)
        worker.refresh_started.connect(self._on_refresh_started)
        worker.refresh_progress.connect(self._on_refresh_progress)
        worker.refresh_completed.connect(self._on_refresh_completed)
        
        self.active_workers.append(worker)
        worker.start()
        
        self._update_status()
    
    def _on_refresh_started(self, message: str):
        """Handle refresh started"""
        self.status_text.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
    
    def _on_refresh_progress(self, progress: int):
        """Handle refresh progress"""
        self.progress_bar.setValue(progress)
    
    def _on_refresh_completed(self, refresh_type: str, success: bool, message: str):
        """Handle refresh completion"""
        # Find and update the request
        for request in self.refresh_history:
            if request.refresh_type.value == refresh_type and request.status == "pending":
                request.status = "completed" if success else "failed"
                request.error = None if success else message
                break
        
        # Remove completed worker
        for worker in self.active_workers[:]:
            if worker.refresh_request.refresh_type.value == refresh_type:
                worker.quit()
                worker.wait()
                self.active_workers.remove(worker)
                break
        
        # Update UI
        self._update_status()
        self._update_history_display()
        
        # Hide progress bar if no active workers
        if not self.active_workers:
            self.progress_bar.setVisible(False)
            self.status_text.setText("Ready")
        
        # Process next item in queue
        self._process_queue()
        
        # Show notification if enabled
        if success:
            self.status_text.setText(f"✅ {refresh_type.title()} refreshed successfully")
        else:
            self.status_text.setText(f"❌ {refresh_type.title()} refresh failed: {message}")
    
    def _toggle_auto_refresh(self, enabled: bool):
        """Toggle auto refresh"""
        if enabled:
            self._setup_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _setup_auto_refresh(self):
        """Setup auto refresh timer"""
        if self.auto_refresh_timer is None:
            self.auto_refresh_timer = QTimer()
            self.auto_refresh_timer.timeout.connect(self._auto_refresh)
        
        interval = self.interval_spin.value() * 1000  # Convert to milliseconds
        self.auto_refresh_timer.start(interval)
        
        self.auto_refresh_status.setText("Auto refresh enabled")
        self._update_next_auto_refresh()
    
    def _stop_auto_refresh(self):
        """Stop auto refresh"""
        if self.auto_refresh_timer:
            self.auto_refresh_timer.stop()
        
        self.auto_refresh_status.setText("Auto refresh disabled")
        self.next_auto_refresh.setText("Next refresh: N/A")
    
    def _auto_refresh(self):
        """Perform auto refresh"""
        enabled_types = [
            refresh_type for refresh_type, checkbox in self.auto_refresh_types.items()
            if checkbox.isChecked()
        ]
        
        for refresh_type in enabled_types:
            request = RefreshRequest(
                refresh_type=refresh_type,
                priority=RefreshPriority.LOW
            )
            self._queue_refresh(request)
        
        self._update_next_auto_refresh()
    
    def _update_next_auto_refresh(self):
        """Update next auto refresh time"""
        if self.auto_refresh_timer and self.auto_refresh_timer.isActive():
            interval_seconds = self.interval_spin.value()
            next_time = datetime.now() + timedelta(seconds=interval_seconds)
            self.next_auto_refresh.setText(f"Next refresh: {next_time.strftime('%H:%M:%S')}")
    
    def _update_status(self):
        """Update status display"""
        self.active_refreshes_label.setText(f"Active refreshes: {len(self.active_workers)}")
        
        queue_size = self.refresh_queue.qsize()
        self.queue_status_label.setText(f"Queue: {queue_size} pending")
    
    def _update_history_display(self):
        """Update the history display"""
        self.history_list.clear()
        
        if not self.refresh_history:
            self.history_list.addItem("No refresh history available")
            return
        
        # Show last 50 refresh operations
        for request in reversed(self.refresh_history[-50:]):
            status_icon = "✅" if request.status == "completed" else "❌" if request.status == "failed" else "⏳"
            duration_text = f" ({request.duration:.2f}s)" if request.duration > 0 else ""
            error_text = f" - {request.error}" if request.error else ""
            
            item_text = f"{status_icon} {request.refresh_type.value.title()}{duration_text}{error_text}"
            item = QListWidgetItem(item_text)
            
            # Color code based on status
            if request.status == "completed":
                item.setBackground(Qt.GlobalColor.lightGray)
            elif request.status == "failed":
                item.setBackground(Qt.GlobalColor.red)
            
            self.history_list.addItem(item)
    
    def _clear_history(self):
        """Clear refresh history"""
        self.refresh_history.clear()
        self._update_history_display()
    
    def get_refresh_status(self, refresh_type: RefreshType) -> Dict[str, Any]:
        """Get status for a specific refresh type"""
        # Find the most recent refresh for this type
        for request in reversed(self.refresh_history):
            if request.refresh_type == refresh_type:
                return {
                    "status": request.status,
                    "timestamp": request.timestamp,
                    "duration": request.duration,
                    "error": request.error
                }
        
        return {"status": "never", "timestamp": None, "duration": 0, "error": None}


def main():
    """Test the Global Refresh Manager"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    refresh_manager = GlobalRefreshManager()
    refresh_manager.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 