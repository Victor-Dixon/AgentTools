#!/usr/bin/env python3
"""
Training Data Component
======================

This component handles training data functionality including:
- Data extraction
- Data management
- Export functionality
- Data analysis
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import csv

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QComboBox, QGroupBox, QGridLayout,
    QCheckBox, QProgressBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from gui.debug_handler import debug_button

logger = logging.getLogger(__name__)

class TrainingDataComponent(QWidget):
    """Training Data component for data extraction and management."""
    
    # Signals
    data_extracted = pyqtSignal(dict)  # Data extraction results
    data_exported = pyqtSignal(str)    # Data export completed
    
    def __init__(self, memory_manager: MemoryManager = None, mmorpg_engine: MMORPGEngine = None):
        super().__init__()
        self.memory_manager = memory_manager or MemoryManager()
        self.mmorpg_engine = mmorpg_engine or MMORPGEngine()
        
        # UI Components
        self.extract_conversations_cb = None
        self.extract_templates_cb = None
        self.extract_analytics_cb = None
        self.extract_mmorpg_cb = None
        self.extract_btn = None
        self.export_btn = None
        self.data_display = None
        self.extraction_progress = None
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the training data user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("📊 Training Data - Extract and Manage Training Data")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Data extraction
        extraction_group = QGroupBox("Data Extraction")
        extraction_layout = QVBoxLayout(extraction_group)
        
        # Extraction options
        options_layout = QGridLayout()
        
        self.extract_conversations_cb = QCheckBox("Extract Conversations")
        self.extract_conversations_cb.setChecked(True)
        options_layout.addWidget(self.extract_conversations_cb, 0, 0)
        
        self.extract_templates_cb = QCheckBox("Extract Templates")
        self.extract_templates_cb.setChecked(True)
        options_layout.addWidget(self.extract_templates_cb, 0, 1)
        
        self.extract_analytics_cb = QCheckBox("Extract Analytics")
        self.extract_analytics_cb.setChecked(False)
        options_layout.addWidget(self.extract_analytics_cb, 1, 0)
        
        self.extract_mmorpg_cb = QCheckBox("Extract MMORPG Data")
        self.extract_mmorpg_cb.setChecked(False)
        options_layout.addWidget(self.extract_mmorpg_cb, 1, 1)
        
        extraction_layout.addLayout(options_layout)
        
        # Extraction controls
        controls_layout = QHBoxLayout()
        self.extract_btn = QPushButton("🔍 Extract Training Data")
        controls_layout.addWidget(self.extract_btn)
        
        self.export_btn = QPushButton("📤 Export Data")
        self.export_btn.setEnabled(False)
        controls_layout.addWidget(self.export_btn)
        
        extraction_layout.addLayout(controls_layout)
        
        # Progress bar
        self.extraction_progress = QProgressBar()
        self.extraction_progress.setVisible(False)
        extraction_layout.addWidget(self.extraction_progress)
        
        layout.addWidget(extraction_group)
        
        # Data display
        data_group = QGroupBox("Extracted Data")
        data_layout = QVBoxLayout(data_group)
        
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setPlaceholderText("Extracted data will appear here...")
        data_layout.addWidget(self.data_display)
        
        layout.addWidget(data_group)
        layout.addStretch()
    
    def connect_signals(self):
        """Connect all signals and slots."""
        self.extract_btn.clicked.connect(self.extract_training_data)
        self.export_btn.clicked.connect(self.export_training_data)
    
    @debug_button("extract_training_data", "Training Data Component")
    def extract_training_data(self):
        """Extract training data based on selected options."""
        # Get selected extraction options
        options = {
            'conversations': self.extract_conversations_cb.isChecked(),
            'templates': self.extract_templates_cb.isChecked(),
            'analytics': self.extract_analytics_cb.isChecked(),
            'mmorpg': self.extract_mmorpg_cb.isChecked()
        }
        
        if not any(options.values()):
            QMessageBox.warning(self, "Warning", "Please select at least one data source to extract.")
            return
        
        # Disable extract button during processing
        self.extract_btn.setEnabled(False)
        self.extract_btn.setText("Extracting...")
        self.extraction_progress.setVisible(True)
        self.extraction_progress.setValue(0)
        
        try:
            # Simulate data extraction
            extraction_data = self.simulate_data_extraction(options)
            
            # Display results
            self.display_extraction_results(extraction_data)
            
            # Enable export button
            self.export_btn.setEnabled(True)
            
            # Emit data extracted signal
            self.data_extracted.emit(extraction_data)
            
            logger.info(f"Extracted training data: {extraction_data.get('total_records', 0)} records")
            
        except Exception as e:
            error_msg = f"Error extracting data: {str(e)}"
            self.data_display.setPlainText(error_msg)
            logger.error(error_msg)
        
        finally:
            # Re-enable extract button
            self.extract_btn.setEnabled(True)
            self.extract_btn.setText("🔍 Extract Training Data")
            self.extraction_progress.setVisible(False)
    
    def simulate_data_extraction(self, options: Dict[str, bool]) -> Dict[str, Any]:
        """Simulate data extraction for demonstration."""
        extraction_data = {
            'timestamp': datetime.now().isoformat(),
            'options': options,
            'data': {},
            'total_records': 0,
            'summary': {}
        }
        
        # Simulate conversation extraction
        if options['conversations']:
            conversations = [
                {'id': 'conv_1', 'title': 'Code Review Discussion', 'messages': 15, 'date': '2024-01-15'},
                {'id': 'conv_2', 'title': 'Architecture Planning', 'messages': 23, 'date': '2024-01-14'},
                {'id': 'conv_3', 'title': 'Bug Fix Discussion', 'messages': 8, 'date': '2024-01-13'}
            ]
            extraction_data['data']['conversations'] = conversations
            extraction_data['summary']['conversations'] = len(conversations)
            extraction_data['total_records'] += len(conversations)
        
        # Simulate template extraction
        if options['templates']:
            templates = [
                {'id': 'template_1', 'name': 'Code Review Template', 'type': 'review', 'usage_count': 45},
                {'id': 'template_2', 'name': 'Bug Report Template', 'type': 'bug_report', 'usage_count': 23},
                {'id': 'template_3', 'name': 'Feature Request Template', 'type': 'feature', 'usage_count': 12}
            ]
            extraction_data['data']['templates'] = templates
            extraction_data['summary']['templates'] = len(templates)
            extraction_data['total_records'] += len(templates)
        
        # Simulate analytics extraction
        if options['analytics']:
            analytics = [
                {'metric': 'code_quality_score', 'value': 85.2, 'trend': 'improving'},
                {'metric': 'bug_frequency', 'value': 2.1, 'trend': 'decreasing'},
                {'metric': 'development_velocity', 'value': 12.5, 'trend': 'stable'}
            ]
            extraction_data['data']['analytics'] = analytics
            extraction_data['summary']['analytics'] = len(analytics)
            extraction_data['total_records'] += len(analytics)
        
        # Simulate MMORPG data extraction
        if options['mmorpg']:
            mmorpg_data = [
                {'player_id': 'player_1', 'level': 25, 'experience': 15000, 'skills': ['coding', 'debugging']},
                {'player_id': 'player_2', 'level': 18, 'experience': 8500, 'skills': ['testing', 'documentation']},
                {'player_id': 'player_3', 'level': 32, 'experience': 28000, 'skills': ['architecture', 'optimization']}
            ]
            extraction_data['data']['mmorpg'] = mmorpg_data
            extraction_data['summary']['mmorpg'] = len(mmorpg_data)
            extraction_data['total_records'] += len(mmorpg_data)
        
        return extraction_data
    
    def display_extraction_results(self, extraction_data: Dict[str, Any]):
        """Display extraction results in the data display."""
        summary = extraction_data.get('summary', {})
        total_records = extraction_data.get('total_records', 0)
        
        result_text = f"""=== Data Extraction Results ===
