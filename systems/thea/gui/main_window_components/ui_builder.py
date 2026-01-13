"""
UI Builder Component
===================

Handles UI layout and component creation for the main window.
Extracted from main_window.py for better modularity and maintainability.
"""

import logging
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QStackedWidget, QFrame, QStatusBar, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# Import panels
from gui.panels.dashboard_panel import DashboardPanel
from gui.panels.conversations_panel import ConversationsPanel
from gui.panels.analytics_panel import AnalyticsPanel
from gui.panels.content_analytics_panel import ContentAnalyticsPanel
from gui.panels.enhanced_analytics_panel import EnhancedAnalyticsPanel
from gui.panels.resume_panel import ResumePanel
from gui.panels.scraper_panel import ScraperPanel
from gui.panels.task_panel import TaskPanel
from gui.panels.quest_log_panel import QuestLogPanel
from gui.panels.export_panel import ExportPanel
from gui.panels.enhanced_devlog_panel import EnhancedDevlogPanel
from gui.panels.skill_tree_panel import SkillTreePanel
from gui.panels.workflow_panel import WorkflowPanel
from gui.panels.gamification_panel import GamificationPanel
from gui.panels.voice_modeling_panel import VoiceModelingPanel
from gui.panels.community_templates_panel import CommunityTemplatesPanel
from gui.panels.templates_panel import TemplatesPanel
from gui.panels.settings_panel import SettingsPanel
from gui.panels.combat_engine_panel import CombatEnginePanel

logger = logging.getLogger(__name__)


