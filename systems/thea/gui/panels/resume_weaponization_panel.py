#!/usr/bin/env python3
from gui.debug_handler import debug_button
"""
Dream.OS Resume Weaponization Panel
===================================

GUI panel for weaponizing conversation corpus to extract resume content.
"""

import sys
from gui.debug_handler import debug_button
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QLabel, QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QSpinBox, QCheckBox, QGroupBox, QSplitter,
    QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.legacy.resume_tracker import ResumeTracker
from dreamscape.core.resume_weaponizer import ResumeWeaponizer

logger = logging.getLogger(__name__)

class WeaponizationWorker(QThread):
    """Background worker for resume weaponization."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, weaponizer: ResumeWeaponizer, limit: Optional[int] = None):
        super().__init__()
        self.weaponizer = weaponizer
        self.limit = limit
    
    def run(self):
        """Run weaponization in background thread."""
        try:
            self.progress.emit("Starting resume weaponization...")
            result = self.weaponizer.weaponize_corpus(limit=self.limit)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class ResumeWeaponizationPanel(QWidget):
    """Main resume weaponization panel."""
    
    def __init__(self, memory_manager: MemoryManager, resume_tracker: ResumeTracker):
        super().__init__()
        self.memory_manager = memory_manager
        self.resume_tracker = resume_tracker
        self.weaponizer = ResumeWeaponizer(memory_manager, resume_tracker)
        self.weaponization_result = None
        
        self.init_ui()
        self.load_current_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🎯 Resume Weaponization")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Extract skills, projects, and knowledge from your conversation corpus to build comprehensive resumes.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_weaponization_tab(), "🚀 Weaponization")
        self.tab_widget.addTab(self.create_skills_tab(), "💪 Skills")
        self.tab_widget.addTab(self.create_projects_tab(), "🏗️ Projects")
        self.tab_widget.addTab(self.create_knowledge_tab(), "🧠 Knowledge")
        self.tab_widget.addTab(self.create_resume_tab(), "📄 Resume")
        self.tab_widget.addTab(self.create_export_tab(), "💾 Export")
        
        self.setLayout(layout)
    
    @debug_button("create_weaponization_tab", "Resume Weaponization Panel")
    def create_weaponization_tab(self) -> QWidget:
        """Create the main weaponization tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Settings group
        settings_group = QGroupBox("Weaponization Settings")
        settings_layout = QVBoxLayout()
        
        # Conversation limit
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Conversation Limit:"))
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setRange(0, 10000)
        self.limit_spinbox.setValue(0)
        self.limit_spinbox.setSpecialValueText("No limit")
        limit_layout.addWidget(self.limit_spinbox)
        limit_layout.addStretch()
        settings_layout.addLayout(limit_layout)
        
        # Target role
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Target Role:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Software Engineer",
            "Full Stack Developer",
            "AI/ML Engineer",
            "DevOps Engineer",
            "Data Scientist",
            "Product Manager",
            "Technical Lead",
            "Custom..."
        ])
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        role_layout.addWidget(self.role_combo)
        role_layout.addStretch()
        settings_layout.addLayout(role_layout)
        
        # Custom role input
        self.custom_role_input = QLineEdit()
        self.custom_role_input.setPlaceholderText("Enter custom role...")
        self.custom_role_input.setVisible(False)
        settings_layout.addWidget(self.custom_role_input)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Weaponization controls
        controls_layout = QHBoxLayout()
        
        self.weaponize_btn = QPushButton("🚀 Start Weaponization")
        self.weaponize_btn.clicked.connect(self.start_weaponization)
        controls_layout.addWidget(self.weaponize_btn)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_weaponization)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Ready to weaponize conversation corpus")
        layout.addWidget(self.status_label)
        
        # Results
        results_group = QGroupBox("Weaponization Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        widget.setLayout(layout)
        return widget
    
    @debug_button("create_skills_tab", "Resume Weaponization Panel")
    def create_skills_tab(self) -> QWidget:
        """Create the skills tab using shared component."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        widget = QWidget()
        layout = QVBoxLayout()
        # Skills table using shared component
        self.skills_table_group = components.create_data_table(
            title="Skills",
            headers=["Skill", "Category", "Level", "XP", "Last Updated"],
            data=[],  # Will be populated later
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.skills_table = self.skills_table_group.table  # Access the table for updates
        layout.addWidget(self.skills_table_group)
        # Skills summary
        self.skills_summary = QLabel()
        layout.addWidget(self.skills_summary)
        widget.setLayout(layout)
        return widget

    @debug_button("create_projects_tab", "Resume Weaponization Panel")
    def create_projects_tab(self) -> QWidget:
        """Create the projects tab using shared component."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        widget = QWidget()
        layout = QVBoxLayout()
        # Projects table using shared component
        self.projects_table_group = components.create_data_table(
            title="Projects",
            headers=["Project", "Status", "Technologies", "Team Size", "Role", "Impact"],
            data=[],  # Will be populated later
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.projects_table = self.projects_table_group.table  # Access the table for updates
        layout.addWidget(self.projects_table_group)
        # Projects summary
        self.projects_summary = QLabel()
        layout.addWidget(self.projects_summary)
        widget.setLayout(layout)
        return widget
    
    @debug_button("create_knowledge_tab", "Resume Weaponization Panel")
    def create_knowledge_tab(self) -> QWidget:
        """Create the knowledge tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Knowledge display
        self.knowledge_text = QTextEdit()
        self.knowledge_text.setReadOnly(True)
        layout.addWidget(self.knowledge_text)
        
        widget.setLayout(layout)
        return widget
    
    @debug_button("create_resume_tab", "Resume Weaponization Panel")
    def create_resume_tab(self) -> QWidget:
        """Create the resume generation tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Resume controls
        controls_layout = QHBoxLayout()
        
        self.generate_resume_btn = QPushButton("📄 Generate Resume")
        self.generate_resume_btn.clicked.connect(self.generate_resume)
        controls_layout.addWidget(self.generate_resume_btn)
        
        self.generate_prompt_btn = QPushButton("🤖 Generate ChatGPT Prompt")
        self.generate_prompt_btn.clicked.connect(self.generate_prompt)
        controls_layout.addWidget(self.generate_prompt_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Resume display
        self.resume_text = QTextEdit()
        self.resume_text.setReadOnly(True)
        layout.addWidget(self.resume_text)
        
        widget.setLayout(layout)
        return widget
    
    @debug_button("create_export_tab", "Resume Weaponization Panel")
    def create_export_tab(self) -> QWidget:
        """Create the export tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Export controls
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()
        
        # Replace individual export buttons with Unified Export Center
        self.unified_export_btn = QPushButton("🚀 Unified Export Center")
        self.unified_export_btn.clicked.connect(self.show_unified_export_center)
        self.unified_export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        export_layout.addWidget(self.unified_export_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Export status
        self.export_status = QLabel("Ready to export")
        layout.addWidget(self.export_status)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    @debug_button("on_role_changed", "Resume Weaponization Panel")
    def on_role_changed(self, role: str):
        """Handle role selection change."""
        if role == "Custom...":
            self.custom_role_input.setVisible(True)
        else:
            self.custom_role_input.setVisible(False)
    
    @debug_button("start_weaponization", "Resume Weaponization Panel")
    def start_weaponization(self):
        """Start the weaponization process."""
        try:
            limit = self.limit_spinbox.value()
            if limit == 0:
                limit = None
            
            self.weaponize_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.status_label.setText("Starting weaponization...")
            
            # Create and start worker
            self.worker = WeaponizationWorker(self.weaponizer, limit)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.weaponization_finished)
            self.worker.error.connect(self.weaponization_error)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"Failed to start weaponization: {e}")
            self.status_label.setText(f"Error: {e}")
    
    @debug_button("stop_weaponization", "Resume Weaponization Panel")
    def stop_weaponization(self):
        """Stop the weaponization process."""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        self.weaponize_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Weaponization stopped")
    
    @debug_button("update_progress", "Resume Weaponization Panel")
    def update_progress(self, message: str):
        """Update progress display."""
        self.status_label.setText(message)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
    
    @debug_button("weaponization_finished", "Resume Weaponization Panel")
    def weaponization_finished(self, result: Dict[str, Any]):
        """Handle weaponization completion."""
        self.weaponization_result = result
        
        self.weaponize_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        self.status_label.setText("Weaponization complete!")
        
        # Update results display
        summary = f"""
🎯 Weaponization Results:
• Skills Extracted: {result['skills_extracted']}
• Projects Identified: {result['projects_extracted']}
• Knowledge Areas: {result['knowledge_extracted']}

{result['summary']}
"""
        self.results_text.setPlainText(summary)
        
        # Refresh all tabs
        self.load_current_data()
        
        QMessageBox.information(self, "Success", "Resume weaponization completed successfully!")
    
    @debug_button("weaponization_error", "Resume Weaponization Panel")
    def weaponization_error(self, error: str):
        """Handle weaponization error."""
        self.weaponize_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error}")
        
        QMessageBox.critical(self, "Error", f"Weaponization failed: {error}")
    
    @debug_button("load_current_data", "Resume Weaponization Panel")
    def load_current_data(self):
        """Load current data into tables."""
        try:
            # Load skills
            skills = self.resume_tracker.get_skills()
            self.skills_table_group.update_data(
                data=[
                    [skill.name, skill.category, f"{skill.current_level}/{skill.max_level}", str(skill.current_xp), skill.last_updated]
                    for skill in skills
                ]
            )
            self.skills_summary.setText(f"Total Skills: {len(skills)}")
            
            # Load projects
            projects = self.resume_tracker.get_projects()
            self.projects_table_group.update_data(
                data=[
                    [project.name, project.status, ", ".join(project.technologies), str(project.team_size), project.role, project.impact_description or "Medium"]
                    for project in projects
                ]
            )
            self.projects_summary.setText(f"Total Projects: {len(projects)}")
            
            # Load knowledge if available
            if self.weaponization_result and 'skill_tree' in self.weaponization_result:
                knowledge_text = "Knowledge Areas:\n\n"
                skill_tree = self.weaponization_result['skill_tree']
                
                for category, knowledge_items in skill_tree.get('knowledge_areas', {}).items():
                    knowledge_text += f"## {category}\n"
                    for item in knowledge_items:
                        knowledge_text += f"• **{item['topic']}**: {item['description']}\n"
                    knowledge_text += "\n"
                
                self.knowledge_text.setPlainText(knowledge_text)
            
        except Exception as e:
            logger.error(f"Failed to load current data: {e}")
    
    @debug_button("generate_resume", "Resume Weaponization Panel")
    def generate_resume(self):
        """Generate resume from current data."""
        try:
            if self.weaponization_result and 'resume_content' in self.weaponization_result:
                resume_content = self.weaponization_result['resume_content']
            else:
                # Generate basic resume from current data
                skills = self.resume_tracker.get_skills()
                projects = self.resume_tracker.get_projects()
                achievements = self.resume_tracker.get_achievements()
                
                resume_content = "# Professional Resume\n\n"
                resume_content += "## Skills\n\n"
                for skill in skills:
                    resume_content += f"• **{skill.name}**: Level {skill.current_level}\n"
                
                resume_content += "\n## Projects\n\n"
                for project in projects:
                    resume_content += f"### {project.name}\n"
                    resume_content += f"{project.description}\n"
                    resume_content += f"**Technologies:** {', '.join(project.technologies)}\n\n"
            
            self.resume_text.setPlainText(resume_content)
            
        except Exception as e:
            logger.error(f"Failed to generate resume: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate resume: {e}")
    
    @debug_button("generate_prompt", "Resume Weaponization Panel")
    def generate_prompt(self):
        """Generate ChatGPT prompt for resume."""
        try:
            role = self.role_combo.currentText()
            if role == "Custom...":
                role = self.custom_role_input.text() or "Software Engineer"
            
            prompt = self.weaponizer.generate_resume_prompt(role)
            self.resume_text.setPlainText(prompt)
            
        except Exception as e:
            logger.error(f"Failed to generate prompt: {e}")
            QMessageBox.critical(self, "Error", f"Failed to generate prompt: {e}")
    
    @debug_button("show_unified_export_center", "Resume Weaponization Panel")
    def show_unified_export_center(self):
        """Show the Unified Export Center for weaponization data."""
        try:
            # Prepare weaponization data for export
            export_data = {
                "skill_database": self._get_skill_database_data(),
                "resume": self._get_resume_data(),
                "skill_tree": self._get_skill_tree_data(),
                "weaponization_result": self.weaponization_result if hasattr(self, 'weaponization_result') else {},
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Create and show Unified Export Center
            from gui.components.unified_export_center import UnifiedExportCenter
            export_center = UnifiedExportCenter()
            
            # Override the data getter to return our weaponization data
            export_center._get_data_for_type = lambda data_type: export_data
            
            export_center.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to open export center: {e}")
    
    def _get_skill_database_data(self):
        """Get skill database data for export."""
        try:
            if self.resume_tracker:
                skills = self.resume_tracker.get_skills()
                return {
                    "skills": skills,
                    "total_skills": len(skills),
                    "export_timestamp": datetime.now().isoformat()
                }
            else:
                return {"skills": [], "error": "Resume tracker not available"}
        except Exception as e:
            return {"skills": [], "error": f"Failed to load skill database: {e}"}
    
    def _get_resume_data(self):
        """Get resume data for export."""
        try:
            # This would integrate with your resume generation
            return {
                "resume_content": "",
                "export_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"resume_content": "", "error": f"Failed to load resume: {e}"}
    
    def _get_skill_tree_data(self):
        """Get skill tree data for export."""
        try:
            # This would integrate with your skill tree generation
            return {
                "skill_tree": {},
                "export_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"skill_tree": {}, "error": f"Failed to load skill tree: {e}"} 