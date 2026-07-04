"""
Community Templates Panel - Refactored Modular Version
=====================================================

This refactored panel demonstrates how the original community_templates_panel.py
(about 1,000 lines) can be replaced with a much smaller implementation using the
shared base classes. It focuses on basic template management and workflows.
"""

import logging
from typing import Dict, Any
from PyQt6.QtWidgets import QTabWidget

from gui.base.data_panel_base import DataPanelBase
from gui.base.workflow_base import WorkflowBase

logger = logging.getLogger(__name__)


class CommunityTemplatesPanelRefactored(DataPanelBase, WorkflowBase):
    """Refactored Community Templates Panel using base classes."""

    def __init__(self):
        DataPanelBase.__init__(
            self,
            title="🌐 Community Templates",
            description="Browse, share, and manage community templates.",
        )
        WorkflowBase.__init__(
            self,
            title="Template Workflows",
            description="Automation and publishing workflows",
        )

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Create the main UI with basic tabs."""
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_data_tab("Marketplace"), "Marketplace")
        self.tab_widget.addTab(self.create_data_tab("My Templates"), "My Templates")
        self.tab_widget.addTab(self.create_workflow_tab("Workflows"), "Workflows")
        self.layout().addWidget(self.tab_widget)

    def get_panel_summary(self) -> Dict[str, Any]:
        """Return a simple summary of templates and workflows."""
        return {
            "templates": len(self.data_records),
            "workflows": len(self.workflow_history),
        }
