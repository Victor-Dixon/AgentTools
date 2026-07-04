"""
Consolidated AI Studio Panel - Refactored Modular Version
=======================================================

This is a refactored version of the original consolidated_ai_studio_panel.py
that inherits from the new base classes to demonstrate the modular structure.

The original file was 982 lines. This refactored version is much smaller and
more maintainable by leveraging the base classes.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QTabWidget

# Import base classes
from gui.base.ai_studio_base import AIStudioBase
from gui.base.data_panel_base import DataPanelBase
from gui.base.workflow_base import WorkflowBase
from gui.base.analytics_base import AnalyticsBase

# Import core systems
from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from dreamscape.core.mmorpg.mmorpg_system import EnhancedProgressSystem

logger = logging.getLogger(__name__)


class AIStudioPanelRefactored(AIStudioBase, DataPanelBase, WorkflowBase, AnalyticsBase):
    """Refactored Consolidated AI Studio Panel using modular base classes."""

    def __init__(self, memory_manager: MemoryManager = None, mmorpg_engine: MMORPGEngine = None):
        # Initialize all base classes
        AIStudioBase.__init__(
            self,
            title="🤖 AI Studio - Modular Version",
            description="Unified AI workflows, training, data management and analytics."
        )
        DataPanelBase.__init__(self, title="Training Data", description="Manage training data")
        WorkflowBase.__init__(self, title="Workflows", description="Automation and devlog workflows")
        AnalyticsBase.__init__(self, title="AI Analytics", description="View AI performance metrics")

        # Core systems
        self.memory_manager = memory_manager or MemoryManager()
        self.mmorpg_engine = mmorpg_engine or MMORPGEngine()
        self.enhanced_progress = EnhancedProgressSystem(self.mmorpg_engine, self.memory_manager)

        # Initialize the panel
        self.init_ui()
        self.load_data()
        self.load_analytics_data()

    def init_ui(self):
        """Initialize the user interface using base class functionality."""
        self.tab_widget = QTabWidget()

        # Core AI features from AIStudioBase
        self.tab_widget.addTab(self.create_chat_tab("Conversational AI"), "Conversational AI")
        self.tab_widget.addTab(self.create_training_tab("Agent Training"), "Agent Training")
        self.tab_widget.addTab(self.create_analysis_tab("AI Analysis"), "AI Analysis")

        # Data management from DataPanelBase
        self.tab_widget.addTab(self.create_data_tab("Training Data"), "Training Data")

        # Analytics and workflow tabs
        self.tab_widget.addTab(self.create_analytics_tab("AI Analytics"), "AI Analytics")
        self.tab_widget.addTab(self.create_workflow_tab("Workflows"), "Workflows")

        # Add tab widget to the main layout
        self.layout().addWidget(self.tab_widget)

    def get_panel_summary(self) -> Dict[str, Any]:
        """Return a high-level summary of panel state."""
        return {
            "conversations": len(self.current_conversation),
            "models": len(self.ai_models),
            "training_data": len(self.data_records),
            "workflows": len(self.workflow_history),
            "analytics": self.get_analytics_summary(),
        }
