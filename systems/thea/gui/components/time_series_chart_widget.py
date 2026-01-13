#!/usr/bin/env python3
"""
Time Series Chart Widget - GUI component for time-series visualization
=====================================================================

Provides an interactive time-series chart widget that displays:
- Line charts for various metrics over time
- Multiple time periods (daily, weekly, monthly)
- Interactive tooltips and zoom functionality
- Export capabilities
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QSizePolicy, QToolTip, QMenu,
    QSlider, QSpinBox, QComboBox, QGroupBox, QFormLayout, QTabWidget
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPixmap, QIcon

from dreamscape.core.time_series_analyzer import TimeSeriesAnalyzer
from dreamscape.core.export_manager import ExportManager

logger = logging.getLogger(__name__)


class TimeSeriesChartWidget(QWidget):
    """Interactive time-series chart widget for visualizing data over time."""
    
    # Signals
    data_point_selected = pyqtSignal(dict)  # Selected data point
    export_requested = pyqtSignal(str, str)  # format, file_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.export_manager = ExportManager()
        
        # Chart data
        self.time_series_data = []
        self.chart_data = {}
        self.trends = {}
        self.selected_point = None
        
        # Display settings
        self.period = 'daily'
        self.days = 30
        self.metric = 'conversation_count'
        self.show_trends = True
        self.show_grid = True
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Controls
        self.create_controls(layout)
        
        # Chart display
        self.create_chart_display(layout)
        
        # Status bar
        self.create_status_bar(layout)
        
    def create_header(self, layout):
        """Create the header section."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title = QLabel("📈 Time Series Chart")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_chart)
        header_layout.addWidget(self.refresh_btn)
        
        # Export button
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.show_export_menu)
        header_layout.addWidget(self.export_btn)
        
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
    def create_controls(self, layout):
        """Create the control panel."""
        controls_group = QGroupBox("Chart Controls")
        controls_layout = QFormLayout(controls_group)
        
        # Time period
        self.period_combo = QComboBox()
        self.period_combo.addItems(['daily', 'weekly', 'monthly'])
        self.period_combo.setCurrentText(self.period)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        controls_layout.addRow("Time Period:", self.period_combo)
        
        # Days/weeks/months
        self.time_range_spin = QSpinBox()
        self.time_range_spin.setRange(7, 365)
        self.time_range_spin.setValue(self.days)
        self.time_range_spin.valueChanged.connect(self.on_time_range_changed)
        controls_layout.addRow("Time Range:", self.time_range_spin)
        
        # Metric selection
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(['conversation_count', 'total_messages', 'total_words'])
        self.metric_combo.setCurrentText(self.metric)
        self.metric_combo.currentTextChanged.connect(self.on_metric_changed)
        controls_layout.addRow("Metric:", self.metric_combo)
        
        # Display options
        self.show_trends_check = QComboBox()
        self.show_trends_check.addItems(['Show Trends', 'Hide Trends'])
        self.show_trends_check.setCurrentText('Show Trends' if self.show_trends else 'Hide Trends')
        self.show_trends_check.currentTextChanged.connect(self.on_show_trends_changed)
        controls_layout.addRow("Trends:", self.show_trends_check)
        
        layout.addWidget(controls_group)
        
    def create_chart_display(self, layout):
        """Create the chart display area."""
        # Tab widget for different chart types
        self.chart_tabs = QTabWidget()
        
        # Main chart tab
        self.main_chart_widget = TimeSeriesChartDisplayWidget()
        self.main_chart_widget.data_point_clicked.connect(self.on_data_point_clicked)
        self.chart_tabs.addTab(self.main_chart_widget, "Main Chart")
        
        # Trends tab
        self.trends_widget = TrendsDisplayWidget()
        self.chart_tabs.addTab(self.trends_widget, "Trends Analysis")
        
        # Statistics tab
        self.stats_widget = StatisticsDisplayWidget()
        self.chart_tabs.addTab(self.stats_widget, "Statistics")
        
        layout.addWidget(self.chart_tabs)
        
    def create_status_bar(self, layout):
        """Create the status bar."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Ready to display time series data")
        status_layout.addWidget(self.status_label)
        
        # Data points count
        self.data_points_label = QLabel("Data Points: 0")
        status_layout.addWidget(self.data_points_label)
        
        # Current metric value
        self.current_value_label = QLabel("Current Value: 0")
        status_layout.addWidget(self.current_value_label)
        
        status_layout.addStretch()
        layout.addWidget(status_frame)
        
    def set_conversations(self, conversations: List[Dict[str, Any]]):
        """Set conversations and generate time series data."""
        try:
            self.status_label.setText("Analyzing time series data...")
            
            # Get current settings
            period = self.period_combo.currentText()
            days = self.time_range_spin.value()
            
            # Generate time series data
            time_series_result = self.time_series_analyzer.get_conversation_time_series(
                conversations, 
                period=period, 
                days=days
            )
            
            self.time_series_data = time_series_result.get('time_series', [])
            self.chart_data = time_series_result.get('chart_data', {})
            self.trends = time_series_result.get('trends', {})
            
            # Update displays
            self.update_chart_displays()
            
            # Update status
            self.data_points_label.setText(f"Data Points: {len(self.time_series_data)}")
            if self.time_series_data:
                latest_value = self.time_series_data[-1].get(self.metric, 0)
                self.current_value_label.setText(f"Current Value: {latest_value}")
            
            self.status_label.setText("Time series chart updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to set conversations: {e}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def update_chart_displays(self):
        """Update all chart displays."""
        # Update main chart
        if self.chart_data:
            metric_data = self.chart_data.get(self.metric, {})
            self.main_chart_widget.set_chart_data(metric_data)
        
        # Update trends display
        if self.trends:
            self.trends_widget.set_trends(self.trends)
        
        # Update statistics display
        if self.time_series_data:
            self.stats_widget.set_statistics(self.time_series_data, self.metric)
    
    def on_period_changed(self, period):
        """Handle time period change."""
        self.period = period
        # Update time range label
        if period == 'daily':
            self.time_range_spin.setSuffix(" days")
        elif period == 'weekly':
            self.time_range_spin.setSuffix(" weeks")
        elif period == 'monthly':
            self.time_range_spin.setSuffix(" months")
    
    def on_time_range_changed(self, value):
        """Handle time range change."""
        self.days = value
    
    def on_metric_changed(self, metric):
        """Handle metric change."""
        self.metric = metric
        self.update_chart_displays()
    
    def on_show_trends_changed(self, text):
        """Handle show trends change."""
        self.show_trends = text == 'Show Trends'
        self.main_chart_widget.set_show_trends(self.show_trends)
    
    def on_data_point_clicked(self, data_point: Dict[str, Any]):
        """Handle data point click."""
        self.selected_point = data_point
        self.data_point_selected.emit(data_point)
        
        # Show tooltip with details
        tooltip_text = f"""
        <b>Date: {data_point.get('date', 'Unknown')}</b><br/>
        Value: {data_point.get('value', 0)}<br/>
        Metric: {self.metric}
        """
        QToolTip.showText(self.cursor().pos(), tooltip_text, self)
    
    def refresh_chart(self):
        """Refresh the chart."""
        self.update_chart_displays()
        self.status_label.setText("Chart refreshed")
    
    def show_export_menu(self):
        """Show export menu."""
        menu = QMenu(self)
        
        # CSV export
        csv_action = QAction("Export to CSV", self)
        csv_action.triggered.connect(lambda: self.export_data('csv'))
        menu.addAction(csv_action)
        
        # JSON export
        json_action = QAction("Export to JSON", self)
        json_action.triggered.connect(lambda: self.export_data('json'))
        menu.addAction(json_action)
        
        # PDF export
        pdf_action = QAction("Export to PDF", self)
        pdf_action.triggered.connect(lambda: self.export_data('pdf'))
        menu.addAction(pdf_action)
        
        menu.exec(self.export_btn.mapToGlobal(self.export_btn.rect().bottomLeft()))
    
    def export_data(self, format: str):
        """Export time series data to specified format."""
        if not self.time_series_data:
            self.status_label.setText("No data to export")
            return
        
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            # Get file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                f"Export Time Series ({format.upper()})", 
                f"time_series_export.{format}", 
                f"{format.upper()} Files (*.{format})"
            )
            
            if file_path:
                # Prepare export data
                export_data = {
                    'time_series_data': self.time_series_data,
                    'chart_data': self.chart_data,
                    'trends': self.trends,
                    'period': self.period,
                    'metric': self.metric,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Export
                self.export_manager.export_analytics_data(export_data, file_path, format)
                
                self.status_label.setText(f"Time series data exported to {format.upper()}")
                self.export_requested.emit(format, file_path)
                
        except Exception as e:
            logger.error(f"Failed to export time series data: {e}")
            self.status_label.setText(f"Export failed: {str(e)}")


class TimeSeriesChartDisplayWidget(QWidget):
    """Widget for displaying the actual time series chart."""
    
    # Signals
    data_point_clicked = pyqtSignal(dict)  # Clicked data point
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_data = {}
        self.show_trends = True
        self.data_points = []  # Store data point rectangles for click detection
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)
        
        # Enable mouse tracking for tooltips
        self.setMouseTracking(True)
        
    def set_chart_data(self, chart_data: Dict[str, Any]):
        """Set chart data to display."""
        self.chart_data = chart_data
        self.data_points.clear()
        self.update()
        
    def set_show_trends(self, show_trends: bool):
        """Set whether to show trends."""
        self.show_trends = show_trends
        self.update()
        
    def paintEvent(self, event):
        """Paint the time series chart."""
        if not self.chart_data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Calculate chart area (with margins)
        margin = 50
        chart_width = width - 2 * margin
        chart_height = height - 2 * margin
        
        if chart_width <= 0 or chart_height <= 0:
            return
        
        # Draw background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # Draw grid
        if self.show_trends:
            self.draw_grid(painter, margin, chart_width, chart_height)
        
        # Draw chart
        self.draw_chart(painter, margin, chart_width, chart_height)
        
        # Draw axes
        self.draw_axes(painter, margin, chart_width, chart_height)
        
        # Draw labels
        self.draw_labels(painter, margin, chart_width, chart_height)
    
    def draw_grid(self, painter: QPainter, margin: int, chart_width: int, chart_height: int):
        """Draw grid lines."""
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        
        # Vertical grid lines
        labels = self.chart_data.get('labels', [])
        if labels:
            for i, label in enumerate(labels):
                x = margin + (i / (len(labels) - 1)) * chart_width
                painter.drawLine(int(x), margin, int(x), margin + chart_height)
        
        # Horizontal grid lines
        data = self.chart_data.get('data', [])
        if data:
            max_value = max(data) if data else 1
            for i in range(5):
                y = margin + chart_height - (i / 4) * chart_height
                painter.drawLine(margin, int(y), margin + chart_width, int(y))
    
    def draw_chart(self, painter: QPainter, margin: int, chart_width: int, chart_height: int):
        """Draw the actual chart line."""
        labels = self.chart_data.get('labels', [])
        data = self.chart_data.get('data', [])
        
        if not labels or not data or len(labels) != len(data):
            return
        
        # Set up pen for line
        painter.setPen(QPen(QColor(0, 100, 200), 2))
        
        # Draw line
        points = []
        self.data_points.clear()
        
        for i, (label, value) in enumerate(zip(labels, data)):
            x = margin + (i / (len(labels) - 1)) * chart_width
            y = margin + chart_height - (value / max(data)) * chart_height
            
            points.append(QPoint(int(x), int(y)))
            
            # Store data point for click detection
            rect = QRect(int(x) - 5, int(y) - 5, 10, 10)
            self.data_points[rect] = {
                'label': label,
                'value': value,
                'index': i
            }
        
        # Draw line connecting points
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])
        
        # Draw data points
        painter.setBrush(QBrush(QColor(0, 100, 200)))
        for point in points:
            painter.drawEllipse(point, 3, 3)
    
    def draw_axes(self, painter: QPainter, margin: int, chart_width: int, chart_height: int):
        """Draw chart axes."""
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        
        # X-axis
        painter.drawLine(margin, margin + chart_height, margin + chart_width, margin + chart_height)
        
        # Y-axis
        painter.drawLine(margin, margin, margin, margin + chart_height)
    
    def draw_labels(self, painter: QPainter, margin: int, chart_width: int, chart_height: int):
        """Draw axis labels."""
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor(0, 0, 0)))
        
        # X-axis labels
        labels = self.chart_data.get('labels', [])
        if labels:
            for i, label in enumerate(labels):
                x = margin + (i / (len(labels) - 1)) * chart_width
                painter.drawText(int(x) - 20, margin + chart_height + 15, 40, 20, 
                               Qt.AlignmentFlag.AlignCenter, str(label))
        
        # Y-axis labels
        data = self.chart_data.get('data', [])
        if data:
            max_value = max(data) if data else 1
            for i in range(5):
                value = (i / 4) * max_value
                y = margin + chart_height - (i / 4) * chart_height
                painter.drawText(5, int(y) - 10, margin - 10, 20, 
                               Qt.AlignmentFlag.AlignRight, f"{value:.0f}")
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is on a data point
            for rect, data_point in self.data_points.items():
                if rect.contains(event.pos()):
                    self.data_point_clicked.emit(data_point)
                    break
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for tooltips."""
        # Check if mouse is over a data point
        for rect, data_point in self.data_points.items():
            if rect.contains(event.pos()):
                tooltip_text = f"{data_point.get('label', '')}: {data_point.get('value', 0)}"
                QToolTip.showText(event.globalPos(), tooltip_text, self)
                break


