"""
Resume Panel for Thea GUI
Handles resume generation and management with weaponization integration.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QGroupBox, QFormLayout, QLineEdit,
    QSpinBox, QCheckBox, QMessageBox, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QProgressBar
)
from gui.debug_handler import debug_button
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from typing import Dict, List, Optional, Any

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.legacy.resume_tracker import ResumeTracker
from dreamscape.core.resume_weaponizer import ResumeWeaponizer
from datetime import datetime

logger = logging.getLogger(__name__)

class ResumePanel(QWidget):
    """Panel for resume generation and management with weaponization integration."""
    
    # Signals
    resume_generated = pyqtSignal(dict)
    resume_exported = pyqtSignal(str)
    weaponization_requested = pyqtSignal()
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None, 
                 resume_tracker: Optional[ResumeTracker] = None, parent=None):
        super().__init__(parent)
        self.memory_manager = memory_manager
        self.resume_tracker = resume_tracker
        self.weaponizer = None
        self.weaponization_result = None
        
        if memory_manager and resume_tracker:
            self.weaponizer = ResumeWeaponizer(memory_manager, resume_tracker)
        
        self.init_ui()
        self.load_weaponized_data()
    
    def init_ui(self):
        """Initialize the resume UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.tab_widget.addTab(self.create_resume_tab(), "Resume Generator")
        self.tab_widget.addTab(self.create_weaponized_data_tab(), "Weaponized Data")
        self.tab_widget.addTab(self.create_skills_tab(), "Skills")
        self.tab_widget.addTab(self.create_projects_tab(), "Projects")
    
    @debug_button("create_header", "Resume Panel")
    def create_header(self, layout):
        """Create panel header."""
        try:
            # Create simple header with refresh button
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            
            # Title
            title = QLabel("Resume Builder")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            header_layout.addWidget(title)
            
            header_layout.addStretch()
            
            # Refresh button
            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self.refresh_data)
            header_layout.addWidget(refresh_btn)
            
            layout.addWidget(header_widget)
            
        except Exception as e:
            logger.error(f"Error creating panel header: {e}")
            # Fallback: create simple header
            header = QLabel("Resume Builder")
            header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)

    @debug_button("refresh_data", "Resume Panel")
    def refresh_data(self):
        """Refresh all resume data."""
        try:
            logger.info("Refreshing resume data")
            self.load_weaponized_data()
            self._get_skills_data()
            self._get_projects_data()
            logger.info("Resume data refresh completed")
        except Exception as e:
            logger.error(f"Error refreshing resume data: {e}")

    def create_resume_tab(self) -> QWidget:
        """Create the resume generator tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuration section
        self.create_config_section(layout)
        
        # Preview section
        self.create_preview_section(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
        
        return widget

    def create_weaponized_data_tab(self) -> QWidget:
        """Create the weaponized data tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Weaponization status
        status_group = QGroupBox("Weaponization Status")
        status_layout = QVBoxLayout(status_group)
        
        self.weaponization_status = QLabel("No weaponization data loaded")
        status_layout.addWidget(self.weaponization_status)
        
        # Weaponization button
        self.weaponize_btn = QPushButton("Run Weaponization")
        self.weaponize_btn.clicked.connect(self.run_weaponization)
        status_layout.addWidget(self.weaponize_btn)
        
        # Progress bar for weaponization
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # Weaponization results
        results_group = QGroupBox("Weaponization Results")
        results_layout = QVBoxLayout(results_group)
        
        self.weaponization_results = QTextEdit()
        self.weaponization_results.setReadOnly(True)
        self.weaponization_results.setMaximumHeight(200)
        results_layout.addWidget(self.weaponization_results)
        
        # Add the missing weaponized_data_text for compatibility
        self.weaponized_data_text = self.weaponization_results
        
        layout.addWidget(results_group)
        
        return widget

    def create_skills_tab(self) -> QWidget:
        """Create the skills display tab using shared component."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
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
        self.skills_summary = QLabel("No skills loaded")
        layout.addWidget(self.skills_summary)
        
        return widget

    @debug_button("create_projects_tab", "Resume Panel")
    def create_projects_tab(self) -> QWidget:
        """Create the projects display tab using shared component."""
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
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
        self.projects_summary = QLabel("No projects loaded")
        layout.addWidget(self.projects_summary)
        
        return widget
    
    @debug_button("create_config_section", "Resume Panel")
    def create_config_section(self, parent_layout):
        """Create the configuration section."""
        config_group = QGroupBox("Resume Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Personal info
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout(personal_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Your full name")
        personal_layout.addRow("Name:", self.name_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("your.email@example.com")
        personal_layout.addRow("Email:", self.email_edit)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+1 (555) 123-4567")
        personal_layout.addRow("Phone:", self.phone_edit)
        
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("City, State")
        personal_layout.addRow("Location:", self.location_edit)
        
        config_layout.addWidget(personal_group)
        
        # Resume settings
        settings_group = QGroupBox("Resume Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Professional", "Creative", "Minimal", "Modern"])
        self.template_combo.setCurrentText("Professional")
        settings_layout.addRow("Template:", self.template_combo)
        
        self.include_skills = QCheckBox("Include weaponized skills")
        self.include_skills.setChecked(True)
        settings_layout.addRow("Include skills:", self.include_skills)
        
        self.include_projects = QCheckBox("Include weaponized projects")
        self.include_projects.setChecked(True)
        settings_layout.addRow("Include projects:", self.include_projects)
        
        self.include_knowledge = QCheckBox("Include knowledge areas")
        self.include_knowledge.setChecked(True)
        settings_layout.addRow("Include knowledge:", self.include_knowledge)
        
        self.max_length = QSpinBox()
        self.max_length.setRange(1, 5)
        self.max_length.setValue(2)
        self.max_length.setSuffix(" pages")
        settings_layout.addRow("Max length:", self.max_length)
        
        config_layout.addWidget(settings_group)
        
        parent_layout.addWidget(config_group)
    
    @debug_button("create_preview_section", "Resume Panel")
    def create_preview_section(self, parent_layout):
        """Create the preview section."""
        preview_group = QGroupBox("Resume Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview header
        preview_header = QHBoxLayout()
        preview_header.addWidget(QLabel("Generated Resume:"))
        preview_header.addStretch()
        
        # Replace refresh button with Unified Load Button
        from gui.components.unified_load_button import create_unified_load_button
        self.load_resume_btn = create_unified_load_button(
            data_type="resume_data",
            text="🔄 Load Resume Data",
            priority="NORMAL",
            use_cache=True,
            background_load=True,
            parent=self
        )
        
        # Connect load completion to refresh the panel
        self.load_resume_btn.load_completed.connect(self.on_resume_data_loaded)
        
        preview_header.addWidget(self.load_resume_btn)
        
        # Preview content
        self.preview_edit = QTextEdit()
        self.preview_edit.setPlaceholderText("Click 'Generate Resume' to create a preview...")
        self.preview_edit.setReadOnly(True)
        preview_layout.addWidget(self.preview_edit)
        
        parent_layout.addWidget(preview_group)
    
    @debug_button("create_action_buttons", "Resume Panel")
    def create_action_buttons(self, parent_layout):
        """Create the action buttons."""
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        self.generate_btn = QPushButton("📝 Generate Resume")
        self.generate_btn.clicked.connect(self.generate_resume)
        button_layout.addWidget(self.generate_btn)
        
        # Replace individual export buttons with Unified Export Center
        self.unified_export_btn = QPushButton("🚀 Export Center")
        self.unified_export_btn.clicked.connect(self.show_unified_export_center)
        self.unified_export_btn.setEnabled(False)
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
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.unified_export_btn)
        
        parent_layout.addLayout(button_layout)
    
    def on_resume_data_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle resume data load completion."""
        if success and data_type == "resume_data":
            # Refresh the resume data display
            self.load_weaponized_data()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load resume data: {message}")
    
    @debug_button("run_weaponization", "Resume Panel")
    def run_weaponization(self):
        """Run the weaponization process."""
        if not self.weaponizer:
            QMessageBox.warning(self, "Warning", "Weaponizer not available. Please ensure memory manager and resume tracker are initialized.")
            return
        
        try:
            self.weaponize_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.weaponization_status.setText("Running weaponization...")
            
            # Run weaponization with limited conversations for testing
            result = self.weaponizer.weaponize_corpus(limit=50)
            
            self.weaponization_result = result
            self.load_weaponized_data()
            
            self.weaponization_status.setText(f"Weaponization complete: {result['skills_extracted']} skills, {result['projects_extracted']} projects")
            QMessageBox.information(self, "Success", f"Weaponization complete!\n\nSkills: {result['skills_extracted']}\nProjects: {result['projects_extracted']}\nKnowledge: {result['knowledge_extracted']}")
            
        except Exception as e:
            self.weaponization_status.setText(f"Weaponization failed: {e}")
            QMessageBox.critical(self, "Error", f"Weaponization failed: {e}")
        finally:
            self.weaponize_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    @debug_button("load_weaponized_data", "Resume Panel")
    def load_weaponized_data(self):
        """Load weaponized data into the display."""
        try:
            if not self.resume_tracker:
                return
            
            # Load skills
            skills = self.resume_tracker.get_skills()
            self.skills_table.setRowCount(len(skills))
            
            for i, skill in enumerate(skills):
                # EDIT START: Defensive access for skill category (handles missing column or attribute)
                if isinstance(skill, dict):
                    category = skill.get('category', 'Unknown')
                    name = skill.get('name', 'Unknown')
                    current_level = skill.get('current_level', '?')
                    max_level = skill.get('max_level', '?')
                    current_xp = skill.get('current_xp', '?')
                    last_updated = skill.get('last_updated', '')
                else:
                    category = getattr(skill, 'category', 'Unknown')
                    name = getattr(skill, 'name', 'Unknown')
                    current_level = getattr(skill, 'current_level', '?')
                    max_level = getattr(skill, 'max_level', '?')
                    current_xp = getattr(skill, 'current_xp', '?')
                    last_updated = getattr(skill, 'last_updated', '')
                # Defensive: always show something for category
                self.skills_table.setItem(i, 0, QTableWidgetItem(str(name)))
                self.skills_table.setItem(i, 1, QTableWidgetItem(str(category)))
                self.skills_table.setItem(i, 2, QTableWidgetItem(f"{current_level}/{max_level}"))
                self.skills_table.setItem(i, 3, QTableWidgetItem(str(current_xp)))
                self.skills_table.setItem(i, 4, QTableWidgetItem(str(last_updated)))
                # EDIT END: Defensive access for skill category
            
            self.skills_summary.setText(f"Total Skills: {len(skills)}")
            
            # Load projects
            projects = self.resume_tracker.get_projects()
            self.projects_table.setRowCount(len(projects))
            
            for i, project in enumerate(projects):
                self.projects_table.setItem(i, 0, QTableWidgetItem(project.name))
                self.projects_table.setItem(i, 1, QTableWidgetItem(project.status))
                self.projects_table.setItem(i, 2, QTableWidgetItem(", ".join(project.technologies)))
                self.projects_table.setItem(i, 3, QTableWidgetItem(str(project.team_size)))
                self.projects_table.setItem(i, 4, QTableWidgetItem(project.role))
                self.projects_table.setItem(i, 5, QTableWidgetItem(project.impact_description or "Medium"))
            
            self.projects_summary.setText(f"Total Projects: {len(projects)}")
            
            # Update weaponized data display
            if self.weaponization_result:
                data_text = f"""
# Weaponized Data Summary

## Skills Extracted: {self.weaponization_result['skills_extracted']}
## Projects Identified: {self.weaponization_result['projects_extracted']}
## Knowledge Areas: {self.weaponization_result['knowledge_extracted']}

## Generated Resume Content:
{self.weaponization_result.get('resume_content', 'No resume content available')}

## Skill Tree:
{self._format_skill_tree(self.weaponization_result.get('skill_tree', {}))}
"""
                self.weaponized_data_text.setPlainText(data_text)
            else:
                self.weaponized_data_text.setPlainText("No weaponized data available. Run weaponization first.")
                
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load weaponized data: {e}")
    
    def _format_skill_tree(self, skill_tree: Dict) -> str:
        """Format skill tree for display."""
        if not skill_tree:
            return "No skill tree available"
        
        formatted = []
        for category, subcategories in skill_tree.items():
            if isinstance(subcategories, dict):
                formatted.append(f"\n## {category.title()}")
                for subcategory, skills in subcategories.items():
                    if skills:
                        formatted.append(f"\n### {subcategory.title()}")
                        for skill in skills[:5]:  # Show top 5
                            formatted.append(f"- {skill['name']} ({skill['proficiency']}) - {skill['confidence']:.1%}")
        
        return "\n".join(formatted)
    
    @debug_button("generate_resume", "Resume Panel")
    def generate_resume(self):
        """Generate the resume based on current configuration and weaponized data."""
        # Validate inputs
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter your name")
            return
        
        # Collect configuration
        config = {
            'name': self.name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'location': self.location_edit.text().strip(),
            'template': self.template_combo.currentText(),
            'include_skills': self.include_skills.isChecked(),
            'include_projects': self.include_projects.isChecked(),
            'include_knowledge': self.include_knowledge.isChecked(),
            'max_length': self.max_length.value()
        }
        
        # Generate resume content with weaponized data
        resume_content = self._generate_resume_content(config)
        
        # Update preview
        self.preview_edit.setPlainText(resume_content)
        
        # Enable export buttons
        self.unified_export_btn.setEnabled(True)
        
        # Emit signal
        self.resume_generated.emit(config)
        
        QMessageBox.information(self, "Success", "Resume generated successfully!")
    
    @debug_button("_generate_resume_content", "Resume Panel")
    def _generate_resume_content(self, config: Dict) -> str:
        """Generate resume content based on configuration and weaponized data."""
        content = f"""# {config['name']}

## Contact Information
- Email: {config['email'] or 'your.email@example.com'}
- Phone: {config['phone'] or '+1 (555) 123-4567'}
- Location: {config['location'] or 'City, State'}

## Summary
Experienced developer with expertise in AI-powered development workflows and modern software engineering practices.

## Skills
"""
        
        # Add weaponized skills if available
        if config['include_skills'] and self.resume_tracker:
            skills = self.resume_tracker.get_skills()
            if skills:
                content += "\n### Technical Skills\n"
                for skill in skills[:10]:  # Top 10 skills
                    content += f"- **{skill['name']}**: Level {skill['current_level']}\n"
            else:
                content += "\n- Python Development\n- AI/ML Integration\n- Web Development\n- Database Management\n- Version Control (Git)\n"
        else:
            content += "\n- Python Development\n- AI/ML Integration\n- Web Development\n- Database Management\n- Version Control (Git)\n"
        
        content += "\n## Experience\n"
        
        # Add weaponized projects if available
        if config['include_projects'] and self.resume_tracker:
            projects = self.resume_tracker.get_projects()
            if projects:
                for project in projects[:5]:  # Top 5 projects
                    content += f"\n### {project.name}\n"
                    content += f"*{project.status.title()}*\n"
                    content += f"{project.description}\n"
                    content += f"**Technologies:** {', '.join(project.technologies)}\n"
                    content += f"**Role:** {project.role}\n"
            else:
                content += "\n### AI Development Specialist\n*2023 - Present*\n- Developed AI-powered conversation management systems\n- Implemented multi-model testing frameworks\n- Created automated workflow optimization tools\n"
        else:
            content += "\n### AI Development Specialist\n*2023 - Present*\n- Developed AI-powered conversation management systems\n- Implemented multi-model testing frameworks\n- Created automated workflow optimization tools\n"
        
        # Add knowledge areas if available
        if config['include_knowledge'] and self.weaponization_result:
            knowledge_tree = self.weaponization_result.get('skill_tree', {}).get('knowledge_areas', {})
            if knowledge_tree:
                content += "\n## Knowledge Areas\n"
                for category, knowledge_items in knowledge_tree.items():
                    content += f"\n### {category}\n"
                    for item in knowledge_items[:3]:  # Top 3 per category
                        content += f"- **{item['topic']}**: {item['description']}\n"
        
        content += "\n## Education\n### Bachelor of Science in Computer Science\n*University Name, 2021*\n\n"
        content += "---\n*Generated using Thea - Dreamscape MMORPG Platform with AI-powered resume weaponization*"
        
        return content
    
    @debug_button("show_unified_export_center", "Resume Panel")
    def show_unified_export_center(self):
        """Show the Unified Export Center for resume data."""
        try:
            # Prepare resume data for export
            export_data = {
                "resume_content": self.preview_edit.toPlainText(),
                "skills": self._get_skills_data(),
                "projects": self._get_projects_data(),
                "weaponization_result": self.weaponization_result if hasattr(self, 'weaponization_result') else {},
                "configuration": self.get_configuration(),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            # Create and show Unified Export Center
            from gui.components.unified_export_center import UnifiedExportCenter
            export_center = UnifiedExportCenter()
            
            # Override the data getter to return our resume data
            export_center._get_data_for_type = lambda data_type: export_data
            
            export_center.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to open export center: {e}")
    
    def _get_skills_data(self):
        """Get skills data for export."""
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
            return {"skills": [], "error": f"Failed to load skills: {e}"}
    
    def _get_projects_data(self):
        """Get projects data for export."""
        try:
            if self.resume_tracker:
                projects = self.resume_tracker.get_projects()
                return {
                    "projects": projects,
                    "total_projects": len(projects),
                    "export_timestamp": datetime.now().isoformat()
                }
            else:
                return {"projects": [], "error": "Resume tracker not available"}
        except Exception as e:
            return {"projects": [], "error": f"Failed to load projects: {e}"}
    
    @debug_button("load_personal_info", "Resume Panel")
    def load_personal_info(self, info: Dict):
        """Load personal information into the form."""
        self.name_edit.setText(info.get('name', ''))
        self.email_edit.setText(info.get('email', ''))
        self.phone_edit.setText(info.get('phone', ''))
        self.location_edit.setText(info.get('location', ''))
    
    def get_configuration(self) -> Dict:
        """Get current configuration."""
        return {
            'name': self.name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'location': self.location_edit.text().strip(),
            'template': self.template_combo.currentText(),
            'include_skills': self.include_skills.isChecked(),
            'include_projects': self.include_projects.isChecked(),
            'include_knowledge': self.include_knowledge.isChecked(),
            'max_length': self.max_length.value()
        } 