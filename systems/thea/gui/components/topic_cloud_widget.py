#!/usr/bin/env python3
"""
Topic Cloud Widget - GUI component for topic visualization
=========================================================

Provides an interactive topic cloud widget that displays:
- Topic frequency as font size
- Color-coded topics by category
- Interactive tooltips with details
- Export functionality
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QSizePolicy, QToolTip, QMenu,
    QSlider, QSpinBox, QComboBox, QGroupBox, QFormLayout
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPixmap, QIcon

from dreamscape.core.topic_analyzer import TopicAnalyzer
from dreamscape.core.export_manager import ExportManager

logger = logging.getLogger(__name__)


class TopicCloudWidget(QWidget):
    """Interactive topic cloud widget for visualizing topic frequencies."""
    
    # Signals
    topic_selected = pyqtSignal(dict)  # Selected topic data
    export_requested = pyqtSignal(str, str)  # format, file_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.topic_analyzer = TopicAnalyzer()
        self.export_manager = ExportManager()
        
        # Topic data
        self.topics = []
        self.topic_cloud_data = []
        self.selected_topic = None
        
        # Display settings
        self.max_topics = 50
        self.min_font_size = 12
        self.max_font_size = 48
        self.color_scheme = 'default'
        
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
        
        # Topic cloud display
        self.create_topic_cloud_display(layout)
        
        # Status bar
        self.create_status_bar(layout)
        
    def create_header(self, layout):
        """Create the header section."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title = QLabel("📊 Topic Cloud")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_topics)
        header_layout.addWidget(self.refresh_btn)
        
        # Export button
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.show_export_menu)
        header_layout.addWidget(self.export_btn)
        
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
    def create_controls(self, layout):
        """Create the control panel."""
        controls_group = QGroupBox("Display Controls")
        controls_layout = QFormLayout(controls_group)
        
        # Max topics slider
        self.max_topics_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_topics_slider.setRange(10, 100)
        self.max_topics_slider.setValue(self.max_topics)
        self.max_topics_slider.valueChanged.connect(self.on_max_topics_changed)
        controls_layout.addRow("Max Topics:", self.max_topics_slider)
        
        # Max topics spinbox
        self.max_topics_spin = QSpinBox()
        self.max_topics_spin.setRange(10, 100)
        self.max_topics_spin.setValue(self.max_topics)
        self.max_topics_spin.valueChanged.connect(self.on_max_topics_spin_changed)
        controls_layout.addRow("", self.max_topics_spin)
        
        # Color scheme
        self.color_scheme_combo = QComboBox()
        self.color_scheme_combo.addItems(['default', 'rainbow', 'heat', 'cool'])
        self.color_scheme_combo.currentTextChanged.connect(self.on_color_scheme_changed)
        controls_layout.addRow("Color Scheme:", self.color_scheme_combo)
        
        # Analysis method
        self.analysis_method_combo = QComboBox()
        self.analysis_method_combo.addItems(['simple', 'advanced'])
        self.analysis_method_combo.currentTextChanged.connect(self.on_analysis_method_changed)
        controls_layout.addRow("Analysis Method:", self.analysis_method_combo)
        
        layout.addWidget(controls_group)
        
    def create_topic_cloud_display(self, layout):
        """Create the topic cloud display area."""
        # Scroll area for topic cloud
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Topic cloud widget
        self.topic_cloud_widget = TopicCloudDisplayWidget()
        self.topic_cloud_widget.topic_clicked.connect(self.on_topic_clicked)
        self.scroll_area.setWidget(self.topic_cloud_widget)
        
        layout.addWidget(self.scroll_area)
        
    def create_status_bar(self, layout):
        """Create the status bar."""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("Ready to display topics")
        status_layout.addWidget(self.status_label)
        
        # Topic count
        self.topic_count_label = QLabel("Topics: 0")
        status_layout.addWidget(self.topic_count_label)
        
        # Total frequency
        self.total_freq_label = QLabel("Total Frequency: 0")
        status_layout.addWidget(self.total_freq_label)
        
        status_layout.addStretch()
        layout.addWidget(status_frame)
        
    def set_conversations(self, conversations: List[Dict[str, Any]]):
        """Set conversations and generate topic cloud."""
        try:
            self.status_label.setText("Analyzing topics...")
            
            # Get analysis method
            method = self.analysis_method_combo.currentText()
            
            # Extract topics
            topic_data = self.topic_analyzer.get_conversation_topics(
                conversations, 
                method=method, 
                max_topics=self.max_topics
            )
            
            self.topics = topic_data.get('topics', [])
            
            # Generate cloud data
            self.topic_cloud_data = self.topic_analyzer.generate_topic_cloud_data(
                self.topics, 
                max_size=self.max_topics
            )
            
            # Update display
            self.update_topic_cloud_display()
            
            # Update status
            total_freq = sum(topic.get('frequency', 0) for topic in self.topics)
            self.topic_count_label.setText(f"Topics: {len(self.topics)}")
            self.total_freq_label.setText(f"Total Frequency: {total_freq}")
            self.status_label.setText("Topic cloud updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to set conversations: {e}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def update_topic_cloud_display(self):
        """Update the topic cloud display."""
        if not self.topic_cloud_data:
            self.topic_cloud_widget.clear_topics()
            return
        
        # Apply color scheme
        colored_data = self.apply_color_scheme(self.topic_cloud_data)
        
        # Update widget
        self.topic_cloud_widget.set_topics(colored_data)
        
    def apply_color_scheme(self, topic_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply color scheme to topic data."""
        if not topic_data:
            return topic_data
        
        scheme = self.color_scheme_combo.currentText()
        colored_data = []
        
        for i, topic in enumerate(topic_data):
            topic_copy = topic.copy()
            
            if scheme == 'rainbow':
                # Rainbow colors
                hue = (i * 360 / len(topic_data)) % 360
                color = QColor.fromHsv(int(hue), 200, 200)
            elif scheme == 'heat':
                # Heat map (red to yellow)
                intensity = topic.get('percentage', 0) / 100.0
                color = QColor.fromHsv(0, 255, int(255 * (0.5 + 0.5 * intensity)))
            elif scheme == 'cool':
                # Cool colors (blue to green)
                intensity = topic.get('percentage', 0) / 100.0
                hue = 180 + int(60 * intensity)  # Blue to green
                color = QColor.fromHsv(hue, 200, 200)
            else:
                # Default (blue shades)
                intensity = topic.get('percentage', 0) / 100.0
                color = QColor.fromHsv(240, 200, int(100 + 155 * intensity))
            
            topic_copy['color'] = color
            colored_data.append(topic_copy)
        
        return colored_data
    
    def on_max_topics_changed(self, value):
        """Handle max topics slider change."""
        self.max_topics = value
        self.max_topics_spin.setValue(value)
        self.update_topic_cloud_display()
    
    def on_max_topics_spin_changed(self, value):
        """Handle max topics spinbox change."""
        self.max_topics = value
        self.max_topics_slider.setValue(value)
        self.update_topic_cloud_display()
    
    def on_color_scheme_changed(self, scheme):
        """Handle color scheme change."""
        self.color_scheme = scheme
        self.update_topic_cloud_display()
    
    def on_analysis_method_changed(self, method):
        """Handle analysis method change."""
        # This would typically trigger a re-analysis
        # For now, just update the display
        self.update_topic_cloud_display()
    
    def on_topic_clicked(self, topic_data: Dict[str, Any]):
        """Handle topic click."""
        self.selected_topic = topic_data
        self.topic_selected.emit(topic_data)
        
        # Show tooltip with details
        tooltip_text = f"""
        <b>{topic_data.get('text', 'Unknown')}</b><br/>
        Frequency: {topic_data.get('frequency', 0)}<br/>
        Weight: {topic_data.get('weight', 0)}<br/>
        Percentage: {topic_data.get('percentage', 0)}%
        """
        QToolTip.showText(self.cursor().pos(), tooltip_text, self)
    
    def refresh_topics(self):
        """Refresh the topic cloud."""
        self.update_topic_cloud_display()
        self.status_label.setText("Topic cloud refreshed")
    
    def show_export_menu(self):
        """Show export menu."""
        menu = QMenu(self)
        
        # CSV export
        csv_action = QAction("Export to CSV", self)
        csv_action.triggered.connect(lambda: self.export_topics('csv'))
        menu.addAction(csv_action)
        
        # JSON export
        json_action = QAction("Export to JSON", self)
        json_action.triggered.connect(lambda: self.export_topics('json'))
        menu.addAction(json_action)
        
        # PDF export
        pdf_action = QAction("Export to PDF", self)
        pdf_action.triggered.connect(lambda: self.export_topics('pdf'))
        menu.addAction(pdf_action)
        
        menu.exec(self.export_btn.mapToGlobal(self.export_btn.rect().bottomLeft()))
    
    def export_topics(self, format: str):
        """Export topics to specified format."""
        if not self.topics:
            self.status_label.setText("No topics to export")
            return
        
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            # Get file path
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                f"Export Topics ({format.upper()})", 
                f"topics_export.{format}", 
                f"{format.upper()} Files (*.{format})"
            )
            
            if file_path:
                # Prepare topic data
                topic_data = {
                    'topics': self.topics,
                    'total_topics': len(self.topics),
                    'analysis_method': self.analysis_method_combo.currentText(),
                    'max_topics': self.max_topics,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Export
                if format == 'csv':
                    self.export_manager.export_topic_data(topic_data, file_path, 'csv')
                elif format == 'json':
                    self.export_manager.export_topic_data(topic_data, file_path, 'json')
                elif format == 'pdf':
                    self.export_manager.export_topic_data(topic_data, file_path, 'pdf')
                
                self.status_label.setText(f"Topics exported to {format.upper()}")
                self.export_requested.emit(format, file_path)
                
        except Exception as e:
            logger.error(f"Failed to export topics: {e}")
            self.status_label.setText(f"Export failed: {str(e)}")


class TopicCloudDisplayWidget(QWidget):
    """Widget for displaying the actual topic cloud."""
    
    # Signals
    topic_clicked = pyqtSignal(dict)  # Clicked topic data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.topics = []
        self.topic_rects = {}  # Store topic rectangles for click detection
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)
        
        # Enable mouse tracking for tooltips
        self.setMouseTracking(True)
        
    def set_topics(self, topics: List[Dict[str, Any]]):
        """Set topics to display."""
        self.topics = topics
        self.topic_rects.clear()
        self.update()
        
    def clear_topics(self):
        """Clear all topics."""
        self.topics = []
        self.topic_rects.clear()
        self.update()
        
    def paintEvent(self, event):
        """Paint the topic cloud."""
        if not self.topics:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate layout
        self.layout_topics(painter)
        
        # Draw topics
        for topic in self.topics:
            self.draw_topic(painter, topic)
    
    def layout_topics(self, painter: QPainter):
        """Layout topics in the available space."""
        if not self.topics:
            return
        
        # Simple layout algorithm
        width = self.width()
        height = self.height()
        
        # Sort topics by size (largest first)
        sorted_topics = sorted(self.topics, key=lambda x: x.get('size', 0), reverse=True)
        
        # Simple grid layout
        cols = max(1, int(len(sorted_topics) ** 0.5))
        rows = (len(sorted_topics) + cols - 1) // cols
        
        cell_width = width / cols
        cell_height = height / rows
        
        self.topic_rects.clear()
        
        for i, topic in enumerate(sorted_topics):
            row = i // cols
            col = i % cols
            
            # Calculate position with some randomness
            x = col * cell_width + (cell_width - 100) / 2
            y = row * cell_height + (cell_height - 50) / 2
            
            # Store rectangle for click detection
            font_size = topic.get('size', 20)
            rect = QRect(int(x), int(y), int(font_size * 3), int(font_size * 1.5))
            self.topic_rects[rect] = topic
            
            # Store position in topic data
            topic['x'] = x
            topic['y'] = y
    
    def draw_topic(self, painter: QPainter, topic: Dict[str, Any]):
        """Draw a single topic."""
        text = topic.get('text', '')
        size = topic.get('size', 20)
        color = topic.get('color', QColor(0, 0, 255))
        x = topic.get('x', 0)
        y = topic.get('y', 0)
        
        # Set font
        font = QFont("Arial", size)
        painter.setFont(font)
        
        # Set color
        painter.setPen(QPen(color))
        
        # Draw text
        painter.drawText(int(x), int(y), text)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is on a topic
            for rect, topic in self.topic_rects.items():
                if rect.contains(event.pos()):
                    self.topic_clicked.emit(topic)
                    break
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for tooltips."""
        # Check if mouse is over a topic
        for rect, topic in self.topic_rects.items():
            if rect.contains(event.pos()):
                tooltip_text = f"{topic.get('text', '')} ({topic.get('frequency', 0)})"
                QToolTip.showText(event.globalPos(), tooltip_text, self)
                break 