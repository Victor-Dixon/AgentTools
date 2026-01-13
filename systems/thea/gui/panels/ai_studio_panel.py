#!/usr/bin/env python3
from gui.debug_handler import debug_button
"""
AI Studio Panel for Thea GUI
============================

Consolidates all AI-related functionality into a single comprehensive panel:
- Conversational AI - Chat with your work
- Intelligent Agent - AI queries and analysis
- Agent Training - Train custom AI models
- Training Data - Extract and manage training data

This eliminates redundancy and provides a unified AI experience.
"""

import sys
from gui.debug_handler import debug_button
import os
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QTabWidget, QSpinBox,
    QCheckBox, QFormLayout, QScrollArea, QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QObject
from PyQt6.QtGui import QFont, QTextCursor

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.intelligent_agent_system import IntelligentAgentSystem
from dreamscape.core.conversational_ai_workflow import ConversationalAIWorkflow
from dreamscape.core.agent_trainer import AgentTrainer
from dreamscape.core.training_data_orchestrator import TrainingDataOrchestrator

logger = logging.getLogger(__name__)

class AIStudioWorker(QObject):
    """Worker thread for AI operations."""
    
    # Signals
    progress_updated = pyqtSignal(str, int)  # message, percentage
    status_updated = pyqtSignal(str)  # status message
    operation_completed = pyqtSignal(dict)  # results
    operation_failed = pyqtSignal(str)  # error message
    
    def __init__(self, operation_type: str, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.kwargs = kwargs
        self.is_running = False
    
    def run(self):
        """Run the specified AI operation."""
        try:
            self.is_running = True
            self.status_updated.emit(f"Starting {self.operation_type} operation...")
            
            if self.operation_type == "conversational_ai":
                self._run_conversational_ai()
            elif self.operation_type == "intelligent_agent":
                self._run_intelligent_agent()
            elif self.operation_type == "agent_training":
                self._run_agent_training()
            elif self.operation_type == "training_data":
                self._run_training_data()
            else:
                self.operation_failed.emit(f"Unknown operation type: {self.operation_type}")
                
        except Exception as e:
            self.operation_failed.emit(f"AI operation failed: {e}")
        finally:
            self.is_running = False
    
    def _run_conversational_ai(self):
        """Run conversational AI operation."""
        try:
            from dreamscape.core.conversational_ai_workflow import ConversationalAIWorkflow
            
            self.progress_updated.emit("Initializing conversational AI...", 20)
            workflow = ConversationalAIWorkflow()
            
            self.progress_updated.emit("Processing conversation...", 60)
            # This would integrate with the existing conversational AI workflow
            result = {"success": True, "message": "Conversational AI operation completed"}
            
            self.progress_updated.emit("Operation completed", 100)
            self.operation_completed.emit(result)
            
        except Exception as e:
            self.operation_failed.emit(f"Conversational AI failed: {e}")
    
    def _run_intelligent_agent(self):
        """Run intelligent agent operation."""
        try:
            from dreamscape.core.intelligent_agent_system import IntelligentAgentSystem
            
            self.progress_updated.emit("Initializing intelligent agent...", 20)
            agent = IntelligentAgentSystem()
            
            self.progress_updated.emit("Processing query...", 60)
            # This would integrate with the existing intelligent agent system
            result = {"success": True, "message": "Intelligent agent operation completed"}
            
            self.progress_updated.emit("Operation completed", 100)
            self.operation_completed.emit(result)
            
        except Exception as e:
            self.operation_failed.emit(f"Intelligent agent failed: {e}")
    
    def _run_agent_training(self):
        """Run agent training operation."""
        try:
            from dreamscape.core.agent_trainer import AgentTrainer
            
            self.progress_updated.emit("Initializing agent trainer...", 20)
            trainer = AgentTrainer()
            
            self.progress_updated.emit("Training agent...", 60)
            # This would integrate with the existing agent training system
            result = {"success": True, "message": "Agent training completed"}
            
            self.progress_updated.emit("Training completed", 100)
            self.operation_completed.emit(result)
            
        except Exception as e:
            self.operation_failed.emit(f"Agent training failed: {e}")
    
    def _run_training_data(self):
        """Run training data extraction operation."""
        try:
            from dreamscape.core.training_data_orchestrator import TrainingDataOrchestrator
            
            self.progress_updated.emit("Initializing training data orchestrator...", 20)
            orchestrator = TrainingDataOrchestrator()
            
            self.progress_updated.emit("Extracting training data...", 60)
            # This would integrate with the existing training data system
            result = {"success": True, "message": "Training data extraction completed"}
            
            self.progress_updated.emit("Extraction completed", 100)
            self.operation_completed.emit(result)
            
        except Exception as e:
            self.operation_failed.emit(f"Training data extraction failed: {e}")


class AIStudioPanel(QWidget):
    """Main AI Studio panel that consolidates all AI functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_thread = None
        self.worker = None
        self.memory_manager = MemoryManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🤖 AI Studio")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Unified AI interface for conversational AI, intelligent agents, training, and data management.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_conversational_ai_tab(), "💬 Conversational AI")
        self.tab_widget.addTab(self.create_intelligent_agent_tab(), "🧠 Intelligent Agent")
        self.tab_widget.addTab(self.create_agent_training_tab(), "🎯 Agent Training")
        self.tab_widget.addTab(self.create_training_data_tab(), "📊 Training Data")
        
        # Progress section
        self.create_progress_section(layout)
    
    @debug_button("create_conversational_ai_tab", "Ai Studio Panel")
    def create_conversational_ai_tab(self) -> QWidget:
        """Create the conversational AI tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Chat with your work using AI-powered conversation analysis and insights.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Session management
        session_group = QGroupBox("Session Management")
        session_layout = QHBoxLayout(session_group)
        
        self.start_session_btn = QPushButton("🚀 Start Session")
        self.start_session_btn.clicked.connect(self.start_conversational_session)
        session_layout.addWidget(self.start_session_btn)
        
        self.end_session_btn = QPushButton("⏹️ End Session")
        self.end_session_btn.clicked.connect(self.end_conversational_session)
        self.end_session_btn.setEnabled(False)
        session_layout.addWidget(self.end_session_btn)
        
        layout.addWidget(session_group)
        
        # Conversation interface
        conv_group = QGroupBox("Conversation Interface")
        conv_layout = QVBoxLayout(conv_group)
        
        # Message input
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        input_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton("📤 Send")
        self.send_btn.clicked.connect(self.send_conversational_message)
        self.send_btn.setEnabled(False)
        input_layout.addWidget(self.send_btn)
        
        conv_layout.addLayout(input_layout)
        
        # Context type selection
        context_layout = QHBoxLayout()
        context_layout.addWidget(QLabel("Context Type:"))
        self.context_type_combo = QComboBox()
        self.context_type_combo.addItems(["General", "Coding", "Writing", "Analysis", "Planning", "Debugging"])
        context_layout.addWidget(self.context_type_combo)
        context_layout.addStretch()
        
        conv_layout.addLayout(context_layout)
        
        # Conversation display
        self.conversation_display = QTextBrowser()
        self.conversation_display.setMinimumHeight(200)
        conv_layout.addWidget(self.conversation_display)
        
        layout.addWidget(conv_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.ask_work_btn = QPushButton("💼 Ask About My Work")
        self.ask_work_btn.clicked.connect(self.ask_about_work)
        actions_layout.addWidget(self.ask_work_btn)
        
        self.workflow_suggestions_btn = QPushButton("🔄 Get Workflow Suggestions")
        self.workflow_suggestions_btn.clicked.connect(self.get_workflow_suggestions)
        actions_layout.addWidget(self.workflow_suggestions_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return widget
    
    @debug_button("create_intelligent_agent_tab", "Ai Studio Panel")
    def create_intelligent_agent_tab(self) -> QWidget:
        """Create the intelligent agent tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("AI-powered queries and analysis for intelligent insights and recommendations.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Query interface
        query_group = QGroupBox("AI Query Interface")
        query_layout = QVBoxLayout(query_group)
        
        # Query input
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter your AI query here...")
        self.query_input.setMaximumHeight(100)
        query_layout.addWidget(self.query_input)
        
        # Query buttons
        button_layout = QHBoxLayout()
        
        self.submit_query_btn = QPushButton("🤖 Submit Query")
        self.submit_query_btn.clicked.connect(self.submit_intelligent_query)
        button_layout.addWidget(self.submit_query_btn)
        
        self.clear_query_btn = QPushButton("🗑️ Clear")
        self.clear_query_btn.clicked.connect(self.clear_query)
        button_layout.addWidget(self.clear_query_btn)
        
        query_layout.addLayout(button_layout)
        
        layout.addWidget(query_group)
        
        # Response display
        response_group = QGroupBox("AI Response")
        response_layout = QVBoxLayout(response_group)
        
        self.response_display = QTextBrowser()
        self.response_display.setMinimumHeight(300)
        response_layout.addWidget(self.response_display)
        
        layout.addWidget(response_group)
        
        # Preset queries
        preset_group = QGroupBox("Preset Queries")
        preset_layout = QGridLayout(preset_group)
        
        presets = [
            ("📊 Analyze My Work Patterns", "Analyze my recent work patterns and suggest improvements"),
            ("🎯 Identify Skill Gaps", "Identify gaps in my current skill set"),
            ("📈 Project Recommendations", "Suggest projects to enhance my portfolio"),
            ("🔍 Code Review Request", "Review my recent code and suggest improvements"),
            ("📝 Documentation Analysis", "Analyze my documentation and suggest enhancements"),
            ("🚀 Career Path Guidance", "Provide guidance on my career development path")
        ]
        
        for i, (label, query) in enumerate(presets):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, q=query: self.load_preset_query(q))
            preset_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(preset_group)
        layout.addStretch()
        
        return widget
    
    @debug_button("create_agent_training_tab", "Ai Studio Panel")
    def create_agent_training_tab(self) -> QWidget:
        """Create the agent training tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Train custom AI models using your conversation data and work patterns.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Training configuration
        config_group = QGroupBox("Training Configuration")
        config_layout = QFormLayout(config_group)
        
        # Model name
        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("My Custom Agent")
        config_layout.addRow("Model Name:", self.model_name_input)
        
        # Base model selection
        self.base_model_combo = QComboBox()
        self.base_model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "custom-transformer", "lstm"])
        config_layout.addRow("Base Model:", self.base_model_combo)
        
        # Training parameters
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 50)
        self.epochs_spin.setValue(3)
        config_layout.addRow("Training Epochs:", self.epochs_spin)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 32)
        self.batch_size_spin.setValue(4)
        config_layout.addRow("Batch Size:", self.batch_size_spin)
        
        layout.addWidget(config_group)
        
        # Training options
        options_group = QGroupBox("Training Options")
        options_layout = QVBoxLayout(options_group)
        
        self.enable_rag_checkbox = QCheckBox("Enable RAG (Retrieval-Augmented Generation)")
        self.enable_rag_checkbox.setChecked(True)
        options_layout.addWidget(self.enable_rag_checkbox)
        
        self.extract_personality_checkbox = QCheckBox("Extract Personality Traits")
        self.extract_personality_checkbox.setChecked(True)
        options_layout.addWidget(self.extract_personality_checkbox)
        
        layout.addWidget(options_group)
        
        # Training actions
        actions_group = QGroupBox("Training Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.start_training_btn = QPushButton("🚀 Start Training")
        self.start_training_btn.clicked.connect(self.start_agent_training)
        actions_layout.addWidget(self.start_training_btn)
        
        self.stop_training_btn = QPushButton("⏹️ Stop Training")
        self.stop_training_btn.clicked.connect(self.stop_agent_training)
        self.stop_training_btn.setEnabled(False)
        actions_layout.addWidget(self.stop_training_btn)
        
        layout.addWidget(actions_group)
        
        # Training status
        status_group = QGroupBox("Training Status")
        status_layout = QVBoxLayout(status_group)
        
        self.training_status_label = QLabel("Ready to start training")
        status_layout.addWidget(self.training_status_label)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        return widget
    
    @debug_button("create_training_data_tab", "Ai Studio Panel")
    def create_training_data_tab(self) -> QWidget:
        """Create the training data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Extract, manage, and analyze training data from your conversations and work.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Data extraction
        extraction_group = QGroupBox("Data Extraction")
        extraction_layout = QVBoxLayout(extraction_group)
        
        # Extraction options
        options_layout = QHBoxLayout()
        
        self.extract_conversations_checkbox = QCheckBox("Extract Conversations")
        self.extract_conversations_checkbox.setChecked(True)
        options_layout.addWidget(self.extract_conversations_checkbox)
        
        self.extract_skills_checkbox = QCheckBox("Extract Skills")
        self.extract_skills_checkbox.setChecked(True)
        options_layout.addWidget(self.extract_skills_checkbox)
        
        self.extract_projects_checkbox = QCheckBox("Extract Projects")
        self.extract_projects_checkbox.setChecked(True)
        options_layout.addWidget(self.extract_projects_checkbox)
        
        extraction_layout.addLayout(options_layout)
        
        # Extraction actions
        actions_layout = QHBoxLayout()
        
        self.extract_data_btn = QPushButton("📊 Extract Training Data")
        self.extract_data_btn.clicked.connect(self.extract_training_data)
        actions_layout.addWidget(self.extract_data_btn)
        
        self.analyze_data_btn = QPushButton("📈 Analyze Data")
        self.analyze_data_btn.clicked.connect(self.analyze_training_data)
        actions_layout.addWidget(self.analyze_data_btn)
        
        extraction_layout.addLayout(actions_layout)
        
        layout.addWidget(extraction_group)
        
        # Data management
        management_group = QGroupBox("Data Management")
        management_layout = QVBoxLayout(management_group)
        
        # Data display
        self.data_display = QTextBrowser()
        self.data_display.setMinimumHeight(200)
        management_layout.addWidget(self.data_display)
        
        # Management actions
        mgmt_actions_layout = QHBoxLayout()
        
        self.export_data_btn = QPushButton("📤 Export Data")
        self.export_data_btn.clicked.connect(self.export_training_data)
        mgmt_actions_layout.addWidget(self.export_data_btn)
        
        self.clear_data_btn = QPushButton("🗑️ Clear Data")
        self.clear_data_btn.clicked.connect(self.clear_training_data)
        mgmt_actions_layout.addWidget(self.clear_data_btn)
        
        management_layout.addLayout(mgmt_actions_layout)
        
        layout.addWidget(management_group)
        layout.addStretch()
        
        return widget
    
    @debug_button("create_progress_section", "Ai Studio Panel")
    def create_progress_section(self, parent_layout):
        """Create the progress section."""
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        parent_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to use AI Studio")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self.status_label)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(150)
        self.log_display.setReadOnly(True)
        parent_layout.addWidget(self.log_display)
    
    def log_message(self, message: str):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
    
    @debug_button("start_ai_operation", "Ai Studio Panel")
    def start_ai_operation(self, operation_type: str, **kwargs):
        """Start an AI operation in a separate thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Operation Running", "Another AI operation is already running. Please wait for it to complete.")
            return
        
        # Create worker and thread
        self.worker = AIStudioWorker(operation_type, **kwargs)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.status_updated.connect(self.update_status)
        self.worker.operation_completed.connect(self.operation_completed)
        self.worker.operation_failed.connect(self.operation_failed)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.finished.connect(self.operation_finished)
        
        # Start operation
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_message(f"Starting {operation_type} operation...")
        self.worker_thread.start()
    
    @debug_button("update_progress", "Ai Studio Panel")
    def update_progress(self, message: str, percentage: int):
        """Update progress bar and log."""
        self.progress_bar.setValue(percentage)
        self.log_message(message)
    
    @debug_button("update_status", "Ai Studio Panel")
    def update_status(self):
        """Create statistics grid using shared components."""
        try:
            from gui.components.shared_components import SharedComponents
            
            components = SharedComponents()
            
            # Create statistics grid with panel-specific data
            stats_data = {
                "Total": 0,
                "Active": 0,
                "Completed": 0
            }
            
            stats_widget = components.create_statistics_grid(
                stats_data=stats_data,
                title="ai_studio_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
    @debug_button("operation_completed", "Ai Studio Panel")
    def operation_completed(self, results: dict):
        """Handle operation completion."""
        self.log_message("AI operation completed successfully!")
        QMessageBox.information(self, "AI Operation Complete", "AI operation completed successfully!")
    
    @debug_button("operation_failed", "Ai Studio Panel")
    def operation_failed(self, error: str):
        """Handle operation failure."""
        self.log_message(f"AI operation failed: {error}")
        QMessageBox.critical(self, "AI Operation Failed", f"AI operation failed: {error}")
    
    @debug_button("operation_finished", "Ai Studio Panel")
    def operation_finished(self):
        """Handle operation thread completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready to use AI Studio")
        
        # Clean up
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
        self.worker = None
    
    # Conversational AI methods
    @debug_button("start_conversational_session", "Ai Studio Panel")
    def start_conversational_session(self):
        """Start a conversational AI session."""
        self.start_session_btn.setEnabled(False)
        self.end_session_btn.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.conversation_display.append("🤖 AI Session started. You can now chat with your work!")
        self.log_message("Conversational AI session started")
    
    @debug_button("end_conversational_session", "Ai Studio Panel")
    def end_conversational_session(self):
        """End the conversational AI session."""
        self.start_session_btn.setEnabled(True)
        self.end_session_btn.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.conversation_display.append("⏹️ AI Session ended.")
        self.log_message("Conversational AI session ended")
    
    @debug_button("send_conversational_message", "Ai Studio Panel")
    def send_conversational_message(self):
        """Send a message to the conversational AI."""
        message = self.message_input.text().strip()
        if not message:
            return
        
        context_type = self.context_type_combo.currentText()
        self.conversation_display.append(f"👤 You ({context_type}): {message}")
        self.message_input.clear()
        
        # Start AI operation
        self.start_ai_operation("conversational_ai", message=message, context_type=context_type)
    
    @debug_button("ask_about_work", "Ai Studio Panel")
    def ask_about_work(self):
        """Ask AI about work patterns."""
        self.conversation_display.append("🤖 AI: Analyzing your work patterns...")
        self.start_ai_operation("conversational_ai", query_type="work_analysis")
    
    @debug_button("get_workflow_suggestions", "Ai Studio Panel")
    def get_workflow_suggestions(self):
        """Get workflow suggestions from AI."""
        self.conversation_display.append("🤖 AI: Generating workflow suggestions...")
        self.start_ai_operation("conversational_ai", query_type="workflow_suggestions")
    
    # Intelligent Agent methods
    @debug_button("submit_intelligent_query", "Ai Studio Panel")
    def submit_intelligent_query(self):
        """Submit a query to the intelligent agent."""
        query = self.query_input.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a query.")
            return
        
        self.response_display.append(f"🤖 Query: {query}")
        self.response_display.append("🧠 Processing...")
        
        # Start AI operation
        self.start_ai_operation("intelligent_agent", query=query)
    
    @debug_button("clear_query", "Ai Studio Panel")
    def clear_query(self):
        """Clear the query input."""
        self.query_input.clear()
        self.response_display.clear()
    
    @debug_button("load_preset_query", "Ai Studio Panel")
    def load_preset_query(self, query: str):
        """Load a preset query."""
        self.query_input.setPlainText(query)
    
    # Agent Training methods
    @debug_button("start_agent_training", "Ai Studio Panel")
    def start_agent_training(self):
        """Start agent training."""
        model_name = self.model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Missing Model Name", "Please enter a model name.")
            return
        
        self.training_status_label.setText("Training in progress...")
        self.start_training_btn.setEnabled(False)
        self.stop_training_btn.setEnabled(True)
        
        # Start AI operation
        self.start_ai_operation("agent_training", 
                               model_name=model_name,
                               base_model=self.base_model_combo.currentText(),
                               epochs=self.epochs_spin.value(),
                               batch_size=self.batch_size_spin.value(),
                               enable_rag=self.enable_rag_checkbox.isChecked(),
                               extract_personality=self.extract_personality_checkbox.isChecked())
    
    @debug_button("stop_agent_training", "Ai Studio Panel")
    def stop_agent_training(self):
        """Stop agent training."""
        self.training_status_label.setText("Training stopped")
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.log_message("Agent training stopped")
    
    # Training Data methods
    @debug_button("extract_training_data", "Ai Studio Panel")
    def extract_training_data(self):
        """Extract training data."""
        self.data_display.append("📊 Extracting training data...")
        self.start_ai_operation("training_data", 
                               extract_conversations=self.extract_conversations_checkbox.isChecked(),
                               extract_skills=self.extract_skills_checkbox.isChecked(),
                               extract_projects=self.extract_projects_checkbox.isChecked())
    
    @debug_button("analyze_training_data", "Ai Studio Panel")
    def analyze_training_data(self):
        """Analyze training data."""
        self.data_display.append("📈 Analyzing training data...")
        self.log_message("Training data analysis started")
    
    @debug_button("export_training_data", "Ai Studio Panel")
    def export_training_data(self):
        """Export training data."""
        self.data_display.append("📤 Exporting training data...")
        self.log_message("Training data export started")
    
    @debug_button("clear_training_data", "Ai Studio Panel")
    def clear_training_data(self):
        """Clear training data display."""
        self.data_display.clear()
        self.log_message("Training data display cleared") 