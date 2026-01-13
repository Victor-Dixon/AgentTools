"""
from gui.debug_handler import debug_button
Task Panel for Thea GUI
Handles task management and tracking.
Converted from Tkinter to PyQt6 for consistency.
"""

import asyncio
from gui.debug_handler import debug_button
import threading
from typing import Dict, List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QProgressBar, QGroupBox, QGridLayout,
    QMessageBox, QSplitter, QListWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, QDate
from PyQt6.QtGui import QFont

class TaskPanel(QWidget):
    """PyQt6 GUI panel for task management."""
    
    # Signals
    task_added = pyqtSignal(bool, str)
    task_updated = pyqtSignal(bool, str)
    task_completed = pyqtSignal(bool, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize task data
        self.tasks = []
        self.selected_task = None
        self.task_counter = 0
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self._load_sample_tasks()
        
    def _setup_ui(self):
        """Setup the PyQt6 user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📋 Task Management")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Main content
        self._create_main_content(layout)
        
        # Status section
        self._create_status_section(layout)
    
    @debug_button("_create_main_content", "Task Panel")
    def _create_main_content(self, parent_layout):
        """Create the main content area."""
        # Split view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Task list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Task list using shared component
        from gui.components.shared_components import SharedComponents, ComponentConfig, ComponentStyle
        components = SharedComponents()
        self.task_list_group = components.create_data_list(
            title="Tasks",
            items=[],  # Will be populated later
            selection_mode=QListWidget.SelectionMode.SingleSelection,
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        self.task_list = self.task_list_group.findChild(QListWidget)
        self.task_list.itemSelectionChanged.connect(self._on_task_selected)
        left_layout.addWidget(self.task_list_group)
        splitter.addWidget(left_widget)
        
        # Right side - Task details and controls
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Task details
        details_group = QGroupBox("Task Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        self.details_text.setPlaceholderText("Select a task to view details...")
        details_layout.addWidget(self.details_text)
        
        right_layout.addWidget(details_group)
        
        # Task controls
        controls_group = QGroupBox("Task Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Task input fields
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("Title:"), 0, 0)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter task title...")
        input_layout.addWidget(self.title_edit, 0, 1)
        
        input_layout.addWidget(QLabel("Description:"), 1, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Enter task description...")
        input_layout.addWidget(self.description_edit, 1, 1)
        
        input_layout.addWidget(QLabel("Priority:"), 2, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        input_layout.addWidget(self.priority_combo, 2, 1)
        
        input_layout.addWidget(QLabel("Status:"), 3, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "In Progress", "Completed", "Cancelled"])
        input_layout.addWidget(self.status_combo, 3, 1)
        
        input_layout.addWidget(QLabel("Due Date:"), 4, 0)
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))
        self.due_date_edit.setCalendarPopup(True)
        input_layout.addWidget(self.due_date_edit, 4, 1)
        
        controls_layout.addLayout(input_layout)
        
        # Control buttons using shared component
        actions = [
            {
                "text": "Add Task",
                "callback": self._add_task,
                "id": "add_task"
            },
            {
                "text": "Update Task",
                "callback": self._update_task,
                "id": "update_task",
                "enabled": False
            },
            {
                "text": "Complete Task",
                "callback": self._complete_task,
                "id": "complete_task",
                "enabled": False
            }
        ]
        actions_panel = components.create_action_panel(
            title="Task Actions",
            actions=actions,
            config=ComponentConfig(style=ComponentStyle.PRIMARY)
        )
        self.add_btn = actions_panel.findChild(QPushButton, "add_task")
        self.update_btn = actions_panel.findChild(QPushButton, "update_task")
        self.complete_btn = actions_panel.findChild(QPushButton, "complete_task")
        controls_layout.addWidget(actions_panel)
        right_layout.addWidget(controls_group)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("0% Complete")
        progress_layout.addWidget(self.progress_label)
        
        right_layout.addWidget(progress_group)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        
        parent_layout.addWidget(splitter)
    
    @debug_button("_create_status_section", "Task Panel")
    def _create_status(self):
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
                title="task_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
    def _load_sample_tasks(self):
        """Load sample tasks for demonstration."""
        sample_tasks = [
            {
                'id': 1,
                'title': 'Complete GUI Documentation',
                'description': 'Document all buttons and their functionality in the Thea GUI',
                'priority': 'High',
                'status': 'In Progress',
                'due_date': '2025-01-15',
                'created_at': '2025-01-10',
                'progress': 75
            },
            {
                'id': 2,
                'title': 'Convert Tkinter to PyQt6',
                'description': 'Convert all remaining Tkinter panels to PyQt6 for consistency',
                'priority': 'Critical',
                'status': 'Completed',
                'due_date': '2025-01-12',
                'created_at': '2025-01-08',
                'progress': 100
            },
            {
                'id': 3,
                'title': 'Test All GUI Buttons',
                'description': 'Create comprehensive tests for all GUI buttons and functionality',
                'priority': 'Medium',
                'status': 'Pending',
                'due_date': '2025-01-20',
                'created_at': '2025-01-10',
                'progress': 0
            }
        ]
        
        self.tasks = sample_tasks
        self.task_counter = len(sample_tasks) + 1
        self._update_task_list()
        self._update_progress()
    
    @debug_button("_update_task_list", "Task Panel")
    def _update_task_list(self):
        """Update the task list display."""
        self.task_list.clear()
        for task in self.tasks:
            status_icon = "DONE" if task['status'] == 'Completed' else "IN PROGRESS" if task['status'] == 'In Progress' else "PENDING"
            priority_icon = "🔴" if task['priority'] == 'Critical' else "🟡" if task['priority'] == 'High' else "🟢"
            self.task_list.addItem(f"{status_icon} {priority_icon} {task['title']}")
    
    @debug_button("_update_progress", "Task Panel")
    def _update_progress(self):
        """Update the overall progress display."""
        if not self.tasks:
            self.progress_bar.setValue(0)
            self.progress_label.setText("0% Complete")
            return
        
        completed_tasks = sum(1 for task in self.tasks if task['status'] == 'Completed')
        total_tasks = len(self.tasks)
        progress_percentage = int((completed_tasks / total_tasks) * 100)
        
        self.progress_bar.setValue(progress_percentage)
        self.progress_label.setText(f"{progress_percentage}% Complete ({completed_tasks}/{total_tasks} tasks)")
    
    @debug_button("_on_task_selected", "Task Panel")
    def _on_task_selected(self):
        """Handle task selection."""
        current_item = self.task_list.currentItem()
        if current_item:
            index = self.task_list.row(current_item)
            if 0 <= index < len(self.tasks):
                self.selected_task = self.tasks[index]
                self._display_task_details(self.selected_task)
                self._enable_task_controls()
        else:
            self.selected_task = None
            self._disable_task_controls()
    
    def _display_task_details(self, task: Dict):
        """Display task details."""
        details = f"Title: {task['title']}\n"
        details += f"Description: {task['description']}\n"
        details += f"Priority: {task['priority']}\n"
        details += f"Status: {task['status']}\n"
        details += f"Due Date: {task['due_date']}\n"
        details += f"Created: {task['created_at']}\n"
        details += f"Progress: {task['progress']}%\n\n"
        
        if task['status'] == 'Completed':
            details += "Task completed successfully!"
        elif task['status'] == 'In Progress':
            details += "⏳ Task is currently in progress..."
        elif task['status'] == 'Cancelled':
            details += "Task has been cancelled."
        else:
            details += "Task is pending..."
        
        self.details_text.setPlainText(details)
    
    @debug_button("_add_task", "Task Panel")
    def _add_task(self):
        """Add a new task."""
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Warning", "Please enter a task title.")
            return
        
        new_task = {
            'id': self.task_counter,
            'title': title,
            'description': description,
            'priority': self.priority_combo.currentText(),
            'status': 'Pending',
            'due_date': self.due_date_edit.date().toString('yyyy-MM-dd'),
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'progress': 0
        }
        
        self.tasks.append(new_task)
        self.task_counter += 1
        
        self._update_task_list()
        self._update_progress()
        self._clear_inputs()
        
        self._update_status("Task added", f"Successfully added task: {title}")
        self.task_added.emit(True, f"Task '{title}' added successfully")
    
    @debug_button("_update_task", "Task Panel")
    def _update_task(self):
        """Update the selected task."""
        if not self.selected_task:
            QMessageBox.warning(self, "Warning", "Please select a task to update.")
            return
        
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Warning", "Please enter a task title.")
            return
        
        # Update the task
        self.selected_task['title'] = title
        self.selected_task['description'] = description
        self.selected_task['priority'] = self.priority_combo.currentText()
        self.selected_task['status'] = self.status_combo.currentText()
        self.selected_task['due_date'] = self.due_date_edit.date().toString('yyyy-MM-dd')
        
        # Update progress based on status
        if self.selected_task['status'] == 'Completed':
            self.selected_task['progress'] = 100
        elif self.selected_task['status'] == 'In Progress':
            self.selected_task['progress'] = 50
        else:
            self.selected_task['progress'] = 0
        
        self._update_task_list()
        self._update_progress()
        self._display_task_details(self.selected_task)
        
        self._update_status("Task updated", f"Successfully updated task: {title}")
        self.task_updated.emit(True, f"Task '{title}' updated successfully")
    
    @debug_button("_complete_task", "Task Panel")
    def _complete_task(self):
        """Mark the selected task as completed."""
        if not self.selected_task:
            QMessageBox.warning(self, "Warning", "Please select a task to complete.")
            return
        
        self.selected_task['status'] = 'Completed'
        self.selected_task['progress'] = 100
        
        self._update_task_list()
        self._update_progress()
        self._display_task_details(self.selected_task)
        
        # Update input fields
        self.status_combo.setCurrentText('Completed')
        
        self._update_status("Task completed", f"Successfully completed task: {self.selected_task['title']}")
        self.task_completed.emit(True, f"Task '{self.selected_task['title']}' completed successfully")
    
    @debug_button("_clear_inputs", "Task Panel")
    def _clear_inputs(self):
        """Clear input fields."""
        self.title_edit.clear()
        self.description_edit.clear()
        self.priority_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))
    
    def _enable_task_controls(self):
        """Enable task control buttons when task is selected."""
        self.update_btn.setEnabled(True)
        self.complete_btn.setEnabled(True)
        
        # Populate input fields with selected task data
        if self.selected_task:
            self.title_edit.setText(self.selected_task['title'])
            self.description_edit.setPlainText(self.selected_task['description'])
            
            # Set priority
            priority_index = self.priority_combo.findText(self.selected_task['priority'])
            if priority_index >= 0:
                self.priority_combo.setCurrentIndex(priority_index)
            
            # Set status
            status_index = self.status_combo.findText(self.selected_task['status'])
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)
            
            # Set due date
            due_date = QDate.fromString(self.selected_task['due_date'], 'yyyy-MM-dd')
            if due_date.isValid():
                self.due_date_edit.setDate(due_date)
    
    def _disable_task_controls(self):
        """Disable task control buttons when no task is selected."""
        self.update_btn.setEnabled(False)
        self.complete_btn.setEnabled(False)
        self._clear_inputs()
    
    @debug_button("_update_status", "Task Panel")
    def _update_status(self):
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
                title="task_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
    def get_task_count(self) -> int:
        """Get the total number of tasks."""
        return len(self.tasks)
    
    def get_completed_task_count(self) -> int:
        """Get the number of completed tasks."""
        return sum(1 for task in self.tasks if task['status'] == 'Completed')
    
    def get_pending_task_count(self) -> int:
        """Get the number of pending tasks."""
        return sum(1 for task in self.tasks if task['status'] == 'Pending')
    
    def get_in_progress_task_count(self) -> int:
        """Get the number of in-progress tasks."""
        return sum(1 for task in self.tasks if task['status'] == 'In Progress')
    
    def get_tasks_by_priority(self, priority: str) -> List[Dict]:
        """Get tasks filtered by priority."""
        return [task for task in self.tasks if task['priority'] == priority]
    
    def get_tasks_by_status(self):
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
                title="task_panel Statistics",
                style="modern"
            )
            
            return stats_widget
            
        except Exception as e:
            logger.error(f"Error creating statistics grid: {e}")
            return QWidget()  # Fallback widget
