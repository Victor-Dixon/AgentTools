"""
Workflow Base - Common Workflow Panel Functionality
=================================================

This module provides the base class for workflow panels with common
functionality like workflow execution, monitoring, and management.
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
    QTextEdit, QLineEdit, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont

from gui.base_panel import BasePanel

logger = logging.getLogger(__name__)


class WorkflowWorker(QThread):
    """Background worker for workflow operations."""
    workflow_started = pyqtSignal(str)
    workflow_progress = pyqtSignal(int, str)
    workflow_completed = pyqtSignal(dict)
    workflow_failed = pyqtSignal(str)
    
    def __init__(self, workflow_type: str, parameters: Dict[str, Any]):
        super().__init__()
        self.workflow_type = workflow_type
        self.parameters = parameters
        self.running = False
    
    def run(self):
        """Execute the workflow."""
        self.running = True
        try:
            self.workflow_started.emit(self.workflow_type)
            
            if self.workflow_type == "comprehensive_preview":
                self._simulate_comprehensive_workflow()
            elif self.workflow_type == "conversation_analysis":
                self._simulate_conversation_analysis()
            elif self.workflow_type == "data_processing":
                self._simulate_data_processing()
            else:
                raise ValueError(f"Unknown workflow type: {self.workflow_type}")
                
        except Exception as e:
            self.workflow_failed.emit(str(e))
        finally:
            self.running = False
    
    def _simulate_comprehensive_workflow(self):
        """Simulate comprehensive preview workflow."""
        import time
        
        steps = [
            "Initializing systems...",
            "Loading conversations...",
            "Processing analytics...",
            "Generating insights...",
            "Creating reports...",
            "Finalizing results..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(1)  # Simulate step execution
            progress = int((i + 1) / len(steps) * 100)
            self.workflow_progress.emit(progress, step)
        
        result = {
            "workflow_type": "comprehensive_preview",
            "status": "completed",
            "steps_completed": len(steps),
            "execution_time": len(steps),
            "results": {
                "conversations_processed": 5,
                "analytics_generated": True,
                "insights_found": 3,
                "reports_created": 2
            },
            "completed_at": datetime.now().isoformat()
        }
        
        self.workflow_completed.emit(result)
    
    def _simulate_conversation_analysis(self):
        """Simulate conversation analysis workflow."""
        import time
        
        steps = [
            "Loading conversation data...",
            "Analyzing patterns...",
            "Extracting insights...",
            "Generating summaries...",
            "Saving results..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(0.8)  # Simulate step execution
            progress = int((i + 1) / len(steps) * 100)
            self.workflow_progress.emit(progress, step)
        
        result = {
            "workflow_type": "conversation_analysis",
            "status": "completed",
            "steps_completed": len(steps),
            "execution_time": len(steps) * 0.8,
            "results": {
                "conversations_analyzed": 150,
                "patterns_identified": 12,
                "insights_extracted": 25,
                "summaries_generated": 150
            },
            "completed_at": datetime.now().isoformat()
        }
        
        self.workflow_completed.emit(result)
    
    def _simulate_data_processing(self):
        """Simulate data processing workflow."""
        import time
        
        steps = [
            "Validating data...",
            "Cleaning data...",
            "Transforming data...",
            "Enriching data...",
            "Saving processed data..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(1.2)  # Simulate step execution
            progress = int((i + 1) / len(steps) * 100)
            self.workflow_progress.emit(progress, step)
        
        result = {
            "workflow_type": "data_processing",
            "status": "completed",
            "steps_completed": len(steps),
            "execution_time": len(steps) * 1.2,
            "results": {
                "records_processed": 1000,
                "data_cleaned": True,
                "transformations_applied": 5,
                "enrichment_added": True
            },
            "completed_at": datetime.now().isoformat()
        }
        
        self.workflow_completed.emit(result)


class WorkflowBase(BasePanel):
    """Base class for workflow panels with common workflow functionality."""
    
    # Workflow-specific signals
    workflow_started = pyqtSignal(str)      # Workflow started (type)
    workflow_progress = pyqtSignal(int, str) # Workflow progress (percentage, step)
    workflow_completed = pyqtSignal(dict)   # Workflow completed (result)
    workflow_failed = pyqtSignal(str)       # Workflow failed (error)
    
    def __init__(self, title: str = "Workflow Panel", description: str = "", parent=None):
        """Initialize the workflow base panel."""
        super().__init__(title, description, parent)
        
        # Workflow state
        self.workflow_history = []
        self.current_workflow = None
        self.workflow_types = [
            "comprehensive_preview",
            "conversation_analysis", 
            "data_processing",
            "template_generation",
            "export_batch"
        ]
        
        # Workflow components
        self.workflow_selector = None
        self.workflow_progress_bar = None
        self.workflow_status_label = None
        self.workflow_history_table = None
        self.workflow_log = None
        
        # Workflow workers
        self.workflow_worker = None
        
        # Workflow settings
        self.auto_save_results = True
        self.notify_on_completion = True
        
        # Initialize workflow UI
        self.setup_workflow_ui()
    
    def setup_workflow_ui(self):
        """Setup workflow-specific UI components."""
        # Create workflow selector
        self.workflow_selector = QComboBox()
        self.workflow_selector.addItems([
            "Comprehensive Preview",
            "Conversation Analysis",
            "Data Processing",
            "Template Generation",
            "Export Batch"
        ])
        
        # Create workflow progress bar
        self.workflow_progress_bar = QProgressBar()
        self.workflow_progress_bar.setVisible(False)
        
        # Create workflow status label
        self.workflow_status_label = QLabel("Ready to execute workflow")
        self.workflow_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create workflow history table
        self.workflow_history_table = QTableWidget()
        self.workflow_history_table.setColumnCount(5)
        self.workflow_history_table.setHorizontalHeaderLabels([
            "Date", "Type", "Status", "Duration", "Results"
        ])
        self.workflow_history_table.horizontalHeader().setStretchLastSection(True)
        
        # Create workflow log
        self.workflow_log = QTextEdit()
        self.workflow_log.setReadOnly(True)
        self.workflow_log.setMaximumHeight(150)
    
    def create_workflow_tab(self, title: str = "Workflows") -> QWidget:
        """Create a standard workflow tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Workflow controls
        controls_group = QGroupBox("Workflow Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Workflow selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Workflow Type:"))
        selection_layout.addWidget(self.workflow_selector)
        selection_layout.addStretch()
        controls_layout.addLayout(selection_layout)
        
        # Workflow options
        options_layout = QHBoxLayout()
        self.auto_save_checkbox = QCheckBox("Auto-save results")
        self.auto_save_checkbox.setChecked(self.auto_save_results)
        options_layout.addWidget(self.auto_save_checkbox)
        
        self.notify_checkbox = QCheckBox("Notify on completion")
        self.notify_checkbox.setChecked(self.notify_on_completion)
        options_layout.addWidget(self.notify_checkbox)
        
        options_layout.addStretch()
        controls_layout.addLayout(options_layout)
        
        # Workflow buttons
        buttons_layout = QHBoxLayout()
        self.start_workflow_button = QPushButton("🚀 Start Workflow")
        self.start_workflow_button.clicked.connect(self.start_workflow)
        buttons_layout.addWidget(self.start_workflow_button)
        
        self.stop_workflow_button = QPushButton("⏹️ Stop Workflow")
        self.stop_workflow_button.clicked.connect(self.stop_workflow)
        self.stop_workflow_button.setEnabled(False)
        buttons_layout.addWidget(self.stop_workflow_button)
        
        self.clear_history_button = QPushButton("🗑️ Clear History")
        self.clear_history_button.clicked.connect(self.clear_workflow_history)
        buttons_layout.addWidget(self.clear_history_button)
        
        buttons_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        # Workflow progress
        controls_layout.addWidget(self.workflow_progress_bar)
        controls_layout.addWidget(self.workflow_status_label)
        
        layout.addWidget(controls_group)
        
        # Workflow log
        log_group = QGroupBox("Workflow Log")
        log_layout = QVBoxLayout(log_group)
        log_layout.addWidget(self.workflow_log)
        layout.addWidget(log_group)
        
        # Workflow history
        history_group = QGroupBox("Workflow History")
        history_layout = QVBoxLayout(history_group)
        history_layout.addWidget(self.workflow_history_table)
        layout.addWidget(history_group)
        
        return tab
    
    def start_workflow(self):
        """Start a workflow execution."""
        workflow_type = self.workflow_selector.currentText().lower().replace(" ", "_")
        
        # Prepare workflow parameters
        parameters = {
            "auto_save": self.auto_save_checkbox.isChecked(),
            "notify": self.notify_checkbox.isChecked(),
            "started_at": datetime.now().isoformat()
        }
        
        # Start workflow worker
        self.workflow_worker = WorkflowWorker(workflow_type, parameters)
        self.workflow_worker.workflow_started.connect(self.on_workflow_started)
        self.workflow_worker.workflow_progress.connect(self.on_workflow_progress)
        self.workflow_worker.workflow_completed.connect(self.on_workflow_completed)
        self.workflow_worker.workflow_failed.connect(self.on_workflow_failed)
        self.workflow_worker.start()
        
        # Update UI
        self.start_workflow_button.setEnabled(False)
        self.stop_workflow_button.setEnabled(True)
        self.workflow_progress_bar.setVisible(True)
    
    def stop_workflow(self):
        """Stop the current workflow."""
        if self.workflow_worker and self.workflow_worker.running:
            self.workflow_worker.terminate()
            self.workflow_worker.wait()
        
        # Update UI
        self.start_workflow_button.setEnabled(True)
        self.stop_workflow_button.setEnabled(False)
        self.workflow_progress_bar.setVisible(False)
        self.workflow_status_label.setText("Workflow stopped")
        
        self.add_workflow_log_entry("Workflow stopped by user")
    
    def on_workflow_started(self, workflow_type: str):
        """Handle workflow start."""
        self.workflow_started.emit(workflow_type)
        self.set_status(f"Started {workflow_type} workflow")
        self.add_workflow_log_entry(f"Started {workflow_type} workflow")
    
    def on_workflow_progress(self, percentage: int, step: str):
        """Handle workflow progress."""
        self.workflow_progress_bar.setValue(percentage)
        self.workflow_status_label.setText(f"Step: {step}")
        self.workflow_progress.emit(percentage, step)
        self.add_workflow_log_entry(f"Progress: {step} ({percentage}%)")
    
    def on_workflow_completed(self, result: Dict[str, Any]):
        """Handle workflow completion."""
        # Add to history
        self.workflow_history.append(result)
        self.update_workflow_history_display()
        
        # Update UI
        self.start_workflow_button.setEnabled(True)
        self.stop_workflow_button.setEnabled(False)
        self.workflow_progress_bar.setVisible(False)
        self.workflow_status_label.setText("Workflow completed successfully")
        
        # Show completion message
        workflow_type = result.get("workflow_type", "Unknown")
        execution_time = result.get("execution_time", 0)
        self.add_workflow_log_entry(f"Completed {workflow_type} workflow in {execution_time:.1f}s")
        
        self.workflow_completed.emit(result)
        self.set_status(f"Workflow completed: {workflow_type}")
        
        # Auto-save if enabled
        if self.auto_save_checkbox.isChecked():
            self.save_workflow_results(result)
        
        # Notify if enabled
        if self.notify_checkbox.isChecked():
            self.show_info(f"Workflow '{workflow_type}' completed successfully!")
    
    def on_workflow_failed(self, error: str):
        """Handle workflow failure."""
        self.workflow_failed.emit(error)
        self.set_status(f"Workflow failed: {error}")
        self.add_workflow_log_entry(f"Error: {error}")
        
        # Update UI
        self.start_workflow_button.setEnabled(True)
        self.stop_workflow_button.setEnabled(False)
        self.workflow_progress_bar.setVisible(False)
        self.workflow_status_label.setText("Workflow failed")
        
        self.show_error(f"Workflow failed: {error}")
    
    def add_workflow_log_entry(self, message: str):
        """Add an entry to the workflow log."""
        if self.workflow_log:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            self.workflow_log.append(log_entry)
    
    def update_workflow_history_display(self):
        """Update the workflow history table display."""
        if not self.workflow_history_table:
            return
        
        self.workflow_history_table.setRowCount(len(self.workflow_history))
        
        for i, workflow in enumerate(self.workflow_history):
            # Date
            date_item = QTableWidgetItem(workflow.get("completed_at", ""))
            self.workflow_history_table.setItem(i, 0, date_item)
            
            # Type
            type_item = QTableWidgetItem(workflow.get("workflow_type", "").replace("_", " ").title())
            self.workflow_history_table.setItem(i, 1, type_item)
            
            # Status
            status_item = QTableWidgetItem(workflow.get("status", "").title())
            if workflow.get("status") == "completed":
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.workflow_history_table.setItem(i, 2, status_item)
            
            # Duration
            duration = workflow.get("execution_time", 0)
            duration_item = QTableWidgetItem(f"{duration:.1f}s")
            self.workflow_history_table.setItem(i, 3, duration_item)
            
            # Results summary
            results = workflow.get("results", {})
            results_summary = f"{len(results)} items"
            results_item = QTableWidgetItem(results_summary)
            self.workflow_history_table.setItem(i, 4, results_item)
    
    def clear_workflow_history(self):
        """Clear the workflow history."""
        self.workflow_history.clear()
        if self.workflow_history_table:
            self.workflow_history_table.setRowCount(0)
        if self.workflow_log:
            self.workflow_log.clear()
        self.set_status("Workflow history cleared")
    
    def save_workflow_results(self, result: Dict[str, Any]):
        """Save workflow results to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            workflow_type = result.get("workflow_type", "unknown")
            filename = f"workflow_results_{workflow_type}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.add_workflow_log_entry(f"Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving workflow results: {e}")
            self.add_workflow_log_entry(f"Error saving results: {e}")
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of workflow operations."""
        return {
            "total_workflows": len(self.workflow_history),
            "completed_workflows": len([w for w in self.workflow_history if w.get("status") == "completed"]),
            "failed_workflows": len([w for w in self.workflow_history if w.get("status") == "failed"]),
            "total_execution_time": sum(w.get("execution_time", 0) for w in self.workflow_history),
            "last_workflow": self.workflow_history[-1] if self.workflow_history else None
        } 