#!/usr/bin/env python3
"""
Content Analytics Widget - Reusable GUI component for content analytics
======================================================================

A compact, reusable widget that provides:
- Template performance metrics
- Content quality indicators
- Quick optimization insights
- Real-time analytics updates
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QProgressBar, QGroupBox, QGridLayout, QTextEdit,
    QComboBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

# Import our content analytics systems
from dreamscape.core.templates.template_processors import TemplatePerformanceAnalytics
from dreamscape.core.content.content_quality_scoring import ContentQualityScorer
from dreamscape.core.analytics.content_analytics_integration import ContentAnalyticsIntegration
from dreamscape.core.utils.database_mixin import ensure_prompt_templates_table

logger = logging.getLogger(__name__)

class ContentAnalyticsWidget(QWidget):
    """Compact content analytics widget for embedding in other panels."""
    
    # Signals
    analytics_updated = pyqtSignal(dict)     # Analytics data updated
    template_selected = pyqtSignal(str)      # Template selected for detailed view
    quality_dimension_selected = pyqtSignal(str)  # Quality dimension selected
    
    def __init__(self, parent=None, compact_mode: bool = True):
        super().__init__(parent)
        self.compact_mode = compact_mode
        
        # EDIT START: Ensure analytics DB schema before any queries
        analytics_db_path = Path("data/template_analytics/template_analytics.db")
        ensure_prompt_templates_table(analytics_db_path)
        # EDIT END

        # Initialize analytics systems
        self.template_analytics = TemplatePerformanceAnalytics()
        self.content_scorer = ContentQualityScorer()
        self.analytics_integration = ContentAnalyticsIntegration()
        
        # Analytics state
        self.analytics_data = {}
        self.template_metrics = {}
        self.quality_scores = {}
        
        self.init_ui()
        self.load_analytics_data()
        
        # Start refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        self.create_header(layout)
        
        # Main content
        if self.compact_mode:
            self.create_compact_content(layout)
        else:
            self.create_full_content(layout)
        
        # Status bar
        self.create_status_bar(layout)
    
    def create_header(self, layout):
        """Create the header section."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title = QLabel("📊 Content Analytics")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Mode toggle
        if not self.compact_mode:
            self.mode_btn = QPushButton("📱 Compact")
            self.mode_btn.clicked.connect(self.toggle_mode)
            header_layout.addWidget(self.mode_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.clicked.connect(self.refresh_analytics)
        header_layout.addWidget(self.refresh_btn)
        
        header_layout.addStretch()
        layout.addWidget(header_frame)
    
    def create_compact_content(self, layout):
        """Create compact content layout."""
        # Key metrics grid
        metrics_group = QGroupBox("Key Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        # Template metrics
        self.template_count_label = QLabel("0")
        self.template_count_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.template_count_label.setStyleSheet("color: #0078d4;")
        metrics_layout.addWidget(QLabel("Templates:"), 0, 0)
        metrics_layout.addWidget(self.template_count_label, 0, 1)
        
        self.success_rate_label = QLabel("0%")
        self.success_rate_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.success_rate_label.setStyleSheet("color: #107c10;")
        metrics_layout.addWidget(QLabel("Success Rate:"), 0, 2)
        metrics_layout.addWidget(self.success_rate_label, 0, 3)
        
        # Quality metrics
        self.quality_score_label = QLabel("0.0")
        self.quality_score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.quality_score_label.setStyleSheet("color: #d83b01;")
        metrics_layout.addWidget(QLabel("Quality Score:"), 1, 0)
        metrics_layout.addWidget(self.quality_score_label, 1, 1)
        
        self.optimization_opps_label = QLabel("0")
        self.optimization_opps_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.optimization_opps_label.setStyleSheet("color: #8661c5;")
        metrics_layout.addWidget(QLabel("Optimizations:"), 1, 2)
        metrics_layout.addWidget(self.optimization_opps_label, 1, 3)
        
        layout.addWidget(metrics_group)
        
        # Quick insights
        insights_group = QGroupBox("Quick Insights")
        insights_layout = QVBoxLayout(insights_group)
        
        self.insights_text = QTextEdit()
        self.insights_text.setMaximumHeight(80)
        self.insights_text.setReadOnly(True)
        insights_layout.addWidget(self.insights_text)
        
        layout.addWidget(insights_group)
    
    def create_full_content(self, layout):
        """Create full content layout."""
        # Template performance section
        template_group = QGroupBox("Template Performance")
        template_layout = QGridLayout(template_group)
        
        self.top_template_label = QLabel("None")
        self.top_template_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        template_layout.addWidget(QLabel("Top Template:"), 0, 0)
        template_layout.addWidget(self.top_template_label, 0, 1)
        
        self.avg_execution_label = QLabel("0ms")
        template_layout.addWidget(QLabel("Avg Execution:"), 0, 2)
        template_layout.addWidget(self.avg_execution_label, 0, 3)
        
        self.error_rate_label = QLabel("0%")
        template_layout.addWidget(QLabel("Error Rate:"), 1, 0)
        template_layout.addWidget(self.error_rate_label, 1, 1)
        
        layout.addWidget(template_group)
        
        # Quality dimensions
        quality_group = QGroupBox("Quality Dimensions")
        quality_layout = QGridLayout(quality_group)
        
        # Top 4 quality dimensions
        self.quality_dimension_labels = {}
        top_dimensions = ["Readability", "Engagement", "SEO Optimization", "Technical Accuracy"]
        
        for i, dimension in enumerate(top_dimensions):
            row = i // 2
            col = i % 2 * 2
            
            name_label = QLabel(dimension)
            name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            quality_layout.addWidget(name_label, row, col)
            
            score_label = QLabel("0.0")
            score_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            quality_layout.addWidget(score_label, row, col + 1)
            
            self.quality_dimension_labels[dimension] = score_label
        
        layout.addWidget(quality_group)
        
        # Recommendations
        rec_group = QGroupBox("Top Recommendations")
        rec_layout = QVBoxLayout(rec_group)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(100)
        self.recommendations_text.setReadOnly(True)
        rec_layout.addWidget(self.recommendations_text)
        
        layout.addWidget(rec_group)
    
    def create_status_bar(self, layout):
        """Create the status bar."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        # Progress indicator
        self.progress_indicator = QLabel("●")
        self.progress_indicator.setStyleSheet("color: #107c10; font-size: 12px;")
        status_layout.addWidget(self.progress_indicator)
        
        status_layout.addStretch()
        layout.addWidget(status_frame)
    
    def load_analytics_data(self):
        """Load analytics data."""
        try:
            self.status_label.setText("Loading...")
            self.progress_indicator.setStyleSheet("color: #d83b01; font-size: 12px;")
            
            # Load template analytics
            self.template_metrics = self.template_analytics.get_performance_report()
            
            # Load content quality data
            self.quality_scores = self.content_scorer.get_quality_summary()
            
            # Get integrated analytics
            self.analytics_data = self.analytics_integration.get_analytics_summary()
            
            # Update display
            self.update_display()
            
            self.status_label.setText("Updated")
            self.progress_indicator.setStyleSheet("color: #107c10; font-size: 12px;")
            
            # Emit signal
            self.analytics_updated.emit(self.analytics_data)
            
        except Exception as e:
            logger.error(f"Failed to load analytics data: {e}")
            self.status_label.setText(f"Error: {e}")
            self.progress_indicator.setStyleSheet("color: #d83b01; font-size: 12px;")
    
    def update_display(self):
        """Update the display with current data."""
        try:
            # Update compact mode display
            if self.compact_mode:
                self.update_compact_display()
            else:
                self.update_full_display()
                
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
    
    def update_compact_display(self):
        """Update compact mode display."""
        # Template metrics
        total_templates = len(self.template_metrics.get('templates', []))
        self.template_count_label.setText(str(total_templates))
        
        avg_success = self.template_metrics.get('average_success_rate', 0)
        self.success_rate_label.setText(f"{avg_success:.1f}%")
        
        # Quality metrics
        avg_quality = self.quality_scores.get('average_score', 0)
        self.quality_score_label.setText(f"{avg_quality:.1f}")
        
        optimization_opps = len(self.analytics_data.get('recommendations', []))
        self.optimization_opps_label.setText(str(optimization_opps))
        
        # Quick insights
        insights = self.generate_quick_insights()
        self.insights_text.setPlainText(insights)
    
    def update_full_display(self):
        """Update full mode display."""
        # Template performance
        templates = self.template_metrics.get('templates', [])
        if templates:
            top_template = max(templates, key=lambda x: x.get('usage_count', 0))
            self.top_template_label.setText(top_template.get('name', 'Unknown'))
        else:
            self.top_template_label.setText("None")
        
        avg_execution = self.template_metrics.get('average_execution_time', 0)
        self.avg_execution_label.setText(f"{avg_execution:.0f}ms")
        
        error_rate = 100 - self.template_metrics.get('average_success_rate', 0)
        self.error_rate_label.setText(f"{error_rate:.1f}%")
        
        # Quality dimensions
        dimension_scores = self.quality_scores.get('dimension_scores', {})
        for dimension, label in self.quality_dimension_labels.items():
            score = dimension_scores.get(dimension, 0)
            label.setText(f"{score:.1f}")
        
        # Recommendations
        recommendations = self.analytics_data.get('recommendations', [])
        if recommendations:
            top_recs = recommendations[:3]  # Top 3 recommendations
            rec_text = "\n".join([f"• {rec.get('recommendation', '')}" for rec in top_recs])
            self.recommendations_text.setPlainText(rec_text)
        else:
            self.recommendations_text.setPlainText("No recommendations available")
    
    def generate_quick_insights(self) -> str:
        """Generate quick insights text."""
        insights = []
        
        # Template insights
        templates = self.template_metrics.get('templates', [])
        if templates:
            top_template = max(templates, key=lambda x: x.get('usage_count', 0))
            insights.append(f"Top template: {top_template.get('name', 'Unknown')}")
        
        # Quality insights
        avg_quality = self.quality_scores.get('average_score', 0)
        if avg_quality > 8.0:
            insights.append("Content quality is excellent")
        elif avg_quality > 6.0:
            insights.append("Content quality is good")
        else:
            insights.append("Content quality needs improvement")
        
        # Optimization insights
        optimization_opps = len(self.analytics_data.get('recommendations', []))
        if optimization_opps > 0:
            insights.append(f"{optimization_opps} optimization opportunities")
        
        return " | ".join(insights) if insights else "No insights available"
    
    def refresh_analytics(self):
        """Refresh analytics data."""
        self.load_analytics_data()
    
    def toggle_mode(self):
        """Toggle between compact and full mode."""
        # This would require recreating the UI, so we'll just update the button text
        if hasattr(self, 'mode_btn'):
            if self.compact_mode:
                self.mode_btn.setText("📊 Full")
            else:
                self.mode_btn.setText("📱 Compact")
    
    def set_compact_mode(self, compact: bool):
        """Set compact mode."""
        self.compact_mode = compact
        # Clear and recreate UI
        for child in self.children():
            if isinstance(child, (QGroupBox, QFrame)):
                child.deleteLater()
        
        # Recreate UI
        layout = self.layout()
        if layout:
            # Clear existing widgets
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Recreate
            self.create_header(layout)
            if self.compact_mode:
                self.create_compact_content(layout)
            else:
                self.create_full_content(layout)
            self.create_status_bar(layout)
            
            # Update display
            self.update_display()


class TemplatePerformanceWidget(QWidget):
    """Focused widget for template performance analytics."""
    
    template_selected = pyqtSignal(str)  # Template selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # EDIT START: Ensure analytics DB schema before any queries
        analytics_db_path = Path("data/template_analytics/template_analytics.db")
        ensure_prompt_templates_table(analytics_db_path)
        # EDIT END
        self.template_analytics = TemplatePerformanceAnalytics()
        self.template_metrics = {}
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        header = QLabel("📋 Template Performance")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        self.total_usage_label = QLabel("0")
        self.total_usage_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(QLabel("Total Usage:"), 0, 0)
        metrics_layout.addWidget(self.total_usage_label, 0, 1)
        
        self.success_rate_label = QLabel("0%")
        self.success_rate_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(QLabel("Success Rate:"), 0, 2)
        metrics_layout.addWidget(self.success_rate_label, 0, 3)
        
        self.avg_time_label = QLabel("0ms")
        self.avg_time_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(QLabel("Avg Time:"), 1, 0)
        metrics_layout.addWidget(self.avg_time_label, 1, 1)
        
        self.error_count_label = QLabel("0")
        self.error_count_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        metrics_layout.addWidget(QLabel("Errors:"), 1, 2)
        metrics_layout.addWidget(self.error_count_label, 1, 3)
        
        layout.addWidget(metrics_group)
        
        # Top templates
        top_group = QGroupBox("Top Templates")
        top_layout = QVBoxLayout(top_group)
        
        self.top_templates_text = QTextEdit()
        self.top_templates_text.setMaximumHeight(100)
        self.top_templates_text.setReadOnly(True)
        top_layout.addWidget(self.top_templates_text)
        
        layout.addWidget(top_group)
    
    def load_data(self):
        """Load template performance data."""
        try:
            self.template_metrics = self.template_analytics.get_performance_report()
            self.update_display()
        except Exception as e:
            logger.error(f"Failed to load template data: {e}")
    
    def update_display(self):
        """Update the display."""
        # Update metrics
        total_usage = sum(t.get('usage_count', 0) for t in self.template_metrics.get('templates', []))
        self.total_usage_label.setText(str(total_usage))
        
        avg_success = self.template_metrics.get('average_success_rate', 0)
        self.success_rate_label.setText(f"{avg_success:.1f}%")
        
        avg_time = self.template_metrics.get('average_execution_time', 0)
        self.avg_time_label.setText(f"{avg_time:.0f}ms")
        
        total_errors = sum(t.get('error_count', 0) for t in self.template_metrics.get('templates', []))
        self.error_count_label.setText(str(total_errors))
        
        # Update top templates
        templates = self.template_metrics.get('templates', [])
        if templates:
            top_templates = sorted(templates, key=lambda x: x.get('usage_count', 0), reverse=True)[:3]
            top_text = "\n".join([f"• {t.get('name', 'Unknown')} ({t.get('usage_count', 0)} uses)" for t in top_templates])
            self.top_templates_text.setPlainText(top_text)
        else:
            self.top_templates_text.setPlainText("No templates available")


class ContentQualityWidget(QWidget):
    """Focused widget for content quality analytics."""
    
    dimension_selected = pyqtSignal(str)  # Quality dimension selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_scorer = ContentQualityScorer()
        self.quality_scores = {}
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        header = QLabel("✨ Content Quality")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Overall quality
        overall_group = QGroupBox("Overall Quality")
        overall_layout = QGridLayout(overall_group)
        
        self.overall_score_label = QLabel("0.0")
        self.overall_score_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.overall_score_label.setStyleSheet("color: #0078d4;")
        overall_layout.addWidget(QLabel("Score:"), 0, 0)
        overall_layout.addWidget(self.overall_score_label, 0, 1)
        
        self.quality_level_label = QLabel("Unknown")
        self.quality_level_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        overall_layout.addWidget(QLabel("Level:"), 0, 2)
        overall_layout.addWidget(self.quality_level_label, 0, 3)
        
        layout.addWidget(overall_group)
        
        # Quality dimensions
        dimensions_group = QGroupBox("Quality Dimensions")
        dimensions_layout = QGridLayout(dimensions_group)
        
        # Create dimension labels
        self.dimension_labels = {}
        dimensions = ["Readability", "Engagement", "SEO", "Technical", "Structure"]
        
        for i, dimension in enumerate(dimensions):
            row = i // 2
            col = i % 2 * 2
            
            name_label = QLabel(dimension)
            name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            dimensions_layout.addWidget(name_label, row, col)
            
            score_label = QLabel("0.0")
            score_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            dimensions_layout.addWidget(score_label, row, col + 1)
            
            self.dimension_labels[dimension] = score_label
        
        layout.addWidget(dimensions_group)
        
        # Quality summary
        summary_group = QGroupBox("Quality Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.quality_summary_text = QTextEdit()
        self.quality_summary_text.setMaximumHeight(80)
        self.quality_summary_text.setReadOnly(True)
        summary_layout.addWidget(self.quality_summary_text)
        
        layout.addWidget(summary_group) 