#!/usr/bin/env python3
"""
Scraper Panel for Dream.OS GUI
==============================

PyQt6 GUI panel that integrates with the ScraperOrchestrator.
Converted from Tkinter to PyQt6 for consistency.
"""

import threading
from gui.debug_handler import debug_button
import queue
from typing import Optional, List
import logging
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QProgressBar,
    QGroupBox,
    QGridLayout,
    QMessageBox,
    QFileDialog,
    QSplitter,
    QListWidget,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QObject
from PyQt6.QtGui import QFont

from dreamscape.scrapers.chatgpt_scraper import ChatGPTScraper
from dreamscape.core.scraping_system import (
    ScraperOrchestrator,
    ConversationData,
    ScrapingResult,
)

logger = logging.getLogger(__name__)


# EDIT START: Worker for scraping with progress bar
class ScraperWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    login_completed = pyqtSignal(bool, str)

    def __init__(self, login_mode, username=None, password=None, cookie_file=None):
        super().__init__()
        self.login_mode = login_mode  # 'credentials' or 'cookies'
        self.username = username
        self.password = password
        self.cookie_file = cookie_file

    def run(self):
        try:
            if self.login_mode == "credentials":
                scraper = ChatGPTScraper(username=self.username, password=self.password)

                def progress_callback(current, total, message):
                    self.progress_updated.emit(current, total, message)

                conversations = scraper.get_conversation_list(
                    progress_callback=progress_callback
                )
                success = bool(conversations)
                msg = (
                    f"Login successful, {len(conversations)} chats found"
                    if success
                    else "Login failed or no conversations scraped"
                )
                self.login_completed.emit(success, msg)
            elif self.login_mode == "cookies":
                scraper = ChatGPTScraper()

                def progress_callback(current, total, message):
                    self.progress_updated.emit(current, total, message)

                # Load cookies and extract
                scraper.cookie_manager.load_cookies(scraper.driver)
                conversations = scraper.get_conversation_list(
                    progress_callback=progress_callback
                )
                success = bool(conversations)
                msg = (
                    f"Login with cookies successful, {len(conversations)} chats found"
                    if success
                    else "Login with cookies failed or no conversations scraped"
                )
                self.login_completed.emit(success, msg)
        except Exception as e:
            self.login_completed.emit(False, str(e))


# EDIT END


