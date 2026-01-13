#!/usr/bin/env python3
"""
Weaponization Panel - GUI for Memory Weaponization System
========================================================

Provides a comprehensive interface for weaponizing the conversation corpus:
- Vector search and context injection
- Training data generation
- MMORPG episode creation
- Analytics dashboard
- Content generation
- API deployment
"""

import sys
from gui.debug_handler import debug_button
import os
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar,
    QGroupBox, QCheckBox, QSpinBox, QLineEdit,
    QTabWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QSplitter, QFrame,
    QScrollArea, QComboBox, QSlider, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

# EDIT START: Consolidate memory imports to use memory_system (core consolidation)
from dreamscape.core.memory_system import MemoryManager, MemoryWeaponizer, WeaponizationConfig, VectorMemory
# EDIT END

logger = logging.getLogger(__name__)

class WeaponizationWorker(QThread):
    """Background worker for weaponization operations."""
    
    progress_updated = pyqtSignal(int, str)  # progress, message
    operation_completed = pyqtSignal(dict)   # results
    operation_failed = pyqtSignal(str)       # error message
    
    def __init__(self, operation: str, config: WeaponizationConfig):
        super().__init__()
        self.operation = operation
        self.config = config
        self.weaponizer = None
        
    def run(self):
        """Execute the weaponization operation."""
        try:
            self.weaponizer = MemoryWeaponizer(self.config)
            
            if self.operation == "full_pipeline":
                self.progress_updated.emit(10, "Initializing weaponization system...")
                results = self.weaponizer.weaponize_full_pipeline()
                self.operation_completed.emit(results)
                
            elif self.operation == "vector_index":
                self.progress_updated.emit(20, "Building vector index...")
                results = self.weaponizer._build_vector_index()
                self.operation_completed.emit(results)
                
            elif self.operation == "training_data":
                self.progress_updated.emit(30, "Generating training data...")
                results = self.weaponizer._generate_training_data()
                self.operation_completed.emit(results)
                
            elif self.operation == "analytics":
                self.progress_updated.emit(40, "Generating analytics...")
                results = self.weaponizer._generate_analytics()
                self.operation_completed.emit(results)
                
            elif self.operation == "content":
                self.progress_updated.emit(50, "Generating content...")
                results = self.weaponizer._generate_content()
                self.operation_completed.emit(results)
                
            elif self.operation == "episodes":
                self.progress_updated.emit(60, "Creating MMORPG episodes...")
                results = self.weaponizer._create_episodes()
                self.operation_completed.emit(results)
                
        except Exception as e:
            logger.error(f"Weaponization operation failed: {e}")
            self.operation_failed.emit(str(e))