class TrendsDisplayWidget(QWidget):
    """Widget for displaying trend analysis."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trends = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Trend Analysis")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Trends display area
        self.trends_text = QLabel()
        self.trends_text.setWordWrap(True)
        self.trends_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.trends_text)
        
        layout.addStretch()
        
    def set_trends(self, trends: Dict[str, Any]):
        """Set trends data to display."""
        self.trends = trends
        
        # Format trends for display
        trends_text = ""
        for metric, trend_data in trends.items():
            trends_text += f"<b>{metric.replace('_', ' ').title()}:</b><br/>"
            trends_text += f"Trend: {trend_data.get('trend', 'Unknown')}<br/>"
            trends_text += f"Change: {trend_data.get('change_percentage', 0):.1f}%<br/>"
            trends_text += f"Growth Rate: {trend_data.get('growth_rate', 0):.4f}<br/>"
            trends_text += f"Volatility: {trend_data.get('volatility', 0):.2f}<br/>"
            trends_text += f"Average: {trend_data.get('average', 0):.2f}<br/><br/>"
        
        self.trends_text.setText(trends_text)


class StatisticsDisplayWidget(QWidget):
    """Widget for displaying statistics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.statistics = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Statistics")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Statistics display area
        self.stats_text = QLabel()
        self.stats_text.setWordWrap(True)
        self.stats_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.stats_text)
        
        layout.addStretch()
        
    def set_statistics(self, time_series_data: List[Dict[str, Any]], metric: str):
        """Set statistics data to display."""
        if not time_series_data:
            return
        
        # Calculate statistics
        values = [item.get(metric, 0) for item in time_series_data]
        
        if not values:
            return
        
        total = sum(values)
        average = total / len(values)
        min_value = min(values)
        max_value = max(values)
        
        # Format statistics for display
        stats_text = f"<b>Statistics for {metric.replace('_', ' ').title()}:</b><br/>"
        stats_text += f"Total: {total}<br/>"
        stats_text += f"Average: {average:.2f}<br/>"
        stats_text += f"Minimum: {min_value}<br/>"
        stats_text += f"Maximum: {max_value}<br/>"
        stats_text += f"Data Points: {len(values)}<br/>"
        
        self.stats_text.setText(stats_text) 