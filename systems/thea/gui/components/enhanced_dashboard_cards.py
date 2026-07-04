"""
Enhanced Dashboard Cards Component
=================================

Provides card-based layout for the dashboard with visual hierarchy,
status indicators, and improved user experience.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QGroupBox, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPainterPath
import logging

logger = logging.getLogger(__name__)


class ActionCard(QFrame):
    """Individual action card with status indicator and hover effects."""
    
    clicked = pyqtSignal()
    
    def __init__(self, title, subtitle, icon, status="ready", parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.status = status
        self.setup_ui()
        self.setup_styling()
        self.setup_animations()
        
    def setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Icon and title
        title_layout = QVBoxLayout()
        
        # Title with icon
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(self.subtitle)
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("color: #b0b0b0;")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel()
        self.update_status_indicator()
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
        layout.addStretch()
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(4)
        layout.addWidget(self.progress_bar)
        
    def setup_styling(self):
        """Setup card styling with hover effects."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Base styling - Dark theme
        self.setStyleSheet("""
            ActionCard {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 8px;
                color: #ffffff;
            }
            ActionCard:hover {
                background-color: #353535;
                border: 1px solid #64b5f6;
            }
            QProgressBar {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 2px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 2px;
            }
            QLabel {
                background-color: transparent;
                color: #ffffff;
            }
        """)
        
        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def setup_animations(self):
        """Setup hover animations."""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def update_status_indicator(self):
        """Update the status indicator based on current status."""
        status_colors = {
            "ready": "🟢",
            "running": "🟡", 
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "disabled": "⚫"
        }
        
        self.status_indicator.setText(status_colors.get(self.status, "🔵"))
        
    def set_status(self, status, progress=None):
        """Update card status and optional progress."""
        self.status = status
        self.update_status_indicator()
        
        if progress is not None:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)
            
    def mousePressEvent(self, event):
        """Handle mouse press with visual feedback."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class QuickAccessCard(QFrame):
    """Smaller card for quick access actions."""
    
    clicked = pyqtSignal()
    
    def __init__(self, title, icon, value="", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.value = value
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """Setup the quick access card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Icon and title
        header = QLabel(f"{self.icon}")
        header.setFont(QFont("Arial", 16))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Value (if provided)
        if self.value:
            self.value_label = QLabel(self.value)
            self.value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.value_label.setStyleSheet("color: #2196f3;")
            layout.addWidget(self.value_label)
        else:
            self.value_label = None
            
    def setup_styling(self):
        """Setup quick access card styling."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet("""
            QuickAccessCard {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #ffffff;
            }
            QuickAccessCard:hover {
                background-color: #353535;
                border: 1px solid #64b5f6;
            }
            QLabel {
                background-color: transparent;
                color: #ffffff;
            }
        """)
        
    def update_value(self, value):
        """Update the value displayed on the card."""
        if self.value_label:
            self.value_label.setText(str(value))
            
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SystemStatusBar(QFrame):
    """System status indicator bar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """Setup system status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(20)
        
        # System status indicators
        self.status_indicators = {}
        systems = [
            ("Memory", "💾", "ready"),
            ("MMORPG", "🎮", "ready"),
            ("ChatGPT", "🤖", "warning"),
            ("Analytics", "📊", "ready"),
            ("Templates", "📝", "ready")
        ]
        
        for name, icon, status in systems:
            indicator = self.create_status_indicator(name, icon, status)
            self.status_indicators[name] = indicator
            layout.addWidget(indicator)
            
        layout.addStretch()
        
        # System info
        self.system_info = QLabel("System: Operational")
        self.system_info.setFont(QFont("Arial", 9))
        self.system_info.setStyleSheet("color: #666666;")
        layout.addWidget(self.system_info)
        
    def create_status_indicator(self, name, icon, status):
        """Create individual status indicator."""
        indicator = QLabel()
        indicator.setToolTip(f"{name} System Status")
        self.update_indicator(indicator, name, icon, status)
        return indicator
        
    def update_indicator(self, indicator, name, icon, status):
        """Update status indicator appearance."""
        status_colors = {
            "ready": "✅",
            "warning": "⚠️",
            "error": "❌",
            "running": "🔄"
        }
        
        status_symbol = status_colors.get(status, "🔵")
        indicator.setText(f"{icon} {name}: {status_symbol}")
        indicator.setFont(QFont("Arial", 9))
        
    def update_system_status(self, system, status):
        """Update status for a specific system."""
        if system in self.status_indicators:
            # Get system info
            systems_info = {
                "Memory": ("💾", "Memory"),
                "MMORPG": ("🎮", "MMORPG"),
                "ChatGPT": ("🤖", "ChatGPT"),
                "Analytics": ("📊", "Analytics"),
                "Templates": ("📝", "Templates")
            }
            
            if system in systems_info:
                icon, name = systems_info[system]
                self.update_indicator(self.status_indicators[system], name, icon, status)
                
    def setup_styling(self):
        """Setup status bar styling."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setMaximumHeight(40)
        self.setStyleSheet("""
            SystemStatusBar {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #ffffff;
            }
        """)


