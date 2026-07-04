"""
Enhanced Devlog Panel - Refactored Modular Version
=================================================

Simplified version of the original enhanced_devlog_panel.py (~960 lines)
focused on workflow-driven devlog generation.
"""

import logging
from PyQt6.QtWidgets import QTabWidget
from typing import Dict, Any

from gui.base.workflow_base import WorkflowBase
from gui.base.data_panel_base import DataPanelBase

logger = logging.getLogger(__name__)


class EnhancedDevlogPanelRefactored(WorkflowBase, DataPanelBase):
    """Refactored Devlog Panel using workflow and data base classes."""

    def __init__(self):
        WorkflowBase.__init__(
            self,
            title="📝 Devlog Generator",
            description="Generate devlogs from workflow activity.",
        )
        DataPanelBase.__init__(
            self,
            title="Devlog Data",
            description="Data sources for devlog generation.",
        )
        self.init_ui()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_workflow_tab("Devlog Workflows"), "Workflows")
        self.tab_widget.addTab(self.create_data_tab("Data"), "Data")
        self.layout().addWidget(self.tab_widget)

    def get_panel_summary(self) -> Dict[str, Any]:
        return {
            "workflows": len(self.workflow_history),
            "records": len(self.data_records),
        }
