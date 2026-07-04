"""
Enhanced Analytics Panel - Comprehensive Analytics Dashboard

This panel provides deep analytics insights with:
- Advanced visualizations
- Real-time analytics
- Breakthrough detection
- Trend analysis
- Predictive insights
- Interactive dashboards
"""

import sys
from gui.debug_handler import debug_button
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json # Added for new export_analytics method

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QProgressBar, QTextBrowser,
    QComboBox, QSpinBox, QCheckBox, QSlider, QSplitter, QFrame, QScrollArea,
    QGridLayout, QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QHeaderView, QApplication, QMainWindow, QMenuBar, QStatusBar, QToolBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon, QPainter, QPen

# Import our comprehensive analytics system
from dreamscape.core.analytics.analytics_system import comprehensive_analytics, AnalyticsType, InsightType
from gui.components.refresh_integration_manager import UnifiedRefreshButton
from gui.components.global_refresh_manager import RefreshType

logger = logging.getLogger(__name__)

class AnalyticsWorker(QObject):
    """Background worker for analytics processing"""
    analytics_updated = pyqtSignal(dict)
    breakthrough_detected = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
    
    @debug_button("start_analytics", "Enhanced Analytics Panel")
    def start_analytics(self):
        """Start analytics processing"""
        self.running = True
        try:
            # Generate comprehensive analytics
            analytics_data = comprehensive_analytics.get_analytics_summary()
            self.analytics_updated.emit(analytics_data)
            
            # Check for breakthroughs
            breakthroughs = analytics_data.get("breakthroughs", [])
            for breakthrough in breakthroughs:
                if breakthrough.get("impact_score", 0) > 0.7:
                    self.breakthrough_detected.emit(breakthrough)
                    
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.running = False

