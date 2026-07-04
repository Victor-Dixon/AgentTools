#!/usr/bin/env python3
"""
Unified Export Center
Consolidates all export functionality across the GUI into a single, intelligent system.
Reduces 82 export buttons to a unified interface with format selection and history tracking.
"""

import json
import csv
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, 
    QLabel, QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QCheckBox, QSpinBox, QLineEdit, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon


class ExportFormat(Enum):
    """Supported export formats"""
    JSON = "json"
    CSV = "csv"
    TXT = "txt"
    MD = "markdown"
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"


@dataclass
class ExportRequest:
    """Represents an export request"""
    data_type: str
    format: ExportFormat
    destination: Path
    options: Dict[str, Any]
    timestamp: datetime
    status: str = "pending"


class ExportWorker(QThread):
    """Background worker for export operations"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    export_completed = pyqtSignal(bool, str)
    
    def __init__(self, export_request: ExportRequest, data: Any):
        super().__init__()
        self.export_request = export_request
        self.data = data
    
    def run(self):
        """Execute the export operation"""
        try:
            self.status_updated.emit("Starting export...")
            self.progress_updated.emit(10)
            
            # Determine export method based on format
            if self.export_request.format == ExportFormat.JSON:
                result = self._export_json()
            elif self.export_request.format == ExportFormat.CSV:
                result = self._export_csv()
            elif self.export_request.format == ExportFormat.TXT:
                result = self._export_txt()
            elif self.export_request.format == ExportFormat.MD:
                result = self._export_markdown()
            elif self.export_request.format == ExportFormat.HTML:
                result = self._export_html()
            else:
                raise ValueError(f"Unsupported format: {self.export_request.format}")
            
            self.progress_updated.emit(100)
            self.status_updated.emit("Export completed successfully!")
            self.export_completed.emit(True, str(self.export_request.destination))
            
        except Exception as e:
            self.status_updated.emit(f"Export failed: {str(e)}")
            self.export_completed.emit(False, str(e))
    
    def _export_json(self) -> bool:
        """Export data as JSON"""
        self.status_updated.emit("Exporting as JSON...")
        self.progress_updated.emit(30)
        
        with open(self.export_request.destination, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
        
        self.progress_updated.emit(80)
        return True
    
    def _export_csv(self) -> bool:
        """Export data as CSV"""
        self.status_updated.emit("Exporting as CSV...")
        self.progress_updated.emit(30)
        
        if isinstance(self.data, list) and self.data:
            # Handle list of dictionaries
            fieldnames = self.data[0].keys()
            with open(self.export_request.destination, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
        else:
            # Handle single dictionary or other data
            with open(self.export_request.destination, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if isinstance(self.data, dict):
                    for key, value in self.data.items():
                        writer.writerow([key, value])
                else:
                    writer.writerow([str(self.data)])
        
        self.progress_updated.emit(80)
        return True
    
    def _export_txt(self) -> bool:
        """Export data as plain text"""
        self.status_updated.emit("Exporting as text...")
        self.progress_updated.emit(30)
        
        with open(self.export_request.destination, 'w', encoding='utf-8') as f:
            if isinstance(self.data, dict):
                for key, value in self.data.items():
                    f.write(f"{key}: {value}\n")
            elif isinstance(self.data, list):
                for item in self.data:
                    f.write(f"{item}\n")
            else:
                f.write(str(self.data))
        
        self.progress_updated.emit(80)
        return True
    
    def _export_markdown(self) -> bool:
        """Export data as Markdown"""
        self.status_updated.emit("Exporting as Markdown...")
        self.progress_updated.emit(30)
        
        with open(self.export_request.destination, 'w', encoding='utf-8') as f:
            f.write(f"# {self.export_request.data_type.title()} Export\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if isinstance(self.data, dict):
                for key, value in self.data.items():
                    f.write(f"## {key}\n{value}\n\n")
            elif isinstance(self.data, list):
                for i, item in enumerate(self.data, 1):
                    f.write(f"### Item {i}\n{str(item)}\n\n")
            else:
                f.write(f"{str(self.data)}\n")
        
        self.progress_updated.emit(80)
        return True
    
    def _export_html(self) -> bool:
        """Export data as HTML"""
        self.status_updated.emit("Exporting as HTML...")
        self.progress_updated.emit(30)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.export_request.data_type.title()} Export</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .content {{ margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.export_request.data_type.title()} Export</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="content">
"""
        
        if isinstance(self.data, list) and self.data:
            html_content += "<table><thead><tr>"
            for key in self.data[0].keys():
                html_content += f"<th>{key}</th>"
            html_content += "</tr></thead><tbody>"
            
            for item in self.data:
                html_content += "<tr>"
                for value in item.values():
                    html_content += f"<td>{value}</td>"
                html_content += "</tr>"
            
            html_content += "</tbody></table>"
        else:
            html_content += f"<pre>{str(self.data)}</pre>"
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(self.export_request.destination, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.progress_updated.emit(80)
        return True


class UnifiedExportCenter(QWidget):
    """
    Unified Export Center - Consolidates all export functionality
    
    Replaces 82 individual export buttons with a single, intelligent interface
    that provides format selection, history tracking, and consistent UX.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.export_history: List[ExportRequest] = []
        self.current_worker: Optional[ExportWorker] = None
        self.export_dir = Path.home() / "Downloads" / "Dreamscape_Exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        self._setup_ui()
        self._load_export_history()
    
    def _setup_ui(self):
        """Setup the export center UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🚀 Unified Export Center")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Create tab widget for different export types
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add export tabs
        self._create_quick_export_tab()
        self._create_advanced_export_tab()
        self._create_history_tab()
        
        # Progress section
        self._create_progress_section(layout)
        
        self.setLayout(layout)
        self.setWindowTitle("Unified Export Center")
        self.resize(600, 500)
    
    def _create_quick_export_tab(self):
        """Create the quick export tab for common operations"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Data type selection
        data_group = QGroupBox("📊 Data to Export")
        data_layout = QVBoxLayout()
        
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems([
            "Conversations",
            "Analytics",
            "Templates", 
            "Memory Data",
            "MMORPG Progress",
            "Settings",
            "All Data"
        ])
        data_layout.addWidget(self.data_type_combo)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # Format selection
        format_group = QGroupBox("📄 Export Format")
        format_layout = QVBoxLayout()
        
        self.format_combo = QComboBox()
        for format_enum in ExportFormat:
            self.format_combo.addItem(format_enum.value.upper(), format_enum)
        format_layout.addWidget(self.format_combo)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Quick export button
        self.quick_export_btn = QPushButton("🚀 Quick Export")
        self.quick_export_btn.clicked.connect(self._quick_export)
        layout.addWidget(self.quick_export_btn)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Quick Export")
    
    def _create_advanced_export_tab(self):
        """Create the advanced export tab with detailed options"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Advanced options
        options_group = QGroupBox("⚙️ Export Options")
        options_layout = QVBoxLayout()
        
        # Include metadata
        self.include_metadata_cb = QCheckBox("Include metadata (timestamps, version info)")
        self.include_metadata_cb.setChecked(True)
        options_layout.addWidget(self.include_metadata_cb)
        
        # Pretty print
        self.pretty_print_cb = QCheckBox("Pretty print (formatted output)")
        self.pretty_print_cb.setChecked(True)
        options_layout.addWidget(self.pretty_print_cb)
        
        # Compression
        self.compress_cb = QCheckBox("Compress output (for large datasets)")
        options_layout.addWidget(self.compress_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Custom destination
        dest_group = QGroupBox("📁 Destination")
        dest_layout = QHBoxLayout()
        
        self.dest_path_edit = QLineEdit(str(self.export_dir))
        dest_layout.addWidget(self.dest_path_edit)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_destination)
        dest_layout.addWidget(self.browse_btn)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Advanced export button
        self.advanced_export_btn = QPushButton("🔧 Advanced Export")
        self.advanced_export_btn.clicked.connect(self._advanced_export)
        layout.addWidget(self.advanced_export_btn)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Advanced Export")
    
    def _create_history_tab(self):
        """Create the export history tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # History display
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
        # Clear history button
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Export History")
        
        self._update_history_display()
    
    def _create_progress_section(self, parent_layout):
        """Create the progress section"""
        progress_group = QGroupBox("📈 Export Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to export")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        parent_layout.addWidget(progress_group)
    
    def _quick_export(self):
        """Handle quick export"""
        data_type = self.data_type_combo.currentText()
        format_enum = self.format_combo.currentData()
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{data_type.lower().replace(' ', '_')}_{timestamp}.{format_enum.value}"
        destination = self.export_dir / filename
        
        # Get data based on type
        data = self._get_data_for_type(data_type)
        if data is None:
            QMessageBox.warning(self, "Export Error", f"No data available for {data_type}")
            return
        
        # Create export request
        request = ExportRequest(
            data_type=data_type,
            format=format_enum,
            destination=destination,
            options={"quick_export": True},
            timestamp=datetime.now()
        )
        
        self._execute_export(request, data)
    
    def _advanced_export(self):
        """Handle advanced export with custom options"""
        data_type = self.data_type_combo.currentText()
        format_enum = self.format_combo.currentData()
        
        # Get custom destination
        dest_path = Path(self.dest_path_edit.text())
        if not dest_path.exists():
            QMessageBox.warning(self, "Invalid Path", "Please select a valid destination directory")
            return
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{data_type.lower().replace(' ', '_')}_{timestamp}.{format_enum.value}"
        destination = dest_path / filename
        
        # Get data
        data = self._get_data_for_type(data_type)
        if data is None:
            QMessageBox.warning(self, "Export Error", f"No data available for {data_type}")
            return
        
        # Create options
        options = {
            "include_metadata": self.include_metadata_cb.isChecked(),
            "pretty_print": self.pretty_print_cb.isChecked(),
            "compress": self.compress_cb.isChecked(),
            "quick_export": False
        }
        
        # Create export request
        request = ExportRequest(
            data_type=data_type,
            format=format_enum,
            destination=destination,
            options=options,
            timestamp=datetime.now()
        )
        
        self._execute_export(request, data)
    
    def _get_data_for_type(self, data_type: str) -> Optional[Any]:
        """Get data for the specified type"""
        try:
            if data_type == "Conversations":
                return self._get_conversation_data()
            elif data_type == "Analytics":
                return self._get_analytics_data()
            elif data_type == "Templates":
                return self._get_template_data()
            elif data_type == "Memory Data":
                return self._get_memory_data()
            elif data_type == "MMORPG Progress":
                return self._get_mmorpg_data()
            elif data_type == "Settings":
                return self._get_settings_data()
            elif data_type == "All Data":
                return self._get_all_data()
            else:
                return None
        except Exception as e:
            print(f"Error getting data for {data_type}: {e}")
            return None
    
    def _get_conversation_data(self) -> Dict:
        """Get conversation data for export"""
        # This would integrate with your conversation storage
        return {
            "conversations": [],
            "total_count": 0,
            "export_timestamp": datetime.now().isoformat()
        }
    
    def _get_analytics_data(self) -> Dict:
        """Get analytics data for export"""
        return {
            "analytics": {},
            "metrics": {},
            "export_timestamp": datetime.now().isoformat()
        }
    
    def _get_template_data(self) -> Dict:
        """Get template data for export"""
        return {
            "templates": [],
            "categories": [],
            "export_timestamp": datetime.now().isoformat()
        }
    
    def _get_memory_data(self) -> Dict:
        """Get memory data for export"""
        return {
            "memory_entries": [],
            "total_entries": 0,
            "export_timestamp": datetime.now().isoformat()
        }
    
    def _get_mmorpg_data(self) -> Dict:
        """Get MMORPG data for export"""
        return {
            "character_progress": {},
            "skills": [],
            "achievements": [],
            "export_timestamp": datetime.now().isoformat()
        }
    
    def _get_settings_data(self) -> Dict:
        """Get settings data for export"""
        return {
            "application_settings": {},
            "user_preferences": {},
            "export_timestamp": datetime.now().isoformat()
        }
    
    def _get_all_data(self) -> Dict:
        """Get all data for export"""
        return {
            "conversations": self._get_conversation_data(),
            "analytics": self._get_analytics_data(),
            "templates": self._get_template_data(),
            "memory": self._get_memory_data(),
            "mmorpg": self._get_mmorpg_data(),
            "settings": self._get_settings_data(),
            "export_timestamp": datetime.now().isoformat()
        }
    
    def _execute_export(self, request: ExportRequest, data: Any):
        """Execute the export operation"""
        # Add to history
        self.export_history.append(request)
        self._save_export_history()
        self._update_history_display()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing export...")
        
        # Disable buttons during export
        self.quick_export_btn.setEnabled(False)
        self.advanced_export_btn.setEnabled(False)
        
        # Start export worker
        self.current_worker = ExportWorker(request, data)
        self.current_worker.progress_updated.connect(self.progress_bar.setValue)
        self.current_worker.status_updated.connect(self.status_label.setText)
        self.current_worker.export_completed.connect(self._on_export_completed)
        self.current_worker.start()
    
    def _on_export_completed(self, success: bool, result: str):
        """Handle export completion"""
        # Re-enable buttons
        self.quick_export_btn.setEnabled(True)
        self.advanced_export_btn.setEnabled(True)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Export Success", f"Data exported successfully to:\n{result}")
        else:
            QMessageBox.critical(self, "Export Failed", f"Export failed:\n{result}")
        
        # Update history
        if self.export_history:
            self.export_history[-1].status = "completed" if success else "failed"
            self._save_export_history()
            self._update_history_display()
    
    def _browse_destination(self):
        """Browse for export destination"""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if directory:
            self.dest_path_edit.setText(directory)
    
    def _clear_history(self):
        """Clear export history"""
        reply = QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to clear the export history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.export_history.clear()
            self._save_export_history()
            self._update_history_display()
    
    def _update_history_display(self):
        """Update the history display"""
        if not self.export_history:
            self.history_text.setText("No export history available")
            return
        
        history_text = "📋 Export History:\n\n"
        for i, request in enumerate(reversed(self.export_history[-20:]), 1):  # Show last 20
            status_icon = "✅" if request.status == "completed" else "❌" if request.status == "failed" else "⏳"
            history_text += f"{i}. {status_icon} {request.data_type} → {request.format.value.upper()}\n"
            history_text += f"   📁 {request.destination.name}\n"
            history_text += f"   🕒 {request.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        self.history_text.setText(history_text)
    
    def _save_export_history(self):
        """Save export history to file"""
        history_file = self.export_dir / "export_history.json"
        try:
            history_data = []
            for request in self.export_history:
                history_data.append({
                    "data_type": request.data_type,
                    "format": request.format.value,
                    "destination": str(request.destination),
                    "options": request.options,
                    "timestamp": request.timestamp.isoformat(),
                    "status": request.status
                })
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            print(f"Error saving export history: {e}")
    
    def _load_export_history(self):
        """Load export history from file"""
        history_file = self.export_dir / "export_history.json"
        if not history_file.exists():
            return
        
        try:
            with open(history_file, 'r') as f:
                history_data = json.load(f)
            
            for item in history_data:
                request = ExportRequest(
                    data_type=item["data_type"],
                    format=ExportFormat(item["format"]),
                    destination=Path(item["destination"]),
                    options=item["options"],
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    status=item.get("status", "unknown")
                )
                self.export_history.append(request)
        except Exception as e:
            print(f"Error loading export history: {e}")


def main():
    """Test the Unified Export Center"""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    export_center = UnifiedExportCenter()
    export_center.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 