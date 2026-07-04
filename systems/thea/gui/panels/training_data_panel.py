#!/usr/bin/env python3
from gui.debug_handler import debug_button
"""
Training Data Panel
==================

GUI panel for structured training data extraction with real-time progress monitoring.
"""

import json
from gui.debug_handler import debug_button
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel,
    QProgressBar, QTextEdit, QSpinBox, QCheckBox, QComboBox, QListWidget,
    QListWidgetItem, QGroupBox, QFormLayout, QLineEdit, QMessageBox,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.training_data_orchestrator import run_structured_training_data_extraction
from gui.components.shared_components import ComponentConfig, ComponentStyle

logger = logging.getLogger(__name__)

class TrainingDataWorker(QThread):
    """Background worker for training data extraction."""
    
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    extraction_completed = pyqtSignal(dict)  # results
    extraction_failed = pyqtSignal(str)  # error message
    
    def __init__(self, output_dir: str, max_conversations: Optional[int], 
                 conversation_ids: Optional[List[str]]):
        super().__init__()
        self.output_dir = output_dir
        self.max_conversations = max_conversations
        self.conversation_ids = conversation_ids
        
    def run(self):
        """Run the extraction process."""
        try:
            def progress_callback(current: int, total: int, message: str):
                self.progress_updated.emit(current, total, message)
            
            result = run_structured_training_data_extraction(
                output_dir=self.output_dir,
                max_conversations=self.max_conversations,
                conversation_ids=self.conversation_ids,
                progress_callback=progress_callback
            )
            
            if result.get("success"):
                self.extraction_completed.emit(result)
            else:
                self.extraction_failed.emit(result.get("error", "Unknown error"))
                
        except Exception as e:
            logger.error(f"Training data extraction failed: {e}")
            self.extraction_failed.emit(str(e))


