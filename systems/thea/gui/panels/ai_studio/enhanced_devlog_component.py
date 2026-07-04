#!/usr/bin/env python3
"""
Enhanced Devlog Component
=========================

This component handles enhanced devlog functionality including:
- Devlog creation and editing
- Quick devlog entries
- Devlog history
- Devlog integration
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QComboBox, QGroupBox, QGridLayout,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from dreamscape.core.memory_system import MemoryManager
from dreamscape.core.mmorpg.mmorpg_engine import MMORPGEngine
from gui.debug_handler import debug_button

logger = logging.getLogger(__name__)

class EnhancedDevlogComponent(QWidget):
    """Enhanced Devlog component for devlog management and integration."""
    
    # Signals
    devlog_created = pyqtSignal(dict)  # Devlog entry created
    devlog_opened = pyqtSignal(str)    # Devlog opened
    quick_devlog_created = pyqtSignal(str)  # Quick devlog created
    
    def __init__(self, memory_manager: MemoryManager = None, mmorpg_engine: MMORPGEngine = None):
        super().__init__()
        self.memory_manager = memory_manager or MemoryManager()
        self.mmorpg_engine = mmorpg_engine or MMORPGEngine()
        
        # Devlog data
        self.devlog_entries = []
        self.current_devlog = None
        
        # UI Components
        self.devlog_list = None
        self.devlog_content = None
        self.open_devlog_btn = None
        self.quick_devlog_btn = None
        self.show_history_btn = None
        self.create_devlog_btn = None
        
        self.init_ui()
        self.connect_signals()
        self.load_devlog_entries()
    
    def init_ui(self):
        """Initialize the enhanced devlog user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("📝 Enhanced Devlog - Development Logging and Integration")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel - Devlog list
        left_panel = QVBoxLayout()
        
        list_group = QGroupBox("Devlog Entries")
        list_layout = QVBoxLayout(list_group)
        
        self.devlog_list = QListWidget()
        self.devlog_list.setMaximumWidth(300)
        list_layout.addWidget(self.devlog_list)
        
        # Devlog list buttons
        list_buttons_layout = QGridLayout()
        
        self.create_devlog_btn = QPushButton("📝 Create Devlog")
        list_buttons_layout.addWidget(self.create_devlog_btn, 0, 0)
        
        self.open_devlog_btn = QPushButton("📖 Open Devlog")
        self.open_devlog_btn.setEnabled(False)
        list_buttons_layout.addWidget(self.open_devlog_btn, 0, 1)
        
        self.quick_devlog_btn = QPushButton("⚡ Quick Devlog")
        list_buttons_layout.addWidget(self.quick_devlog_btn, 1, 0)
        
        self.show_history_btn = QPushButton("📚 History")
        list_buttons_layout.addWidget(self.show_history_btn, 1, 1)
        
        list_layout.addLayout(list_buttons_layout)
        left_panel.addWidget(list_group)
        
        content_layout.addLayout(left_panel)
        
        # Right panel - Devlog content
        right_panel = QVBoxLayout()
        
        content_group = QGroupBox("Devlog Content")
        content_layout_right = QVBoxLayout(content_group)
        
        self.devlog_content = QTextEdit()
        self.devlog_content.setReadOnly(True)
        self.devlog_content.setPlaceholderText("Select a devlog entry to view content...")
        content_layout_right.addWidget(self.devlog_content)
        
        right_panel.addWidget(content_group)
        
        content_layout.addLayout(right_panel)
        layout.addLayout(content_layout)
        layout.addStretch()
    
    def connect_signals(self):
        """Connect all signals and slots."""
        self.devlog_list.itemClicked.connect(self.on_devlog_selected)
        self.create_devlog_btn.clicked.connect(self.create_devlog)
        self.open_devlog_btn.clicked.connect(self.open_devlog)
        self.quick_devlog_btn.clicked.connect(self.quick_devlog)
        self.show_history_btn.clicked.connect(self.show_devlog_history)
    
    def load_devlog_entries(self):
        """Load devlog entries."""
        try:
            # Simulate loading devlog entries
            self.devlog_entries = [
                {
                    'id': 'devlog_1',
                    'title': 'AI Studio Refactoring Progress',
                    'date': '2024-01-15',
                    'content': 'Started refactoring the AI Studio panel into modular components. Created ConversationalAIComponent and IntelligentAgentComponent. Progress is good.',
                    'tags': ['refactoring', 'ai-studio', 'modularization']
                },
                {
                    'id': 'devlog_2',
                    'title': 'Model Training Implementation',
                    'date': '2024-01-14',
                    'content': 'Implemented the agent training system with progress tracking and result visualization. Training pipeline is working well.',
                    'tags': ['training', 'models', 'implementation']
                },
                {
                    'id': 'devlog_3',
                    'title': 'Analytics Dashboard Enhancement',
                    'date': '2024-01-13',
                    'content': 'Enhanced the analytics dashboard with new metrics and improved visualization. User feedback is positive.',
                    'tags': ['analytics', 'dashboard', 'enhancement']
                }
            ]
            
            self.refresh_devlog_list()
            logger.info(f"Loaded {len(self.devlog_entries)} devlog entries")
            
        except Exception as e:
            logger.error(f"Error loading devlog entries: {e}")
    
    def refresh_devlog_list(self):
        """Refresh the devlog list display."""
        self.devlog_list.clear()
        
        for entry in self.devlog_entries:
            item = QListWidgetItem(f"{entry['title']} ({entry['date']})")
            item.setData(Qt.ItemDataRole.UserRole, entry['id'])
            self.devlog_list.addItem(item)
    
    def on_devlog_selected(self, item: QListWidgetItem):
        """Handle devlog selection."""
        devlog_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_devlog = devlog_id
        
        # Find and display devlog content
        for entry in self.devlog_entries:
            if entry['id'] == devlog_id:
                self.display_devlog_content(entry)
                self.open_devlog_btn.setEnabled(True)
                break
    
    def display_devlog_content(self, entry: Dict[str, Any]):
        """Display devlog content."""
        content_text = f"""=== Devlog Entry ===
Title: {entry.get('title', 'Unknown')}
Date: {entry.get('date', 'Unknown')}
Tags: {', '.join(entry.get('tags', []))}

=== Content ===
{entry.get('content', 'No content available')}

=== Entry Information ===
• Entry ID: {entry.get('id', 'Unknown')}
• Created: {entry.get('date', 'Unknown')}
• Tags: {len(entry.get('tags', []))} tags
• Content Length: {len(entry.get('content', ''))} characters

=== Quick Actions ===
• Edit this entry
• Add to favorites
• Share with team
• Export entry"""
        
        self.devlog_content.setPlainText(content_text)
    
    @debug_button("create_devlog", "Enhanced Devlog Component")
    def create_devlog(self):
        """Create a new devlog entry."""
        # Get devlog details from user
        title, ok = QInputDialog.getText(self, "Create Devlog", "Enter devlog title:")
        if not ok or not title.strip():
            return
        
        content, ok = QInputDialog.getMultiLineText(self, "Create Devlog", "Enter devlog content:")
        if not ok:
            return
        
        # Create new devlog entry
        new_entry = {
            'id': f"devlog_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': title.strip(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'content': content.strip() if content else '',
            'tags': ['new', 'created']
        }
        
        self.devlog_entries.append(new_entry)
        self.refresh_devlog_list()
        
        # Emit devlog created signal
        self.devlog_created.emit(new_entry)
        
        logger.info(f"Created new devlog: {title}")
    
    @debug_button("open_devlog", "Enhanced Devlog Component")
    def open_devlog(self):
        """Open the selected devlog for editing."""
        if not self.current_devlog:
            return
        
        # Find the devlog entry
        for entry in self.devlog_entries:
            if entry['id'] == self.current_devlog:
                # Emit devlog opened signal
                self.devlog_opened.emit(self.current_devlog)
                
                QMessageBox.information(
                    self, 
                    "Open Devlog", 
                    f"Opening devlog: {entry['title']}\n\nThis would open the devlog in the main devlog editor."
                )
                
                logger.info(f"Opening devlog: {entry['title']}")
                break
    
    @debug_button("quick_devlog", "Enhanced Devlog Component")
    def quick_devlog(self):
        """Create a quick devlog entry."""
        content, ok = QInputDialog.getMultiLineText(
            self, 
            "Quick Devlog", 
            "Enter quick devlog entry:"
        )
        
        if not ok or not content.strip():
            return
        
        # Create quick devlog entry
        quick_entry = {
            'id': f"quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': f"Quick Entry - {datetime.now().strftime('%H:%M')}",
            'date': datetime.now().strftime('%Y-%m-%d'),
            'content': content.strip(),
            'tags': ['quick', 'note']
        }
        
        self.devlog_entries.append(quick_entry)
        self.refresh_devlog_list()
        
        # Emit quick devlog created signal
        self.quick_devlog_created.emit(content.strip())
        
        logger.info("Created quick devlog entry")
    
    @debug_button("show_devlog_history", "Enhanced Devlog Component")
    def show_devlog_history(self):
        """Show devlog history and statistics."""
        if not self.devlog_entries:
            QMessageBox.information(self, "History", "No devlog entries found.")
            return
        
        # Generate history report
        history_text = f"""=== Devlog History Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== Summary ===
Total Entries: {len(self.devlog_entries)}
Date Range: {min(entry['date'] for entry in self.devlog_entries)} to {max(entry['date'] for entry in self.devlog_entries)}
Average Entries per Day: {len(self.devlog_entries) / max(1, (datetime.now() - datetime.strptime(min(entry['date'] for entry in self.devlog_entries), '%Y-%m-%d')).days):.1f}

=== Recent Entries ===
"""
        
        # Show recent entries (last 5)
        recent_entries = sorted(self.devlog_entries, key=lambda x: x['date'], reverse=True)[:5]
        for i, entry in enumerate(recent_entries, 1):
            history_text += f"{i}. {entry['title']} ({entry['date']})\n"
        
        history_text += f"""
=== Tag Analysis ===
"""
        
        # Analyze tags
        all_tags = []
        for entry in self.devlog_entries:
            all_tags.extend(entry.get('tags', []))
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
            history_text += f"• {tag}: {count} entries\n"
        
        history_text += f"""
=== Content Statistics ===
Total Content Length: {sum(len(entry.get('content', '')) for entry in self.devlog_entries):,} characters
Average Entry Length: {sum(len(entry.get('content', '')) for entry in self.devlog_entries) / len(self.devlog_entries):.0f} characters
Longest Entry: {max(len(entry.get('content', '')) for entry in self.devlog_entries):,} characters

=== Recommendations ===
• Continue regular devlog entries for project tracking
• Use tags consistently for better organization
• Consider longer entries for complex topics
• Review and update older entries as needed"""
        
        self.devlog_content.setPlainText(history_text)
    
    def get_devlog_entries(self) -> List[Dict[str, Any]]:
        """Get all devlog entries."""
        return self.devlog_entries.copy()
    
    def get_current_devlog(self) -> Optional[str]:
        """Get the currently selected devlog ID."""
        return self.current_devlog
    
    def add_devlog_entry(self, entry: Dict[str, Any]):
        """Add a new devlog entry."""
        self.devlog_entries.append(entry)
        self.refresh_devlog_list()
    
    def update_devlog_entry(self, devlog_id: str, updates: Dict[str, Any]):
        """Update a devlog entry."""
        for entry in self.devlog_entries:
            if entry['id'] == devlog_id:
                entry.update(updates)
                if devlog_id == self.current_devlog:
                    self.display_devlog_content(entry)
                break
    
    def delete_devlog_entry(self, devlog_id: str):
        """Delete a devlog entry."""
        self.devlog_entries = [entry for entry in self.devlog_entries if entry['id'] != devlog_id]
        self.refresh_devlog_list()
        
        if devlog_id == self.current_devlog:
            self.current_devlog = None
            self.devlog_content.clear()
            self.open_devlog_btn.setEnabled(False)
    
    def search_devlog_entries(self, query: str) -> List[Dict[str, Any]]:
        """Search devlog entries."""
        query_lower = query.lower()
        results = []
        
        for entry in self.devlog_entries:
            if (query_lower in entry.get('title', '').lower() or
                query_lower in entry.get('content', '').lower() or
                any(query_lower in tag.lower() for tag in entry.get('tags', []))):
                results.append(entry)
        
        return results
    
    def export_devlog_entries(self, file_path: str):
        """Export devlog entries to file."""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'entries': self.devlog_entries,
                'total_entries': len(self.devlog_entries)
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Devlog entries exported to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting devlog entries: {e}")
    
    def clear_devlog_content(self):
        """Clear the devlog content display."""
        self.devlog_content.clear()
        self.current_devlog = None
        self.open_devlog_btn.setEnabled(False) 