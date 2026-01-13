#!/usr/bin/env python3
"""
Unified Data Loading System
Consolidates all data loading operations across the GUI into a single, intelligent system.
"""

import os
import sys
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QProgressBar,
    QPushButton, QComboBox, QSpinBox, QCheckBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QTextEdit, QMessageBox,
    QDialog, QDialogButtonBox, QFrame, QSplitter, QTabWidget,
    QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QPixmap

logger = logging.getLogger(__name__)

class LoadPriority(Enum):
    """Priority levels for data loading operations."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class LoadStatus(Enum):
    """Status of data loading operations."""
    PENDING = "pending"
    LOADING = "loading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class LoadOperation:
    """Represents a data loading operation."""
    id: str
    name: str
    description: str
    priority: LoadPriority
    data_type: str
    source: str
    target_panel: str
    callback: Optional[Callable] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: LoadStatus = LoadStatus.PENDING
    progress: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Any] = None
    cache_key: Optional[str] = None
    cache_duration: int = 300  # 5 minutes default

class DataLoaderWorker(QThread):
    """Background worker for data loading operations."""
    
    progress_updated = pyqtSignal(str, int, str)  # operation_id, progress, message
    operation_completed = pyqtSignal(str, bool, str, Any)  # operation_id, success, message, result
    operation_started = pyqtSignal(str)  # operation_id
    
    def __init__(self, operation: LoadOperation):
        super().__init__()
        self.operation = operation
        self._cancelled = False
        
    def run(self):
        """Execute the loading operation."""
        try:
            self.operation_started.emit(self.operation.id)
            self.operation.status = LoadStatus.LOADING
            self.operation.start_time = datetime.now()
            
            # Simulate progress updates
            self.progress_updated.emit(self.operation.id, 10, "Initializing...")
            time.sleep(0.1)
            
            self.progress_updated.emit(self.operation.id, 30, "Loading data...")
            time.sleep(0.2)
            
            # Execute the actual loading operation
            if self.operation.callback:
                result = self.operation.callback(**self.operation.parameters)
                self.operation.result = result
            else:
                # Default loading logic based on data type
                result = self._default_load_operation()
                self.operation.result = result
            
            self.progress_updated.emit(self.operation.id, 90, "Finalizing...")
            time.sleep(0.1)
            
            self.progress_updated.emit(self.operation.id, 100, "Completed")
            self.operation.status = LoadStatus.COMPLETED
            self.operation.end_time = datetime.now()
            
            self.operation_completed.emit(
                self.operation.id, 
                True, 
                f"Successfully loaded {self.operation.data_type}", 
                result
            )
            
        except Exception as e:
            logger.error(f"Load operation failed: {e}")
            self.operation.status = LoadStatus.FAILED
            self.operation.error_message = str(e)
            self.operation.end_time = datetime.now()
            
            self.operation_completed.emit(
                self.operation.id, 
                False, 
                f"Failed to load {self.operation.data_type}: {e}", 
                None
            )
    
    def _default_load_operation(self):
        """Default loading logic based on data type."""
        data_type = self.operation.data_type.lower()
        
        if "conversation" in data_type:
            return self._load_conversations()
        elif "template" in data_type:
            return self._load_templates()
        elif "analytics" in data_type:
            return self._load_analytics()
        elif "skill" in data_type:
            return self._load_skills()
        elif "project" in data_type:
            return self._load_projects()
        elif "agent" in data_type:
            return self._load_agents()
        else:
            return {"message": f"Default load for {data_type}", "data": []}
    
    def _load_conversations(self):
        """Load conversations from memory manager."""
        try:
            # This would integrate with your memory manager
            return {
                "conversations": [],
                "total_count": 0,
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to load conversations: {e}")
    
    def _load_templates(self):
        """Load templates from disk."""
        try:
            # This would integrate with your template system
            return {
                "templates": [],
                "total_count": 0,
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to load templates: {e}")
    
    def _load_analytics(self):
        """Load analytics data."""
        try:
            # This would integrate with your analytics system
            return {
                "analytics": {},
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to load analytics: {e}")
    
    def _load_skills(self):
        """Load skills from MMORPG system."""
        try:
            # This would integrate with your MMORPG system
            return {
                "skills": [],
                "total_count": 0,
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to load skills: {e}")
    
    def _load_projects(self):
        """Load projects data."""
        try:
            # This would integrate with your project system
            return {
                "projects": [],
                "total_count": 0,
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to load projects: {e}")
    
    def _load_agents(self):
        """Load AI agents."""
        try:
            # This would integrate with your agent system
            return {
                "agents": [],
                "total_count": 0,
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to load agents: {e}")

class DataCache:
    """Simple in-memory cache for loaded data."""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data if not expired."""
        if key in self._cache:
            timestamp = self._timestamps.get(key)
            if timestamp and (datetime.now() - timestamp).seconds < 300:  # 5 minutes
                return self._cache[key]
            else:
                # Remove expired cache entry
                del self._cache[key]
                if key in self._timestamps:
                    del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any):
        """Cache data with current timestamp."""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def clear(self):
        """Clear all cached data."""
        self._cache.clear()
        self._timestamps.clear()
    
    def remove(self, key: str):
        """Remove specific cache entry."""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]

