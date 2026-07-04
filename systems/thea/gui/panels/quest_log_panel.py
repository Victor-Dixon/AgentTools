from __future__ import annotations
from gui.debug_handler import debug_button

"""Qt-only Quest Log panel (MVP)
Replaces the previous Tkinter-based TaskPanel so the sidebar "Quest Log" button
shows an interactive table to create / update / complete tasks.
"""

from typing import List, Optional
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QComboBox, QLineEdit, QTextEdit, QDateEdit, QSpinBox, QTabWidget)  # Added QTabWidget

from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from dreamscape.core.mmorpg.models import Quest, QuestType


class QuestLogPanel(QWidget):
    """Qt Quest Log panel MVP, now with Achievements and Badges tabs."""

    tasks_changed = pyqtSignal()

    def __init__(self, engine: MMORPGEngine, parent: QWidget | None = None):
        super().__init__(parent)
        self.engine = engine
        self._build_ui()
        self._refresh()

    # ---------- UI ----------
    @debug_button("_build_ui", "Quest Log Panel")
    def _build_ui(self):
        # EDIT START — Agent 2: Add tabs for Achievements and Badges.
        root = QVBoxLayout(self)
        header = QLabel("Quest Log, Achievements, Badges")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        root.addWidget(header)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # Quest Log Tab
        quest_tab = QWidget()
        quest_layout = QVBoxLayout(quest_tab)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Status", "XP", "Difficulty"])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(0, 5):
            h.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        quest_layout.addWidget(self.table)
        # Buttons (expanded CRUD)
        btns = QHBoxLayout()
        self.new_btn = QPushButton("New")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.complete_btn = QPushButton("Complete")
        self.new_btn.clicked.connect(self._new_quest)
        self.edit_btn.clicked.connect(self._edit_quest)
        self.delete_btn.clicked.connect(self._delete_quest)
        self.complete_btn.clicked.connect(self._complete_quest)
        for b in (self.new_btn, self.edit_btn, self.delete_btn, self.complete_btn):
            btns.addWidget(b)
        btns.addStretch(1)
        quest_layout.addLayout(btns)
        self.tabs.addTab(quest_tab, "Quests")

        # Achievements Tab
        self.achievements_table = QTableWidget(0, 6)
        self.achievements_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "XP", "Completed", "Tags"])
        h2 = self.achievements_table.horizontalHeader()
        h2.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(0, 6):
            h2.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.achievements_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        ach_tab = QWidget()
        ach_layout = QVBoxLayout(ach_tab)
        ach_layout.addWidget(self.achievements_table)
        self.tabs.addTab(ach_tab, "Achievements")

        # Badges Tab
        self.badges_table = QTableWidget(0, 5)
        self.badges_table.setHorizontalHeaderLabels(["ID", "Name", "XP", "Completed", "Tags"])
        h3 = self.badges_table.horizontalHeader()
        h3.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(0, 5):
            h3.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.badges_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        badge_tab = QWidget()
        badge_layout = QVBoxLayout(badge_tab)
        badge_layout.addWidget(self.badges_table)
        self.tabs.addTab(badge_tab, "Badges")
        # EDIT END

    # ---------- helpers ----------
    def _set_item(self, row: int, col: int, text: str):
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, col, item)

    def _get_selected_quest_id(self) -> Optional[str]:
        if not self.table.selectionModel().hasSelection():
            return None
        row = self.table.selectionModel().selectedRows()[0].row()
        return self.table.item(row, 0).text()

    # ---------- data ops ----------
    @debug_button("_refresh", "Quest Log Panel")
    def _refresh(self):
        # EDIT START — Agent 2: Refresh all tabs (quests, achievements, badges).
        # Quests
        quests: List[Quest] = self.engine.get_active_quests() + self.engine.get_quests_by_status("available")
        self.table.setRowCount(len(quests))
        for row, q in enumerate(quests):
            self._set_item(row, 0, q.id)
            self._set_item(row, 1, q.title)
            self._set_item(row, 2, q.status)
            self._set_item(row, 3, str(q.xp_reward))
            self._set_item(row, 4, str(q.difficulty))
        self.tasks_changed.emit()
        # Achievements
        achievements = self.engine.get_achievements()
        self.achievements_table.setRowCount(len(achievements))
        for row, a in enumerate(achievements):
            self.achievements_table.setItem(row, 0, QTableWidgetItem(str(getattr(a, 'id', ''))))
            self.achievements_table.setItem(row, 1, QTableWidgetItem(str(getattr(a, 'name', ''))))
            self.achievements_table.setItem(row, 2, QTableWidgetItem(str(getattr(a, 'category', ''))))
            self.achievements_table.setItem(row, 3, QTableWidgetItem(str(getattr(a, 'xp_reward', ''))))
            self.achievements_table.setItem(row, 4, QTableWidgetItem(str(getattr(a, 'completed_at', ''))))
            self.achievements_table.setItem(row, 5, QTableWidgetItem(", ".join(getattr(a, 'tags', []))))
        # Badges
        badges = self.engine.get_badges()
        self.badges_table.setRowCount(len(badges))
        for row, b in enumerate(badges):
            self.badges_table.setItem(row, 0, QTableWidgetItem(str(getattr(b, 'id', ''))))
            self.badges_table.setItem(row, 1, QTableWidgetItem(str(getattr(b, 'name', ''))))
            self.badges_table.setItem(row, 2, QTableWidgetItem(str(getattr(b, 'xp_reward', ''))))
            self.badges_table.setItem(row, 3, QTableWidgetItem(str(getattr(b, 'completed_at', ''))))
            self.badges_table.setItem(row, 4, QTableWidgetItem(", ".join(getattr(b, 'tags', []))))
        # EDIT END

    # ---------- dialogs ----------
    class _QuestDialog(QDialog):
        def __init__(self, parent: QWidget, quest: Quest | None = None):
            super().__init__(parent)
            self.setWindowTitle("Quest")
            self.quest = quest
            layout = QFormLayout(self)
            self.title_edit = QLineEdit(quest.title if quest else "")
            self.desc_edit = QTextEdit(quest.description if quest else "")
            self.type_combo = QComboBox()
            for qt in QuestType:
                self.type_combo.addItem(qt.value, qt)
            if quest:
                self.type_combo.setCurrentText(quest.quest_type.value)
            self.diff_spin = QSpinBox()
            self.diff_spin.setRange(1, 10)
            self.diff_spin.setValue(quest.difficulty if quest else 1)
            self.xp_spin = QSpinBox()
            self.xp_spin.setRange(1, 10000)
            self.xp_spin.setValue(quest.xp_reward if quest else 10)

            layout.addRow("Title", self.title_edit)
            layout.addRow("Description", self.desc_edit)
            layout.addRow("Type", self.type_combo)
            layout.addRow("Difficulty", self.diff_spin)
            layout.addRow("XP", self.xp_spin)

            btn_box = QHBoxLayout()
            ok = QPushButton("OK")
            cancel = QPushButton("Cancel")
            ok.clicked.connect(self.accept)
            cancel.clicked.connect(self.reject)
            btn_box.addWidget(ok)
            btn_box.addWidget(cancel)
            layout.addRow(btn_box)

        def data(self):
            qt = self.type_combo.currentData()
            return {
                "title": self.title_edit.text(),
                "description": self.desc_edit.toPlainText(),
                "quest_type": qt,
                "difficulty": self.diff_spin.value(),
                "xp_reward": self.xp_spin.value(),
            }

    @debug_button("_new_quest", "Quest Log Panel")
    def _new_quest(self):
        dlg = self._QuestDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.data()
        import uuid, datetime
        q = Quest(
            id=str(uuid.uuid4())[:8],
            created_at=datetime.datetime.now(),
            completed_at=None,
            skill_rewards={},
            status="available",
            conversation_id=None,
            **data,
        )
        self.engine.add_quest(q)
        self._refresh()

    @debug_button("_edit_quest", "Quest Log Panel")
    def _edit_quest(self):
        qid = self._get_selected_quest_id()
        if not qid:
            return
        quest = self.engine.game_state.quests.get(qid)
        if not quest:
            return
        dlg = self._QuestDialog(self, quest)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.engine.update_quest(qid, **dlg.data())
        self._refresh()

    @debug_button("_delete_quest", "Quest Log Panel")
    def _delete_quest(self):
        qid = self._get_selected_quest_id()
        if not qid:
            return
        if QMessageBox.question(self, "Delete Quest", "Permanently delete this quest?") != QMessageBox.StandardButton.Yes:
            return
        self.engine.delete_quest(qid)
        self._refresh()

    # ---------- slots ----------
    @debug_button("_complete_quest", "Quest Log Panel")
    def _complete_quest(self):
        qid = self._get_selected_quest_id()
        if not qid:
            return
        if self.engine.complete_quest(qid):
            QMessageBox.information(self, "Quest", "Quest completed!")
        else:
            QMessageBox.warning(self, "Quest", "Unable to complete quest.")
        self._refresh() 