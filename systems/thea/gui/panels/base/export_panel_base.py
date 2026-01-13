"""
Export Panel Base - Common Export Panel Functionality
===================================================

This module provides the base class for export panels with common
functionality like format selection, export history, and batch operations.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import csv
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QComboBox,
    QSpinBox, QCheckBox, QSplitter, QFrame, QScrollArea,
    QGridLayout, QListWidget, QListWidgetItem, QHeaderView,
    QFileDialog, QProgressDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont

from gui.base_panel import BasePanel

logger = logging.getLogger(__name__)


class ExportWorker(QThread):
    """Background worker for export operations."""
    export_progress = pyqtSignal(int)
    export_completed = pyqtSignal(dict)
    export_failed = pyqtSignal(str)
    
    def __init__(self, export_data: Dict[str, Any], format: str, file_path: str):
        super().__init__()
        self.export_data = export_data
        self.format = format
        self.file_path = file_path
    
    def run(self):
        """Execute the export operation."""
        try:
            self.export_progress.emit(10)
            
            if self.format == "json":
                result = self._export_json()
            elif self.format == "csv":
                result = self._export_csv()
            elif self.format == "txt":
                result = self._export_txt()
            elif self.format == "md":
                result = self._export_markdown()
            else:
                raise ValueError(f"Unsupported format: {self.format}")
            
            self.export_progress.emit(100)
            self.export_completed.emit(result)
            
        except Exception as e:
            self.export_failed.emit(str(e))
    
    def _export_json(self) -> Dict[str, Any]:
        """Export data as JSON."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.export_data, f, indent=2, ensure_ascii=False)
        
        return {
            "format": "json",
            "file_path": self.file_path,
            "size": Path(self.file_path).stat().st_size,
            "exported_at": datetime.now().isoformat()
        }
    
    def _export_csv(self) -> Dict[str, Any]:
        """Export data as CSV."""
        # Flatten the data for CSV export
        flattened_data = self._flatten_data(self.export_data)
        
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
        
        return {
            "format": "csv",
            "file_path": self.file_path,
            "size": Path(self.file_path).stat().st_size,
            "exported_at": datetime.now().isoformat()
        }
    
    def _export_txt(self) -> Dict[str, Any]:
        """Export data as plain text."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self._format_as_text(self.export_data))
        
        return {
            "format": "txt",
            "file_path": self.file_path,
            "size": Path(self.file_path).stat().st_size,
            "exported_at": datetime.now().isoformat()
        }
    
    def _export_markdown(self) -> Dict[str, Any]:
        """Export data as Markdown."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self._format_as_markdown(self.export_data))
        
        return {
            "format": "md",
            "file_path": self.file_path,
            "size": Path(self.file_path).stat().st_size,
            "exported_at": datetime.now().isoformat()
        }
    
    def _flatten_data(self, data: Any, prefix: str = "") -> List[Dict[str, Any]]:
        """Flatten nested data for CSV export."""
        if isinstance(data, dict):
            flattened = {}
            for key, value in data.items():
                new_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    flattened.update(self._flatten_data(value, new_key))
                else:
                    flattened[new_key] = value
            return [flattened]
        elif isinstance(data, list):
            result = []
            for item in data:
                result.extend(self._flatten_data(item, prefix))
            return result
        else:
            return [{prefix: data}] if prefix else [{"value": data}]
    
    def _format_as_text(self, data: Any, indent: int = 0) -> str:
        """Format data as plain text."""
        if isinstance(data, dict):
            result = ""
            for key, value in data.items():
                result += "  " * indent + f"{key}: {self._format_as_text(value, indent + 1)}\n"
            return result
        elif isinstance(data, list):
            result = ""
            for i, item in enumerate(data):
                result += "  " * indent + f"[{i}]: {self._format_as_text(item, indent + 1)}\n"
            return result
        else:
            return str(data)
    
    def _format_as_markdown(self, data: Any, level: int = 1) -> str:
        """Format data as Markdown."""
        if isinstance(data, dict):
            result = ""
            for key, value in data.items():
                result += "#" * level + f" {key}\n\n"
                result += self._format_as_markdown(value, level + 1) + "\n\n"
            return result
        elif isinstance(data, list):
            result = ""
            for item in data:
                result += self._format_as_markdown(item, level) + "\n"
            return result
        else:
            return str(data)


