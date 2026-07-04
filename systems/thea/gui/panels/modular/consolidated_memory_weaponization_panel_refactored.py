"""
Consolidated Memory Weaponization Panel - Refactored
===================================================

A minimal modular implementation replacing the original
consolidated_memory_weaponization_panel.py (~900 lines).
It combines data management with analytics of weaponization metrics.
"""

import logging
from PyQt6.QtWidgets import QTabWidget
from typing import Dict, Any

from gui.base.data_panel_base import DataPanelBase
from gui.base.analytics_base import AnalyticsBase

logger = logging.getLogger(__name__)


class MemoryWeaponizationPanelRefactored(DataPanelBase, AnalyticsBase):
    """Refactored Memory Weaponization Panel using base classes."""

    def __init__(self):
        DataPanelBase.__init__(self, title="💣 Memory Weaponization", description="Manage memory weaponization data")
        AnalyticsBase.__init__(self, title="Weaponization Analytics", description="Analytics for memory weaponization")
        self.init_ui()
        self.load_data()
        self.load_analytics_data()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_data_tab("Weaponization Data"), "Data")
        self.tab_widget.addTab(self.create_analytics_tab("Analytics"), "Analytics")
        self.layout().addWidget(self.tab_widget)

    def get_panel_summary(self) -> Dict[str, Any]:
        return {
            "records": len(self.data_records),
            "analytics": self.get_analytics_summary(),
        }