class UnifiedDataLoader(QWidget):
    """Unified Data Loading System with intelligent caching and background processing."""
    
    # Signals
    operation_started = pyqtSignal(str)  # operation_id
    operation_completed = pyqtSignal(str, bool, str, Any)  # operation_id, success, message, result
    progress_updated = pyqtSignal(str, int, str)  # operation_id, progress, message
    cache_updated = pyqtSignal(str, Any)  # cache_key, data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache = DataCache()
        self.active_operations = {}
        self.operation_history = []
        self.max_concurrent_operations = 3
        self.operation_counter = 0
        
        self.init_ui()
        self.setup_auto_refresh()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🚀 Unified Data Loading System")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Create tabbed interface
        self.tab_widget = QTabWidget()
        
        # Active Operations Tab
        self.active_tab = self.create_active_operations_tab()
        self.tab_widget.addTab(self.active_tab, "🔄 Active Operations")
        
        # Quick Load Tab
        self.quick_load_tab = self.create_quick_load_tab()
        self.tab_widget.addTab(self.quick_load_tab, "⚡ Quick Load")
        
        # Cache Management Tab
        self.cache_tab = self.create_cache_management_tab()
        self.tab_widget.addTab(self.cache_tab, "💾 Cache Management")
        
        # History Tab
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📋 Load History")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready to load data")
        layout.addWidget(self.status_label)
    
    def create_active_operations_tab(self) -> QWidget:
        """Create the active operations tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Active operations table
        self.active_operations_table = QTableWidget()
        self.active_operations_table.setColumnCount(6)
        self.active_operations_table.setHorizontalHeaderLabels([
            "Operation", "Type", "Priority", "Progress", "Status", "Actions"
        ])
        
        header = self.active_operations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.active_operations_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.cancel_all_btn = QPushButton("❌ Cancel All")
        self.cancel_all_btn.clicked.connect(self.cancel_all_operations)
        button_layout.addWidget(self.cancel_all_btn)
        
        self.clear_completed_btn = QPushButton("🧹 Clear Completed")
        self.clear_completed_btn.clicked.connect(self.clear_completed_operations)
        button_layout.addWidget(self.clear_completed_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def create_quick_load_tab(self) -> QWidget:
        """Create the quick load tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Quick load options
        options_group = QGroupBox("Quick Load Options")
        options_layout = QVBoxLayout(options_group)
        
        # Data type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Data Type:"))
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            "Conversations", "Templates", "Analytics", "Skills", 
            "Projects", "Agents", "Settings", "User Data"
        ])
        type_layout.addWidget(self.data_type_combo)
        options_layout.addLayout(type_layout)
        
        # Priority selection
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Normal", "High", "Critical"])
        self.priority_combo.setCurrentText("Normal")
        priority_layout.addWidget(self.priority_combo)
        options_layout.addLayout(priority_layout)
        
        # Options
        self.use_cache_checkbox = QCheckBox("Use cached data if available")
        self.use_cache_checkbox.setChecked(True)
        options_layout.addWidget(self.use_cache_checkbox)
        
        self.background_checkbox = QCheckBox("Load in background")
        self.background_checkbox.setChecked(True)
        options_layout.addWidget(self.background_checkbox)
        
        layout.addWidget(options_group)
        
        # Quick load buttons
        buttons_group = QGroupBox("Quick Load Actions")
        buttons_layout = QGridLayout(buttons_group)
        
        self.load_conversations_btn = QPushButton("💬 Load Conversations")
        self.load_conversations_btn.clicked.connect(lambda: self.quick_load("conversations"))
        buttons_layout.addWidget(self.load_conversations_btn, 0, 0)
        
        self.load_templates_btn = QPushButton("📝 Load Templates")
        self.load_templates_btn.clicked.connect(lambda: self.quick_load("templates"))
        buttons_layout.addWidget(self.load_templates_btn, 0, 1)
        
        self.load_analytics_btn = QPushButton("📊 Load Analytics")
        self.load_analytics_btn.clicked.connect(lambda: self.quick_load("analytics"))
        buttons_layout.addWidget(self.load_analytics_btn, 1, 0)
        
        self.load_skills_btn = QPushButton("🎯 Load Skills")
        self.load_skills_btn.clicked.connect(lambda: self.quick_load("skills"))
        buttons_layout.addWidget(self.load_skills_btn, 1, 1)
        
        self.load_projects_btn = QPushButton("📋 Load Projects")
        self.load_projects_btn.clicked.connect(lambda: self.quick_load("projects"))
        buttons_layout.addWidget(self.load_projects_btn, 2, 0)
        
        self.load_agents_btn = QPushButton("🤖 Load Agents")
        self.load_agents_btn.clicked.connect(lambda: self.quick_load("agents"))
        buttons_layout.addWidget(self.load_agents_btn, 2, 1)
        
        layout.addWidget(buttons_group)
        
        # Load all button
        self.load_all_btn = QPushButton("🚀 Load All Data")
        self.load_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.load_all_btn.clicked.connect(self.load_all_data)
        layout.addWidget(self.load_all_btn)
        
        layout.addStretch()
        return widget
    
    def create_cache_management_tab(self) -> QWidget:
        """Create the cache management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Cache info
        info_group = QGroupBox("Cache Information")
        info_layout = QVBoxLayout(info_group)
        
        self.cache_info_label = QLabel("Cache: 0 items, 0 MB")
        info_layout.addWidget(self.cache_info_label)
        
        layout.addWidget(info_group)
        
        # Cache table
        self.cache_table = QTableWidget()
        self.cache_table.setColumnCount(4)
        self.cache_table.setHorizontalHeaderLabels([
            "Cache Key", "Data Type", "Size", "Actions"
        ])
        
        header = self.cache_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.cache_table)
        
        # Cache control buttons
        cache_buttons_layout = QHBoxLayout()
        
        self.refresh_cache_btn = QPushButton("🔄 Refresh Cache")
        self.refresh_cache_btn.clicked.connect(self.refresh_cache_display)
        cache_buttons_layout.addWidget(self.refresh_cache_btn)
        
        self.clear_cache_btn = QPushButton("🧹 Clear Cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_buttons_layout.addWidget(self.clear_cache_btn)
        
        cache_buttons_layout.addStretch()
        layout.addLayout(cache_buttons_layout)
        
        return widget
    
    def create_history_tab(self) -> QWidget:
        """Create the load history tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Operation", "Type", "Status", "Duration", "Result"
        ])
        
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.history_table)
        
        # History control buttons
        history_buttons_layout = QHBoxLayout()
        
        self.clear_history_btn = QPushButton("🧹 Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        history_buttons_layout.addWidget(self.clear_history_btn)
        
        self.export_history_btn = QPushButton("📤 Export History")
        self.export_history_btn.clicked.connect(self.export_history)
        history_buttons_layout.addWidget(self.export_history_btn)
        
        history_buttons_layout.addStretch()
        layout.addLayout(history_buttons_layout)
        
        return widget
    
    def setup_auto_refresh(self):
        """Setup automatic refresh of the UI."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_ui)
        self.refresh_timer.start(1000)  # Refresh every second
    
    def refresh_ui(self):
        """Refresh the user interface."""
        self.update_active_operations_table()
        self.update_cache_info()
        self.update_history_table()
    
    def update_active_operations_table(self):
        """Update the active operations table."""
        self.active_operations_table.setRowCount(len(self.active_operations))
        
        for row, (operation_id, operation) in enumerate(self.active_operations.items()):
            # Operation name
            name_item = QTableWidgetItem(operation.name)
            self.active_operations_table.setItem(row, 0, name_item)
            
            # Data type
            type_item = QTableWidgetItem(operation.data_type)
            self.active_operations_table.setItem(row, 1, type_item)
            
            # Priority
            priority_item = QTableWidgetItem(operation.priority.name)
            self.active_operations_table.setItem(row, 2, priority_item)
            
            # Progress
            progress_item = QTableWidgetItem(f"{operation.progress}%")
            self.active_operations_table.setItem(row, 3, progress_item)
            
            # Status
            status_item = QTableWidgetItem(operation.status.value)
            self.active_operations_table.setItem(row, 4, status_item)
            
            # Actions
            if operation.status == LoadStatus.LOADING:
                cancel_btn = QPushButton("❌ Cancel")
                cancel_btn.clicked.connect(lambda checked, op_id=operation_id: self.cancel_operation(op_id))
                self.active_operations_table.setCellWidget(row, 5, cancel_btn)
    
    def update_cache_info(self):
        """Update cache information display."""
        cache_size = len(self.cache._cache)
        self.cache_info_label.setText(f"Cache: {cache_size} items")
    
    def update_history_table(self):
        """Update the history table."""
        # Limit to last 50 operations
        recent_history = self.operation_history[-50:]
        self.history_table.setRowCount(len(recent_history))
        
        for row, operation in enumerate(recent_history):
            # Time
            time_str = operation.start_time.strftime("%H:%M:%S") if operation.start_time else "N/A"
            time_item = QTableWidgetItem(time_str)
            self.history_table.setItem(row, 0, time_item)
            
            # Operation name
            name_item = QTableWidgetItem(operation.name)
            self.history_table.setItem(row, 1, name_item)
            
            # Data type
            type_item = QTableWidgetItem(operation.data_type)
            self.history_table.setItem(row, 2, type_item)
            
            # Status
            status_item = QTableWidgetItem(operation.status.value)
            self.history_table.setItem(row, 3, status_item)
            
            # Duration
            if operation.start_time and operation.end_time:
                duration = (operation.end_time - operation.start_time).total_seconds()
                duration_item = QTableWidgetItem(f"{duration:.2f}s")
            else:
                duration_item = QTableWidgetItem("N/A")
            self.history_table.setItem(row, 4, duration_item)
            
            # Result
            if operation.status == LoadStatus.COMPLETED:
                result_item = QTableWidgetItem("✅ Success")
            elif operation.status == LoadStatus.FAILED:
                result_item = QTableWidgetItem(f"❌ {operation.error_message}")
            else:
                result_item = QTableWidgetItem("⏳ Pending")
            self.history_table.setItem(row, 5, result_item)
    
    def quick_load(self, data_type: str):
        """Quick load specific data type."""
        priority_text = self.priority_combo.currentText()
        priority = LoadPriority[priority_text.upper()]
        
        operation = LoadOperation(
            id=f"quick_load_{data_type}_{int(time.time())}",
            name=f"Quick Load {data_type.title()}",
            description=f"Quick load operation for {data_type}",
            priority=priority,
            data_type=data_type,
            source="quick_load",
            target_panel="unified_loader"
        )
        
        self.start_operation(operation)
    
    def load_all_data(self):
        """Load all data types."""
        data_types = ["conversations", "templates", "analytics", "skills", "projects", "agents"]
        
        for data_type in data_types:
            operation = LoadOperation(
                id=f"load_all_{data_type}_{int(time.time())}",
                name=f"Load All {data_type.title()}",
                description=f"Load all {data_type} data",
                priority=LoadPriority.NORMAL,
                data_type=data_type,
                source="load_all",
                target_panel="unified_loader"
            )
            
            self.start_operation(operation)
    
    def start_operation(self, operation: LoadOperation):
        """Start a loading operation."""
        # Check cache first if enabled
        if operation.cache_key and self.cache.get(operation.cache_key):
            cached_data = self.cache.get(operation.cache_key)
            self.operation_completed.emit(
                operation.id, True, f"Loaded {operation.data_type} from cache", cached_data
            )
            return
        
        # Check if we can start more operations
        if len(self.active_operations) >= self.max_concurrent_operations:
            # Queue the operation
            self.operation_history.append(operation)
            self.status_label.setText(f"Queued: {operation.name}")
            return
        
        # Start the operation
        self.active_operations[operation.id] = operation
        self.operation_history.append(operation)
        
        # Create and start worker
        worker = DataLoaderWorker(operation)
        worker.progress_updated.connect(self.on_progress_updated)
        worker.operation_completed.connect(self.on_operation_completed)
        worker.operation_started.connect(self.on_operation_started)
        
        worker.start()
        
        self.status_label.setText(f"Started: {operation.name}")
    
    def on_operation_started(self, operation_id: str):
        """Handle operation start."""
        if operation_id in self.active_operations:
            self.operation_started.emit(operation_id)
    
    def on_progress_updated(self, operation_id: str, progress: int, message: str):
        """Handle progress updates."""
        if operation_id in self.active_operations:
            self.active_operations[operation_id].progress = progress
            self.progress_updated.emit(operation_id, progress, message)
    
    def on_operation_completed(self, operation_id: str, success: bool, message: str, result: Any):
        """Handle operation completion."""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation.status = LoadStatus.COMPLETED if success else LoadStatus.FAILED
            operation.result = result
            
            # Cache the result if successful
            if success and operation.cache_key:
                self.cache.set(operation.cache_key, result)
                self.cache_updated.emit(operation.cache_key, result)
            
            # Remove from active operations after a delay
            QTimer.singleShot(2000, lambda: self.remove_completed_operation(operation_id))
            
            self.operation_completed.emit(operation_id, success, message, result)
            self.status_label.setText(message)
    
    def remove_completed_operation(self, operation_id: str):
        """Remove completed operation from active list."""
        if operation_id in self.active_operations:
            del self.active_operations[operation_id]
    
    def cancel_operation(self, operation_id: str):
        """Cancel a specific operation."""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation.status = LoadStatus.CANCELLED
            operation.end_time = datetime.now()
            
            # Remove from active operations
            del self.active_operations[operation_id]
            
            self.status_label.setText(f"Cancelled: {operation.name}")
    
    def cancel_all_operations(self):
        """Cancel all active operations."""
        for operation_id in list(self.active_operations.keys()):
            self.cancel_operation(operation_id)
    
    def clear_completed_operations(self):
        """Clear completed operations from history."""
        self.operation_history = [
            op for op in self.operation_history 
            if op.status not in [LoadStatus.COMPLETED, LoadStatus.FAILED, LoadStatus.CANCELLED]
        ]
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        self.cache_updated.emit("all", None)
        self.status_label.setText("Cache cleared")
    
    def refresh_cache_display(self):
        """Refresh the cache display."""
        self.update_cache_info()
        self.update_cache_table()
    
    def update_cache_table(self):
        """Update the cache table display."""
        cache_items = list(self.cache._cache.items())
        self.cache_table.setRowCount(len(cache_items))
        
        for row, (key, value) in enumerate(cache_items):
            # Cache key
            key_item = QTableWidgetItem(key)
            self.cache_table.setItem(row, 0, key_item)
            
            # Data type
            type_item = QTableWidgetItem(type(value).__name__)
            self.cache_table.setItem(row, 1, type_item)
            
            # Size (approximate)
            size_item = QTableWidgetItem(f"{len(str(value))} chars")
            self.cache_table.setItem(row, 2, size_item)
            
            # Actions
            remove_btn = QPushButton("🗑️ Remove")
            remove_btn.clicked.connect(lambda checked, k=key: self.cache.remove(k))
            self.cache_table.setCellWidget(row, 3, remove_btn)
    
    def clear_history(self):
        """Clear operation history."""
        self.operation_history.clear()
        self.status_label.setText("History cleared")
    
    def export_history(self):
        """Export operation history."""
        try:
            history_data = []
            for operation in self.operation_history:
                history_data.append({
                    "id": operation.id,
                    "name": operation.name,
                    "data_type": operation.data_type,
                    "status": operation.status.value,
                    "start_time": operation.start_time.isoformat() if operation.start_time else None,
                    "end_time": operation.end_time.isoformat() if operation.end_time else None,
                    "error_message": operation.error_message
                })
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_history_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            QMessageBox.information(self, "Export Complete", f"History exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export history: {e}")
    
    def get_cached_data(self, data_type: str) -> Optional[Any]:
        """Get cached data for a specific type."""
        cache_key = f"{data_type}_data"
        return self.cache.get(cache_key)
    
    def set_cached_data(self, data_type: str, data: Any):
        """Set cached data for a specific type."""
        cache_key = f"{data_type}_data"
        self.cache.set(cache_key, data)
        self.cache_updated.emit(cache_key, data)
    
    def show_loader(self):
        """Show the unified data loader."""
        self.show()
        self.raise_()
        self.activateWindow() 