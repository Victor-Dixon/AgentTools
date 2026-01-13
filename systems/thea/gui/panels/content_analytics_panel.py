#!/usr/bin/env python3
"""
Content Analytics Panel - GUI for Template Performance & Content Quality Analytics
================================================================================

This panel provides comprehensive visualization and analysis of:
- Template performance metrics and trends
- Content quality scoring across multiple dimensions
- Optimization recommendations and insights
- Real-time analytics dashboard
"""

import sys
from gui.debug_handler import debug_button
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
    QPushButton, QTextEdit, QLineEdit, QComboBox, QSpinBox,
    QProgressBar, QGroupBox, QFormLayout, QCheckBox, QListWidget,
    QListWidgetItem, QSplitter, QFrame, QScrollArea, QGridLayout,
    QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QDateEdit, QCalendarWidget,
    QSlider, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QDate
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette

# Import our content analytics systems
from dreamscape.core.templates.template_processors import TemplatePerformanceAnalytics
from dreamscape.core.templates.template_engine import PromptTemplateEngine
from dreamscape.core.content.content_quality_scoring import ContentQualityScorer
from dreamscape.core.analytics.content_analytics_integration import ContentAnalyticsIntegration
from dreamscape.core.utils.database_mixin import ensure_prompt_templates_table

logger = logging.getLogger(__name__)

