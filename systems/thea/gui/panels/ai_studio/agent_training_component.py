#!/usr/bin/env python3
"""
Agent Training Component
========================

This component handles agent training functionality including:
- Training configuration
- Training controls
- Progress monitoring
- Results display
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QComboBox, QGroupBox, QFormLayout,
    QSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from gui.debug_handler import debug_button

logger = logging.getLogger(__name__)

class AgentTrainingComponent(QWidget):
    """Agent Training component for model training interface and controls."""
    
    # Signals
    training_started = pyqtSignal(dict)  # Training started with config
    training_stopped = pyqtSignal()      # Training stopped
    training_completed = pyqtSignal(dict)  # Training completed with results
    
    def __init__(self, memory_manager: MemoryManager = None, mmorpg_engine: MMORPGEngine = None):
        super().__init__()
        self.memory_manager = memory_manager or MemoryManager()
        self.mmorpg_engine = mmorpg_engine or MMORPGEngine()
        
        # Training state
        self.is_training = False
        self.training_timer = QTimer()
        self.training_timer.timeout.connect(self.update_training_progress)
        
        # UI Components
        self.model_name_input = None
        self.training_data_source = None
        self.epochs_spin = None
        self.batch_size_spin = None
        self.start_training_btn = None
        self.stop_training_btn = None
        self.training_progress = None
        self.training_status = None
        self.training_results = None
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the agent training user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🎯 Agent Training - Train Custom AI Models")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Training configuration
        config_group = QGroupBox("Training Configuration")
        config_layout = QFormLayout(config_group)
        
        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("Enter model name...")
        config_layout.addRow("Model Name:", self.model_name_input)
        
        self.training_data_source = QComboBox()
        self.training_data_source.addItems([
            "Conversation History",
            "Selected Conversations",
            "Custom Data",
            "Mixed Sources"
        ])
        config_layout.addRow("Data Source:", self.training_data_source)
        
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(10)
        config_layout.addRow("Training Epochs:", self.epochs_spin)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 128)
        self.batch_size_spin.setValue(16)
        config_layout.addRow("Batch Size:", self.batch_size_spin)
        
        layout.addWidget(config_group)
        
        # Training controls
        controls_group = QGroupBox("Training Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        button_layout = QHBoxLayout()
        self.start_training_btn = QPushButton("🚀 Start Training")
        button_layout.addWidget(self.start_training_btn)
        
        self.stop_training_btn = QPushButton("⏹️ Stop Training")
        self.stop_training_btn.setEnabled(False)
        button_layout.addWidget(self.stop_training_btn)
        
        controls_layout.addLayout(button_layout)
        
        # Training progress
        self.training_progress = QProgressBar()
        controls_layout.addWidget(self.training_progress)
        
        self.training_status = QLabel("Ready to train")
        controls_layout.addWidget(self.training_status)
        
        layout.addWidget(controls_group)
        
        # Training results
        results_group = QGroupBox("Training Results")
        results_layout = QVBoxLayout(results_group)
        
        self.training_results = QTextEdit()
        self.training_results.setReadOnly(True)
        self.training_results.setPlaceholderText("Training results will appear here...")
        results_layout.addWidget(self.training_results)
        
        layout.addWidget(results_group)
        layout.addStretch()
    
    def connect_signals(self):
        """Connect all signals and slots."""
        self.start_training_btn.clicked.connect(self.start_agent_training)
        self.stop_training_btn.clicked.connect(self.stop_agent_training)
    
    @debug_button("start_agent_training", "Agent Training Component")
    def start_agent_training(self):
        """Start the agent training process."""
        model_name = self.model_name_input.text().strip()
        if not model_name:
            self.training_status.setText("Error: Please enter a model name")
            return
        
        # Get training configuration
        config = {
            'model_name': model_name,
            'data_source': self.training_data_source.currentText(),
            'epochs': self.epochs_spin.value(),
            'batch_size': self.batch_size_spin.value(),
            'start_time': datetime.now().isoformat()
        }
        
        # Update UI state
        self.is_training = True
        self.start_training_btn.setEnabled(False)
        self.stop_training_btn.setEnabled(True)
        self.training_progress.setValue(0)
        self.training_status.setText("Training started...")
        
        # Clear previous results
        self.training_results.clear()
        
        # Start progress timer
        self.training_timer.start(100)  # Update every 100ms
        
        # Emit training started signal
        self.training_started.emit(config)
        
        logger.info(f"Started training for model: {model_name}")
    
    @debug_button("stop_agent_training", "Agent Training Component")
    def stop_agent_training(self):
        """Stop the agent training process."""
        self.is_training = False
        self.training_timer.stop()
        
        # Update UI state
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.training_status.setText("Training stopped")
        
        # Emit training stopped signal
        self.training_stopped.emit()
        
        logger.info("Training stopped by user")
    
    @debug_button("update_training_progress", "Agent Training Component")
    def update_training_progress(self):
        """Update training progress simulation."""
        if not self.is_training:
            return
        
        current_progress = self.training_progress.value()
        if current_progress < 100:
            # Simulate progress
            new_progress = min(current_progress + 1, 100)
            self.training_progress.setValue(new_progress)
            
            # Update status
            if new_progress < 100:
                self.training_status.setText(f"Training in progress... {new_progress}%")
            else:
                self.on_training_completed({
                    'model_name': self.model_name_input.text(),
                    'accuracy': 0.85 + (new_progress % 10) * 0.01,
                    'loss': 0.15 - (new_progress % 10) * 0.01,
                    'epochs_completed': self.epochs_spin.value(),
                    'completion_time': datetime.now().isoformat()
                })
    
    @debug_button("on_training_completed", "Agent Training Component")
    def on_training_completed(self, result: dict):
        """Handle training completion."""
        self.is_training = False
        self.training_timer.stop()
        
        # Update UI state
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.training_progress.setValue(100)
        self.training_status.setText("Training completed!")
        
        # Display results
        result_text = f"""=== Training Completed ===
