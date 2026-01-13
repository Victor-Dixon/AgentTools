#!/usr/bin/env python3
"""
Conversational AI Panel
=======================

GUI panel for interactive "speaking" with ChatGPT using rich conversation context.
"""

import sys
from gui.debug_handler import debug_button
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QLabel, QComboBox, QSplitter, QGroupBox,
    QScrollArea, QFrame, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor

from dreamscape.core.conversational_ai_workflow import ConversationalAIWorkflow

logger = logging.getLogger(__name__)

class ConversationalAIWorker(QThread):
    """Background worker for AI operations."""
    
    response_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, workflow: ConversationalAIWorkflow, operation: str, **kwargs):
        super().__init__()
        self.workflow = workflow
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Execute the AI operation."""
        try:
            if self.operation == "start_session":
                result = self.workflow.start_session(**self.kwargs)
            elif self.operation == "speak":
                result = self.workflow.process_user_message(**self.kwargs)
            elif self.operation == "ask_work":
                result = self.workflow.analyze_work_patterns_from_question(**self.kwargs)
            elif self.operation == "get_suggestions":
                result = self.workflow.generate_workflow_suggestions(**self.kwargs)
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            self.response_ready.emit(result)
            
        except Exception as e:
            logger.error(f"AI operation failed: {e}")
            self.error_occurred.emit(str(e))

class ConversationalAIPanel(QWidget):
    """Panel for conversational AI workflow interaction."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflow = ConversationalAIWorkflow()
        self.current_session = None
        self.worker = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🤖 Conversational AI Workflow")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Session controls
        session_group = QGroupBox("Session Management")
        session_layout = QHBoxLayout()
        
        self.start_session_btn = QPushButton("🚀 Start New Session")
        self.start_session_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }")
        
        self.end_session_btn = QPushButton("🏁 End Session")
        self.end_session_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }")
        self.end_session_btn.setEnabled(False)
        
        self.session_status = QLabel("No active session")
        self.session_status.setStyleSheet("color: #666; font-style: italic;")
        
        session_layout.addWidget(self.start_session_btn)
        session_layout.addWidget(self.end_session_btn)
        session_layout.addWidget(self.session_status)
        session_layout.addStretch()
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # Main conversation area
        conversation_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Conversation
        conversation_group = QGroupBox("💬 Conversation")
        conversation_layout = QVBoxLayout()
        
        # Context type selector
        context_layout = QHBoxLayout()
        context_layout.addWidget(QLabel("Context Type:"))
        
        self.context_type_combo = QComboBox()
        self.context_type_combo.addItems([
            "general", "coding", "writing", "analysis", "planning", "debugging"
        ])
        self.context_type_combo.setCurrentText("general")
        
        context_layout.addWidget(self.context_type_combo)
        context_layout.addStretch()
        
        conversation_layout.addLayout(context_layout)
        
        # Message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setStyleSheet("QLineEdit { padding: 8px; font-size: 14px; }")
        conversation_layout.addWidget(self.message_input)
        
        # Send button
        self.send_btn = QPushButton("📤 Send Message")
        self.send_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")
        self.send_btn.setEnabled(False)
        conversation_layout.addWidget(self.send_btn)
        
        # Conversation history
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setStyleSheet("""
            QTextEdit { 
                background-color: #f8f9fa; 
                border: 1px solid #ddd; 
                padding: 10px; 
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        conversation_layout.addWidget(self.conversation_display)
        
        conversation_group.setLayout(conversation_layout)
        conversation_splitter.addWidget(conversation_group)
        
        # Right panel - Context & Insights
        context_group = QGroupBox("🔍 Context & Insights")
        context_layout = QVBoxLayout()
        
        # Context display
        self.context_display = QTextEdit()
        self.context_display.setReadOnly(True)
        self.context_display.setMaximumHeight(200)
        self.context_display.setStyleSheet("""
            QTextEdit { 
                background-color: #fff3cd; 
                border: 1px solid #ffeaa7; 
                padding: 8px; 
                font-size: 11px;
            }
        """)
        context_layout.addWidget(QLabel("Context Used:"))
        context_layout.addWidget(self.context_display)
        
        # Insights display
        self.insights_display = QTextEdit()
        self.insights_display.setReadOnly(True)
        self.insights_display.setMaximumHeight(150)
        self.insights_display.setStyleSheet("""
            QTextEdit { 
                background-color: #d1ecf1; 
                border: 1px solid #bee5eb; 
                padding: 8px; 
                font-size: 11px;
            }
        """)
        context_layout.addWidget(QLabel("Insights:"))
        context_layout.addWidget(self.insights_display)
        
        # Quick actions
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QVBoxLayout()
        
        self.ask_work_btn = QPushButton("❓ Ask About My Work")
        self.ask_work_btn.setStyleSheet("QPushButton { background-color: #ff9800; color: white; padding: 6px; }")
        self.ask_work_btn.setEnabled(False)
        
        self.get_suggestions_btn = QPushButton("💡 Get Workflow Suggestions")
        self.get_suggestions_btn.setStyleSheet("QPushButton { background-color: #9c27b0; color: white; padding: 6px; }")
        self.get_suggestions_btn.setEnabled(False)
        
        actions_layout.addWidget(self.ask_work_btn)
        actions_layout.addWidget(self.get_suggestions_btn)
        
        actions_group.setLayout(actions_layout)
        context_layout.addWidget(actions_group)
        
        context_group.setLayout(context_layout)
        conversation_splitter.addWidget(context_group)
        
        # Set splitter proportions
        conversation_splitter.setSizes([600, 400])
        layout.addWidget(conversation_splitter)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
        
    @debug_button("setup_connections", "Conversational Ai Panel")
    def setup_connections(self):
        """Setup signal connections."""
        self.start_session_btn.clicked.connect(self.start_session)
        self.end_session_btn.clicked.connect(self.end_session)
        self.send_btn.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        self.ask_work_btn.clicked.connect(self.ask_about_work)
        self.get_suggestions_btn.clicked.connect(self.get_workflow_suggestions)
        
    @debug_button("start_session", "Conversational Ai Panel")
    def start_session(self):
        """Start a new conversation session."""
        try:
            self.set_loading_state(True, "Starting session...")
            
            self.worker = ConversationalAIWorker(self.workflow, "start_session")
            self.worker.response_ready.connect(self.on_session_started)
            self.worker.error_occurred.connect(self.on_error)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            self.on_error(str(e))
    
    @debug_button("on_session_started", "Conversational Ai Panel")
    def on_session_started(self, result: Dict[str, Any]):
        """Handle session start response."""
        try:
            if result.get('success'):
                self.current_session = result
                self.session_status.setText(f"Session: {result['session_id']}")
                self.session_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
                
                # Enable conversation controls
                self.send_btn.setEnabled(True)
                self.ask_work_btn.setEnabled(True)
                self.get_suggestions_btn.setEnabled(True)
                self.start_session_btn.setEnabled(False)
                self.end_session_btn.setEnabled(True)
                
                # Display session info
                self.conversation_display.append(
                    f"<div style='background-color: #e8f5e8; padding: 10px; margin: 5px; border-radius: 5px;'>"
                    f"<b>🤖 AI Assistant:</b> Session started! I've analyzed your work patterns from "
                    f"{len(result.get('work_patterns', {}).get('topics', {}))} conversations. "
                    f"I'm ready to help with context-aware assistance. What would you like to work on?"
                    f"</div>"
                )
                
                # Display work patterns
                self.display_work_patterns(result.get('work_patterns', {}))
                
            else:
                self.on_error(result.get('error', 'Unknown error'))
                
        except Exception as e:
            logger.error(f"Failed to handle session start: {e}")
            self.on_error(str(e))
        finally:
            self.set_loading_state(False, "Session ready")
    
    @debug_button("send_message", "Conversational Ai Panel")
    def send_message(self):
        """Send a message to the AI workflow."""
        message = self.message_input.text().strip()
        if not message:
            return
        
        if not self.current_session:
            QMessageBox.warning(self, "No Session", "Please start a session first.")
            return
        
        try:
            self.set_loading_state(True, "Processing message...")
            
            # Add user message to display
            self.conversation_display.append(
                f"<div style='background-color: #e3f2fd; padding: 10px; margin: 5px; border-radius: 5px;'>"
                f"<b>👤 You:</b> {message}"
                f"</div>"
            )
            
            # Clear input
            self.message_input.clear()
            
            # Send to AI
            context_type = self.context_type_combo.currentText()
            self.worker = ConversationalAIWorker(
                self.workflow, "speak", 
                message=message, context_type=context_type
            )
            self.worker.response_ready.connect(self.on_message_response)
            self.worker.error_occurred.connect(self.on_error)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.on_error(str(e))
    
    @debug_button("on_message_response", "Conversational Ai Panel")
    def on_message_response(self, result: Dict[str, Any]):
        """Handle message response."""
        try:
            # Display AI response
            self.conversation_display.append(
                f"<div style='background-color: #f3e5f5; padding: 10px; margin: 5px; border-radius: 5px;'>"
                f"<b>🤖 AI Assistant:</b> {result.get('response', 'No response generated')}"
                f"</div>"
            )
            
            # Display context used
            if result.get('context_used'):
                self.display_context(result['context_used'])
            
            # Display work analysis
            if result.get('work_analysis'):
                self.display_insights(result['work_analysis'])
            
            # Scroll to bottom
            self.conversation_display.moveCursor(QTextCursor.MoveOperation.End)
                
        except Exception as e:
            logger.error(f"Failed to handle message response: {e}")
            self.on_error(str(e))
        finally:
            self.set_loading_state(False, "Ready")
    
    @debug_button("ask_about_work", "Conversational Ai Panel")
    def ask_about_work(self):
        """Ask AI about work patterns."""
        try:
            question, ok = QMessageBox.question(
                self, "Ask About Work", 
                "What would you like to know about your work patterns?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            
            if ok:
                # For now, use a default question - could be enhanced with a dialog
                question_text = "What are my main work patterns and how can I improve my workflow?"
                
                self.set_loading_state(True, "Analyzing work patterns...")
                
                self.worker = ConversationalAIWorker(
                    self.workflow, "ask_work", question=question_text
                )
                self.worker.response_ready.connect(self.on_work_analysis)
                self.worker.error_occurred.connect(self.on_error)
                self.worker.start()
                
        except Exception as e:
            logger.error(f"Failed to ask about work: {e}")
            self.on_error(str(e))
    
    @debug_button("on_work_analysis", "Conversational Ai Panel")
    def on_work_analysis(self, result: Dict[str, Any]):
        """Handle work analysis response."""
        try:
            # Display analysis
            if result.get('analysis'):
                self.conversation_display.append(
                    f"<div style='background-color: #fff3cd; padding: 10px; margin: 5px; border-radius: 5px;'>"
                    f"<b>📊 Work Analysis:</b> {result['analysis']}"
                    f"</div>"
                )
            
            # Display patterns
            if result.get('patterns'):
                patterns = result['patterns']
                patterns_text = []
                for category, items in patterns.items():
                    if items:
                        if isinstance(items, dict):
                            items_text = ", ".join([f"{k} ({v})" for k, v in items.items()])
                        else:
                            items_text = ", ".join(str(item) for item in items)
                        patterns_text.append(f"<b>{category.title()}:</b> {items_text}")
                
                if patterns_text:
                    self.conversation_display.append(
                        f"<div style='background-color: #d1ecf1; padding: 10px; margin: 5px; border-radius: 5px;'>"
                        f"<b>🔍 Patterns Found:</b><br>{'<br>'.join(patterns_text)}"
                        f"</div>"
                    )
                
        except Exception as e:
            logger.error(f"Failed to handle work analysis: {e}")
            self.on_error(str(e))
        finally:
            self.set_loading_state(False, "Ready")
    
    @debug_button("get_workflow_suggestions", "Conversational Ai Panel")
    def get_workflow_suggestions(self):
        """Get workflow suggestions."""
        try:
            task, ok = QMessageBox.question(
                self, "Workflow Suggestions", 
                "What task would you like suggestions for?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            
            if ok:
                # For now, use a default task - could be enhanced with a dialog
                task_text = "Improve my overall development workflow"
                
                self.set_loading_state(True, "Generating suggestions...")
                
                self.worker = ConversationalAIWorker(
                    self.workflow, "get_suggestions", task=task_text
                )
                self.worker.response_ready.connect(self.on_suggestions)
                self.worker.error_occurred.connect(self.on_error)
                self.worker.start()
                
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            self.on_error(str(e))
    
    @debug_button("on_suggestions", "Conversational Ai Panel")
    def on_suggestions(self, result: Dict[str, Any]):
        """Handle suggestions response."""
        try:
            # Display suggestions
            if result.get('suggestions'):
                suggestions_text = "\n".join([f"• {suggestion}" for suggestion in result['suggestions']])
                self.conversation_display.append(
                    f"<div style='background-color: #e8f5e8; padding: 10px; margin: 5px; border-radius: 5px;'>"
                    f"<b>💡 Workflow Suggestions:</b><br>{suggestions_text}"
                    f"</div>"
                )
            
            # Display context used
            if result.get('context_used'):
                self.display_context(result['context_used'])
                
        except Exception as e:
            logger.error(f"Failed to handle suggestions: {e}")
            self.on_error(str(e))
        finally:
            self.set_loading_state(False, "Ready")
    
    @debug_button("end_session", "Conversational Ai Panel")
    def end_session(self):
        """End the current session."""
        try:
            if not self.current_session:
                return
            
            self.set_loading_state(True, "Ending session...")
            
            result = self.workflow.save_session_summary()
            
            if result.get('summary'):
                # Display session summary
                summary = result['summary']
                self.conversation_display.append(
                    f"<div style='background-color: #f8d7da; padding: 10px; margin: 5px; border-radius: 5px;'>"
                    f"<b>🏁 Session Ended:</b> {summary.get('total_messages', 0)} messages, "
                    f"session saved to {result.get('file_path', 'unknown location')}."
                    f"</div>"
                )
                
                # Reset UI
                self.current_session = None
                self.session_status.setText("No active session")
                self.session_status.setStyleSheet("color: #666; font-style: italic;")
                
                self.send_btn.setEnabled(False)
                self.ask_work_btn.setEnabled(False)
                self.get_suggestions_btn.setEnabled(False)
                self.start_session_btn.setEnabled(True)
                self.end_session_btn.setEnabled(False)
                
                # Clear displays
                self.context_display.clear()
                self.insights_display.clear()
                
            else:
                self.on_error(result.get('error', 'Unknown error'))
                
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            self.on_error(str(e))
        finally:
            self.set_loading_state(False, "Ready")
    
    def display_work_patterns(self, patterns: Dict[str, Any]):
        """Display work patterns in context area."""
        try:
            text = "<b>📊 Your Work Patterns:</b><br><br>"
            
            if patterns.get('topics'):
                text += "<b>Top Topics:</b><br>"
                for topic, count in list(patterns['topics'].items())[:5]:
                    text += f"• {topic} ({count} conversations)<br>"
                text += "<br>"
            
            if patterns.get('technologies'):
                text += "<b>Technologies:</b><br>"
                for tech, count in list(patterns['technologies'].items())[:5]:
                    text += f"• {tech} ({count} mentions)<br>"
                text += "<br>"
            
            if patterns.get('project_themes'):
                text += "<b>Project Themes:</b><br>"
                for theme in patterns['project_themes'][:3]:
                    text += f"• {theme}<br>"
            
            self.context_display.setHtml(text)
            
        except Exception as e:
            logger.error(f"Failed to display work patterns: {e}")
    
    def display_context(self, context_data: Dict[str, Any]):
        """Display context information."""
        try:
            text = "<b>🔍 Context Used:</b><br><br>"
            
            if context_data.get('conversations'):
                text += f"<b>Relevant Conversations ({context_data.get('total_results', 0)}):</b><br>"
                for conv in context_data['conversations'][:3]:
                    text += f"• <b>{conv['title']}</b> ({conv['timestamp']})<br>"
                    text += f"  {conv['content'][:100]}...<br><br>"
            
            text += f"<b>Context Type:</b> {context_data.get('context_type', 'general')}"
            
            self.context_display.setHtml(text)
            
        except Exception as e:
            logger.error(f"Failed to display context: {e}")
    
    def display_insights(self, insights: Dict[str, Any]):
        """Display insights from AI response."""
        try:
            text = "<b>💡 Insights:</b><br><br>"
            
            if insights.get('key_points'):
                text += "<b>Key Points:</b><br>"
                for point in insights['key_points'][:3]:
                    text += f"• {point}<br>"
                text += "<br>"
            
            if insights.get('suggestions'):
                text += "<b>Suggestions:</b><br>"
                for suggestion in insights['suggestions'][:3]:
                    text += f"• {suggestion}<br>"
            
            self.insights_display.setHtml(text)
            
        except Exception as e:
            logger.error(f"Failed to display insights: {e}")
    
    @debug_button("set_loading_state", "Conversational Ai Panel")
    def set_loading_state(self, loading: bool, message: str):
        """Set loading state."""
        self.progress_bar.setVisible(loading)
        self.status_label.setText(message)
        
        # Disable/enable controls
        self.send_btn.setEnabled(not loading and self.current_session is not None)
        self.ask_work_btn.setEnabled(not loading and self.current_session is not None)
        self.get_suggestions_btn.setEnabled(not loading and self.current_session is not None)
        self.start_session_btn.setEnabled(not loading and self.current_session is None)
        self.end_session_btn.setEnabled(not loading and self.current_session is not None)
    
    @debug_button("on_error", "Conversational Ai Panel")
    def on_error(self, error_message: str):
        """Handle errors."""
        logger.error(f"Conversational AI error: {error_message}")
        self.set_loading_state(False, f"Error: {error_message}")
        
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if self.current_session:
                self.workflow.end_session()
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}") 