Timestamp: {extraction_data.get('timestamp', 'Unknown')}
Total Records: {total_records}

=== Extraction Summary ===
"""
        
        for data_type, count in summary.items():
            result_text += f"• {data_type.title()}: {count} records\n"
        
        result_text += f"""
=== Data Preview ===
"""
        
        # Show preview of each data type
        for data_type, data in extraction_data.get('data', {}).items():
            if data:
                result_text += f"\n{data_type.title()}:\n"
                for i, item in enumerate(data[:3]):  # Show first 3 items
                    result_text += f"  {i+1}. {str(item)[:100]}...\n"
                if len(data) > 3:
                    result_text += f"  ... and {len(data) - 3} more records\n"
        
        result_text += f"""
=== Next Steps ===
1. Review the extracted data above
2. Export data if needed
3. Use data for model training
4. Clean and preprocess data as required"""
        
        self.data_display.setPlainText(result_text)
    
    @debug_button("export_training_data", "Training Data Component")
    def export_training_data(self):
        """Export the extracted training data."""
        if not self.data_display.toPlainText().strip():
            QMessageBox.warning(self, "Warning", "No data to export. Please extract data first.")
            return
        
        # Get export file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Training Data",
            f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Export data based on file extension
            if file_path.endswith('.json'):
                self.export_as_json(file_path)
            elif file_path.endswith('.csv'):
                self.export_as_csv(file_path)
            else:
                self.export_as_json(file_path)
            
            QMessageBox.information(self, "Success", f"Data exported successfully to:\n{file_path}")
            self.data_exported.emit(file_path)
            
            logger.info(f"Training data exported to: {file_path}")
            
        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            logger.error(error_msg)
    
    def export_as_json(self, file_path: str):
        """Export data as JSON."""
        # This would export the actual extraction data
        # For now, we'll export a sample structure
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'data_type': 'training_data',
            'records': 15,  # Sample count
            'format': 'json'
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def export_as_csv(self, file_path: str):
        """Export data as CSV."""
        # This would export the actual extraction data
        # For now, we'll export a sample structure
        sample_data = [
            ['record_id', 'data_type', 'content', 'timestamp'],
            ['1', 'conversation', 'Code review discussion', datetime.now().isoformat()],
            ['2', 'template', 'Bug report template', datetime.now().isoformat()],
            ['3', 'analytics', 'Code quality metric', datetime.now().isoformat()]
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(sample_data)
    
    def get_extraction_options(self) -> Dict[str, bool]:
        """Get current extraction options."""
        return {
            'conversations': self.extract_conversations_cb.isChecked(),
            'templates': self.extract_templates_cb.isChecked(),
            'analytics': self.extract_analytics_cb.isChecked(),
            'mmorpg': self.extract_mmorpg_cb.isChecked()
        }
    
    def set_extraction_options(self, options: Dict[str, bool]):
        """Set extraction options."""
        if 'conversations' in options:
            self.extract_conversations_cb.setChecked(options['conversations'])
        if 'templates' in options:
            self.extract_templates_cb.setChecked(options['templates'])
        if 'analytics' in options:
            self.extract_analytics_cb.setChecked(options['analytics'])
        if 'mmorpg' in options:
            self.extract_mmorpg_cb.setChecked(options['mmorpg'])
    
    def clear_data_display(self):
        """Clear the data display."""
        self.data_display.clear()
        self.export_btn.setEnabled(False)
    
    def get_extracted_data_text(self) -> str:
        """Get the current extracted data as text."""
        return self.data_display.toPlainText()
    
    def is_data_available(self) -> bool:
        """Check if extracted data is available for export."""
        return bool(self.data_display.toPlainText().strip()) and self.export_btn.isEnabled()
    
    def disable_extraction(self):
        """Disable extraction during processing."""
        self.extract_btn.setEnabled(False)
        self.extract_conversations_cb.setEnabled(False)
        self.extract_templates_cb.setEnabled(False)
        self.extract_analytics_cb.setEnabled(False)
        self.extract_mmorpg_cb.setEnabled(False)
    
    def enable_extraction(self):
        """Enable extraction after processing."""
        self.extract_btn.setEnabled(True)
        self.extract_conversations_cb.setEnabled(True)
        self.extract_templates_cb.setEnabled(True)
        self.extract_analytics_cb.setEnabled(True)
        self.extract_mmorpg_cb.setEnabled(True) 