class EnhancedDashboardCards(QWidget):
    """Enhanced dashboard with card-based layout."""
    
    # Signals for actions
    setup_clicked = pyqtSignal()
    showcase_clicked = pyqtSignal()
    preview_clicked = pyqtSignal()  # NEW: Preview workflow signal
    workflow_clicked = pyqtSignal()
    refresh_clicked = pyqtSignal()
    stats_clicked = pyqtSignal()
    conversations_clicked = pyqtSignal()
    templates_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the enhanced dashboard UI."""
        # Set dark theme for main widget
        self.setStyleSheet("""
            EnhancedDashboardCards {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 5px;
                margin: 10px 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🏠 Dreamscape Dashboard")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        
        # Primary actions (large cards)
        self.create_primary_actions(layout)
        
        # Quick access (medium cards)
        self.create_quick_access(layout)
        
        # System status (compact bar)
        self.create_system_status(layout)
        
    def create_primary_actions(self, parent_layout):
        """Create primary action cards."""
        group = QGroupBox("⚡ Primary Actions")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QHBoxLayout(group)
        layout.setSpacing(15)
        
        # Setup & Test card
        self.setup_card = ActionCard(
            "Setup & Test",
            "Validate all systems and run comprehensive tests",
            "🔧",
            "ready"
        )
        self.setup_card.clicked.connect(self.setup_clicked.emit)
        layout.addWidget(self.setup_card)
        
        # Showcase card
        self.showcase_card = ActionCard(
            "Comprehensive Showcase", 
            "Demonstrate all 22 features across 6 categories",
            "🎭",
            "ready"
        )
        self.showcase_card.clicked.connect(self.showcase_clicked.emit)
        layout.addWidget(self.showcase_card)
        
        # Preview card (NEW) - Limited to 5 conversations
        self.preview_card = ActionCard(
            "Preview Workflow",
            "Showcase all features with 5 conversations only",
            "🎯",
            "ready"
        )
        self.preview_card.clicked.connect(self.preview_clicked.emit)
        layout.addWidget(self.preview_card)
        
        # Workflow card
        self.workflow_card = ActionCard(
            "End-to-End Workflow",
            "Complete conversation processing pipeline",
            "🚀", 
            "ready"
        )
        self.workflow_card.clicked.connect(self.workflow_clicked.emit)
        layout.addWidget(self.workflow_card)
        
        parent_layout.addWidget(group)
        
    def create_quick_access(self, parent_layout):
        """Create quick access cards."""
        group = QGroupBox("🔗 Quick Access")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QHBoxLayout(group)
        layout.setSpacing(15)
        
        # Stats overview
        self.stats_card = QuickAccessCard("Stats Overview", "📊", "0")
        self.stats_card.clicked.connect(self.stats_clicked.emit)
        layout.addWidget(self.stats_card)
        
        # Recent conversations
        self.conversations_card = QuickAccessCard("Recent Convos", "💬", "0")
        self.conversations_card.clicked.connect(self.conversations_clicked.emit)
        layout.addWidget(self.conversations_card)
        
        # Quick template
        self.templates_card = QuickAccessCard("Quick Template", "📝")
        self.templates_card.clicked.connect(self.templates_clicked.emit)
        layout.addWidget(self.templates_card)
        
        # Refresh dashboard
        self.refresh_card = QuickAccessCard("Refresh Dashboard", "🔄")
        self.refresh_card.clicked.connect(self.refresh_clicked.emit)
        layout.addWidget(self.refresh_card)
        
        parent_layout.addWidget(group)
        
    def create_system_status(self, parent_layout):
        """Create system status bar."""
        group = QGroupBox("⚙️ System Status")
        group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        
        self.status_bar = SystemStatusBar()
        layout.addWidget(self.status_bar)
        
        parent_layout.addWidget(group)
        
    def update_card_status(self, card_name, status, progress=None):
        """Update status of a specific card."""
        cards = {
            "setup": self.setup_card,
            "showcase": self.showcase_card,
            "preview": self.preview_card,
            "workflow": self.workflow_card
        }
        
        if card_name in cards:
            cards[card_name].set_status(status, progress)
            
    def update_quick_access_values(self, stats_count=0, conversations_count=0):
        """Update values on quick access cards."""
        self.stats_card.update_value(str(stats_count))
        self.conversations_card.update_value(str(conversations_count))
        
    def update_system_status(self, system, status):
        """Update system status indicator."""
        self.status_bar.update_system_status(system, status) 