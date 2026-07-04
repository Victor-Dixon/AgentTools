"""
Intelligent Agent Panel for Thea GUI
Handles intelligent agent interactions and queries.
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

from dreamscape.core.intelligent_agent_system import IntelligentAgentSystem

class IntelligentAgentPanel(QWidget):
    """PyQt6 GUI panel for intelligent agent interactions."""
    
    # Signals
    query_completed = pyqtSignal(bool, str)
    status_updated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize agent system
        self.agent_system = IntelligentAgentSystem()
        self.current_query = ""
        self.query_history = []
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the PyQt6 user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🧠 Intelligent Agent System")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Main content
        self._create_main_content(layout)
        
        # Status section
        self._create_status_section(layout)
    
    @debug_button("_create_main_content", "Intelligent Agent Panel")
    def _create_main_content(self, parent_layout):
        """Create the main content area."""
        # Split view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Query interface
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Query section
        query_group = QGroupBox("Query Interface")
        query_layout = QVBoxLayout(query_group)
        
        # Query input
        query_input_layout = QHBoxLayout()
        query_input_layout.addWidget(QLabel("Query:"))
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("Enter your query here...")
        query_input_layout.addWidget(self.query_edit)
        
        query_layout.addLayout(query_input_layout)
        
        # Query buttons
        query_buttons_layout = QHBoxLayout()
        
        self.send_query_btn = QPushButton("Send Query")
        self.send_query_btn.clicked.connect(self._send_query)
        query_buttons_layout.addWidget(self.send_query_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_query)
        query_buttons_layout.addWidget(self.clear_btn)
        
        self.status_btn = QPushButton("Status")
        self.status_btn.clicked.connect(self._show_status)
        query_buttons_layout.addWidget(self.status_btn)
        
        query_layout.addLayout(query_buttons_layout)
        left_layout.addWidget(query_group)
        
        # Response section
        response_group = QGroupBox("Agent Response")
        response_layout = QVBoxLayout(response_group)
        
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setPlaceholderText("Agent response will appear here...")
        response_layout.addWidget(self.response_text)
        
        left_layout.addWidget(response_group)
        splitter.addWidget(left_widget)
        
        # Right side - History and details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Query history
        history_group = QGroupBox("Query History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        self.history_list.itemSelectionChanged.connect(self._on_history_selected)
        history_layout.addWidget(self.history_list)
        
        right_layout.addWidget(history_group)
        
        # Agent details
        details_group = QGroupBox("Agent Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        self.details_text.setPlaceholderText("Agent details will appear here...")
        details_layout.addWidget(self.details_text)
        
        right_layout.addWidget(details_group)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 300])
        
        parent_layout.addWidget(splitter)
    
    @debug_button("_create_status_section", "Intelligent Agent Panel")
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
                title="intelligent_agent_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _send_query(self):
        """Send a query to the intelligent agent."""
        query = self.query_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a query.")
            return
        
        self.current_query = query
        self._update_status("Processing query...", f"Sending query: {query}")
        self._disable_controls()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate processing
        self.progress_bar.setValue(25)
        QTimer.singleShot(500, lambda: self.progress_bar.setValue(50))
        QTimer.singleShot(1000, lambda: self.progress_bar.setValue(75))
        QTimer.singleShot(1500, lambda: self._complete_query())

    def _complete_query(self):
        """Complete the query processing."""
        self.progress_bar.setValue(100)
        
        # Generate mock response
        response = f"Response to: {self.current_query}\n\n"
        response += "This is a simulated response from the intelligent agent system. "
        response += "In a real implementation, this would contain the actual agent response "
        response += "based on the query and available context.\n\n"
        response += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.response_text.setPlainText(response)
        
        # Add to history
        self._add_to_history(self.current_query, response)
        
        # Update status
        self._update_status("Query completed", f"Successfully processed query: {self.current_query}")
        
        # Re-enable controls
        self._enable_controls()
        self.progress_bar.setVisible(False)
        
        # Emit signal
        self.query_completed.emit(True, "Query completed successfully")
    
    @debug_button("_clear_query", "Intelligent Agent Panel")
    def _clear_query(self):
        """Clear the query input and response."""
        self.query_edit.clear()
        self.response_text.clear()
        self._update_status("Cleared", "Query input and response cleared")
    
    @debug_button("_show_status", "Intelligent Agent Panel")
    def _show_status(self):
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
                title="intelligent_agent_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _add_to_history(self, query: str, response: str):
        """Add query and response to history."""
        history_item = {
            'query': query,
            'response': response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.query_history.append(history_item)
        
        # Update history list
        self.history_list.addItem(f"{history_item['timestamp']}: {query[:50]}...")
    
    @debug_button("_on_history_selected", "Intelligent Agent Panel")
    def _on_history_selected(self):
        """Handle history item selection."""
        current_item = self.history_list.currentItem()
        if current_item:
            index = self.history_list.row(current_item)
            if 0 <= index < len(self.query_history):
                history_item = self.query_history[index]
                
                # Show query and response
                self.query_edit.setText(history_item['query'])
                self.response_text.setPlainText(history_item['response'])
                
                # Show details
                details = f"Query: {history_item['query']}\n\n"
                details += f"Response: {history_item['response']}\n\n"
                details += f"Timestamp: {history_item['timestamp']}"
                self.details_text.setPlainText(details)
    
    @debug_button("_update_status", "Intelligent Agent Panel")
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
                title="intelligent_agent_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _disable_controls(self):
        """Disable controls during processing."""
        self.send_query_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.status_btn.setEnabled(False)
        self.query_edit.setEnabled(False)

    def _enable_controls(self):
        """Enable controls after processing."""
        self.send_query_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.status_btn.setEnabled(True)
        self.query_edit.setEnabled(True)
    
    @debug_button("refresh_agent_status", "Intelligent Agent Panel")
    def refresh_agent_status(self):
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
                title="intelligent_agent_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def get_agent_info(self) -> Dict:
        """Get information about the intelligent agent system."""
        return {
            'system': 'Intelligent Agent System',
            'status': 'Online',
            'queries_processed': len(self.query_history),
            'last_query': self.query_history[-1]['timestamp'] if self.query_history else None
        } 