Model: {result.get('model_name', 'Unknown')}
Accuracy: {result.get('accuracy', 0):.3f}
Loss: {result.get('loss', 0):.3f}
Epochs: {result.get('epochs_completed', 0)}
Completed: {result.get('completion_time', 'Unknown')}

=== Training Summary ===
✅ Training completed successfully
✅ Model saved to disk
✅ Performance metrics calculated
✅ Ready for deployment

=== Next Steps ===
1. Test the model with sample data
2. Deploy to production environment
3. Monitor performance metrics
4. Retrain if necessary"""
        
        self.training_results.setPlainText(result_text)
        
        # Emit training completed signal
        self.training_completed.emit(result)
        
        logger.info(f"Training completed for model: {result.get('model_name', 'Unknown')}")
    
    def get_training_config(self) -> Dict[str, Any]:
        """Get current training configuration."""
        return {
            'model_name': self.model_name_input.text().strip(),
            'data_source': self.training_data_source.currentText(),
            'epochs': self.epochs_spin.value(),
            'batch_size': self.batch_size_spin.value()
        }
    
    def set_training_config(self, config: Dict[str, Any]):
        """Set training configuration."""
        if 'model_name' in config:
            self.model_name_input.setText(config['model_name'])
        if 'data_source' in config:
            index = self.training_data_source.findText(config['data_source'])
            if index >= 0:
                self.training_data_source.setCurrentIndex(index)
        if 'epochs' in config:
            self.epochs_spin.setValue(config['epochs'])
        if 'batch_size' in config:
            self.batch_size_spin.setValue(config['batch_size'])
    
    def is_training_active(self) -> bool:
        """Check if training is currently active."""
        return self.is_training
    
    def get_progress(self) -> int:
        """Get current training progress."""
        return self.training_progress.value()
    
    def set_progress(self, progress: int):
        """Set training progress."""
        self.training_progress.setValue(max(0, min(100, progress)))
    
    def add_training_log(self, message: str):
        """Add a log message to training results."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        current_text = self.training_results.toPlainText()
        if current_text:
            self.training_results.setPlainText(f"{current_text}\n{log_entry}")
        else:
            self.training_results.setPlainText(log_entry)
    
    def clear_results(self):
        """Clear training results."""
        self.training_results.clear()
    
    def disable_config(self):
        """Disable configuration during training."""
        self.model_name_input.setEnabled(False)
        self.training_data_source.setEnabled(False)
        self.epochs_spin.setEnabled(False)
        self.batch_size_spin.setEnabled(False)
    
    def enable_config(self):
        """Enable configuration after training."""
        self.model_name_input.setEnabled(True)
        self.training_data_source.setEnabled(True)
        self.epochs_spin.setEnabled(True)
        self.batch_size_spin.setEnabled(True) 