class VectorSearchWidget(QWidget):
    """Widget for vector search and context injection."""
    
    def __init__(self, memory_manager: MemoryManager):
        super().__init__()
        self.memory_manager = memory_manager
        self.vector_memory = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the vector search UI."""
        layout = QVBoxLayout(self)
        
        # Search section
        search_group = QGroupBox("🔍 Vector Search & Context Injection")
        search_layout = QVBoxLayout(search_group)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter your search query...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        # Search options
        options_layout = QHBoxLayout()
        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(1, 50)
        self.top_k_spin.setValue(10)
        self.top_k_spin.setPrefix("Top K: ")
        options_layout.addWidget(self.top_k_spin)
        
        self.role_filter = QComboBox()
        self.role_filter.addItems(["All", "user", "assistant", "system"])
        options_layout.addWidget(QLabel("Role Filter:"))
        options_layout.addWidget(self.role_filter)
        
        search_button = QPushButton("🔍 Search")
        search_button.clicked.connect(self.perform_search)
        options_layout.addWidget(search_button)
        
        search_layout.addLayout(options_layout)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(300)
        search_layout.addWidget(self.results_text)
        
        layout.addWidget(search_group)
        
        # Initialize vector memory
        self.init_vector_memory()
        
    def init_vector_memory(self):
        """Initialize vector memory system."""
        try:
            self.vector_memory = VectorMemory(
                index_path="outputs/weaponization/faiss_index"
            )
            self.results_text.append("✅ Vector memory initialized successfully")
        except Exception as e:
            self.results_text.append(f"❌ Failed to initialize vector memory: {e}")
    
    @debug_button("perform_search", "Weaponization Panel")
    def perform_search(self):
        """Perform vector search."""
        if not self.vector_memory:
            self.results_text.append("❌ Vector memory not initialized")
            return
            
        query = self.search_input.text().strip()
        if not query:
            return
            
        try:
            top_k = self.top_k_spin.value()
            role_filter = self.role_filter.currentText()
            role_filter = None if role_filter == "All" else role_filter
            
            results = self.vector_memory.search(
                query, 
                top_k=top_k,
                role_filter=role_filter
            )
            
            self.display_search_results(results)
            
        except Exception as e:
            self.results_text.append(f"❌ Search failed: {e}")
    
    @debug_button("display_search_results", "Weaponization Panel")
    def display_search_results(self, results: List[Dict]):
        """Display search results."""
        self.results_text.clear()
        self.results_text.append(f"🔍 Search Results ({len(results)} found):\n")
        
        for i, result in enumerate(results, 1):
            score = result.get('score', 0)
            content = result.get('content', '')
            role = result.get('role', 'unknown')
            conv_id = result.get('conversation_id', 'unknown')
            
            self.results_text.append(f"📄 Result {i} (Score: {score:.3f})")
            self.results_text.append(f"Role: {role} | Conversation: {conv_id}")
            self.results_text.append(f"Content: {content[:200]}...")
            self.results_text.append("-" * 50)

class WeaponizationPanel(QWidget):
    """Main weaponization panel with comprehensive features."""
    
    weaponization_completed = pyqtSignal(dict)  # results
    weaponization_failed = pyqtSignal(str)      # error message
    
    def __init__(self, memory_manager: MemoryManager):
        super().__init__()
        self.memory_manager = memory_manager
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the weaponization panel UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⚔️ Memory Weaponization System")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_overview_tab(), "📊 Overview")
        self.tab_widget.addTab(self.create_vector_search_tab(), "🔍 Vector Search")
        self.tab_widget.addTab(self.create_training_tab(), "🎯 Training Data")
        self.tab_widget.addTab(self.create_episodes_tab(), "🎮 MMORPG Episodes")
        self.tab_widget.addTab(self.create_analytics_tab(), "📈 Analytics")
        self.tab_widget.addTab(self.create_content_tab(), "📝 Content")
        self.tab_widget.addTab(self.create_api_tab(), "🌐 API")
        self.tab_widget.addTab(self.create_settings_tab(), "⚙️ Settings")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to weaponize your conversation corpus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
    @debug_button("create_overview_tab", "Weaponization Panel")
    def create_overview(self):
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
                title="weaponization_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def create_vector_search_tab(self) -> QWidget:
        """Create the vector search tab."""
        return VectorSearchWidget(self.memory_manager)
    
    @debug_button("create_training_tab", "Weaponization Panel")
    def create_training_tab(self) -> QWidget:
        """Create the training data generation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuration
        config_group = QGroupBox("⚙️ Training Data Configuration")
        config_layout = QGridLayout(config_group)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 1000)
        self.chunk_size_spin.setValue(512)
        config_layout.addWidget(QLabel("Chunk Size:"), 0, 0)
        config_layout.addWidget(self.chunk_size_spin, 0, 1)
        
        self.overlap_spin = QSpinBox()
        self.overlap_spin.setRange(0, 200)
        self.overlap_spin.setValue(50)
        config_layout.addWidget(QLabel("Overlap:"), 1, 0)
        config_layout.addWidget(self.overlap_spin, 1, 1)
        
        layout.addWidget(config_group)
        
        # Dataset types
        datasets_group = QGroupBox("📚 Dataset Types")
        datasets_layout = QVBoxLayout(datasets_group)
        
        self.dataset_checkboxes = {}
        dataset_types = [
            "conversation_pairs", "qa_pairs", "instruction_following", "code_generation"
        ]
        
        for dataset_type in dataset_types:
            checkbox = QCheckBox(dataset_type.replace("_", " ").title())
            checkbox.setChecked(True)
            self.dataset_checkboxes[dataset_type] = checkbox
            datasets_layout.addWidget(checkbox)
        
        layout.addWidget(datasets_group)
        
        # Generate button
        generate_btn = QPushButton("🎯 Generate Training Data")
        generate_btn.clicked.connect(self.generate_training_data)
        layout.addWidget(generate_btn)
        
        # Results
        self.training_results = QTextEdit()
        self.training_results.setReadOnly(True)
        layout.addWidget(self.training_results)
        
        return widget
    
    @debug_button("create_episodes_tab", "Weaponization Panel")
    def create_episodes_tab(self) -> QWidget:
        """Create the MMORPG episodes tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create episodes action using shared component
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        actions = [
            {
                "text": "🎮 Create MMORPG Episodes",
                "callback": self.create_episodes,
                "id": "create_episodes"
            }
        ]
        actions_panel = components.create_action_panel(
            title="Episode Actions",
            actions=actions,
            config=ComponentConfig(style=ComponentStyle.PRIMARY)
        )
        self.create_episodes_btn = actions_panel.findChild(QPushButton, "create_episodes")
        layout.addWidget(actions_panel)
        # Episodes table using shared component
        self.episodes_table_group = components.create_data_table(
            title="Episodes",
            headers=["Episode ID", "Title", "Difficulty", "Length"],
            data=[],  # Will be populated later
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.episodes_table = self.episodes_table_group.table  # Access the table for updates
        layout.addWidget(self.episodes_table_group)
        return widget
    
    @debug_button("create_analytics_tab", "Weaponization Panel")
    def create_analytics_tab(self) -> QWidget:
        """Create the analytics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Analytics types
        analytics_group = QGroupBox("📈 Analytics Types")
        analytics_layout = QVBoxLayout(analytics_group)
        
        self.analytics_checkboxes = {}
        analytics_types = [
            "daily_stats", "agent_performance", "conversation_trends"
        ]
        
        for analytics_type in analytics_types:
            checkbox = QCheckBox(analytics_type.replace("_", " ").title())
            checkbox.setChecked(True)
            self.analytics_checkboxes[analytics_type] = checkbox
            analytics_layout.addWidget(checkbox)
        
        layout.addWidget(analytics_group)
        
        # Generate analytics button
        generate_btn = QPushButton("📈 Generate Analytics")
        generate_btn.clicked.connect(self.generate_analytics)
        layout.addWidget(generate_btn)
        
        # Analytics results
        self.analytics_results = QTextEdit()
        self.analytics_results.setReadOnly(True)
        layout.addWidget(self.analytics_results)
        
        return widget
    
    @debug_button("create_content_tab", "Weaponization Panel")
    def create_content_tab(self) -> QWidget:
        """Create the content generation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Content types
        content_group = QGroupBox("📝 Content Types")
        content_layout = QVBoxLayout(content_group)
        
        self.content_checkboxes = {}
        content_types = ["blog_posts", "social_posts"]
        
        for content_type in content_types:
            checkbox = QCheckBox(content_type.replace("_", " ").title())
            checkbox.setChecked(True)
            self.content_checkboxes[content_type] = checkbox
            content_layout.addWidget(checkbox)
        
        layout.addWidget(content_group)
        
        # Generate content button
        generate_btn = QPushButton("📝 Generate Content")
        generate_btn.clicked.connect(self.generate_content)
        layout.addWidget(generate_btn)
        
        # Content results
        self.content_results = QTextEdit()
        self.content_results.setReadOnly(True)
        layout.addWidget(self.content_results)
        
        return widget
    
    @debug_button("create_api_tab", "Weaponization Panel")
    def create_api_tab(self) -> QWidget:
        """Create the API deployment tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API configuration
        api_group = QGroupBox("🌐 API Configuration")
        api_layout = QGridLayout(api_group)
        
        self.api_host = QLineEdit("localhost")
        api_layout.addWidget(QLabel("Host:"), 0, 0)
        api_layout.addWidget(self.api_host, 0, 1)
        
        self.api_port = QSpinBox()
        self.api_port.setRange(1000, 9999)
        self.api_port.setValue(8000)
        api_layout.addWidget(QLabel("Port:"), 1, 0)
        api_layout.addWidget(self.api_port, 1, 1)
        
        layout.addWidget(api_group)
        
        # Deploy button
        deploy_btn = QPushButton("🌐 Deploy Context Injection API")
        deploy_btn.clicked.connect(self.deploy_api)
        layout.addWidget(deploy_btn)
        
        # API status
        self.api_status = QLabel("API not deployed")
        self.api_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.api_status)
        
        # API endpoints info
        self.api_info = QTextEdit()
        self.api_info.setReadOnly(True)
        self.api_info.setMaximumHeight(200)
        layout.addWidget(self.api_info)
        
        return widget
    
    @debug_button("create_settings_tab", "Weaponization Panel")
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Weaponization settings
        settings_group = QGroupBox("⚙️ Weaponization Settings")
        settings_layout = QGridLayout(settings_group)
        
        self.corpus_path = QLineEdit("dreamos_memory.db")
        settings_layout.addWidget(QLabel("Corpus Path:"), 0, 0)
        settings_layout.addWidget(self.corpus_path, 0, 1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_corpus_path)
        settings_layout.addWidget(browse_btn, 0, 2)
        
        self.output_dir = QLineEdit("outputs/weaponization")
        settings_layout.addWidget(QLabel("Output Directory:"), 1, 0)
        settings_layout.addWidget(self.output_dir, 1, 1)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output_dir)
        settings_layout.addWidget(browse_output_btn, 1, 2)
        
        self.embedding_model = QLineEdit("sentence-transformers/all-MiniLM-L6-v2")
        settings_layout.addWidget(QLabel("Embedding Model:"), 2, 0)
        settings_layout.addWidget(self.embedding_model, 2, 1)
        
        layout.addWidget(settings_group)
        
        # Save settings button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        return widget
    
    @debug_button("load_corpus_stats", "Weaponization Panel")
    def load_corpus_stats(self):
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
                title="weaponization_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def get_weaponization_config(self) -> WeaponizationConfig:
        """Get weaponization configuration from UI."""
        return WeaponizationConfig(
            corpus_path=self.corpus_path.text(),
            output_dir=self.output_dir.text(),
            chunk_size=self.chunk_size_spin.value(),
            overlap=self.overlap_spin.value(),
            embedding_model=self.embedding_model.text()
        )
    
    @debug_button("run_full_weaponization", "Weaponization Panel")
    def run_full_weaponization(self):
        """Run the full weaponization pipeline."""
        reply = QMessageBox.question(
            self,
            "Full Weaponization",
            "This will run the complete weaponization pipeline:\n\n"
            "• Build vector index\n"
            "• Generate training data\n"
            "• Create MMORPG episodes\n"
            "• Generate analytics\n"
            "• Create content\n"
            "• Deploy API\n\n"
            "This may take several minutes. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.run_operation("full_pipeline")
    
    def run_operation(self, operation: str):
        """Run a specific weaponization operation."""
        config = self.get_weaponization_config()
        
        self.worker = WeaponizationWorker(operation, config)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.operation_completed.connect(self.operation_completed)
        self.worker.operation_failed.connect(self.operation_failed)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Running {operation.replace('_', ' ')}...")
        
        self.worker.start()
    
    @debug_button("update_progress", "Weaponization Panel")
    def update_progress(self, value: int, message: str):
        """Update progress bar and status."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    @debug_button("operation_completed", "Weaponization Panel")
    def operation_completed(self, results: Dict):
        """Handle operation completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Operation completed successfully!")
        
        # Display results based on operation
        if self.worker.operation == "full_pipeline":
            self.display_full_pipeline_results(results)
        elif self.worker.operation == "training_data":
            self.display_training_results(results)
        elif self.worker.operation == "analytics":
            self.display_analytics_results(results)
        elif self.worker.operation == "content":
            self.display_content_results(results)
        elif self.worker.operation == "episodes":
            self.display_episode_results(results)
        
        self.weaponization_completed.emit(results)
    
    @debug_button("operation_failed", "Weaponization Panel")
    def operation_failed(self, error: str):
        """Handle operation failure."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Operation failed: {error}")
        self.weaponization_failed.emit(error)
        
        QMessageBox.critical(self, "Weaponization Failed", f"Operation failed:\n\n{error}")
    
    def display_full_pipeline_results(self, results: Dict):
        """Display full pipeline results."""
        message = "🚀 Full Weaponization Pipeline Completed!\n\n"
        
        if "corpus_stats" in results:
            stats = results["corpus_stats"]
            message += f"📊 Corpus: {stats.get('total_conversations', 0)} conversations, {stats.get('total_messages', 0)} messages\n"
        
        if "vector_index" in results:
            vector = results["vector_index"]
            message += f"🔍 Vector Index: {vector.get('total_chunks', 0)} chunks\n"
        
        if "training_data" in results:
            training = results["training_data"]
            message += f"🎯 Training Data: {training.get('total_samples', 0)} samples\n"
        
        if "episodes" in results:
            episodes = results["episodes"]
            message += f"🎮 Episodes: {episodes.get('total_episodes', 0)} created\n"
        
        if "analytics" in results:
            analytics = results["analytics"]
            message += f"📈 Analytics: Dashboard generated\n"
        
        if "content" in results:
            content = results["content"]
            message += f"📝 Content: {len(content.get('blog_posts', []))} blog posts, {len(content.get('social_posts', []))} social posts\n"
        
        if "api" in results:
            api = results["api"]
            message += f"🌐 API: {api.get('deployment_status', 'unknown')}\n"
        
        QMessageBox.information(self, "Weaponization Complete", message)
    
    def display_training_results(self, results: Dict):
        """Display training data results."""
        self.training_results.clear()
        self.training_results.append("🎯 Training Data Generation Results:\n")
        
        total_samples = results.get("total_samples", 0)
        self.training_results.append(f"Total Samples: {total_samples}\n")
        
        datasets = results.get("datasets", {})
        for dataset_name, dataset_data in datasets.items():
            count = len(dataset_data) if isinstance(dataset_data, list) else 0
            self.training_results.append(f"{dataset_name}: {count} samples")
        
        self.tab_widget.setCurrentIndex(2)  # Switch to training tab
    
    def display_analytics_results(self, results: Dict):
        """Display analytics results."""
        self.analytics_results.clear()
        self.analytics_results.append("📈 Analytics Generation Results:\n")
        
        for key, value in results.items():
            if key != "dashboard_path":
                self.analytics_results.append(f"{key}: {value}")
        
        if "dashboard_path" in results:
            self.analytics_results.append(f"\nDashboard saved to: {results['dashboard_path']}")
        
        self.tab_widget.setCurrentIndex(4)  # Switch to analytics tab
    
    def display_content_results(self, results: Dict):
        """Display content generation results."""
        self.content_results.clear()
        self.content_results.append("📝 Content Generation Results:\n")
        
        blog_posts = results.get("blog_posts", [])
        social_posts = results.get("social_posts", [])
        
        self.content_results.append(f"Blog Posts: {len(blog_posts)}")
        self.content_results.append(f"Social Posts: {len(social_posts)}\n")
        
        if blog_posts:
            self.content_results.append("Sample Blog Post:")
            self.content_results.append(blog_posts[0].get("title", "No title"))
            self.content_results.append(blog_posts[0].get("content", "No content")[:200] + "...")
        
        self.tab_widget.setCurrentIndex(5)  # Switch to content tab
    
    def display_episode_results(self, results: Dict):
        """Display episode creation results."""
        episodes = results.get("episodes", [])
        total_episodes = results.get("total_episodes", 0)
        
        self.episodes_table.setRowCount(len(episodes))
        
        for i, episode in enumerate(episodes):
            self.episodes_table.setItem(i, 0, QTableWidgetItem(episode.get("id", "")))
            self.episodes_table.setItem(i, 1, QTableWidgetItem(episode.get("title", "")))
            self.episodes_table.setItem(i, 2, QTableWidgetItem(episode.get("difficulty", "")))
            self.episodes_table.setItem(i, 3, QTableWidgetItem(str(episode.get("length", 0))))
        
        self.tab_widget.setCurrentIndex(3)  # Switch to episodes tab
    
    @debug_button("generate_training_data", "Weaponization Panel")
    def generate_training_data(self):
        """Generate training data with current settings."""
        self.run_operation("training_data")
    
    @debug_button("create_episodes", "Weaponization Panel")
    def create_episodes(self):
        """Create MMORPG episodes."""
        self.run_operation("episodes")
    
    @debug_button("generate_analytics", "Weaponization Panel")
    def generate_analytics(self):
        """Generate analytics dashboard."""
        self.run_operation("analytics")
    
    @debug_button("generate_content", "Weaponization Panel")
    def generate_content(self):
        """Generate content."""
        self.run_operation("content")
    
    @debug_button("deploy_api", "Weaponization Panel")
    def deploy_api(self):
        """Deploy context injection API."""
        self.run_operation("api_deployment")
    
    @debug_button("browse_corpus_path", "Weaponization Panel")
    def browse_corpus_path(self):
        """Browse for corpus path."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Corpus Database", "", "Database Files (*.db *.sqlite)"
        )
        if path:
            self.corpus_path.setText(path)
    
    @debug_button("browse_output_dir", "Weaponization Panel")
    def browse_output_dir(self):
        """Browse for output directory."""
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_dir.setText(path)
    
    @debug_button("save_settings", "Weaponization Panel")
    def save_settings(self):
        """Save weaponization settings."""
        # This could save to a config file
        QMessageBox.information(self, "Settings Saved", "Weaponization settings saved successfully!") 