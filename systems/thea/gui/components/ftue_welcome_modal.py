#!/usr/bin/env python3
"""
FTUE Welcome Modal & Onboarding Flow
====================================

A multi-step modal dialog for first-time user experience (FTUE) onboarding.
- Step 1: Welcome
- Step 2: Profile Setup (optional)
- Step 3: Quick Tour
- Step 4: Finish

Shows only on first launch (uses settings_manager to persist 'has_seen_ftue').
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QStackedWidget,
    QWidget,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Reuse settings_manager from core
from dreamscape.core.settings_manager import settings_manager


class FTUEWelcomeModal(QDialog):
    """First-Time User Experience (FTUE) Welcome Modal and Onboarding Flow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Dreamscape!")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.current_step = 0
        self.profile_name = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Stacked widget for steps
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Step 1: Welcome
        welcome_page = QWidget()
        wl = QVBoxLayout(welcome_page)
        wl.addWidget(self._title_label("👋 Welcome to Dreamscape!"))
        wl.addWidget(
            self._subtitle_label("Your AI-powered MMORPG journey begins here.")
        )
        wl.addWidget(self._body_label("Let's get you set up in just a few steps."))
        wl.addStretch()
        self.next_btn1 = QPushButton("Next →")
        self.next_btn1.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        wl.addWidget(self.next_btn1, alignment=Qt.AlignmentFlag.AlignRight)
        self.stack.addWidget(welcome_page)

        # Step 2: Profile Setup
        profile_page = QWidget()
        pl = QVBoxLayout(profile_page)
        pl.addWidget(self._title_label("📝 Set Up Your Profile"))
        pl.addWidget(self._body_label("Enter a display name (optional):"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Dreamer123")
        pl.addWidget(self.name_input)
        pl.addStretch()
        btns2 = QHBoxLayout()
        back2 = QPushButton("← Back")
        back2.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        next2 = QPushButton("Next →")
        next2.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        btns2.addWidget(back2)
        btns2.addStretch()
        btns2.addWidget(next2)
        pl.addLayout(btns2)
        self.stack.addWidget(profile_page)

        # Step 3: Quick Tour
        tour_page = QWidget()
        tl = QVBoxLayout(tour_page)
        tl.addWidget(self._title_label("🚀 Quick Tour"))
        tl.addWidget(
            self._body_label(
                "• Dashboard: See your stats and progress\n• Templates: Choose how you interact\n• Skill Tree: Track your learning\n• Settings: Personalize your experience"
            )
        )
        tl.addStretch()
        btns3 = QHBoxLayout()
        back3 = QPushButton("← Back")
        back3.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        next3 = QPushButton("Finish →")
        next3.clicked.connect(self.finish_onboarding)
        btns3.addWidget(back3)
        btns3.addStretch()
        btns3.addWidget(next3)
        tl.addLayout(btns3)
        self.stack.addWidget(tour_page)

        # Step 4: Finish
        finish_page = QWidget()
        fl = QVBoxLayout(finish_page)
        fl.addWidget(self._title_label("🎉 All Set!"))
        fl.addWidget(
            self._body_label(
                "You're ready to explore Dreamscape.\nYou can revisit onboarding anytime from Settings."
            )
        )
        fl.addStretch()
        done_btn = QPushButton("Start Exploring →")
        done_btn.clicked.connect(self.accept)
        fl.addWidget(done_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.stack.addWidget(finish_page)

        self.stack.setCurrentIndex(0)

    def _title_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl

    def _subtitle_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 14))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #666;")
        return lbl

    def _body_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Arial", 11))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        return lbl

    def finish_onboarding(self):
        # Save profile name if entered
        name = self.name_input.text().strip()
        if name:
            settings_manager.set("profile_name", name)
        # Set FTUE flag
        settings_manager.set("has_seen_ftue", True)
        self.stack.setCurrentIndex(3)

    @staticmethod
    def maybe_show(parent=None):
        # Only show if FTUE not completed
        if not settings_manager.get("has_seen_ftue", False):
            dlg = FTUEWelcomeModal(parent)
            dlg.exec()


# END OF FILE
