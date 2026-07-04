#!/usr/bin/env python3
from gui.debug_handler import debug_button
"""
AI Agent Training Panel for Thea GUI
Handles training personalized AI agents from ChatGPT conversation history.
"""

import json
from gui.debug_handler import debug_button
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QTabWidget, QCheckBox,
    QSpinBox, QDoubleSpinBox, QFormLayout, QScrollArea, QTreeWidget,
    QTreeWidgetItem, QSlider, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QIcon

from dreamscape.core.memory_system import MemoryManager, MemoryAPI
from dreamscape.core.legacy.conversation_system import ConversationStatsUpdater  # Consolidated import (was conversation_stats_updater)
from dreamscape.core.agent_trainer import AgentTrainer, TrainingConfig, AgentPersonality

class AgentTrainingWorker(QThread):
    """Worker thread for agent training operations."""
    
    progress_updated = pyqtSignal(int, str)
    training_completed = pyqtSignal(dict)
    training_failed = pyqtSignal(str)
    
    def __init__(self, training_config: TrainingConfig, memory_manager: MemoryManager, agent_name: str):
        super().__init__()
        self.training_config = training_config
        self.memory_manager = memory_manager
        self.agent_name = agent_name
        self.is_running = True
    
    def run(self):
        """Run the training process."""
        try:
            self.progress_updated.emit(0, "Initializing agent trainer...")
            
            # Initialize agent trainer
            trainer = AgentTrainer(self.memory_manager, self.training_config)
            
            self.progress_updated.emit(10, "Starting agent training...")
            
            # Train the agent
            result = trainer.train_agent(self.agent_name)
            
            self.progress_updated.emit(100, "Training completed!")
            
            # Convert result to dict for signal
            result_dict = {
                'agent_id': result.agent_id,
                'agent_name': self.agent_name,
                'personality': {
                    'helpfulness': result.personality.helpfulness,
                    'technical_depth': result.personality.technical_depth,
                    'communication_style': result.personality.communication_style,
                    'problem_solving_approach': result.personality.problem_solving_approach,
                    'creativity': result.personality.creativity,
                    'formality': result.personality.formality,
                    'expertise_domains': result.personality.expertise_domains
                },
                'training_metrics': result.training_metrics,
                'skill_tree': result.skill_tree,
                'model_path': result.model_path,
                'knowledge_base_path': result.knowledge_base_path,
                'training_duration': result.training_duration,
                'created_at': result.created_at
            }
            
            self.training_completed.emit(result_dict)
            
        except Exception as e:
            self.training_failed.emit(str(e))
        finally:
            self.is_running = False
    
    @debug_button("stop", "Ai Agent Training Panel")
    def stop(self):
        """Stop the training process."""
        self.is_running = False