class ExportPanelBase(BasePanel):
    """Base class for export panels with common export functionality."""
    
    # Export-specific signals
    export_started = pyqtSignal(str)      # Export started (format)
    export_completed = pyqtSignal(dict)   # Export completed (result)
    export_failed = pyqtSignal(str)       # Export failed (error)
    export_progress = pyqtSignal(int)     # Export progress (percentage)
    
    def __init__(self, title: str = "Export Panel", description: str = "", parent=None):
        """Initialize the export base panel."""
        super().__init__(title, description, parent)
        
        # Export state
        self.export_data = {}
        self.export_history = []
        self.export_formats = ["json", "csv", "txt", "md", "html", "pdf", "excel"]
        self.current_export = None
        
        # Export components
        self.format_selector = None
        self.export_history_table = None
        self.batch_export_list = None
        
        # Export settings
        self.auto_open_export = False
        self.include_timestamp = True
        self.compression_enabled = False
        
        # Initialize export UI
        self.setup_export_ui()
    
    def setup_export_ui(self):
        """Setup export-specific UI components."""
        # Create format selector
        self.format_selector = QComboBox()
        self.format_selector.addItems([fmt.upper() for fmt in self.export_formats])
        
        # Create export history table
        self.export_history_table = QTableWidget()
        self.export_history_table.setColumnCount(5)
        self.export_history_table.setHorizontalHeaderLabels([
            "Date", "Format", "File", "Size", "Status"
        ])
        self.export_history_table.horizontalHeader().setStretchLastSection(True)
        
        # Create batch export list
        self.batch_export_list = QListWidget()
    
    def create_export_tab(self, title: str = "Export") -> QWidget:
        """Create a standard export tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export controls
        controls_group = QGroupBox("Export Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        format_layout.addWidget(self.format_selector)
        format_layout.addStretch()
        controls_layout.addLayout(format_layout)
        
        # Export options
        options_layout = QHBoxLayout()
        self.auto_open_checkbox = QCheckBox("Auto-open after export")
        self.auto_open_checkbox.setChecked(self.auto_open_export)
        options_layout.addWidget(self.auto_open_checkbox)
        
        self.timestamp_checkbox = QCheckBox("Include timestamp")
        self.timestamp_checkbox.setChecked(self.include_timestamp)
        options_layout.addWidget(self.timestamp_checkbox)
        
        self.compression_checkbox = QCheckBox("Enable compression")
        self.compression_checkbox.setChecked(self.compression_enabled)
        options_layout.addWidget(self.compression_checkbox)
        
        options_layout.addStretch()
        controls_layout.addLayout(options_layout)
        
        # Export buttons
        buttons_layout = QHBoxLayout()
        self.export_button = QPushButton("📤 Export")
        self.export_button.clicked.connect(self.start_export)
        buttons_layout.addWidget(self.export_button)
        
        self.batch_export_button = QPushButton("📦 Batch Export")
        self.batch_export_button.clicked.connect(self.start_batch_export)
        buttons_layout.addWidget(self.batch_export_button)
        
        self.clear_history_button = QPushButton("🗑️ Clear History")
        self.clear_history_button.clicked.connect(self.clear_export_history)
        buttons_layout.addWidget(self.clear_history_button)
        
        buttons_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        layout.addWidget(controls_group)
        
        # Export history
        history_group = QGroupBox("Export History")
        history_layout = QVBoxLayout(history_group)
        history_layout.addWidget(self.export_history_table)
        layout.addWidget(history_group)
        
        return tab
    
    def start_export(self):
        """Start a single export operation."""
        if not self.export_data:
            self.show_warning("No data available for export")
            return
        
        format = self.format_selector.currentText().lower()
        
        # Get file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export as {format.upper()}",
            f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
            f"{format.upper()} Files (*.{format})"
        )
        
        if not file_path:
            return
        
        self.export_started.emit(format)
        self.set_status(f"Starting {format.upper()} export...")
        
        # Create and start export worker
        self.current_export = ExportWorker(self.export_data, format, file_path)
        self.current_export.export_progress.connect(self.update_export_progress)
        self.current_export.export_completed.connect(self.on_export_completed)
        self.current_export.export_failed.connect(self.on_export_failed)
        self.current_export.start()
    
    def start_batch_export(self):
        """Start a batch export operation."""
        if not self.export_data:
            self.show_warning("No data available for batch export")
            return
        
        # Get directory for batch export
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select directory for batch export"
        )
        
        if not directory:
            return
        
        self.set_status("Starting batch export...")
        
        # Export in all formats
        for format in self.export_formats:
            file_path = Path(directory) / f"batch_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            
            worker = ExportWorker(self.export_data, format, str(file_path))
            worker.export_completed.connect(self.on_export_completed)
            worker.export_failed.connect(self.on_export_failed)
            worker.start()
    
    def update_export_progress(self, percentage: int):
        """Update export progress."""
        self.update_progress(percentage)
        self.export_progress.emit(percentage)
    
    def on_export_completed(self, result: Dict[str, Any]):
        """Handle export completion."""
        # Add to history
        self.export_history.append(result)
        self.update_export_history_display()
        
        # Update status
        self.set_status(f"Export completed: {result['file_path']}")
        self.export_completed.emit(result)
        
        # Auto-open if enabled
        if self.auto_open_checkbox.isChecked():
            self.open_export_file(result['file_path'])
    
    def on_export_failed(self, error: str):
        """Handle export failure."""
        self.set_status(f"Export failed: {error}")
        self.export_failed.emit(error)
        self.show_error(f"Export failed: {error}")
    
    def update_export_history_display(self):
        """Update the export history table display."""
        if not self.export_history_table:
            return
        
        self.export_history_table.setRowCount(len(self.export_history))
        
        for i, export in enumerate(self.export_history):
            # Date
            date_item = QTableWidgetItem(export.get('exported_at', ''))
            self.export_history_table.setItem(i, 0, date_item)
            
            # Format
            format_item = QTableWidgetItem(export.get('format', '').upper())
            self.export_history_table.setItem(i, 1, format_item)
            
            # File
            file_item = QTableWidgetItem(Path(export.get('file_path', '')).name)
            self.export_history_table.setItem(i, 2, file_item)
            
            # Size
            size = export.get('size', 0)
            size_item = QTableWidgetItem(self._format_file_size(size))
            self.export_history_table.setItem(i, 3, size_item)
            
            # Status
            status_item = QTableWidgetItem("✅ Completed")
            status_item.setForeground(Qt.GlobalColor.green)
            self.export_history_table.setItem(i, 4, status_item)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def open_export_file(self, file_path: str):
        """Open the exported file."""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
                
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
    
    def clear_export_history(self):
        """Clear the export history."""
        self.export_history.clear()
        if self.export_history_table:
            self.export_history_table.setRowCount(0)
        self.set_status("Export history cleared")
    
    def set_export_data(self, data: Dict[str, Any]):
        """Set the data to be exported."""
        self.export_data = data
        if self.include_timestamp:
            self.export_data['exported_at'] = datetime.now().isoformat()
    
    def get_export_summary(self) -> Dict[str, Any]:
        """Get a summary of export operations."""
        return {
            "total_exports": len(self.export_history),
            "formats_used": list(set(exp.get('format') for exp in self.export_history)),
            "total_size": sum(exp.get('size', 0) for exp in self.export_history),
            "last_export": self.export_history[-1] if self.export_history else None
        } 