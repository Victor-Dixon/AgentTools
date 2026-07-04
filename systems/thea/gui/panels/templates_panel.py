"""
Templates Panel for Thea GUI
Manages prompt templates and template operations.
"""

import logging
from gui.debug_handler import debug_button
from gui.components.unified_export_center import UnifiedExportCenter

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QLineEdit,
    QSplitter,
    QMessageBox,
    QInputDialog,
    QFileDialog,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict, Any
import os
import glob
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class TemplatesPanel(QWidget):
    """Panel for managing prompt templates."""

    # Signals
    template_selected = pyqtSignal(dict)
    template_saved = pyqtSignal(dict)
    template_deleted = pyqtSignal(str)
    template_applied = pyqtSignal(dict)  # EDIT: Signal for applying a template

    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates = []
        self.current_template = None
        self.templates_dir = Path("templates")
        self.init_ui()
        # Load templates on startup
        self.load_templates_from_disk()

    def init_ui(self):
        """Initialize the templates UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        self.create_header()

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left side - template list
        self.create_template_list(splitter)

        # Right side - template editor
        self.create_template_editor(splitter)

        # Set splitter proportions
        splitter.setSizes([300, 700])

    def showEvent(self, event):
        """Called when the panel becomes visible (tab switch)."""
        super().showEvent(event)
        # Reload templates when tab is activated
        self.load_templates_from_disk()

    @debug_button("load_templates_from_disk", "Templates Panel")
    def load_templates_from_disk(self):
        """Load all .j2 and .txt templates from the templates directory."""
        if not self.templates_dir.exists():
            print(f"Templates directory not found: {self.templates_dir}")
            return

        templates = []

        # Find all .j2 and .txt files recursively, excluding archive directory
        for pattern in ["**/*.j2", "**/*.txt"]:
            for file_path in self.templates_dir.glob(pattern):
                # Skip archive directory
                if "archive" in file_path.parts:
                    continue

                try:
                    # Read file content
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Create template object
                    template = {
                        "name": file_path.stem,  # filename without extension
                        "content": content,
                        "file_path": str(file_path),
                        "category": self._get_template_category(file_path),
                        "created_at": self._get_file_timestamp(file_path),
                        "updated_at": self._get_file_timestamp(file_path),
                    }

                    templates.append(template)

                except Exception as e:
                    print(f"Error loading template {file_path}: {e}")

        # Sort templates by category and name
        templates.sort(key=lambda x: (x["category"], x["name"]))

        # Load into the panel
        self.load_templates(templates)

        print(f"Loaded {len(templates)} templates from disk")

    def _get_template_category(self, file_path: Path) -> str:
        """Determine template category based on file path."""
        relative_path = file_path.relative_to(self.templates_dir)

        if relative_path.parts[0] == "prompts":
            return "Prompts"
        elif relative_path.parts[0] == "dreamscape":
            return "Dreamscape"
        else:
            return "General"

    def _get_file_timestamp(self, file_path: Path) -> str:
        """Get file modification timestamp."""
        try:
            stat = file_path.stat()
            return str(stat.st_mtime)
        except:
            return self._get_current_timestamp()

    @debug_button("create_header", "Templates Panel")
    def create_header(self):
        """Create panel header using shared components with unified load button."""
        try:
            from gui.components.shared_components import SharedComponents
            from gui.components.unified_load_button import UnifiedLoadButton
            
            components = SharedComponents()
            
            # Create header with title and icon
            header_widget = components.create_panel_header(
                title="Templates",
                icon="📋"
            )
            
            # Add unified load button
            self.unified_load_btn = UnifiedLoadButton(
                data_type="templates",
                text="Load Templates",
                priority="NORMAL"
            )
            
            # Connect signals
            self.unified_load_btn.load_completed.connect(self.on_templates_loaded)
            
            # Add the load button to the header layout
            if hasattr(header_widget, 'layout'):
                header_widget.layout().addWidget(self.unified_load_btn)
            
            return header_widget
            
        except Exception as e:
            logger.error(f"Error creating panel header: {e}")
            return QWidget()  # Fallback widget
    
    def on_templates_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle templates load completion."""
        if success and data_type == "templates":
            # Refresh the templates display
            self.load_templates_from_disk()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load templates: {message}")

    @debug_button("create_template_list", "Templates Panel")
    def create_template_list(self, parent):
        """Create the template list widget."""
        # Container widget
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.template_list.itemSelectionChanged.connect(self.on_template_selected)
        list_layout.addWidget(self.template_list)
        
        # Status label
        self.template_status_label = QLabel("No templates loaded")
        self.template_status_label.setStyleSheet("color: #666; font-style: italic;")
        list_layout.addWidget(self.template_status_label)
        
        parent.addWidget(list_widget)

    @debug_button("create_template_editor", "Templates Panel")
    def create_template_editor(self, parent):
        """Create the template editor widget."""
        # Container widget
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # Editor header
        editor_header = QHBoxLayout()
        
        self.editor_title = QLabel("Select a template to edit")
        self.editor_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        editor_header.addWidget(self.editor_title)
        
        editor_header.addStretch()
        
        # Export button
        self.template_export_btn = QPushButton("🚀 Export Center")
        self.template_export_btn.setEnabled(False)
        self.template_export_btn.clicked.connect(self.show_export_center)
        self.template_export_btn.setToolTip("Open Unified Export Center")
        editor_header.addWidget(self.template_export_btn)
        
        editor_layout.addLayout(editor_header)
        
        # Template content editor
        self.template_editor = QTextEdit()
        self.template_editor.setPlaceholderText("Select a template to edit its content...")
        self.template_editor.setFont(QFont("Consolas", 10))
        editor_layout.addWidget(self.template_editor)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_template)
        action_layout.addWidget(self.save_btn)
        
        self.apply_btn = QPushButton("✨ Apply")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.apply_template)
        action_layout.addWidget(self.apply_btn)
        
        action_layout.addStretch()
        
        editor_layout.addLayout(action_layout)
        
        parent.addWidget(editor_widget)

    def load_templates(self, templates: List[Dict]):
        """Load templates into the list widget."""
        self.templates = templates
        self.template_list.clear()
        
        for template in templates:
            item = QListWidgetItem(f"{template['category']} - {template['name']}")
            item.setData(Qt.ItemDataRole.UserRole, template)
            self.template_list.addItem(item)
        
        # Update status
        self.template_status_label.setText(f"Loaded {len(templates)} templates")
        
        # Enable export button if templates exist
        self.template_export_btn.setEnabled(len(templates) > 0)

    def on_template_selected(self):
        """Handle template selection."""
        current_item = self.template_list.currentItem()
        if current_item:
            template = current_item.data(Qt.ItemDataRole.UserRole)
            self.current_template = template
            self.view_template(template)
        else:
            self.clear_editor()

    def view_template(self, template: Dict):
        """View a template in the editor."""
        self.editor_title.setText(f"Editing: {template['name']}")
        self.template_editor.setPlainText(template['content'])
        self.save_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        self.template_export_btn.setEnabled(True)

    def clear_editor(self):
        """Clear the template editor."""
        self.editor_title.setText("Select a template to edit")
        self.template_editor.clear()
        self.save_btn.setEnabled(False)
        self.apply_btn.setEnabled(False)
        self.template_export_btn.setEnabled(False)
        self.current_template = None

    def save_template(self):
        """Save the current template."""
        if not self.current_template:
            return
        
        try:
            content = self.template_editor.toPlainText()
            file_path = Path(self.current_template['file_path'])
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update the template object
            self.current_template['content'] = content
            self.current_template['updated_at'] = self._get_current_timestamp()
            
            QMessageBox.information(self, "Success", f"Template '{self.current_template['name']}' saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save template: {e}")

    def apply_template(self):
        """Apply the current template."""
        if not self.current_template:
            return
        
        # Emit signal for template application
        self.template_applied.emit(self.current_template)
        QMessageBox.information(self, "Success", f"Template '{self.current_template['name']}' applied!")

    def show_export_center(self):
        """Show the unified export center."""
        try:
            from gui.main_window import TheaMainWindow
            main_window = self.window()
            if hasattr(main_window, 'show_export_center'):
                main_window.show_export_center()
            else:
                QMessageBox.warning(self, "Export Center", "Export center not available")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open export center: {e}")

    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return str(datetime.now().timestamp())
