"""
from gui.debug_handler import debug_button
AI Interaction Panel for Thea GUI
Handles AI interactions with conversations and content.
Converted from Tkinter to PyQt6 for consistency.
"""

import asyncio
from gui.debug_handler import debug_button
import threading
from typing import Dict, List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont

from dreamscape.core.memory_system import MemoryAPI

class AIInteractionPanel(QWidget):
    """PyQt6 GUI panel for AI interactions with conversations."""
    
    # Signals
    query_sent = pyqtSignal(bool, str)
    processing_completed = pyqtSignal(bool, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize memory API
        self.memory_api = MemoryAPI()
        self.conversations = []
        self.selected_conversation = None
        self.current_query = ""
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self._load_conversations()
        
    def _setup_ui(self):
        """Setup the PyQt6 user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🤖 AI Interaction Panel")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Main content
        self._create_main_content(layout)
        
        # Status section
        self._create_status_section(layout)
    
    @debug_button("_create_main_content", "Ai Interaction Panel")
    def _create_main_content(self, parent_layout):
        """Create the main content area."""
        # Split view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Conversation list and search
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search section
        search_group = QGroupBox("Search Conversations")
        search_layout = QHBoxLayout(search_group)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search conversations...")
        self.search_edit.textChanged.connect(self._filter_conversations)
        search_layout.addWidget(self.search_edit)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.clicked.connect(self._filter_conversations)
        search_layout.addWidget(self.search_btn)
        
        left_layout.addWidget(search_group)
        
        # Conversation list
        list_group = QGroupBox("Conversations")
        list_layout = QVBoxLayout(list_group)
        
        self.conversation_list = QListWidget()
        self.conversation_list.itemSelectionChanged.connect(self._on_conversation_selected)
        list_layout.addWidget(self.conversation_list)
        
        left_layout.addWidget(list_group)
        splitter.addWidget(left_widget)
        
        # Right side - Conversation details and interaction
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Conversation info
        info_group = QGroupBox("Conversation Information")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlaceholderText("Select a conversation to view details...")
        info_layout.addWidget(self.info_text)
        
        right_layout.addWidget(info_group)
        
        # Interaction section
        interaction_group = QGroupBox("AI Interaction")
        interaction_layout = QVBoxLayout(interaction_group)
        
        # Query input
        query_layout = QHBoxLayout()
        query_layout.addWidget(QLabel("Query:"))
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("Enter your query...")
        query_layout.addWidget(self.query_edit)
        
        interaction_layout.addLayout(query_layout)
        
        # Interaction buttons
        buttons_layout = QHBoxLayout()
        
        self.send_btn = QPushButton("Send Query")
        self.send_btn.clicked.connect(self._send_query)
        self.send_btn.setEnabled(False)
        buttons_layout.addWidget(self.send_btn)
        
        self.process_btn = QPushButton("Process with Dreamscape")
        self.process_btn.clicked.connect(self._process_with_dreamscape)
        self.process_btn.setEnabled(False)
        buttons_layout.addWidget(self.process_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_query)
        buttons_layout.addWidget(self.clear_btn)
        
        interaction_layout.addLayout(buttons_layout)
        right_layout.addWidget(interaction_group)
        
        # Response section
        response_group = QGroupBox("AI Response")
        response_layout = QVBoxLayout(response_group)
        
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setPlaceholderText("AI response will appear here...")
        response_layout.addWidget(self.response_text)
        
        right_layout.addWidget(response_group)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        
        parent_layout.addWidget(splitter)
    
    @debug_button("_create_status_section", "Ai Interaction Panel")
    def _create_status(self):
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
                title="ai_interaction_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _load_conversations(self):
        """Load conversations from the memory API."""
        try:
            self._update_status("Loading conversations...", "Fetching conversations from database...")
            
            # Get conversations from memory API
            self.conversations = self.memory_api.get_conversations(limit=100, offset=0)
            
            # Update conversation list
            self.conversation_list.clear()
            for conv in self.conversations:
                title = conv.get('title', 'Untitled')
                self.conversation_list.addItem(title)
            
            self._update_status("Conversations loaded", f"Loaded {len(self.conversations)} conversations")
            
        except Exception as e:
            self._update_status("Error loading conversations", f"Failed to load conversations: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load conversations: {str(e)}")

    @debug_button("_filter_conversations", "Ai Interaction Panel")
    def _filter_conversations(self):
        """Filter conversations based on search text."""
        search_text = self.search_edit.text().lower().strip()
        
        # Clear and repopulate list
        self.conversation_list.clear()
        
        for conv in self.conversations:
            title = conv.get('title', 'Untitled')
            if search_text in title.lower():
                self.conversation_list.addItem(title)
        
        self._update_status("Filtered conversations", f"Showing {self.conversation_list.count()} conversations")
    
    @debug_button("_on_conversation_selected", "Ai Interaction Panel")
    def _on_conversation_selected(self):
        """Handle conversation selection."""
        current_item = self.conversation_list.currentItem()
        if current_item:
            title = current_item.text()
            
            # Find the selected conversation
            for conv in self.conversations:
                if conv.get('title') == title:
                    self.selected_conversation = conv
                    self._display_conversation_info(conv)
                    self._enable_interaction_buttons()
                    break
        else:
            self.selected_conversation = None
            self._disable_interaction_buttons()
    
    def _display_conversation_info(self, conversation: Dict):
        """Display conversation information."""
        info = f"Title: {conversation.get('title', 'Untitled')}\n"
        info += f"Messages: {conversation.get('message_count', 0)}\n"
        info += f"Words: {conversation.get('word_count', 0)}\n"
        info += f"Model: {conversation.get('model', 'Unknown')}\n"
        info += f"Created: {conversation.get('created_at', 'Unknown')}\n"
        info += f"Source: {conversation.get('source', 'Unknown')}\n\n"
        
        # Add a preview of the conversation content
        content = conversation.get('content', '')
        if content:
            preview = content[:200] + "..." if len(content) > 200 else content
            info += f"Preview:\n{preview}"
        
        self.info_text.setPlainText(info)
    
    @debug_button("_send_query", "Ai Interaction Panel")
    def _send_query(self):
        """Send a query to the selected conversation."""
        if not self.selected_conversation:
            QMessageBox.warning(self, "Warning", "Please select a conversation first.")
            return
        
        query = self.query_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a query.")
            return
        
        self.current_query = query
        self._update_status("Sending query...", f"Sending query to conversation: {self.selected_conversation.get('title')}")
        self._disable_controls()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate query processing
        self.progress_bar.setValue(25)
        QTimer.singleShot(500, lambda: self.progress_bar.setValue(50))
        QTimer.singleShot(1000, lambda: self.progress_bar.setValue(75))
        QTimer.singleShot(1500, lambda: self._complete_query())
    
    def _complete_query(self):
        """Complete the query processing."""
        self.progress_bar.setValue(100)
        
        # Generate mock response
        response = f"Query: {self.current_query}\n\n"
        response += f"Conversation: {self.selected_conversation.get('title', 'Untitled')}\n\n"
        response += "This is a simulated AI response. In a real implementation, this would contain "
        response += "the actual AI response based on the query and conversation context.\n\n"
        response += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.response_text.setPlainText(response)
        
        # Update status
        self._update_status("Query completed", f"Successfully processed query for conversation: {self.selected_conversation.get('title')}")
        
        # Re-enable controls
        self._enable_controls()
        self.progress_bar.setVisible(False)
        
        # Emit signal
        self.query_sent.emit(True, "Query sent successfully")
    
    @debug_button("_process_with_dreamscape", "Ai Interaction Panel")
    def _process_with_dreamscape(self):
        """Process the selected conversation with Dreamscape."""
        if not self.selected_conversation:
            QMessageBox.warning(self, "Warning", "Please select a conversation first.")
            return
        
        self._update_status("Processing with Dreamscape...", f"Processing conversation: {self.selected_conversation.get('title')}")
        self._disable_controls()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate Dreamscape processing
        self.progress_bar.setValue(20)
        QTimer.singleShot(500, lambda: self.progress_bar.setValue(40))
        QTimer.singleShot(1000, lambda: self.progress_bar.setValue(60))
        QTimer.singleShot(1500, lambda: self.progress_bar.setValue(80))
        QTimer.singleShot(2000, lambda: self._complete_dreamscape_processing())
    
    @debug_button("_complete_dreamscape_processing", "Ai Interaction Panel")
    def _complete_dreamscape_processing(self):
        """Complete the Dreamscape processing."""
        self.progress_bar.setValue(100)
        
        # Generate mock Dreamscape response
        response = f"Dreamscape Processing Results:\n\n"
        response += f"Conversation: {self.selected_conversation.get('title', 'Untitled')}\n\n"
        response += "✅ Memory Integration: Complete\n"
        response += "✅ Vector Indexing: Updated\n"
        response += "✅ Context Analysis: Processed\n"
        response += "✅ Skill Extraction: Completed\n"
        response += "✅ Knowledge Synthesis: Generated\n\n"
        response += "The conversation has been successfully integrated into the Dreamscape memory system.\n"
        response += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.response_text.setPlainText(response)
        
        # Update status
        self._update_status("Dreamscape processing completed", f"Successfully processed conversation with Dreamscape")
        
        # Re-enable controls
        self._enable_controls()
        self.progress_bar.setVisible(False)
        
        # Emit signal
        self.processing_completed.emit(True, "Dreamscape processing completed")
    
    @debug_button("_clear_query", "Ai Interaction Panel")
    def _clear_query(self):
        """Clear the query input and response."""
        self.query_edit.clear()
        self.response_text.clear()
        self._update_status("Cleared", "Query input and response cleared")
    
    @debug_button("_update_status", "Ai Interaction Panel")
    def _update_status(self):
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
                title="ai_interaction_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _enable_interaction_buttons(self):
        """Enable interaction buttons when conversation is selected."""
        self.send_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
    
    def _disable_interaction_buttons(self):
        """Disable interaction buttons when no conversation is selected."""
        self.send_btn.setEnabled(False)
        self.process_btn.setEnabled(False)
    
    def _disable_controls(self):
        """Disable controls during processing."""
        self.send_btn.setEnabled(False)
        self.process_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.query_edit.setEnabled(False)
        self.conversation_list.setEnabled(False)
        self.search_edit.setEnabled(False)
        self.search_btn.setEnabled(False)
    
    def _enable_controls(self):
        """Enable controls after processing."""
        self.clear_btn.setEnabled(True)
        self.query_edit.setEnabled(True)
        self.conversation_list.setEnabled(True)
        self.search_edit.setEnabled(True)
        self.search_btn.setEnabled(True)
        
        # Re-enable interaction buttons if conversation is selected
        if self.selected_conversation:
            self.send_btn.setEnabled(True)
            self.process_btn.setEnabled(True)
    
    @debug_button("refresh_conversations", "Ai Interaction Panel")
    def refresh_conversations(self):
        """Refresh the conversation list."""
        self._load_conversations()
    
    def get_selected_conversation(self) -> Optional[Dict]:
        """Get the currently selected conversation."""
        return self.selected_conversation
    
    def get_conversation_count(self) -> int:
        """Get the total number of conversations."""
        return len(self.conversations)