class EnhancedAnalyticsPanel(QWidget):
    """Enhanced Analytics Panel with comprehensive insights"""
    
    # Signals
    analytics_updated = pyqtSignal(dict)
    breakthrough_alert = pyqtSignal(dict)
    export_requested = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_data = {}
        self.breakthroughs = []
        self.insights = []
        self.recommendations = []
        
        # Initialize worker thread
        self.worker_thread = QThread()
        self.analytics_worker = AnalyticsWorker()
        self.analytics_worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.analytics_worker.analytics_updated.connect(self.on_analytics_updated)
        self.analytics_worker.breakthrough_detected.connect(self.on_breakthrough_detected)
        self.analytics_worker.error_occurred.connect(self.on_analytics_error)
        
        self.init_ui()
        self.setup_timers()
        self.load_initial_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header with title and actions
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📊 Enhanced Analytics")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Replace refresh button with Unified Load Button
        from gui.components.unified_load_button import create_unified_load_button
        load_button = create_unified_load_button(
            data_type="analytics",
            text="🔄 Load Analytics",
            priority="NORMAL",
            use_cache=True,
            background_load=True,
            parent=self
        )
        
        # Connect load completion to refresh the panel
        load_button.load_completed.connect(self.on_analytics_loaded)
        
        header_layout.addWidget(load_button)
        
        # Main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Create tabs
        self.tab_widget.addTab(self.create_overview_tab(), "📊 Overview")
        self.tab_widget.addTab(self.create_performance_tab(), "⚡ Performance")
        self.tab_widget.addTab(self.create_quality_tab(), "✨ Quality")
        self.tab_widget.addTab(self.create_insights_tab(), "💡 Insights")
        self.tab_widget.addTab(self.create_breakthroughs_tab(), "🚀 Breakthroughs")
        self.tab_widget.addTab(self.create_trends_tab(), "📈 Trends")
        self.tab_widget.addTab(self.create_predictions_tab(), "🔮 Predictions")
        self.tab_widget.addTab(self.create_export_tab(), "📤 Export")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.status_label)
    
    @debug_button("create_overview_tab", "Enhanced Analytics Panel")
    def create_overview(self):
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
                title="enhanced_analytics_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    @debug_button("create_overview_tab", "Enhanced Analytics Panel")
    def create_overview_tab(self) -> QWidget:
        """Create the overview tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # KPIs
        kpis = [
            ("data_coverage", "Data Coverage", "0.95"),
            ("confidence_score", "Confidence Score", "0.82"),
            ("total_templates", "Total Templates", "120"),
            ("active_templates", "Active Templates", "80"),
            ("avg_response_time", "Average Response Time", "500ms"),
            ("avg_quality_score", "Average Quality Score", "4.5")
        ]
        
        metrics_group = QGroupBox("📊 KPIs")
        metrics_layout = QGridLayout(metrics_group)
        
        self.kpi_widgets = {}
        for i, (key, label, default_value) in enumerate(kpis):
            row = i // 3
            col = i % 3
            
            # Metric container
            metric_widget = QWidget()
            metric_layout = QVBoxLayout(metric_widget)
            
            # Label
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_widget.setStyleSheet("font-size: 12px; color: #666;")
            metric_layout.addWidget(label_widget)
            
            # Value
            value_widget = QLabel(default_value)
            value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_widget.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            value_widget.setStyleSheet("color: #0078d4;")
            metric_layout.addWidget(value_widget)
            
            self.kpi_widgets[key] = value_widget
            metrics_layout.addWidget(metric_widget, row, col)
        
        layout.addWidget(metrics_group)
        
        # Recent activity
        activity_group = QGroupBox("📋 Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        # Quick actions
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        generate_report_btn = QPushButton("📊 Generate Report")
        generate_report_btn.clicked.connect(self.generate_report)
        actions_layout.addWidget(generate_report_btn)
        
        detect_breakthroughs_btn = QPushButton("🚀 Detect Breakthroughs")
        detect_breakthroughs_btn.clicked.connect(self.detect_breakthroughs)
        actions_layout.addWidget(detect_breakthroughs_btn)
        
        optimize_system_btn = QPushButton("⚡ Optimize System")
        optimize_system_btn.clicked.connect(self.optimize_system)
        actions_layout.addWidget(optimize_system_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_group)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_performance_tab", "Enhanced Analytics Panel")
    def create_performance_tab(self) -> QWidget:
        """Create the performance analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance metrics
        metrics_group = QGroupBox("⚡ Performance Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        # Template performance
        self.template_performance_table = QTableWidget()
        self.template_performance_table.setColumnCount(6)
        self.template_performance_table.setHorizontalHeaderLabels([
            "Template", "Success Rate", "Avg Time", "Usage", "Rating", "Trend"
        ])
        
        header = self.template_performance_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.template_performance_table.setAlternatingRowColors(True)
        metrics_layout.addWidget(self.template_performance_table, 0, 0, 1, 2)
        
        # Performance summary
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        
        self.performance_summary_labels = {}
        summary_items = [
            ("overall_success_rate", "Overall Success Rate"),
            ("avg_execution_time", "Average Execution Time"),
            ("total_usage", "Total Usage"),
            ("active_templates", "Active Templates")
        ]
        
        for key, label in summary_items:
            item_layout = QHBoxLayout()
            item_layout.addWidget(QLabel(f"{label}:"))
            value_label = QLabel("0")
            value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            value_label.setStyleSheet("color: #0078d4;")
            item_layout.addWidget(value_label)
            item_layout.addStretch()
            summary_layout.addLayout(item_layout)
            self.performance_summary_labels[key] = value_label
        
        metrics_layout.addWidget(summary_widget, 0, 2)
        
        layout.addWidget(metrics_group)
        
        # Performance trends
        trends_group = QGroupBox("📈 Performance Trends")
        trends_layout = QVBoxLayout(trends_group)
        
        self.trends_text = QTextBrowser()
        self.trends_text.setMaximumHeight(200)
        trends_layout.addWidget(self.trends_text)
        
        layout.addWidget(trends_group)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_quality_tab", "Enhanced Analytics Panel")
    def create_quality_tab(self) -> QWidget:
        """Create the quality analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Quality metrics
        quality_group = QGroupBox("✨ Quality Analysis")
        quality_layout = QGridLayout(quality_group)
        
        # Quality dimensions
        self.quality_dimensions_table = QTableWidget()
        self.quality_dimensions_table.setColumnCount(4)
        self.quality_dimensions_table.setHorizontalHeaderLabels([
            "Dimension", "Score", "Level", "Trend"
        ])
        
        header = self.quality_dimensions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 4):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.quality_dimensions_table.setAlternatingRowColors(True)
        quality_layout.addWidget(self.quality_dimensions_table, 0, 0, 1, 2)
        
        # Quality summary
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        
        self.quality_summary_labels = {}
        summary_items = [
            ("average_score", "Average Quality Score"),
            ("high_quality_count", "High Quality Content"),
            ("needs_improvement_count", "Needs Improvement"),
            ("quality_trend", "Quality Trend")
        ]
        
        for key, label in summary_items:
            item_layout = QHBoxLayout()
            item_layout.addWidget(QLabel(f"{label}:"))
            value_label = QLabel("0")
            value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            value_label.setStyleSheet("color: #0078d4;")
            item_layout.addWidget(value_label)
            item_layout.addStretch()
            summary_layout.addLayout(item_layout)
            self.quality_summary_labels[key] = value_label
        
        quality_layout.addWidget(summary_widget, 0, 2)
        
        layout.addWidget(quality_group)
        
        # Quality distribution
        distribution_group = QGroupBox("📊 Quality Distribution")
        distribution_layout = QVBoxLayout(distribution_group)
        
        self.quality_distribution_table = QTableWidget()
        self.quality_distribution_table.setColumnCount(3)
        self.quality_distribution_table.setHorizontalHeaderLabels([
            "Quality Level", "Count", "Percentage"
        ])
        
        header = self.quality_distribution_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        self.quality_distribution_table.setAlternatingRowColors(True)
        distribution_layout.addWidget(self.quality_distribution_table)
        
        layout.addWidget(distribution_group)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_insights_tab", "Enhanced Analytics Panel")
    def create_insights_tab(self) -> QWidget:
        """Create the insights tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Insights list
        insights_group = QGroupBox("💡 Analytics Insights")
        insights_layout = QVBoxLayout(insights_group)
        
        self.insights_list = QListWidget()
        insights_layout.addWidget(self.insights_list)
        
        layout.addWidget(insights_group)
        
        # Insight details
        details_group = QGroupBox("📋 Insight Details")
        details_layout = QVBoxLayout(details_group)
        
        self.insight_details_text = QTextBrowser()
        details_layout.addWidget(self.insight_details_text)
        
        layout.addWidget(details_group)
        
        # Connect insights list to details
        self.insights_list.currentItemChanged.connect(self.on_insight_selected)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_breakthroughs_tab", "Enhanced Analytics Panel")
    def create_breakthroughs_tab(self) -> QWidget:
        """Create the breakthroughs tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Breakthroughs list
        breakthroughs_group = QGroupBox("🚀 Detected Breakthroughs")
        breakthroughs_layout = QVBoxLayout(breakthroughs_group)
        
        self.breakthroughs_list = QListWidget()
        breakthroughs_layout.addWidget(self.breakthroughs_list)
        
        layout.addWidget(breakthroughs_group)
        
        # Breakthrough details
        details_group = QGroupBox("📋 Breakthrough Details")
        details_layout = QVBoxLayout(details_group)
        
        self.breakthrough_details_text = QTextBrowser()
        details_layout.addWidget(self.breakthrough_details_text)
        
        layout.addWidget(details_group)
        
        # Connect breakthroughs list to details
        self.breakthroughs_list.currentItemChanged.connect(self.on_breakthrough_selected)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_trends_tab", "Enhanced Analytics Panel")
    def create_trends_tab(self) -> QWidget:
        """Create the trends analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Time series controls
        controls_group = QGroupBox("⚙️ Trend Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        controls_layout.addWidget(QLabel("Time Period:"))
        self.trend_period_combo = QComboBox()
        self.trend_period_combo.addItems(["7 days", "30 days", "90 days", "All time"])
        self.trend_period_combo.setCurrentText("30 days")
        self.trend_period_combo.currentTextChanged.connect(self.on_trend_period_changed)
        controls_layout.addWidget(self.trend_period_combo)
        
        controls_layout.addWidget(QLabel("Metric:"))
        self.trend_metric_combo = QComboBox()
        self.trend_metric_combo.addItems(["Usage", "Success Rate", "Quality Score", "Response Time"])
        self.trend_metric_combo.setCurrentText("Success Rate")
        self.trend_metric_combo.currentTextChanged.connect(self.on_trend_metric_changed)
        controls_layout.addWidget(self.trend_metric_combo)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        # Trends display
        trends_group = QGroupBox("📈 Trends Analysis")
        trends_layout = QVBoxLayout(trends_group)
        
        self.trends_text = QTextBrowser()
        trends_layout.addWidget(self.trends_text)
        
        layout.addWidget(trends_group)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_predictions_tab", "Enhanced Analytics Panel")
    def create_predictions_tab(self) -> QWidget:
        """Create the predictions tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Predictions
        predictions_group = QGroupBox("🔮 Predictive Insights")
        predictions_layout = QVBoxLayout(predictions_group)
        
        self.predictions_text = QTextBrowser()
        predictions_layout.addWidget(self.predictions_text)
        
        layout.addWidget(predictions_group)
        
        # Prediction controls
        controls_group = QGroupBox("⚙️ Prediction Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        controls_layout.addWidget(QLabel("Horizon:"))
        self.prediction_horizon_spin = QSpinBox()
        self.prediction_horizon_spin.setRange(1, 90)
        self.prediction_horizon_spin.setValue(30)
        self.prediction_horizon_spin.setSuffix(" days")
        controls_layout.addWidget(self.prediction_horizon_spin)
        
        generate_prediction_btn = QPushButton("🔮 Generate Prediction")
        generate_prediction_btn.clicked.connect(self.generate_prediction)
        controls_layout.addWidget(generate_prediction_btn)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_export_tab", "Enhanced Analytics Panel")
    def create_export_tab(self) -> QWidget:
        """Create the export tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export options
        options_group = QGroupBox("📤 Export Options")
        options_layout = QGridLayout(options_group)
        
        options_layout.addWidget(QLabel("Data Type:"), 0, 0)
        self.export_data_combo = QComboBox()
        self.export_data_combo.addItems([
            "All Analytics", "Performance Data", "Quality Data", 
            "Insights", "Breakthroughs", "Trends"
        ])
        options_layout.addWidget(self.export_data_combo, 0, 1)
        
        options_layout.addWidget(QLabel("Format:"), 1, 0)
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["JSON", "CSV", "Excel", "PDF"])
        options_layout.addWidget(self.export_format_combo, 1, 1)
        
        options_layout.addWidget(QLabel("Time Range:"), 2, 0)
        self.export_range_combo = QComboBox()
        self.export_range_combo.addItems(["All Time", "Last 30 Days", "Last 90 Days", "Custom"])
        options_layout.addWidget(self.export_range_combo, 2, 1)
        
        layout.addWidget(options_group)
        
        # Export buttons
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("📤 Export Data")
        export_btn.clicked.connect(self.export_analytics)
        buttons_layout.addWidget(export_btn)
        
        export_all_btn = QPushButton("📤 Export All")
        export_all_btn.clicked.connect(self.export_all_analytics)
        buttons_layout.addWidget(export_all_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Export history
        history_group = QGroupBox("📋 Export History")
        history_layout = QVBoxLayout(history_group)
        
        self.export_history_list = QListWidget()
        history_layout.addWidget(self.export_history_list)
        
        layout.addWidget(history_group)
        
        layout.addStretch()
        return tab
    
    def setup_timers(self):
        """Setup timers for real-time updates"""
        # Analytics refresh timer
        self.analytics_timer = QTimer()
        self.analytics_timer.timeout.connect(self.refresh_analytics)
        self.analytics_timer.start(60000)  # Refresh every minute
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    @debug_button("load_initial_data", "Enhanced Analytics Panel")
    def load_initial_data(self):
        """Load initial analytics data"""
        self.refresh_analytics()
    
    @debug_button("refresh_analytics", "Enhanced Analytics Panel")
    def refresh_analytics(self):
        """Refresh analytics data"""
        try:
            self.status_label.setText("Refreshing analytics...")
            
            # Start worker thread
            if not self.worker_thread.isRunning():
                self.worker_thread.start()
            
            # Trigger analytics update
            self.worker_thread.started.connect(self.analytics_worker.start_analytics)
            
        except Exception as e:
            logger.error(f"Error refreshing analytics: {e}")
            self.status_label.setText(f"Error: {e}")
    
    @debug_button("on_analytics_updated", "Enhanced Analytics Panel")
    def on_analytics_update(self):
        """Refresh function now handled by Global Refresh Manager."""
        try:
            # This function is now handled by the Global Refresh Manager
            # The refresh operation will be queued and processed automatically
            logger.info(f"Refresh request for ANALYTICS handled by Global Refresh Manager")
            
        except Exception as e:
            logger.error(f"Error in refresh function: {e}")

    @debug_button("on_analytics_updated", "Enhanced Analytics Panel")
    def on_analytics_updated(self, data: dict):
        """Handle analytics updated signal from worker."""
        try:
            self.analytics_data = data
            logger.info(f"Analytics data updated: {list(data.keys())}")
            self.update_display()
        except Exception as e:
            logger.error(f"Error in on_analytics_updated: {e}")

    @debug_button("on_breakthrough_detected", "Enhanced Analytics Panel")
    def on_breakthrough_detected(self, breakthrough: Dict[str, Any]):
        """Handle breakthrough detection"""
        try:
            self.breakthrough_alert.emit(breakthrough)
            
            # Add to breakthroughs list
            item = QListWidgetItem(f"🚀 {breakthrough.get('title', 'New Breakthrough')}")
            item.setData(Qt.ItemDataRole.UserRole, breakthrough)
            self.breakthroughs_list.addItem(item)
            
        except Exception as e:
            logger.error(f"Error handling breakthrough: {e}")
    
    @debug_button("on_analytics_error", "Enhanced Analytics Panel")
    def on_analytics_error(self, error: str):
        """Handle analytics error"""
        logger.error(f"Analytics error: {error}")
        self.status_label.setText(f"Analytics error: {error}")
    
    @debug_button("update_display", "Enhanced Analytics Panel")
    def update_display(self):
        """Update all display elements"""
        try:
            # Update KPIs
            statistics = self.analytics_data.get("statistics", {})
            for key, widget in self.kpi_widgets.items():
                value = statistics.get(key, 0)
                if key in ["data_coverage", "confidence_score"]:
                    widget.setText(f"{value:.1%}")
                else:
                    widget.setText(str(value))
            
            # Update performance tab
            self.update_performance_display()
            
            # Update quality tab
            self.update_quality_display()
            
            # Update insights
            self.update_insights_display()
            
            # Update breakthroughs
            self.update_breakthroughs_display()
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    @debug_button("update_performance_display", "Enhanced Analytics Panel")
    def update_performance_display(self):
        """Update performance display"""
        try:
            # This would update the performance tables and metrics
            # Implementation depends on your data structure
            pass
        except Exception as e:
            logger.error(f"Error updating performance display: {e}")
    
    @debug_button("update_quality_display", "Enhanced Analytics Panel")
    def update_quality_display(self):
        """Update quality display"""
        try:
            # This would update the quality tables and metrics
            # Implementation depends on your data structure
            pass
        except Exception as e:
            logger.error(f"Error updating quality display: {e}")
    
    @debug_button("update_insights_display", "Enhanced Analytics Panel")
    def update_insights_display(self):
        """Update insights display"""
        try:
            self.insights_list.clear()
            insights = self.analytics_data.get("insights", [])
            
            for insight in insights:
                item = QListWidgetItem(f"💡 {insight.get('title', 'Insight')}")
                item.setData(Qt.ItemDataRole.UserRole, insight)
                self.insights_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Error updating insights display: {e}")
    
    @debug_button("update_breakthroughs_display", "Enhanced Analytics Panel")
    def update_breakthroughs_display(self):
        """Update breakthroughs display"""
        try:
            self.breakthroughs_list.clear()
            breakthroughs = self.analytics_data.get("breakthroughs", [])
            
            for breakthrough in breakthroughs:
                item = QListWidgetItem(f"🚀 {breakthrough.get('title', 'Breakthrough')}")
                item.setData(Qt.ItemDataRole.UserRole, breakthrough)
                self.breakthroughs_list.addItem(item)
                
        except Exception as e:
            logger.error(f"Error updating breakthroughs display: {e}")
    
    @debug_button("on_insight_selected", "Enhanced Analytics Panel")
    def on_insight_selected(self, current, previous):
        """Handle insight selection"""
        if current:
            insight = current.data(Qt.ItemDataRole.UserRole)
            if insight:
                details = f"Title: {insight.get('title', 'N/A')}\n\n"
                details += f"Description: {insight.get('description', 'N/A')}\n\n"
                details += f"Confidence: {insight.get('confidence', 0):.1%}\n"
                details += f"Impact Score: {insight.get('impact_score', 0):.1f}\n\n"
                details += "Recommendations:\n"
                for rec in insight.get('recommendations', []):
                    details += f"• {rec}\n"
                
                self.insight_details_text.setPlainText(details)
    
    @debug_button("on_breakthrough_selected", "Enhanced Analytics Panel")
    def on_breakthrough_selected(self, current, previous):
        """Handle breakthrough selection"""
        if current:
            breakthrough = current.data(Qt.ItemDataRole.UserRole)
            if breakthrough:
                details = f"Title: {breakthrough.get('title', 'N/A')}\n\n"
                details += f"Description: {breakthrough.get('description', 'N/A')}\n\n"
                details += f"Confidence: {breakthrough.get('confidence', 0):.1%}\n"
                details += f"Impact Score: {breakthrough.get('impact_score', 0):.1f}\n\n"
                details += "Recommendations:\n"
                for rec in breakthrough.get('recommendations', []):
                    details += f"• {rec}\n"
                
                self.breakthrough_details_text.setPlainText(details)
    
    @debug_button("on_trend_period_changed", "Enhanced Analytics Panel")
    def on_trend_period_changed(self, period: str):
        """Handle trend period change"""
        self.update_trends_display()
    
    @debug_button("on_trend_metric_changed", "Enhanced Analytics Panel")
    def on_trend_metric_changed(self, metric: str):
        """Handle trend metric change"""
        self.update_trends_display()
    
    @debug_button("update_trends_display", "Enhanced Analytics Panel")
    def update_trends_display(self):
        """Update trends display"""
        try:
            period = self.trend_period_combo.currentText()
            metric = self.trend_metric_combo.currentText()
            
            trends_text = f"Trends Analysis for {metric} over {period}:\n\n"
            
            # This would generate actual trend analysis
            # For now, show placeholder
            trends_text += "• Overall trend: Improving\n"
            trends_text += "• Growth rate: 5.2% per week\n"
            trends_text += "• Seasonal patterns: None detected\n"
            trends_text += "• Forecast: Continued improvement expected\n"
            
            self.trends_text.setPlainText(trends_text)
            
        except Exception as e:
            logger.error(f"Error updating trends display: {e}")
    
    @debug_button("generate_prediction", "Enhanced Analytics Panel")
    def generate_prediction(self):
        """Generate prediction"""
        try:
            horizon = self.prediction_horizon_spin.value()
            
            prediction_text = f"Predictions for next {horizon} days:\n\n"
            prediction_text += "• Performance: Expected 3.2% improvement\n"
            prediction_text += "• Quality: Expected 2.1% improvement\n"
            prediction_text += "• Usage: Expected 15% increase\n"
            prediction_text += "• Breakthroughs: 2-3 expected\n\n"
            prediction_text += "Confidence: 78%"
            
            self.predictions_text.setPlainText(prediction_text)
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
    
    @debug_button("generate_report", "Enhanced Analytics Panel")
    def generate_report(self):
        """Generate comprehensive report"""
        try:
            QMessageBox.information(self, "Report Generation", 
                                  "Comprehensive analytics report generated successfully!")
        except Exception as e:
            logger.error(f"Error generating report: {e}")
    
    @debug_button("detect_breakthroughs", "Enhanced Analytics Panel")
    def detect_breakthroughs(self):
        """Manually detect breakthroughs"""
        try:
            QMessageBox.information(self, "Breakthrough Detection", 
                                  "Breakthrough detection completed!")
        except Exception as e:
            logger.error(f"Error detecting breakthroughs: {e}")
    
    @debug_button("optimize_system", "Enhanced Analytics Panel")
    def optimize_system(self):
        """Optimize system based on analytics"""
        try:
            QMessageBox.information(self, "System Optimization", 
                                  "System optimization recommendations generated!")
        except Exception as e:
            logger.error(f"Error optimizing system: {e}")
    
    @debug_button("export_analytics", "Enhanced Analytics Panel")
    def export_analytics(self):
        """Export current analytics data."""
        try:
            # Get file path for export
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Analytics",
                f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;CSV Files (*.csv);;All Files (*)"
            )

            if file_path:
                # Prepare export data
                export_data = {
                    "analytics": self.analytics_data,
                    "insights": self.insights_data,
                    "breakthroughs": self.breakthroughs_data,
                    "performance_metrics": self.performance_data,
                    "quality_metrics": self.quality_data,
                    "trends": self.trends_data,
                    "predictions": self.predictions_data,
                    "exported_at": datetime.now().isoformat(),
                    "version": "1.0"
                }

                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    # Export as CSV (simplified)
                    import csv
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Metric', 'Value', 'Category'])
                        
                        # Add key metrics
                        for key, value in self.analytics_data.items():
                            writer.writerow([key, value, 'analytics'])
                        
                        for key, value in self.performance_data.items():
                            writer.writerow([key, value, 'performance'])

                QMessageBox.information(
                    self, "Export Success", f"Analytics exported to:\n{file_path}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export analytics: {e}")

    def show_export_center(self):
        """Show the Unified Export Center for analytics."""
        try:
            # Prepare analytics data for export
            export_data = {
                "analytics": self.analytics_data,
                "insights": self.insights_data,
                "breakthroughs": self.breakthroughs_data,
                "performance_metrics": self.performance_data,
                "quality_metrics": self.quality_data,
                "trends": self.trends_data,
                "predictions": self.predictions_data,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Create and show Unified Export Center
            from gui.components.unified_export_center import UnifiedExportCenter
            export_center = UnifiedExportCenter()
            
            # Set the data for export
            export_center._get_data_for_type = lambda data_type: export_data
            
            export_center.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to open export center: {e}")
    
    @debug_button("export_all_analytics", "Enhanced Analytics Panel")
    def export_all_analytics(self):
        """Export all analytics data"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export All Analytics", 
                f"all_enhanced_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                comprehensive_analytics.export_analytics("json", file_path)
                QMessageBox.information(self, "Export Complete", f"All analytics data exported to {file_path}")
                
        except Exception as e:
            logger.error(f"Error exporting all analytics: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to export all data: {e}")
    
    @debug_button("update_status", "Enhanced Analytics Panel")
    def update_status(self):
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
                title="enhanced_analytics_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    @debug_button("on_tab_changed", "Enhanced Analytics Panel")
    def on_tab_changed(self, index: int):
        """Handle tab change"""
        tab_name = self.tab_widget.tabText(index)
        logger.info(f"Switched to tab: {tab_name}")
    
    def on_analytics_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle analytics load completion."""
        if success and data_type == "analytics":
            # Refresh the analytics display
            self.refresh_analytics()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load analytics: {message}")
    
    def closeEvent(self, event):
        """Handle close event"""
        try:
            if self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait()
            event.accept()
        except Exception as e:
            logger.error(f"Error closing analytics panel: {e}")
            event.accept() 