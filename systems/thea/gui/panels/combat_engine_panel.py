#!/usr/bin/env python3
"""
Combat Engine Panel for Dreamscape Advanced Features
===================================================

GUI panel for the metaphorical combat engine that gamifies problem-solving.
Shows battle logs, skill progression, and learning analytics.
"""

import sys
from gui.debug_handler import debug_button
from datetime import datetime
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from dreamscape.core.gamification import (
    CombatEngine, ProblemChallenge, UserSkill, BattleResult,
    ProblemCategory, SkillCategory, ApproachType
)

class CombatEnginePanel(QWidget):
    """GUI panel for the metaphorical combat engine."""
    
    # Signals
    battle_completed = pyqtSignal(dict)
    skill_updated = pyqtSignal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize combat engine
        self.combat_engine = CombatEngine()
        self.current_battle = None
        
        # Setup UI
        self._setup_ui()
        self._load_sample_data()
        
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("⚔️ Problem-Solving Combat Engine")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_battle_tab()
        self._create_skills_tab()
        self._create_analytics_tab()
        self._create_journey_tab()
        
    @debug_button("_create_battle_tab", "Combat Engine Panel")
    def _create_battle_tab(self):
        """Create the battle simulation tab."""
        battle_widget = QWidget()
        layout = QVBoxLayout(battle_widget)
        
        # Battle controls
        controls_group = QGroupBox("Battle Controls")
        controls_layout = QGridLayout(controls_group)
        
        # Problem selection
        controls_layout.addWidget(QLabel("Problem:"), 0, 0)
        self.problem_combo = QComboBox()
        self.problem_combo.addItems([
            "Import Error Resolution",
            "Database Connection Issue", 
            "API Integration Challenge",
            "Performance Optimization",
            "UI/UX Design Problem",
            "Debugging Complex Bug",
            "Architecture Decision",
            "Code Refactoring"
        ])
        controls_layout.addWidget(self.problem_combo, 0, 1)
        
        # Approach selection
        controls_layout.addWidget(QLabel("Approach:"), 1, 0)
        self.approach_combo = QComboBox()
        self.approach_combo.addItems([approach.value for approach in ApproachType])
        controls_layout.addWidget(self.approach_combo, 1, 1)
        
        # Battle button
        self.battle_button = QPushButton("⚔️ Start Battle")
        self.battle_button.clicked.connect(self._start_battle)
        controls_layout.addWidget(self.battle_button, 2, 0, 1, 2)
        
        layout.addWidget(controls_group)
        
        # Battle log
        log_group = QGroupBox("Battle Log")
        log_layout = QVBoxLayout(log_group)
        
        self.battle_log = QTextEdit()
        self.battle_log.setReadOnly(True)
        self.battle_log.setMaximumHeight(200)
        log_layout.addWidget(self.battle_log)
        
        layout.addWidget(log_group)
        
        # Battle result
        result_group = QGroupBox("Battle Result")
        result_layout = QGridLayout(result_group)
        
        self.result_label = QLabel("No battle fought yet")
        self.result_label.setFont(QFont("Arial", 12))
        result_layout.addWidget(self.result_label, 0, 0)
        
        self.experience_label = QLabel("")
        result_layout.addWidget(self.experience_label, 1, 0)
        
        self.skills_label = QLabel("")
        result_layout.addWidget(self.skills_label, 2, 0)
        
        layout.addWidget(result_group)
        
        self.tab_widget.addTab(battle_widget, "⚔️ Battle")
        
    @debug_button("_create_skills_tab", "Combat Engine Panel")
    def _create_skills_tab(self):
        """Create the skills progression tab."""
        skills_widget = QWidget()
        layout = QVBoxLayout(skills_widget)
        
        # Skills overview
        overview_group = QGroupBox("Skills Overview")
        overview_layout = QGridLayout(overview_group)
        
        self.skills_table = QTableWidget()
        self.skills_table.setColumnCount(4)
        self.skills_table.setHorizontalHeaderLabels(["Skill", "Level", "XP", "Category"])
        self.skills_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        overview_layout.addWidget(self.skills_table, 0, 0)
        
        layout.addWidget(overview_group)
        
        # Add skill button
        add_skill_layout = QHBoxLayout()
        add_skill_layout.addWidget(QLabel("Add Skill:"))
        
        self.skill_name_edit = QLineEdit()
        self.skill_name_edit.setPlaceholderText("Skill name")
        add_skill_layout.addWidget(self.skill_name_edit)
        
        self.skill_level_spin = QComboBox()
        self.skill_level_spin.addItems([str(i) for i in range(1, 11)])
        add_skill_layout.addWidget(self.skill_level_spin)
        
        self.skill_category_combo = QComboBox()
        self.skill_category_combo.addItems([cat.value for cat in SkillCategory])
        add_skill_layout.addWidget(self.skill_category_combo)
        
        add_skill_button = QPushButton("Add Skill")
        add_skill_button.clicked.connect(self._add_skill)
        add_skill_layout.addWidget(add_skill_button)
        
        layout.addLayout(add_skill_layout)
        
        self.tab_widget.addTab(skills_widget, "🎯 Skills")
        
    @debug_button("_create_analytics_tab", "Combat Engine Panel")
    def _create_analytics_tab(self):
        """Create the learning analytics tab."""
        analytics_widget = QWidget()
        layout = QVBoxLayout(analytics_widget)
        
        # Analytics overview
        analytics_group = QGroupBox("Learning Analytics")
        analytics_layout = QGridLayout(analytics_group)
        
        self.analytics_text = QTextEdit()
        self.analytics_text.setReadOnly(True)
        analytics_layout.addWidget(self.analytics_text, 0, 0)
        
        layout.addWidget(analytics_group)
        
        # Refresh button
        refresh_button = QPushButton("🔄 Refresh Analytics")
        refresh_button.clicked.connect(self._refresh_analytics)
        layout.addWidget(refresh_button)
        
        self.tab_widget.addTab(analytics_widget, "📊 Analytics")
        
    @debug_button("_create_journey_tab", "Combat Engine Panel")
    def _create_journey_tab(self):
        """Create the learning journey tab."""
        journey_widget = QWidget()
        layout = QVBoxLayout(journey_widget)
        
        # Journey controls
        journey_controls = QHBoxLayout()
        
        self.journey_button = QPushButton("🚀 Start Learning Journey")
        self.journey_button.clicked.connect(self._start_learning_journey)
        journey_controls.addWidget(self.journey_button)
        
        layout.addLayout(journey_controls)
        
        # Journey log
        journey_group = QGroupBox("Learning Journey")
        journey_layout = QVBoxLayout(journey_group)
        
        self.journey_log = QTextEdit()
        self.journey_log.setReadOnly(True)
        journey_layout.addWidget(self.journey_log)
        
        layout.addWidget(journey_group)
        
        self.tab_widget.addTab(journey_widget, "🗺️ Journey")
        
    @debug_button("_load_sample_data", "Combat Engine Panel")
    def _load_sample_data(self):
        """Load sample skills and data for demonstration."""
        # Add sample skills
        sample_skills = [
            UserSkill("Python", 7, SkillCategory.PROGRAMMING, 350),
            UserSkill("JavaScript", 6, SkillCategory.PROGRAMMING, 280),
            UserSkill("React", 5, SkillCategory.FRAMEWORK, 200),
            UserSkill("Debugging", 8, SkillCategory.PROBLEM_SOLVING, 450),
            UserSkill("API Integration", 6, SkillCategory.DOMAIN, 300),
            UserSkill("Database Design", 5, SkillCategory.DOMAIN, 250)
        ]
        
        for skill in sample_skills:
            self.combat_engine.add_user_skill(skill)
        
        self._update_skills_table()
        self._refresh_analytics()
        
    @debug_button("_start_battle", "Combat Engine Panel")
    def _start_battle(self):
        """Start a problem-solving battle."""
        problem_name = self.problem_combo.currentText()
        approach_name = self.approach_combo.currentText()
        
        # Create problem challenge
        problem = ProblemChallenge(
            name=problem_name,
            difficulty=random.randint(4, 8),
            category=random.choice(list(ProblemCategory)),
            skills_required=["Python", "Debugging"],
            solution_approach=approach_name
        )
        
        approach = ApproachType(approach_name)
        
        # Log battle start
        self.battle_log.append(f"⚔️ Starting battle: {problem_name}")
        self.battle_log.append(f"   Difficulty: {problem.difficulty}/10")
        self.battle_log.append(f"   Category: {problem.category.value}")
        self.battle_log.append(f"   Approach: {approach_name}")
        self.battle_log.append("")
        
        # Solve the problem
        result = self.combat_engine.solve_problem(problem, approach)
        
        # Update UI
        self._update_battle_result(result)
        self._update_skills_table()
        self._refresh_analytics()
        
        # Emit signals
        self.battle_completed.emit({
            "problem": problem_name,
            "success": result.success,
            "experience": result.experience_gained
        })
        
    @debug_button("_update_battle_result", "Combat Engine Panel")
    def _update_battle_result(self, result: BattleResult):
        """Update the battle result display."""
        if result.success:
            self.result_label.setText("🎉 Victory!")
            self.result_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.result_label.setText("💀 Defeat")
            self.result_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.experience_label.setText(f"Experience Gained: {result.experience_gained} XP")
        
        if result.skills_improved:
            skills_text = "Skills Improved: " + ", ".join(result.skills_improved)
        else:
            skills_text = "No skills improved"
        self.skills_label.setText(skills_text)
        
        # Add to battle log
        self.battle_log.append(f"🎯 Result: {'Victory' if result.success else 'Defeat'}")
        self.battle_log.append(f"   Experience: {result.experience_gained} XP")
        if result.insights_learned:
            self.battle_log.append("   Insights:")
            for insight in result.insights_learned:
                self.battle_log.append(f"     • {insight}")
        self.battle_log.append("")
        
    @debug_button("_add_skill", "Combat Engine Panel")
    def _add_skill(self):
        """Add a new skill to the user's profile."""
        name = self.skill_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a skill name")
            return
        
        level = int(self.skill_level_spin.currentText())
        category = SkillCategory(self.skill_category_combo.currentText())
        
        skill = UserSkill(name, level, category)
        self.combat_engine.add_user_skill(skill)
        
        self.skill_name_edit.clear()
        self._update_skills_table()
        self._refresh_analytics()
        
        QMessageBox.information(self, "Success", f"Added skill: {name} (Level {level})")
        
    @debug_button("_update_skills_table", "Combat Engine Panel")
    def _update_skills_table(self):
        """Update the skills table display."""
        skills = list(self.combat_engine.user_skills.values())
        self.skills_table.setRowCount(len(skills))
        
        for i, skill in enumerate(skills):
            self.skills_table.setItem(i, 0, QTableWidgetItem(skill.name))
            self.skills_table.setItem(i, 1, QTableWidgetItem(str(skill.level)))
            self.skills_table.setItem(i, 2, QTableWidgetItem(str(skill.experience_points)))
            self.skills_table.setItem(i, 3, QTableWidgetItem(skill.category.value))
            
            # Color code by level
            if skill.level >= 8:
                self.skills_table.item(i, 1).setBackground(QColor(144, 238, 144))  # Light green
            elif skill.level >= 6:
                self.skills_table.item(i, 1).setBackground(QColor(255, 255, 224))  # Light yellow
            else:
                self.skills_table.item(i, 1).setBackground(QColor(255, 182, 193))  # Light red
                
    @debug_button("_refresh_analytics", "Combat Engine Panel")
    def _refresh_analytics(self):
        """Refresh the learning analytics display."""
        analytics = self.combat_engine.get_learning_analytics()
        
        if "message" in analytics:
            self.analytics_text.setText(analytics["message"])
            return
        
        # Format analytics for display
        text = "📊 Learning Analytics\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Total Battles: {analytics['total_battles']}\n"
        text += f"Success Rate: {analytics['success_rate']:.1%}\n"
        text += f"Total Experience: {analytics['total_experience']} XP\n\n"
        
        text += "🎯 Skills Progression:\n"
        for skill, level in analytics['skills_progression'].items():
            text += f"  • {skill}: Level {level}\n"
        text += "\n"
        
        text += "📈 Recent Battles:\n"
        for battle in analytics['recent_battles']:
            status = "✅" if battle['success'] else "❌"
            text += f"  {status} {battle['problem']} ({battle['approach']}) - {battle['experience']} XP\n"
        
        self.analytics_text.setText(text)
        
    @debug_button("_start_learning_journey", "Combat Engine Panel")
    def _start_learning_journey(self):
        """Start a complete learning journey."""
        self.journey_log.clear()
        self.journey_log.append("🚀 Starting Learning Journey...\n")
        
        # Create sample problems for the journey
        problems = [
            ProblemChallenge("Basic Syntax Error", 3, ProblemCategory.TECHNICAL, ["Python"], "systematic"),
            ProblemChallenge("API Authentication", 5, ProblemCategory.INTEGRATION, ["API Integration"], "iterative"),
            ProblemChallenge("Performance Bottleneck", 7, ProblemCategory.PERFORMANCE, ["Debugging"], "analytical"),
            ProblemChallenge("Database Query Optimization", 6, ProblemCategory.OPTIMIZATION, ["Database Design"], "systematic"),
            ProblemChallenge("UI Component Design", 4, ProblemCategory.DESIGN, ["React"], "experimental")
        ]
        
        # Simulate the journey
        journey = self.combat_engine.simulate_learning_journey(problems)
        
        # Display results
        self.journey_log.append(f"🎉 Journey Complete!\n")
        self.journey_log.append(f"Problems Solved: {journey.successful_solves}/{journey.total_problems}\n")
        self.journey_log.append(f"Total Experience: {journey.total_experience} XP\n")
        self.journey_log.append(f"Duration: {(journey.end_time - journey.start_time).total_seconds():.1f} seconds\n\n")
        
        self.journey_log.append("📚 Skills Progression:\n")
        for skill, xp in journey.skills_progression.items():
            self.journey_log.append(f"  • {skill}: +{xp} XP\n")
        
        # Update other displays
        self._update_skills_table()
        self._refresh_analytics()
        
        QMessageBox.information(self, "Journey Complete", 
                              f"Learning journey completed!\n"
                              f"Solved {journey.successful_solves}/{journey.total_problems} problems\n"
                              f"Gained {journey.total_experience} XP") 