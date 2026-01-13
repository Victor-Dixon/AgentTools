#!/usr/bin/env python3
"""
Conversation Labeling UI Component
==================================

User-assisted labeling interface for conversation review and correction.
Allows users to review, correct, and validate conversation labels and user/agent separation.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QListWidget, QListWidgetItem, QSplitter, QGroupBox, QGridLayout,
    QComboBox, QLineEdit, QMessageBox, QProgressBar, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ConversationLabelingUI(QWidget):
    """
    User-assisted labeling UI for conversation review and correction.
    
    Features:
    - Review conversations with user/agent message separation
    - Correct mislabeled messages (user vs agent)
    - Validate conversation structure
    - Export corrected data
    - Integration with existing template and conversation systems
    """
    
    # Signals for integration with other components
    conversation_corrected = pyqtSignal(dict)  # Emitted when a conversation is corrected
    labeling_completed = pyqtSignal(list)      # Emitted when labeling session is complete
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversations = []
        self.current_conversation_index = 0
        self.corrections_made = []
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Conversation Review & Labeling")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Progress indicator
        self.progress_label = QLabel("Ready to review conversations")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content area
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left panel: Conversation list
        left_panel = self.create_conversation_list_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel: Message review and correction
        right_panel = self.create_message_review_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([300, 700])
        
        # Bottom panel: Actions
        bottom_panel = self.create_actions_panel()
        layout.addWidget(bottom_panel)
        
    def create_conversation_list_panel(self) -> QWidget:
        """Create the conversation list panel."""
        panel = QGroupBox("Conversations")
        layout = QVBoxLayout(panel)
        
        # Search/filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter conversations...")
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Conversation list
        self.conversation_list = QListWidget()
        self.conversation_list.setAlternatingRowColors(True)
        layout.addWidget(self.conversation_list)
        
        # Conversation info
        self.conversation_info = QLabel("Select a conversation to review")
        self.conversation_info.setWordWrap(True)
        layout.addWidget(self.conversation_info)
        
        return panel
        
    def create_message_review_panel(self) -> QWidget:
        """Create the message review and correction panel."""
        panel = QGroupBox("Message Review & Correction")
        layout = QVBoxLayout(panel)
        
        # Message list
        self.message_list = QListWidget()
        self.message_list.setAlternatingRowColors(True)
        layout.addWidget(self.message_list)
        
        # Message details
        details_group = QGroupBox("Message Details")
        details_layout = QGridLayout(details_group)
        
        details_layout.addWidget(QLabel("Role:"), 0, 0)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "assistant", "system"])
        details_layout.addWidget(self.role_combo, 0, 1)
        
        details_layout.addWidget(QLabel("Index:"), 1, 0)
        self.index_label = QLabel("")
        details_layout.addWidget(self.index_label, 1, 1)
        
        details_layout.addWidget(QLabel("Content:"), 2, 0)
        self.content_edit = QTextEdit()
        self.content_edit.setMaximumHeight(100)
        details_layout.addWidget(self.content_edit, 2, 1)
        
        # Correction buttons
        button_layout = QHBoxLayout()
        self.apply_correction_btn = QPushButton("Apply Correction")
        self.apply_correction_btn.setEnabled(False)
        button_layout.addWidget(self.apply_correction_btn)
        
        self.revert_btn = QPushButton("Revert Changes")
        self.revert_btn.setEnabled(False)
        button_layout.addWidget(self.revert_btn)
        
        button_layout.addStretch()
        details_layout.addLayout(button_layout, 3, 0, 1, 2)
        
        layout.addWidget(details_group)
        
        return panel
        
    def create_actions_panel(self) -> QWidget:
        """Create the actions panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(panel)
        
        # Navigation buttons
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setEnabled(False)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.setEnabled(False)
        layout.addWidget(self.next_btn)
        
        layout.addStretch()
        
        # Action buttons
        self.export_btn = QPushButton("Export Corrected Data")
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        self.complete_btn = QPushButton("Complete Review")
        self.complete_btn.setEnabled(False)
        layout.addWidget(self.complete_btn)
        
        return panel
        
    def setup_connections(self):
        """Set up signal connections."""
        # Conversation list
        self.conversation_list.currentRowChanged.connect(self.on_conversation_selected)
        self.search_edit.textChanged.connect(self.filter_conversations)
        
        # Message list
        self.message_list.currentRowChanged.connect(self.on_message_selected)
        
        # Correction controls
        self.apply_correction_btn.clicked.connect(self.apply_correction)
        self.revert_btn.clicked.connect(self.revert_changes)
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        self.content_edit.textChanged.connect(self.on_content_changed)
        
        # Navigation
        self.prev_btn.clicked.connect(self.previous_conversation)
        self.next_btn.clicked.connect(self.next_conversation)
        
        # Actions
        self.export_btn.clicked.connect(self.export_corrected_data)
        self.complete_btn.clicked.connect(self.complete_review)
        
    def load_conversations(self, conversations: List[Dict]):
        """Load conversations for review."""
        self.conversations = conversations
        self.current_conversation_index = 0
        self.corrections_made = []
        
        self.populate_conversation_list()
        self.update_progress()
        
        if self.conversations:
            self.conversation_list.setCurrentRow(0)
            self.next_btn.setEnabled(len(self.conversations) > 1)
            self.complete_btn.setEnabled(True)
            
    def populate_conversation_list(self):
        """Populate the conversation list."""
        self.conversation_list.clear()
        
        for i, conv in enumerate(self.conversations):
            conv_id = conv.get("conversation_id", f"Conversation {i+1}")
            user_count = len(conv.get("user_messages", []))
            agent_count = len(conv.get("agent_messages", []))
            
            item_text = f"{conv_id}\nUser: {user_count} | Agent: {agent_count}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            
            # Color code based on review status
            if self.has_corrections(i):
                item.setBackground(QColor(255, 255, 200))  # Light yellow for corrected
            else:
                item.setBackground(QColor(240, 240, 240))  # Light gray for unreviewed
                
            self.conversation_list.addItem(item)
            
    def filter_conversations(self, text: str):
        """Filter conversations based on search text."""
        for i in range(self.conversation_list.count()):
            item = self.conversation_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def on_conversation_selected(self, row: int):
        """Handle conversation selection."""
        if row >= 0 and row < len(self.conversations):
            self.current_conversation_index = row
            self.load_conversation_messages()
            self.update_navigation_buttons()
            
    def load_conversation_messages(self):
        """Load messages for the selected conversation."""
        if not self.conversations:
            return
            
        conv = self.conversations[self.current_conversation_index]
        self.message_list.clear()
        
        # Combine user and agent messages with their roles
        all_messages = []
        
        for msg in conv.get("user_messages", []):
            msg["role"] = "user"
            all_messages.append(msg)
            
        for msg in conv.get("agent_messages", []):
            msg["role"] = "assistant"
            all_messages.append(msg)
            
        # Sort by index
        all_messages.sort(key=lambda x: x.get("index", 0))
        
        # Add to list
        for msg in all_messages:
            role = msg.get("role", "unknown")
            content_preview = msg.get("content", "")[:100] + "..." if len(msg.get("content", "")) > 100 else msg.get("content", "")
            
            item_text = f"[{role.upper()}] {content_preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, msg)
            
            # Color code by role
            if role == "user":
                item.setBackground(QColor(200, 230, 255))  # Light blue for user
            elif role == "assistant":
                item.setBackground(QColor(255, 200, 200))  # Light red for assistant
            else:
                item.setBackground(QColor(200, 200, 200))  # Gray for unknown
                
            self.message_list.addItem(item)
            
        # Update conversation info
        conv_id = conv.get("conversation_id", f"Conversation {self.current_conversation_index + 1}")
        self.conversation_info.setText(f"Conversation: {conv_id}\nMessages: {len(all_messages)}")
        
    def on_message_selected(self, row: int):
        """Handle message selection."""
        if row >= 0 and row < self.message_list.count():
            item = self.message_list.item(row)
            message = item.data(Qt.ItemDataRole.UserRole)
            
            if message:
                self.role_combo.setCurrentText(message.get("role", "user"))
                self.index_label.setText(str(message.get("index", "")))
                self.content_edit.setPlainText(message.get("content", ""))
                
                self.apply_correction_btn.setEnabled(True)
                
    def on_role_changed(self, role: str):
        """Handle role change."""
        # Enable apply button if changes were made
        current_row = self.message_list.currentRow()
        if current_row >= 0:
            item = self.message_list.item(current_row)
            original_message = item.data(Qt.ItemDataRole.UserRole)
            if original_message and role != original_message.get("role"):
                self.apply_correction_btn.setEnabled(True)
                
    def on_content_changed(self):
        """Handle content change."""
        # Enable apply button if changes were made
        current_row = self.message_list.currentRow()
        if current_row >= 0:
            item = self.message_list.item(current_row)
            original_message = item.data(Qt.ItemDataRole.UserRole)
            if original_message:
                new_content = self.content_edit.toPlainText()
                if new_content != original_message.get("content"):
                    self.apply_correction_btn.setEnabled(True)
                    
    def apply_correction(self):
        """Apply the current correction."""
        current_row = self.message_list.currentRow()
        if current_row < 0:
            return
            
        item = self.message_list.item(current_row)
        original_message = item.data(Qt.ItemDataRole.UserRole)
        
        if not original_message:
            return
            
        # Create corrected message
        corrected_message = original_message.copy()
        corrected_message["role"] = self.role_combo.currentText()
        corrected_message["content"] = self.content_edit.toPlainText()
        
        # Update the message in the conversation
        conv = self.conversations[self.current_conversation_index]
        
        # Find and update the message in the appropriate list
        if original_message.get("role") == "user":
            for i, msg in enumerate(conv.get("user_messages", [])):
                if msg.get("index") == original_message.get("index"):
                    conv["user_messages"][i] = corrected_message
                    break
        elif original_message.get("role") == "assistant":
            for i, msg in enumerate(conv.get("agent_messages", [])):
                if msg.get("index") == original_message.get("index"):
                    conv["agent_messages"][i] = corrected_message
                    break
                    
        # Update the list item
        role = corrected_message.get("role", "unknown")
        content_preview = corrected_message.get("content", "")[:100] + "..." if len(corrected_message.get("content", "")) > 100 else corrected_message.get("content", "")
        item.setText(f"[{role.upper()}] {content_preview}")
        
        # Update colors
        if role == "user":
            item.setBackground(QColor(200, 230, 255))
        elif role == "assistant":
            item.setBackground(QColor(255, 200, 200))
        else:
            item.setBackground(QColor(200, 200, 200))
            
        # Mark conversation as corrected
        self.mark_conversation_corrected(self.current_conversation_index)
        
        # Emit signal
        self.conversation_corrected.emit(conv)
        
        # Reset UI
        self.apply_correction_btn.setEnabled(False)
        self.revert_btn.setEnabled(True)
        
        QMessageBox.information(self, "Correction Applied", "Message correction has been applied successfully.")
        
    def revert_changes(self):
        """Revert changes to the current message."""
        current_row = self.message_list.currentRow()
        if current_row >= 0:
            item = self.message_list.item(current_row)
            original_message = item.data(Qt.ItemDataRole.UserRole)
            
            if original_message:
                self.role_combo.setCurrentText(original_message.get("role", "user"))
                self.content_edit.setPlainText(original_message.get("content", ""))
                
        self.apply_correction_btn.setEnabled(False)
        self.revert_btn.setEnabled(False)
        
    def mark_conversation_corrected(self, conv_index: int):
        """Mark a conversation as having corrections."""
        if conv_index not in self.corrections_made:
            self.corrections_made.append(conv_index)
            
        # Update the conversation list item color
        for i in range(self.conversation_list.count()):
            item = self.conversation_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == conv_index:
                item.setBackground(QColor(255, 255, 200))  # Light yellow
                break
                
    def has_corrections(self, conv_index: int) -> bool:
        """Check if a conversation has corrections."""
        return conv_index in self.corrections_made
        
    def update_navigation_buttons(self):
        """Update navigation button states."""
        self.prev_btn.setEnabled(self.current_conversation_index > 0)
        self.next_btn.setEnabled(self.current_conversation_index < len(self.conversations) - 1)
        
    def previous_conversation(self):
        """Navigate to the previous conversation."""
        if self.current_conversation_index > 0:
            self.conversation_list.setCurrentRow(self.current_conversation_index - 1)
            
    def next_conversation(self):
        """Navigate to the next conversation."""
        if self.current_conversation_index < len(self.conversations) - 1:
            self.conversation_list.setCurrentRow(self.current_conversation_index + 1)
            
    def update_progress(self):
        """Update progress display."""
        if not self.conversations:
            self.progress_label.setText("No conversations loaded")
            return
            
        reviewed = len(self.corrections_made)
        total = len(self.conversations)
        
        self.progress_label.setText(f"Progress: {reviewed}/{total} conversations reviewed")
        
        if total > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(reviewed)
        else:
            self.progress_bar.setVisible(False)
            
    def export_corrected_data(self):
        """Export the corrected conversation data."""
        if not self.conversations:
            QMessageBox.warning(self, "No Data", "No conversations to export.")
            return
            
        # For now, just emit the corrected data
        # In a full implementation, you might want to save to a file
        self.labeling_completed.emit(self.conversations)
        
        QMessageBox.information(self, "Export Complete", 
                              f"Exported {len(self.conversations)} conversations with corrections.")
        
    def complete_review(self):
        """Complete the review session."""
        if not self.conversations:
            QMessageBox.warning(self, "No Data", "No conversations to review.")
            return
            
        # Emit the final corrected data
        self.labeling_completed.emit(self.conversations)
        
        QMessageBox.information(self, "Review Complete", 
                              f"Review completed for {len(self.conversations)} conversations.\n"
                              f"Corrections made: {len(self.corrections_made)}")
        
        # Reset the UI
        self.conversations = []
        self.current_conversation_index = 0
        self.corrections_made = []
        self.conversation_list.clear()
        self.message_list.clear()
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Ready to review conversations")
        
        # Disable buttons
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.complete_btn.setEnabled(False) 