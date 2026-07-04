#!/usr/bin/env python3
"""
Skill Tree Panel for Thea GUI
Visualizes skill progression and learning journey based on conversation analysis.
"""

import json
from gui.debug_handler import debug_button
import math
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QTabWidget, QCheckBox,
    QSpinBox, QDoubleSpinBox, QFormLayout, QScrollArea, QTreeWidget,
    QTreeWidgetItem, QSlider, QProgressDialog, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsLineItem, QGraphicsRectItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, pyqtSlot, QRectF, QPointF
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPen, QBrush, QColor, QPainter

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.memory_system import MemoryAPI
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine

class SkillNode(QGraphicsEllipseItem):
    """Custom graphics item for skill nodes."""
    
    def __init__(self, skill_data: Dict[str, Any], x: float, y: float, parent=None):
        super().__init__(x, y, 80, 80, parent)
        self.skill_data = skill_data
        self.setup_appearance()
        self.setup_tooltip()
    
    def setup_appearance(self):
        """Setup the visual appearance of the skill node."""
        # Set colors based on skill level
        level = self.skill_data.get('level', 1)
        if level >= 5:
            color = QColor(255, 215, 0)  # Gold
        elif level >= 3:
            color = QColor(138, 43, 226)  # Purple
        elif level >= 2:
            color = QColor(0, 128, 255)  # Blue
        else:
            color = QColor(128, 128, 128)  # Gray
        
        # Set brush and pen
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor(0, 0, 0), 2))
        
        # Make it selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
    
    def setup_tooltip(self):
        """Setup tooltip for the skill node."""
        skill_name = self.skill_data.get('name', 'Unknown Skill')
        level = self.skill_data.get('level', 1)
        xp = self.skill_data.get('xp', 0)
        description = self.skill_data.get('description', 'No description available')
        
        tooltip = f"<b>{skill_name}</b><br>"
        tooltip += f"Level: {level}<br>"
        tooltip += f"XP: {xp}<br>"
        tooltip += f"<br>{description}"

        self.setToolTip(tooltip)

    def mousePressEvent(self, event):
        """Emit signal when the node is clicked."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.scene() and hasattr(self.scene().views()[0], 'skill_selected'):
                self.scene().views()[0].skill_selected.emit(self.skill_data)
        super().mousePressEvent(event)

class SkillTreeGraphicsView(QGraphicsView):
    """Custom graphics view for skill tree visualization."""
    
    skill_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # Setup scene
        self.setup_scene()
    
    def setup_scene(self):
        """Setup the graphics scene."""
        # Set scene size
        self.scene.setSceneRect(QRectF(0, 0, 2000, 1500))
        
        # Add background
        background = QGraphicsRectItem(0, 0, 2000, 1500)
        background.setBrush(QBrush(QColor(240, 240, 240)))
        background.setPen(QPen(QColor(200, 200, 200)))
        self.scene.addItem(background)
    
    @debug_button("add_skill_node", "Skill Tree Panel")
    def add_skill_node(self, skill_data: Dict[str, Any], x: float, y: float) -> SkillNode:
        """Add a skill node to the scene."""
        node = SkillNode(skill_data, x, y)
        self.scene.addItem(node)
        
        # Add skill name text
        text = QGraphicsTextItem(skill_data.get('name', 'Unknown'), node)
        text.setDefaultTextColor(QColor(0, 0, 0))
        text.setFont(QFont("Arial", 8))
        
        # Center text on node
        text_rect = text.boundingRect()
        text.setPos(40 - text_rect.width() / 2, 40 - text_rect.height() / 2)
        
        return node
    
    @debug_button("add_connection_line", "Skill Tree Panel")
    def add_connection_line(self, start_node: SkillNode, end_node: SkillNode):
        """Add a connection line between two skill nodes."""
        # Calculate line positions
        start_pos = start_node.pos() + QPointF(40, 40)  # Center of start node
        end_pos = end_node.pos() + QPointF(40, 40)      # Center of end node
        
        # Create line
        line = QGraphicsLineItem(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
        line.setPen(QPen(QColor(100, 100, 100), 2))
        self.scene.addItem(line)
        
        # Add arrow at the end
        self.add_arrow(end_pos, start_pos)
    
    @debug_button("add_arrow", "Skill Tree Panel")
    def add_arrow(self, end_pos: QPointF, start_pos: QPointF):
        """Add an arrow at the end of a connection line."""
        # Calculate arrow direction
        direction = end_pos - start_pos
        length = math.sqrt(direction.x()**2 + direction.y()**2)
        
        if length == 0:
            return
        
        # Normalize direction
        direction = direction / length
        
        # Calculate arrow points
        arrow_length = 10
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Arrow tip
        tip = end_pos
        
        # Arrow base points
        base1 = end_pos - arrow_length * QPointF(
            direction.x() * math.cos(arrow_angle) - direction.y() * math.sin(arrow_angle),
            direction.x() * math.sin(arrow_angle) + direction.y() * math.cos(arrow_angle)
        )
        
        base2 = end_pos - arrow_length * QPointF(
            direction.x() * math.cos(-arrow_angle) - direction.y() * math.sin(-arrow_angle),
            direction.x() * math.sin(-arrow_angle) + direction.y() * math.cos(-arrow_angle)
        )
        
        # Create arrow polygon
        arrow = QGraphicsRectItem(0, 0, 1, 1)  # Placeholder
        # In a real implementation, you'd create a QGraphicsPolygonItem for the arrow
        
        self.scene.addItem(arrow)

class SkillTreePanel(QWidget):
    """Skill Tree Panel for Thea GUI."""
    
    # Signals
    skill_selected = pyqtSignal(dict)
    skill_tree_updated = pyqtSignal(dict)
    
    def __init__(self, memory_manager: MemoryManager, mmorpg_engine: MMORPGEngine, parent=None):
        super().__init__(parent)
        self.memory_manager = memory_manager
        self.memory_api = MemoryAPI()
        self.mmorpg_engine = mmorpg_engine
        self.current_skills = {}
        self.skill_nodes = {}
        
        # Setup UI
        self._setup_ui()
        self._load_skills()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🌳 Skill Tree Visualization")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left side - Skill tree visualization
        self._create_skill_tree_view(main_splitter)
        
        # Right side - Skill details and controls
        self._create_skill_details_panel(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([800, 400])
    
    @debug_button("_create_skill_tree_view", "Skill Tree Panel")
    def _create_skill_tree_view(self, parent):
        """Create the skill tree visualization view."""
        # Create graphics view
        self.skill_tree_view = SkillTreeGraphicsView()
        self.skill_tree_view.skill_selected.connect(self._on_skill_selected)
        
        # Create controls for the view
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # View controls
        view_group = QGroupBox("View Controls")
        view_layout = QHBoxLayout(view_group)
        
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        view_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        view_layout.addWidget(self.zoom_out_btn)
        
        self.reset_view_btn = QPushButton("🏠 Reset View")
        self.reset_view_btn.clicked.connect(self._reset_view)
        view_layout.addWidget(self.reset_view_btn)
        
        self.fit_view_btn = QPushButton("📐 Fit to View")
        self.fit_view_btn.clicked.connect(self._fit_to_view)
        view_layout.addWidget(self.fit_view_btn)
        
        controls_layout.addWidget(view_group)
        
        # Layout controls
        layout_group = QGroupBox("Layout")
        layout_layout = QHBoxLayout(layout_group)
        
        self.layout_combo = QComboBox()
        self.layout_combo.addItems([
            "Tree Layout",
            "Radial Layout", 
            "Grid Layout",
            "Hierarchical Layout"
        ])
        self.layout_combo.currentTextChanged.connect(self._change_layout)
        layout_layout.addWidget(QLabel("Layout:"))
        layout_layout.addWidget(self.layout_combo)
        
        self.refresh_layout_btn = QPushButton("🔄 Refresh")
        self.refresh_layout_btn.clicked.connect(self._refresh_layout)
        layout_layout.addWidget(self.refresh_layout_btn)
        
        controls_layout.addWidget(layout_group)
        
        # Add to splitter
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.skill_tree_view)
        left_layout.addWidget(controls_widget)
        
        parent.addWidget(left_widget)
    
    @debug_button("_create_skill_details_panel", "Skill Tree Panel")
    def _create_skill_details_panel(self, parent):
        """Create the skill details panel."""
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Skill overview
        overview_group = QGroupBox("Skill Overview")
        overview_layout = QGridLayout(overview_group)
        
        self.total_skills_label = QLabel("Total Skills: 0")
        overview_layout.addWidget(self.total_skills_label, 0, 0)
        
        self.max_level_label = QLabel("Max Level: 0")
        overview_layout.addWidget(self.max_level_label, 0, 1)
        
        self.total_xp_label = QLabel("Total XP: 0")
        overview_layout.addWidget(self.total_xp_label, 1, 0)
        
        self.completion_label = QLabel("Completion: 0%")
        overview_layout.addWidget(self.completion_label, 1, 1)
        
        details_layout.addWidget(overview_group)
        
        # Selected skill details
        selected_group = QGroupBox("Selected Skill")
        selected_layout = QVBoxLayout(selected_group)
        
        self.selected_skill_name = QLabel("No skill selected")
        self.selected_skill_name.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        selected_layout.addWidget(self.selected_skill_name)
        
        self.selected_skill_level = QLabel("Level: N/A")
        selected_layout.addWidget(self.selected_skill_level)
        
        self.selected_skill_xp = QLabel("XP: N/A")
        selected_layout.addWidget(self.selected_skill_xp)
        
        self.selected_skill_progress = QProgressBar()
        self.selected_skill_progress.setRange(0, 100)
        self.selected_skill_progress.setValue(0)
        selected_layout.addWidget(self.selected_skill_progress)
        
        self.selected_skill_description = QTextEdit()
        self.selected_skill_description.setReadOnly(True)
        self.selected_skill_description.setMaximumHeight(100)
        self.selected_skill_description.setPlaceholderText("Skill description will appear here...")
        selected_layout.addWidget(self.selected_skill_description)
        
        details_layout.addWidget(selected_group)
        
        # Skill actions using shared component
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        
        actions = [
            {
                "text": "➕ Add Skill",
                "callback": self._add_skill,
                "id": "add_skill"
            },
            {
                "text": "✏️ Edit Skill",
                "callback": self._edit_skill,
                "id": "edit_skill",
                "enabled": False
            },
            {
                "text": "🗑️ Delete Skill",
                "callback": self._delete_skill,
                "id": "delete_skill",
                "enabled": False
            }
        ]
        
        actions_panel = components.create_action_panel(
            title="Actions",
            actions=actions,
            config=ComponentConfig(style=ComponentStyle.PRIMARY)
        )
        
        # Store action buttons for later access
        self.add_skill_btn = actions_panel.findChild(QPushButton, "add_skill")
        self.edit_skill_btn = actions_panel.findChild(QPushButton, "edit_skill")
        self.delete_skill_btn = actions_panel.findChild(QPushButton, "delete_skill")
        
        # Export Center button remains as a standalone
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
        
        # Create actions group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.addWidget(actions_panel)
        actions_layout.addWidget(self.unified_export_btn)
        details_layout.addWidget(actions_group)
        
        # Skill filters
        filters_group = QGroupBox("Filters")
        filters_layout = QVBoxLayout(filters_group)
        
        self.show_unlocked_cb = QCheckBox("Show Unlocked Skills")
        self.show_unlocked_cb.setChecked(True)
        self.show_unlocked_cb.toggled.connect(self._apply_filters)
        filters_layout.addWidget(self.show_unlocked_cb)
        
        self.show_locked_cb = QCheckBox("Show Locked Skills")
        self.show_locked_cb.setChecked(True)
        self.show_locked_cb.toggled.connect(self._apply_filters)
        filters_layout.addWidget(self.show_locked_cb)
        
        self.min_level_spin = QSpinBox()
        self.min_level_spin.setRange(0, 10)
        self.min_level_spin.setValue(0)
        self.min_level_spin.valueChanged.connect(self._apply_filters)
        filters_layout.addWidget(QLabel("Minimum Level:"))
        filters_layout.addWidget(self.min_level_spin)
        
        details_layout.addWidget(filters_group)
        
        parent.addWidget(details_widget)
    
    @debug_button("_load_skills", "Skill Tree Panel")
    def _load_skills(self):
        # EDIT START — Agent 2: Integrate knowledge graph backend for advanced skill tree visualization.
        """Load skills and knowledge graph from the backend."""
        try:
            # Try to use the new knowledge graph API if available
            kg_api = None
            if hasattr(self.mmorpg_engine, 'enhanced_skill_resume_system'):
                kg_api = getattr(self.mmorpg_engine, 'enhanced_skill_resume_system', None)
            if kg_api and hasattr(kg_api, 'get_knowledge_graph'):
                graph = kg_api.get_knowledge_graph()
                self.current_skills = {node['id']: node for node in graph['nodes']}
                self.knowledge_edges = graph['edges']
                self._update_overview()
                self._build_skill_tree_knowledge_graph()
                return
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load knowledge graph: {e}\nFalling back to legacy skill loading.")
        # Fallback to legacy skill loading
        try:
            skills = self.mmorpg_engine.get_skills()
            self.current_skills = {}
            for skill in skills:
                if hasattr(skill, 'name'):
                    skill_dict = {
                        'name': skill.name,
                        'level': getattr(skill, 'current_level', getattr(skill, 'level', 1)),
                        'xp': getattr(skill, 'experience_points', getattr(skill, 'xp', 0)),
                        'max_level': getattr(skill, 'max_level', 100),
                        'description': getattr(skill, 'description', f'{skill.name} skill'),
                        'category': getattr(skill, 'category', 'general')
                    }
                    self.current_skills[skill.name] = skill_dict
            self.knowledge_edges = []
            self._update_overview()
            self._build_skill_tree()
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load skills: {e}")
        # EDIT END
    
    @debug_button("_update_overview", "Skill Tree Panel")
    def _update_overview(self):
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
                title="skill_tree_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
        levels = [skill.get('level', 1) for skill in self.current_skills.values()]
        max_level = max(levels) if levels else 1
        xps = [skill.get('xp', 0) for skill in self.current_skills.values()]
        total_xp = sum(xps) if xps else 0
        
        # Calculate completion percentage
        total_possible_xp = total_skills * 1000  # Assuming 1000 XP per skill max
        completion = (total_xp / total_possible_xp * 100) if total_possible_xp > 0 else 0
        
        self.total_skills_label.setText(f"Total Skills: {total_skills}")
        self.max_level_label.setText(f"Max Level: {max_level}")
        self.total_xp_label.setText(f"Total XP: {total_xp}")
        self.completion_label.setText(f"Completion: {completion:.1f}%")
    
    @debug_button("_build_skill_tree", "Skill Tree Panel")
    def _build_skill_tree(self):
        """Build the skill tree visualization."""
        # Clear existing nodes
        self.skill_tree_view.scene.clear()
        self.skill_nodes.clear()
        
        # Setup scene
        self.skill_tree_view.setup_scene()
        
        # Create skill nodes
        skills_list = list(self.current_skills.values())
        
        for i, skill in enumerate(skills_list):
            # Calculate position based on layout
            layout_type = self.layout_combo.currentText()
            
            if layout_type == "Tree Layout":
                x = 200 + (i % 5) * 200
                y = 100 + (i // 5) * 150
            elif layout_type == "Radial Layout":
                angle = (i / len(skills_list)) * 2 * math.pi
                radius = 300
                x = 500 + radius * math.cos(angle)
                y = 400 + radius * math.sin(angle)
            elif layout_type == "Grid Layout":
                cols = math.ceil(math.sqrt(len(skills_list)))
                x = 100 + (i % cols) * 150
                y = 100 + (i // cols) * 150
            else:  # Hierarchical Layout
                x = 200 + i * 100
                y = 100 + (skill.get('level', 1) - 1) * 120
            
            # Create node
            node = self.skill_tree_view.add_skill_node(skill, x, y)
            self.skill_nodes[skill.get('name', '')] = node
        
        # Add connections (simplified - in reality you'd have skill dependencies)
        nodes_list = list(self.skill_nodes.values())
        for i in range(len(nodes_list) - 1):
            self.skill_tree_view.add_connection_line(nodes_list[i], nodes_list[i + 1])
    
    @debug_button("_build_skill_tree_knowledge_graph", "Skill Tree Panel")
    def _build_skill_tree_knowledge_graph(self):
        # EDIT START — Agent 2: Render nodes and edges from knowledge graph backend.
        """Build the skill tree visualization from the knowledge graph (nodes/edges)."""
        self.skill_tree_view.scene.clear()
        self.skill_nodes.clear()
        self.skill_tree_view.setup_scene()
        # Layout: simple radial for now (can be improved)
        nodes_list = list(self.current_skills.values())
        n = len(nodes_list)
        node_positions = {}
        for i, node in enumerate(nodes_list):
            angle = (i / max(1, n)) * 2 * math.pi
            radius = 400
            x = 600 + radius * math.cos(angle)
            y = 400 + radius * math.sin(angle)
            skill_node = self.skill_tree_view.add_skill_node(node, x, y)
            self.skill_nodes[node['id']] = skill_node
            node_positions[node['id']] = (x, y)
        # Draw edges (dependencies/unlocks)
        for edge in getattr(self, 'knowledge_edges', []):
            src = edge['source']
            tgt = edge['target']
            edge_type = edge.get('type', 'dependency')
            if src in self.skill_nodes and tgt in self.skill_nodes:
                # Style: dependencies = solid, unlocks = dashed
                line = QGraphicsLineItem()
                start_node = self.skill_nodes[src]
                end_node = self.skill_nodes[tgt]
                start_pos = start_node.pos() + QPointF(40, 40)
                end_pos = end_node.pos() + QPointF(40, 40)
                line.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
                if edge_type == 'unlock':
                    pen = QPen(QColor(0, 128, 0), 2, Qt.PenStyle.DashLine)
                else:
                    pen = QPen(QColor(100, 100, 100), 2, Qt.PenStyle.SolidLine)
                line.setPen(pen)
                self.skill_tree_view.scene.addItem(line)
        # EDIT END
    
    @debug_button("_on_skill_selected", "Skill Tree Panel")
    def _on_skill_selected(self, skill_data: Dict[str, Any]):
        """Handle skill selection."""
        skill_name = skill_data.get('name', 'Unknown')
        
        # Update selected skill display
        self.selected_skill_name.setText(skill_name)
        self.selected_skill_level.setText(f"Level: {skill_data.get('level', 1)}")
        self.selected_skill_xp.setText(f"XP: {skill_data.get('xp', 0)}")
        
        # Calculate progress
        current_xp = skill_data.get('xp', 0)
        level = skill_data.get('level', 1)
        xp_for_next = level * 1000  # Simplified XP calculation
        progress = min((current_xp / xp_for_next) * 100, 100) if xp_for_next > 0 else 0
        self.selected_skill_progress.setValue(int(progress))
        
        # Update description
        description = skill_data.get('description', 'No description available')
        self.selected_skill_description.setPlainText(description)
        
        # Enable edit/delete buttons
        self.edit_skill_btn.setEnabled(True)
        self.delete_skill_btn.setEnabled(True)
        
        # Emit signal
        self.skill_selected.emit(skill_data)
    
    @debug_button("_zoom_in", "Skill Tree Panel")
    def _zoom_in(self):
        """Zoom in the view."""
        self.skill_tree_view.scale(1.2, 1.2)
    
    @debug_button("_zoom_out", "Skill Tree Panel")
    def _zoom_out(self):
        """Zoom out the view."""
        self.skill_tree_view.scale(0.8, 0.8)
    
    @debug_button("_reset_view", "Skill Tree Panel")
    def _reset_view(self):
        """Reset the view."""
        self.skill_tree_view.resetTransform()
    
    @debug_button("_fit_to_view", "Skill Tree Panel")
    def _fit_to_view(self):
        """Fit the skill tree to the view."""
        self.skill_tree_view.fitInView(self.skill_tree_view.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    @debug_button("_change_layout", "Skill Tree Panel")
    def _change_layout(self, layout_name: str):
        """Change the skill tree layout."""
        self._build_skill_tree()
    
    @debug_button("_refresh_layout", "Skill Tree Panel")
    def _refresh_layout(self):
        """Refresh the skill tree layout."""
        self._build_skill_tree()
    
    @debug_button("_apply_filters", "Skill Tree Panel")
    def _apply_filters(self):
        """Apply filters to the skill tree."""
        # This would filter the displayed skills based on the filter settings
        # For now, just rebuild the tree
        self._build_skill_tree()
    
    @debug_button("_add_skill", "Skill Tree Panel")
    def _add_skill(self):
        """Add a new skill."""
        # This would open a dialog to add a new skill
        QMessageBox.information(self, "Add Skill", "Add skill functionality will be implemented in the next version.")
    
    @debug_button("_edit_skill", "Skill Tree Panel")
    def _edit_skill(self):
        """Edit the selected skill."""
        # This would open a dialog to edit the selected skill
        QMessageBox.information(self, "Edit Skill", "Edit skill functionality will be implemented in the next version.")
    
    @debug_button("_delete_skill", "Skill Tree Panel")
    def _delete_skill(self):
        """Delete the selected skill."""
        # This would delete the selected skill
        QMessageBox.information(self, "Delete Skill", "Delete skill functionality will be implemented in the next version.")
    
    def show_unified_export_center(self):
        """Show the Unified Export Center for skill tree data."""
        try:
            # Prepare skill tree data for export
            export_data = {
                "skills": self.current_skills if hasattr(self, 'current_skills') else {},
                "knowledge_edges": self.knowledge_edges if hasattr(self, 'knowledge_edges') else [],
                "skill_tree": self._get_skill_tree_data(),
                "skill_overview": self._get_skill_overview_data(),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Create and show Unified Export Center
            from gui.components.unified_export_center import UnifiedExportCenter
            export_center = UnifiedExportCenter()
            
            # Override the data getter to return our skill tree data
            export_center._get_data_for_type = lambda data_type: export_data
            
            export_center.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to open export center: {e}")
    
    def _get_skill_tree_data(self):
        """Get skill tree visualization data for export."""
        try:
            return {
                "total_skills": len(self.current_skills) if hasattr(self, 'current_skills') else 0,
                "skill_categories": self._get_skill_categories(),
                "skill_levels": self._get_skill_levels(),
                "export_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"skill_tree": {}, "error": f"Failed to load skill tree data: {e}"}
    
    def _get_skill_overview(self):
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
                title="skill_tree_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _get_skill_categories(self):
        """Get skill categories for export."""
        try:
            if hasattr(self, 'current_skills'):
                categories = {}
                for skill in self.current_skills.values():
                    category = skill.get('category', 'general')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(skill)
                return categories
            else:
                return {}
        except Exception:
            return {}

    def _get_skill_levels(self):
        """Get skill levels for export."""
        try:
            if hasattr(self, 'current_skills'):
                levels = {}
                for skill in self.current_skills.values():
                    level = skill.get('level', 1)
                    if level not in levels:
                        levels[level] = []
                    levels[level].append(skill)
                return levels
            else:
                return {}
        except Exception:
            return {}
    
    @debug_button("refresh_data", "Skill Tree Panel")
    def refresh_data(self):
        """Refresh the skill tree data using Unified Data Loading System."""
        try:
            from gui.components.unified_load_button import create_unified_load_button
            
            # Create a temporary load button for skills
            load_button = create_unified_load_button(
                data_type="skills",
                text="🔄 Load Skills",
                priority="NORMAL",
                use_cache=True,
                background_load=True,
                parent=self
            )
            
            # Connect load completion to refresh the panel
            load_button.load_completed.connect(self.on_skills_loaded)
            
            # Trigger the load
            load_button.click()
            
        except Exception as e:
            # Fallback to direct load if unified system fails
            self._load_skills()
    
    def on_skills_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle skills load completion."""
        if success and data_type == "skills":
            # Refresh the skills display
            self._load_skills()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load skills: {message}") 