class ScraperPanel(QWidget):
    """PyQt6 GUI panel for ChatGPT scraping operations."""

    # Signals
    login_completed = pyqtSignal(bool, str)
    extraction_completed = pyqtSignal(bool, str)
    content_extraction_completed = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize state
        self.orchestrator: Optional[ScraperOrchestrator] = None
        self.conversations: List[ConversationData] = []
        self.thread_queue = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None

        # Setup UI
        self._setup_ui()
        self._setup_threading()

        logger.info("ScraperPanel initialized")

    def _setup_ui(self):
        """Setup the PyQt6 user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("ChatGPT Scraper")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Control Panel
        self._create_control_panel(layout)

        # Status Panel
        self._create_status(layout)

        # Results Panel
        self._create_results_panel(layout)

        # AI Interaction Panel
        self._create_interaction_panel(layout)

        # EDIT START: Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        # EDIT END

    @debug_button("_create_control_panel", "Scraper Panel")
    def _create_control_panel(self, parent_layout):
        """Create the control panel."""
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout(control_group)

        # Login Section
        login_group = QGroupBox("Login")
        login_layout = QVBoxLayout(login_group)

        # Credentials
        cred_layout = QGridLayout()

        cred_layout.addWidget(QLabel("Username:"), 0, 0)
        self.username_edit = QLineEdit()
        cred_layout.addWidget(self.username_edit, 0, 1)

        cred_layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        cred_layout.addWidget(self.password_edit, 1, 1)

        login_layout.addLayout(cred_layout)

        # Cookie file
        cookie_layout = QHBoxLayout()
        cookie_layout.addWidget(QLabel("Cookie File:"))
        self.cookie_file_edit = QLineEdit("chatgpt_cookies.pkl")
        cookie_layout.addWidget(self.cookie_file_edit)

        login_layout.addLayout(cookie_layout)

        # Login buttons
        login_buttons_layout = QHBoxLayout()

        self.login_button = QPushButton("Login with Credentials")
        self.login_button.clicked.connect(self._login)
        login_buttons_layout.addWidget(self.login_button)

        self.cookie_login_button = QPushButton("Login with Cookies")
        self.cookie_login_button.clicked.connect(self._login_with_cookies)
        login_buttons_layout.addWidget(self.cookie_login_button)

        login_layout.addLayout(login_buttons_layout)
        control_layout.addWidget(login_group)

        # Scraping Section
        scraping_group = QGroupBox("Scraping")
        scraping_layout = QVBoxLayout(scraping_group)

        # Options
        options_layout = QGridLayout()

        options_layout.addWidget(QLabel("Max Conversations:"), 0, 0)
        self.max_conv_edit = QLineEdit("1500")
        options_layout.addWidget(self.max_conv_edit, 0, 1)

        options_layout.addWidget(QLabel("Output File:"), 1, 0)
        self.output_file_edit = QLineEdit("chatgpt_conversations.json")
        options_layout.addWidget(self.output_file_edit, 1, 1)

        scraping_layout.addLayout(options_layout)

        # Scraping buttons
        scraping_buttons_layout = QHBoxLayout()

        self.extract_button = QPushButton("Extract Conversations")
        self.extract_button.clicked.connect(self._extract_conversations)
        scraping_buttons_layout.addWidget(self.extract_button)

        self.content_button = QPushButton("Extract Content")
        self.content_button.clicked.connect(self._extract_content)
        scraping_buttons_layout.addWidget(self.content_button)

        self.save_button = QPushButton("Save Results")
        self.save_button.clicked.connect(self._save_results)
        scraping_buttons_layout.addWidget(self.save_button)

        scraping_layout.addLayout(scraping_buttons_layout)
        control_layout.addWidget(scraping_group)

        parent_layout.addWidget(control_group)

    @debug_button("_create_status", "Scraper Panel")
    def _create_status(self, parent_layout):
        """Create statistics grid using shared components."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        try:
            # Create statistics grid with panel-specific data
            stats_data = {
                "Total": 0,
                "Active": 0,
                "Completed": 0
            }
            
            stats_widget = components.create_statistics_grid(
                stats_data=stats_data,
                title="scraper_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    @debug_button("_create_results_panel", "Scraper Panel")
    def _create_results_panel(self, parent_layout):
        """Create the results panel using shared component."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        self.results_table_group = components.create_data_table(
            title="Results",
            headers=["Title", "Messages", "Model", "Status", "URL"],
            data=[],  # Will be populated later
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.results_table = self.results_table_group.table  # Access the table for updates
        parent_layout.addWidget(self.results_table_group)

    @debug_button("_create_interaction_panel", "Scraper Panel")
    def _create_interaction_panel(self, parent_layout):
        """Create the AI interaction panel using shared component."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        interaction_group = QGroupBox("AI Interaction")
        interaction_layout = QVBoxLayout(interaction_group)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        # Left side - conversation list using shared component
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Conversations"))
        self.conv_list_group = components.create_data_list(
            title="Conversations",
            items=[],  # Will be populated later
            selection_mode=QListWidget.SelectionMode.SingleSelection,
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.conv_list = self.conv_list_group.findChild(QListWidget)
        self.conv_list.itemSelectionChanged.connect(self._on_conversation_selected)
        left_layout.addWidget(self.conv_list_group)
        splitter.addWidget(left_widget)
        # Right side - conversation content and interaction
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Conversation content
        content_group = QGroupBox("Conversation Content")
        content_layout = QVBoxLayout(content_group)

        self.conversation_content = QTextEdit()
        self.conversation_content.setReadOnly(True)
        content_layout.addWidget(self.conversation_content)

        right_layout.addWidget(content_group)

        # Interaction controls
        interaction_controls_group = QGroupBox("Interaction")
        interaction_controls_layout = QVBoxLayout(interaction_controls_group)

        # Prompt input
        prompt_layout = QHBoxLayout()
        prompt_layout.addWidget(QLabel("Prompt:"))
        self.prompt_edit = QLineEdit()
        prompt_layout.addWidget(self.prompt_edit)

        interaction_controls_layout.addLayout(prompt_layout)

        # Interaction buttons
        interaction_buttons_layout = QHBoxLayout()

        self.send_button = QPushButton("Send Prompt")
        self.send_button.clicked.connect(self._send_prompt)
        interaction_buttons_layout.addWidget(self.send_button)

        self.regenerate_button = QPushButton("Regenerate Response")
        self.regenerate_button.clicked.connect(self._regenerate_response)
        interaction_buttons_layout.addWidget(self.regenerate_button)

        interaction_controls_layout.addLayout(interaction_buttons_layout)
        right_layout.addWidget(interaction_controls_group)

        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([200, 400])

        interaction_layout.addWidget(splitter)
        parent_layout.addWidget(interaction_group)

    def _setup_threading(self):
        """Setup threading for background operations."""
        self.worker_thread = None
        self.thread_queue = queue.Queue()

    @debug_button("_on_conversation_selected", "Scraper Panel")
    def _on_conversation_selected(self):
        """Handle conversation selection."""
        current_item = self.conv_list.currentItem()
        if current_item:
            conversation_title = current_item.text()
            # Find conversation data and update content
            for conv in self.conversations:
                if conv.title == conversation_title:
                    self._update_conversation_content(conv)
                    break

    @debug_button("_send_prompt", "Scraper Panel")
    def _send_prompt(self):
        """Send a prompt to the selected conversation."""
        current_item = self.conv_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a conversation first.")
            return

        prompt = self.prompt_edit.text().strip()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt.")
            return

        conversation_title = current_item.text()
        # Find conversation and send prompt
        for conv in self.conversations:
            if conv.title == conversation_title:
                self._send_prompt_worker(conv, prompt)
                break

    @debug_button("_send_prompt_worker", "Scraper Panel")
    def _send_prompt_worker(self, conversation: dict, prompt: str):
        """Worker method for sending prompts."""
        try:
            self._update_status(
                "Sending prompt...", "Sending prompt to conversation..."
            )
            self._disable_controls()

            # This would integrate with the actual scraper
            # For now, just simulate the operation
            QTimer.singleShot(
                2000,
                lambda: self._handle_send_prompt_result(
                    ScrapingResult(success=True, message="Prompt sent successfully")
                ),
            )

        except Exception as e:
            self._handle_send_prompt_result(
                ScrapingResult(success=False, message=str(e))
            )

    @debug_button("_regenerate_response", "Scraper Panel")
    def _regenerate_response(self):
        """Regenerate response for the selected conversation."""
        current_item = self.conv_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a conversation first.")
            return

        conversation_title = current_item.text()
        # Find conversation and regenerate response
        for conv in self.conversations:
            if conv.title == conversation_title:
                self._regenerate_response_worker(conv)
                break

    @debug_button("_regenerate_response_worker", "Scraper Panel")
    def _regenerate_response_worker(self, conversation: dict):
        """Worker method for regenerating responses."""
        try:
            self._update_status(
                "Regenerating response...", "Regenerating AI response..."
            )
            self._disable_controls()

            # This would integrate with the actual scraper
            # For now, just simulate the operation
            QTimer.singleShot(
                2000,
                lambda: self._handle_regenerate_response_result(
                    ScrapingResult(
                        success=True, message="Response regenerated successfully"
                    )
                ),
            )

        except Exception as e:
            self._handle_regenerate_response_result(
                ScrapingResult(success=False, message=str(e))
            )

    @debug_button("_handle_send_prompt_result", "Scraper Panel")
    def _handle_send_prompt_result(self, result: ScrapingResult):
        """Handle send prompt result."""
        self._enable_controls()
        if result.success:
            self._update_status("Prompt sent successfully", result.message)
            QMessageBox.information(self, "Success", "Prompt sent successfully!")
        else:
            self._update_status("Failed to send prompt", result.message)
            QMessageBox.critical(
                self, "Error", f"Failed to send prompt: {result.message}"
            )

    @debug_button("_handle_regenerate_response_result", "Scraper Panel")
    def _handle_regenerate_response_result(self, result: ScrapingResult):
        """Handle regenerate response result."""
        self._enable_controls()
        if result.success:
            self._update_status("Response regenerated successfully", result.message)
            QMessageBox.information(
                self, "Success", "Response regenerated successfully!"
            )
        else:
            self._update_status("Failed to regenerate response", result.message)
            QMessageBox.critical(
                self, "Error", f"Failed to regenerate response: {result.message}"
            )

    @debug_button("_update_conversation_content", "Scraper Panel")
    def _update_conversation_content(self, conversation: dict):
        """Update the conversation content display."""
        # This would display the actual conversation content
        content = f"Conversation: {conversation.get('title', 'Unknown')}\n\n"
        content += f"Messages: {conversation.get('message_count', 0)}\n"
        content += f"Model: {conversation.get('model', 'Unknown')}\n"
        content += f"URL: {conversation.get('url', 'N/A')}\n\n"
        content += "Conversation content would be displayed here..."

        self.conversation_content.setPlainText(content)

    def _handle_thread_result(self, result_tuple):
        """Handle results from worker threads."""
        operation, result = result_tuple

        if operation == "login":
            self._handle_login_result(result)
        elif operation == "extract_conversations":
            self._handle_extract_conversations_result(result)
        elif operation == "extract_content":
            self._handle_extract_content_result(result)

    @debug_button("_handle_login_result", "Scraper Panel")
    def _handle_login_result(self, success, message):
        self.progress_bar.setVisible(False)
        self.status_label.setText(message)
        self._enable_controls()
        if not success:
            QMessageBox.critical(self, "Login Failed", message)
        else:
            QMessageBox.information(self, "Login Successful", message)

    def _handle_extract_conversations_result(self, result: ScrapingResult):
        """Handle extract conversations result."""
        self._enable_controls()
        if result.success:
            self._update_status("Conversations extracted successfully", result.message)
            self._update_results_table()
            QMessageBox.information(
                self, "Success", "Conversations extracted successfully!"
            )
        else:
            self._update_status("Failed to extract conversations", result.message)
            QMessageBox.critical(
                self, "Error", f"Failed to extract conversations: {result.message}"
            )

    def _handle_extract_content_result(self, result: ScrapingResult):
        """Handle extract content result."""
        self._enable_controls()
        if result.success:
            self._update_status("Content extracted successfully", result.message)
            self._update_results_table()
            QMessageBox.information(self, "Success", "Content extracted successfully!")
        else:
            self._update_status("Failed to extract content", result.message)
            QMessageBox.critical(
                self, "Error", f"Failed to extract content: {result.message}"
            )

    @debug_button("_update_results_table", "Scraper Panel")
    def _update_results_table(self):
        """Update the results table with conversation data."""
        self.results_table.setRowCount(len(self.conversations))

        for i, conv in enumerate(self.conversations):
            self.results_table.setItem(i, 0, QTableWidgetItem(conv.get("title", "")))
            self.results_table.setItem(
                i, 1, QTableWidgetItem(str(conv.get("message_count", 0)))
            )
            self.results_table.setItem(i, 2, QTableWidgetItem(conv.get("model", "")))
            self.results_table.setItem(i, 3, QTableWidgetItem(conv.get("status", "")))
            self.results_table.setItem(i, 4, QTableWidgetItem(conv.get("url", "")))

        # Update conversation list
        self.conv_list.clear()
        for conv in self.conversations:
            self.conv_list.addItem(conv.get("title", "Unknown"))

    @debug_button("_update_status", "Scraper Panel")
    def _update_status(self):
        """Create statistics grid using shared components."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        try:
            # Create statistics grid with panel-specific data
            stats_data = {
                "Total": 0,
                "Active": 0,
                "Completed": 0
            }
            
            stats_widget = components.create_statistics_grid(
                stats_data=stats_data,
                title="scraper_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _is_operation_running(self) -> bool:
        """Check if an operation is currently running."""
        return self.worker_thread is not None and self.worker_thread.is_alive()

    @debug_button("_check_prerequisites", "Scraper Panel")
    def _check_prerequisites(self) -> bool:
        """Check if prerequisites are met for operations."""
        return self.orchestrator is not None

    def _disable_controls(self):
        """Disable controls during operations."""
        self.login_button.setEnabled(False)
        self.cookie_login_button.setEnabled(False)
        self.extract_button.setEnabled(False)
        self.content_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.send_button.setEnabled(False)
        self.regenerate_button.setEnabled(False)

    def _enable_controls(self):
        """Enable controls after operations."""
        self.login_button.setEnabled(True)
        self.cookie_login_button.setEnabled(True)
        self.extract_button.setEnabled(True)
        self.content_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.send_button.setEnabled(True)
        self.regenerate_button.setEnabled(True)

    @debug_button("_login", "Scraper Panel")
    def _login(self):
        """Login with credentials using ScraperOrchestrator (refactored for standards compliance)."""
        if self._is_operation_running():
            return
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(
                self, "Warning", "Please enter both username and password."
            )
            return
        try:
            self._update_status(
                "Logging in...", "Attempting to login with credentials..."
            )
            self._disable_controls()
            # EDIT START: Use ScraperWorker for real login with progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Starting chat extraction...")
            self.worker = ScraperWorker(
                "credentials", username=username, password=password
            )
            self.worker.progress_updated.connect(self._update_progress)
            self.worker.login_completed.connect(self._handle_login_result)
            self.worker.start()
            # EDIT END
        except Exception as e:
            self._handle_login_result(False, str(e))

    @debug_button("_login_with_cookies", "Scraper Panel")
    def _login_with_cookies(self):
        """Login with cookies using ScraperOrchestrator (refactored for standards compliance)."""
        if self._is_operation_running():
            return
        cookie_file = self.cookie_file_edit.text().strip()
        if not cookie_file:
            QMessageBox.warning(self, "Warning", "Please enter a cookie file path.")
            return
        try:
            self._update_status("Logging in...", "Attempting to login with cookies...")
            self._disable_controls()
            # EDIT START: Use ScraperWorker for real cookie login with progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Starting chat extraction...")
            self.worker = ScraperWorker("cookies", cookie_file=cookie_file)
            self.worker.progress_updated.connect(self._update_progress)
            self.worker.login_completed.connect(self._handle_login_result)
            self.worker.start()
            # EDIT END
        except Exception as e:
            self._handle_login_result(False, str(e))

    @debug_button("_extract_conversations", "Scraper Panel")
    def _extract_conversations(self):
        """Extract conversation metadata."""
        if not self._check_prerequisites():
            QMessageBox.warning(self, "Warning", "Please login first.")
            return

        if self._is_operation_running():
            return

        try:
            max_conv = int(self.max_conv_edit.text())
        except ValueError:
            QMessageBox.warning(
                self, "Warning", "Please enter a valid number for max conversations."
            )
            return

        try:
            self._update_status(
                "Extracting conversations...",
                f"Extracting up to {max_conv} conversations...",
            )
            self._disable_controls()

            # Simulate extraction process
            QTimer.singleShot(
                3000,
                lambda: self._handle_extract_conversations_result(
                    ScrapingResult(
                        success=True, message=f"Extracted {max_conv} conversations"
                    )
                ),
            )

        except Exception as e:
            self._handle_extract_conversations_result(
                ScrapingResult(success=False, message=str(e))
            )

    @debug_button("_extract_content", "Scraper Panel")
    def _extract_content(self):
        """Extract conversation content."""
        if not self._check_prerequisites():
            QMessageBox.warning(self, "Warning", "Please login first.")
            return

        if self._is_operation_running():
            return

        try:
            self._update_status(
                "Extracting content...", "Extracting conversation content..."
            )
            self._disable_controls()

            # Simulate content extraction process
            QTimer.singleShot(
                5000,
                lambda: self._handle_extract_content_result(
                    ScrapingResult(
                        success=True, message="Content extracted successfully"
                    )
                ),
            )

        except Exception as e:
            self._handle_extract_content_result(
                ScrapingResult(success=False, message=str(e))
            )

    @debug_button("_save_results", "Scraper Panel")
    def _save_results(self):
        """Save scraped results."""
        if not self.conversations:
            QMessageBox.warning(self, "Warning", "No conversations to save.")
            return

        output_file = self.output_file_edit.text().strip()
        if not output_file:
            QMessageBox.warning(self, "Warning", "Please enter an output file path.")
            return

        try:
            # Save conversations to file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "Success", f"Results saved to {output_file}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save results: {str(e)}")

    def on_destroy(self):
        """Cleanup when panel is destroyed."""
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)

    # EDIT START: Update progress bar and status label
    @debug_button("_update_progress", "Scraper Panel")
    def _update_progress(self, current, total, message):
        self.progress_bar.setMaximum(max(total, 1))
        self.progress_bar.setValue(current)
        self.status_label.setText(message)

    # EDIT END
