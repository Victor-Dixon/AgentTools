#!/usr/bin/env python3
"""
Consolidated AI Studio Panel
============================

This panel consolidates all AI-related functionality:
- Conversational AI
- Intelligent Agent
- AI Agent Training
- Training Data
- Multi-Model Management
"""

import sys
from gui.debug_handler import debug_button
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
    QPushButton, QTextEdit, QLineEdit, QComboBox, QSpinBox,
    QProgressBar, QGroupBox, QFormLayout, QCheckBox, QListWidget,
    QListWidgetItem, QSplitter, QFrame, QScrollArea, QGridLayout,
    QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from dreamscape.core.template_engine import render_template
from dreamscape.core.mmorpg.mmorpg_system import EnhancedProgressSystem
from gui.components.refresh_integration_manager import UnifiedRefreshButton
from gui.components.global_refresh_manager import RefreshType

logger = logging.getLogger(__name__)

class AIStudioPanel(QWidget):
    """Consolidated AI Studio Panel with all AI functionality."""
    
    # Signals for AI operations
    ai_response_received = pyqtSignal(dict)  # AI response data
    training_completed = pyqtSignal(dict)    # Training results
    data_extracted = pyqtSignal(dict)        # Data extraction results
    model_updated = pyqtSignal(dict)         # Model update results
    
    def __init__(self, memory_manager: MemoryManager = None, mmorpg_engine: MMORPGEngine = None):
        super().__init__()
        self.memory_manager = memory_manager or MemoryManager()
        self.mmorpg_engine = mmorpg_engine or MMORPGEngine()
        self.enhanced_progress = EnhancedProgressSystem(self.mmorpg_engine, self.memory_manager)
        
        # AI Studio state
        self.current_conversation = None
        self.ai_models = {}
        self.training_data = {}
        self.extraction_results = {}
        
        self.init_ui()
        self.load_ai_state()
    
    def init_ui(self):
        """Initialize the AI Studio user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🤖 AI Studio - Complete AI Workflow Management")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Manage all AI interactions, training, and data extraction from a unified interface.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add consolidated tabs
        self.tab_widget.addTab(self.create_conversational_ai_tab(), "Conversational AI")
        self.tab_widget.addTab(self.create_intelligent_agent_tab(), "Intelligent Agent")
        self.tab_widget.addTab(self.create_agent_training_tab(), "Agent Training")
        self.tab_widget.addTab(self.create_training_data_tab(), "Training Data")
        self.tab_widget.addTab(self.create_multi_model_tab(), "Model Management")
        self.tab_widget.addTab(self.create_ai_analytics_tab(), "AI Analytics")
        self.tab_widget.addTab(self.create_enhanced_devlog_tab(), "Enhanced Devlog")
        
        # Progress section
        self.create_progress_section(layout)
        
        # Connect signals
        self.connect_signals()
    
    @debug_button("create_conversational_ai_tab", "Consolidated Ai Studio Panel")
    def create_conversational_ai_tab(self) -> QWidget:
        """Create the conversational AI tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("💬 Conversational AI - Chat with Your Work")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Conversation selection
        conv_group = QGroupBox("Select Conversation Context")
        conv_layout = QVBoxLayout(conv_group)
        
        self.conversation_combo = QComboBox()
        self.conversation_combo.addItem("Select a conversation...")
        conv_layout.addWidget(self.conversation_combo)
        
        self.load_conversations_btn = QPushButton("🔄 Load Recent Conversations")
        self.load_conversations_btn.clicked.connect(self.load_conversations)
        conv_layout.addWidget(self.load_conversations_btn)
        
        layout.addWidget(conv_group)
        
        # Chat interface
        chat_group = QGroupBox("AI Chat Interface")
        chat_layout = QVBoxLayout(chat_group)
        
        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setMaximumHeight(300)
        chat_layout.addWidget(QLabel("Chat History:"))
        chat_layout.addWidget(self.chat_history)
        
        # Input area
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask the AI about your work...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        input_layout.addWidget(self.chat_input)
        
        self.send_chat_btn = QPushButton("Send")
        self.send_chat_btn.clicked.connect(self.send_chat_message)
        input_layout.addWidget(self.send_chat_btn)
        
        chat_layout.addLayout(input_layout)
        layout.addWidget(chat_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QGridLayout(actions_group)
        
        self.analyze_btn = QPushButton("🔍 Analyze Current Work")
        self.analyze_btn.clicked.connect(self.analyze_current_work)
        actions_layout.addWidget(self.analyze_btn, 0, 0)
        
        self.suggest_btn = QPushButton("💡 Get Suggestions")
        self.suggest_btn.clicked.connect(self.get_suggestions)
        actions_layout.addWidget(self.suggest_btn, 0, 1)
        
        self.explain_btn = QPushButton("📚 Explain Concepts")
        self.explain_btn.clicked.connect(self.explain_concepts)
        actions_layout.addWidget(self.explain_btn, 1, 0)
        
        self.debug_btn = QPushButton("🐛 Debug Help")
        self.debug_btn.clicked.connect(self.get_debug_help)
        actions_layout.addWidget(self.debug_btn, 1, 1)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_intelligent_agent_tab", "Consolidated Ai Studio Panel")
    def create_intelligent_agent_tab(self) -> QWidget:
        """Create the intelligent agent tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("🧠 Intelligent Agent - Advanced AI Queries")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Query interface
        query_group = QGroupBox("AI Query Interface")
        query_layout = QVBoxLayout(query_group)
        
        # Query type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Query Type:"))
        self.query_type_combo = QComboBox()
        self.query_type_combo.addItems([
            "General Analysis",
            "Code Review",
            "Architecture Analysis",
            "Performance Optimization",
            "Security Review",
            "Best Practices",
            "Custom Query"
        ])
        type_layout.addWidget(self.query_type_combo)
        query_layout.addLayout(type_layout)
        
        # Query input
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter your AI query here...")
        self.query_input.setMaximumHeight(150)
        query_layout.addWidget(QLabel("Query:"))
        query_layout.addWidget(self.query_input)
        
        # Context selection
        context_layout = QHBoxLayout()
        context_layout.addWidget(QLabel("Context:"))
        self.context_combo = QComboBox()
        self.context_combo.addItems([
            "Current Project",
            "All Conversations",
            "Recent Work",
            "Specific Files",
            "Custom Context"
        ])
        context_layout.addWidget(self.context_combo)
        query_layout.addLayout(context_layout)
        
        # Execute button
        self.execute_query_btn = QPushButton("🚀 Execute Query")
        self.execute_query_btn.clicked.connect(self.execute_ai_query)
        query_layout.addWidget(self.execute_query_btn)
        
        layout.addWidget(query_group)
        
        # Results area
        results_group = QGroupBox("Query Results")
        results_layout = QVBoxLayout(results_group)
        
        self.query_results = QTextEdit()
        self.query_results.setReadOnly(True)
        results_layout.addWidget(self.query_results)
        
        layout.addWidget(results_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_agent_training_tab", "Consolidated Ai Studio Panel")
    def create_agent_training_tab(self) -> QWidget:
        """Create the agent training tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        self.start_training_btn.clicked.connect(self.start_agent_training)
        button_layout.addWidget(self.start_training_btn)
        
        self.stop_training_btn = QPushButton("⏹️ Stop Training")
        self.stop_training_btn.clicked.connect(self.stop_agent_training)
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
        results_layout.addWidget(self.training_results)
        
        layout.addWidget(results_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_training_data_tab", "Consolidated Ai Studio Panel")
    def create_training_data_tab(self) -> QWidget:
        """Create the training data tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
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
        
        self.extract_code_cb = QCheckBox("Extract Code Snippets")
        self.extract_code_cb.setChecked(True)
        options_layout.addWidget(self.extract_code_cb, 0, 1)
        
        self.extract_patterns_cb = QCheckBox("Extract Work Patterns")
        self.extract_patterns_cb.setChecked(True)
        options_layout.addWidget(self.extract_patterns_cb, 1, 0)
        
        self.extract_skills_cb = QCheckBox("Extract Skill Data")
        self.extract_skills_cb.setChecked(True)
        options_layout.addWidget(self.extract_skills_cb, 1, 1)
        
        extraction_layout.addLayout(options_layout)
        
        # Extraction controls
        controls_layout = QHBoxLayout()
        self.extract_data_btn = QPushButton("📥 Extract Training Data")
        self.extract_data_btn.clicked.connect(self.extract_training_data)
        controls_layout.addWidget(self.extract_data_btn)
        
        self.export_data_btn = QPushButton("📤 Export Data")
        self.export_data_btn.clicked.connect(self.export_training_data)
        controls_layout.addWidget(self.export_data_btn)
        
        extraction_layout.addLayout(controls_layout)
        
        layout.addWidget(extraction_group)
        
        # Data preview
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.data_preview = QTableWidget()
        self.data_preview.setColumnCount(4)
        self.data_preview.setHorizontalHeaderLabels(["Type", "Count", "Size", "Status"])
        self.data_preview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        preview_layout.addWidget(self.data_preview)
        
        layout.addWidget(preview_group)
        
        # Data statistics
        stats_group = QGroupBox("Data Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.total_conversations_label = QLabel("0")
        stats_layout.addRow("Total Conversations:", self.total_conversations_label)
        
        self.total_code_snippets_label = QLabel("0")
        stats_layout.addRow("Code Snippets:", self.total_code_snippets_label)
        
        self.total_patterns_label = QLabel("0")
        stats_layout.addRow("Work Patterns:", self.total_patterns_label)
        
        self.total_skills_label = QLabel("0")
        stats_layout.addRow("Skills Data:", self.total_skills_label)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_multi_model_tab", "Consolidated Ai Studio Panel")
    def create_multi_model_tab(self) -> QWidget:
        """Create the multi-model management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("🔧 Model Management - Manage AI Models")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Model list
        models_group = QGroupBox("Available Models")
        models_layout = QVBoxLayout(models_group)
        
        self.models_list = QListWidget()
        self.models_list.itemClicked.connect(self.on_model_selected)
        models_layout.addWidget(self.models_list)
        
        # Model controls
        model_controls_layout = QHBoxLayout()
        self.add_model_btn = QPushButton("➕ Add Model")
        self.add_model_btn.clicked.connect(self.add_model)
        model_controls_layout.addWidget(self.add_model_btn)
        
        self.remove_model_btn = QPushButton("➖ Remove Model")
        self.remove_model_btn.clicked.connect(self.remove_model)
        model_controls_layout.addWidget(self.remove_model_btn)
        
        self.refresh_models_btn = QPushButton("🔄 Refresh")
        self.refresh_models_btn.clicked.connect(self.refresh_models)
        model_controls_layout.addWidget(self.refresh_models_btn)
        
        models_layout.addLayout(model_controls_layout)
        layout.addWidget(models_group)
        
        # Model details
        details_group = QGroupBox("Model Details")
        details_layout = QFormLayout(details_group)
        
        self.model_name_label = QLabel("No model selected")
        details_layout.addRow("Name:", self.model_name_label)
        
        self.model_type_label = QLabel("")
        details_layout.addRow("Type:", self.model_type_label)
        
        self.model_status_label = QLabel("")
        details_layout.addRow("Status:", self.model_status_label)
        
        self.model_performance_label = QLabel("")
        details_layout.addRow("Performance:", self.model_performance_label)
        
        layout.addWidget(details_group)
        
        # Model actions
        actions_group = QGroupBox("Model Actions")
        actions_layout = QGridLayout(actions_group)
        
        self.test_model_btn = QPushButton("🧪 Test Model")
        self.test_model_btn.clicked.connect(self.test_model)
        actions_layout.addWidget(self.test_model_btn, 0, 0)
        
        self.update_model_btn = QPushButton("🔄 Update Model")
        self.update_model_btn.clicked.connect(self.update_model)
        actions_layout.addWidget(self.update_model_btn, 0, 1)
        
        self.export_model_btn = QPushButton("📤 Export Model")
        self.export_model_btn.clicked.connect(self.export_model)
        actions_layout.addWidget(self.export_model_btn, 1, 0)
        
        self.import_model_btn = QPushButton("📥 Import Model")
        self.import_model_btn.clicked.connect(self.import_model)
        actions_layout.addWidget(self.import_model_btn, 1, 1)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_ai_analytics_tab", "Consolidated Ai Studio Panel")
    def create_ai_analytics_tab(self) -> QWidget:
        """Create the AI analytics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("📈 AI Analytics - Monitor AI Performance")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Analytics overview
        overview_group = QGroupBox("AI Performance Overview")
        overview_layout = QGridLayout(overview_group)
        
        self.total_queries_label = QLabel("0")
        overview_layout.addWidget(QLabel("Total Queries:"), 0, 0)
        overview_layout.addWidget(self.total_queries_label, 0, 1)
        
        self.success_rate_label = QLabel("0%")
        overview_layout.addWidget(QLabel("Success Rate:"), 0, 2)
        overview_layout.addWidget(self.success_rate_label, 0, 3)
        
        self.avg_response_time_label = QLabel("0ms")
        overview_layout.addWidget(QLabel("Avg Response Time:"), 1, 0)
        overview_layout.addWidget(self.avg_response_time_label, 1, 1)
        
        self.active_models_label = QLabel("0")
        overview_layout.addWidget(QLabel("Active Models:"), 1, 2)
        overview_layout.addWidget(self.active_models_label, 1, 3)
        
        layout.addWidget(overview_group)
        
        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(5)
        self.metrics_table.setHorizontalHeaderLabels([
            "Model", "Queries", "Success Rate", "Avg Time", "Last Used"
        ])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        metrics_layout.addWidget(self.metrics_table)
        
        layout.addWidget(metrics_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent AI Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(200)
        activity_layout.addWidget(self.activity_log)
        
        layout.addWidget(activity_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_progress_section", "Consolidated Ai Studio Panel")
    def create_progress_section(self, layout: QVBoxLayout):
        """Create the progress section."""
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("AI Studio ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    @debug_button("connect_signals", "Consolidated Ai Studio Panel")
    def connect_signals(self):
        """Connect all signals."""
        # Connect AI response signals
        self.ai_response_received.connect(self.on_ai_response)
        self.training_completed.connect(self.on_training_completed)
        self.data_extracted.connect(self.on_data_extracted)
        self.model_updated.connect(self.on_model_update)
    
    @debug_button("load_ai_state", "Consolidated Ai Studio Panel")
    def load_ai_state(self):
        """Load AI state from memory."""
        try:
            # Load conversations
            self.load_conversations()
            
            # Load models
            self.refresh_models()
            
            # Load analytics
            self.load_analytics()
            
            self.status_label.setText("AI Studio loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI state: {e}")
            self.status_label.setText(f"Error loading AI state: {e}")
    
    @debug_button("load_conversations", "Consolidated Ai Studio Panel")
    def load_conversations(self):
        """Load recent conversations for context."""
        try:
            conversations = self.memory_manager.get_recent_conversations(limit=20)
            
            self.conversation_combo.clear()
            self.conversation_combo.addItem("Select a conversation...")
            
            for conv in conversations:
                title = conv.get('title', 'Untitled')[:50]
                self.conversation_combo.addItem(title, conv.get('id'))
            
            self.status_label.setText(f"Loaded {len(conversations)} conversations")
            
        except Exception as e:
            logger.error(f"Failed to load conversations: {e}")
            self.status_label.setText(f"Error loading conversations: {e}")
    
    @debug_button("refresh_models", "Consolidated Ai Studio Panel")
    def refresh_models(self):
        """Refresh the models list."""
        try:
            # This would load actual models from storage
            # For now, we'll use placeholder data
            models = [
                {"name": "Conversational AI", "type": "Chat", "status": "Active"},
                {"name": "Code Analysis", "type": "Analysis", "status": "Active"},
                {"name": "Training Assistant", "type": "Training", "status": "Inactive"}
            ]
            
            self.models_list.clear()
            for model in models:
                item = QListWidgetItem(f"{model['name']} ({model['type']})")
                item.setData(Qt.ItemDataRole.UserRole, model)
                self.models_list.addItem(item)
            
            self.status_label.setText(f"Loaded {len(models)} models")
            
        except Exception as e:
            logger.error(f"Failed to refresh models: {e}")
            self.status_label.setText(f"Error refreshing models: {e}")
    
    @debug_button("load_analytics", "Consolidated Ai Studio Panel")
    def load_analytics(self):
        """Load AI analytics data."""
        try:
            # Placeholder analytics data
            self.total_queries_label.setText("1,234")
            self.success_rate_label.setText("95.2%")
            self.avg_response_time_label.setText("1.2s")
            self.active_models_label.setText("3")
            
            # Load recent activity
            self.activity_log.append("2024-01-15 10:30: AI query executed successfully")
            self.activity_log.append("2024-01-15 10:25: Model training completed")
            self.activity_log.append("2024-01-15 10:20: Data extraction finished")
            
        except Exception as e:
            logger.error(f"Failed to load analytics: {e}")
    
    # Chat functionality
    @debug_button("send_chat_message", "Consolidated Ai Studio Panel")
    def send_chat_message(self):
        """Send a chat message to the AI."""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        # Add user message to chat
        self.chat_history.append(f"<b>You:</b> {message}")
        self.chat_input.clear()
        
        # Simulate AI response (replace with actual AI call)
        self.status_label.setText("AI is thinking...")
        QTimer.singleShot(2000, lambda: self.simulate_ai_response(message))
    
    def simulate_ai_response(self, message: str):
        """Simulate an AI response (replace with actual AI integration)."""
        response = f"AI Response to: {message}\n\nThis is a simulated response. In the actual implementation, this would call the ChatGPT API or other AI service."
        self.chat_history.append(f"<b>AI:</b> {response}")
        self.status_label.setText("AI Studio ready")
    
    # Query functionality
    @debug_button("execute_ai_query", "Consolidated Ai Studio Panel")
    def execute_ai_query(self):
        """Execute an AI query."""
        query = self.query_input.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a query")
            return
        
        query_type = self.query_type_combo.currentText()
        context = self.context_combo.currentText()
        
        self.status_label.setText(f"Executing {query_type} query...")
        self.query_results.clear()
        
        # Simulate query execution (replace with actual AI call)
        QTimer.singleShot(3000, lambda: self.simulate_query_result(query, query_type, context))
    
    def simulate_query_result(self, query: str, query_type: str, context: str):
        """Simulate query result (replace with actual AI integration)."""
        result = f"""
Query Type: {query_type}
Context: {context}
Query: {query}

Result:
This is a simulated AI query result. In the actual implementation, this would:
1. Send the query to the appropriate AI model
2. Process the response
3. Format and display the results

The query would be analyzed based on the selected context and query type.
"""
        self.query_results.setPlainText(result)
        self.status_label.setText("Query executed successfully")
    
    # Training functionality
    @debug_button("start_agent_training", "Consolidated Ai Studio Panel")
    def start_agent_training(self):
        """Start agent training."""
        model_name = self.model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Warning", "Please enter a model name")
            return
        
        self.start_training_btn.setEnabled(False)
        self.stop_training_btn.setEnabled(True)
        self.training_progress.setValue(0)
        self.training_status.setText("Training started...")
        
        # Simulate training progress
        self.training_timer = QTimer()
        self.training_timer.timeout.connect(self.update_training_progress)
        self.training_timer.start(1000)
    
    @debug_button("update_training_progress", "Consolidated Ai Studio Panel")
    def update_training_progress(self):
        """Update training progress."""
        current = self.training_progress.value()
        if current < 100:
            self.training_progress.setValue(current + 10)
            self.training_status.setText(f"Training... {current + 10}%")
        else:
            self.training_timer.stop()
            self.training_completed.emit({"model_name": self.model_name_input.text(), "success": True})
    
    @debug_button("stop_agent_training", "Consolidated Ai Studio Panel")
    def stop_agent_training(self):
        """Stop agent training."""
        if hasattr(self, 'training_timer'):
            self.training_timer.stop()
        
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.training_status.setText("Training stopped")
    
    @debug_button("on_training_completed", "Consolidated Ai Studio Panel")
    def on_training_completed(self, result: dict):
        """Handle training completion."""
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.training_status.setText("Training completed successfully")
        
        self.training_results.append(f"Training completed for {result['model_name']}")
        self.status_label.setText("Training completed")
    
    # Data extraction functionality
    @debug_button("extract_training_data", "Consolidated Ai Studio Panel")
    def extract_training_data(self):
        """Extract training data."""
        self.status_label.setText("Extracting training data...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate extraction progress
        QTimer.singleShot(2000, lambda: self.simulate_data_extraction())
    
    def simulate_data_extraction(self):
        """Simulate data extraction (replace with actual extraction)."""
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        
        # Update statistics
        self.total_conversations_label.setText("454")
        self.total_code_snippets_label.setText("1,234")
        self.total_patterns_label.setText("89")
        self.total_skills_label.setText("15")
        
        self.status_label.setText("Training data extracted successfully")
        self.data_extracted.emit({"conversations": 454, "code_snippets": 1234})
    
    @debug_button("export_training_data", "Consolidated Ai Studio Panel")
    def export_training_data(self):
        """Export training data."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Training Data", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            # Simulate export
            self.status_label.setText("Training data exported successfully")
    
    # Model management functionality
    @debug_button("on_model_selected", "Consolidated Ai Studio Panel")
    def on_model_selected(self, item: QListWidgetItem):
        """Handle model selection."""
        model_data = item.data(Qt.ItemDataRole.UserRole)
        if model_data:
            self.model_name_label.setText(model_data['name'])
            self.model_type_label.setText(model_data['type'])
            self.model_status_label.setText(model_data['status'])
            self.model_performance_label.setText("95.2% accuracy")
    
    @debug_button("add_model", "Consolidated Ai Studio Panel")
    def add_model(self):
        """Add a new model."""
        # Simulate adding a model
        self.status_label.setText("Model added successfully")
        self.refresh_models()
    
    @debug_button("remove_model", "Consolidated Ai Studio Panel")
    def remove_model(self):
        """Remove selected model."""
        current_item = self.models_list.currentItem()
        if current_item:
            self.models_list.takeItem(self.models_list.row(current_item))
            self.status_label.setText("Model removed successfully")
    
    @debug_button("test_model", "Consolidated Ai Studio Panel")
    def test_model(self):
        """Test selected model."""
        self.status_label.setText("Model test completed")
    
    @debug_button("update_model", "Consolidated Ai Studio Panel")
    def update_model(self):
        """Update selected model."""
        self.status_label.setText("Model updated successfully")
    
    @debug_button("export_model", "Consolidated Ai Studio Panel")
    def export_model(self):
        """Export selected model."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Model", "", "Model Files (*.model);;All Files (*)"
        )
        if file_path:
            self.status_label.setText("Model exported successfully")
    
    @debug_button("import_model", "Consolidated Ai Studio Panel")
    def import_model(self):
        """Import a model."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Model", "", "Model Files (*.model);;All Files (*)"
        )
        if file_path:
            self.status_label.setText("Model imported successfully")
            self.refresh_models()
    
    # Quick actions
    @debug_button("analyze_current_work", "Consolidated Ai Studio Panel")
    def analyze_current_work(self):
        """Analyze current work."""
        self.chat_input.setText("Please analyze my current work and provide insights")
        self.send_chat_message()
    
    @debug_button("get_suggestions", "Consolidated Ai Studio Panel")
    def get_suggestions(self):
        """Get suggestions."""
        self.chat_input.setText("What suggestions do you have for improving my current project?")
        self.send_chat_message()
    
    @debug_button("explain_concepts", "Consolidated Ai Studio Panel")
    def explain_concepts(self):
        """Explain concepts."""
        self.chat_input.setText("Please explain the key concepts in my current work")
        self.send_chat_message()
    
    @debug_button("get_debug_help", "Consolidated Ai Studio Panel")
    def get_debug_help(self):
        """Get debug help."""
        self.chat_input.setText("I need help debugging my current code. Can you assist?")
        self.send_chat_message()
    
    # Signal handlers
    @debug_button("on_ai_response", "Consolidated Ai Studio Panel")
    def on_ai_response(self, response_data: dict):
        """Handle AI response."""
        self.status_label.setText("AI response received")
    
    @debug_button("on_data_extracted", "Consolidated Ai Studio Panel")
    def on_data_extracted(self, extraction_data: dict):
        """Handle data extraction completion."""
        self.status_label.setText("Data extraction completed")
    
    @debug_button("on_model_update", "Consolidated Ai Studio Panel")
    def on_model_update(self):
        """Refresh function now handled by Global Refresh Manager."""
        try:
            # This function is now handled by the Global Refresh Manager
            # The refresh operation will be queued and processed automatically
            logger.info(f"Refresh request for UI handled by Global Refresh Manager")
            
        except Exception as e:
            logger.error(f"Error in refresh function: {e}")

    @debug_button("create_enhanced_devlog_tab", "Consolidated Ai Studio Panel")
    def create_enhanced_devlog_tab(self) -> QWidget:
        """Create the enhanced devlog tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("📝 Enhanced Devlog - Context-Aware Development Logs")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Generate comprehensive development logs that leverage your work patterns, conversation history, and MMORPG progress.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Quick access to enhanced devlog panel
        access_group = QGroupBox("Enhanced Devlog Access")
        access_layout = QVBoxLayout(access_group)
        
        access_desc = QLabel("The Enhanced Devlog Generator provides context-aware development logs using the advanced template system.")
        access_desc.setWordWrap(True)
        access_layout.addWidget(access_desc)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.open_devlog_btn = QPushButton("Open Enhanced Devlog")
        self.open_devlog_btn.clicked.connect(self.open_enhanced_devlog)
        actions_layout.addWidget(self.open_devlog_btn)
        
        self.quick_devlog_btn = QPushButton("Quick Devlog")
        self.quick_devlog_btn.clicked.connect(self.quick_devlog)
        actions_layout.addWidget(self.quick_devlog_btn)
        
        self.devlog_history_btn = QPushButton("Devlog History")
        self.devlog_history_btn.clicked.connect(self.show_devlog_history)
        actions_layout.addWidget(self.devlog_history_btn)
        
        actions_layout.addStretch()
        access_layout.addLayout(actions_layout)
        
        layout.addWidget(access_group)
        
        # Template information
        template_group = QGroupBox("Enhanced Template Features")
        template_layout = QVBoxLayout(template_group)
        
        features = [
            "Work Pattern Analysis - Leverages your development patterns and technology preferences",
            "MMORPG Integration - Incorporates your current skill levels and progress",
            "Relevant History - Analyzes conversation history for context",
            "Achievement Tracking - Tracks development milestones and XP gains",
            "Context-Aware Generation - Creates logs tailored to your workflow"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setWordWrap(True)
            template_layout.addWidget(label)
        
        layout.addWidget(template_group)
        
        # Recent devlogs
        recent_group = QGroupBox("Recent Devlogs")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_devlogs_list = QListWidget()
        self.recent_devlogs_list.setMaximumHeight(150)
        recent_layout.addWidget(self.recent_devlogs_list)
        
        layout.addWidget(recent_group)
        layout.addStretch()
        
        return tab
    
    # Enhanced Devlog methods
    @debug_button("open_enhanced_devlog", "Consolidated Ai Studio Panel")
    def open_enhanced_devlog(self):
        """Open the enhanced devlog panel."""
        QMessageBox.information(self, "Enhanced Devlog", "Enhanced devlog panel would open here")
    
    @debug_button("quick_devlog", "Consolidated Ai Studio Panel")
    def quick_devlog(self):
        """Quick generate a devlog."""
        QMessageBox.information(self, "Quick Devlog", "Quick devlog generation would start here")
    
    @debug_button("show_devlog_history", "Consolidated Ai Studio Panel")
    def show_devlog_history(self):
        """Show devlog history."""
        QMessageBox.information(self, "Devlog History", "Devlog history would be displayed here") 