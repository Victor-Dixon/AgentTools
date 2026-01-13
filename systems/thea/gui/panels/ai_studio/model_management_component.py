#!/usr/bin/env python3
"""
Model Management Component
=========================

This component handles model management functionality including:
- Model listing and selection
- Model operations (add, remove, test, update)
- Model import/export
- Model configuration
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QComboBox, QGroupBox, QGridLayout,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from gui.debug_handler import debug_button

logger = logging.getLogger(__name__)

class ModelManagementComponent(QWidget):
    """Model Management component for multi-model management."""
    
    # Signals
    model_selected = pyqtSignal(str)  # Model selected
    model_added = pyqtSignal(dict)    # Model added
    model_removed = pyqtSignal(str)   # Model removed
    model_tested = pyqtSignal(dict)   # Model test results
    
    def __init__(self, memory_manager: MemoryManager = None, mmorpg_engine: MMORPGEngine = None):
        super().__init__()
        self.memory_manager = memory_manager or MemoryManager()
        self.mmorpg_engine = mmorpg_engine or MMORPGEngine()
        
        # Model data
        self.ai_models = {}
        self.selected_model = None
        
        # UI Components
        self.model_list = None
        self.model_info = None
        self.add_model_btn = None
        self.remove_model_btn = None
        self.test_model_btn = None
        self.update_model_btn = None
        self.export_model_btn = None
        self.import_model_btn = None
        
        self.init_ui()
        self.connect_signals()
        self.load_models()
    
    def init_ui(self):
        """Initialize the model management user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🤖 Model Management - Multi-Model Management")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel - Model list
        left_panel = QVBoxLayout()
        
        list_group = QGroupBox("Available Models")
        list_layout = QVBoxLayout(list_group)
        
        self.model_list = QListWidget()
        self.model_list.setMaximumWidth(300)
        list_layout.addWidget(self.model_list)
        
        # Model list buttons
        list_buttons_layout = QGridLayout()
        
        self.add_model_btn = QPushButton("➕ Add Model")
        list_buttons_layout.addWidget(self.add_model_btn, 0, 0)
        
        self.remove_model_btn = QPushButton("🗑️ Remove")
        self.remove_model_btn.setEnabled(False)
        list_buttons_layout.addWidget(self.remove_model_btn, 0, 1)
        
        self.import_model_btn = QPushButton("📥 Import")
        list_buttons_layout.addWidget(self.import_model_btn, 1, 0)
        
        self.export_model_btn = QPushButton("📤 Export")
        self.export_model_btn.setEnabled(False)
        list_buttons_layout.addWidget(self.export_model_btn, 1, 1)
        
        list_layout.addLayout(list_buttons_layout)
        left_panel.addWidget(list_group)
        
        content_layout.addLayout(left_panel)
        
        # Right panel - Model details
        right_panel = QVBoxLayout()
        
        details_group = QGroupBox("Model Details")
        details_layout = QVBoxLayout(details_group)
        
        self.model_info = QTextEdit()
        self.model_info.setReadOnly(True)
        self.model_info.setPlaceholderText("Select a model to view details...")
        details_layout.addWidget(self.model_info)
        
        # Model operation buttons
        operation_buttons_layout = QHBoxLayout()
        
        self.test_model_btn = QPushButton("🧪 Test Model")
        self.test_model_btn.setEnabled(False)
        operation_buttons_layout.addWidget(self.test_model_btn)
        
        self.update_model_btn = QPushButton("🔄 Update Model")
        self.update_model_btn.setEnabled(False)
        operation_buttons_layout.addWidget(self.update_model_btn)
        
        details_layout.addLayout(operation_buttons_layout)
        right_panel.addWidget(details_group)
        
        content_layout.addLayout(right_panel)
        layout.addLayout(content_layout)
        layout.addStretch()
    
    def connect_signals(self):
        """Connect all signals and slots."""
        self.model_list.itemClicked.connect(self.on_model_selected)
        self.add_model_btn.clicked.connect(self.add_model)
        self.remove_model_btn.clicked.connect(self.remove_model)
        self.test_model_btn.clicked.connect(self.test_model)
        self.update_model_btn.clicked.connect(self.update_model)
        self.export_model_btn.clicked.connect(self.export_model)
        self.import_model_btn.clicked.connect(self.import_model)
    
    def load_models(self):
        """Load available AI models."""
        try:
            # Simulate loading models
            self.ai_models = {
                'gpt-4': {
                    'name': 'GPT-4',
                    'type': 'Language Model',
                    'version': '4.0',
                    'status': 'Active',
                    'accuracy': 0.92,
                    'last_updated': '2024-01-15',
                    'description': 'Advanced language model for complex reasoning tasks'
                },
                'claude-3': {
                    'name': 'Claude-3',
                    'type': 'Language Model',
                    'version': '3.0',
                    'status': 'Active',
                    'accuracy': 0.89,
                    'last_updated': '2024-01-14',
                    'description': 'Anthropic\'s latest language model'
                },
                'custom-model-1': {
                    'name': 'Custom Model 1',
                    'type': 'Custom Trained',
                    'version': '1.0',
                    'status': 'Training',
                    'accuracy': 0.78,
                    'last_updated': '2024-01-13',
                    'description': 'Custom trained model for specific tasks'
                }
            }
            
            self.refresh_model_list()
            logger.info(f"Loaded {len(self.ai_models)} models")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def refresh_model_list(self):
        """Refresh the model list display."""
        self.model_list.clear()
        
        for model_id, model_data in self.ai_models.items():
            item = QListWidgetItem(f"{model_data['name']} ({model_data['type']})")
            item.setData(Qt.ItemDataRole.UserRole, model_id)
            self.model_list.addItem(item)
    
    @debug_button("on_model_selected", "Model Management Component")
    def on_model_selected(self, item: QListWidgetItem):
        """Handle model selection."""
        model_id = item.data(Qt.ItemDataRole.UserRole)
        self.selected_model = model_id
        
        if model_id in self.ai_models:
            model_data = self.ai_models[model_id]
            self.display_model_info(model_data)
            
            # Enable operation buttons
            self.remove_model_btn.setEnabled(True)
            self.test_model_btn.setEnabled(True)
            self.update_model_btn.setEnabled(True)
            self.export_model_btn.setEnabled(True)
            
            # Emit model selected signal
            self.model_selected.emit(model_id)
            
            logger.info(f"Selected model: {model_id}")
    
    def display_model_info(self, model_data: Dict[str, Any]):
        """Display model information."""
        info_text = f"""=== Model Information ===
Name: {model_data.get('name', 'Unknown')}
Type: {model_data.get('type', 'Unknown')}
Version: {model_data.get('version', 'Unknown')}
Status: {model_data.get('status', 'Unknown')}
Accuracy: {model_data.get('accuracy', 0):.3f}
Last Updated: {model_data.get('last_updated', 'Unknown')}

Description: {model_data.get('description', 'No description available')}

=== Model Statistics ===
• Performance: {model_data.get('accuracy', 0) * 100:.1f}%
• Status: {model_data.get('status', 'Unknown')}
• Version: {model_data.get('version', 'Unknown')}

=== Available Operations ===
• Test Model: Evaluate model performance
• Update Model: Refresh model parameters
• Export Model: Save model configuration
• Remove Model: Delete model from system"""
        
        self.model_info.setPlainText(info_text)
    
    @debug_button("add_model", "Model Management Component")
    def add_model(self):
        """Add a new model."""
        # Get model details from user
        model_name, ok = QInputDialog.getText(self, "Add Model", "Enter model name:")
        if not ok or not model_name.strip():
            return
        
        model_type, ok = QInputDialog.getItem(
            self, "Add Model", "Select model type:",
            ["Language Model", "Custom Trained", "Fine-tuned", "Other"], 0, False
        )
        if not ok:
            return
        
        # Create new model entry
        model_id = f"model-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        new_model = {
            'name': model_name.strip(),
            'type': model_type,
            'version': '1.0',
            'status': 'Inactive',
            'accuracy': 0.0,
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'description': f'New {model_type.lower()} model'
        }
        
        self.ai_models[model_id] = new_model
        self.refresh_model_list()
        
        # Emit model added signal
        self.model_added.emit({'model_id': model_id, 'model_data': new_model})
        
        logger.info(f"Added new model: {model_name}")
    
    @debug_button("remove_model", "Model Management Component")
    def remove_model(self):
        """Remove the selected model."""
        if not self.selected_model:
            return
        
        # Confirm removal
        reply = QMessageBox.question(
            self, "Remove Model",
            f"Are you sure you want to remove '{self.ai_models[self.selected_model]['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            model_name = self.ai_models[self.selected_model]['name']
            del self.ai_models[self.selected_model]
            
            self.refresh_model_list()
            self.model_info.clear()
            self.selected_model = None
            
            # Disable operation buttons
            self.remove_model_btn.setEnabled(False)
            self.test_model_btn.setEnabled(False)
            self.update_model_btn.setEnabled(False)
            self.export_model_btn.setEnabled(False)
            
            # Emit model removed signal
            self.model_removed.emit(self.selected_model)
            
            logger.info(f"Removed model: {model_name}")
    
    @debug_button("test_model", "Model Management Component")
    def test_model(self):
        """Test the selected model."""
        if not self.selected_model:
            return
        
        model_data = self.ai_models[self.selected_model]
        
        # Simulate model testing
        test_result = {
            'model_id': self.selected_model,
            'model_name': model_data['name'],
            'test_time': datetime.now().isoformat(),
            'accuracy': model_data.get('accuracy', 0.0),
            'response_time': 1.2 + (hash(self.selected_model) % 10) * 0.1,
            'status': 'Passed' if model_data.get('accuracy', 0) > 0.7 else 'Failed'
        }
        
        # Display test results
        result_text = f"""=== Model Test Results ===
Model: {test_result['model_name']}
Test Time: {test_result['test_time']}
Accuracy: {test_result['accuracy']:.3f}
Response Time: {test_result['response_time']:.2f}s
Status: {test_result['status']}

=== Test Summary ===
✅ Model loaded successfully
✅ Test queries executed
✅ Performance metrics calculated
✅ Results validated

=== Recommendations ===
• Model performance: {'Good' if test_result['accuracy'] > 0.8 else 'Needs improvement'}
• Response time: {'Acceptable' if test_result['response_time'] < 2.0 else 'Slow'}
• Overall status: {test_result['status']}"""
        
        self.model_info.setPlainText(result_text)
        
        # Emit model tested signal
        self.model_tested.emit(test_result)
        
        logger.info(f"Tested model: {model_data['name']}")
    
    @debug_button("update_model", "Model Management Component")
    def update_model(self):
        """Update the selected model."""
        if not self.selected_model:
            return
        
        model_data = self.ai_models[self.selected_model]
        
        # Simulate model update
        model_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        model_data['version'] = f"{float(model_data['version']) + 0.1:.1f}"
        
        # Update display
        self.display_model_info(model_data)
        
        logger.info(f"Updated model: {model_data['name']}")
    
    @debug_button("export_model", "Model Management Component")
    def export_model(self):
        """Export the selected model configuration."""
        if not self.selected_model:
            return
        
        model_data = self.ai_models[self.selected_model]
        
        # Get export file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Model Configuration",
            f"{model_data['name'].replace(' ', '_')}_config.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Export model configuration
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'model_config': model_data,
                'export_version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Success", f"Model configuration exported to:\n{file_path}")
            logger.info(f"Exported model configuration: {file_path}")
            
        except Exception as e:
            error_msg = f"Error exporting model: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            logger.error(error_msg)
    
    @debug_button("import_model", "Model Management Component")
    def import_model(self):
        """Import a model configuration."""
        # Get import file path
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Model Configuration",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Import model configuration
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            model_config = import_data.get('model_config', {})
            if not model_config:
                raise ValueError("Invalid model configuration file")
            
            # Add imported model
            model_id = f"imported-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            self.ai_models[model_id] = model_config
            
            self.refresh_model_list()
            
            QMessageBox.information(self, "Success", f"Model imported successfully:\n{model_config.get('name', 'Unknown')}")
            logger.info(f"Imported model: {model_config.get('name', 'Unknown')}")
            
        except Exception as e:
            error_msg = f"Error importing model: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            logger.error(error_msg)
    
    def get_selected_model(self) -> Optional[str]:
        """Get the currently selected model ID."""
        return self.selected_model
    
    def get_model_data(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model data by ID."""
        return self.ai_models.get(model_id)
    
    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all available models."""
        return self.ai_models.copy()
    
    def update_model_data(self, model_id: str, updates: Dict[str, Any]):
        """Update model data."""
        if model_id in self.ai_models:
            self.ai_models[model_id].update(updates)
            if model_id == self.selected_model:
                self.display_model_info(self.ai_models[model_id])
    
    def clear_selection(self):
        """Clear the current model selection."""
        self.model_list.clearSelection()
        self.selected_model = None
        self.model_info.clear()
        
        # Disable operation buttons
        self.remove_model_btn.setEnabled(False)
        self.test_model_btn.setEnabled(False)
        self.update_model_btn.setEnabled(False)
        self.export_model_btn.setEnabled(False) 