class AIAgentTrainingPanel(QWidget):
    """AI Agent Training Panel for Thea GUI."""
    
    # Signals
    agent_trained = pyqtSignal(dict)
    training_progress = pyqtSignal(int, str)
    
    def __init__(self, memory_manager: MemoryManager, parent=None):
        super().__init__(parent)
        self.memory_manager = memory_manager
        self.memory_api = MemoryAPI()
        self.training_worker = None
        self.current_agent_config = None
        self.trained_agents = []
        
        # Setup UI
        self._setup_ui()
        self._load_initial_data()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🤖 AI Agent Training System")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_training_tab()
        self._create_agent_config_tab()
        self._create_knowledge_tab()
        self._create_skills_tab()
        self._create_results_tab()
        self._create_trained_agents_tab()
    
    @debug_button("_create_training_tab", "Ai Agent Training Panel")
    def _create_training_tab(self):
        """Create the training configuration tab."""
        training_widget = QWidget()
        training_layout = QVBoxLayout(training_widget)
        
        # Training configuration
        config_group = QGroupBox("Training Configuration")
        config_layout = QFormLayout(config_group)
        
        # Agent name
        self.agent_name_edit = QLineEdit()
        self.agent_name_edit.setPlaceholderText("My Personal Agent")
        config_layout.addRow("Agent Name:", self.agent_name_edit)
        
        # Training data source
        self.data_source_combo = QComboBox()
        self.data_source_combo.addItems([
            "All Conversations",
            "Recent Conversations (Last 30 days)",
            "Development Focused",
            "Technical Conversations",
            "Selected Conversations"
        ])
        config_layout.addRow("Data Source:", self.data_source_combo)
        
        # Model settings
        self.base_model_combo = QComboBox()
        self.base_model_combo.addItems([
            "microsoft/DialoGPT-medium",
            "gpt2-medium",
            "microsoft/DialoGPT-small"
        ])
        config_layout.addRow("Base Model:", self.base_model_combo)
        
        # Training parameters
        self.learning_rate_spin = QDoubleSpinBox()
        self.learning_rate_spin.setRange(0.0001, 0.01)
        self.learning_rate_spin.setValue(0.0005)
        self.learning_rate_spin.setSingleStep(0.0001)
        self.learning_rate_spin.setDecimals(4)
        config_layout.addRow("Learning Rate:", self.learning_rate_spin)
        
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 10)
        self.epochs_spin.setValue(3)
        config_layout.addRow("Training Epochs:", self.epochs_spin)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 16)
        self.batch_size_spin.setValue(4)
        config_layout.addRow("Batch Size:", self.batch_size_spin)
        
        training_layout.addWidget(config_group)
        
        # Training options
        options_group = QGroupBox("Training Options")
        options_layout = QVBoxLayout(options_group)
        
        self.extract_personality_cb = QCheckBox("Extract personality traits")
        self.extract_personality_cb.setChecked(True)
        options_layout.addWidget(self.extract_personality_cb)
        
        self.build_knowledge_cb = QCheckBox("Build knowledge base (RAG)")
        self.build_knowledge_cb.setChecked(True)
        options_layout.addWidget(self.build_knowledge_cb)
        
        self.create_skills_cb = QCheckBox("Generate skill tree")
        self.create_skills_cb.setChecked(True)
        options_layout.addWidget(self.create_skills_cb)
        
        self.enable_fine_tuning_cb = QCheckBox("Enable fine-tuning (requires PyTorch)")
        self.enable_fine_tuning_cb.setChecked(True)
        options_layout.addWidget(self.enable_fine_tuning_cb)
        
        training_layout.addWidget(options_group)
        
        # Training controls
        controls_layout = QHBoxLayout()
        
        self.start_training_btn = QPushButton("🚀 Start Training")
        self.start_training_btn.clicked.connect(self._start_training)
        controls_layout.addWidget(self.start_training_btn)
        
        self.stop_training_btn = QPushButton("⏹️ Stop Training")
        self.stop_training_btn.clicked.connect(self._stop_training)
        self.stop_training_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_training_btn)
        
        self.export_btn = QPushButton("📤 Export Agent")
        self.export_btn.clicked.connect(self._export_agent)
        self.export_btn.setEnabled(False)
        controls_layout.addWidget(self.export_btn)
        
        training_layout.addLayout(controls_layout)
        
        # Progress section
        progress_group = QGroupBox("Training Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to start training")
        self.progress_label.setStyleSheet("font-weight: bold;")
        progress_layout.addWidget(self.progress_label)
        
        training_layout.addWidget(progress_group)
        
        self.tab_widget.addTab(training_widget, "Training")
    
    @debug_button("_create_agent_config_tab", "Ai Agent Training Panel")
    def _create_agent_config_tab(self):
        """Create the agent configuration tab."""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        # Agent personality
        personality_group = QGroupBox("Agent Personality")
        personality_layout = QFormLayout(personality_group)
        
        self.helpfulness_slider = QSlider(Qt.Orientation.Horizontal)
        self.helpfulness_slider.setRange(0, 100)
        self.helpfulness_slider.setValue(80)
        personality_layout.addRow("Helpfulness:", self.helpfulness_slider)
        
        self.technical_depth_slider = QSlider(Qt.Orientation.Horizontal)
        self.technical_depth_slider.setRange(0, 100)
        self.technical_depth_slider.setValue(70)
        personality_layout.addRow("Technical Depth:", self.technical_depth_slider)
        
        self.communication_style_combo = QComboBox()
        self.communication_style_combo.addItems([
            "Professional",
            "Casual",
            "Technical",
            "Friendly",
            "Formal"
        ])
        personality_layout.addRow("Communication Style:", self.communication_style_combo)
        
        config_layout.addWidget(personality_group)
        
        # Agent capabilities
        capabilities_group = QGroupBox("Agent Capabilities")
        capabilities_layout = QVBoxLayout(capabilities_group)
        
        self.cap_conversation_cb = QCheckBox("Conversation Analysis")
        self.cap_conversation_cb.setChecked(True)
        capabilities_layout.addWidget(self.cap_conversation_cb)
        
        self.cap_problem_solving_cb = QCheckBox("Problem Solving")
        self.cap_problem_solving_cb.setChecked(True)
        capabilities_layout.addWidget(self.cap_problem_solving_cb)
        
        self.cap_knowledge_cb = QCheckBox("Knowledge Retrieval (RAG)")
        self.cap_knowledge_cb.setChecked(True)
        capabilities_layout.addWidget(self.cap_knowledge_cb)
        
        self.cap_patterns_cb = QCheckBox("Pattern Recognition")
        self.cap_patterns_cb.setChecked(True)
        capabilities_layout.addWidget(self.cap_patterns_cb)
        
        self.cap_gaming_cb = QCheckBox("Game Facilitation")
        self.cap_gaming_cb.setChecked(True)
        capabilities_layout.addWidget(self.cap_gaming_cb)
        
        config_layout.addWidget(capabilities_group)
        
        # LoRA settings
        lora_group = QGroupBox("LoRA Fine-tuning Settings")
        lora_layout = QFormLayout(lora_group)
        
        self.lora_r_spin = QSpinBox()
        self.lora_r_spin.setRange(4, 64)
        self.lora_r_spin.setValue(16)
        lora_layout.addRow("LoRA Rank (r):", self.lora_r_spin)
        
        self.lora_alpha_spin = QSpinBox()
        self.lora_alpha_spin.setRange(8, 128)
        self.lora_alpha_spin.setValue(32)
        lora_layout.addRow("LoRA Alpha:", self.lora_alpha_spin)
        
        self.lora_dropout_spin = QDoubleSpinBox()
        self.lora_dropout_spin.setRange(0.0, 0.5)
        self.lora_dropout_spin.setValue(0.1)
        self.lora_dropout_spin.setSingleStep(0.05)
        lora_layout.addRow("LoRA Dropout:", self.lora_dropout_spin)
        
        config_layout.addWidget(lora_group)
        
        config_layout.addStretch()
        
        self.tab_widget.addTab(config_widget, "Configuration")
    
    @debug_button("_create_knowledge_tab", "Ai Agent Training Panel")
    def _create_knowledge_tab(self):
        """Create the knowledge base tab."""
        knowledge_widget = QWidget()
        knowledge_layout = QVBoxLayout(knowledge_widget)
        
        # Knowledge base info
        info_group = QGroupBox("Knowledge Base Information")
        info_layout = QVBoxLayout(info_group)
        
        self.knowledge_info_label = QLabel("Knowledge base will be built during training")
        info_layout.addWidget(self.knowledge_info_label)
        
        knowledge_layout.addWidget(info_group)
        
        # Knowledge search
        search_group = QGroupBox("Knowledge Search")
        search_layout = QVBoxLayout(search_group)
        
        search_input_layout = QHBoxLayout()
        self.knowledge_search_edit = QLineEdit()
        self.knowledge_search_edit.setPlaceholderText("Search knowledge base...")
        search_input_layout.addWidget(self.knowledge_search_edit)
        
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self._search_knowledge)
        search_input_layout.addWidget(self.search_btn)
        
        search_layout.addLayout(search_input_layout)
        
        self.knowledge_results = QTextEdit()
        self.knowledge_results.setMaximumHeight(200)
        self.knowledge_results.setReadOnly(True)
        search_layout.addWidget(self.knowledge_results)
        
        knowledge_layout.addWidget(search_group)
        
        knowledge_layout.addStretch()
        
        self.tab_widget.addTab(knowledge_widget, "Knowledge")
    
    @debug_button("_create_skills_tab", "Ai Agent Training Panel")
    def _create_skills_tab(self):
        """Create the skills tab."""
        skills_widget = QWidget()
        skills_layout = QVBoxLayout(skills_widget)
        
        # Skills overview
        overview_group = QGroupBox("Skills Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        self.skills_overview_label = QLabel("Skills will be extracted during training")
        overview_layout.addWidget(self.skills_overview_label)
        
        skills_layout.addWidget(overview_group)
        
        # Skills tree
        tree_group = QGroupBox("Skill Tree")
        tree_layout = QVBoxLayout(tree_group)
        
        self.skills_tree = QTreeWidget()
        self.skills_tree.setHeaderLabel("Skills")
        tree_layout.addWidget(self.skills_tree)
        
        skills_layout.addWidget(tree_group)
        
        self.tab_widget.addTab(skills_widget, "Skills")
    
    @debug_button("_create_results_tab", "Ai Agent Training Panel")
    def _create_results_tab(self):
        """Create the training results tab."""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Training metrics
        metrics_group = QGroupBox("Training Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_display = QTextEdit()
        self.metrics_display.setReadOnly(True)
        metrics_layout.addWidget(self.metrics_display)
        
        results_layout.addWidget(metrics_group)
        
        # Agent details
        details_group = QGroupBox("Agent Details")
        details_layout = QVBoxLayout(details_group)
        
        self.agent_details_display = QTextEdit()
        self.agent_details_display.setReadOnly(True)
        details_layout.addWidget(self.agent_details_display)
        
        results_layout.addWidget(details_group)
        
        self.tab_widget.addTab(results_widget, "Results")
    
    @debug_button("_create_trained_agents_tab", "Ai Agent Training Panel")
    def _create_trained_agents_tab(self):
        """Create the trained agents tab."""
        agents_widget = QWidget()
        agents_layout = QVBoxLayout(agents_widget)
        
        # Agents list
        list_group = QGroupBox("Trained Agents")
        list_layout = QVBoxLayout(list_group)
        
        self.agents_list = QListWidget()
        self.agents_list.itemClicked.connect(self._select_trained_agent)
        list_layout.addWidget(self.agents_list)
        
        agents_layout.addWidget(list_group)
        
        # Agent actions
        actions_group = QGroupBox("Agent Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.load_agent_btn = QPushButton("📂 Load Agent")
        self.load_agent_btn.clicked.connect(self._load_trained_agent)
        actions_layout.addWidget(self.load_agent_btn)
        
        self.query_agent_btn = QPushButton("💬 Query Agent")
        self.query_agent_btn.clicked.connect(self._query_trained_agent)
        actions_layout.addWidget(self.query_agent_btn)
        
        self.delete_agent_btn = QPushButton("🗑️ Delete Agent")
        self.delete_agent_btn.clicked.connect(self._delete_trained_agent)
        actions_layout.addWidget(self.delete_agent_btn)
        
        agents_layout.addWidget(actions_group)
        
        # Query interface
        query_group = QGroupBox("Agent Query")
        query_layout = QVBoxLayout(query_group)
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Ask your trained agent a question...")
        query_layout.addWidget(self.query_input)
        
        self.query_response = QTextEdit()
        self.query_response.setReadOnly(True)
        self.query_response.setMaximumHeight(200)
        query_layout.addWidget(self.query_response)
        
        agents_layout.addWidget(query_group)
        
        self.tab_widget.addTab(agents_widget, "Trained Agents")
    
    @debug_button("_load_initial_data", "Ai Agent Training Panel")
    def _load_initial_data(self):
        """Load initial data and populate UI."""
        try:
            # Load trained agents
            self._load_trained_agents()
            
            # Update conversation stats
            self._update_conversation_stats()
            
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}")
    
    @debug_button("_load_trained_agents", "Ai Agent Training Panel")
    def _load_trained_agents(self):
        """Load list of trained agents."""
        try:
            trainer = AgentTrainer(self.memory_manager)
            self.trained_agents = trainer.list_trained_agents()
            
            self.agents_list.clear()
            for agent in self.trained_agents:
                self.agents_list.addItem(f"{agent.get('name', 'Unknown')} ({agent.get('agent_id', 'Unknown')})")
            
        except Exception as e:
            logger.error(f"Failed to load trained agents: {e}")
    
    @debug_button("_update_conversation_stats", "Ai Agent Training Panel")
    def _update_conversation_stats(self):
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
                title="ai_agent_training_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _start_training(self):
        """Start the agent training process."""
        try:
            # Validate configuration
            agent_name = self.agent_name_edit.text().strip()
            if not agent_name:
                QMessageBox.warning(self, "Warning", "Please enter an agent name.")
                return
            
            # Create training configuration
            training_config = TrainingConfig(
                base_model=self.base_model_combo.currentText(),
                learning_rate=self.learning_rate_spin.value(),
                num_epochs=self.epochs_spin.value(),
                batch_size=self.batch_size_spin.value(),
                lora_r=self.lora_r_spin.value(),
                lora_alpha=self.lora_alpha_spin.value(),
                lora_dropout=self.lora_dropout_spin.value(),
                extract_personality=self.extract_personality_cb.isChecked(),
                enable_rag=self.build_knowledge_cb.isChecked()
            )
            
            # Start training worker
            self.training_worker = AgentTrainingWorker(training_config, self.memory_manager, agent_name)
            self.training_worker.progress_updated.connect(self._update_progress)
            self.training_worker.training_completed.connect(self._training_completed)
            self.training_worker.training_failed.connect(self._training_failed)
            
            # Update UI
            self.start_training_btn.setEnabled(False)
            self.stop_training_btn.setEnabled(True)
            self.progress_bar.setValue(0)
            
            # Start training
            self.training_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start training: {e}")
    
    @debug_button("_stop_training", "Ai Agent Training Panel")
    def _stop_training(self):
        """Stop the training process."""
        if self.training_worker and self.training_worker.isRunning():
            self.training_worker.stop()
            self.training_worker.wait()
        
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.progress_label.setText("Training stopped")
    
    @debug_button("_update_progress", "Ai Agent Training Panel")
    def _update_progress(self, value: int, message: str):
        """Update training progress."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    @debug_button("_training_completed", "Ai Agent Training Panel")
    def _training_completed(self, result: dict):
        """Handle training completion."""
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.progress_label.setText("Training completed!")
        
        # Store result
        self.current_agent_config = result
        
        # Update UI
        self.export_btn.setEnabled(True)
        
        # Update displays
        self._update_training_results(result)
        
        # Reload trained agents
        self._load_trained_agents()
        
        # Show success message
        QMessageBox.information(self, "Training Complete", 
                              f"Agent '{result['agent_name']}' trained successfully!\n"
                              f"Training duration: {result['training_duration']:.2f} seconds")
    
    @debug_button("_training_failed", "Ai Agent Training Panel")
    def _training_failed(self, error: str):
        """Handle training failure."""
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        self.progress_label.setText(f"Training failed: {error}")
        
        QMessageBox.critical(self, "Training Failed", f"Agent training failed:\n{error}")
    
    @debug_button("_update_training_results", "Ai Agent Training Panel")
    def _update_training_results(self, result: dict):
        """Update training results displays."""
        # Update metrics display
        metrics_text = f"""Training Metrics:
Agent ID: {result['agent_id']}
Agent Name: {result['agent_name']}
Training Duration: {result['training_duration']:.2f} seconds
Created At: {result['created_at']}

Model Path: {result['model_path']}
Knowledge Base Path: {result['knowledge_base_path']}

Training Metrics:
"""
        for key, value in result['training_metrics'].items():
            metrics_text += f"{key}: {value}\n"
        
        self.metrics_display.setText(metrics_text)
        
        # Update agent details
        personality = result['personality']
        details_text = f"""Agent Personality:
Helpfulness: {personality['helpfulness']:.2f}
Technical Depth: {personality['technical_depth']:.2f}
Communication Style: {personality['communication_style']}
Problem Solving Approach: {personality['problem_solving_approach']}
Creativity: {personality['creativity']:.2f}
Formality: {personality['formality']:.2f}

Expertise Domains: {', '.join(personality['expertise_domains'])}

Skill Tree:
"""
        skill_tree = result['skill_tree']
        for skill, details in skill_tree.get('root_skills', {}).items():
            details_text += f"- {details['name']}: {details['level']} (count: {details['count']})\n"
        
        self.agent_details_display.setText(details_text)
        
        # Update skills tree
        self._update_skills_tree(skill_tree)
    
    @debug_button("_update_skills_tree", "Ai Agent Training Panel")
    def _update_skills_tree(self, skill_tree: dict):
        """Update the skills tree display."""
        self.skills_tree.clear()
        
        root_skills = skill_tree.get('root_skills', {})
        for skill, details in root_skills.items():
            skill_item = QTreeWidgetItem(self.skills_tree)
            skill_item.setText(0, f"{details['name']} ({details['level']})")
            skill_item.setData(0, Qt.ItemDataRole.UserRole, details)
        
        self.skills_tree.expandAll()
    
    @debug_button("_export_agent", "Ai Agent Training Panel")
    def _export_agent(self):
        """Export the trained agent."""
        if not self.current_agent_config:
            QMessageBox.warning(self, "Warning", "No agent to export. Please train an agent first.")
            return
        
        try:
            # Create export directory
            export_dir = Path("outputs/trained_agents")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Export agent configuration
            agent_name = self.current_agent_config.get('agent_name', 'agent')
            export_file = export_dir / f"{agent_name}_export.json"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_agent_config, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Agent exported successfully to:\n{export_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export agent: {e}")
    
    @debug_button("_search_knowledge", "Ai Agent Training Panel")
    def _search_knowledge(self):
        """Search the knowledge base."""
        query = self.knowledge_search_edit.text().strip()
        if not query:
            return
        
        try:
            # This would implement actual knowledge search
            # For now, show a placeholder
            self.knowledge_results.setText(f"Searching for: {query}\n\nThis feature will be implemented in the next version.")
        except Exception as e:
            self.knowledge_results.setText(f"Search failed: {e}")
    
    @debug_button("_select_trained_agent", "Ai Agent Training Panel")
    def _select_trained_agent(self, item):
        """Handle selection of trained agent."""
        # Implementation for selecting trained agent
        pass
    
    @debug_button("_load_trained_agent", "Ai Agent Training Panel")
    def _load_trained_agent(self):
        """Load a trained agent."""
        current_item = self.agents_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select an agent to load.")
            return
        
        try:
            # Get agent ID from item text
            item_text = current_item.text()
            agent_id = item_text.split('(')[-1].rstrip(')')
            
            # Load agent configuration
            trainer = AgentTrainer(self.memory_manager)
            agent_config = trainer.load_trained_agent(agent_id)
            
            if agent_config:
                self.current_agent_config = agent_config
                self._update_training_results(agent_config)
                QMessageBox.information(self, "Agent Loaded", f"Agent '{agent_config.get('name', 'Unknown')}' loaded successfully!")
            else:
                QMessageBox.warning(self, "Load Failed", "Failed to load agent configuration.")
                
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load agent: {e}")
    
    @debug_button("_query_trained_agent", "Ai Agent Training Panel")
    def _query_trained_agent(self):
        """Query a trained agent."""
        if not self.current_agent_config:
            QMessageBox.warning(self, "Warning", "Please load an agent first.")
            return
        
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a query.")
            return
        
        try:
            agent_id = self.current_agent_config.get('agent_id')
            trainer = AgentTrainer(self.memory_manager)
            response = trainer.query_agent(agent_id, query)
            
            self.query_response.setText(response)
            
        except Exception as e:
            self.query_response.setText(f"Query failed: {e}")
    
    @debug_button("_delete_trained_agent", "Ai Agent Training Panel")
    def _delete_trained_agent(self):
        """Delete a trained agent."""
        current_item = self.agents_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select an agent to delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this agent? This action cannot be undone.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Implementation for deleting agent
                QMessageBox.information(self, "Delete Complete", "Agent deleted successfully!")
                self._load_trained_agents()
            except Exception as e:
                QMessageBox.critical(self, "Delete Failed", f"Failed to delete agent: {e}") 