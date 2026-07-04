#!/usr/bin/env python3
"""
Refresh Integration Manager
Integrates the Global Refresh Manager with existing panels to replace individual refresh buttons.
This system consolidates 91 refresh buttons into a unified, intelligent refresh system.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QMenu, QToolButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QIcon, QAction

from gui.components.refresh_types import RefreshType, RefreshPriority


logger = logging.getLogger(__name__)


class RefreshButtonType(Enum):
    """Types of refresh buttons that can be replaced"""
    CONVERSATIONS = "conversations"
    ANALYTICS = "analytics"
    TEMPLATES = "templates"
    MEMORY = "memory"
    MMORPG = "mmorpg"
    SETTINGS = "settings"
    UI = "ui"
    DASHBOARD = "dashboard"
    CHATGPT = "chatgpt"
    LEADERBOARD = "leaderboard"
    PATTERNS = "patterns"
    HISTORY = "history"
    QUALITY = "quality"
    RECOMMENDATIONS = "recommendations"
    CHART = "chart"
    MODELS = "models"
    STATS = "stats"
    LAYOUT = "layout"
    PROFILES = "profiles"
    DATA = "data"
    OVERVIEW = "overview"


@dataclass
class RefreshButtonConfig:
    """Configuration for a refresh button replacement"""
    button_type: RefreshButtonType
    panel_name: str
    original_button_name: str
    refresh_type: RefreshType
    priority: RefreshPriority = RefreshPriority.NORMAL
    tooltip: str = ""
    icon: str = "🔄"
    custom_callback: Optional[Callable] = None


class RefreshIntegrationManager(QObject):
    """
    Manages integration of Global Refresh Manager with existing panels.
    Replaces individual refresh buttons with unified refresh system.
    """
    
    refresh_requested = pyqtSignal(RefreshType, RefreshPriority)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.refresh_manager: Optional[GlobalRefreshManager] = None
        self.button_configs: Dict[str, RefreshButtonConfig] = {}
        self.replaced_buttons: Dict[str, QPushButton] = {}
        self.panel_integrations: Dict[str, Any] = {}
        
        self._setup_button_configs()
    
    def _setup_button_configs(self):
        """Setup configurations for all refresh buttons to be replaced"""
        configs = [
            # Dashboard Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.DASHBOARD,
                panel_name="dashboard_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.ALL,
                tooltip="Refresh all dashboard data",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.CHATGPT,
                panel_name="dashboard_panel",
                original_button_name="chatgpt_refresh_btn",
                refresh_type=RefreshType.CONVERSATIONS,
                tooltip="Refresh ChatGPT conversations",
                icon="📥"
            ),
            
            # Conversations Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.CONVERSATIONS,
                panel_name="conversations_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.CONVERSATIONS,
                tooltip="Refresh conversations",
                icon="🔄"
            ),
            
            # Analytics Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.ANALYTICS,
                panel_name="analytics_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh analytics data",
                icon="🔄"
            ),
            
            # Enhanced Analytics Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.ANALYTICS,
                panel_name="enhanced_analytics_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh enhanced analytics",
                icon="🔄"
            ),
            
            # Content Analytics Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.OVERVIEW,
                panel_name="content_analytics_panel",
                original_button_name="refresh_overview_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh overview analytics",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.TEMPLATES,
                panel_name="content_analytics_panel",
                original_button_name="refresh_templates_btn",
                refresh_type=RefreshType.TEMPLATES,
                tooltip="Refresh template analytics",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.QUALITY,
                panel_name="content_analytics_panel",
                original_button_name="refresh_quality_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh quality metrics",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.RECOMMENDATIONS,
                panel_name="content_analytics_panel",
                original_button_name="refresh_recommendations_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh recommendations",
                icon="🔄"
            ),
            
            # Templates Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.TEMPLATES,
                panel_name="templates_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.TEMPLATES,
                tooltip="Refresh templates",
                icon="🔄"
            ),
            
            # Memory Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.MEMORY,
                panel_name="memory_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.MEMORY,
                tooltip="Refresh memory data",
                icon="🔄"
            ),
            
            # MMORPG Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.MMORPG,
                panel_name="mmorpg_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.MMORPG,
                tooltip="Refresh MMORPG data",
                icon="🔄"
            ),
            
            # Settings Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.SETTINGS,
                panel_name="settings_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.SETTINGS,
                tooltip="Refresh settings",
                icon="🔄"
            ),
            
            # Gamification Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.LEADERBOARD,
                panel_name="gamification_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.MMORPG,
                tooltip="Refresh leaderboard",
                icon="🔄"
            ),
            
            # Enhanced Devlog Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.PATTERNS,
                panel_name="enhanced_devlog_panel",
                original_button_name="refresh_patterns_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh work patterns",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.HISTORY,
                panel_name="enhanced_devlog_panel",
                original_button_name="refresh_history_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh devlog history",
                icon="🔄"
            ),
            
            # Training Data Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.CONVERSATIONS,
                panel_name="training_data_panel",
                original_button_name="refresh_button",
                refresh_type=RefreshType.CONVERSATIONS,
                tooltip="Refresh training data",
                icon="🔄"
            ),
            
            # Resume Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.DATA,
                panel_name="resume_panel",
                original_button_name="refresh_data_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh resume data",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.OVERVIEW,
                panel_name="resume_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh resume preview",
                icon="🔄"
            ),
            
            # Voice Modeling Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.PROFILES,
                panel_name="voice_modeling_panel",
                original_button_name="refresh_profiles_btn",
                refresh_type=RefreshType.SETTINGS,
                tooltip="Refresh voice profiles",
                icon="🔄"
            ),
            
            # Skill Tree Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.LAYOUT,
                panel_name="skill_tree_panel",
                original_button_name="refresh_layout_btn",
                refresh_type=RefreshType.MMORPG,
                tooltip="Refresh skill tree layout",
                icon="🔄"
            ),
            
            # Workflow Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.STATS,
                panel_name="workflow_panel",
                original_button_name="refresh_status_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh workflow status",
                icon="🔄"
            ),
            
            # Community Templates Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.TEMPLATES,
                panel_name="community_templates_panel",
                original_button_name="refresh_btn",
                refresh_type=RefreshType.TEMPLATES,
                tooltip="Refresh community templates",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.TEMPLATES,
                panel_name="community_templates_panel",
                original_button_name="refresh_my_btn",
                refresh_type=RefreshType.TEMPLATES,
                tooltip="Refresh my templates",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.STATS,
                panel_name="community_templates_panel",
                original_button_name="refresh_stats_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh template stats",
                icon="🔄"
            ),
            
            # Consolidated Analytics Export Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.ANALYTICS,
                panel_name="consolidated_analytics_export_panel",
                original_button_name="refresh_analytics_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh analytics data",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.CONVERSATIONS,
                panel_name="consolidated_analytics_export_panel",
                original_button_name="refresh_conversations_btn",
                refresh_type=RefreshType.CONVERSATIONS,
                tooltip="Refresh conversations",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.CHART,
                panel_name="consolidated_analytics_export_panel",
                original_button_name="refresh_chart_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh chart data",
                icon="🔄"
            ),
            RefreshButtonConfig(
                button_type=RefreshButtonType.HISTORY,
                panel_name="consolidated_analytics_export_panel",
                original_button_name="refresh_history_btn",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh export history",
                icon="🔄"
            ),
            
            # Consolidated AI Studio Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.MODELS,
                panel_name="consolidated_ai_studio_panel",
                original_button_name="refresh_models_btn",
                refresh_type=RefreshType.SETTINGS,
                tooltip="Refresh AI models",
                icon="🔄"
            ),
            
            # Combat Engine Panel
            RefreshButtonConfig(
                button_type=RefreshButtonType.ANALYTICS,
                panel_name="combat_engine_panel",
                original_button_name="refresh_button",
                refresh_type=RefreshType.ANALYTICS,
                tooltip="Refresh combat analytics",
                icon="🔄"
            ),
        ]
        
        # Store configurations by panel and button name
        for config in configs:
            key = f"{config.panel_name}.{config.original_button_name}"
            self.button_configs[key] = config
    
    def set_refresh_manager(self, refresh_manager: "GlobalRefreshManager"):
        """Set the global refresh manager instance"""
        self.refresh_manager = refresh_manager
    
    def integrate_panel(self, panel_name: str, panel_instance: QWidget):
        """Integrate a panel with the refresh manager"""
        try:
            self.panel_integrations[panel_name] = panel_instance
            self._replace_panel_buttons(panel_name, panel_instance)
            logger.info(f"Integrated refresh manager with {panel_name}")
        except Exception as e:
            logger.error(f"Failed to integrate {panel_name}: {e}")
    
    def _replace_panel_buttons(self, panel_name: str, panel_instance: QWidget):
        """Replace refresh buttons in a panel"""
        for key, config in self.button_configs.items():
            if config.panel_name == panel_name:
                self._replace_single_button(panel_instance, config)
    
    def _replace_single_button(self, panel_instance: QWidget, config: RefreshButtonConfig):
        """Replace a single refresh button"""
        try:
            # Find the original button
            original_button = getattr(panel_instance, config.original_button_name, None)
            if not original_button:
                logger.warning(f"Button {config.original_button_name} not found in {config.panel_name}")
                return
            
            # Create replacement button
            replacement_button = self._create_unified_refresh_button(config)
            
            # Replace the button in the layout
            self._replace_button_in_layout(original_button, replacement_button)
            
            # Store the replacement
            key = f"{config.panel_name}.{config.original_button_name}"
            self.replaced_buttons[key] = replacement_button
            
            logger.info(f"Replaced {config.original_button_name} in {config.panel_name}")
            
        except Exception as e:
            logger.error(f"Failed to replace button {config.original_button_name} in {config.panel_name}: {e}")
    
    def _create_unified_refresh_button(self, config: RefreshButtonConfig) -> QPushButton:
        """Create a unified refresh button"""
        button = QPushButton(f"{config.icon} Refresh")
        button.setToolTip(config.tooltip or f"Refresh {config.refresh_type.value}")
        
        # Connect to refresh manager
        button.clicked.connect(
            lambda: self._handle_refresh_request(config.refresh_type, config.priority)
        )
        
        # Apply styling
        button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        
        return button
    
    def _replace_button_in_layout(self, old_button: QPushButton, new_button: QPushButton):
        """Replace a button in its parent layout"""
        try:
            # Get the parent layout
            parent = old_button.parent()
            if not parent:
                return
            
            # Find the layout containing the old button
            for child in parent.children():
                if isinstance(child, QWidget):
                    layout = child.layout()
                    if layout:
                        # Find the index of the old button
                        for i in range(layout.count()):
                            item = layout.itemAt(i)
                            if item.widget() == old_button:
                                # Replace the button
                                layout.removeWidget(old_button)
                                layout.insertWidget(i, new_button)
                                old_button.hide()
                                new_button.show()
                                return
        except Exception as e:
            logger.error(f"Failed to replace button in layout: {e}")
    
    def _handle_refresh_request(self, refresh_type: RefreshType, priority: RefreshPriority):
        """Handle a refresh request"""
        if self.refresh_manager:
            request = RefreshRequest(
                refresh_type=refresh_type,
                priority=priority
            )
            self.refresh_manager._queue_refresh(request)
            self.refresh_requested.emit(refresh_type, priority)
        else:
            logger.warning("Refresh manager not available")
    
    def create_global_refresh_button(self, refresh_type: RefreshType, 
                                   priority: RefreshPriority = RefreshPriority.NORMAL,
                                   text: str = "Refresh", icon: str = "🔄",
                                   tooltip: str = "") -> QPushButton:
        """Create a global refresh button for new components"""
        button = QPushButton(f"{icon} {text}")
        button.setToolTip(tooltip or f"Refresh {refresh_type.value}")
        
        button.clicked.connect(
            lambda: self._handle_refresh_request(refresh_type, priority)
        )
        
        return button
    
    def create_refresh_menu_button(self, panel_name: str) -> QToolButton:
        """Create a refresh menu button for panels with multiple refresh options"""
        button = QToolButton()
        button.setText("🔄")
        button.setToolTip("Refresh Options")
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # Create menu with refresh options
        menu = QMenu()
        
        # Add refresh options for this panel
        panel_configs = [
            config for config in self.button_configs.values()
            if config.panel_name == panel_name
        ]
        
        for config in panel_configs:
            action = QAction(f"{config.icon} {config.refresh_type.value.title()}", menu)
            action.triggered.connect(
                lambda checked, rt=config.refresh_type, p=config.priority: 
                self._handle_refresh_request(rt, p)
            )
            menu.addAction(action)
        
        # Add separator and global refresh option
        menu.addSeparator()
        global_action = QAction("🔄 Refresh All", menu)
        global_action.triggered.connect(
            lambda: self._handle_refresh_request(RefreshType.ALL, RefreshPriority.NORMAL)
        )
        menu.addAction(global_action)
        
        button.setMenu(menu)
        return button
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the status of refresh integration"""
        return {
            "total_buttons_configured": len(self.button_configs),
            "total_buttons_replaced": len(self.replaced_buttons),
            "panels_integrated": list(self.panel_integrations.keys()),
            "replacement_rate": len(self.replaced_buttons) / len(self.button_configs) if self.button_configs else 0
        }
    
    def show_refresh_manager(self):
        """Show the global refresh manager"""
        if self.refresh_manager:
            self.refresh_manager.show()
            self.refresh_manager.raise_()
            self.refresh_manager.activateWindow()
        else:
            logger.warning("Refresh manager not available")


