"""
Content Analytics Panel - Refactored Modular Version
===================================================

Simplified replacement for content_analytics_panel.py (~900 lines) using
AnalyticsBase and DataPanelBase for content analysis and management.
"""

import logging
from PyQt6.QtWidgets import QTabWidget
from typing import Dict, Any

from gui.base.analytics_base import AnalyticsBase
from gui.base.data_panel_base import DataPanelBase

logger = logging.getLogger(__name__)


class ContentAnalyticsPanelRefactored(AnalyticsBase, DataPanelBase):
    """Refactored Content Analytics Panel using base classes."""

    def __init__(self):
        AnalyticsBase.__init__(self, title="📰 Content Analytics", description="Analyze generated content")
        DataPanelBase.__init__(self, title="Content Data", description="Data used for analytics")
        self.init_ui()
        self.load_data()
        self.load_analytics_data()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_analytics_tab("Content Metrics"), "Metrics")
        self.tab_widget.addTab(self.create_data_tab("Content Data"), "Data")
        self.layout().addWidget(self.tab_widget)

    def get_panel_summary(self) -> Dict[str, Any]:
        return {
            "records": len(self.data_records),
            "analytics": self.get_analytics_summary(),
        }
