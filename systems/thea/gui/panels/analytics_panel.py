"""
from gui.debug_handler import debug_button
Analytics Panel for Thea GUI
Displays analytics and statistics about conversations and usage.
"""

from gui.debug_handler import debug_button
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QProgressBar, QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict

class AnalyticsPanel(QWidget):
    """Panel for displaying analytics and statistics."""
    
    # Signals
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the analytics UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Main content
        self.create_main_content(layout)
        
        # Detailed analytics
        self.create_detailed_analytics(layout)
    
    @debug_button("create_header", "Analytics Panel")
    def create_header(self):
        """Create panel header using shared components."""
        try:
            from gui.components.shared_components import SharedComponents
            
            components = SharedComponents()
            
            # Create header with title and icon
            header_widget = components.create_panel_header(
                title="Analytics",
                icon="📊",
                show_refresh_button=True,
                refresh_callback=self.refresh_data
            )
            
            return header_widget
            
        except Exception as e:
            logger.error(f"Error creating panel header: {e}")
            return QWidget()  # Fallback widget

    def create_main_content(self, parent_layout):
        """Create the main content area."""
        content_layout = QHBoxLayout()
        # Overview stats
        self.create_overview_stats(content_layout)
        # Usage trends
        self.create_usage_trends(content_layout)
        parent_layout.addLayout(content_layout)

    @debug_button("create_overview_stats", "Analytics Panel")
    def create_overview_stats(self):
        """Create statistics grid using shared components."""
        try:
            from gui.components.shared_components import SharedComponents
            components = SharedComponents()
            stats_data = {
                "Total": 0,
                "Active": 0,
                "Completed": 0
            }
            stats_widget = components.create_statistics_grid(
                stats_data=stats_data,
                title="analytics_panel Statistics",
                style="modern"
            )
            return stats_widget
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def create_usage_trends(self, parent_layout):
        """Create the usage trends section."""
        trends_group = QGroupBox("Usage Trends")
        trends_layout = QVBoxLayout(trends_group)
        # Daily activity
        daily_label = QLabel("Daily Activity")
        daily_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trends_layout.addWidget(daily_label)
        self.daily_progress = QProgressBar()
        self.daily_progress.setRange(0, 100)
        self.daily_progress.setValue(0)
        self.daily_progress.setFormat("Today: %v conversations")
        trends_layout.addWidget(self.daily_progress)
        # Weekly activity
        weekly_label = QLabel("Weekly Activity")
        weekly_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trends_layout.addWidget(weekly_label)
        self.weekly_progress = QProgressBar()
        self.weekly_progress.setRange(0, 100)
        self.weekly_progress.setValue(0)
        self.weekly_progress.setFormat("This week: %v conversations")
        trends_layout.addWidget(self.weekly_progress)
        # Monthly activity
        monthly_label = QLabel("Monthly Activity")
        monthly_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        trends_layout.addWidget(monthly_label)
        self.monthly_progress = QProgressBar()
        self.monthly_progress.setRange(0, 100)
        self.monthly_progress.setValue(0)
        self.monthly_progress.setFormat("This month: %v conversations")
        trends_layout.addWidget(self.monthly_progress)
        parent_layout.addWidget(trends_group)
    
    @debug_button("create_detailed_analytics", "Analytics Panel")
    def create_detailed_analytics(self, parent_layout):
        """Create the detailed analytics section."""
        detailed_group = QGroupBox("Detailed Analytics")
        detailed_layout = QVBoxLayout(detailed_group)
        
        # Model usage table
        model_label = QLabel("Model Usage")
        model_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        detailed_layout.addWidget(model_label)
        
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(3)
        self.model_table.setHorizontalHeaderLabels([
            "Model", "Conversations", "Percentage"
        ])
        
        # Configure table
        header = self.model_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.model_table.setAlternatingRowColors(True)
        detailed_layout.addWidget(self.model_table)
        
        # Top topics
        topics_label = QLabel("Top Conversation Topics")
        topics_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        detailed_layout.addWidget(topics_label)
        
        self.topics_table = QTableWidget()
        self.topics_table.setColumnCount(3)
        self.topics_table.setHorizontalHeaderLabels([
            "Topic", "Frequency", "Last Used"
        ])
        
        # Configure table
        header = self.topics_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.topics_table.setAlternatingRowColors(True)
        detailed_layout.addWidget(self.topics_table)
        
        parent_layout.addWidget(detailed_group)
    
    @debug_button("update_overview_stats", "Analytics Panel")
    def update_overview_stats(self):
        """Create statistics grid using shared components."""
        try:
            from gui.components.shared_components import SharedComponents
            components = SharedComponents()
            stats_data = {
                "Total": 0,
                "Active": 0,
                "Completed": 0
            }
            stats_widget = components.create_statistics_grid(
                stats_data=stats_data,
                title="analytics_panel Statistics",
                style="modern"
            )
            return stats_widget
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    @debug_button("refresh_data", "Analytics Panel")
    def refresh_data(self):
        """Refresh analytics data."""
        try:
            logger.info("Refreshing analytics data...")
            # Emit refresh signal
            self.refresh_requested.emit()
            # Update overview stats
            self.update_overview_stats()
            logger.info("Analytics data refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing analytics data: {e}")

    def update_usage_trends(self, trends: Dict):
        """Update the usage trends."""
        # Update progress bars
        daily_conv = trends.get('daily_conversations', 0)
        weekly_conv = trends.get('weekly_conversations', 0)
        monthly_conv = trends.get('monthly_conversations', 0)
        # Set reasonable max values
        self.daily_progress.setMaximum(max(daily_conv * 2, 10))
        self.weekly_progress.setMaximum(max(weekly_conv * 2, 50))
        self.monthly_progress.setMaximum(max(monthly_conv * 2, 200))
        self.daily_progress.setValue(daily_conv)
        self.weekly_progress.setValue(weekly_conv)
        self.monthly_progress.setValue(monthly_conv)
    
    @debug_button("update_model_usage", "Analytics Panel")
    def update_model_usage(self, model_usage: List[Dict]):
        """Update the model usage table."""
        self.model_table.setRowCount(0)
        
        if not model_usage:
            return
        
        total_conv = sum(usage.get('conversations', 0) for usage in model_usage)
        
        for usage in model_usage:
            row = self.model_table.rowCount()
            self.model_table.insertRow(row)
            
            model = usage.get('model', 'Unknown')
            conversations = usage.get('conversations', 0)
            percentage = (conversations / total_conv * 100) if total_conv > 0 else 0
            
            self.model_table.setItem(row, 0, QTableWidgetItem(model))
            self.model_table.setItem(row, 1, QTableWidgetItem(str(conversations)))
            self.model_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))
    
    @debug_button("update_topics", "Analytics Panel")
    def update_topics(self, topics: List[Dict]):
        """Update the topics table."""
        self.topics_table.setRowCount(0)
        
        for topic in topics:
            row = self.topics_table.rowCount()
            self.topics_table.insertRow(row)
            
            self.topics_table.setItem(row, 0, QTableWidgetItem(topic.get('topic', 'Unknown')))
            self.topics_table.setItem(row, 1, QTableWidgetItem(str(topic.get('frequency', 0))))
            self.topics_table.setItem(row, 2, QTableWidgetItem(topic.get('last_used', 'Unknown')))
    
    @debug_button("on_period_changed", "Analytics Panel")
    def on_period_changed(self, period: str):
        """Handle time period change."""
        # This would trigger a refresh with the new period
        self.refresh_requested.emit()
    
    def get_selected_period(self) -> str:
        """Get the currently selected time period."""
        return self.period_combo.currentText()
    
    @debug_button("update_overview", "Analytics Panel")
    def update_overview(self):
        """Create statistics grid using shared components."""
        try:
            from gui.components.shared_components import SharedComponents
            
            components = SharedComponents()
            
            # Create statistics grid with panel-specific data
            stats_data = {
                "Total": 0,
                "Active": 0,
                "Completed": 0
            }
            
            stats_widget = components.create_statistics_grid(
                stats_data=stats_data,
                title="analytics_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
