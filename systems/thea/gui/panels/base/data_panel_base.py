"""
Data Panel Base - Common Data Management Panel Functionality
==========================================================

This module provides the base class for data management panels with common
functionality like data loading, filtering, and manipulation.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QComboBox,
    QSpinBox, QCheckBox, QSplitter, QFrame, QScrollArea,
    QGridLayout, QListWidget, QListWidgetItem, QHeaderView,
    QLineEdit, QTextEdit, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont

from gui.base_panel import BasePanel

logger = logging.getLogger(__name__)


class DataWorker(QThread):
    """Background worker for data operations."""
    data_loaded = pyqtSignal(dict)
    data_processed = pyqtSignal(dict)
    data_filtered = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, operation_type: str, data: Dict[str, Any]):
        super().__init__()
        self.operation_type = operation_type
        self.data = data
        self.running = False
    
    def run(self):
        """Execute the data operation."""
        self.running = True
        try:
            if self.operation_type == "load":
                self._simulate_data_load()
            elif self.operation_type == "process":
                self._simulate_data_process()
            elif self.operation_type == "filter":
                self._simulate_data_filter()
            else:
                raise ValueError(f"Unknown operation type: {self.operation_type}")
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.running = False
    
    def _simulate_data_load(self):
        """Simulate data loading."""
        import time
        time.sleep(1)  # Simulate loading time
        
        loaded_data = {
            "total_records": 150,
            "data_type": self.data.get("data_type", "conversations"),
            "columns": ["id", "title", "content", "timestamp", "metadata"],
            "sample_data": [
                {"id": 1, "title": "Sample Conversation", "content": "Sample content", "timestamp": "2025-01-01"},
                {"id": 2, "title": "Another Conversation", "content": "More content", "timestamp": "2025-01-02"}
            ],
            "loaded_at": datetime.now().isoformat()
        }
        
        self.data_loaded.emit(loaded_data)
    
    def _simulate_data_process(self):
        """Simulate data processing."""
        import time
        time.sleep(2)  # Simulate processing time
        
        processed_data = {
            "original_count": self.data.get("record_count", 100),
            "processed_count": 95,
            "errors": 5,
            "processing_time": 2.1,
            "processed_at": datetime.now().isoformat()
        }
        
        self.data_processed.emit(processed_data)
    
    def _simulate_data_filter(self):
        """Simulate data filtering."""
        import time
        time.sleep(0.5)  # Simulate filtering time
        
        filter_criteria = self.data.get("filter_criteria", {})
        filtered_data = {
            "original_count": 150,
            "filtered_count": 75,
            "filter_criteria": filter_criteria,
            "filtered_at": datetime.now().isoformat()
        }
        
        self.data_filtered.emit(filtered_data)


class DataPanelBase(BasePanel):
    """Base class for data management panels with common data functionality."""
    
    # Data-specific signals
    data_loaded = pyqtSignal(dict)         # Data loaded
    data_processed = pyqtSignal(dict)      # Data processed
    data_filtered = pyqtSignal(dict)       # Data filtered
    data_updated = pyqtSignal(dict)        # Data updated
    
    def __init__(self, title: str = "Data Panel", description: str = "", parent=None):
        """Initialize the data base panel."""
        super().__init__(title, description, parent)
        
        # Data state
        self.data_records = []
        self.filtered_records = []
        self.data_columns = []
        self.data_filters = {}
        
        # Data components
        self.data_table = None
        self.filter_input = None
        self.column_selector = None
        self.data_summary_label = None
        
        # Data workers
        self.data_worker = None
        
        # Data settings
        self.auto_refresh_data = False
        self.refresh_interval = 60000  # 1 minute
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_data_operation)
        
        # Initialize data UI
        self.setup_data_ui()
    
    def setup_data_ui(self):
        """Setup data-specific UI components."""
        # Create data table
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Create filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filter criteria...")
        self.filter_input.textChanged.connect(self.apply_filter)
        
        # Create column selector
        self.column_selector = QComboBox()
        self.column_selector.addItems(["All Columns", "ID", "Title", "Content", "Timestamp"])
        self.column_selector.currentTextChanged.connect(self.on_column_selection_changed)
        
        # Create data summary label
        self.data_summary_label = QLabel("No data loaded")
        self.data_summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def create_data_tab(self, title: str = "Data") -> QWidget:
        """Create a standard data tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data controls
        controls_group = QGroupBox("Data Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Load and refresh buttons
        buttons_layout = QHBoxLayout()
        self.load_data_button = QPushButton("📂 Load Data")
        self.load_data_button.clicked.connect(self.load_data)
        buttons_layout.addWidget(self.load_data_button)
        
        self.refresh_data_button = QPushButton("🔄 Refresh")
        self.refresh_data_button.clicked.connect(self.refresh_data)
        buttons_layout.addWidget(self.refresh_data_button)
        
        self.process_data_button = QPushButton("⚙️ Process")
        self.process_data_button.clicked.connect(self.process_data)
        buttons_layout.addWidget(self.process_data_button)
        
        buttons_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("Column:"))
        filter_layout.addWidget(self.column_selector)
        filter_layout.addStretch()
        controls_layout.addLayout(filter_layout)
        
        layout.addWidget(controls_group)
        
        # Data summary
        summary_group = QGroupBox("Data Summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.data_summary_label)
        layout.addWidget(summary_group)
        
        # Data table
        table_group = QGroupBox("Data Records")
        table_layout = QVBoxLayout(table_group)
        table_layout.addWidget(self.data_table)
        layout.addWidget(table_group)
        
        return tab
    
    def load_data(self):
        """Load data from source."""
        self.set_status("Loading data...")
        self.show_progress(True)
        
        # Start data loading worker
        self.data_worker = DataWorker("load", {"data_type": "conversations"})
        self.data_worker.data_loaded.connect(self.on_data_loaded)
        self.data_worker.error_occurred.connect(self.on_data_error)
        self.data_worker.start()
    
    def refresh_data(self):
        """Refresh the current data."""
        if self.data_records:
            self.load_data()
        else:
            self.set_status("No data to refresh")
    
    def process_data(self):
        """Process the loaded data."""
        if not self.data_records:
            self.show_warning("No data to process")
            return
        
        self.set_status("Processing data...")
        self.show_progress(True)
        
        # Start data processing worker
        self.data_worker = DataWorker("process", {"record_count": len(self.data_records)})
        self.data_worker.data_processed.connect(self.on_data_processed)
        self.data_worker.error_occurred.connect(self.on_data_error)
        self.data_worker.start()
    
    def apply_filter(self):
        """Apply filter to the data."""
        filter_text = self.filter_input.text().strip()
        if not filter_text:
            self.filtered_records = self.data_records.copy()
        else:
            self.filtered_records = [
                record for record in self.data_records
                if self._record_matches_filter(record, filter_text)
            ]
        
        self.update_data_table()
        self.update_data_summary()
        self.data_filtered.emit({
            "original_count": len(self.data_records),
            "filtered_count": len(self.filtered_records),
            "filter_text": filter_text
        })
    
    def _record_matches_filter(self, record: Dict[str, Any], filter_text: str) -> bool:
        """Check if a record matches the filter criteria."""
        filter_text = filter_text.lower()
        
        for key, value in record.items():
            if isinstance(value, str) and filter_text in value.lower():
                return True
            elif isinstance(value, (int, float)) and filter_text in str(value):
                return True
        
        return False
    
    def on_data_loaded(self, data: Dict[str, Any]):
        """Handle data loaded event."""
        self.data_records = data.get("sample_data", [])
        self.data_columns = data.get("columns", [])
        self.filtered_records = self.data_records.copy()
        
        self.setup_data_table()
        self.update_data_summary()
        
        self.data_loaded.emit(data)
        self.set_status(f"Data loaded: {len(self.data_records)} records")
        self.show_progress(False)
    
    def on_data_processed(self, result: Dict[str, Any]):
        """Handle data processed event."""
        self.data_processed.emit(result)
        self.set_status(f"Data processed: {result.get('processed_count', 0)} records")
        self.show_progress(False)
        
        # Show processing results
        self.show_info(
            f"Processing completed!\n"
            f"Original: {result.get('original_count', 0)}\n"
            f"Processed: {result.get('processed_count', 0)}\n"
            f"Errors: {result.get('errors', 0)}"
        )
    
    def on_data_error(self, error: str):
        """Handle data operation error."""
        self.set_status(f"Data error: {error}")
        self.show_error(f"Data operation failed: {error}")
        self.show_progress(False)
    
    def setup_data_table(self):
        """Setup the data table with columns and data."""
        if not self.data_table or not self.data_columns:
            return
        
        # Set up columns
        self.data_table.setColumnCount(len(self.data_columns))
        self.data_table.setHorizontalHeaderLabels(self.data_columns)
        
        # Set up rows
        self.data_table.setRowCount(len(self.filtered_records))
        
        # Populate data
        for row, record in enumerate(self.filtered_records):
            for col, column in enumerate(self.data_columns):
                value = record.get(column, "")
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(row, col, item)
        
        # Resize columns to content
        self.data_table.resizeColumnsToContents()
    
    def update_data_table(self):
        """Update the data table with current filtered data."""
        if not self.data_table:
            return
        
        self.data_table.setRowCount(len(self.filtered_records))
        
        for row, record in enumerate(self.filtered_records):
            for col, column in enumerate(self.data_columns):
                value = record.get(column, "")
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(row, col, item)
    
    def update_data_summary(self):
        """Update the data summary display."""
        if not self.data_summary_label:
            return
        
        total_records = len(self.data_records)
        filtered_records = len(self.filtered_records)
        
        if total_records == 0:
            summary_text = "No data loaded"
        elif filtered_records == total_records:
            summary_text = f"Showing {total_records} records"
        else:
            summary_text = f"Showing {filtered_records} of {total_records} records (filtered)"
        
        self.data_summary_label.setText(summary_text)
    
    def on_column_selection_changed(self, column: str):
        """Handle column selection change."""
        if column == "All Columns":
            self.setup_data_table()
        else:
            # Filter to show only selected column
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels([column])
            
            self.data_table.setRowCount(len(self.filtered_records))
            for row, record in enumerate(self.filtered_records):
                value = record.get(column, "")
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(row, 0, item)
    
    def start_auto_refresh(self, interval: int = None):
        """Start automatic data refresh."""
        if interval:
            self.refresh_interval = interval
        
        self.auto_refresh_data = True
        self.refresh_timer.start(self.refresh_interval)
        self.set_status("Auto-refresh started")
    
    def stop_auto_refresh(self):
        """Stop automatic data refresh."""
        self.auto_refresh_data = False
        self.refresh_timer.stop()
        self.set_status("Auto-refresh stopped")
    
    def auto_refresh_data_operation(self):
        """Automatically refresh data."""
        if self.auto_refresh_data:
            self.refresh_data()
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of the data."""
        return {
            "total_records": len(self.data_records),
            "filtered_records": len(self.filtered_records),
            "columns": self.data_columns,
            "filters_applied": self.data_filters,
            "last_updated": datetime.now().isoformat()
        }
    
    def export_data(self, format: str = "json") -> str:
        """Export the current data."""
        try:
            export_data = {
                "data_records": self.filtered_records,
                "columns": self.data_columns,
                "summary": self.get_data_summary(),
                "exported_at": datetime.now().isoformat()
            }
            
            if format == "json":
                return json.dumps(export_data, indent=2)
            else:
                return str(export_data)
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return None 