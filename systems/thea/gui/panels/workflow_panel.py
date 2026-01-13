#!/usr/bin/env python3
"""
Workflow Panel for Thea GUI
===========================

Consolidates all command-line workflows into a single GUI tab:
- Unified Conversation Workflow
- Scraping and Processing
- Enhanced Templates
- Status Monitoring
- Batch Operations

This eliminates the need for multiple command-line scripts by providing
a comprehensive GUI interface for all workflow operations.
"""

import sys
from gui.debug_handler import debug_button
import os
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QTabWidget, QSpinBox,
    QCheckBox, QFormLayout, QScrollArea, QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QObject
from PyQt6.QtGui import QFont, QTextCursor

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from dreamscape.core.discord.manager import DiscordManager
from dreamscape.core.mmorpg.mmorpg_system import EnhancedProgressSystem
from dreamscape.core.scraping_system import ScraperOrchestrator
from dreamscape.core.template_engine import render_template

logger = logging.getLogger(__name__)

class WorkflowWorker(QObject):
    """Worker thread for running workflows."""
    
    # Signals
    progress_updated = pyqtSignal(str, int)  # message, percentage
    status_updated = pyqtSignal(str)  # status message
    workflow_completed = pyqtSignal(dict)  # results
    workflow_failed = pyqtSignal(str)  # error message
    
    def __init__(self, workflow_type: str, **kwargs):
        super().__init__()
        self.workflow_type = workflow_type
        self.kwargs = kwargs
        self.is_running = False
    
    def run(self):
        """Run the specified workflow."""
        try:
            self.is_running = True
            self.status_updated.emit(f"Starting {self.workflow_type} workflow...")
            
            if self.workflow_type == "unified_workflow":
                self._run_unified_workflow()
            elif self.workflow_type == "scrape_only":
                self._run_scrape_only()
            elif self.workflow_type == "process_only":
                self._run_process_only()
            elif self.workflow_type == "force_reprocess":
                self._run_force_reprocess()
            elif self.workflow_type == "test_templates":
                self._run_test_templates()
            elif self.workflow_type == "status_check":
                self._run_status_check()
            else:
                self.workflow_failed.emit(f"Unknown workflow type: {self.workflow_type}")
                
        except Exception as e:
            self.workflow_failed.emit(f"Workflow failed: {e}")
        finally:
            self.is_running = False
    
    def _run_unified_workflow(self):
        """Run the complete unified workflow."""
        try:
            from scripts.unified_conversation_workflow import UnifiedConversationWorkflow
            
            self.progress_updated.emit("Initializing workflow...", 10)
            workflow = UnifiedConversationWorkflow(
                headless=self.kwargs.get('headless', False),
                max_conversations=self.kwargs.get('max_conversations', 100)
            )
            
            self.progress_updated.emit("Running complete workflow...", 20)
            results = workflow.run_complete_workflow(
                scrape=self.kwargs.get('scrape', True),
                force_reingest=self.kwargs.get('force_reingest', False),
                force_reprocess=self.kwargs.get('force_reprocess', False)
            )
            
            self.progress_updated.emit("Workflow completed", 100)
            self.workflow_completed.emit(results)
            
        except Exception as e:
            self.workflow_failed.emit(f"Unified workflow failed: {e}")
    
    def _run_scrape_only(self):
        """Run scraping only workflow."""
        try:
            from scripts.unified_conversation_workflow import UnifiedConversationWorkflow
            
            self.progress_updated.emit("Initializing scraper...", 20)
            workflow = UnifiedConversationWorkflow(
                headless=self.kwargs.get('headless', False),
                max_conversations=self.kwargs.get('max_conversations', 100)
            )
            
            self.progress_updated.emit("Scraping conversations...", 50)
            scraped = workflow.scrape_conversations()
            
            if scraped:
                self.progress_updated.emit("Ingesting conversations...", 80)
                results = workflow.ingest_conversations(scraped)
                self.progress_updated.emit("Scraping completed", 100)
                self.workflow_completed.emit({
                    "success": True,
                    "conversations_scraped": len(scraped),
                    "new_conversations": results.get('new_conversations', 0)
                })
            else:
                self.workflow_failed.emit("No conversations scraped")
                
        except Exception as e:
            self.workflow_failed.emit(f"Scraping failed: {e}")
    
    @debug_button("_run_process_only", "Workflow Panel")
    def _run_process_only(self):
        """Run processing only workflow."""
        try:
            from scripts.unified_conversation_workflow import UnifiedConversationWorkflow
            
            self.progress_updated.emit("Initializing processor...", 20)
            workflow = UnifiedConversationWorkflow()
            
            self.progress_updated.emit("Processing conversations...", 60)
            results = workflow.process_all_conversations(force_reprocess=False)
            
            self.progress_updated.emit("Processing completed", 100)
            self.workflow_completed.emit(results)
            
        except Exception as e:
            self.workflow_failed.emit(f"Processing failed: {e}")
    
    @debug_button("_run_force_reprocess", "Workflow Panel")
    def _run_force_reprocess(self):
        """Run force reprocess workflow."""
        try:
            from scripts.unified_conversation_workflow import UnifiedConversationWorkflow
            
            self.progress_updated.emit("Initializing processor...", 20)
            workflow = UnifiedConversationWorkflow()
            
            self.progress_updated.emit("Force re-processing conversations...", 60)
            results = workflow.process_all_conversations(force_reprocess=True)
            
            self.progress_updated.emit("Re-processing completed", 100)
            self.workflow_completed.emit(results)
            
        except Exception as e:
            self.workflow_failed.emit(f"Re-processing failed: {e}")
    
    @debug_button("_run_test_templates", "Workflow Panel")
    def _run_test_templates(self):
        """Run enhanced template tests."""
        try:
            from scripts.test_enhanced_templates import EnhancedTemplateTester
            
            self.progress_updated.emit("Testing enhanced templates...", 50)
            tester = EnhancedTemplateTester()
            results = tester.run_enhanced_template_tests()
            
            self.progress_updated.emit("Template tests completed", 100)
            self.workflow_completed.emit(results)
            
        except Exception as e:
            self.workflow_failed.emit(f"Template tests failed: {e}")
    
    @debug_button("_run_status_check", "Workflow Panel")
    def _run_status(self):
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
                title="workflow_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

