#!/usr/bin/env python3
"""
Voice Modeling Panel for Dreamscape GUI
=======================================

Provides a comprehensive interface for voice modeling and content generation.
Features:
- Voice profile creation and management
- Voice training from conversation history
- Content generation with voice consistency
- Voice analysis and visualization
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Path setup for imports

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
    QPushButton, QTextEdit, QLineEdit, QComboBox, QSpinBox,
    QProgressBar, QGroupBox, QFormLayout, QCheckBox, QListWidget,
    QListWidgetItem, QSplitter, QFrame, QScrollArea, QGridLayout,
    QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSlider, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap

from dreamscape.core.voice_modeling_system import VoiceModelingSystem, VoiceProfile, VoiceTrainingConfig
from dreamscape.core.memory_system import MemoryManager
from gui.components.refresh_integration_manager import UnifiedRefreshButton
from gui.components.global_refresh_manager import RefreshType
from gui.components.data_loader import DataLoader
from gui.debug_handler import debug_button

logger = logging.getLogger(__name__)

class VoiceTrainingWorker(QThread):
    """Worker thread for voice training operations."""
    
    training_progress = pyqtSignal(int)
    training_status = pyqtSignal(str)
    training_complete = pyqtSignal(bool, str)
    
    def __init__(self, voice_system: VoiceModelingSystem, profile_id: str, 
                 conversations: List[Dict], config: VoiceTrainingConfig):
        super().__init__()
        self.voice_system = voice_system
        self.profile_id = profile_id
        self.conversations = conversations
        self.config = config
    
    def run(self):
        """Run the voice training process."""
        try:
            self.training_status.emit("Starting voice training...")
            self.training_progress.emit(10)
            
            # Train the voice profile
            success = self.voice_system.train_voice_from_conversations(
                self.profile_id, self.conversations, self.config
            )
            
            self.training_progress.emit(100)
            
            if success:
                self.training_status.emit("Voice training completed successfully!")
                self.training_complete.emit(True, "Voice profile trained successfully")
            else:
                self.training_status.emit("Voice training failed!")
                self.training_complete.emit(False, "Failed to train voice profile")
                
        except Exception as e:
            logger.error(f"Error in voice training: {e}")
            self.training_status.emit(f"Error: {str(e)}")
            self.training_complete.emit(False, f"Training error: {str(e)}")

class VoiceModelingPanel(QWidget):
    """Comprehensive voice modeling panel for Dreamscape GUI."""
    
    # Signals
    voice_profile_created = pyqtSignal(str)  # profile_id
    voice_profile_updated = pyqtSignal(str)  # profile_id
    voice_training_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, memory_manager: MemoryManager = None):
        super().__init__()
        self.memory_manager = memory_manager or MemoryManager()
        self.voice_system = VoiceModelingSystem()
        self.data_loader = DataLoader()
        
        # UI state
        self.current_profile = None
        self.training_worker = None
        
        self.init_ui()
        self.load_voice_profiles()
    
    def init_ui(self):
        """Initialize the voice modeling user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🎭 Voice Modeling & Content Generation")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Create, train, and manage voice profiles for personalized content generation.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_profiles_tab(), "👤 Voice Profiles")
        self.tab_widget.addTab(self.create_training_tab(), "🎯 Voice Training")
        self.tab_widget.addTab(self.create_generation_tab(), "✨ Content Generation")
        self.tab_widget.addTab(self.create_analysis_tab(), "📊 Voice Analysis")
        
        # Status section
        self.create_status_section(layout)
        
        # Connect signals
        self.connect_signals()
    
    @debug_button("create_profiles_tab", "Voice Modeling Panel")
    def create_profiles_tab(self) -> QWidget:
        """Create the voice profiles management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Voice Profile Management")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Profile creation section
        create_group = QGroupBox("Create New Voice Profile")
        create_layout = QFormLayout(create_group)
        
        self.profile_name_edit = QLineEdit()
        self.profile_name_edit.setPlaceholderText("Enter profile name...")
        create_layout.addRow("Profile Name:", self.profile_name_edit)
        
        self.profile_type_combo = QComboBox()
        self.profile_type_combo.addItems(["user", "agent"])
        create_layout.addRow("Profile Type:", self.profile_type_combo)
        
        create_btn_layout = QHBoxLayout()
        self.create_profile_btn = QPushButton("Create Profile")
        self.create_profile_btn.clicked.connect(self.create_voice_profile)
        create_btn_layout.addWidget(self.create_profile_btn)
        create_btn_layout.addStretch()
        create_layout.addRow("", create_btn_layout)
        
        layout.addWidget(create_group)
        
        # Profile list section using shared component
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        list_group = QGroupBox("Voice Profiles")
        list_layout = QVBoxLayout(list_group)
        self.profiles_list_group = components.create_data_list(
            title="Voice Profiles",
            items=[],  # Will be populated later
            selection_mode=QListWidget.SelectionMode.SingleSelection,
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.profiles_list = self.profiles_list_group.findChild(QListWidget)
        self.profiles_list.itemSelectionChanged.connect(self.on_profile_selected)
        list_layout.addWidget(self.profiles_list_group)
        # Profile actions using shared component
        actions = [
            {
                "text": "🔄 Refresh",
                "callback": self.load_voice_profiles,
                "id": "refresh_profiles"
            },
            {
                "text": "🗑️ Delete",
                "callback": self.delete_voice_profile,
                "id": "delete_profile",
                "enabled": False
            }
        ]
        actions_panel = components.create_action_panel(
            title="Profile Actions",
            actions=actions,
            config=ComponentConfig(style=ComponentStyle.PRIMARY)
        )
        self.refresh_profiles_btn = actions_panel.findChild(QPushButton, "refresh_profiles")
        self.delete_profile_btn = actions_panel.findChild(QPushButton, "delete_profile")
        list_layout.addWidget(actions_panel)
        layout.addWidget(list_group)
        
        # Profile details section
        details_group = QGroupBox("Profile Details")
        details_layout = QFormLayout(details_group)
        
        self.profile_id_label = QLabel("No profile selected")
        details_layout.addRow("Profile ID:", self.profile_id_label)
        
        self.profile_confidence_label = QLabel("0.0")
        details_layout.addRow("Confidence Score:", self.profile_confidence_label)
        
        self.profile_samples_label = QLabel("0")
        details_layout.addRow("Training Samples:", self.profile_samples_label)
        
        self.profile_updated_label = QLabel("Never")
        details_layout.addRow("Last Updated:", self.profile_updated_label)
        
        layout.addWidget(details_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_training_tab", "Voice Modeling Panel")
    def create_training_tab(self) -> QWidget:
        """Create the voice training tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Voice Training from Conversations")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Training configuration
        config_group = QGroupBox("Training Configuration")
        config_layout = QFormLayout(config_group)
        
        self.min_samples_spin = QSpinBox()
        self.min_samples_spin.setRange(5, 50)
        self.min_samples_spin.setValue(10)
        config_layout.addRow("Minimum Samples:", self.min_samples_spin)
        
        self.max_samples_spin = QSpinBox()
        self.max_samples_spin.setRange(20, 200)
        self.max_samples_spin.setValue(100)
        config_layout.addRow("Maximum Samples:", self.max_samples_spin)
        
        self.confidence_threshold_spin = QDoubleSpinBox()
        self.confidence_threshold_spin.setRange(0.1, 1.0)
        self.confidence_threshold_spin.setValue(0.7)
        self.confidence_threshold_spin.setSingleStep(0.1)
        config_layout.addRow("Confidence Threshold:", self.confidence_threshold_spin)
        
        self.analysis_depth_combo = QComboBox()
        self.analysis_depth_combo.addItems(["basic", "standard", "comprehensive"])
        self.analysis_depth_combo.setCurrentText("comprehensive")
        config_layout.addRow("Analysis Depth:", self.analysis_depth_combo)
        
        layout.addWidget(config_group)
        
        # Conversation selection
        conv_group = QGroupBox("Conversation Selection")
        conv_layout = QVBoxLayout(conv_group)
        
        # Conversation list
        self.conversations_list = QListWidget()
        self.conversations_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        conv_layout.addWidget(self.conversations_list)
        
        # Conversation controls
        conv_controls = QHBoxLayout()
        
        self.load_conversations_btn = QPushButton("📂 Load Conversations")
        self.load_conversations_btn.clicked.connect(self.load_conversations_for_training)
        conv_controls.addWidget(self.load_conversations_btn)
        
        self.select_all_conv_btn = QPushButton("Select All")
        self.select_all_conv_btn.clicked.connect(self.select_all_conversations)
        conv_controls.addWidget(self.select_all_conv_btn)
        
        self.deselect_all_conv_btn = QPushButton("Deselect All")
        self.deselect_all_conv_btn.clicked.connect(self.deselect_all_conversations)
        conv_controls.addWidget(self.deselect_all_conv_btn)
        
        conv_controls.addStretch()
        conv_layout.addLayout(conv_controls)
        
        layout.addWidget(conv_group)
        
        # Training controls
        training_group = QGroupBox("Training Controls")
        training_layout = QVBoxLayout(training_group)
        
        # Profile selection for training
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Target Profile:"))
        
        self.training_profile_combo = QComboBox()
        self.training_profile_combo.addItem("Select a profile...")
        profile_layout.addWidget(self.training_profile_combo)
        
        profile_layout.addStretch()
        training_layout.addLayout(profile_layout)
        
        # Training button
        self.start_training_btn = QPushButton("🚀 Start Voice Training")
        self.start_training_btn.clicked.connect(self.start_voice_training)
        self.start_training_btn.setEnabled(False)
        training_layout.addWidget(self.start_training_btn)
        
        # Training progress
        self.training_progress = QProgressBar()
        self.training_progress.setVisible(False)
        training_layout.addWidget(self.training_progress)
        
        self.training_status = QLabel("Ready to train")
        training_layout.addWidget(self.training_status)
        
        layout.addWidget(training_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_generation_tab", "Voice Modeling Panel")
    def create_generation_tab(self) -> QWidget:
        """Create the content generation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Content Generation with Voice")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Voice selection
        voice_group = QGroupBox("Voice Selection")
        voice_layout = QFormLayout(voice_group)
        
        self.generation_voice_combo = QComboBox()
        self.generation_voice_combo.addItem("Select a voice...")
        voice_layout.addRow("Voice Profile:", self.generation_voice_combo)
        
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems([
            "response", "explanation", "story", "technical", "creative", "professional"
        ])
        voice_layout.addRow("Content Type:", self.content_type_combo)
        
        layout.addWidget(voice_group)
        
        # Content input
        input_group = QGroupBox("Content Input")
        input_layout = QVBoxLayout(input_group)
        
        self.content_prompt_edit = QTextEdit()
        self.content_prompt_edit.setPlaceholderText("Enter your prompt or content request...")
        self.content_prompt_edit.setMaximumHeight(100)
        input_layout.addWidget(self.content_prompt_edit)
        
        # Generation controls
        gen_controls = QHBoxLayout()
        
        self.generate_content_btn = QPushButton("✨ Generate Content")
        self.generate_content_btn.clicked.connect(self.generate_content_with_voice)
        self.generate_content_btn.setEnabled(False)
        gen_controls.addWidget(self.generate_content_btn)
        
        self.clear_content_btn = QPushButton("Clear")
        self.clear_content_btn.clicked.connect(self.clear_content)
        gen_controls.addWidget(self.clear_content_btn)
        
        gen_controls.addStretch()
        input_layout.addLayout(gen_controls)
        
        layout.addWidget(input_group)
        
        # Generated content
        output_group = QGroupBox("Generated Content")
        output_layout = QVBoxLayout(output_group)
        
        self.generated_content_edit = QTextEdit()
        self.generated_content_edit.setReadOnly(True)
        self.generated_content_edit.setPlaceholderText("Generated content will appear here...")
        output_layout.addWidget(self.generated_content_edit)
        
        # Output controls
        output_controls = QHBoxLayout()
        
        self.copy_content_btn = QPushButton("📋 Copy")
        self.copy_content_btn.clicked.connect(self.copy_generated_content)
        output_controls.addWidget(self.copy_content_btn)
        
        self.save_content_btn = QPushButton("💾 Save")
        self.save_content_btn.clicked.connect(self.save_generated_content)
        output_controls.addWidget(self.save_content_btn)
        
        output_controls.addStretch()
        output_layout.addLayout(output_controls)
        
        layout.addWidget(output_group)
        
        return tab
    
    @debug_button("create_analysis_tab", "Voice Modeling Panel")
    def create_analysis_tab(self) -> QWidget:
        """Create the voice analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Voice Analysis & Visualization")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Analysis selection
        analysis_group = QGroupBox("Analysis Selection")
        analysis_layout = QFormLayout(analysis_group)
        
        self.analysis_profile_combo = QComboBox()
        self.analysis_profile_combo.addItem("Select a profile...")
        self.analysis_profile_combo.currentTextChanged.connect(self.update_voice_analysis)
        analysis_layout.addRow("Profile to Analyze:", self.analysis_profile_combo)
        
        layout.addWidget(analysis_group)
        
        # Voice characteristics display
        characteristics_group = QGroupBox("Voice Characteristics")
        characteristics_layout = QGridLayout(characteristics_group)
        
        # Tone and style
        characteristics_layout.addWidget(QLabel("Tone:"), 0, 0)
        self.tone_label = QLabel("Not analyzed")
        characteristics_layout.addWidget(self.tone_label, 0, 1)
        
        characteristics_layout.addWidget(QLabel("Writing Style:"), 0, 2)
        self.writing_style_label = QLabel("Not analyzed")
        characteristics_layout.addWidget(self.writing_style_label, 0, 3)
        
        characteristics_layout.addWidget(QLabel("Formality:"), 1, 0)
        self.formality_label = QLabel("Not analyzed")
        characteristics_layout.addWidget(self.formality_label, 1, 1)
        
        characteristics_layout.addWidget(QLabel("Technical Depth:"), 1, 2)
        self.technical_depth_label = QLabel("Not analyzed")
        characteristics_layout.addWidget(self.technical_depth_label, 1, 3)
        
        # Levels
        characteristics_layout.addWidget(QLabel("Creativity Level:"), 2, 0)
        self.creativity_slider = QSlider(Qt.Orientation.Horizontal)
        self.creativity_slider.setRange(0, 100)
        self.creativity_slider.setEnabled(False)
        characteristics_layout.addWidget(self.creativity_slider, 2, 1)
        
        characteristics_layout.addWidget(QLabel("Humor Level:"), 2, 2)
        self.humor_slider = QSlider(Qt.Orientation.Horizontal)
        self.humor_slider.setRange(0, 100)
        self.humor_slider.setEnabled(False)
        characteristics_layout.addWidget(self.humor_slider, 2, 3)
        
        characteristics_layout.addWidget(QLabel("Empathy Level:"), 3, 0)
        self.empathy_slider = QSlider(Qt.Orientation.Horizontal)
        self.empathy_slider.setRange(0, 100)
        self.empathy_slider.setEnabled(False)
        characteristics_layout.addWidget(self.empathy_slider, 3, 1)
        
        characteristics_layout.addWidget(QLabel("Emoji Usage:"), 3, 2)
        self.emoji_slider = QSlider(Qt.Orientation.Horizontal)
        self.emoji_slider.setRange(0, 100)
        self.emoji_slider.setEnabled(False)
        characteristics_layout.addWidget(self.emoji_slider, 3, 3)
        
        layout.addWidget(characteristics_group)
        
        # Expertise and topics
        expertise_group = QGroupBox("Expertise & Topics")
        expertise_layout = QVBoxLayout(expertise_group)
        
        self.expertise_text = QTextEdit()
        self.expertise_text.setReadOnly(True)
        self.expertise_text.setMaximumHeight(100)
        self.expertise_text.setPlaceholderText("Expertise domains and preferred topics will appear here...")
        expertise_layout.addWidget(self.expertise_text)
        
        layout.addWidget(expertise_group)
        
        # Communication patterns
        patterns_group = QGroupBox("Communication Patterns")
        patterns_layout = QGridLayout(patterns_group)
        
        patterns_layout.addWidget(QLabel("Greeting Style:"), 0, 0)
        self.greeting_style_label = QLabel("Not analyzed")
        patterns_layout.addWidget(self.greeting_style_label, 0, 1)
        
        patterns_layout.addWidget(QLabel("Question Style:"), 0, 2)
        self.question_style_label = QLabel("Not analyzed")
        patterns_layout.addWidget(self.question_style_label, 0, 3)
        
        patterns_layout.addWidget(QLabel("Explanation Style:"), 1, 0)
        self.explanation_style_label = QLabel("Not analyzed")
        patterns_layout.addWidget(self.explanation_style_label, 1, 1)
        
        patterns_layout.addWidget(QLabel("Vocabulary Complexity:"), 1, 2)
        self.vocabulary_label = QLabel("Not analyzed")
        patterns_layout.addWidget(self.vocabulary_label, 1, 3)
        
        layout.addWidget(patterns_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_status_section", "Voice Modeling Panel")
    def create_status_section(self, layout: QVBoxLayout):
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
                title="voice_modeling_panel Statistics",
                style="modern"
            )
            
            layout.addWidget(stats_widget)
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            layout.addWidget(QWidget())  # Fallback widget

    def connect_signals(self):
        """Connect UI signals."""
        # Profile selection
        self.profiles_list.itemSelectionChanged.connect(self.on_profile_selected)
        
        # Training completion
        self.voice_profile_created.connect(self.on_voice_profile_created)
        self.voice_profile_updated.connect(self.on_voice_profile_updated)
        self.voice_training_complete.connect(self.on_voice_training_complete)
    
    @debug_button("load_voice_profiles", "Voice Modeling Panel")
    def load_voice_profiles(self, force_reload: bool = False):
        """Load and display voice profiles using DataLoader."""
        try:
            profiles = self.data_loader.load(
                "voice_profiles", self.voice_system.list_voice_profiles, force_reload
            )
            
            self.profiles_list.clear()
            self.generation_voice_combo.clear()
            self.training_profile_combo.clear()
            self.analysis_profile_combo.clear()
            
            # Add default options
            self.generation_voice_combo.addItem("Select a voice...")
            self.training_profile_combo.addItem("Select a profile...")
            self.analysis_profile_combo.addItem("Select a profile...")
            
            for profile in profiles:
                # Add to profiles list
                item = QListWidgetItem(f"{profile.name} ({profile.type})")
                item.setData(Qt.ItemDataRole.UserRole, profile.id)
                self.profiles_list.addItem(item)
                
                # Add to combo boxes
                self.generation_voice_combo.addItem(profile.name, profile.id)
                self.training_profile_combo.addItem(profile.name, profile.id)
                self.analysis_profile_combo.addItem(profile.name, profile.id)
            
            self.delete_profile_btn.setEnabled(False) # Disable delete until a profile is selected
            
        except Exception as e:
            logger.error(f"Error loading voice profiles: {e}")
            self.status_label.setText(f"Error loading profiles: {e}")
    
    @debug_button("create_voice_profile", "Voice Modeling Panel")
    def create_voice_profile(self):
        """Create a new voice profile."""
        name = self.profile_name_edit.text().strip()
        profile_type = self.profile_type_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a profile name.")
            return
        
        try:
            profile = self.voice_system.create_voice_profile(name, profile_type)
            self.voice_profile_created.emit(profile.id)
            
            self.profile_name_edit.clear()
            self.status_label.setText(f"Created voice profile: {name}")
            
        except Exception as e:
            logger.error(f"Error creating voice profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create voice profile: {e}")
    
    @debug_button("delete_voice_profile", "Voice Modeling Panel")
    def delete_voice_profile(self):
        """Delete the selected voice profile."""
        current_item = self.profiles_list.currentItem()
        if not current_item:
            return
        
        profile_id = current_item.data(Qt.ItemDataRole.UserRole)
        profile_name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the voice profile '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.voice_system.delete_voice_profile(profile_id)
                if success:
                    self.load_voice_profiles()
                    self.status_label.setText(f"Deleted voice profile: {profile_name}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete voice profile")
            except Exception as e:
                logger.error(f"Error deleting voice profile: {e}")
                QMessageBox.critical(self, "Error", f"Error deleting profile: {e}")
    
    @debug_button("on_profile_selected", "Voice Modeling Panel")
    def on_profile_selected(self):
        """Handle profile selection."""
        current_item = self.profiles_list.currentItem()
        if not current_item:
            self.delete_profile_btn.setEnabled(False)
            self.clear_profile_details()
            return
        
        profile_id = current_item.data(Qt.ItemDataRole.UserRole)
        profile = self.voice_system.get_voice_profile(profile_id)
        
        if profile:
            self.current_profile = profile
            self.update_profile_details(profile)
            self.delete_profile_btn.setEnabled(True)
        else:
            self.clear_profile_details()
    
    @debug_button("update_profile_details", "Voice Modeling Panel")
    def update_profile_details(self, profile: VoiceProfile):
        """Update profile details display."""
        self.profile_id_label.setText(profile.id)
        self.profile_confidence_label.setText(f"{profile.confidence_score:.2f}")
        self.profile_samples_label.setText(str(profile.sample_count))
        self.profile_updated_label.setText(profile.updated_at.strftime("%Y-%m-%d %H:%M"))
    
    @debug_button("clear_profile_details", "Voice Modeling Panel")
    def clear_profile_details(self):
        """Clear profile details display."""
        self.profile_id_label.setText("No profile selected")
        self.profile_confidence_label.setText("0.0")
        self.profile_samples_label.setText("0")
        self.profile_updated_label.setText("Never")
        self.current_profile = None
    
    @debug_button("load_conversations_for_training", "Voice Modeling Panel")
    def load_conversations_for_training(self):
        """Load conversations for voice training."""
        try:
            conversations = self.memory_manager.get_conversations()
            
            self.conversations_list.clear()
            for conv in conversations:
                title = conv.get('title', 'Untitled')
                item = QListWidgetItem(title)
                item.setData(Qt.ItemDataRole.UserRole, conv)
                self.conversations_list.addItem(item)
            
            self.status_label.setText(f"Loaded {len(conversations)} conversations")
            
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
            self.status_label.setText(f"Error loading conversations: {e}")
    
    @debug_button("select_all_conversations", "Voice Modeling Panel")
    def select_all_conversations(self):
        """Select all conversations in the list."""
        for i in range(self.conversations_list.count()):
            self.conversations_list.item(i).setSelected(True)
    
    @debug_button("deselect_all_conversations", "Voice Modeling Panel")
    def deselect_all_conversations(self):
        """Deselect all conversations in the list."""
        self.conversations_list.clearSelection()
    
    @debug_button("start_voice_training", "Voice Modeling Panel")
    def start_voice_training(self):
        """Start voice training process."""
        # Get selected profile
        profile_index = self.training_profile_combo.currentIndex()
        if profile_index == 0:  # "Select a profile..."
            QMessageBox.warning(self, "No Profile Selected", "Please select a target profile.")
            return
        
        profile_id = self.training_profile_combo.currentData()
        
        # Get selected conversations
        selected_items = self.conversations_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Conversations Selected", "Please select conversations for training.")
            return
        
        conversations = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        
        # Create training config
        config = VoiceTrainingConfig(
            min_samples=self.min_samples_spin.value(),
            max_samples=self.max_samples_spin.value(),
            confidence_threshold=self.confidence_threshold_spin.value(),
            analysis_depth=self.analysis_depth_combo.currentText()
        )
        
        # Start training worker
        self.training_worker = VoiceTrainingWorker(
            self.voice_system, profile_id, conversations, config
        )
        
        self.training_worker.training_progress.connect(self.training_progress.setValue)
        self.training_worker.training_status.connect(self.training_status.setText)
        self.training_worker.training_complete.connect(self.on_voice_training_complete)
        
        # Update UI
        self.start_training_btn.setEnabled(False)
        self.training_progress.setVisible(True)
        self.training_progress.setValue(0)
        
        # Start training
        self.training_worker.start()
    
    @debug_button("generate_content_with_voice", "Voice Modeling Panel")
    def generate_content_with_voice(self):
        """Generate content using the selected voice profile."""
        # Get selected voice
        voice_index = self.generation_voice_combo.currentIndex()
        if voice_index == 0:  # "Select a voice..."
            QMessageBox.warning(self, "No Voice Selected", "Please select a voice profile.")
            return
        
        profile_id = self.generation_voice_combo.currentData()
        prompt = self.content_prompt_edit.toPlainText().strip()
        content_type = self.content_type_combo.currentText()
        
        if not prompt:
            QMessageBox.warning(self, "No Prompt", "Please enter a prompt for content generation.")
            return
        
        try:
            # Generate content
            content = self.voice_system.generate_content_with_voice(
                profile_id, prompt, content_type
            )
            
            self.generated_content_edit.setPlainText(content)
            self.status_label.setText("Content generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate content: {e}")
    
    @debug_button("clear_content", "Voice Modeling Panel")
    def clear_content(self):
        """Clear content input and output."""
        self.content_prompt_edit.clear()
        self.generated_content_edit.clear()
    
    @debug_button("copy_generated_content", "Voice Modeling Panel")
    def copy_generated_content(self):
        """Copy generated content to clipboard."""
        content = self.generated_content_edit.toPlainText()
        if content:
            clipboard = self.window().clipboard()
            clipboard.setText(content)
            self.status_label.setText("Content copied to clipboard")
    
    @debug_button("save_generated_content", "Voice Modeling Panel")
    def save_generated_content(self):
        """Save generated content to file."""
        content = self.generated_content_edit.toPlainText()
        if not content:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Generated Content", "", 
            "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.setText(f"Content saved to {file_path}")
            except Exception as e:
                logger.error(f"Error saving content: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save content: {e}")
    
    @debug_button("update_voice_analysis", "Voice Modeling Panel")
    def update_voice_analysis(self):
        """Update voice analysis display."""
        profile_index = self.analysis_profile_combo.currentIndex()
        if profile_index == 0:  # "Select a profile..."
            self.clear_voice_analysis()
            return
        
        profile_id = self.analysis_profile_combo.currentData()
        profile = self.voice_system.get_voice_profile(profile_id)
        
        if profile:
            self.display_voice_analysis(profile)
        else:
            self.clear_voice_analysis()
    
    def display_voice_analysis(self, profile: VoiceProfile):
        """Display voice analysis for a profile."""
        # Update labels
        self.tone_label.setText(profile.tone)
        self.writing_style_label.setText(profile.writing_style)
        self.formality_label.setText(profile.formality_level)
        self.technical_depth_label.setText(profile.technical_depth)
        self.greeting_style_label.setText(profile.greeting_style)
        self.question_style_label.setText(profile.question_style)
        self.explanation_style_label.setText(profile.explanation_style)
        self.vocabulary_label.setText(profile.vocabulary_complexity)
        
        # Update sliders
        self.creativity_slider.setValue(int(profile.creativity_level * 100))
        self.humor_slider.setValue(int(profile.humor_level * 100))
        self.empathy_slider.setValue(int(profile.empathy_level * 100))
        self.emoji_slider.setValue(int(profile.emoji_usage * 100))
        
        # Update expertise text
        expertise_text = f"Expertise Domains: {', '.join(profile.expertise_domains)}\n\n"
        expertise_text += f"Preferred Topics: {', '.join(profile.preferred_topics[:5])}\n\n"
        expertise_text += f"Technical Terms: {', '.join(profile.technical_terms[:10])}"
        
        self.expertise_text.setPlainText(expertise_text)
    
    @debug_button("clear_voice_analysis", "Voice Modeling Panel")
    def clear_voice_analysis(self):
        """Clear voice analysis display."""
        self.tone_label.setText("Not analyzed")
        self.writing_style_label.setText("Not analyzed")
        self.formality_label.setText("Not analyzed")
        self.technical_depth_label.setText("Not analyzed")
        self.greeting_style_label.setText("Not analyzed")
        self.question_style_label.setText("Not analyzed")
        self.explanation_style_label.setText("Not analyzed")
        self.vocabulary_label.setText("Not analyzed")
        
        self.creativity_slider.setValue(0)
        self.humor_slider.setValue(0)
        self.empathy_slider.setValue(0)
        self.emoji_slider.setValue(0)
        
        self.expertise_text.clear()
    
    @debug_button("on_voice_profile_created", "Voice Modeling Panel")
    def on_voice_profile_created(self, profile_id: str):
        """Handle voice profile creation."""
        self.load_voice_profiles()
    
    @debug_button("on_voice_profile_updated", "Voice Modeling Panel")
    def on_voice_profile_update(self):
        """Refresh function now handled by Global Refresh Manager."""
        try:
            # This function is now handled by the Global Refresh Manager
            # The refresh operation will be queued and processed automatically
            logger.info(f"Refresh request for UI handled by Global Refresh Manager")
            
        except Exception as e:
            logger.error(f"Error in refresh function: {e}")

    @debug_button("on_voice_training_complete", "Voice Modeling Panel")
    def on_voice_training_complete(self, success: bool, message: str):
        """Handle voice training completion."""
        # Update UI
        self.start_training_btn.setEnabled(True)
        self.training_progress.setVisible(False)
        
        if success:
            self.load_voice_profiles()
            QMessageBox.information(self, "Training Complete", message)
        else:
            QMessageBox.warning(self, "Training Failed", message)
        
        self.status_label.setText(message)
    
    @debug_button("refresh_ui", "Voice Modeling Panel")
    def refresh_ui(self):
        """Refresh the UI state."""
        self.load_voice_profiles()
        if self.current_profile:
            self.update_profile_details(self.current_profile) 