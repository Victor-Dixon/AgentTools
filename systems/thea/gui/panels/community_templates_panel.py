#!/usr/bin/env python3
"""
Community Templates Panel for Dreamscape GUI
============================================

Provides a comprehensive interface for community template sharing and discovery.
Features:
- Template marketplace browsing
- Template creation and editing
- Rating and review system
- Search and filtering
- Community interaction
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
    QHeaderView, QAbstractItemView, QSlider, QDoubleSpinBox,
    QTextBrowser, QDialog, QDialogButtonBox, QVBoxLayout as QVBoxLayoutDialog
)
from gui.components.shared_components import SharedComponents
from gui.components.data_loader import DataLoader
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap

from dreamscape.core.community_template_system import (
    CommunityTemplateSystem, CommunityTemplate, TemplateReview, TemplateCategory
)

logger = logging.getLogger(__name__)

class TemplateCreationDialog(QDialog):
    """Dialog for creating new community templates."""
    
    def __init__(self, parent=None, template=None):
        super().__init__(parent)
        self.template = template
        self.is_edit_mode = template is not None
        
        self.setWindowTitle("Edit Template" if self.is_edit_mode else "Create New Template")
        self.setModal(True)
        self.resize(800, 600)
        
        self.init_ui()
        if self.is_edit_mode:
            self.load_template_data()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayoutDialog(self)
        
        # Template details
        details_group = QGroupBox("Template Details")
        details_layout = QFormLayout(details_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter template name...")
        details_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Enter template description...")
        details_layout.addRow("Description:", self.description_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "general", "conversation", "analysis", "creative", "technical",
            "business", "education", "social", "mmorpg", "ai"
        ])
        details_layout.addRow("Category:", self.category_combo)
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["beginner", "intermediate", "advanced"])
        details_layout.addRow("Difficulty:", self.difficulty_combo)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter tags separated by commas...")
        details_layout.addRow("Tags:", self.tags_edit)
        
        self.is_public_cb = QCheckBox("Make template public")
        self.is_public_cb.setChecked(True)
        details_layout.addRow("", self.is_public_cb)
        
        layout.addWidget(details_group)
        
        # Template content
        content_group = QGroupBox("Template Content")
        content_layout = QVBoxLayout(content_group)
        
        content_help = QLabel("Use Jinja2 syntax for variables: {{ variable_name }}")
        content_help.setStyleSheet("color: #666; font-style: italic;")
        content_layout.addWidget(content_help)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Enter your template content here...")
        content_layout.addWidget(self.content_edit)
        
        layout.addWidget(content_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    @debug_button("load_template_data", "Community Templates Panel")
    def load_template_data(self):
        """Load existing template data for editing."""
        if not self.template:
            return
        
        self.name_edit.setText(self.template.name)
        self.description_edit.setPlainText(self.template.description)
        self.category_combo.setCurrentText(self.template.category)
        self.difficulty_combo.setCurrentText(self.template.difficulty_level)
        self.tags_edit.setText(", ".join(self.template.tags))
        self.content_edit.setPlainText(self.template.content)
        self.is_public_cb.setChecked(self.template.is_public)
    
    def get_template_data(self) -> Dict[str, Any]:
        """Get template data from the dialog."""
        tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]
        
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'content': self.content_edit.toPlainText().strip(),
            'category': self.category_combo.currentText(),
            'difficulty_level': self.difficulty_combo.currentText(),
            'tags': tags,
            'is_public': self.is_public_cb.isChecked()
        }

class ReviewDialog(QDialog):
    """Dialog for rating and reviewing templates."""
    
    def __init__(self, template_name: str, parent=None):
        super().__init__(parent)
        self.template_name = template_name
        
        self.setWindowTitle(f"Rate & Review: {template_name}")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayoutDialog(self)
        
        # Rating
        rating_group = QGroupBox("Rating")
        rating_layout = QVBoxLayout(rating_group)
        
        self.rating_slider = QSlider(Qt.Orientation.Horizontal)
        self.rating_slider.setRange(1, 5)
        self.rating_slider.setValue(5)
        self.rating_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rating_slider.setTickInterval(1)
        rating_layout.addWidget(self.rating_slider)
        
        self.rating_label = QLabel("5 stars")
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rating_layout.addWidget(self.rating_label)
        
        self.rating_slider.valueChanged.connect(self.update_rating_label)
        layout.addWidget(rating_group)
        
        # Review
        review_group = QGroupBox("Review (Optional)")
        review_layout = QVBoxLayout(review_group)
        
        self.review_edit = QTextEdit()
        self.review_edit.setPlaceholderText("Share your thoughts about this template...")
        self.review_edit.setMaximumHeight(150)
        review_layout.addWidget(self.review_edit)
        
        layout.addWidget(review_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    @debug_button("update_rating_label", "Community Templates Panel")
    def update_rating_label(self, value: int):
        """Update the rating label."""
        self.rating_label.setText(f"{value} star{'s' if value != 1 else ''}")
    
    def get_review_data(self) -> Dict[str, Any]:
        """Get review data from the dialog."""
        return {
            'rating': self.rating_slider.value(),
            'review_text': self.review_edit.toPlainText().strip()
        }

class CommunityTemplatesPanel(QWidget):
    """Comprehensive community templates panel for Dreamscape GUI."""
    
    # Signals
    template_created = pyqtSignal(str)  # template_id
    template_updated = pyqtSignal(str)  # template_id
    template_downloaded = pyqtSignal(str)  # template_id
    
    def __init__(self, user_id: str = "default_user", user_name: str = "User"):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.community_system = CommunityTemplateSystem()
        # Data loader for caching operations
        self.data_loader = DataLoader()
        
        # UI state
        self.current_template = None
        self.current_category = None
        
        self.init_ui()
        self.load_templates()
        self.load_categories()
    
    def init_ui(self):
        """Initialize the community templates user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("🌐 Community Templates & Prompts")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Discover, create, and share custom templates with the community.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_marketplace_tab(), "🏪 Marketplace")
        self.tab_widget.addTab(self.create_my_templates_tab(), "📝 My Templates")
        self.tab_widget.addTab(self.create_create_tab(), "✨ Create Template")
        self.tab_widget.addTab(self.create_stats_tab(), "📊 Community Stats")
        
        # Status section
        self.create_status_section(layout)
        
        # Connect signals
        self.connect_signals()
    
    @debug_button("create_marketplace_tab", "Community Templates Panel")
    def create_marketplace_tab(self) -> QWidget:
        """Create the template marketplace tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Template Marketplace")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Search and filter controls
        controls_group = QGroupBox("Search & Filter")
        controls_layout = QGridLayout(controls_group)
        
        # Search
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search templates...")
        self.search_edit.textChanged.connect(self.search_templates)
        controls_layout.addWidget(QLabel("Search:"), 0, 0)
        controls_layout.addWidget(self.search_edit, 0, 1)
        
        # Category filter
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("All Categories")
        self.category_filter_combo.currentTextChanged.connect(self.filter_by_category)
        controls_layout.addWidget(QLabel("Category:"), 0, 2)
        controls_layout.addWidget(self.category_filter_combo, 0, 3)
        
        # Sort options
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Newest", "Most Popular", "Highest Rated", "Most Downloaded", "Name"
        ])
        self.sort_combo.currentTextChanged.connect(self.sort_templates)
        controls_layout.addWidget(QLabel("Sort by:"), 1, 0)
        controls_layout.addWidget(self.sort_combo, 1, 1)
        
        # Difficulty filter
        self.difficulty_filter_combo = QComboBox()
        self.difficulty_filter_combo.addItems(["All Levels", "Beginner", "Intermediate", "Advanced"])
        self.difficulty_filter_combo.currentTextChanged.connect(self.filter_by_difficulty)
        controls_layout.addWidget(QLabel("Difficulty:"), 1, 2)
        controls_layout.addWidget(self.difficulty_filter_combo, 1, 3)
        
        layout.addWidget(controls_group)
        
        # Template list
        list_group = QGroupBox("Templates")
        list_layout = QVBoxLayout(list_group)
        
        # Template table
        self.templates_table = QTableWidget()
        self.templates_table.setColumnCount(7)
        self.templates_table.setHorizontalHeaderLabels([
            "Name", "Author", "Category", "Rating", "Downloads", "Updated", "Actions"
        ])
        
        # Configure table
        header = self.templates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.templates_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.templates_table.itemSelectionChanged.connect(self.on_template_selected)
        
        list_layout.addWidget(self.templates_table)
        
        # Template actions
        actions_layout = QHBoxLayout()
        
        components = SharedComponents()
        self.refresh_btn = components.create_refresh_button(
            callback=lambda: self.load_templates(force_reload=True)
        )
        actions_layout.addWidget(self.refresh_btn)
        
        self.download_btn = QPushButton("📥 Download")
        self.download_btn.clicked.connect(self.download_selected_template)
        self.download_btn.setEnabled(False)
        actions_layout.addWidget(self.download_btn)
        
        self.rate_btn = QPushButton("⭐ Rate")
        self.rate_btn.clicked.connect(self.rate_selected_template)
        self.rate_btn.setEnabled(False)
        actions_layout.addWidget(self.rate_btn)
        
        self.fork_btn = QPushButton("🍴 Fork")
        self.fork_btn.clicked.connect(self.fork_selected_template)
        self.fork_btn.setEnabled(False)
        actions_layout.addWidget(self.fork_btn)
        
        actions_layout.addStretch()
        list_layout.addLayout(actions_layout)
        
        layout.addWidget(list_group)
        
        # Template details
        details_group = QGroupBox("Template Details")
        details_layout = QVBoxLayout(details_group)
        
        self.template_details = QTextBrowser()
        self.template_details.setMaximumHeight(200)
        self.template_details.setPlaceholderText("Select a template to view details...")
        details_layout.addWidget(self.template_details)
        
        layout.addWidget(details_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_my_templates_tab", "Community Templates Panel")
    def create_my_templates_tab(self) -> QWidget:
        """Create the my templates tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("My Templates")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # My templates list
        list_group = QGroupBox("My Templates")
        list_layout = QVBoxLayout(list_group)
        
        self.my_templates_list = QListWidget()
        self.my_templates_list.itemSelectionChanged.connect(self.on_my_template_selected)
        list_layout.addWidget(self.my_templates_list)
        
        # My template actions
        my_actions_layout = QHBoxLayout()
        
        self.refresh_my_btn = components.create_refresh_button(
            callback=lambda: self.load_my_templates(force_reload=True)
        )
        my_actions_layout.addWidget(self.refresh_my_btn)
        
        self.edit_my_btn = QPushButton("✏️ Edit")
        self.edit_my_btn.clicked.connect(self.edit_my_template)
        self.edit_my_btn.setEnabled(False)
        my_actions_layout.addWidget(self.edit_my_btn)
        
        self.delete_my_btn = QPushButton("🗑️ Delete")
        self.delete_my_btn.clicked.connect(self.delete_my_template)
        self.delete_my_btn.setEnabled(False)
        my_actions_layout.addWidget(self.delete_my_btn)
        
        my_actions_layout.addStretch()
        list_layout.addLayout(my_actions_layout)
        
        layout.addWidget(list_group)
        
        # My template details
        my_details_group = QGroupBox("Template Details")
        my_details_layout = QVBoxLayout(my_details_group)
        
        self.my_template_details = QTextBrowser()
        self.my_template_details.setMaximumHeight(300)
        self.my_template_details.setPlaceholderText("Select a template to view details...")
        my_details_layout.addWidget(self.my_template_details)
        
        layout.addWidget(my_details_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_create_tab", "Community Templates Panel")
    def create_create_tab(self) -> QWidget:
        """Create the template creation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Create New Template")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Create button
        create_group = QGroupBox("Template Creation")
        create_layout = QVBoxLayout(create_group)
        
        create_info = QLabel("Click the button below to create a new community template.")
        create_layout.addWidget(create_info)
        
        self.create_template_btn = QPushButton("✨ Create New Template")
        self.create_template_btn.clicked.connect(self.create_new_template)
        self.create_template_btn.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; }")
        create_layout.addWidget(self.create_template_btn)
        
        layout.addWidget(create_group)
        
        # Template guidelines
        guidelines_group = QGroupBox("Template Guidelines")
        guidelines_layout = QVBoxLayout(guidelines_group)
        
        guidelines_text = QTextBrowser()
        guidelines_text.setHtml("""
        <h3>Creating Great Templates</h3>
        <ul>
        <li><b>Clear Purpose:</b> Make sure your template has a specific, useful purpose</li>
        <li><b>Good Documentation:</b> Provide clear descriptions and usage instructions</li>
        <li><b>Variable Usage:</b> Use Jinja2 syntax for variables: {{ variable_name }}</li>
        <li><b>Appropriate Tags:</b> Add relevant tags to help others find your template</li>
        <li><b>Test Your Template:</b> Make sure it works before sharing</li>
        </ul>
        
        <h3>Jinja2 Variable Examples</h3>
        <ul>
        <li><code>{{ user_name }}</code> - Simple variable</li>
        <li><code>{{ conversation_content }}</code> - Content variable</li>
        <li><code>{% for item in items %}{{ item }}{% endfor %}</code> - Loop</li>
        <li><code>{% if condition %}content{% endif %}</code> - Conditional</li>
        </ul>
        """)
        guidelines_layout.addWidget(guidelines_text)
        
        layout.addWidget(guidelines_group)
        layout.addStretch()
        
        return tab
    
    @debug_button("create_stats_tab", "Community Templates Panel")
    def create_stats(self):
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
                title="community_templates_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def create_status(self):
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
                title="community_templates_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def connect_signals(self):
        """Connect UI signals."""
        # Template selection
        self.templates_table.itemSelectionChanged.connect(self.on_template_selected)
        self.my_templates_list.itemSelectionChanged.connect(self.on_my_template_selected)

    @debug_button("load_templates", "Community Templates Panel")
    def load_templates(self, force_reload: bool = False):
        """Load and display templates using DataLoader."""
        try:
            templates = self.data_loader.load(
                "public_templates",
                lambda: self.community_system.list_templates(is_public=True),
                force_reload,
            )
            self.update_templates_table(templates)
            self.status_label.setText(f"Loaded {len(templates)} templates")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            self.status_label.setText(f"Error loading templates: {e}")
    
    @debug_button("update_templates_table", "Community Templates Panel")
    def update_templates_table(self, templates: List[CommunityTemplate]):
        """Update the templates table."""
        self.templates_table.setRowCount(len(templates))
        
        for row, template in enumerate(templates):
            # Name
            name_item = QTableWidgetItem(template.name)
            name_item.setData(Qt.ItemDataRole.UserRole, template.id)
            self.templates_table.setItem(row, 0, name_item)
            
            # Author
            author_item = QTableWidgetItem(template.author_name)
            self.templates_table.setItem(row, 1, author_item)
            
            # Category
            category_item = QTableWidgetItem(template.category)
            self.templates_table.setItem(row, 2, category_item)
            
            # Rating
            rating_text = f"{template.average_rating:.1f} ({template.rating_count})"
            rating_item = QTableWidgetItem(rating_text)
            self.templates_table.setItem(row, 3, rating_item)
            
            # Downloads
            download_item = QTableWidgetItem(str(template.download_count))
            self.templates_table.setItem(row, 4, download_item)
            
            # Updated
            updated_text = template.updated_at.strftime("%Y-%m-%d")
            updated_item = QTableWidgetItem(updated_text)
            self.templates_table.setItem(row, 5, updated_item)
            
            # Actions placeholder
            actions_item = QTableWidgetItem("View")
            self.templates_table.setItem(row, 6, actions_item)
    
    @debug_button("load_my_templates", "Community Templates Panel")
    def load_my_templates(self, force_reload: bool = False):
        """Load user's own templates using DataLoader."""
        try:
            templates = self.data_loader.load(
                f"my_templates_{self.user_id}",
                lambda: self.community_system.list_templates(author_id=self.user_id),
                force_reload,
            )

            self.my_templates_list.clear()
            for template in templates:
                item = QListWidgetItem(f"{template.name} ({template.category})")
                item.setData(Qt.ItemDataRole.UserRole, template.id)
                self.my_templates_list.addItem(item)

            self.status_label.setText(f"Loaded {len(templates)} of your templates")

        except Exception as e:
            logger.error(f"Error loading my templates: {e}")
            self.status_label.setText(f"Error loading templates: {e}")
    
    @debug_button("load_categories", "Community Templates Panel")
    def load_categories(self):
        """Load template categories."""
        try:
            categories = self.community_system.get_categories()
            
            self.category_filter_combo.clear()
            self.category_filter_combo.addItem("All Categories")
            
            for category in categories:
                self.category_filter_combo.addItem(category.name)
            
        except Exception as e:
            logger.error(f"Error loading categories: {e}")
    
    @debug_button("load_stats", "Community Templates Panel")
    def load_stats(self):
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
                title="community_templates_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def on_template_selected(self):
        """Handle template selection in marketplace."""
        current_row = self.templates_table.currentRow()
        if current_row >= 0:
            item = self.templates_table.item(current_row, 0)
            if item:
                template_id = item.data(Qt.ItemDataRole.UserRole)
                template = self.community_system.get_template(template_id)
                if template:
                    self.current_template = template
                    self.update_template_details(template)
                    self.download_btn.setEnabled(True)
                    self.rate_btn.setEnabled(True)
                    self.fork_btn.setEnabled(True)
    
    @debug_button("on_my_template_selected", "Community Templates Panel")
    def on_my_template_selected(self):
        """Handle my template selection."""
        current_item = self.my_templates_list.currentItem()
        if current_item:
            template_id = current_item.data(Qt.ItemDataRole.UserRole)
            template = self.community_system.get_template(template_id)
            if template:
                self.current_template = template
                self.update_my_template_details(template)
                self.edit_my_btn.setEnabled(True)
                self.delete_my_btn.setEnabled(True)
    
    @debug_button("update_template_details", "Community Templates Panel")
    def update_template_details(self, template: CommunityTemplate):
        """Update template details display."""
        details_html = f"""
        <h3>{template.name}</h3>
        <p><b>Author:</b> {template.author_name}</p>
        <p><b>Category:</b> {template.category}</p>
        <p><b>Difficulty:</b> {template.difficulty_level}</p>
        <p><b>Rating:</b> {template.average_rating:.1f}/5 ({template.rating_count} reviews)</p>
        <p><b>Downloads:</b> {template.download_count}</p>
        <p><b>Tags:</b> {', '.join(template.tags)}</p>
        <p><b>Description:</b> {template.description}</p>
        <hr>
        <h4>Template Content:</h4>
        <pre>{template.content}</pre>
        """
        
        self.template_details.setHtml(details_html)
    
    @debug_button("update_my_template_details", "Community Templates Panel")
    def update_my_template_details(self, template: CommunityTemplate):
        """Update my template details display."""
        details_html = f"""
        <h3>{template.name}</h3>
        <p><b>Category:</b> {template.category}</p>
        <p><b>Difficulty:</b> {template.difficulty_level}</p>
        <p><b>Public:</b> {'Yes' if template.is_public else 'No'}</p>
        <p><b>Rating:</b> {template.average_rating:.1f}/5 ({template.rating_count} reviews)</p>
        <p><b>Downloads:</b> {template.download_count}</p>
        <p><b>Tags:</b> {', '.join(template.tags)}</p>
        <p><b>Description:</b> {template.description}</p>
        <hr>
        <h4>Template Content:</h4>
        <pre>{template.content}</pre>
        """
        
        self.my_template_details.setHtml(details_html)
    
    @debug_button("create_new_template", "Community Templates Panel")
    def create_new_template(self):
        """Create a new template."""
        dialog = TemplateCreationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template_data = dialog.get_template_data()
            
            try:
                template_id = self.community_system.create_template(
                    name=template_data['name'],
                    content=template_data['content'],
                    author_id=self.user_id,
                    author_name=self.user_name,
                    category=template_data['category'],
                    description=template_data['description'],
                    tags=template_data['tags'],
                    is_public=template_data['is_public']
                )
                
                self.template_created.emit(template_id)
                self.load_my_templates()
                self.status_label.setText(f"Created template: {template_data['name']}")
                
                # Switch to my templates tab
                self.tab_widget.setCurrentIndex(1)
                
            except Exception as e:
                logger.error(f"Error creating template: {e}")
                QMessageBox.critical(self, "Error", f"Failed to create template: {e}")
    
    @debug_button("download_selected_template", "Community Templates Panel")
    def download_selected_template(self):
        """Download the selected template."""
        if not self.current_template:
            return
        
        try:
            success = self.community_system.download_template(
                self.current_template.id, self.user_id
            )
            
            if success:
                self.template_downloaded.emit(self.current_template.id)
                self.status_label.setText(f"Downloaded template: {self.current_template.name}")
                
                # Refresh the table to update download count
                self.load_templates()
            else:
                QMessageBox.warning(self, "Download Failed", "Failed to download template")
                
        except Exception as e:
            logger.error(f"Error downloading template: {e}")
            QMessageBox.critical(self, "Error", f"Error downloading template: {e}")
    
    @debug_button("rate_selected_template", "Community Templates Panel")
    def rate_selected_template(self):
        """Rate the selected template."""
        if not self.current_template:
            return
        
        dialog = ReviewDialog(self.current_template.name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            review_data = dialog.get_review_data()
            
            try:
                success = self.community_system.rate_template(
                    template_id=self.current_template.id,
                    user_id=self.user_id,
                    user_name=self.user_name,
                    rating=review_data['rating'],
                    review_text=review_data['review_text']
                )
                
                if success:
                    self.status_label.setText(f"Rated template: {self.current_template.name}")
                    self.load_templates()  # Refresh to update ratings
                else:
                    QMessageBox.warning(self, "Rating Failed", "Failed to rate template")
                    
            except Exception as e:
                logger.error(f"Error rating template: {e}")
                QMessageBox.critical(self, "Error", f"Error rating template: {e}")
    
    @debug_button("fork_selected_template", "Community Templates Panel")
    def fork_selected_template(self):
        """Fork the selected template."""
        if not self.current_template:
            return
        
        # Get new name from user
        new_name, ok = QLineEdit.getText(
            self, "Fork Template", 
            f"Enter a name for your fork of '{self.current_template.name}':"
        )
        
        if ok and new_name.strip():
            try:
                new_template_id = self.community_system.fork_template(
                    template_id=self.current_template.id,
                    user_id=self.user_id,
                    user_name=self.user_name,
                    new_name=new_name.strip()
                )
                
                if new_template_id:
                    self.template_created.emit(new_template_id)
                    self.load_my_templates()
                    self.status_label.setText(f"Forked template: {new_name}")
                    
                    # Switch to my templates tab
                    self.tab_widget.setCurrentIndex(1)
                else:
                    QMessageBox.warning(self, "Fork Failed", "Failed to fork template")
                    
            except Exception as e:
                logger.error(f"Error forking template: {e}")
                QMessageBox.critical(self, "Error", f"Error forking template: {e}")
    
    @debug_button("edit_my_template", "Community Templates Panel")
    def edit_my_template(self):
        """Edit the selected my template."""
        if not self.current_template:
            return
        
        dialog = TemplateCreationDialog(self, self.current_template)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template_data = dialog.get_template_data()
            
            try:
                success = self.community_system.update_template(
                    self.current_template.id, template_data
                )
                
                if success:
                    self.template_updated.emit(self.current_template.id)
                    self.load_my_templates()
                    self.status_label.setText(f"Updated template: {template_data['name']}")
                else:
                    QMessageBox.warning(self, "Update Failed", "Failed to update template")
                    
            except Exception as e:
                logger.error(f"Error updating template: {e}")
                QMessageBox.critical(self, "Error", f"Error updating template: {e}")
    
    @debug_button("delete_my_template", "Community Templates Panel")
    def delete_my_template(self):
        """Delete the selected my template."""
        if not self.current_template:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{self.current_template.name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.community_system.delete_template(
                    self.current_template.id, self.user_id
                )
                
                if success:
                    self.load_my_templates()
                    self.status_label.setText(f"Deleted template: {self.current_template.name}")
                    self.current_template = None
                else:
                    QMessageBox.warning(self, "Delete Failed", "Failed to delete template")
                    
            except Exception as e:
                logger.error(f"Error deleting template: {e}")
                QMessageBox.critical(self, "Error", f"Error deleting template: {e}")
    
    @debug_button("search_templates", "Community Templates Panel")
    def search_templates(self):
        """Search templates."""
        query = self.search_edit.text().strip()
        if not query:
            self.load_templates()
            return
        
        try:
            templates = self.community_system.search_templates(query)
            self.update_templates_table(templates)
            self.status_label.setText(f"Found {len(templates)} templates for '{query}'")
            
        except Exception as e:
            logger.error(f"Error searching templates: {e}")
            self.status_label.setText(f"Error searching: {e}")
    
    @debug_button("filter_by_category", "Community Templates Panel")
    def filter_by_category(self):
        """Filter templates by category."""
        category = self.category_filter_combo.currentText()
        if category == "All Categories":
            self.load_templates()
            return
        
        try:
            templates = self.community_system.list_templates(category=category.lower())
            self.update_templates_table(templates)
            self.status_label.setText(f"Showing {len(templates)} templates in {category}")
            
        except Exception as e:
            logger.error(f"Error filtering by category: {e}")
            self.status_label.setText(f"Error filtering: {e}")
    
    @debug_button("filter_by_difficulty", "Community Templates Panel")
    def filter_by_difficulty(self):
        """Filter templates by difficulty."""
        difficulty = self.difficulty_filter_combo.currentText()
        if difficulty == "All Levels":
            self.load_templates()
            return
        
        try:
            templates = self.community_system.list_templates()
            filtered_templates = [t for t in templates if t.difficulty_level == difficulty.lower()]
            self.update_templates_table(filtered_templates)
            self.status_label.setText(f"Showing {len(filtered_templates)} {difficulty} templates")
            
        except Exception as e:
            logger.error(f"Error filtering by difficulty: {e}")
            self.status_label.setText(f"Error filtering: {e}")
    
    @debug_button("sort_templates", "Community Templates Panel")
    def sort_templates(self):
        """Sort templates."""
        sort_by = self.sort_combo.currentText()
        
        sort_mapping = {
            "Newest": ("created_at", "desc"),
            "Most Popular": ("download_count", "desc"),
            "Highest Rated": ("average_rating", "desc"),
            "Most Downloaded": ("download_count", "desc"),
            "Name": ("name", "asc")
        }
        
        if sort_by in sort_mapping:
            sort_field, sort_order = sort_mapping[sort_by]
            try:
                templates = self.community_system.list_templates(sort_by=sort_field, sort_order=sort_order)
                self.update_templates_table(templates)
                self.status_label.setText(f"Sorted by {sort_by}")
                
            except Exception as e:
                logger.error(f"Error sorting templates: {e}")
                self.status_label.setText(f"Error sorting: {e}")
    
    @debug_button("refresh_ui", "Community Templates Panel")
    def refresh_ui(self):
        """Refresh the UI state."""
        self.load_templates()
        self.load_my_templates()
        self.load_stats() 