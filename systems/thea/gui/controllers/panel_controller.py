"""
Panel Controller - GUI Panel Management
======================================

This controller handles panel lifecycle, switching, and management,
separated from the main window for better organization.
"""

import logging
from typing import Dict, Any, Optional, Type
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel

logger = logging.getLogger(__name__)


class PanelController(QObject):
    """Controls panel lifecycle and management."""
    
    # Signals for panel events
    panel_switched = pyqtSignal(str)  # panel_name
    panel_added = pyqtSignal(str, QWidget)  # panel_name, widget
    panel_removed = pyqtSignal(str)  # panel_name
    panel_error = pyqtSignal(str, str)  # panel_name, error
    
    def __init__(self, stacked_widget: QStackedWidget, parent=None):
        """Initialize the panel controller."""
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.main_window = parent
        
        # Panel registry
        self.panels = {}
        self.panel_order = []
        self.current_panel = None
        
        # Panel creation callbacks
        self.panel_factories = {}
        
        # Initialize with placeholder panels
        self._register_default_panels()
    
    def _register_default_panels(self):
        """Register default panel factories."""
        try:
            # Register panel factories with lazy loading
            self.panel_factories.update({
                "dashboard": self._create_dashboard_panel,
                "conversations": self._create_conversations_panel,
                "analytics": self._create_analytics_panel,
                "ai_studio": self._create_ai_studio_panel,
                "templates": self._create_templates_panel,
                "mmorpg": self._create_mmorpg_panel,
                "training": self._create_training_panel,
                "weaponization": self._create_weaponization_panel,
                "exports": self._create_exports_panel,
                "scraper": self._create_scraper_panel,
                "devlog": self._create_devlog_panel,
                "workflow": self._create_workflow_panel,
                "voice": self._create_voice_panel,
                "gamification": self._create_gamification_panel,
                "skills": self._create_skills_panel
            })
            
            logger.info(f"Registered {len(self.panel_factories)} panel factories")
            
        except Exception as e:
            logger.error(f"Failed to register default panels: {e}")
    
    def add_panel(self, panel_name: str, widget: QWidget, add_to_stack: bool = True):
        """Add a panel to the controller."""
        try:
            # Store panel reference
            self.panels[panel_name] = widget
            
            # Add to order if not present
            if panel_name not in self.panel_order:
                self.panel_order.append(panel_name)
            
            # Add to stacked widget
            if add_to_stack:
                self.stacked_widget.addWidget(widget)
            
            self.panel_added.emit(panel_name, widget)
            logger.debug(f"Added panel: {panel_name}")
            
        except Exception as e:
            logger.error(f"Failed to add panel {panel_name}: {e}")
            self.panel_error.emit(panel_name, str(e))
    
    def remove_panel(self, panel_name: str):
        """Remove a panel from the controller."""
        try:
            if panel_name in self.panels:
                widget = self.panels.pop(panel_name)
                
                # Remove from order
                if panel_name in self.panel_order:
                    self.panel_order.remove(panel_name)
                
                # Remove from stacked widget
                self.stacked_widget.removeWidget(widget)
                
                self.panel_removed.emit(panel_name)
                logger.debug(f"Removed panel: {panel_name}")
            
        except Exception as e:
            logger.error(f"Failed to remove panel {panel_name}: {e}")
            self.panel_error.emit(panel_name, str(e))
    
    def switch_panel(self, panel_name: str):
        """Switch to a specific panel."""
        try:
            # Get or create panel
            panel = self.get_panel(panel_name)
            
            if panel:
                # Set current widget in stack
                self.stacked_widget.setCurrentWidget(panel)
                self.current_panel = panel_name
                
                # Refresh panel if it has refresh method
                if hasattr(panel, 'refresh_data'):
                    try:
                        panel.refresh_data()
                    except Exception as e:
                        logger.warning(f"Failed to refresh panel {panel_name}: {e}")
                
                self.panel_switched.emit(panel_name)
                logger.debug(f"Switched to panel: {panel_name}")
            else:
                logger.error(f"Panel not found: {panel_name}")
                
        except Exception as e:
            logger.error(f"Failed to switch to panel {panel_name}: {e}")
            self.panel_error.emit(panel_name, str(e))
    
    def get_panel(self, panel_name: str) -> Optional[QWidget]:
        """Get a panel, creating it if necessary."""
        try:
            # Return existing panel
            if panel_name in self.panels:
                return self.panels[panel_name]
            
            # Create panel using factory
            if panel_name in self.panel_factories:
                panel = self.panel_factories[panel_name]()
                if panel:
                    self.add_panel(panel_name, panel)
                    return panel
            
            # Create placeholder panel
            logger.warning(f"No factory for panel {panel_name}, creating placeholder")
            panel = self._create_placeholder_panel(panel_name)
            self.add_panel(panel_name, panel)
            return panel
            
        except Exception as e:
            logger.error(f"Failed to get panel {panel_name}: {e}")
            self.panel_error.emit(panel_name, str(e))
            return None
    
    def _create_placeholder_panel(self, panel_name: str) -> QWidget:
        """Create a placeholder panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = panel_name.replace('_', ' ').title()
        label = QLabel(f"🚧 {title} Panel\n\nThis panel is under development.")
        label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 16px;
                text-align: center;
                padding: 40px;
                border: 2px dashed #444444;
                border-radius: 8px;
                background-color: #1a1a1a;
            }
        """)
        
        layout.addWidget(label)
        return widget
    
    # Panel factory methods (lazy loading)
    def _create_dashboard_panel(self) -> Optional[QWidget]:
        """Create dashboard panel."""
        try:
            from gui.panels.dashboard_panel import DashboardPanel
            return DashboardPanel()
        except ImportError as e:
            logger.warning(f"Dashboard panel not available: {e}")
            return None
    
    def _create_conversations_panel(self) -> Optional[QWidget]:
        """Create conversations panel."""
        try:
            from gui.panels.conversations_panel import ConversationsPanel
            return ConversationsPanel()
        except ImportError as e:
            logger.warning(f"Conversations panel not available: {e}")
            return None
    
    def _create_analytics_panel(self) -> Optional[QWidget]:
        """Create analytics panel."""
        try:
            from gui.panels.consolidated_analytics_export_panel import AnalyticsExportPanel
            return AnalyticsExportPanel()
        except ImportError as e:
            logger.warning(f"Analytics panel not available: {e}")
            return None
    
    def _create_ai_studio_panel(self) -> Optional[QWidget]:
        """Create AI studio panel."""
        try:
            from gui.panels.consolidated_ai_studio_panel import AIStudioPanel
            return AIStudioPanel()
        except ImportError as e:
            logger.warning(f"AI Studio panel not available: {e}")
            return None
    
    def _create_templates_panel(self) -> Optional[QWidget]:
        """Create templates panel."""
        try:
            from gui.panels.community_templates_panel import CommunityTemplatesPanel
            return CommunityTemplatesPanel()
        except ImportError as e:
            logger.warning(f"Templates panel not available: {e}")
            return None
    
    def _create_mmorpg_panel(self) -> Optional[QWidget]:
        """Create MMORPG panel."""
        try:
            from gui.panels.resume_panel import ResumePanel
            return ResumePanel()
        except ImportError as e:
            logger.warning(f"MMORPG panel not available: {e}")
            return None
    
    def _create_training_panel(self) -> Optional[QWidget]:
        """Create training panel."""
        try:
            from gui.panels.ai_agent_training_panel import AIAgentTrainingPanel
            return AIAgentTrainingPanel()
        except ImportError as e:
            logger.warning(f"Training panel not available: {e}")
            return None
    
    def _create_weaponization_panel(self) -> Optional[QWidget]:
        """Create weaponization panel."""
        try:
            from gui.panels.consolidated_memory_weaponization_panel import MemoryWeaponizationPanel
            return MemoryWeaponizationPanel()
        except ImportError as e:
            logger.warning(f"Weaponization panel not available: {e}")
            return None
    
    def _create_exports_panel(self) -> Optional[QWidget]:
        """Create exports panel."""
        try:
            from gui.panels.enhanced_analytics_panel import EnhancedAnalyticsPanel
            return EnhancedAnalyticsPanel()
        except ImportError as e:
            logger.warning(f"Exports panel not available: {e}")
            return None
    
    def _create_scraper_panel(self) -> Optional[QWidget]:
        """Create scraper panel."""
        try:
            from gui.panels.scraper_panel import ScraperPanel
            return ScraperPanel()
        except ImportError as e:
            logger.warning(f"Scraper panel not available: {e}")
            return None
    
    def _create_devlog_panel(self) -> Optional[QWidget]:
        """Create devlog panel."""
        try:
            from gui.panels.enhanced_devlog_panel import EnhancedDevlogPanel
            return EnhancedDevlogPanel()
        except ImportError as e:
            logger.warning(f"Devlog panel not available: {e}")
            return None
    
    def _create_workflow_panel(self) -> Optional[QWidget]:
        """Create workflow panel."""
        try:
            from gui.panels.workflow_panel import WorkflowPanel
            return WorkflowPanel()
        except ImportError as e:
            logger.warning(f"Workflow panel not available: {e}")
            return None
    
    def _create_voice_panel(self) -> Optional[QWidget]:
        """Create voice panel."""
        try:
            from gui.panels.voice_modeling_panel import VoiceModelingPanel
            return VoiceModelingPanel()
        except ImportError as e:
            logger.warning(f"Voice panel not available: {e}")
            return None
    
    def _create_gamification_panel(self) -> Optional[QWidget]:
        """Create gamification panel."""
        try:
            from gui.panels.gamification_panel import GamificationPanel
            return GamificationPanel()
        except ImportError as e:
            logger.warning(f"Gamification panel not available: {e}")
            return None
    
    def _create_skills_panel(self) -> Optional[QWidget]:
        """Create skills panel."""
        try:
            from gui.panels.skill_tree_panel import SkillTreePanel
            return SkillTreePanel()
        except ImportError as e:
            logger.warning(f"Skills panel not available: {e}")
            return None
    
    def get_panel_list(self) -> list:
        """Get list of available panels."""
        return self.panel_order.copy()
    
    def get_current_panel(self) -> Optional[str]:
        """Get current panel name."""
        return self.current_panel
    
    def refresh_current_panel(self):
        """Refresh the current panel."""
        if self.current_panel and self.current_panel in self.panels:
            panel = self.panels[self.current_panel]
            if hasattr(panel, 'refresh_data'):
                try:
                    panel.refresh_data()
                    logger.debug(f"Refreshed panel: {self.current_panel}")
                except Exception as e:
                    logger.error(f"Failed to refresh panel {self.current_panel}: {e}")
    
    def refresh_all_panels(self):
        """Refresh all loaded panels."""
        for panel_name, panel in self.panels.items():
            if hasattr(panel, 'refresh_data'):
                try:
                    panel.refresh_data()
                    logger.debug(f"Refreshed panel: {panel_name}")
                except Exception as e:
                    logger.error(f"Failed to refresh panel {panel_name}: {e}")
    
    def get_panel_stats(self) -> Dict[str, Any]:
        """Get panel statistics."""
        return {
            "total_panels": len(self.panel_factories),
            "loaded_panels": len(self.panels),
            "current_panel": self.current_panel,
            "panel_order": self.panel_order.copy(),
            "available_panels": list(self.panel_factories.keys())
        }