class UnifiedRefreshButton(QPushButton):
    """
    Unified refresh button that integrates with the Global Refresh Manager.
    Use this instead of individual refresh buttons in new components.
    """
    
    def __init__(self, refresh_type: RefreshType, 
                 priority: RefreshPriority = RefreshPriority.NORMAL,
                 text: str = "Refresh", icon: str = "🔄",
                 tooltip: str = "", parent=None):
        super().__init__(f"{icon} {text}", parent)
        
        self.refresh_type = refresh_type
        self.priority = priority
        self.integration_manager = None
        
        self.setToolTip(tooltip or f"Refresh {refresh_type.value}")
        self.clicked.connect(self._handle_click)
        
        # Apply default styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
    
    def set_integration_manager(self, manager: RefreshIntegrationManager):
        """Set the integration manager"""
        self.integration_manager = manager
    
    def _handle_click(self):
        """Handle button click"""
        if self.integration_manager:
            self.integration_manager._handle_refresh_request(self.refresh_type, self.priority)
        else:
            logger.warning("Integration manager not set for UnifiedRefreshButton")


def create_refresh_integration_manager() -> RefreshIntegrationManager:
    """Create and configure a refresh integration manager"""
    from gui.components.global_refresh_manager import GlobalRefreshManager  # moved import here to avoid circular import
    manager = RefreshIntegrationManager()
    
    # Create the global refresh manager
    refresh_manager = GlobalRefreshManager()
    manager.set_refresh_manager(refresh_manager)
    
    return manager 