class ContentAnalyticsPanel(QWidget):
    """Content Analytics Panel with comprehensive template and content analysis."""
    
    # Signals
    analytics_updated = pyqtSignal(dict)     # Analytics data updated
    optimization_recommended = pyqtSignal(dict)  # Optimization recommendations
    export_requested = pyqtSignal(str, str)  # format, file_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # EDIT START: Ensure analytics DB schema before any queries
        analytics_db_path = Path("data/template_analytics/template_analytics.db")
        ensure_prompt_templates_table(analytics_db_path)
        # EDIT END

        # Initialize template engine for analytics
        self.template_engine = PromptTemplateEngine("data/template_analytics/template_analytics.db")
        
        # Initialize analytics systems
        self.template_analytics = TemplatePerformanceAnalytics(self.template_engine)
        self.content_scorer = ContentQualityScorer()
        self.analytics_integration = ContentAnalyticsIntegration()
        
        # Analytics state
        self.analytics_data = {}
        self.template_metrics = {}
        self.quality_scores = {}
        self.recommendations = []
        
        self.init_ui()
        self.load_analytics_data()
        
        # Start refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the content analytics user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("📊 Content Analytics Dashboard")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Comprehensive analysis of template performance and content quality across all dimensions.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_overview_tab(), "📈 Overview")
        self.tab_widget.addTab(self.create_template_analytics_tab(), "📋 Template Analytics")
        self.tab_widget.addTab(self.create_content_quality_tab(), "✨ Content Quality")
        self.tab_widget.addTab(self.create_recommendations_tab(), "💡 Recommendations")
        self.tab_widget.addTab(self.create_export_tab(), "📤 Export")
        
        # Progress section
        self.create_progress_section(layout)
        
        # Connect signals
        self.connect_signals()
    
    @debug_button("create_overview_tab", "Content Analytics Panel")
    def create_overview_tab(self):
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
                title="content_analytics_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
    
    @debug_button("create_template_analytics_tab", "Content Analytics Panel")
    def create_template_analytics_tab(self) -> QWidget:
        """Create the template analytics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("📋 Template Performance Analytics")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Template performance table
        performance_group = QGroupBox("Template Performance Metrics")
        performance_layout = QVBoxLayout(performance_group)
        
        self.template_table = QTableWidget()
        self.template_table.setColumnCount(7)
        self.template_table.setHorizontalHeaderLabels([
            "Template", "Usage Count", "Success Rate", "Avg Time", "Errors", "Rating", "Trend"
        ])
        
        # Configure table
        header = self.template_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.template_table.setAlternatingRowColors(True)
        performance_layout.addWidget(self.template_table)
        
        layout.addWidget(performance_group)
        
        # Usage trends
        trends_group = QGroupBox("Usage Trends")
        trends_layout = QVBoxLayout(trends_group)
        
        # Time period selector
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Time Period:"))
        
        self.trend_period_combo = QComboBox()
        self.trend_period_combo.addItems(["Last 7 days", "Last 30 days", "Last 90 days", "All time"])
        self.trend_period_combo.setCurrentText("Last 30 days")
        self.trend_period_combo.currentTextChanged.connect(self.on_trend_period_changed)
        period_layout.addWidget(self.trend_period_combo)
        period_layout.addStretch()
        trends_layout.addLayout(period_layout)
        
        # Trends table
        self.trends_table = QTableWidget()
        self.trends_table.setColumnCount(4)
        self.trends_table.setHorizontalHeaderLabels([
            "Template", "Usage Trend", "Success Trend", "Performance"
        ])
        
        header = self.trends_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 4):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.trends_table.setAlternatingRowColors(True)
        trends_layout.addWidget(self.trends_table)
        
        layout.addWidget(trends_group)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        
        # Replace refresh button with Unified Load Button
        from gui.components.unified_load_button import create_unified_load_button
        self.load_templates_btn = create_unified_load_button(
            data_type="template_analytics",
            text="🔄 Load Template Analytics",
            priority="NORMAL",
            use_cache=True,
            background_load=True,
            parent=self
        )
        
        # Connect load completion to refresh the panel
        self.load_templates_btn.load_completed.connect(self.on_template_analytics_loaded)
        
        refresh_layout.addWidget(self.load_templates_btn)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_content_quality_tab", "Content Analytics Panel")
    def create_content_quality_tab(self) -> QWidget:
        """Create the content quality analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Header
        header = QLabel("✨ Content Quality Analysis")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # Quality dimensions overview
        dimensions_group = QGroupBox("Quality Dimensions")
        dimensions_layout = QGridLayout(dimensions_group)

        # Create quality dimension labels
        self.quality_labels = {}
        quality_dimensions = [
            "Readability", "Engagement", "SEO Optimization", "Technical Accuracy",
            "Structure", "Originality", "Completeness", "Clarity", "Actionability", "Visual Appeal"
        ]

        for i, dimension in enumerate(quality_dimensions):
            row = i // 2
            col = i % 2 * 2

            # Dimension name
            name_label = QLabel(dimension)
            name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            dimensions_layout.addWidget(name_label, row, col)

            # Score label
            score_label = QLabel("0.0")
            score_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            score_label.setStyleSheet("color: #0078d4;")
            dimensions_layout.addWidget(score_label, row, col + 1)

            self.quality_labels[dimension] = score_label

        layout.addWidget(dimensions_group)

        # Quality distribution
        distribution_group = QGroupBox("Quality Distribution")
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

        # Quality analysis
        analysis_group = QGroupBox("Quality Analysis")
        analysis_layout = QVBoxLayout(analysis_group)

        self.quality_analysis_text = QTextBrowser()
        self.quality_analysis_text.setMaximumHeight(200)
        analysis_layout.addWidget(self.quality_analysis_text)

        layout.addWidget(analysis_group)

        # Refresh button using shared component
        refresh_layout = QHBoxLayout()
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        self.refresh_quality_btn = components.create_refresh_button(
            text="Refresh Quality", callback=self.refresh_content_quality
        )
        refresh_layout.addWidget(self.refresh_quality_btn)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)

        layout.addStretch()
        return tab
    
    @debug_button("create_recommendations_tab", "Content Analytics Panel")
    def create_recommendations_tab(self) -> QWidget:
        """Create the recommendations tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("💡 Optimization Recommendations")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Priority recommendations
        priority_group = QGroupBox("High Priority Recommendations")
        priority_layout = QVBoxLayout(priority_group)
        
        self.priority_list = QListWidget()
        priority_layout.addWidget(self.priority_list)
        
        layout.addWidget(priority_group)
        
        # All recommendations
        all_group = QGroupBox("All Recommendations")
        all_layout = QVBoxLayout(all_group)
        
        self.recommendations_table = QTableWidget()
        self.recommendations_table.setColumnCount(4)
        self.recommendations_table.setHorizontalHeaderLabels([
            "Category", "Recommendation", "Impact", "Effort"
        ])
        
        header = self.recommendations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.recommendations_table.setAlternatingRowColors(True)
        all_layout.addWidget(self.recommendations_table)
        
        layout.addWidget(all_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.apply_recommendation_btn = QPushButton("✅ Apply Selected")
        self.apply_recommendation_btn.clicked.connect(self.apply_recommendation)
        action_layout.addWidget(self.apply_recommendation_btn)
        
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        self.refresh_recommendations_btn = components.create_refresh_button(
            text="Refresh Recommendations", callback=self.refresh_recommendations
        )
        action_layout.addWidget(self.refresh_recommendations_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_export_tab", "Content Analytics Panel")
    def create_export_tab(self) -> QWidget:
        """Create the export tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("📤 Export Analytics Data")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout(options_group)
        
        # Data type selection
        self.export_data_combo = QComboBox()
        self.export_data_combo.addItems([
            "All Analytics Data",
            "Template Performance Only",
            "Content Quality Only",
            "Recommendations Only"
        ])
        options_layout.addRow("Data Type:", self.export_data_combo)
        
        # Format selection
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["JSON", "CSV", "Excel", "PDF"])
        options_layout.addRow("Format:", self.export_format_combo)
        
        # Date range
        self.export_start_date = QDateEdit()
        self.export_start_date.setDate(QDate.currentDate().addDays(-30))
        options_layout.addRow("Start Date:", self.export_start_date)
        
        self.export_end_date = QDateEdit()
        self.export_end_date.setDate(QDate.currentDate())
        options_layout.addRow("End Date:", self.export_end_date)
        
        layout.addWidget(options_group)
        
        # Replace individual export buttons with Unified Export Center
        export_layout = QHBoxLayout()
        self.unified_export_btn = QPushButton("🚀 Export Center")
        self.unified_export_btn.clicked.connect(self.show_unified_export_center)
        self.unified_export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        export_layout.addWidget(self.unified_export_btn)
        
        # Export history
        history_group = QGroupBox("Export History")
        history_layout = QVBoxLayout(history_group)
        
        self.export_history_table = QTableWidget()
        self.export_history_table.setColumnCount(4)
        self.export_history_table.setHorizontalHeaderLabels([
            "Date", "Type", "Format", "Status"
        ])
        
        header = self.export_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.export_history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.export_history_table)
        
        layout.addWidget(history_group)
        
        layout.addStretch()
        return tab
    
    @debug_button("create_progress_section", "Content Analytics Panel")
    def create_progress_section(self, layout: QVBoxLayout):
        """Create the progress section."""
        progress_group = QGroupBox("Analytics Status")
        progress_layout = QVBoxLayout(progress_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to analyze content")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
    
    @debug_button("connect_signals", "Content Analytics Panel")
    def connect_signals(self):
        """Connect all signals."""
        # Tab change events
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Export signals
        self.export_requested.connect(self.handle_export_request)
    
    @debug_button("load_analytics_data", "Content Analytics Panel")
    def load_analytics_data(self):
        """Load initial analytics data."""
        try:
            self.status_label.setText("Loading analytics data...")
            self.progress_bar.setValue(25)
            
            # Load template analytics
            self.template_metrics = self.template_analytics.generate_performance_report()
            self.progress_bar.setValue(50)
            
            # Load content quality data
            self.quality_scores = self.content_scorer.get_quality_summary()
            self.progress_bar.setValue(75)
            
            # Get integrated analytics
            self.analytics_data = self.analytics_integration.get_analytics_summary()
            self.progress_bar.setValue(100)
            
            # Update UI
            self.update_overview_display()
            self.update_template_display()
            self.update_quality_display()
            self.update_recommendations_display()
            
            self.status_label.setText("Analytics data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load analytics data: {e}")
            self.status_label.setText(f"Error loading data: {e}")
    
    @debug_button("refresh_analytics", "Content Analytics Panel")
    def refresh_analytics(self):
        """Refresh all analytics data."""
        self.load_analytics_data()
        self.analytics_updated.emit(self.analytics_data)
    
    def on_analytics_updated(self, data: dict):
        """Handle analytics data updates."""
        try:
            logger.info("Content Analytics Panel received analytics update")
            self.analytics_data = data
            self.refresh_analytics()
        except Exception as e:
            logger.error(f"Error handling analytics update: {e}")
    
    @debug_button("update_overview_display", "Content Analytics Panel")
    def update_overview_display(self):
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
                title="content_analytics_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
    
    @debug_button("update_template_display", "Content Analytics Panel")
    def update_template_display(self):
        """Update the template analytics display."""
        try:
            # EDIT START: Robustly handle dataclass, dict, and sqlite3.Row for template rows
            # Rationale: Prevent .name attribute errors if template is a sqlite3.Row or dict, not a dataclass
            if hasattr(self.template_metrics, 'top_performers'):
                templates = self.template_metrics.top_performers
                self.template_table.setRowCount(len(templates))
                for i, template in enumerate(templates):
                    def get_field(obj, attr, default):
                        # Try attribute access (dataclass)
                        if hasattr(obj, attr):
                            return getattr(obj, attr, default)
                        # Try dict-style access (dict or sqlite3.Row)
                        try:
                            return obj[attr]
                        except (KeyError, TypeError, IndexError):
                            return default
                    self.template_table.setItem(i, 0, QTableWidgetItem(str(get_field(template, 'template_name', 'Unknown'))))
                    self.template_table.setItem(i, 1, QTableWidgetItem(str(get_field(template, 'total_usage', 0))))
                    self.template_table.setItem(i, 2, QTableWidgetItem(f"{get_field(template, 'success_rate', 0):.1f}%"))
                    self.template_table.setItem(i, 3, QTableWidgetItem(f"{get_field(template, 'avg_execution_time', 0):.0f}ms"))
                    self.template_table.setItem(i, 4, QTableWidgetItem(str(get_field(template, 'error_count', 0))))
                    self.template_table.setItem(i, 5, QTableWidgetItem(f"{get_field(template, 'avg_user_feedback', 0):.1f}"))
                    self.template_table.setItem(i, 6, QTableWidgetItem('Good'))
                # Update trends table - use top performers as trends
                self.trends_table.setRowCount(len(templates))
                for i, template in enumerate(templates):
                    self.trends_table.setItem(i, 0, QTableWidgetItem(str(get_field(template, 'template_name', 'Unknown'))))
                    self.trends_table.setItem(i, 1, QTableWidgetItem('Increasing'))
                    self.trends_table.setItem(i, 2, QTableWidgetItem('Good'))
                    self.trends_table.setItem(i, 3, QTableWidgetItem('Excellent'))
            else:
                templates = self.template_metrics.get('templates', [])
                self.template_table.setRowCount(len(templates))
                for i, template in enumerate(templates):
                    def get_field(obj, key, default):
                        try:
                            return obj[key]
                        except (KeyError, TypeError, IndexError):
                            return default
                    self.template_table.setItem(i, 0, QTableWidgetItem(str(get_field(template, 'name', 'Unknown'))))
                    self.template_table.setItem(i, 1, QTableWidgetItem(str(get_field(template, 'usage_count', 0))))
                    self.template_table.setItem(i, 2, QTableWidgetItem(f"{get_field(template, 'success_rate', 0):.1f}%"))
                    self.template_table.setItem(i, 3, QTableWidgetItem(f"{get_field(template, 'avg_execution_time', 0):.0f}ms"))
                    self.template_table.setItem(i, 4, QTableWidgetItem(str(get_field(template, 'error_count', 0))))
                    self.template_table.setItem(i, 5, QTableWidgetItem(f"{get_field(template, 'user_rating', 0):.1f}"))
                    self.template_table.setItem(i, 6, QTableWidgetItem(get_field(template, 'trend', 'Stable')))
                trends = self.template_metrics.get('usage_trends', [])
                self.trends_table.setRowCount(len(trends))
                for i, trend in enumerate(trends):
                    def get_field(obj, key, default):
                        try:
                            return obj[key]
                        except (KeyError, TypeError, IndexError):
                            return default
                    self.trends_table.setItem(i, 0, QTableWidgetItem(str(get_field(trend, 'template_name', 'Unknown'))))
                    self.trends_table.setItem(i, 1, QTableWidgetItem(get_field(trend, 'usage_trend', 'Stable')))
                    self.trends_table.setItem(i, 2, QTableWidgetItem(get_field(trend, 'success_trend', 'Stable')))
                    self.trends_table.setItem(i, 3, QTableWidgetItem(get_field(trend, 'performance', 'Good')))
            # EDIT END
        except Exception as e:
            logger.error(f"Failed to update template display: {e}")
    
    @debug_button("update_quality_display", "Content Analytics Panel")
    def update_quality_display(self):
        """Update the content quality display."""
        try:
            # Update quality dimension scores
            dimension_scores = self.quality_scores.get('dimension_scores', {})
            for dimension, label in self.quality_labels.items():
                score = dimension_scores.get(dimension, 0)
                label.setText(f"{score:.1f}")
            
            # Update quality distribution
            distribution = self.quality_scores.get('quality_distribution', {})
            self.quality_distribution_table.setRowCount(len(distribution))
            for i, (level, data) in enumerate(distribution.items()):
                self.quality_distribution_table.setItem(i, 0, QTableWidgetItem(level))
                self.quality_distribution_table.setItem(i, 1, QTableWidgetItem(str(data.get('count', 0))))
                self.quality_distribution_table.setItem(i, 2, QTableWidgetItem(f"{data.get('percentage', 0):.1f}%"))
            
            # Update quality analysis
            analysis = self.quality_scores.get('analysis', '')
            self.quality_analysis_text.setPlainText(analysis)
            
        except Exception as e:
            logger.error(f"Failed to update quality display: {e}")
    
    @debug_button("update_recommendations_display", "Content Analytics Panel")
    def update_recommendations_display(self):
        """Update the recommendations display."""
        try:
            recommendations = self.analytics_data.get('recommendations', [])
            
            # Update priority list
            self.priority_list.clear()
            priority_recs = [r for r in recommendations if r.get('priority', 'Low') == 'High']
            for rec in priority_recs:
                item = QListWidgetItem(f"🔴 {rec.get('category', 'General')}: {rec.get('recommendation', '')}")
                self.priority_list.addItem(item)
            
            # Update recommendations table
            self.recommendations_table.setRowCount(len(recommendations))
            for i, rec in enumerate(recommendations):
                self.recommendations_table.setItem(i, 0, QTableWidgetItem(rec.get('category', 'General')))
                self.recommendations_table.setItem(i, 1, QTableWidgetItem(rec.get('recommendation', '')))
                self.recommendations_table.setItem(i, 2, QTableWidgetItem(rec.get('impact', 'Medium')))
                self.recommendations_table.setItem(i, 3, QTableWidgetItem(rec.get('effort', 'Medium')))
                
        except Exception as e:
            logger.error(f"Failed to update recommendations display: {e}")
    
    @debug_button("refresh_overview", "Content Analytics Panel")
    def refresh_overview(self):
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
                title="content_analytics_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
    
    @debug_button("refresh_template_analytics", "Content Analytics Panel")
    def refresh_template_analytics(self):
        """Refresh template analytics."""
        try:
            self.template_metrics = self.template_analytics.generate_performance_report()
            self.update_template_display()
        except Exception as e:
            logger.error(f"Failed to refresh template analytics: {e}")
    
    @debug_button("refresh_content_quality", "Content Analytics Panel")
    def refresh_content_quality(self):
        """Refresh content quality analysis."""
        try:
            self.quality_scores = self.content_scorer.get_quality_summary()
            self.update_quality_display()
        except Exception as e:
            logger.error(f"Failed to refresh content quality: {e}")
    
    @debug_button("refresh_recommendations", "Content Analytics Panel")
    def refresh_recommendations(self):
        """Refresh recommendations."""
        try:
            self.analytics_data = self.analytics_integration.get_analytics_summary()
            self.update_recommendations_display()
        except Exception as e:
            logger.error(f"Failed to refresh recommendations: {e}")
    
    @debug_button("on_trend_period_changed", "Content Analytics Panel")
    def on_trend_period_changed(self, period: str):
        """Handle trend period change."""
        self.refresh_template_analytics()
    
    @debug_button("on_tab_changed", "Content Analytics Panel")
    def on_tab_changed(self, index: int):
        """Handle tab change."""
        tab_name = self.tab_widget.tabText(index)
        if "Template" in tab_name:
            self.refresh_template_analytics()
        elif "Quality" in tab_name:
            self.refresh_content_quality()
        elif "Recommendations" in tab_name:
            self.refresh_recommendations()
    
    @debug_button("apply_recommendation", "Content Analytics Panel")
    def apply_recommendation(self):
        """Apply the selected recommendation."""
        current_row = self.recommendations_table.currentRow()
        if current_row >= 0:
            recommendation = self.analytics_data.get('recommendations', [])[current_row]
            QMessageBox.information(self, "Apply Recommendation", 
                                  f"Would you like to apply: {recommendation.get('recommendation', '')}")
    
    @debug_button("export_analytics_data", "Content Analytics Panel")
    def export_analytics_data(self):
        """Export analytics data."""
        try:
            data_type = self.export_data_combo.currentText()
            format_type = self.export_format_combo.currentText()
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"Export {data_type}", 
                f"content_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type.lower()}",
                f"{format_type} Files (*.{format_type.lower()})"
            )
            
            if file_path:
                self.export_requested.emit(format_type, file_path)
                
        except Exception as e:
            logger.error(f"Failed to export analytics data: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to export data: {e}")
    
    @debug_button("export_all_analytics", "Content Analytics Panel")
    def export_all_analytics(self):
        """Export all analytics data."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export All Analytics", 
                f"all_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                # Export all data
                all_data = {
                    'template_analytics': self.template_metrics,
                    'content_quality': self.quality_scores,
                    'integrated_analytics': self.analytics_data,
                    'export_timestamp': datetime.now().isoformat()
                }
                
                import json
                with open(file_path, 'w') as f:
                    json.dump(all_data, f, indent=2, default=str)
                
                QMessageBox.information(self, "Export Complete", f"All analytics data exported to {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to export all analytics: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to export all data: {e}")
    
    @debug_button("handle_export_request", "Content Analytics Panel")
    def handle_export_request(self, format_type: str, file_path: str):
        """Handle export request."""
        try:
            # Export based on format type
            if format_type.lower() == 'json':
                self.export_to_json(file_path)
            elif format_type.lower() == 'csv':
                self.export_to_csv(file_path)
            else:
                QMessageBox.warning(self, "Export Error", f"Format {format_type} not supported yet")
                
        except Exception as e:
            logger.error(f"Failed to handle export request: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to export: {e}")
    
    @debug_button("export_to_json", "Content Analytics Panel")
    def export_to_json(self, file_path: str):
        """Export data to JSON format."""
        import json
        data = {
            'template_analytics': self.template_metrics,
            'content_quality': self.quality_scores,
            'integrated_analytics': self.analytics_data
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        QMessageBox.information(self, "Export Complete", f"Data exported to {file_path}")
    
    @debug_button("export_to_csv", "Content Analytics Panel")
    def export_to_csv(self, file_path: str):
        """Export data to CSV format."""
        import csv
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Metric', 'Value'])
            
            # Template metrics
            for template in self.template_metrics.get('templates', []):
                writer.writerow(['Template', template.get('name', ''), template.get('usage_count', 0)])
            
            # Quality scores
            for dimension, score in self.quality_scores.get('dimension_scores', {}).items():
                writer.writerow(['Quality', dimension, score])
        
        QMessageBox.information(self, "Export Complete", f"Data exported to {file_path}") 

    def show_unified_export_center(self):
        """Show the Unified Export Center for content analytics data."""
        try:
            # Prepare content analytics data for export
            export_data = {
                "template_analytics": self.template_metrics if hasattr(self, 'template_metrics') else {},
                "content_quality": self.quality_scores if hasattr(self, 'quality_scores') else {},
                "integrated_analytics": self.analytics_data if hasattr(self, 'analytics_data') else {},
                "recommendations": self._get_recommendations_data(),
                "export_history": self._get_export_history_data(),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Create and show Unified Export Center
            from gui.components.unified_export_center import UnifiedExportCenter
            export_center = UnifiedExportCenter()
            
            # Override the data getter to return our analytics data
            export_center._get_data_for_type = lambda data_type: export_data
            
            export_center.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to open export center: {e}")
    
    def on_template_analytics_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle template analytics load completion."""
        if success and data_type == "template_analytics":
            # Refresh the template analytics display
            self.refresh_template_analytics()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load template analytics: {message}")
    
    def on_quality_data_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle quality data load completion."""
        if success and data_type == "content_quality":
            # Refresh the quality display
            self.refresh_content_quality()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load quality data: {message}")
    
    def on_recommendations_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle recommendations load completion."""
        if success and data_type == "recommendations":
            # Refresh the recommendations display
            self.refresh_recommendations()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load recommendations: {message}")
    
    def _get_recommendations_data(self):
        """Get recommendations data for export."""
        try:
            # This would integrate with your recommendations system
            return {
                "recommendations": [],
                "total_recommendations": 0,
                "export_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"recommendations": [], "error": f"Failed to load recommendations: {e}"}
    
    def _get_export_history_data(self):
        """Get export history data for export."""
        try:
            # This would integrate with your export history
            return {
                "export_history": [],
                "total_exports": 0,
                "export_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"export_history": [], "error": f"Failed to load export history: {e}"} 