class WorkflowPanel(QWidget):
    """Main panel for managing and running workflows."""
    
    # Signals
    workflow_completed = pyqtSignal(dict)  # results
    workflow_failed = pyqtSignal(str)  # error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_thread = None
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🔄 Unified Workflow Management")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Manage all conversation workflows from a single interface. No more command-line scripts needed!")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_unified_workflow_tab(), "🚀 Unified Workflow")
        self.tab_widget.addTab(self.create_scraping_tab(), "📥 Scraping")
        self.tab_widget.addTab(self.create_processing_tab(), "🔄 Processing")
        self.tab_widget.addTab(self.create_templates_tab(), "📝 Templates")
        self.tab_widget.addTab(self.create_status_tab(), "📊 Status")
        self.tab_widget.addTab(self.create_batch_tab(), "⚡ Batch Operations")
        
        # Progress section
        self.create_progress_section(layout)
    
    @debug_button("create_unified_workflow_tab", "Workflow Panel")
    def create_unified_workflow_tab(self) -> QWidget:
        """Create the unified workflow tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Run the complete workflow: scrape conversations, ingest them, and process with enhanced templates.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Configuration group
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout(config_group)
        
        # Max conversations
        self.max_conversations_spin = QSpinBox()
        self.max_conversations_spin.setRange(1, 1000)
        self.max_conversations_spin.setValue(100)
        config_layout.addRow("Max Conversations:", self.max_conversations_spin)
        
        # Headless mode
        self.headless_checkbox = QCheckBox("Run browser in headless mode")
        config_layout.addRow("", self.headless_checkbox)
        
        # Force options
        self.force_reingest_checkbox = QCheckBox("Force re-ingestion")
        config_layout.addRow("", self.force_reingest_checkbox)
        
        self.force_reprocess_checkbox = QCheckBox("Force re-processing")
        config_layout.addRow("", self.force_reprocess_checkbox)
        
        layout.addWidget(config_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.run_unified_btn = QPushButton("🚀 Run Complete Workflow")
        self.run_unified_btn.clicked.connect(self.run_unified_workflow)
        button_layout.addWidget(self.run_unified_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    @debug_button("create_scraping_tab", "Workflow Panel")
    def create_scraping_tab(self) -> QWidget:
        """Create the scraping tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Scrape new conversations from ChatGPT and ingest them into the system.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Configuration
        config_group = QGroupBox("Scraping Configuration")
        config_layout = QFormLayout(config_group)
        
        self.scrape_max_conv_spin = QSpinBox()
        self.scrape_max_conv_spin.setRange(1, 1000)
        self.scrape_max_conv_spin.setValue(100)
        config_layout.addRow("Max Conversations:", self.scrape_max_conv_spin)
        
        self.scrape_headless_checkbox = QCheckBox("Run browser in headless mode")
        config_layout.addRow("", self.scrape_headless_checkbox)
        
        layout.addWidget(config_group)
        
        # Action button
        self.run_scrape_btn = QPushButton("📥 Scrape Conversations")
        self.run_scrape_btn.clicked.connect(self.run_scrape_only)
        layout.addWidget(self.run_scrape_btn)
        
        layout.addStretch()
        return widget
    
    @debug_button("create_processing_tab", "Workflow Panel")
    def create_processing_tab(self) -> QWidget:
        """Create the processing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Process existing conversations with enhanced templates and update MMORPG progress.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout(options_group)
        
        self.force_reprocess_checkbox = QCheckBox("Force re-processing (ignore already processed)")
        options_layout.addWidget(self.force_reprocess_checkbox)
        
        layout.addWidget(options_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.run_process_btn = QPushButton("🔄 Process Conversations")
        self.run_process_btn.clicked.connect(self.run_process_only)
        button_layout.addWidget(self.run_process_btn)
        
        self.run_force_btn = QPushButton("⚡ Force Re-process")
        self.run_force_btn.clicked.connect(self.run_force_reprocess)
        button_layout.addWidget(self.run_force_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    @debug_button("create_templates_tab", "Workflow Panel")
    def create_templates_tab(self) -> QWidget:
        """Create the templates tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Test and validate enhanced templates with human-AI workflow context.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Template info
        info_group = QGroupBox("Enhanced Templates")
        info_layout = QVBoxLayout(info_group)
        
        templates_info = QTextBrowser()
        templates_info.setHtml("""
        <h3>Available Enhanced Templates:</h3>
        <ul>
            <li><b>Enhanced Conversation Analyzer</b> - Deep analysis with work patterns</li>
            <li><b>Enhanced Devlog Generator</b> - Context-aware devlog creation</li>
            <li><b>Enhanced Action Planner</b> - Strategic action planning</li>
            <li><b>Dreamscape Narrative</b> - MMORPG story generation</li>
            <li><b>Code Review</b> - Technical code analysis</li>
        </ul>
        <p>These templates leverage human-AI workflow context for deeper insights.</p>
        """)
        info_layout.addWidget(templates_info)
        
        layout.addWidget(info_group)
        
        # Action button
        self.test_templates_btn = QPushButton("🧪 Test Enhanced Templates")
        self.test_templates_btn.clicked.connect(self.run_test_templates)
        layout.addWidget(self.test_templates_btn)
        
        layout.addStretch()
        return widget
    
    @debug_button("create_status_tab", "Workflow Panel")
    def create_status_tab(self):
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
                title="workflow_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    @debug_button("create_batch_tab", "Workflow Panel")
    def create_batch_tab(self) -> QWidget:
        """Create the batch operations tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Description
        desc = QLabel("Quick batch operations for common workflows.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Batch operations
        batch_group = QGroupBox("Batch Operations")
        batch_layout = QVBoxLayout(batch_group)
        
        # Quick scrape and process
        self.quick_workflow_btn = QPushButton("⚡ Quick Workflow (Scrape + Process)")
        self.quick_workflow_btn.clicked.connect(self.run_quick_workflow)
        batch_layout.addWidget(self.quick_workflow_btn)
        
        # Process all unprocessed
        self.process_unprocessed_btn = QPushButton("🔄 Process All Unprocessed")
        self.process_unprocessed_btn.clicked.connect(self.run_process_unprocessed)
        batch_layout.addWidget(self.process_unprocessed_btn)
        
        # Force reprocess all
        self.force_all_btn = QPushButton("⚡ Force Re-process All")
        self.force_all_btn.clicked.connect(self.run_force_all)
        batch_layout.addWidget(self.force_all_btn)
        
        layout.addWidget(batch_group)
        layout.addStretch()
        
        return widget
    
    @debug_button("create_progress_section", "Workflow Panel")
    def create_progress_section(self, parent_layout):
        """Create the progress section."""
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        parent_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to run workflows")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self.status_label)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setMaximumHeight(200)
        self.log_display.setReadOnly(True)
        parent_layout.addWidget(self.log_display)
    
    def log_message(self, message: str):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
    
    @debug_button("start_workflow", "Workflow Panel")
    def start_workflow(self, workflow_type: str, **kwargs):
        """Start a workflow in a separate thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Workflow Running", "Another workflow is already running. Please wait for it to complete.")
            return
        
        # Create worker and thread
        self.worker = WorkflowWorker(workflow_type, **kwargs)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.status_updated.connect(self.update_status)
        self.worker.workflow_completed.connect(self.workflow_completed)
        self.worker.workflow_failed.connect(self.workflow_failed)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.finished.connect(self.workflow_finished)
        
        # Start workflow
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_message(f"Starting {workflow_type} workflow...")
        self.worker_thread.start()
    
    @debug_button("update_progress", "Workflow Panel")
    def update_progress(self, message: str, percentage: int):
        """Update progress bar and log."""
        self.progress_bar.setValue(percentage)
        self.log_message(message)
    
    @debug_button("update_status", "Workflow Panel")
    def update_status(self):
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
                title="workflow_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    @debug_button("workflow_completed", "Workflow Panel")
    def workflow_completed(self, results: dict):
        """Handle workflow completion."""
        self.log_message("Workflow completed successfully!")
        
        # Display results
        if "conversations_scraped" in results:
            self.log_message(f"Conversations scraped: {results['conversations_scraped']}")
        if "new_conversations" in results:
            self.log_message(f"New conversations: {results['new_conversations']}")
        if "processed_conversations" in results:
            self.log_message(f"Conversations processed: {results['processed_conversations']}")
        
        QMessageBox.information(self, "Workflow Complete", "Workflow completed successfully!")
    
    @debug_button("workflow_failed", "Workflow Panel")
    def workflow_failed(self, error: str):
        """Handle workflow failure."""
        self.log_message(f"Workflow failed: {error}")
        QMessageBox.critical(self, "Workflow Failed", f"Workflow failed: {error}")
    
    @debug_button("workflow_finished", "Workflow Panel")
    def workflow_finished(self):
        """Handle workflow thread completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready to run workflows")
        
        # Clean up
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
        self.worker = None
    
    # Workflow action methods
    @debug_button("run_unified_workflow", "Workflow Panel")
    def run_unified_workflow(self):
        """Run the complete unified workflow."""
        kwargs = {
            'headless': self.headless_checkbox.isChecked(),
            'max_conversations': self.max_conversations_spin.value(),
            'scrape': True,
            'force_reingest': self.force_reingest_checkbox.isChecked(),
            'force_reprocess': self.force_reprocess_checkbox.isChecked()
        }
        self.start_workflow("unified_workflow", **kwargs)
    
    @debug_button("run_scrape_only", "Workflow Panel")
    def run_scrape_only(self):
        """Run scraping only workflow."""
        kwargs = {
            'headless': self.scrape_headless_checkbox.isChecked(),
            'max_conversations': self.scrape_max_conv_spin.value()
        }
        self.start_workflow("scrape_only", **kwargs)
    
    @debug_button("run_process_only", "Workflow Panel")
    def run_process_only(self):
        """Run processing only workflow."""
        self.start_workflow("process_only")
    
    @debug_button("run_force_reprocess", "Workflow Panel")
    def run_force_reprocess(self):
        """Run force reprocess workflow."""
        self.start_workflow("force_reprocess")
    
    @debug_button("run_test_templates", "Workflow Panel")
    def run_test_templates(self):
        """Run enhanced template tests."""
        self.start_workflow("test_templates")
    
    @debug_button("run_status_check", "Workflow Panel")
    def run_status(self):
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
                title="workflow_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    @debug_button("run_quick_workflow", "Workflow Panel")
    def run_quick_workflow(self):
        """Run quick workflow (scrape + process)."""
        kwargs = {
            'headless': True,
            'max_conversations': 50,
            'scrape': True,
            'force_reingest': False,
            'force_reprocess': False
        }
        self.start_workflow("unified_workflow", **kwargs)
    
    @debug_button("run_process_unprocessed", "Workflow Panel")
    def run_process_unprocessed(self):
        """Run processing for unprocessed conversations."""
        self.start_workflow("process_only")
    
    @debug_button("run_force_all", "Workflow Panel")
    def run_force_all(self):
        """Run force reprocess for all conversations."""
        self.start_workflow("force_reprocess") 