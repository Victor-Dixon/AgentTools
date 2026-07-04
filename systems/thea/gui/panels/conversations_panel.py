"""
Conversations Panel for Thea GUI
Displays and manages conversation history.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTextEdit, QLineEdit,
    QSplitter, QHeaderView, QMessageBox, QComboBox, QFileDialog
)
from gui.debug_handler import debug_button
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from typing import List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Helper item so the "Messages" column sorts numerically
class NumericItem(QTableWidgetItem):
    def __init__(self, value: int):
        super().__init__(str(value))
        self._value = value

    def __lt__(self, other: "QTableWidgetItem") -> bool:  # type: ignore[override]
        if isinstance(other, NumericItem):
            return self._value < other._value
        # Fallback to default behavior for non-numeric items
        try:
            return float(self.text()) < float(other.text())
        except Exception:
            return super().__lt__(other)

class ConversationsPanel(QWidget):
    """Panel for managing and viewing conversations."""
    
    # Signals
    conversation_selected = pyqtSignal(dict)
    refresh_requested = pyqtSignal()
    process_conversations_requested = pyqtSignal()
    update_statistics_requested = pyqtSignal()
    import_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Pagination state
        self.current_page = 1
        self.page_size = 100
        self.total_conversations = 0
        self.total_pages = 1
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the conversations UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header()
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - conversation list
        self.create_conversation_list(splitter)
        
        # Right side - conversation viewer
        self.create_conversation_viewer(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.prev_page_btn = QPushButton("← Previous")
        self.prev_page_btn.clicked.connect(self.previous_page)
        self.prev_page_btn.setEnabled(False)
        self.prev_page_btn.setToolTip("Go to previous page")
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_info_label = QLabel("Page 1 of 1")
        self.page_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(self.page_info_label)
        
        self.next_page_btn = QPushButton("Next →")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        self.next_page_btn.setToolTip("Go to next page")
        pagination_layout.addWidget(self.next_page_btn)
        
        # Add page size selector
        pagination_layout.addWidget(QLabel("Page Size:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "200", "500", "All"])
        self.page_size_combo.setCurrentText("100")
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        pagination_layout.addWidget(self.page_size_combo)
        
        pagination_layout.addStretch()
        
        # Add total count label
        self.total_count_label = QLabel("Total: 0 conversations")
        pagination_layout.addWidget(self.total_count_label)
        
        layout.addLayout(pagination_layout)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.refresh_requested.emit)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_selected_conversation)
        QShortcut(QKeySequence("Ctrl+Right"), self).activated.connect(self.next_page)
        QShortcut(QKeySequence("Ctrl+Left"), self).activated.connect(self.previous_page)
    
    @debug_button("create_header", "Conversations Panel")
    def create_header(self):
        """Create panel header using shared components with unified load button."""
        try:
            from gui.components.shared_components import SharedComponents
            from gui.components.unified_load_button import UnifiedLoadButton
            
            components = SharedComponents()
            
            # Create header with title and icon
            header_widget = components.create_panel_header(
                title="Conversations",
                icon="💬"
            )
            
            # Add unified load button
            self.unified_load_btn = UnifiedLoadButton(
                data_type="conversations",
                text="Load Conversations",
                priority="NORMAL"
            )
            
            # Connect signals
            self.unified_load_btn.load_completed.connect(self.on_conversations_loaded)
            
            # Add the load button to the header layout
            if hasattr(header_widget, 'layout'):
                header_widget.layout().addWidget(self.unified_load_btn)
            
            return header_widget
            
        except Exception as e:
            logger.error(f"Error creating panel header: {e}")
            return QWidget()  # Fallback widget
    
    def on_conversations_loaded(self, data_type: str, success: bool, message: str, result: Any):
        """Handle conversations load completion."""
        if success and data_type == "conversations":
            # Refresh the conversations display
            self.load_all_conversations()
        elif not success:
            # Show error message
            QMessageBox.warning(self, "Load Error", f"Failed to load conversations: {message}")

    def create_conversation_list(self, parent):
        """Create the conversation list table."""
        # Container widget
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table
        self.conversations_table = QTableWidget()
        self.conversations_table.setColumnCount(4)
        self.conversations_table.setHorizontalHeaderLabels([
            "Title", "Source", "Messages", "Date"
        ])
        
        # Configure table
        header = self.conversations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Allow user to sort columns (numeric sort handled via NumericItem for message count)
        self.conversations_table.setSortingEnabled(True)

        # Enable internal drag and drop to reorder rows
        self.conversations_table.setDragEnabled(True)
        self.conversations_table.setAcceptDrops(True)
        self.conversations_table.setDragDropMode(QTableWidget.DragDropMode.InternalMove)
        
        self.conversations_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.conversations_table.itemSelectionChanged.connect(self.on_conversation_selected)
        
        list_layout.addWidget(self.conversations_table)
        
        # Status label
        self.status_label = QLabel("No conversations loaded")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        list_layout.addWidget(self.status_label)
        
        # Add note about chronological order
        order_note = QLabel("📅 Conversations shown in chronological order (oldest first)")
        order_note.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        list_layout.addWidget(order_note)
        
        parent.addWidget(list_widget)
    
    @debug_button("create_conversation_viewer", "Conversations Panel")
    def create_conversation_viewer(self, parent):
        """Create the conversation viewer."""
        # Container widget
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout(viewer_widget)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Viewer header
        viewer_header = QHBoxLayout()
        
        self.viewer_title = QLabel("Select a conversation to view")
        self.viewer_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        viewer_header.addWidget(self.viewer_title)
        
        viewer_header.addStretch()
        
        # Export button
        self.export_btn = QPushButton("🚀 Export Center")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.show_export_center)
        self.export_btn.setToolTip("Open Unified Export Center")
        viewer_header.addWidget(self.export_btn)
        
        # Generate Training Data button
        self.generate_training_data_btn = QPushButton("🤖 Generate Training Data")
        self.generate_training_data_btn.setEnabled(False)
        self.generate_training_data_btn.clicked.connect(self.generate_training_data_for_selected)
        self.generate_training_data_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 5px; }")
        self.generate_training_data_btn.setToolTip("Create training data from conversation")
        viewer_header.addWidget(self.generate_training_data_btn)
        
        viewer_layout.addLayout(viewer_header)
        
        # Conversation content
        self.conversation_content = QTextEdit()
        self.conversation_content.setReadOnly(True)
        self.conversation_content.setPlaceholderText("Select a conversation from the list to view its content...")
        viewer_layout.addWidget(self.conversation_content)
        
        parent.addWidget(viewer_widget)
    
    @debug_button("update_conversations_table", "Conversations Panel")
    def update_conversations_table(self, conversations: List[Dict]):
        """Update the conversations table with new data."""
        self.conversations_table.setRowCount(len(conversations))
        
        for row, conversation in enumerate(conversations):
            # Title
            title_item = QTableWidgetItem(conversation.get('title', 'Untitled'))
            title_item.setData(Qt.ItemDataRole.UserRole, conversation)
            self.conversations_table.setItem(row, 0, title_item)
            
            # Source (instead of model)
            source_item = QTableWidgetItem(conversation.get('source', 'Unknown'))
            self.conversations_table.setItem(row, 1, source_item)
            
            # Message count
            message_count = int(conversation.get('message_count', 0))
            message_item = NumericItem(message_count)
            self.conversations_table.setItem(row, 2, message_item)
            
            # Date
            created_at = conversation.get('created_at', '')
            if created_at:
                # Format date for display
                try:
                    from datetime import datetime
                    if isinstance(created_at, str):
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        dt = created_at
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = str(created_at)[:19]  # First 19 chars for YYYY-MM-DD HH:MM:SS
            else:
                date_str = 'Unknown'
            
            date_item = QTableWidgetItem(date_str)
            self.conversations_table.setItem(row, 3, date_item)
        
        self.status_label.setText(f"Loaded {len(conversations)} conversations in chronological order")
    
    @debug_button("on_conversation_selected", "Conversations Panel")
    def on_conversation_selected(self):
        """Handle conversation selection."""
        current_row = self.conversations_table.currentRow()
        if current_row >= 0:
            item = self.conversations_table.item(current_row, 0)
            if item:
                conversation = item.data(Qt.ItemDataRole.UserRole)
                self.view_conversation(conversation)
    
    def view_conversation(self, conversation: Dict):
        """Display a conversation in the viewer."""
        if not conversation:
            return
        
        # Update title
        title = conversation.get('title', 'Untitled')
        self.viewer_title.setText(title)
        
        # Update content
        content = conversation.get('content', 'No content available')
        self.conversation_content.setPlainText(content)
        
        # Enable export button
        self.export_btn.setEnabled(True)
        
        # Enable generate training data button
        self.generate_training_data_btn.setEnabled(True)
        
        # Emit signal
        self.conversation_selected.emit(conversation)
    
    @debug_button("filter_conversations", "Conversations Panel")
    def filter_conversations(self, text: str):
        """Filter conversations based on search text."""
        for row in range(self.conversations_table.rowCount()):
            title_item = self.conversations_table.item(row, 0)
            if title_item:
                title = title_item.text().lower()
                should_show = not text or text.lower() in title
                self.conversations_table.setRowHidden(row, not should_show)
    
    def get_selected_conversation(self) -> Dict:
        """Get the currently selected conversation."""
        current_row = self.conversations_table.currentRow()
        if current_row >= 0:
            item = self.conversations_table.item(current_row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return {}
    
    @debug_button("clear_viewer", "Conversations Panel")
    def clear_viewer(self):
        """Clear the conversation viewer."""
        self.viewer_title.setText("Select a conversation to view")
        self.conversation_content.clear()
        self.export_btn.setEnabled(False)
        self.generate_training_data_btn.setEnabled(False)
    
    @debug_button("export_selected_conversation", "Conversations Panel")
    def export_selected_conversation(self):
        """Export the selected conversation."""
        conversation = self.get_selected_conversation()
        if not conversation:
            QMessageBox.warning(self, "No Selection", "Please select a conversation to export.")
            return

        try:
            # Get file path for export
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Conversation",
                f"{conversation['title']}.json",
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
            )

            if file_path:
                # Export conversation data
                export_data = {
                    "title": conversation["title"],
                    "content": conversation["content"],
                    "source": conversation.get("source", "Unknown"),
                    "message_count": conversation.get("message_count", 0),
                    "created_at": conversation.get("created_at", ""),
                    "exported_at": datetime.now().isoformat(),
                    "version": "1.0"
                }

                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    # Export as text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Title: {export_data['title']}\n")
                        f.write(f"Source: {export_data['source']}\n")
                        f.write(f"Message Count: {export_data['message_count']}\n")
                        f.write(f"Created: {export_data['created_at']}\n")
                        f.write(f"Exported: {export_data['exported_at']}\n")
                        f.write("\n" + "="*50 + "\n\n")
                        f.write(export_data['content'])

                QMessageBox.information(
                    self, "Export Success", f"Conversation exported to:\n{file_path}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export conversation: {e}")

    def show_export_center(self):
        """Show the Unified Export Center for conversations."""
        try:
            # Get current conversation data for export
            conversation = self.get_selected_conversation()
            
            if conversation:
                # Export selected conversation
                export_data = {
                    "title": conversation["title"],
                    "content": conversation["content"],
                    "source": conversation.get("source", "Unknown"),
                    "message_count": conversation.get("message_count", 0),
                    "created_at": conversation.get("created_at", ""),
                    "exported_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            else:
                # Export all conversations (placeholder)
                export_data = {
                    "conversations": [],
                    "exported_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            
            # Create and show Unified Export Center
            from gui.components.unified_export_center import UnifiedExportCenter
            export_center = UnifiedExportCenter()
            
            # Set the data for export
            export_center._get_data_for_type = lambda data_type: export_data
            
            export_center.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to open export center: {e}")
    
    @debug_button("generate_training_data_for_selected", "Conversations Panel")
    def generate_training_data_for_selected(self):
        """Generate structured training data for the currently selected conversation."""
        conversation = self.get_selected_conversation()
        if not conversation:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select a conversation to generate training data for.")
            return
        
        try:
            from PyQt6.QtWidgets import QMessageBox, QProgressDialog
            from PyQt6.QtCore import QThread, pyqtSignal
            
            # Create a progress dialog
            progress = QProgressDialog("Generating structured training data...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setAutoClose(True)
            progress.show()
            
            # Create a worker thread for the generation
            class TrainingDataWorker(QThread):
                finished = pyqtSignal(dict)
                progress = pyqtSignal(str, int, int)
                
                def __init__(self, conversation):
                    super().__init__()
                    self.conversation = conversation
                
                def run(self):
                    try:
                        from dreamscape.core.training_data_orchestrator import TrainingDataOrchestrator
                        
                        orchestrator = TrainingDataOrchestrator()
                        
                        def progress_callback(message, current, total):
                            self.progress.emit(message, current, total)
                        
                        result = orchestrator.generate_structured_data_for_conversation(
                            self.conversation,
                            use_chatgpt=True,
                            headless=False,  # Show browser for manual login if needed
                            progress_callback=progress_callback
                        )
                        
                        self.finished.emit(result)
                        
                    except Exception as e:
                        self.finished.emit({
                            "success": False,
                            "error": str(e)
                        })
            
            # Start the worker thread
            worker = TrainingDataWorker(conversation)
            
            def on_progress(message, current, total):
                progress.setLabelText(message)
                if total > 0:
                    progress.setValue(int((current / total) * 100))
            
            def on_finished(result):
                progress.close()
                
                if result.get("success", False):
                    output_file = result.get("output_file", "Unknown")
                    QMessageBox.information(
                        self, 
                        "Training Data Generated", 
                        f"Structured training data generated successfully!\n\n"
                        f"Saved to: {output_file}\n\n"
                        f"Conversation: {result.get('title', 'Unknown')}"
                    )
                else:
                    error_msg = result.get("error", "Unknown error")
                    QMessageBox.critical(
                        self, 
                        "Generation Failed", 
                        f"Failed to generate training data:\n{error_msg}"
                    )
            
            worker.progress.connect(on_progress)
            worker.finished.connect(on_finished)
            worker.start()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to start training data generation:\n{str(e)}")
    
    @debug_button("previous_page", "Conversations Panel")
    def previous_page(self):
        """Go to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_current_page()
    
    @debug_button("next_page", "Conversations Panel")
    def next_page(self):
        """Go to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_current_page()
    
    @debug_button("on_page_size_changed", "Conversations Panel")
    def on_page_size_changed(self, new_size: str):
        """Handle page size change from the combo box."""
        # Special sentinel: "All" -> 0 means unlimited (fetch all rows)
        if new_size.lower() == "all":
            self.page_size = 0
        else:
            try:
                self.page_size = int(new_size)
            except ValueError:
                # Fallback to default 100 if parsing fails
                self.page_size = 100

        self.current_page = 1  # Reset to first page whenever size changes
        self.calculate_total_pages()
        self.load_current_page()
    
    def calculate_total_pages(self):
        """Calculate total number of pages."""
        if self.page_size > 0:
            self.total_pages = (self.total_conversations + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 1
    
    @debug_button("update_pagination_controls", "Conversations Panel")
    def update_pagination_controls(self):
        """Update pagination control states."""
        # Update page info
        self.page_info_label.setText(f"Page {self.current_page} of {self.total_pages}")
        
        # Update total count
        self.total_count_label.setText(f"Total: {self.total_conversations} conversations")
        
        # Update button states
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
    
    @debug_button("load_current_page", "Conversations Panel")
    def load_current_page(self):
        """Load the current page of conversations."""
        try:
            from dreamscape.core.memory_system import get_memory_api
            api = get_memory_api()

            if self.page_size == 0:
                # "All" – fetch every conversation
                conversations = api.get_conversations_chronological(limit=None, offset=0)
                offset = 0
            else:
                offset = (self.current_page - 1) * self.page_size
                conversations = api.get_conversations_chronological(limit=self.page_size, offset=offset)
            
            # Update table
            self.update_conversations_table(conversations)
            
            # Update pagination controls
            self.update_pagination_controls()
            
            # Update status
            if self.page_size == 0:
                self.status_label.setText(f"Showing all {self.total_conversations} conversations")
            else:
                start_item = offset + 1
                end_item = min(offset + self.page_size, self.total_conversations)
                self.status_label.setText(
                    f"Showing conversations {start_item}-{end_item} of {self.total_conversations}")
            
        except Exception as e:
            self.status_label.setText(f"Error loading page: {e}")
    
    @debug_button("load_all_conversations", "Conversations Panel")
    def load_all_conversations(self):
        """Load all conversations with pagination."""
        try:
            # Get total count
            from dreamscape.core.memory_system import get_memory_api
            api = get_memory_api()
            self.total_conversations = api.get_conversations_count()
            
            # Calculate total pages
            self.calculate_total_pages()
            
            # Load first page
            self.current_page = 1
            self.load_current_page()
            
        except Exception as e:
            self.status_label.setText(f"Error loading conversations: {e}") 