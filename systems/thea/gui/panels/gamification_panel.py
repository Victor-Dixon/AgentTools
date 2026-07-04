#!/usr/bin/env python3
"""
Gamification Panel
==================

GUI panel for displaying user rewards, badges, contribution tracking,
and leaderboards for the labeling gamification system.
"""

import logging
from gui.debug_handler import debug_button
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QTabWidget, QScrollArea,
    QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

from dreamscape.core.gamification.labeling_rewards import (
    LabelingRewardsSystem, LabelingAction, LabelingBadge
)
from dreamscape.core.gamification.contribution_tracker import (
    ContributionTracker, ContributionType, QualityLevel
)
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from dreamscape.core.memory_system import MemoryManager

logger = logging.getLogger(__name__)

class GamificationWorker(QThread):
    """Background worker for gamification operations."""
    
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Execute the gamification operation."""
        try:
            if self.operation == "load_user_stats":
                result = self._load_user_stats()
            elif self.operation == "load_leaderboard":
                result = self._load_leaderboard()
            elif self.operation == "load_analytics":
                result = self._load_analytics()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            self.data_ready.emit(result)
            
        except Exception as e:
            logger.error(f"Gamification operation failed: {e}")
            self.error_occurred.emit(str(e))
    
    @debug_button("_load_user_stats", "Gamification Panel")
    def _load_user_stats(self):
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
                title="gamification_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget

    def _load_leaderboard(self):
        """Load leaderboard data."""
        return {"status": "success", "data": {}}

    @debug_button("_load_analytics", "Gamification Panel")
    def _load_analytics(self):
        """Load analytics data."""
        return {"status": "success", "data": {}}

class BadgeWidget(QWidget):
    """Custom widget for displaying badges."""
    
    def __init__(self, badge_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.badge_data = badge_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize the badge widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Badge icon/emoji
        icon_label = QLabel("🏅")  # Default badge emoji
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont("Arial", 24))
        layout.addWidget(icon_label)
        
        # Badge name
        name_label = QLabel(self.badge_data.get("name", "Unknown Badge"))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Badge description
        desc_label = QLabel(self.badge_data.get("description", ""))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont("Arial", 8))
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Progress bar (if not earned)
        if not self.badge_data.get("earned", False):
            progress = self.badge_data.get("progress", {})
            if progress.get("required", 0) > 0:
                progress_bar = QProgressBar()
                progress_bar.setMaximum(progress["required"])
                progress_bar.setValue(progress["current"])
                progress_bar.setFormat(f"{progress['current']}/{progress['required']}")
                layout.addWidget(progress_bar)
        
        # Style based on earned status
        if self.badge_data.get("earned", False):
            self.setStyleSheet("""
                QWidget {
                    background-color: #4CAF50;
                    border: 2px solid #45a049;
                    border-radius: 10px;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    border: 2px solid #ddd;
                    border-radius: 10px;
                    color: #666;
                }
            """)

class GamificationPanel(QWidget):
    """Main gamification panel for displaying rewards and progress."""
    
    # Signals
    session_started = pyqtSignal(str)
    session_ended = pyqtSignal(dict)
    reward_earned = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize systems
        self.memory_manager = MemoryManager()
        self.mmorpg_engine = MMORPGEngine()
        self.labeling_rewards = LabelingRewardsSystem(self.mmorpg_engine, self.memory_manager)
        self.contribution_tracker = ContributionTracker(self.memory_manager)
        
        # Current session
        self.current_session_id = None
        self.current_user_id = "default_user"  # In a real app, this would come from auth
        
        # Initialize UI attributes (will be created in init_ui)
        self.xp_label = None
        self.level_label = None
        self.contributions_label = None
        self.conversations_labeled_label = None
        self.streak_label = None
        self.accuracy_label = None
        self.status_label = None
        self.xp_progress_bar = None
        self.streak_progress_label = None
        self.leaderboard_table = None
        self.badge_layout = None
        
        # Setup UI
        self.init_ui()
        self.setup_connections()
        
        # Load initial data
        self.load_user_data()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Gamification Center")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Session controls
        self.create_session_controls(layout)
        
        # Main content area
        self.create_main_content(layout)
        
        # Status bar
        self.create_status_bar(layout)
    
    @debug_button("create_session_controls", "Gamification Panel")
    def create_session_controls(self, parent_layout):
        """Create session control buttons."""
        session_group = QGroupBox("Labeling Session")
        session_layout = QHBoxLayout(session_group)
        
        self.start_session_btn = QPushButton("Start Labeling Session")
        self.start_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.end_session_btn = QPushButton("End Session")
        self.end_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.end_session_btn.setEnabled(False)
        
        self.session_status = QLabel("No active session")
        self.session_status.setStyleSheet("color: #666; font-style: italic;")
        
        session_layout.addWidget(self.start_session_btn)
        session_layout.addWidget(self.end_session_btn)
        session_layout.addWidget(self.session_status)
        session_layout.addStretch()
        
        parent_layout.addWidget(session_group)
    
    @debug_button("create_main_content", "Gamification Panel")
    def create_main_content(self, parent_layout):
        """Create the main content area with tabs."""
        self.tab_widget = QTabWidget()
        
        # Overview tab
        self.tab_widget.addTab(self.create_overview_tab(), "Overview")
        
        # Badges tab
        self.tab_widget.addTab(self.create_badges_tab(), "Badges")
        
        # Progress tab
        self.tab_widget.addTab(self.create_progress_tab(), "Progress")
        
        # Leaderboard tab
        self.tab_widget.addTab(self.create_leaderboard_tab(), "Leaderboard")
        
        # Analytics tab
        self.tab_widget.addTab(self.create_analytics_tab(), "Analytics")
        
        parent_layout.addWidget(self.tab_widget)
    
    @debug_button("create_overview_tab", "Gamification Panel")
    def create_overview_tab(self):
        """Create the overview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # User stats section
        stats_group = QGroupBox("User Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Create labels
        self.xp_label = QLabel("Total XP: 0")
        self.level_label = QLabel("Level: 1")
        self.contributions_label = QLabel("Total Contributions: 0")
        self.conversations_labeled_label = QLabel("Conversations Labeled: 0")
        self.streak_label = QLabel("Current Streak: 0 days")
        self.accuracy_label = QLabel("Accuracy Rate: 0.0%")
        
        # Add labels to grid
        stats_layout.addWidget(self.xp_label, 0, 0)
        stats_layout.addWidget(self.level_label, 0, 1)
        stats_layout.addWidget(self.contributions_label, 1, 0)
        stats_layout.addWidget(self.conversations_labeled_label, 1, 1)
        stats_layout.addWidget(self.streak_label, 2, 0)
        stats_layout.addWidget(self.accuracy_label, 2, 1)
        
        layout.addWidget(stats_group)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return widget

    def create_badges_tab(self) -> QWidget:
        """Create the badges tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Badge grid
        self.badge_scroll = QScrollArea()
        self.badge_widget = QWidget()
        self.badge_layout = QGridLayout(self.badge_widget)
        
        # Placeholder badges (will be populated with real data)
        badge_data = [
            {"name": "First Label", "description": "Complete your first labeling action", "earned": True},
            {"name": "Labeling Apprentice", "description": "Complete 10 labeling actions", "earned": False, "progress": {"current": 3, "required": 10}},
            {"name": "Quality Contributor", "description": "Maintain 90% accuracy over 20 actions", "earned": False, "progress": {"current": 15, "required": 20}},
            {"name": "Batch Processor", "description": "Process 10 conversations in one session", "earned": False, "progress": {"current": 5, "required": 10}},
            {"name": "Consistency Champion", "description": "Label for 7 consecutive days", "earned": False, "progress": {"current": 3, "required": 7}},
            {"name": "Labeling Legend", "description": "Complete 500 labeling actions", "earned": False, "progress": {"current": 25, "required": 500}}
        ]
        
        for i, badge in enumerate(badge_data):
            badge_widget = BadgeWidget(badge)
            row = i // 3
            col = i % 3
            self.badge_layout.addWidget(badge_widget, row, col)
        
        self.badge_scroll.setWidget(self.badge_widget)
        self.badge_scroll.setWidgetResizable(True)
        layout.addWidget(self.badge_scroll)
        
        return widget
    
    @debug_button("create_progress_tab", "Gamification Panel")
    def create_progress_tab(self) -> QWidget:
        """Create the progress tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Progress charts (placeholder)
        progress_group = QGroupBox("Progress Charts")
        progress_layout = QVBoxLayout(progress_group)
        
        # XP Progress
        xp_progress_label = QLabel("XP Progress")
        xp_progress_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        progress_layout.addWidget(xp_progress_label)
        
        self.xp_progress_bar = QProgressBar()
        self.xp_progress_bar.setMaximum(100)
        self.xp_progress_bar.setValue(25)
        self.xp_progress_bar.setFormat("Level 1: 250/1000 XP")
        progress_layout.addWidget(self.xp_progress_bar)
        
        # Skill Progress
        skill_progress_label = QLabel("Skill Progress")
        skill_progress_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        progress_layout.addWidget(skill_progress_label)
        
        skills = ["Analytical Thinking", "Classification Accuracy", "Attention to Detail"]
        self.skill_progress_bars = {}
        
        for skill in skills:
            skill_layout = QHBoxLayout()
            skill_label = QLabel(skill)
            skill_label.setMinimumWidth(150)
            skill_layout.addWidget(skill_label)
            
            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)
            progress_bar.setValue(30 + skills.index(skill) * 20)
            progress_bar.setFormat(f"Level {1 + skills.index(skill)}")
            skill_layout.addWidget(progress_bar)
            
            self.skill_progress_bars[skill] = progress_bar
            progress_layout.addLayout(skill_layout)
        
        layout.addWidget(progress_group)
        
        # Streak tracking
        streak_group = QGroupBox("Streak Tracking")
        streak_layout = QVBoxLayout(streak_group)
        
        self.streak_progress_label = QLabel("Current Streak: 3 days")
        self.streak_progress_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        streak_layout.addWidget(self.streak_progress_label)
        
        self.longest_streak_label = QLabel("Longest Streak: 7 days")
        streak_layout.addWidget(self.longest_streak_label)
        
        layout.addWidget(streak_group)
        
        return widget
    
    @debug_button("create_leaderboard_tab", "Gamification Panel")
    def create_leaderboard_tab(self) -> QWidget:
        """Create the leaderboard tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Leaderboard table
        leaderboard_group = QGroupBox("Top Contributors")
        leaderboard_layout = QVBoxLayout(leaderboard_group)
        
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(5)
        self.leaderboard_table.setHorizontalHeaderLabels([
            "Rank", "User", "Total XP", "Contributions", "Badges"
        ])
        
        # Set up table
        header = self.leaderboard_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Sample data
        sample_data = [
            ["1", "User1", "1,250", "45", "8"],
            ["2", "User2", "980", "32", "6"],
            ["3", "User3", "750", "28", "5"],
            ["4", "User4", "620", "25", "4"],
            ["5", "User5", "480", "20", "3"]
        ]
        
        self.leaderboard_table.setRowCount(len(sample_data))
        for i, row_data in enumerate(sample_data):
            for j, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                if j == 0:  # Rank column
                    item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                self.leaderboard_table.setItem(i, j, item)
        
        leaderboard_layout.addWidget(self.leaderboard_table)
        layout.addWidget(leaderboard_group)
        
        # Refresh button using shared component
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        refresh_btn = components.create_refresh_button(
            text="Refresh Leaderboard", callback=self.refresh_leaderboard
        )
        layout.addWidget(refresh_btn)
        
        return widget
    
    @debug_button("create_analytics_tab", "Gamification Panel")
    def create_analytics_tab(self) -> QWidget:
        """Create the analytics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Analytics overview
        analytics_group = QGroupBox("Analytics Overview")
        analytics_layout = QGridLayout(analytics_group)
        
        # Quality metrics
        self.quality_score_label = QLabel("Average Quality Score: 0.85")
        analytics_layout.addWidget(self.quality_score_label, 0, 0)
        
        self.consistency_score_label = QLabel("Consistency Score: 0.78")
        analytics_layout.addWidget(self.consistency_score_label, 0, 1)
        
        # Contribution types
        self.contribution_types_label = QLabel("Most Common: Conversation Labeling")
        analytics_layout.addWidget(self.contribution_types_label, 1, 0)
        
        self.active_days_label = QLabel("Active Days: 15")
        analytics_layout.addWidget(self.active_days_label, 1, 1)
        
        layout.addWidget(analytics_group)
        
        # Detailed analytics (placeholder)
        details_group = QGroupBox("Detailed Analytics")
        details_layout = QVBoxLayout(details_group)
        
        details_text = QTextEdit()
        details_text.setPlainText("""
Quality Distribution:
- Excellent: 25%
- Good: 45%
- Average: 20%
- Poor: 10%

Contribution Types:
- Conversation Labeling: 60%
- Category Correction: 20%
- Tag Management: 15%
- Quality Review: 5%

Weekly Activity:
- Monday: 15 contributions
- Tuesday: 12 contributions
- Wednesday: 18 contributions
- Thursday: 10 contributions
- Friday: 8 contributions
- Weekend: 5 contributions
        """)
        details_text.setReadOnly(True)
        details_layout.addWidget(details_text)
        
        layout.addWidget(details_group)
        
        return widget
    
    @debug_button("create_status_bar", "Gamification Panel")
    def create_status_bar(self, parent_layout):
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
                title="gamification_panel Statistics",
                style="modern"
            )
            
            parent_layout.addWidget(stats_widget)
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            # Fallback: create simple status widget
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)
            fallback_label = QLabel("Status not available")
            fallback_layout.addWidget(fallback_label)
            parent_layout.addWidget(fallback_widget)

    def setup_connections(self):
        """Setup signal connections."""
        self.start_session_btn.clicked.connect(self.start_labeling_session)
        self.end_session_btn.clicked.connect(self.end_labeling_session)
    
    @debug_button("start_labeling_session", "Gamification Panel")
    def start_labeling_session(self):
        """Start a new labeling session."""
        try:
            self.current_session_id = self.labeling_rewards.start_labeling_session(self.current_user_id)
            
            # Update UI
            self.start_session_btn.setEnabled(False)
            self.end_session_btn.setEnabled(True)
            self.session_status.setText(f"Active session: {self.current_session_id[:8]}...")
            self.session_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # Emit signal
            self.session_started.emit(self.current_session_id)
            
            logger.info(f"Started labeling session: {self.current_session_id}")
            
        except Exception as e:
            logger.error(f"Failed to start labeling session: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start session: {e}")
    
    @debug_button("end_labeling_session", "Gamification Panel")
    def end_labeling_session(self):
        """End the current labeling session."""
        if not self.current_session_id:
            return
        
        try:
            # End session
            session_summary = self.labeling_rewards.end_labeling_session(self.current_session_id)
            
            # Update UI
            self.start_session_btn.setEnabled(True)
            self.end_session_btn.setEnabled(False)
            self.session_status.setText("No active session")
            self.session_status.setStyleSheet("color: #666; font-style: italic;")
            
            # Show summary
            summary_text = f"""
Session Summary:
- Duration: {session_summary['duration_minutes']:.1f} minutes
- Total Actions: {session_summary['total_actions']}
- XP Earned: {session_summary['total_xp_earned']}
- Badges Earned: {len(session_summary['badges_earned'])}
- Conversations Labeled: {session_summary['conversations_labeled']}
- Accuracy Score: {session_summary['accuracy_score']:.2f}
            """
            
            QMessageBox.information(self, "Session Complete", summary_text)
            
            # Emit signal
            self.session_ended.emit(session_summary)
            
            # Clear session
            self.current_session_id = None
            
            # Refresh data
            self.load_user_data()
            
        except Exception as e:
            logger.error(f"Failed to end labeling session: {e}")
            QMessageBox.critical(self, "Error", f"Failed to end session: {e}")
    
    def award_labeling_action(self, action: LabelingAction, accuracy: float = 1.0, metadata: Dict[str, Any] = None):
        """Award XP for a labeling action."""
        if not self.current_session_id:
            logger.warning("No active session for awarding action")
            return
        
        try:
            reward = self.labeling_rewards.award_labeling_action(
                self.current_session_id, action, accuracy, metadata
            )
            
            # Record contribution
            self.contribution_tracker.record_contribution(
                self.current_user_id,
                ContributionType.CONVERSATION_LABELING,
                metadata.get("conversation_id") if metadata else None,
                {"action": action.value, "accuracy": accuracy},
                metadata
            )
            
            # Show notification
            notification_text = f"🎉 +{reward.xp_amount} XP for {action.value.replace('_', ' ').title()}"
            self.status_label.setText(notification_text)
            
            # Emit signal
            self.reward_earned.emit({
                "xp_amount": reward.xp_amount,
                "action": action.value,
                "description": reward.description
            })
            
            logger.info(f"Awarded {reward.xp_amount} XP for {action.value}")
            
        except Exception as e:
            logger.error(f"Failed to award labeling action: {e}")
    
    @debug_button("load_user_data", "Gamification Panel")
    def load_user_data(self):
        """Load user data and update UI."""
        try:
            # Load user stats
            user_stats = self.labeling_rewards.get_user_labeling_stats(self.current_user_id)
            
            # Update overview
            self.xp_label.setText(f"Total XP: {user_stats.get('total_xp_earned', 0):,}")
            self.level_label.setText(f"Level: {user_stats.get('current_level', 1)}")
            self.contributions_label.setText(f"Total Contributions: {user_stats.get('total_actions', 0)}")
            self.conversations_labeled_label.setText(f"Conversations Labeled: {user_stats.get('conversations_labeled', 0)}")
            self.streak_label.setText(f"Current Streak: {user_stats.get('streak_days', 0)} days")
            
            accuracy = user_stats.get('accuracy_rate', 0.0) * 100
            self.accuracy_label.setText(f"Accuracy Rate: {accuracy:.1f}%")
            
            # Load badges
            badges = self.labeling_rewards.get_available_badges(self.current_user_id)
            self.update_badges_display(badges)
            
            # Load progress
            self.update_progress_display(user_stats)
            
            self.status_label.setText("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load user data: {e}")
            self.status_label.setText(f"Error loading data: {e}")
    
    @debug_button("update_badges_display", "Gamification Panel")
    def update_badges_display(self, badges: List[Dict[str, Any]]):
        """Update the badges display."""
        # Clear existing badges
        for i in reversed(range(self.badge_layout.count())):
            widget = self.badge_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add new badges
        for i, badge in enumerate(badges):
            badge_widget = BadgeWidget(badge)
            row = i // 3
            col = i % 3
            self.badge_layout.addWidget(badge_widget, row, col)
    
    @debug_button("update_progress_display", "Gamification Panel")
    def update_progress_display(self, user_stats: Dict[str, Any]):
        """Update the progress display."""
        # Update XP progress
        current_xp = user_stats.get('total_xp_earned', 0)
        level = user_stats.get('current_level', 1)
        xp_for_next = level * 100  # Simple level calculation
        
        self.xp_progress_bar.setMaximum(xp_for_next)
        self.xp_progress_bar.setValue(current_xp % xp_for_next)
        self.xp_progress_bar.setFormat(f"Level {level}: {current_xp % xp_for_next}/{xp_for_next} XP")
        
        # Update streak
        streak = user_stats.get('streak_days', 0)
        self.streak_progress_label.setText(f"Current Streak: {streak} days")
    
    @debug_button("refresh_data", "Gamification Panel")
    def refresh_data(self):
        """Refresh all data."""
        self.load_user_data()
        self.refresh_leaderboard()
    
    @debug_button("refresh_leaderboard", "Gamification Panel")
    def refresh_leaderboard(self):
        """Refresh the leaderboard data."""
        try:
            leaderboard = self.labeling_rewards.get_leaderboard(limit=10)
            
            self.leaderboard_table.setRowCount(len(leaderboard))
            for i, entry in enumerate(leaderboard):
                self.leaderboard_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.leaderboard_table.setItem(i, 1, QTableWidgetItem(entry['user_id']))
                self.leaderboard_table.setItem(i, 2, QTableWidgetItem(f"{entry['total_xp_earned']:,}"))
                self.leaderboard_table.setItem(i, 3, QTableWidgetItem(str(entry['total_actions'])))
                self.leaderboard_table.setItem(i, 4, QTableWidgetItem(str(entry['badges_earned'])))
            
            self.status_label.setText("Leaderboard refreshed")
            
        except Exception as e:
            logger.error(f"Failed to refresh leaderboard: {e}")
            self.status_label.setText(f"Error refreshing leaderboard: {e}")
    
    @debug_button("start_labeling_workflow", "Gamification Panel")
    def start_labeling_workflow(self):
        """Start the labeling workflow."""
        QMessageBox.information(self, "Labeling Workflow", 
                              "This would open the conversation labeling interface.")
    
    @debug_button("open_review_interface", "Gamification Panel")
    def open_review_interface(self):
        """Open the contribution review interface."""
        QMessageBox.information(self, "Review Interface", 
                              "This would open the contribution review interface.") 