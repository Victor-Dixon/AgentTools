#!/usr/bin/env python3
"""
Shared Components Library
Eliminates duplicate UI code by providing standardized components for common UI elements.
Reduces code duplication and ensures consistent UI across all panels.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QProgressBar, QGroupBox, QFrame, QSpacerItem, QSizePolicy,
    QTextEdit, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QSplitter, QTabWidget, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QGridLayout, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

logger = logging.getLogger(__name__)

class ComponentStyle(Enum):
    """Predefined component styles"""
    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


@dataclass
class ComponentConfig:
    """Configuration for shared components"""
    style: ComponentStyle = ComponentStyle.DEFAULT
    show_icon: bool = True
    show_border: bool = True
    collapsible: bool = False
    expandable: bool = False
    animated: bool = False


class SharedComponents:
    """
    Shared Components Library
    
    Provides standardized UI components to eliminate code duplication
    and ensure consistent user experience across all panels.
    """
    
    def __init__(self):
        self._style_cache: Dict[str, str] = {}
        self._icon_cache: Dict[str, QIcon] = {}
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup component styles"""
        self._style_cache = {
            ComponentStyle.DEFAULT.value: """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """,
            ComponentStyle.PRIMARY.value: """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #007bff;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #f8f9fa;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #007bff;
                }
            """,
            ComponentStyle.SUCCESS.value: """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #f8fff9;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #28a745;
                }
            """,
            ComponentStyle.WARNING.value: """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #ffc107;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #fffbf0;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #856404;
                }
            """,
            ComponentStyle.ERROR.value: """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #dc3545;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #fff5f5;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #dc3545;
                }
            """,
            ComponentStyle.INFO.value: """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #17a2b8;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #f0f8ff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #17a2b8;
                }
            """
        }
    
    def create_header(self, title: str, subtitle: str = "", icon: str = "", 
                     config: ComponentConfig = None) -> QWidget:
        """
        Create a standardized header component
        
        Args:
            title: Main header text
            subtitle: Optional subtitle
            icon: Optional icon (emoji or icon name)
            config: Component configuration
        
        Returns:
            QWidget: Header widget
        """
        if config is None:
            config = ComponentConfig()
        
        header_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Main title row
        title_layout = QHBoxLayout()
        
        if icon and config.show_icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 20))
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial", 10))
            subtitle_label.setStyleSheet("color: #666666;")
            layout.addWidget(subtitle_label)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        header_widget.setLayout(layout)
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            header_widget.setStyleSheet(self._style_cache[config.style.value])
        
        return header_widget

    def create_panel_header(self, title: str, icon: str = "", 
                           refresh_callback: Callable = None,
                           additional_buttons: List[Dict[str, Any]] = None,
                           config: ComponentConfig = None) -> QWidget:
        """
        Create a standardized panel header with title, icon, and action buttons
        
        Args:
            title: Panel title
            icon: Optional icon (emoji or icon name)
            refresh_callback: Optional callback for refresh button
            additional_buttons: List of additional button configurations
            config: Component configuration
        
        Returns:
            QWidget: Panel header widget
        """
        if config is None:
            config = ComponentConfig()
        if additional_buttons is None:
            additional_buttons = []
        
        header_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title and icon
        if icon and config.show_icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 16))
            layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Additional buttons (left side)
        for button_config in additional_buttons:
            btn = QPushButton(button_config.get("text", ""))
            if "icon" in button_config:
                btn.setText(button_config["icon"] + " " + btn.text())
            if "callback" in button_config:
                btn.clicked.connect(button_config["callback"])
            if "tooltip" in button_config:
                btn.setToolTip(button_config["tooltip"])
            layout.addWidget(btn)
        
        # Refresh button (right side)
        if refresh_callback:
            refresh_btn = QPushButton("🔄 Refresh")
            refresh_btn.clicked.connect(refresh_callback)
            layout.addWidget(refresh_btn)
        
        header_widget.setLayout(layout)
        return header_widget

    def create_statistics_grid(self, title: str = "Statistics", 
                              stats: List[Dict[str, Any]] = None,
                              stats_data: Dict[str, Any] = None,
                              config: ComponentConfig = None,
                              style: str = None) -> QGroupBox:
        """
        Create a standardized statistics grid
        
        Args:
            title: Section title
            stats: List of statistics to display (preferred format)
            stats_data: Dictionary of statistics (legacy format)
            config: Component configuration
            style: Style string (legacy parameter)
        
        Returns:
            QGroupBox: Statistics grid widget
        """
        if config is None:
            config = ComponentConfig()
        if stats is None and stats_data is None:
            stats = []
        elif stats is None and stats_data is not None:
            # Convert legacy stats_data format to stats format
            stats = []
            for key, value in stats_data.items():
                stats.append({
                    "label": key,
                    "value": str(value),
                    "key": key.lower().replace(" ", "_"),
                    "color": "#0078d4"  # Default color
                })
        
        # Handle legacy style parameter
        if style and style == "modern":
            config.style = ComponentStyle.PRIMARY
        
        stats_group = QGroupBox(title)
        layout = QGridLayout()
        
        # Create stat labels
        stat_labels = {}
        for i, stat in enumerate(stats):
            # Label
            label = QLabel(stat.get("label", f"Stat {i+1}"))
            layout.addWidget(label, i // 2, (i % 2) * 2)
            
            # Value
            value_label = QLabel(stat.get("value", "0"))
            value_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Apply color if specified
            if "color" in stat:
                value_label.setStyleSheet(f"color: {stat['color']};")
            
            layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)
            stat_labels[stat.get("key", f"stat_{i}")] = value_label
        
        stats_group.setLayout(layout)
        
        # Store labels for later updates
        stats_group.stat_labels = stat_labels
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            stats_group.setStyleSheet(self._style_cache[config.style.value])
        
        return stats_group

    def create_refresh_button(self, text: str = "Refresh", 
                             icon: str = "🔄",
                             callback: Callable = None,
                             tooltip: str = "") -> QPushButton:
        """
        Create a standardized refresh button
        
        Args:
            text: Button text
            icon: Button icon (emoji)
            callback: Click callback function
            tooltip: Button tooltip
        
        Returns:
            QPushButton: Refresh button
        """
        button = QPushButton(f"{icon} {text}")
        if callback:
            button.clicked.connect(callback)
        if tooltip:
            button.setToolTip(tooltip)
        return button

    def create_action_buttons(self, actions: List[Dict[str, Any]]) -> QWidget:
        """
        Create a standardized action button group
        
        Args:
            actions: List of action configurations
        
        Returns:
            QWidget: Action buttons widget
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        for action in actions:
            btn = QPushButton(action.get("text", ""))
            if "icon" in action:
                btn.setText(action["icon"] + " " + btn.text())
            if "callback" in action:
                btn.clicked.connect(action["callback"])
            if "tooltip" in action:
                btn.setToolTip(action["tooltip"])
            if "enabled" in action:
                btn.setEnabled(action["enabled"])
            layout.addWidget(btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_data_list(self, title: str = "Data List",
                        items: List[Dict[str, Any]] = None,
                        selection_mode: QAbstractItemView.SelectionMode = QAbstractItemView.SelectionMode.SingleSelection,
                        config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized data list widget
        
        Args:
            title: Section title
            items: List of items to display
            selection_mode: List selection mode
            config: Component configuration
        
        Returns:
            QGroupBox: Data list widget
        """
        if config is None:
            config = ComponentConfig()
        if items is None:
            items = []
        
        list_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # Create list widget
        list_widget = QListWidget()
        list_widget.setSelectionMode(selection_mode)
        
        # Add items
        for item in items:
            list_item = QListWidgetItem()
            if "icon" in item:
                list_item.setText(item["icon"] + " " + item.get("text", ""))
            else:
                list_item.setText(item.get("text", ""))
            if "tooltip" in item:
                list_item.setToolTip(item["tooltip"])
            if "data" in item:
                list_item.setData(Qt.ItemDataRole.UserRole, item["data"])
            list_widget.addItem(list_item)
        
        layout.addWidget(list_widget)
        list_group.setLayout(layout)
        
        # Store list widget for later access
        list_group.list_widget = list_widget
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            list_group.setStyleSheet(self._style_cache[config.style.value])
        
        return list_group

    def create_form_section(self, title: str = "Form",
                           fields: List[Dict[str, Any]] = None,
                           config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized form section
        
        Args:
            title: Section title
            fields: List of form field configurations
            config: Component configuration
        
        Returns:
            QGroupBox: Form section widget
        """
        if config is None:
            config = ComponentConfig()
        if fields is None:
            fields = []
        
        form_group = QGroupBox(title)
        layout = QGridLayout()
        
        form_widgets = {}
        
        for i, field in enumerate(fields):
            field_type = field.get("type", "text")
            field_label = field.get("label", f"Field {i+1}")
            field_key = field.get("key", f"field_{i}")
            
            # Add label
            label = QLabel(field_label)
            layout.addWidget(label, i, 0)
            
            # Create input widget based on type
            if field_type == "text":
                widget = QLineEdit()
                if "placeholder" in field:
                    widget.setPlaceholderText(field["placeholder"])
                if "default" in field:
                    widget.setText(field["default"])
            elif field_type == "textarea":
                widget = QTextEdit()
                if "default" in field:
                    widget.setPlainText(field["default"])
            elif field_type == "combo":
                widget = QComboBox()
                if "options" in field:
                    widget.addItems(field["options"])
                if "default" in field:
                    widget.setCurrentText(field["default"])
            elif field_type == "spin":
                widget = QSpinBox()
                if "min" in field:
                    widget.setMinimum(field["min"])
                if "max" in field:
                    widget.setMaximum(field["max"])
                if "default" in field:
                    widget.setValue(field["default"])
            elif field_type == "check":
                widget = QCheckBox()
                if "default" in field:
                    widget.setChecked(field["default"])
            else:
                widget = QLineEdit()
            
            layout.addWidget(widget, i, 1)
            form_widgets[field_key] = widget
        
        form_group.setLayout(layout)
        form_group.form_widgets = form_widgets
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            form_group.setStyleSheet(self._style_cache[config.style.value])
        
        return form_group

    def create_split_panel(self, left_widget: QWidget = None,
                          right_widget: QWidget = None,
                          left_title: str = "Left Panel",
                          right_title: str = "Right Panel",
                          proportions: List[int] = None) -> QSplitter:
        """
        Create a standardized split panel layout
        
        Args:
            left_widget: Left panel widget
            right_widget: Right panel widget
            left_title: Left panel title
            right_title: Right panel title
            proportions: Split proportions [left, right]
        
        Returns:
            QSplitter: Split panel widget
        """
        if proportions is None:
            proportions = [300, 700]
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel
        if left_widget:
            left_group = QGroupBox(left_title)
            left_layout = QVBoxLayout()
            left_layout.addWidget(left_widget)
            left_group.setLayout(left_layout)
            splitter.addWidget(left_group)
        
        # Right panel
        if right_widget:
            right_group = QGroupBox(right_title)
            right_layout = QVBoxLayout()
            right_layout.addWidget(right_widget)
            right_group.setLayout(right_layout)
            splitter.addWidget(right_group)
        
        # Set proportions
        splitter.setSizes(proportions)
        
        return splitter

    def create_tab_panel(self, tabs: List[Dict[str, Any]] = None) -> QTabWidget:
        """
        Create a standardized tab panel
        
        Args:
            tabs: List of tab configurations
        
        Returns:
            QTabWidget: Tab panel widget
        """
        if tabs is None:
            tabs = []
        
        tab_widget = QTabWidget()
        
        for tab in tabs:
            widget = tab.get("widget", QWidget())
            title = tab.get("title", "Tab")
            icon = tab.get("icon", "")
            
            if icon:
                tab_widget.addTab(widget, icon + " " + title)
            else:
                tab_widget.addTab(widget, title)
        
        return tab_widget

    def create_status_bar(self, status_items: List[Dict[str, Any]] = None) -> QWidget:
        """
        Create a standardized status bar
        
        Args:
            status_items: List of status item configurations
        
        Returns:
            QWidget: Status bar widget
        """
        if status_items is None:
            status_items = []
        
        status_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        status_labels = {}
        
        for item in status_items:
            label = QLabel(item.get("text", ""))
            if "icon" in item:
                label.setText(item["icon"] + " " + label.text())
            if "color" in item:
                label.setStyleSheet(f"color: {item['color']};")
            layout.addWidget(label)
            status_labels[item.get("key", "status")] = label
        
        layout.addStretch()
        status_widget.setLayout(layout)
        status_widget.status_labels = status_labels
        
        return status_widget

    def create_progress_section(self, title: str = "Progress", 
                               show_percentage: bool = True,
                               show_status: bool = True,
                               config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized progress section
        
        Args:
            title: Section title
            show_percentage: Whether to show percentage
            show_status: Whether to show status text
            config: Component configuration
        
        Returns:
            QGroupBox: Progress section widget
        """
        if config is None:
            config = ComponentConfig()
        
        progress_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(0)
        layout.addWidget(progress_bar)
        
        # Status row
        if show_status or show_percentage:
            status_layout = QHBoxLayout()
            
            if show_status:
                status_label = QLabel("Ready")
                status_label.setObjectName("status_label")
                status_layout.addWidget(status_label)
            
            status_layout.addStretch()
            
            if show_percentage:
                percentage_label = QLabel("0%")
                percentage_label.setObjectName("percentage_label")
                status_layout.addWidget(percentage_label)
            
            layout.addLayout(status_layout)
        
        progress_group.setLayout(layout)
        
        # Store widgets for later updates
        progress_group.progress_bar = progress_bar
        if show_status:
            progress_group.status_label = progress_group.findChild(QLabel, "status_label")
        if show_percentage:
            progress_group.percentage_label = progress_group.findChild(QLabel, "percentage_label")
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            progress_group.setStyleSheet(self._style_cache[config.style.value])
        
        return progress_group

    def create_status_section(self, title: str = "Status", 
                            show_icon: bool = True,
                            config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized status section
        
        Args:
            title: Section title
            show_icon: Whether to show status icons
            config: Component configuration
        
        Returns:
            QGroupBox: Status section widget
        """
        if config is None:
            config = ComponentConfig()
        
        status_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # Status items will be added dynamically
        status_group.status_layout = layout
        status_group.setLayout(layout)
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            status_group.setStyleSheet(self._style_cache[config.style.value])
        
        return status_group

    def add_status_item(self, status_group: QGroupBox, label: str, 
                       status: str = "ok", icon: str = "✅") -> QLabel:
        """
        Add a status item to a status section
        
        Args:
            status_group: Status group widget
            label: Status label
            status: Status type (ok, warning, error, info)
            icon: Status icon
        
        Returns:
            QLabel: Status label widget
        """
        status_layout = status_group.status_layout
        
        # Status row
        status_row = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            status_row.addWidget(icon_label)
        
        label_widget = QLabel(label)
        status_row.addWidget(label_widget)
        status_row.addStretch()
        
        # Apply status-specific styling
        if status == "ok":
            label_widget.setStyleSheet("color: #28a745;")
        elif status == "warning":
            label_widget.setStyleSheet("color: #ffc107;")
        elif status == "error":
            label_widget.setStyleSheet("color: #dc3545;")
        elif status == "info":
            label_widget.setStyleSheet("color: #17a2b8;")
        
        status_layout.addLayout(status_row)
        
        return label_widget

    def create_button_group(self, title: str = "", 
                           buttons: List[Dict[str, Any]] = None,
                           config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized button group
        
        Args:
            title: Group title
            buttons: List of button configurations
            config: Component configuration
        
        Returns:
            QGroupBox: Button group widget
        """
        if config is None:
            config = ComponentConfig()
        if buttons is None:
            buttons = []
        
        button_group = QGroupBox(title)
        layout = QHBoxLayout()
        
        for button_config in buttons:
            button = QPushButton(button_config.get("text", ""))
            
            if "icon" in button_config:
                button.setText(button_config["icon"] + " " + button.text())
            
            if "callback" in button_config:
                button.clicked.connect(button_config["callback"])
            
            if "tooltip" in button_config:
                button.setToolTip(button_config["tooltip"])
            
            if "enabled" in button_config:
                button.setEnabled(button_config["enabled"])
            
            layout.addWidget(button)
        
        layout.addStretch()
        button_group.setLayout(layout)
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            button_group.setStyleSheet(self._style_cache[config.style.value])
        
        return button_group

    def create_data_table(self, title: str = "Data", 
                         headers: List[str] = None,
                         data: List[List[Any]] = None,
                         config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized data table
        
        Args:
            title: Table title
            headers: Column headers
            data: Table data
            config: Component configuration
        
        Returns:
            QGroupBox: Data table widget
        """
        if config is None:
            config = ComponentConfig()
        if headers is None:
            headers = []
        if data is None:
            data = []
        
        table_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Set data
        table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                if j < len(headers):
                    table.setItem(i, j, QTableWidgetItem(str(cell)))
        
        # Auto-resize columns
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(table)
        table_group.setLayout(layout)
        
        # Store table for later access
        table_group.table = table
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            table_group.setStyleSheet(self._style_cache[config.style.value])
        
        return table_group

    def create_info_panel(self, title: str = "Information", 
                         content: str = "",
                         config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized information panel
        
        Args:
            title: Panel title
            content: Information content
            config: Component configuration
        
        Returns:
            QGroupBox: Information panel widget
        """
        if config is None:
            config = ComponentConfig()
        
        info_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # Content label
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setOpenExternalLinks(True)
        layout.addWidget(content_label)
        
        info_group.setLayout(layout)
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            info_group.setStyleSheet(self._style_cache[config.style.value])
        
        return info_group

    def create_action_panel(self, title: str = "Actions", 
                           actions: List[Dict[str, Any]] = None,
                           config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized action panel
        
        Args:
            title: Panel title
            actions: List of action configurations
            config: Component configuration
        
        Returns:
            QGroupBox: Action panel widget
        """
        if config is None:
            config = ComponentConfig()
        if actions is None:
            actions = []
        
        action_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        for action in actions:
            button = QPushButton(action.get("text", ""))
            
            if "icon" in action:
                button.setText(action["icon"] + " " + button.text())
            
            if "callback" in action:
                button.clicked.connect(action["callback"])
            
            if "tooltip" in action:
                button.setToolTip(action["tooltip"])
            
            if "enabled" in action:
                button.setEnabled(action["enabled"])
            
            layout.addWidget(button)
        
        action_group.setLayout(layout)
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            action_group.setStyleSheet(self._style_cache[config.style.value])
        
        return action_group

    def create_loading_indicator(self, message: str = "Loading...", 
                                config: ComponentConfig = None) -> QWidget:
        """
        Create a standardized loading indicator
        
        Args:
            message: Loading message
            config: Component configuration
        
        Returns:
            QWidget: Loading indicator widget
        """
        if config is None:
            config = ComponentConfig()
        
        loading_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Loading message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont("Arial", 12))
        layout.addWidget(message_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)  # Indeterminate
        layout.addWidget(progress_bar)
        
        loading_widget.setLayout(layout)
        
        # Apply style
        if config.style != ComponentStyle.DEFAULT:
            loading_widget.setStyleSheet(self._style_cache[config.style.value])
        
        return loading_widget

    def create_error_panel(self, title: str = "Error", 
                          error_message: str = "",
                          show_retry: bool = True,
                          retry_callback: Callable = None,
                          config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized error panel
        
        Args:
            title: Panel title
            error_message: Error message
            show_retry: Whether to show retry button
            retry_callback: Retry callback function
            config: Component configuration
        
        Returns:
            QGroupBox: Error panel widget
        """
        if config is None:
            config = ComponentConfig()
        
        error_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # Error icon and message
        error_layout = QHBoxLayout()
        error_icon = QLabel("❌")
        error_icon.setFont(QFont("Arial", 16))
        error_layout.addWidget(error_icon)
        
        error_label = QLabel(error_message)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("color: #dc3545;")
        error_layout.addWidget(error_label)
        
        layout.addLayout(error_layout)
        
        # Retry button
        if show_retry and retry_callback:
            retry_button = QPushButton("🔄 Retry")
            retry_button.clicked.connect(retry_callback)
            layout.addWidget(retry_button)
        
        error_group.setLayout(layout)
        
        # Apply error style
        error_group.setStyleSheet(self._style_cache[ComponentStyle.ERROR.value])
        
        return error_group

    def create_success_panel(self, title: str = "Success", 
                            message: str = "",
                            show_details: bool = False,
                            details: str = "",
                            config: ComponentConfig = None) -> QGroupBox:
        """
        Create a standardized success panel
        
        Args:
            title: Panel title
            message: Success message
            show_details: Whether to show details
            details: Additional details
            config: Component configuration
        
        Returns:
            QGroupBox: Success panel widget
        """
        if config is None:
            config = ComponentConfig()
        
        success_group = QGroupBox(title)
        layout = QVBoxLayout()
        
        # Success icon and message
        success_layout = QHBoxLayout()
        success_icon = QLabel("✅")
        success_icon.setFont(QFont("Arial", 16))
        success_layout.addWidget(success_icon)
        
        success_label = QLabel(message)
        success_label.setWordWrap(True)
        success_label.setStyleSheet("color: #28a745;")
        success_layout.addWidget(success_label)
        
        layout.addLayout(success_layout)
        
        # Details
        if show_details and details:
            details_label = QLabel(details)
            details_label.setWordWrap(True)
            details_label.setStyleSheet("color: #666666; font-size: 10px;")
            layout.addWidget(details_label)
        
        success_group.setLayout(layout)
        
        # Apply success style
        success_group.setStyleSheet(self._style_cache[ComponentStyle.SUCCESS.value])
        
        return success_group

    def validate_component(self, component: QWidget, component_type: str = "unknown") -> bool:
        """
        Validate that a component was created correctly
        
        Args:
            component: The component to validate
            component_type: Type of component for error messages
        
        Returns:
            bool: True if component is valid, False otherwise
        """
        try:
            if component is None:
                logger.error(f"Failed to create {component_type}: component is None")
                return False
            
            if not isinstance(component, QWidget):
                logger.error(f"Failed to create {component_type}: not a QWidget")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating {component_type}: {e}")
            return False

    def safe_create_component(self, create_func: Callable, *args, **kwargs) -> Optional[QWidget]:
        """
        Safely create a component with error handling
        
        Args:
            create_func: Function to create the component
            *args: Arguments for the create function
            **kwargs: Keyword arguments for the create function
        
        Returns:
            Optional[QWidget]: Created component or None if failed
        """
        try:
            component = create_func(*args, **kwargs)
            if self.validate_component(component, create_func.__name__):
                return component
            else:
                logger.error(f"Component validation failed for {create_func.__name__}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating component {create_func.__name__}: {e}")
            return None


# Global instance for easy access
shared_components = SharedComponents()


def main():
    """Test the shared components"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create test window
    from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
    
    window = QMainWindow()
    window.setWindowTitle("Shared Components Test")
    window.resize(800, 600)
    
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    # Test components
    components = SharedComponents()
    
    # Header
    header = components.create_header("Test Application", "Testing shared components", "🧪")
    layout.addWidget(header)
    
    # Panel header
    panel_header = components.create_panel_header(
        "Test Panel", 
        "📊",
        lambda: print("Refresh clicked"),
        [{"text": "Export", "icon": "📤", "callback": lambda: print("Export clicked")}]
    )
    layout.addWidget(panel_header)
    
    # Statistics grid
    stats = components.create_statistics_grid("Test Statistics", [
        {"label": "Total Items", "value": "1,234", "key": "total", "color": "#0078d4"},
        {"label": "Active Items", "value": "567", "key": "active", "color": "#107c10"},
        {"label": "Pending Items", "value": "89", "key": "pending", "color": "#ffc107"},
        {"label": "Error Items", "value": "12", "key": "errors", "color": "#dc3545"}
    ])
    layout.addWidget(stats)
    
    # Action buttons
    actions = components.create_action_buttons([
        {"text": "Add Item", "icon": "➕", "callback": lambda: print("Add clicked")},
        {"text": "Edit Item", "icon": "✏️", "callback": lambda: print("Edit clicked")},
        {"text": "Delete Item", "icon": "🗑️", "callback": lambda: print("Delete clicked")}
    ])
    layout.addWidget(actions)
    
    # Status bar
    status_bar = components.create_status_bar([
        {"text": "Ready", "icon": "✅", "key": "status"},
        {"text": "Connected", "icon": "🔗", "key": "connection", "color": "#28a745"}
    ])
    layout.addWidget(status_bar)
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 