class UIBuilder(QWidget):
    """
    Handles UI layout and component creation for the main window.
    
    This component is responsible for:
    - Building the main window layout
    - Creating the sidebar navigation
    - Setting up the main content area
    - Managing panel widgets
    - Applying styling and themes
    """
    
    # Signals
    panel_switched = pyqtSignal(str)  # Emitted when a panel is switched
    sidebar_button_clicked = pyqtSignal(str)  # Emitted when sidebar button is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # UI components
        self.sidebar: Optional[QWidget] = None
        self.main_content: Optional[QStackedWidget] = None
        self.status_bar: Optional[QStatusBar] = None
        
        # Panel management
        self.panels: Dict[str, QWidget] = {}
        self.panel_buttons: Dict[str, QPushButton] = {}
        self.current_panel: str = "dashboard"
        
        # System references (will be set by main window)
        self.memory_manager = None
        self.mmorpg_engine = None
        self.discord_manager = None
        self.scraping_manager = None
        self.resume_tracker = None
        self.enhanced_skill_system = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        try:
            # Main layout
            main_layout = QHBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create sidebar
            self.sidebar = self._create_sidebar()
            main_layout.addWidget(self.sidebar)
            
            # Create main content area
            self.main_content = self._create_main_content()
            main_layout.addWidget(self.main_content)
            
            # Set layout proportions (sidebar: 250px, main content: flexible)
            main_layout.setStretch(0, 0)  # Sidebar fixed width
            main_layout.setStretch(1, 1)  # Main content flexible
            
            self.setLayout(main_layout)
            logger.info("✅ UI layout setup completed")
            
        except Exception as e:
            logger.error(f"❌ UI setup failed: {str(e)}")
            raise
    
    def _create_sidebar(self) -> QWidget:
        """Create the sidebar navigation."""
        try:
            sidebar = QFrame()
            sidebar.setObjectName("sidebar")
            sidebar.setFixedWidth(250)
            sidebar.setStyleSheet("""
                QFrame#sidebar {
                    background-color: #2c3e50;
                    border-right: 1px solid #34495e;
                }
            """)
            
            # Sidebar layout
            layout = QVBoxLayout(sidebar)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(5)
            
            # Header
            header = QLabel("🌌 Dreamscape")
            header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            header.setStyleSheet("color: white; padding: 10px;")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)
            
            # Navigation buttons
            self._create_navigation_buttons(layout)
            
            # Spacer to push buttons to top
            layout.addStretch()
            
            # Status section
            self._create_status_section(layout)
            
            logger.info("✅ Sidebar created successfully")
            return sidebar
            
        except Exception as e:
            logger.error(f"❌ Sidebar creation failed: {str(e)}")
            raise
    
    def _create_navigation_buttons(self, layout: QVBoxLayout):
        """Create navigation buttons for the sidebar."""
        try:
            # Define panel configurations
            panel_configs = [
                {"name": "dashboard", "text": "🏠 Dashboard", "icon": "🏠"},
                {"name": "conversations", "text": "💬 Conversations", "icon": "💬"},
                {"name": "analytics", "text": "📊 Analytics", "icon": "📊"},
                {"name": "content_analytics", "text": "📈 Content Analytics", "icon": "📈"},
                {"name": "enhanced_analytics", "text": "🔍 Enhanced Analytics", "icon": "🔍"},
                {"name": "resume", "text": "📄 Resume", "icon": "📄"},
                {"name": "scraper", "text": "🕷️ Scraper", "icon": "🕷️"},
                {"name": "task", "text": "✅ Tasks", "icon": "✅"},
                {"name": "quest_log", "text": "🎯 Quest Log", "icon": "🎯"},
                {"name": "export", "text": "📤 Export", "icon": "📤"},
                {"name": "enhanced_devlog", "text": "📝 DevLog", "icon": "📝"},
                {"name": "skill_tree", "text": "🌳 Skill Tree", "icon": "🌳"},
                {"name": "workflow", "text": "⚙️ Workflow", "icon": "⚙️"},
                {"name": "gamification", "text": "🎮 Gamification", "icon": "🎮"},
                {"name": "voice_modeling", "text": "🎤 Voice Modeling", "icon": "🎤"},
                {"name": "community_templates", "text": "👥 Community Templates", "icon": "👥"},
                {"name": "templates", "text": "📋 Templates", "icon": "📋"},
                {"name": "combat_engine", "text": "⚔️ Combat Engine", "icon": "⚔️"},
                {"name": "settings", "text": "⚙️ Settings", "icon": "⚙️"},
            ]
            
            # Create buttons
            for config in panel_configs:
                button = self._create_navigation_button(
                    config["name"], 
                    config["text"], 
                    config["icon"]
                )
                self.panel_buttons[config["name"]] = button
                layout.addWidget(button)
            
            logger.info(f"✅ Created {len(panel_configs)} navigation buttons")
            
        except Exception as e:
            logger.error(f"❌ Navigation button creation failed: {str(e)}")
            raise
    
    def _create_navigation_button(self, panel_name: str, text: str, icon: str) -> QPushButton:
        """Create a single navigation button."""
        button = QPushButton(f"{icon} {text}")
        button.setObjectName(f"nav_button_{panel_name}")
        button.setCheckable(True)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                text-align: left;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
                font-weight: bold;
            }
        """)
        
        # Connect button click
        button.clicked.connect(lambda: self._on_navigation_button_clicked(panel_name))
        
        return button
    
    def _create_status_section(self, layout: QVBoxLayout):
        """Create the status section in the sidebar."""
        try:
            # Status frame
            status_frame = QFrame()
            status_frame.setStyleSheet("""
                QFrame {
                    background-color: #34495e;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            
            status_layout = QVBoxLayout(status_frame)
            
            # Status title
            status_title = QLabel("📊 System Status")
            status_title.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
            status_layout.addWidget(status_title)
            
            # Status indicators
            self.status_indicators = {}
            status_items = [
                ("memory", "🧠 Memory", "Initializing..."),
                ("mmorpg", "🎮 MMORPG", "Initializing..."),
                ("discord", "🤖 Discord", "Initializing..."),
                ("scraper", "🕷️ Scraper", "Initializing..."),
            ]
            
            for key, label, initial_status in status_items:
                status_widget = QLabel(f"{label}: {initial_status}")
                status_widget.setStyleSheet("color: #bdc3c7; font-size: 12px; padding: 2px;")
                status_layout.addWidget(status_widget)
                self.status_indicators[key] = status_widget
            
            layout.addWidget(status_frame)
            logger.info("✅ Status section created")
            
        except Exception as e:
            logger.error(f"❌ Status section creation failed: {str(e)}")
    
    def _create_main_content(self) -> QStackedWidget:
        """Create the main content area with stacked widgets."""
        try:
            main_content = QStackedWidget()
            main_content.setObjectName("main_content")
            main_content.setStyleSheet("""
                QStackedWidget#main_content {
                    background-color: #ecf0f1;
                }
            """)
            
            # Create placeholder panels (will be replaced with actual panels)
            self._create_placeholder_panels(main_content)
            
            logger.info("✅ Main content area created")
            return main_content
            
        except Exception as e:
            logger.error(f"❌ Main content creation failed: {str(e)}")
            raise
    
    def _create_placeholder_panels(self, stacked_widget: QStackedWidget):
        """Create placeholder panels for all navigation items."""
        try:
            panel_names = list(self.panel_buttons.keys())
            
            for panel_name in panel_names:
                placeholder = self._create_placeholder_panel(panel_name)
                self.panels[panel_name] = placeholder
                stacked_widget.addWidget(placeholder)
            
            # Set initial panel
            if "dashboard" in self.panels:
                stacked_widget.setCurrentWidget(self.panels["dashboard"])
                self._update_button_states("dashboard")
            
            logger.info(f"✅ Created {len(panel_names)} placeholder panels")
            
        except Exception as e:
            logger.error(f"❌ Placeholder panel creation failed: {str(e)}")
            raise
    
    def _create_placeholder_panel(self, panel_name: str) -> QWidget:
        """Create a placeholder panel for a given panel name."""
        try:
            panel = QWidget()
            
            layout = QVBoxLayout(panel)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Panel title
            title = QLabel(f"📋 {panel_name.replace('_', ' ').title()} Panel")
            title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Status message
            status = QLabel("Panel is being initialized...")
            status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status.setStyleSheet("color: #7f8c8d; font-size: 14px;")
            layout.addWidget(status)
            
            panel.setLayout(layout)
            return panel
            
        except Exception as e:
            logger.error(f"❌ Placeholder panel creation failed for {panel_name}: {str(e)}")
            raise
    
    def _on_navigation_button_clicked(self, panel_name: str):
        """Handle navigation button clicks."""
        try:
            if panel_name in self.panels:
                self.main_content.setCurrentWidget(self.panels[panel_name])
                self.current_panel = panel_name
                self._update_button_states(panel_name)
                self.panel_switched.emit(panel_name)
                self.sidebar_button_clicked.emit(panel_name)
                logger.info(f"✅ Switched to panel: {panel_name}")
            else:
                logger.warning(f"⚠️ Panel not found: {panel_name}")
                
        except Exception as e:
            logger.error(f"❌ Panel switch failed: {str(e)}")
    
    def _update_button_states(self, active_panel: str):
        """Update button states to show which panel is active."""
        try:
            for panel_name, button in self.panel_buttons.items():
                button.setChecked(panel_name == active_panel)
                
        except Exception as e:
            logger.error(f"❌ Button state update failed: {str(e)}")
    
    def set_system_references(self, systems_data: Dict[str, Any]):
        """Set system references for panels."""
        try:
            self.memory_manager = systems_data.get("memory_manager")
            self.mmorpg_engine = systems_data.get("mmorpg_engine")
            self.discord_manager = systems_data.get("discord_manager")
            self.scraping_manager = systems_data.get("scraping_manager")
            self.resume_tracker = systems_data.get("resume_tracker")
            self.enhanced_skill_system = systems_data.get("enhanced_skill_system")
            
            logger.info("✅ System references set for UI builder")
            
        except Exception as e:
            logger.error(f"❌ Setting system references failed: {str(e)}")
    
    def create_actual_panels(self):
        """Create actual panel instances and replace placeholders."""
        try:
            # Create actual panel instances
            actual_panels = {
                "dashboard": DashboardPanel(),
                "conversations": ConversationsPanel(),
                "analytics": AnalyticsPanel(),
                "content_analytics": ContentAnalyticsPanel(),
                "enhanced_analytics": EnhancedAnalyticsPanel(),
                "resume": ResumePanel(),
                "scraper": ScraperPanel(),
                "task": TaskPanel(),
                "quest_log": QuestLogPanel(),
                "export": ExportPanel(),
                "enhanced_devlog": EnhancedDevlogPanel(),
                "skill_tree": SkillTreePanel(),
                "workflow": WorkflowPanel(),
                "gamification": GamificationPanel(),
                "voice_modeling": VoiceModelingPanel(),
                "community_templates": CommunityTemplatesPanel(),
                "templates": TemplatesPanel(),
                "combat_engine": CombatEnginePanel(),
                "settings": SettingsPanel(),
            }
            
            # Replace placeholders with actual panels
            for panel_name, panel in actual_panels.items():
                if panel_name in self.panels:
                    # Remove placeholder
                    old_panel = self.panels[panel_name]
                    self.main_content.removeWidget(old_panel)
                    old_panel.deleteLater()
                    
                    # Add actual panel
                    self.panels[panel_name] = panel
                    self.main_content.addWidget(panel)
                    
                    # Set system references for panel
                    self._set_panel_system_references(panel, panel_name)
            
            # Set current panel
            if self.current_panel in self.panels:
                self.main_content.setCurrentWidget(self.panels[self.current_panel])
            
            logger.info("✅ Actual panels created and placeholders replaced")
            
        except Exception as e:
            logger.error(f"❌ Actual panel creation failed: {str(e)}")
            raise
    
    def _set_panel_system_references(self, panel: QWidget, panel_name: str):
        """Set system references for a specific panel."""
        try:
            # Check if panel has set_managers method
            if hasattr(panel, 'set_managers'):
                panel.set_managers(
                    self.memory_manager,
                    self.mmorpg_engine,
                    self.discord_manager,
                    self.scraping_manager,
                    self.resume_tracker,
                    self.enhanced_skill_system
                )
                logger.info(f"✅ Set system references for {panel_name}")
            
        except Exception as e:
            logger.error(f"❌ Setting system references for {panel_name} failed: {str(e)}")
    
    def update_status_indicator(self, system_name: str, status: str, color: str = "#bdc3c7"):
        """Update a status indicator in the sidebar."""
        try:
            if system_name in self.status_indicators:
                indicator = self.status_indicators[system_name]
                current_text = indicator.text()
                label = current_text.split(":")[0]  # Extract label part
                indicator.setText(f"{label}: {status}")
                indicator.setStyleSheet(f"color: {color}; font-size: 12px; padding: 2px;")
                
        except Exception as e:
            logger.error(f"❌ Status indicator update failed: {str(e)}")
    
    def get_current_panel(self) -> str:
        """Get the name of the currently active panel."""
        return self.current_panel
    
    def get_panel(self, panel_name: str) -> Optional[QWidget]:
        """Get a specific panel by name."""
        return self.panels.get(panel_name)
    
    def switch_to_panel(self, panel_name: str):
        """Programmatically switch to a specific panel."""
        self._on_navigation_button_clicked(panel_name) 