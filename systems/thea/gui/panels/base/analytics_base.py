"""
Analytics Base - Common Analytics Panel Functionality
===================================================

This module provides the base class for analytics panels with common
functionality like data visualization, chart management, and analytics
processing.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QComboBox,
    QSpinBox, QCheckBox, QSplitter, QFrame, QScrollArea,
    QGridLayout, QListWidget, QListWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from gui.base_panel import BasePanel

logger = logging.getLogger(__name__)


class AnalyticsBase(BasePanel):
    """Base class for analytics panels with common analytics functionality."""
    
    # Analytics-specific signals
    analytics_updated = pyqtSignal(dict)      # Analytics data updated
    chart_updated = pyqtSignal(str, dict)     # Chart updated (chart_type, data)
    insight_detected = pyqtSignal(dict)       # New insight detected
    trend_identified = pyqtSignal(dict)       # Trend identified
    
    def __init__(self, title: str = "Analytics Panel", description: str = "", parent=None):
        """Initialize the analytics base panel."""
        super().__init__(title, description, parent)
        
        # Analytics state
        self.analytics_data = {}
        self.charts = {}
        self.insights = []
        self.trends = []
        self.metrics = {}
        
        # Analytics components
        self.metrics_table = None
        self.insights_list = None
        self.trends_list = None
        self.chart_selector = None
        
        # Analytics settings
        self.refresh_interval = 30000  # 30 seconds
        self.auto_refresh = False
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_analytics)
        
        # Initialize analytics UI
        self.setup_analytics_ui()
    
    def setup_analytics_ui(self):
        """Setup analytics-specific UI components."""
        # Create metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(3)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value", "Change"])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        
        # Create insights list
        self.insights_list = QListWidget()
        
        # Create trends list
        self.trends_list = QListWidget()
        
        # Create chart selector
        self.chart_selector = QComboBox()
        self.chart_selector.addItems(["Overview", "Performance", "Trends", "Breakdown"])
        self.chart_selector.currentTextChanged.connect(self.on_chart_selection_changed)
    
    def create_analytics_tab(self, title: str = "Analytics") -> QWidget:
        """Create a standard analytics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Chart selector
        chart_controls = QHBoxLayout()
        chart_controls.addWidget(QLabel("Chart Type:"))
        chart_controls.addWidget(self.chart_selector)
        chart_controls.addStretch()
        layout.addLayout(chart_controls)
        
        # Chart area
        chart_group = QGroupBox("Chart")
        chart_layout = QVBoxLayout(chart_group)
        self.chart_area = QLabel("Chart will be displayed here")
        self.chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_area.setMinimumHeight(300)
        chart_layout.addWidget(self.chart_area)
        layout.addWidget(chart_group)
        
        # Metrics and insights splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Metrics panel
        metrics_panel = self.create_metrics_panel()
        splitter.addWidget(metrics_panel)
        
        # Insights panel
        insights_panel = self.create_insights_panel()
        splitter.addWidget(insights_panel)
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_metrics_panel(self) -> QWidget:
        """Create the metrics display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Metrics header
        header = QLabel("📊 Key Metrics")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Metrics table
        layout.addWidget(self.metrics_table)
        
        return panel
    
    def create_insights_panel(self) -> QWidget:
        """Create the insights display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Insights header
        header = QLabel("💡 Insights")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Insights list
        layout.addWidget(self.insights_list)
        
        return panel
    
    def create_trends_panel(self) -> QWidget:
        """Create the trends display panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Trends header
        header = QLabel("📈 Trends")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Trends list
        layout.addWidget(self.trends_list)
        
        return panel
    
    def load_analytics_data(self):
        """Load analytics data. Override in subclasses."""
        logger.info(f"Loading analytics data for {self.panel_name}")
        
        # Simulate loading analytics data
        self.analytics_data = {
            "total_conversations": 150,
            "total_messages": 2500,
            "avg_response_time": 2.5,
            "engagement_rate": 0.85,
            "satisfaction_score": 4.2
        }
        
        self.update_metrics_display()
        self.analytics_updated.emit(self.analytics_data)
    
    def update_metrics_display(self):
        """Update the metrics table display."""
        if not self.metrics_table:
            return
        
        self.metrics_table.setRowCount(len(self.analytics_data))
        
        for i, (metric, value) in enumerate(self.analytics_data.items()):
            # Metric name
            name_item = QTableWidgetItem(metric.replace("_", " ").title())
            self.metrics_table.setItem(i, 0, name_item)
            
            # Value
            value_item = QTableWidgetItem(str(value))
            self.metrics_table.setItem(i, 1, value_item)
            
            # Change (placeholder)
            change_item = QTableWidgetItem("+0%")
            change_item.setForeground(Qt.GlobalColor.green)
            self.metrics_table.setItem(i, 2, change_item)
    
    def add_insight(self, insight: Dict[str, Any]):
        """Add an insight to the insights list."""
        if not self.insights_list:
            return
        
        insight_text = f"💡 {insight.get('title', 'Insight')}: {insight.get('description', '')}"
        item = QListWidgetItem(insight_text)
        item.setData(Qt.ItemDataRole.UserRole, insight)
        self.insights_list.addItem(item)
        
        self.insights.append(insight)
        self.insight_detected.emit(insight)
    
    def add_trend(self, trend: Dict[str, Any]):
        """Add a trend to the trends list."""
        if not self.trends_list:
            return
        
        trend_text = f"📈 {trend.get('title', 'Trend')}: {trend.get('description', '')}"
        item = QListWidgetItem(trend_text)
        item.setData(Qt.ItemDataRole.UserRole, trend)
        self.trends_list.addItem(item)
        
        self.trends.append(trend)
        self.trend_identified.emit(trend)
    
    def update_chart(self, chart_type: str, data: Dict[str, Any]):
        """Update a chart with new data."""
        self.charts[chart_type] = data
        self.chart_updated.emit(chart_type, data)
        
        # Update chart display if this is the current chart
        if self.chart_selector and self.chart_selector.currentText() == chart_type:
            self.display_chart(chart_type, data)
    
    def display_chart(self, chart_type: str, data: Dict[str, Any]):
        """Display a chart. Override in subclasses for actual chart rendering."""
        if hasattr(self, 'chart_area'):
            self.chart_area.setText(f"Chart: {chart_type}\nData: {json.dumps(data, indent=2)}")
    
    def on_chart_selection_changed(self, chart_type: str):
        """Handle chart selection change."""
        if chart_type in self.charts:
            self.display_chart(chart_type, self.charts[chart_type])
    
    def start_auto_refresh(self, interval: int = None):
        """Start automatic refresh of analytics data."""
        if interval:
            self.refresh_interval = interval
        
        self.auto_refresh = True
        self.refresh_timer.start(self.refresh_interval)
        self.set_status("Auto-refresh started")
    
    def stop_auto_refresh(self):
        """Stop automatic refresh of analytics data."""
        self.auto_refresh = False
        self.refresh_timer.stop()
        self.set_status("Auto-refresh stopped")
    
    def auto_refresh_analytics(self):
        """Automatically refresh analytics data."""
        if self.auto_refresh:
            self.load_analytics_data()
    
    def export_analytics(self, format: str = "json"):
        """Export analytics data."""
        try:
            export_data = {
                "analytics_data": self.analytics_data,
                "insights": self.insights,
                "trends": self.trends,
                "charts": self.charts,
                "exported_at": datetime.now().isoformat()
            }
            
            if format == "json":
                return json.dumps(export_data, indent=2)
            else:
                # Add other export formats as needed
                return str(export_data)
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            return None
    
    def clear_analytics(self):
        """Clear all analytics data."""
        self.analytics_data.clear()
        self.insights.clear()
        self.trends.clear()
        self.charts.clear()
        
        if self.metrics_table:
            self.metrics_table.setRowCount(0)
        if self.insights_list:
            self.insights_list.clear()
        if self.trends_list:
            self.trends_list.clear()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a summary of analytics data."""
        return {
            "total_metrics": len(self.analytics_data),
            "total_insights": len(self.insights),
            "total_trends": len(self.trends),
            "total_charts": len(self.charts),
            "last_updated": datetime.now().isoformat()
        } 