class TrainingDataPanel(QWidget):
    """Main training data extraction panel."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.memory_manager = MemoryManager()
        self.worker = None
        self.extraction_results = {}
        
        self.init_ui()
        self.load_conversations()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_extraction_tab(), "🚀 Extraction")
        self.tab_widget.addTab(self.create_configuration_tab(), "⚙️ Configuration")
        self.tab_widget.addTab(self.create_results_tab(), "📊 Results")
        self.tab_widget.addTab(self.create_conversation_selection_tab(), "📋 Conversations")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    @debug_button("create_extraction_tab", "Training Data Panel")
    def create_extraction_tab(self) -> QWidget:
        """Create the extraction tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Status section
        status_group = QGroupBox("Extraction Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready to start extraction")
        self.status_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        status_group.setLayout(status_layout)
        
        # Control section
        control_group = QGroupBox("Extraction Controls")
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🚀 Start Extraction")
        self.start_button.clicked.connect(self.start_extraction)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        self.stop_button = QPushButton("⏹️ Stop Extraction")
        self.stop_button.clicked.connect(self.stop_extraction)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        
        # Log section
        log_group = QGroupBox("Extraction Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        # Add all sections to main layout
        layout.addWidget(status_group)
        layout.addWidget(control_group)
        layout.addWidget(log_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    @debug_button("create_configuration_tab", "Training Data Panel")
    def create_configuration_tab(self) -> QWidget:
        """Create the configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Output configuration
        output_group = QGroupBox("Output Configuration")
        output_layout = QFormLayout()
        
        self.output_dir_edit = QLineEdit("outputs/training_data/structured")
        self.output_dir_edit.setPlaceholderText("Enter output directory path")
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_directory)
        
        output_layout.addRow("Output Directory:", self.output_dir_edit)
        output_layout.addRow("", self.browse_button)
        output_group.setLayout(output_layout)
        
        # Processing configuration
        processing_group = QGroupBox("Processing Configuration")
        processing_layout = QFormLayout()
        
        self.max_conversations_spin = QSpinBox()
        self.max_conversations_spin.setRange(1, 10000)
        self.max_conversations_spin.setValue(50)
        self.max_conversations_spin.setSpecialValueText("All")
        
        self.use_selected_checkbox = QCheckBox("Use selected conversations only")
        self.use_selected_checkbox.setChecked(False)
        
        processing_layout.addRow("Max Conversations:", self.max_conversations_spin)
        processing_layout.addRow("", self.use_selected_checkbox)
        processing_group.setLayout(processing_layout)
        
        # Quality settings
        quality_group = QGroupBox("Quality Settings")
        quality_layout = QFormLayout()
        
        self.overwrite_checkbox = QCheckBox("Overwrite existing files")
        self.overwrite_checkbox.setChecked(False)
        
        self.validate_data_checkbox = QCheckBox("Validate extracted data")
        self.validate_data_checkbox.setChecked(True)
        
        quality_layout.addRow("", self.overwrite_checkbox)
        quality_layout.addRow("", self.validate_data_checkbox)
        quality_group.setLayout(quality_layout)
        
        # Add all groups to main layout
        layout.addWidget(output_group)
        layout.addWidget(processing_group)
        layout.addWidget(quality_group)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    @debug_button("create_results_tab", "Training Data Panel")
    def create_results_tab(self) -> QWidget:
        """Create the results tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary section using shared component
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        
        # Create summary table using shared component
        self.summary_table_group = components.create_data_table(
            title="Extraction Summary",
            headers=["Metric", "Value"],
            data=[],  # Will be populated later
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.summary_table = self.summary_table_group.table  # Access the table for updates
        
        # Create field analysis table using shared component
        self.field_table_group = components.create_data_table(
            title="Field Analysis",
            headers=["Field", "Present", "Percentage", "Sample"],
            data=[],  # Will be populated later
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.field_table = self.field_table_group.table  # Access the table for updates
        
        # Actions section using shared component
        actions = [
            {
                "text": "📁 View Output Directory",
                "callback": self.view_output_directory,
                "enabled": False,
                "id": "view_output"
            },
            {
                "text": "🚀 Export Center",
                "callback": self.show_unified_export_center,
                "enabled": False,
                "id": "export_center",
                "style": "success"
            }
        ]
        
        actions_group = components.create_action_panel(
            title="Actions",
            actions=actions,
            config=ComponentConfig(style=ComponentStyle.PRIMARY)
        )
        
        # Store action buttons for later access
        self.view_output_button = actions_group.findChild(QPushButton, "view_output")
        self.unified_export_btn = actions_group.findChild(QPushButton, "export_center")
        
        # Add all groups to main layout
        layout.addWidget(self.summary_table_group)
        layout.addWidget(self.field_table_group)
        layout.addWidget(actions_group)
        
        widget.setLayout(layout)
        return widget
        
    @debug_button("create_conversation_selection_tab", "Training Data Panel")
    def create_conversation_selection_tab(self) -> QWidget:
        """Create the conversation selection tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Selection controls using shared component
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        
        # Create action buttons using shared component
        selection_actions = [
            {
                "text": "Select All",
                "callback": self.select_all_conversations,
                "id": "select_all"
            },
            {
                "text": "Deselect All",
                "callback": self.deselect_all_conversations,
                "id": "deselect_all"
            }
        ]
        
        controls_group = components.create_action_panel(
            title="Selection Controls",
            actions=selection_actions,
            config=ComponentConfig(style=ComponentStyle.PRIMARY)
        )
        
        # Store action buttons for later access
        self.select_all_button = controls_group.findChild(QPushButton, "select_all")
        self.deselect_all_button = controls_group.findChild(QPushButton, "deselect_all")
        
        # Replace refresh button with Unified Load Button
        from gui.components.unified_load_button import create_unified_load_button
        self.unified_load_btn = create_unified_load_button(
            data_type="conversations",
            text="🔄 Load Conversations",
            priority="NORMAL",
            use_cache=True,
            background_load=True,
            parent=self
        )
        
        # Connect load completion to refresh the panel
        self.unified_load_btn.load_completed.connect(self.on_conversations_loaded)
        
        # Add load button to controls
        controls_layout = controls_group.layout()
        controls_layout.addWidget(self.unified_load_btn)
        
        # Create conversation list using shared component
        self.conversation_list_group = components.create_data_list(
            title="Conversations",
            items=[],  # Will be populated later
            selection_mode=QListWidget.SelectionMode.MultiSelection,
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.conversation_list = self.conversation_list_group.findChild(QListWidget)
        
        # Status section using shared component
        self.status_group = components.create_status_section(
            title="Status",
            show_icon=True,
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.conversation_count_label = self.status_group.findChild(QLabel)
        
        # Add all groups to main layout
        layout.addWidget(controls_group)
        layout.addWidget(self.conversation_list_group)
        layout.addWidget(self.status_group)
        
        widget.setLayout(layout)
        return widget
        
    @debug_button("load_conversations", "Training Data Panel")
    def load_conversations(self):
        """Load conversations from memory manager."""
        try:
            conversations = self.memory_manager.get_conversations()
            
            self.conversation_list.clear()
            for conversation in conversations:
                title = conversation.get('title', 'Untitled')
                conv_id = conversation.get('id', 'unknown')
                item_text = f"{title} (ID: {conv_id})"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, conv_id)
                self.conversation_list.addItem(item)
            
            self.conversation_count_label.setText(f"Loaded {len(conversations)} conversations")
            self.log_message(f"Loaded {len(conversations)} conversations from memory")
            
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            self.log_message(f"Error loading conversations: {e}")
            
    @debug_button("start_extraction", "Training Data Panel")
    def start_extraction(self):
        """Start the extraction process."""
        try:
            # Get configuration
            output_dir = self.output_dir_edit.text().strip()
            max_conversations = self.max_conversations_spin.value()
            use_selected = self.use_selected_checkbox.isChecked()
            
            # Get selected conversation IDs if using selection
            conversation_ids = None
            if use_selected:
                selected_items = self.conversation_list.selectedItems()
                if not selected_items:
                    QMessageBox.warning(self, "No Selection", "Please select conversations to process.")
                    return
                conversation_ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
                max_conversations = None  # Override max when using selection
            
            # Validate output directory
            if not output_dir:
                QMessageBox.warning(self, "Invalid Output", "Please specify an output directory.")
                return
            
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Start worker
            self.worker = TrainingDataWorker(output_dir, max_conversations, conversation_ids)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.extraction_completed.connect(self.extraction_completed)
            self.worker.extraction_failed.connect(self.extraction_failed)
            
            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.status_label.setText("Extraction in progress...")
            self.status_label.setStyleSheet("font-weight: bold; color: #FF8C00;")
            
            self.log_message("Starting structured training data extraction...")
            
            # Start the worker
            self.worker.start()
            
        except Exception as e:
            logger.error(f"Error starting extraction: {e}")
            self.log_message(f"Error starting extraction: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start extraction: {e}")
            
    @debug_button("stop_extraction", "Training Data Panel")
    def stop_extraction(self):
        """Stop the extraction process."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Extraction stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: #DC143C;")
        
        self.log_message("Extraction stopped by user")
        
    @debug_button("update_progress", "Training Data Panel")
    def update_progress(self, current: int, total: int, message: str):
        """Update progress bar and log."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.log_message(f"Progress: {current}/{total} - {message}")
        
    @debug_button("extraction_completed", "Training Data Panel")
    def extraction_completed(self, results: Dict[str, Any]):
        """Handle extraction completion."""
        self.extraction_results = results
        
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Extraction completed successfully!")
        self.status_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        
        # Update results tab
        self.update_results_display(results)
        
        # Enable action buttons
        self.view_output_button.setEnabled(True)
        self.unified_export_btn.setEnabled(True)
        
        # Log completion
        stats = results.get("statistics", {})
        summary = stats.get("extraction_summary", {})
        self.log_message(f"Extraction completed!")
        self.log_message(f"   Success: {summary.get('successful_extractions', 0)}/{summary.get('total_conversations', 0)}")
        self.log_message(f"   Time: {summary.get('extraction_time_seconds', 0):.2f}s")
        
        # Switch to results tab
        self.tab_widget.setCurrentIndex(2)
        
    @debug_button("extraction_failed", "Training Data Panel")
    def extraction_failed(self, error_message: str):
        """Handle extraction failure."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Extraction failed")
        self.status_label.setStyleSheet("font-weight: bold; color: #DC143C;")
        
        self.log_message(f"Extraction failed: {error_message}")
        QMessageBox.critical(self, "Extraction Failed", f"Extraction failed: {error_message}")
        
    @debug_button("update_results_display", "Training Data Panel")
    def update_results_display(self, results: Dict[str, Any]):
        """Update the results display with extraction statistics."""
        stats = results.get("statistics", {})
        summary = stats.get("extraction_summary", {})
        field_analysis = stats.get("field_analysis", {})
        
        # Update summary table
        self.summary_table.setRowCount(6)
        summary_data = [
            ("Total Conversations", str(summary.get("total_conversations", 0))),
            ("Successful Extractions", str(summary.get("successful_extractions", 0))),
            ("Failed Extractions", str(summary.get("failed_extractions", 0))),
            ("Success Rate", f"{summary.get('success_rate_percentage', 0):.1f}%"),
            ("Extraction Time", f"{summary.get('extraction_time_seconds', 0):.2f}s"),
            ("Output Directory", results.get("output_directory", "Unknown"))
        ]
        
        for i, (metric, value) in enumerate(summary_data):
            self.summary_table.setItem(i, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(i, 1, QTableWidgetItem(value))
        
        # Update field analysis table
        self.field_table.setRowCount(len(field_analysis))
        for i, (field, analysis) in enumerate(field_analysis.items()):
            self.field_table.setItem(i, 0, QTableWidgetItem(field))
            self.field_table.setItem(i, 1, QTableWidgetItem(str(analysis.get("present_count", 0))))
            self.field_table.setItem(i, 2, QTableWidgetItem(f"{analysis.get('present_percentage', 0):.1f}%"))
            
            sample_values = analysis.get("sample_values", [])
            sample_text = ", ".join(str(v)[:20] for v in sample_values[:2])
            if len(sample_values) > 2:
                sample_text += "..."
            self.field_table.setItem(i, 3, QTableWidgetItem(sample_text))
        
    @debug_button("select_all_conversations", "Training Data Panel")
    def select_all_conversations(self):
        """Select all conversations in the list."""
        for i in range(self.conversation_list.count()):
            self.conversation_list.item(i).setSelected(True)
            
    @debug_button("deselect_all_conversations", "Training Data Panel")
    def deselect_all_conversations(self):
        """Deselect all conversations in the list."""
        self.conversation_list.clearSelection()
        
    @debug_button("browse_output_directory", "Training Data Panel")
    def browse_output_directory(self):
        """Browse for output directory."""
        from PyQt6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)
            
    @debug_button("view_output_directory", "Training Data Panel")
    def view_output_directory(self):
        """Open the output directory in file explorer."""
        if self.extraction_results:
            output_dir = self.extraction_results.get("output_directory")
            if output_dir and os.path.exists(output_dir):
                os.startfile(output_dir)  # Windows
            else:
                QMessageBox.warning(self, "Directory Not Found", "Output directory not found.")
                
    def show_unified_export_center(self):
        """Show the Unified Export Center for training data results."""
        try:
            # Prepare training data results for export
            export_data = {
                "extraction_results": self.extraction_results if hasattr(self, 'extraction_results') else {},
                "configuration": self._get_configuration_data(),
                "conversation_data": self._get_conversation_data(),
                "output_files": self._get_output_files_data(),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Create and show Unified Export Center
            from gui.components.unified_export_center import UnifiedExportCenter
            export_center = UnifiedExportCenter()
            
            # Override the data getter to return our training data
            export_center._get_data_for_type = lambda data_type: export_data
            
            export_center.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to open export center: {e}")
    
    def on_conversations_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle conversations load completion."""
        if success and data_type == "conversations":
            # Refresh the conversations display
            self.load_conversations()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load conversations: {message}")
    
    def _get_configuration_data(self):
        """Get configuration data for export."""
        try:
            return {
                "output_directory": self.output_dir_edit.text() if hasattr(self, 'output_dir_edit') else "",
                "max_conversations": self.max_conversations_spin.value() if hasattr(self, 'max_conversations_spin') else 0,
                "use_selected": self.use_selected_checkbox.isChecked() if hasattr(self, 'use_selected_checkbox') else False,
                "export_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"configuration": {}, "error": f"Failed to load configuration: {e}"}
    
    def _get_conversation_data(self):
        """Get conversation data for export."""
        try:
            if hasattr(self, 'conversation_list'):
                selected_items = self.conversation_list.selectedItems()
                conversations = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
                return {
                    "selected_conversations": conversations,
                    "total_selected": len(conversations),
                    "export_timestamp": datetime.now().isoformat()
                }
            else:
                return {"conversations": [], "error": "Conversation list not available"}
        except Exception as e:
            return {"conversations": [], "error": f"Failed to load conversation data: {e}"}
    
    def _get_output_files_data(self):
        """Get output files data for export."""
        try:
            output_dir = self.output_dir_edit.text() if hasattr(self, 'output_dir_edit') else ""
            if output_dir:
                from pathlib import Path
                output_path = Path(output_dir)
                if output_path.exists():
                    files = list(output_path.glob("*"))
                    return {
                        "output_directory": str(output_path),
                        "files": [str(f) for f in files],
                        "total_files": len(files),
                        "export_timestamp": datetime.now().isoformat()
                    }
            return {"output_files": [], "error": "Output directory not available"}
        except Exception as e:
            return {"output_files": [], "error": f"Failed to load output files: {e}"}
        
    def log_message(self, message: str):
        """Add a message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum()) 