#!/usr/bin/env python3
"""
Enhanced Devlog Panel
=====================

This panel provides advanced devlog generation using the enhanced template
that leverages human-AI workflow context, work patterns, and MMORPG state.
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
    QHeaderView, QAbstractItemView, QDateEdit, QCalendarWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QDate
from PyQt6.QtGui import QFont, QIcon, QPixmap

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from dreamscape.core.template_engine import render_template
from dreamscape.core.mmorpg.mmorpg_system import EnhancedProgressSystem
from dreamscape.core.utils.context_utils import extract_last_yaml_block

logger = logging.getLogger(__name__)

class DevlogGenerationWorker(QThread):
    """Worker thread for devlog generation."""
    
    generation_completed = pyqtSignal(dict)  # Generated devlog data
    generation_failed = pyqtSignal(str)      # Error message
    progress_updated = pyqtSignal(int)       # Progress percentage
    
    def __init__(self, template_data: dict, memory_manager: MemoryManager, mmorpg_engine: MMORPGEngine, use_yaml: bool = True):
        super().__init__()
        self.template_data = template_data
        self.memory_manager = memory_manager
        self.mmorpg_engine = mmorpg_engine
        self.use_yaml = use_yaml  # Toggle for YAML vs context-driven generation
    
    def run(self):
        """Generate the devlog using YAML-driven or context-driven approach."""
        try:
            self.progress_updated.emit(10)
            
            # Try YAML-driven generation first if enabled
            if self.use_yaml:
                devlog_content, context, generation_method = self._try_yaml_generation()
                if devlog_content:
                    self.progress_updated.emit(100)
                    result = {
                        'content': devlog_content,
                        'context': context,
                        'timestamp': context.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        'generation_method': generation_method
                    }
                    self.generation_completed.emit(result)
                    return
            
            # Fallback to context-driven generation
            self.progress_updated.emit(20)
            devlog_content, context = self._context_driven_generation()
            
            self.progress_updated.emit(100)
            
            result = {
                'content': devlog_content,
                'context': context,
                'timestamp': context['timestamp'],
                'generation_method': 'context-driven'
            }
            
            self.generation_completed.emit(result)
            
        except Exception as e:
            logger.error(f"Devlog generation failed: {e}")
            self.generation_failed.emit(str(e))
    
    def _try_yaml_generation(self):
        """Attempt YAML-driven devlog generation."""
        try:
            # Get the most recent conversation
            conversations = self.memory_manager.get_recent_conversations(limit=1)
            if not conversations:
                return None, None, None
            
            conversation = conversations[0]
            conversation_text = conversation.get('content', '')
            
            # Extract YAML block from conversation
            structured = extract_last_yaml_block(conversation_text)
            if not structured:
                return None, None, None
            
            # Use Jinja2 template with structured YAML data
            from jinja2 import Environment, FileSystemLoader
            template_dir = Path(__file__).parent.parent.parent.parent / "templates"
            env = Environment(loader=FileSystemLoader(str(template_dir)))
            
            try:
                template = env.get_template('devlog_template.md.j2')
                devlog_content = template.render(**structured)
                
                # Prepare context for result
                context = {
                    **structured,
                    'conversation_title': conversation.get('title', 'Untitled'),
                    'conversation_id': conversation.get('id', 'unknown'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'generation_method': 'yaml-driven'
                }
                
                return devlog_content, context, 'yaml-driven'
                
            except Exception as e:
                logger.warning(f"YAML template rendering failed: {e}")
                return None, None, None
                
        except Exception as e:
            logger.error(f"YAML generation failed: {e}")
            return None, None, None
    
    def _context_driven_generation(self):
        """Fallback to context-driven devlog generation."""
        # Gather context data
        work_patterns = self._get_work_patterns()
        self.progress_updated.emit(40)
        
        mmorpg_state = self._get_mmorpg_state()
        self.progress_updated.emit(60)
        
        current_skills = self._get_current_skills()
        self.progress_updated.emit(80)
        
        relevant_history = self._get_relevant_history()
        self.progress_updated.emit(90)
        
        # Prepare template context
        context = {
            **self.template_data,
            'work_patterns': work_patterns,
            'mmorpg_state': mmorpg_state,
            'current_skills': current_skills,
            'relevant_history': relevant_history,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Render template
        template_path = Path(__file__).parent.parent.parent.parent / "templates" / "prompts" / "enhanced_devlog_generator.j2"
        devlog_content = render_template(str(template_path), context)
        
        return devlog_content, context
    
    def _get_work_patterns(self) -> Dict[str, Any]:
        """Get work patterns from conversation history."""
        try:
            conversations = self.memory_manager.get_recent_conversations(limit=100)
            
            # Analyze technologies mentioned
            technologies = {}
            topics = {}
            challenges = {}
            
            for conv in conversations:
                content = conv.get('content', '').lower()
                
                # Technology detection
                tech_keywords = ['python', 'javascript', 'api', 'gui', 'database', 'docker', 'kubernetes', 'aws', 'azure']
                for tech in tech_keywords:
                    if tech in content:
                        technologies[tech] = technologies.get(tech, 0) + 1
                
                # Topic detection
                topic_keywords = ['development', 'debugging', 'testing', 'deployment', 'optimization', 'architecture']
                for topic in topic_keywords:
                    if topic in content:
                        topics[topic] = topics.get(topic, 0) + 1
                
                # Challenge detection
                challenge_keywords = ['error', 'bug', 'issue', 'problem', 'fix', 'resolve']
                for challenge in challenge_keywords:
                    if challenge in content:
                        challenges[challenge] = challenges.get(challenge, 0) + 1
            
            return {
                'technologies': technologies,
                'topics': topics,
                'challenges': challenges,
                'total_conversations': len(conversations)
            }
            
        except Exception as e:
            logger.error(f"Error getting work patterns: {e}")
            return {}
    
    def _get_mmorpg_state(self) -> Dict[str, Any]:
        """Get current MMORPG state."""
        try:
            player = self.mmorpg_engine.get_player()
            skills = self.mmorpg_engine.get_skills()
            
            return {
                'level': getattr(player, 'level', 1),
                'xp': getattr(player, 'xp', 0),
                'active_skills': len(skills) if skills else 0,
                'recent_achievements': [],  # Placeholder
                'active_quests': []  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error getting MMORPG state: {e}")
            return {}
    
    def _get_current_skills(self) -> Dict[str, int]:
        """Get current skill levels."""
        try:
            skills = self.mmorpg_engine.get_skills()
            if isinstance(skills, dict):
                return skills
            elif isinstance(skills, list):
                return {skill.get('name', f'Skill_{i}'): skill.get('level', 1) for i, skill in enumerate(skills)}
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting current skills: {e}")
            return {}
    
    def _get_relevant_history(self) -> List[Dict[str, Any]]:
        """Get relevant conversation history."""
        try:
            conversations = self.memory_manager.get_recent_conversations(limit=10)
            
            relevant_history = []
            for conv in conversations:
                # Calculate relevance score based on content
                content = conv.get('content', '').lower()
                relevance_score = 0
                
                # Score based on development-related keywords
                dev_keywords = ['code', 'development', 'bug', 'fix', 'implement', 'design', 'architecture']
                for keyword in dev_keywords:
                    if keyword in content:
                        relevance_score += 1
                
                if relevance_score > 0:
                    relevant_history.append({
                        'title': conv.get('title', 'Untitled'),
                        'timestamp': conv.get('timestamp', 'Unknown'),
                        'content': conv.get('content', ''),
                        'relevance_score': relevance_score
                    })
            
            # Sort by relevance score
            relevant_history.sort(key=lambda x: x['relevance_score'], reverse=True)
            return relevant_history[:5]  # Top 5 most relevant
            
        except Exception as e:
            logger.error(f"Error getting relevant history: {e}")
            return []

class EnhancedDevlogPanel(QWidget):
    """Enhanced Devlog Panel with context-aware generation."""
    
    # Signals
    devlog_generated = pyqtSignal(dict)  # Generated devlog data
    devlog_saved = pyqtSignal(str)       # File path where saved
    devlog_exported = pyqtSignal(str)    # Export format and path
    
    def __init__(self, memory_manager: MemoryManager = None, mmorpg_engine: MMORPGEngine = None):
        super().__init__()
        self.memory_manager = memory_manager or MemoryManager()
        self.mmorpg_engine = mmorpg_engine or MMORPGEngine()
        self.enhanced_progress = EnhancedProgressSystem(self.mmorpg_engine, self.memory_manager)
        
        # Devlog state
        self.current_devlog = None
        self.generation_worker = None
        self.devlog_history = []
        
        self.init_ui()
        self.load_devlog_history()
    
    def init_ui(self):
        """Initialize the enhanced devlog user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Enhanced Devlog Generator - Context-Aware Development Logs")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Generate comprehensive development logs that leverage your work patterns, conversation history, and MMORPG progress.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_generation_tab(), "Generate Devlog")
        self.tab_widget.addTab(self.create_context_tab(), "Context Analysis")
        self.tab_widget.addTab(self.create_history_tab(), "Devlog History")
        self.tab_widget.addTab(self.create_templates_tab(), "Templates")
        
        # Progress section
        self.create_progress_section(layout)
        
        # Connect signals
        self.connect_signals()
    
    @debug_button("create_generation_tab", "Enhanced Devlog Panel")
    def create_generation_tab(self) -> QWidget:
        """Create the devlog generation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("🚀 Generate Enhanced Devlog")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Conversation selection
        conv_group = QGroupBox("Select Development Session")
        conv_layout = QVBoxLayout(conv_group)
        
        self.conversation_combo = QComboBox()
        self.conversation_combo.addItem("Select a conversation...")
        conv_layout.addWidget(self.conversation_combo)
        
        self.load_conversations_btn = QPushButton("🔄 Load Recent Conversations")
        self.load_conversations_btn.clicked.connect(self.load_conversations)
        conv_layout.addWidget(self.load_conversations_btn)
        
        layout.addWidget(conv_group)
        
        # Generation options
        options_group = QGroupBox("Generation Options")
        options_layout = QFormLayout(options_group)
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems([
            "Development Session",
            "Code Review",
            "Bug Fix",
            "Feature Implementation",
            "Architecture Discussion",
            "Learning Session",
            "Problem Solving",
            "System Integration"
        ])
        options_layout.addRow("Session Type:", self.analysis_type_combo)
        
        self.include_context_cb = QCheckBox("Include Work Pattern Context")
        self.include_context_cb.setChecked(True)
        options_layout.addRow("Context Options:", self.include_context_cb)
        
        self.include_skills_cb = QCheckBox("Include Skill Development")
        self.include_skills_cb.setChecked(True)
        options_layout.addRow("", self.include_skills_cb)
        
        self.include_history_cb = QCheckBox("Include Relevant History")
        self.include_history_cb.setChecked(True)
        options_layout.addRow("", self.include_history_cb)
        
        # YAML-driven generation toggle
        self.use_yaml_cb = QCheckBox("🎯 Use YAML-driven Generation (Recommended)")
        self.use_yaml_cb.setChecked(True)
        self.use_yaml_cb.setToolTip("Extract structured YAML from conversation for precise devlog generation. Falls back to context-driven if no YAML found.")
        options_layout.addRow("Generation Method:", self.use_yaml_cb)
        
        layout.addWidget(options_group)
        
        # Generation controls
        controls_group = QGroupBox("Generation Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        button_layout = QHBoxLayout()
        
        self.generate_devlog_btn = QPushButton("🚀 Generate Enhanced Devlog")
        self.generate_devlog_btn.clicked.connect(self.generate_devlog)
        button_layout.addWidget(self.generate_devlog_btn)
        
        self.quick_generate_btn = QPushButton("⚡ Quick Generate")
        self.quick_generate_btn.clicked.connect(self.quick_generate)
        button_layout.addWidget(self.quick_generate_btn)
        
        self.batch_generate_btn = QPushButton("📦 Batch Generate")
        self.batch_generate_btn.clicked.connect(self.batch_generate)
        button_layout.addWidget(self.batch_generate_btn)
        
        controls_layout.addLayout(button_layout)
        
        # Preview area
        preview_layout = QHBoxLayout()
        
        preview_label = QLabel("Generated Devlog Preview:")
        preview_layout.addWidget(preview_label)
        
        self.preview_btn = QPushButton("👁️ Preview")
        self.preview_btn.clicked.connect(self.preview_devlog)
        preview_layout.addWidget(self.preview_btn)
        
        controls_layout.addLayout(preview_layout)
        
        layout.addWidget(controls_group)
        
        # Generated content
        content_group = QGroupBox("Generated Devlog")
        content_layout = QVBoxLayout(content_group)
        
        self.generated_content = QTextEdit()
        self.generated_content.setReadOnly(True)
        self.generated_content.setPlaceholderText("Generated devlog will appear here...")
        content_layout.addWidget(self.generated_content)
        
        # Content actions
        actions_layout = QHBoxLayout()
        
        self.save_devlog_btn = QPushButton("💾 Save Devlog")
        self.save_devlog_btn.clicked.connect(self.save_devlog)
        actions_layout.addWidget(self.save_devlog_btn)
        
        self.export_devlog_btn = QPushButton("📤 Export")
        self.export_devlog_btn.clicked.connect(self.export_devlog)
        actions_layout.addWidget(self.export_devlog_btn)
        
        self.copy_devlog_btn = QPushButton("📋 Copy")
        self.copy_devlog_btn.clicked.connect(self.copy_devlog)
        actions_layout.addWidget(self.copy_devlog_btn)
        
        actions_layout.addStretch()
        content_layout.addLayout(actions_layout)
        
        layout.addWidget(content_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_context_tab", "Enhanced Devlog Panel")
    def create_context_tab(self) -> QWidget:
        """Create the context analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("🎯 Context Analysis - Work Patterns & Development State")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Work patterns
        patterns_group = QGroupBox("Work Patterns Analysis")
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.patterns_table = QTableWidget()
        self.patterns_table.setColumnCount(3)
        self.patterns_table.setHorizontalHeaderLabels(["Category", "Item", "Frequency"])
        self.patterns_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        patterns_layout.addWidget(self.patterns_table)
        
        self.refresh_patterns_btn = QPushButton("🔄 Refresh Patterns")
        self.refresh_patterns_btn.clicked.connect(self.refresh_work_patterns)
        patterns_layout.addWidget(self.refresh_patterns_btn)
        
        layout.addWidget(patterns_group)
        
        # MMORPG state
        state_group = QGroupBox("Current Development State")
        state_layout = QGridLayout(state_group)
        
        self.level_label = QLabel("Loading...")
        state_layout.addWidget(QLabel("Platform Level:"), 0, 0)
        state_layout.addWidget(self.level_label, 0, 1)
        
        self.xp_label = QLabel("Loading...")
        state_layout.addWidget(QLabel("Development XP:"), 0, 2)
        state_layout.addWidget(self.xp_label, 0, 3)
        
        self.skills_label = QLabel("Loading...")
        state_layout.addWidget(QLabel("Active Skills:"), 1, 0)
        state_layout.addWidget(self.skills_label, 1, 1)
        
        self.achievements_label = QLabel("Loading...")
        state_layout.addWidget(QLabel("Recent Achievements:"), 1, 2)
        state_layout.addWidget(self.achievements_label, 1, 3)
        
        layout.addWidget(state_group)
        
        # Skill development
        skills_group = QGroupBox("Skill Development Status")
        skills_layout = QVBoxLayout(skills_group)
        
        self.skills_list = QListWidget()
        skills_layout.addWidget(self.skills_list)
        
        layout.addWidget(skills_group)
        
        # Relevant history
        history_group = QGroupBox("Relevant Development History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        layout.addWidget(history_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_history_tab", "Enhanced Devlog Panel")
    def create_history_tab(self) -> QWidget:
        """Create the devlog history tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("📋 Devlog History - Past Generated Logs")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # History table
        history_group = QGroupBox("Generated Devlogs")
        history_layout = QVBoxLayout(history_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Session Type", "Conversation", "Context Used", "Method", "Actions"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)
        
        # History controls
        controls_layout = QHBoxLayout()
        
        self.refresh_history_btn = QPushButton("🔄 Refresh History")
        self.refresh_history_btn.clicked.connect(self.refresh_devlog_history)
        controls_layout.addWidget(self.refresh_history_btn)
        
        self.export_history_btn = QPushButton("📤 Export History")
        self.export_history_btn.clicked.connect(self.export_devlog_history)
        controls_layout.addWidget(self.export_history_btn)
        
        self.clear_history_btn = QPushButton("🗑️ Clear History")
        self.clear_history_btn.clicked.connect(self.clear_devlog_history)
        controls_layout.addWidget(self.clear_history_btn)
        
        controls_layout.addStretch()
        history_layout.addLayout(controls_layout)
        
        layout.addWidget(history_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_templates_tab", "Enhanced Devlog Panel")
    def create_templates_tab(self) -> QWidget:
        """Create the templates tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("📄 Devlog Templates - Customize Your Logs")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Template selection
        template_group = QGroupBox("Available Templates")
        template_layout = QVBoxLayout(template_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Enhanced Devlog Generator (Default)",
            "Quick Development Summary",
            "Detailed Technical Analysis",
            "Learning Session Log",
            "Problem-Solving Journey",
            "Custom Template"
        ])
        template_layout.addWidget(self.template_combo)
        
        # Template preview
        preview_group = QGroupBox("Template Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.template_preview)
        
        layout.addWidget(template_group)
        layout.addWidget(preview_group)
        
        # Template actions
        actions_group = QGroupBox("Template Actions")
        actions_layout = QGridLayout(actions_group)
        
        self.load_template_btn = QPushButton("📂 Load Template")
        self.load_template_btn.clicked.connect(self.load_template)
        actions_layout.addWidget(self.load_template_btn, 0, 0)
        
        self.save_template_btn = QPushButton("💾 Save Template")
        self.save_template_btn.clicked.connect(self.save_template)
        actions_layout.addWidget(self.save_template_btn, 0, 1)
        
        self.edit_template_btn = QPushButton("✏️ Edit Template")
        self.edit_template_btn.clicked.connect(self.edit_template)
        actions_layout.addWidget(self.edit_template_btn, 1, 0)
        
        self.create_template_btn = QPushButton("➕ Create New")
        self.create_template_btn.clicked.connect(self.create_template)
        actions_layout.addWidget(self.create_template_btn, 1, 1)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_progress_section", "Enhanced Devlog Panel")
    def create_progress_section(self, layout: QVBoxLayout):
        """Create the progress section."""
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Enhanced Devlog Generator ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    @debug_button("connect_signals", "Enhanced Devlog Panel")
    def connect_signals(self):
        """Connect all signals."""
        self.devlog_generated.connect(self.on_devlog_generated)
        self.devlog_saved.connect(self.on_devlog_saved)
        self.devlog_exported.connect(self.on_devlog_exported)
    
    @debug_button("load_devlog_history", "Enhanced Devlog Panel")
    def load_devlog_history(self):
        """Load devlog history."""
        try:
            # Load from memory manager or file system
            # For now, we'll use placeholder data
            self.devlog_history = [
                {
                    'date': '2024-01-15 10:30',
                    'session_type': 'Development Session',
                    'conversation': 'GUI Consolidation Work',
                    'context_used': 'Work patterns, MMORPG state, Skills',
                    'file_path': 'devlogs/gui_consolidation_20240115.md'
                }
            ]
            
            self.refresh_devlog_history()
            
        except Exception as e:
            logger.error(f"Failed to load devlog history: {e}")
    
    @debug_button("load_conversations", "Enhanced Devlog Panel")
    def load_conversations(self):
        """Load recent conversations for devlog generation."""
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
    
    @debug_button("generate_devlog", "Enhanced Devlog Panel")
    def generate_devlog(self):
        """Generate an enhanced devlog."""
        conversation_id = self.conversation_combo.currentData()
        if not conversation_id:
            QMessageBox.warning(self, "Warning", "Please select a conversation")
            return
        
        # Get conversation data
        conversation = self.memory_manager.get_conversation(conversation_id)
        if not conversation:
            QMessageBox.warning(self, "Warning", "Selected conversation not found")
            return
        
        # Prepare template data
        template_data = {
            'conversation_title': conversation.get('title', 'Untitled'),
            'conversation_content': conversation.get('content', ''),
            'conversation_length': len(conversation.get('content', '')),
            'analysis_type': self.analysis_type_combo.currentText()
        }
        
        # Start generation
        self.status_label.setText("Generating enhanced devlog...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Get YAML preference from UI
        use_yaml = self.use_yaml_cb.isChecked()
        
        self.generation_worker = DevlogGenerationWorker(
            template_data, self.memory_manager, self.mmorpg_engine, use_yaml
        )
        self.generation_worker.generation_completed.connect(self.on_generation_completed)
        self.generation_worker.generation_failed.connect(self.on_generation_failed)
        self.generation_worker.progress_updated.connect(self.progress_bar.setValue)
        
        self.generation_worker.start()
    
    @debug_button("quick_generate", "Enhanced Devlog Panel")
    def quick_generate(self):
        """Quick generate devlog for most recent conversation."""
        try:
            conversations = self.memory_manager.get_recent_conversations(limit=1)
            if conversations:
                # Auto-select the most recent conversation
                self.conversation_combo.setCurrentIndex(1)  # Skip "Select a conversation..."
                self.generate_devlog()
            else:
                QMessageBox.warning(self, "Warning", "No conversations found")
        except Exception as e:
            logger.error(f"Quick generate failed: {e}")
    
    @debug_button("batch_generate", "Enhanced Devlog Panel")
    def batch_generate(self):
        """Batch generate devlogs for multiple conversations."""
        QMessageBox.information(self, "Batch Generate", "Batch generation dialog would open here")
    
    @debug_button("preview_devlog", "Enhanced Devlog Panel")
    def preview_devlog(self):
        """Preview the generated devlog."""
        if self.current_devlog:
            # Show preview dialog
            QMessageBox.information(self, "Devlog Preview", "Preview dialog would show here")
        else:
            QMessageBox.warning(self, "Warning", "No devlog generated yet")
    
    @debug_button("save_devlog", "Enhanced Devlog Panel")
    def save_devlog(self):
        """Save the generated devlog."""
        if not self.current_devlog:
            QMessageBox.warning(self, "Warning", "No devlog to save")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Devlog", "", "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_devlog['content'])
                
                self.status_label.setText("Devlog saved successfully")
                self.devlog_saved.emit(file_path)
                
                # Add to history
                generation_method = self.current_devlog.get('generation_method', 'context-driven')
                context_used = 'YAML-structured data' if generation_method == 'yaml-driven' else 'Work patterns, MMORPG state, Skills'
                
                self.devlog_history.append({
                    'date': self.current_devlog['timestamp'],
                    'session_type': self.analysis_type_combo.currentText(),
                    'conversation': self.conversation_combo.currentText(),
                    'context_used': context_used,
                    'generation_method': generation_method,
                    'file_path': file_path
                })
                
                self.refresh_devlog_history()
                
            except Exception as e:
                logger.error(f"Failed to save devlog: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save devlog: {e}")
    
    @debug_button("export_devlog", "Enhanced Devlog Panel")
    def export_devlog(self):
        """Export the devlog in different formats."""
        if not self.current_devlog:
            QMessageBox.warning(self, "Warning", "No devlog to export")
            return
        
        # Export options dialog would go here
        QMessageBox.information(self, "Export Devlog", "Export options dialog would open here")
    
    @debug_button("copy_devlog", "Enhanced Devlog Panel")
    def copy_devlog(self):
        """Copy devlog content to clipboard."""
        if self.current_devlog:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_devlog['content'])
            self.status_label.setText("Devlog copied to clipboard")
        else:
            QMessageBox.warning(self, "Warning", "No devlog to copy")
    
    @debug_button("refresh_work_patterns", "Enhanced Devlog Panel")
    def refresh_work_patterns(self):
        """Refresh work patterns analysis."""
        try:
            # Create a temporary worker to get patterns
            worker = DevlogGenerationWorker({}, self.memory_manager, self.mmorpg_engine)
            work_patterns = worker._get_work_patterns()
            
            # Update patterns table
            self.patterns_table.setRowCount(0)
            
            # Add technologies
            for tech, count in work_patterns.get('technologies', {}).items():
                row = self.patterns_table.rowCount()
                self.patterns_table.insertRow(row)
                self.patterns_table.setItem(row, 0, QTableWidgetItem("Technology"))
                self.patterns_table.setItem(row, 1, QTableWidgetItem(tech))
                self.patterns_table.setItem(row, 2, QTableWidgetItem(str(count)))
            
            # Add topics
            for topic, count in work_patterns.get('topics', {}).items():
                row = self.patterns_table.rowCount()
                self.patterns_table.insertRow(row)
                self.patterns_table.setItem(row, 0, QTableWidgetItem("Topic"))
                self.patterns_table.setItem(row, 1, QTableWidgetItem(topic))
                self.patterns_table.setItem(row, 2, QTableWidgetItem(str(count)))
            
            self.status_label.setText("Work patterns refreshed")
            
        except Exception as e:
            logger.error(f"Failed to refresh work patterns: {e}")
    
    @debug_button("refresh_devlog_history", "Enhanced Devlog Panel")
    def refresh_devlog_history(self):
        """Refresh the devlog history table."""
        try:
            self.history_table.setRowCount(len(self.devlog_history))
            
            for i, devlog in enumerate(self.devlog_history):
                self.history_table.setItem(i, 0, QTableWidgetItem(devlog['date']))
                self.history_table.setItem(i, 1, QTableWidgetItem(devlog['session_type']))
                self.history_table.setItem(i, 2, QTableWidgetItem(devlog['conversation']))
                self.history_table.setItem(i, 3, QTableWidgetItem(devlog['context_used']))
                
                # Method column
                method = devlog.get('generation_method', 'context-driven')
                method_display = "🎯 YAML" if method == 'yaml-driven' else "🔄 Context"
                self.history_table.setItem(i, 4, QTableWidgetItem(method_display))
                
                # Actions button
                actions_btn = QPushButton("📋 View")
                actions_btn.clicked.connect(lambda checked, row=i: self.view_devlog(row))
                self.history_table.setCellWidget(i, 5, actions_btn)
            
        except Exception as e:
            logger.error(f"Failed to refresh devlog history: {e}")
    
    def view_devlog(self, row: int):
        """View a specific devlog from history."""
        if 0 <= row < len(self.devlog_history):
            devlog = self.devlog_history[row]
            QMessageBox.information(self, f"Devlog: {devlog['conversation']}", 
                                  f"Date: {devlog['date']}\nType: {devlog['session_type']}\nFile: {devlog['file_path']}")
    
    @debug_button("export_devlog_history", "Enhanced Devlog Panel")
    def export_devlog_history(self):
        """Export devlog history."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Devlog History", "", "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.status_label.setText("Devlog history exported successfully")
    
    @debug_button("clear_devlog_history", "Enhanced Devlog Panel")
    def clear_devlog_history(self):
        """Clear devlog history."""
        reply = QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to clear the devlog history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.devlog_history.clear()
            self.refresh_devlog_history()
            self.status_label.setText("Devlog history cleared")
    
    # Template methods (placeholder implementations)
    @debug_button("load_template", "Enhanced Devlog Panel")
    def load_template(self):
        """Load a template."""
        QMessageBox.information(self, "Load Template", "Template loading dialog would open here")
    
    @debug_button("save_template", "Enhanced Devlog Panel")
    def save_template(self):
        """Save a template."""
        QMessageBox.information(self, "Save Template", "Template saving dialog would open here")
    
    @debug_button("edit_template", "Enhanced Devlog Panel")
    def edit_template(self):
        """Edit a template."""
        QMessageBox.information(self, "Edit Template", "Template editing dialog would open here")
    
    @debug_button("create_template", "Enhanced Devlog Panel")
    def create_template(self):
        """Create a new template."""
        QMessageBox.information(self, "Create Template", "Template creation dialog would open here")
    
    # Signal handlers
    @debug_button("on_generation_completed", "Enhanced Devlog Panel")
    def on_generation_completed(self, result: dict):
        """Handle devlog generation completion."""
        self.current_devlog = result
        self.generated_content.setPlainText(result['content'])
        self.progress_bar.setVisible(False)
        
        # Show generation method in status
        generation_method = result.get('generation_method', 'unknown')
        if generation_method == 'yaml-driven':
            self.status_label.setText("✅ YAML-driven devlog generated successfully")
        else:
            self.status_label.setText("✅ Context-driven devlog generated successfully")
        
        self.devlog_generated.emit(result)
    
    @debug_button("on_generation_failed", "Enhanced Devlog Panel")
    def on_generation_failed(self, error: str):
        """Handle devlog generation failure."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Devlog generation failed: {error}")
        QMessageBox.critical(self, "Generation Error", f"Failed to generate devlog: {error}")
    
    @debug_button("on_devlog_generated", "Enhanced Devlog Panel")
    def on_devlog_generated(self, data: dict):
        """Handle devlog generation."""
        self.status_label.setText("Devlog ready for saving or export")
    
    @debug_button("on_devlog_saved", "Enhanced Devlog Panel")
    def on_devlog_saved(self, file_path: str):
        """Handle devlog save."""
        self.status_label.setText(f"Devlog saved to {file_path}")
    
    @debug_button("on_devlog_exported", "Enhanced Devlog Panel")
    def on_devlog_exported(self, export_info: str):
        """Handle devlog export."""
        self.status_label.setText(f"Devlog exported: {export_info}") 