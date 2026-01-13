"""Enhanced DevLog Panel – create, save, and post devlog updates with conversation processing integration.

This Qt panel now integrates with the conversation processing system to automatically
generate devlogs from development-focused conversations by sending templates to ChatGPT.
"""

from __future__ import annotations

import asyncio
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QListWidget, QHBoxLayout, QFileDialog, QTabWidget,
    QProgressBar, QComboBox, QCheckBox, QGroupBox, QTextBrowser,
    QSplitter, QFrame
)

from dreamscape.tools.devlog_tool import DevLogTool, DevLogPost
from dreamscape.core.scraping_system import ScraperOrchestrator
from dreamscape.core.memory_manager import MemoryManager
from dreamscape.core.template_engine import render_template

logger = logging.getLogger(__name__)


class DevLogGeneratorWorker(QThread):
    """Worker thread for generating devlogs from conversations."""
    
    progress_updated = pyqtSignal(str)
    conversation_processed = pyqtSignal(dict)
    generation_complete = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, conversations: List[Dict], template_type: str = "development"):
        super().__init__()
        self.conversations = conversations
        self.template_type = template_type
        self.is_running = False
        
    def run(self):
        """Run the devlog generation process."""
        try:
            self.is_running = True
            self.progress_updated.emit("Initializing scraper orchestrator...")
            
            # Initialize scraper orchestrator
            orchestrator = ScraperOrchestrator(
                headless=False,
                use_undetected=True
            )
            
            with orchestrator:
                if not orchestrator.is_initialized:
                    self.error_occurred.emit("Failed to initialize browser")
                    return
                
                self.progress_updated.emit("Browser initialized successfully")
                
                # Process conversations
                generated_devlogs = []
                
                for i, conversation in enumerate(self.conversations):
                    if not self.is_running:
                        break
                        
                    self.progress_updated.emit(f"Processing conversation {i+1}/{len(self.conversations)}: {conversation.get('title', 'Unknown')}")
                    
                    try:
                        # Generate devlog from conversation
                        devlog = self._generate_devlog_from_conversation(orchestrator, conversation)
                        if devlog:
                            generated_devlogs.append(devlog)
                            self.conversation_processed.emit({
                                'conversation': conversation,
                                'devlog': devlog
                            })
                            
                    except Exception as e:
                        logger.error(f"Error processing conversation {conversation.get('title', 'Unknown')}: {e}")
                        continue
                
                self.progress_updated.emit("Devlog generation complete!")
                self.generation_complete.emit(generated_devlogs)
                
        except Exception as e:
            self.error_occurred.emit(f"Devlog generation failed: {e}")
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop the generation process."""
        self.is_running = False
    
    def _generate_devlog_from_conversation(self, orchestrator: ScraperOrchestrator, conversation: Dict) -> Optional[Dict]:
        """Generate a devlog from a single conversation."""
        try:
            # Create development-focused template
            template_content = self._get_development_template(conversation)
            
            # Send template to ChatGPT
            result = orchestrator.send_content_to_chat(
                content=template_content,
                wait_for_response=True,
                create_new_conversation=True
            )
            
            if not result.success:
                logger.warning(f"Failed to send template for conversation: {conversation.get('title', 'Unknown')}")
                return None
            
            # Parse the response into devlog format
            devlog = self._parse_devlog_response(result.response, conversation)
            return devlog
            
        except Exception as e:
            logger.error(f"Error generating devlog from conversation: {e}")
            return None
    
    def _get_development_template(self, conversation: Dict) -> str:
        """Get development-focused template for conversation analysis."""
        
        template = f"""You are an expert development log analyst. Analyze the following conversation and create a comprehensive development log entry.

**CONVERSATION TO ANALYZE:**
Title: {conversation.get('title', 'Unknown')}
URL: {conversation.get('url', 'Unknown')}

Please provide a development log entry in the following format:

**Title:** [Concise title for the development update]
**Description:** [Brief description of what was accomplished]
**Content:** [Detailed analysis including:
- Key technical challenges faced
- Solutions implemented
- Code snippets or technical details (if any)
- Lessons learned
- Next steps or future improvements]
**Tags:** [Comma-separated tags like: development, ai, automation, etc.]
**Challenges:** [List of specific challenges encountered]
**Solutions:** [List of solutions implemented]
**Key Learnings:** [List of important insights gained]

Focus on development-related content, technical details, and actionable insights that would be valuable for a development team or project documentation."""
        
        return template
    
    def _parse_devlog_response(self, response: str, conversation: Dict) -> Dict:
        """Parse ChatGPT response into structured devlog format."""
        try:
            # Extract sections from response
            sections = {
                'title': '',
                'description': '',
                'content': '',
                'tags': [],
                'challenges': [],
                'solutions': [],
                'key_learnings': []
            }
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect sections
                if line.startswith('**Title:**'):
                    current_section = 'title'
                    sections['title'] = line.replace('**Title:**', '').strip()
                elif line.startswith('**Description:**'):
                    current_section = 'description'
                    sections['description'] = line.replace('**Description:**', '').strip()
                elif line.startswith('**Content:**'):
                    current_section = 'content'
                    sections['content'] = line.replace('**Content:**', '').strip()
                elif line.startswith('**Tags:**'):
                    current_section = 'tags'
                    tags_text = line.replace('**Tags:**', '').strip()
                    sections['tags'] = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                elif line.startswith('**Challenges:**'):
                    current_section = 'challenges'
                elif line.startswith('**Solutions:**'):
                    current_section = 'solutions'
                elif line.startswith('**Key Learnings:**'):
                    current_section = 'key_learnings'
                elif line.startswith('-') and current_section in ['challenges', 'solutions', 'key_learnings']:
                    item = line.replace('-', '').strip()
                    if item:
                        sections[current_section].append(item)
                elif current_section == 'content' and line:
                    sections['content'] += '\n' + line
            
            # Create devlog structure
            devlog = {
                'title': sections['title'] or f"Development Update: {conversation.get('title', 'Unknown')}",
                'description': sections['description'] or "Development progress update",
                'content': sections['content'] or response,
                'tags': sections['tags'],
                'challenges': sections['challenges'],
                'solutions': sections['solutions'],
                'key_learnings': sections['key_learnings'],
                'source_conversation': conversation,
                'generated_at': datetime.now().isoformat(),
                'template_type': self.template_type
            }
            
            return devlog
            
        except Exception as e:
            logger.error(f"Error parsing devlog response: {e}")
            # Fallback to basic structure
            return {
                'title': f"Development Update: {conversation.get('title', 'Unknown')}",
                'description': "Development progress update",
                'content': response,
                'tags': ['development', 'auto-generated'],
                'challenges': [],
                'solutions': [],
                'key_learnings': [],
                'source_conversation': conversation,
                'generated_at': datetime.now().isoformat(),
                'template_type': self.template_type
            }


class DevLogPanel(QWidget):
    """Enhanced Qt panel for devlog authoring, Discord posting, and conversation-based generation."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.tool = DevLogTool()
        self.memory_manager = MemoryManager()
        self.generator_worker = None
        self._build_ui()
        self._refresh_list()

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        root.addWidget(self.tab_widget)
        
        # Manual DevLog Tab
        self._create_manual_devlog_tab()
        
        # Auto-Generation Tab
        self._create_auto_generation_tab()
        
        # Generated DevLogs Tab
        self._create_generated_devlogs_tab()

    def _create_manual_devlog_tab(self):
        """Create the manual devlog creation tab."""
        manual_widget = QWidget()
        layout = QVBoxLayout(manual_widget)
        
        # Title
        title_lbl = QLabel("📝 Manual DevLog Creation")
        title_lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_lbl)
        
        # Form fields
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Title")
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Short description")
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (comma-separated)")
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Main update details …")
        self.content_edit.setMinimumHeight(140)

        layout.addWidget(self.title_edit)
        layout.addWidget(self.desc_edit)
        layout.addWidget(self.tags_edit)
        layout.addWidget(self.content_edit)

        # Action buttons
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Locally")
        self.post_btn = QPushButton("🚀 Post to Discord")
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.post_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        # Connect signals
        self.save_btn.clicked.connect(lambda: self._handle_submit(post_to_discord=False))
        self.post_btn.clicked.connect(lambda: self._handle_submit(post_to_discord=True))

        # Recent devlogs list
        self.list_widget = QListWidget()
        layout.addWidget(QLabel("Recent DevLogs:"))
        layout.addWidget(self.list_widget, 1)
        self.list_widget.itemDoubleClicked.connect(self._open_selected_file)
        
        self.tab_widget.addTab(manual_widget, "📝 Manual Creation")

    def _create_auto_generation_tab(self):
        """Create the auto-generation tab."""
        auto_widget = QWidget()
        layout = QVBoxLayout(auto_widget)
        
        # Title
        title_lbl = QLabel("🤖 Auto-Generate DevLogs from Conversations")
        title_lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_lbl)
        
        # Configuration group
        config_group = QGroupBox("Generation Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Template type selection
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template Type:"))
        self.template_type_combo = QComboBox()
        self.template_type_combo.addItems([
            "Development",
            "Technical Analysis", 
            "Project Update",
            "Code Review",
            "Architecture Discussion"
        ])
        template_layout.addWidget(self.template_type_combo)
        template_layout.addStretch()
        config_layout.addLayout(template_layout)
        
        # Conversation selection
        conv_layout = QHBoxLayout()
        conv_layout.addWidget(QLabel("Conversation Filter:"))
        self.conv_filter_combo = QComboBox()
        self.conv_filter_combo.addItems([
            "All Conversations",
            "Development Focused",
            "Recent (Last 7 days)",
            "Recent (Last 30 days)",
            "High Message Count (>50)",
            "Contains Code"
        ])
        conv_layout.addWidget(self.conv_filter_combo)
        conv_layout.addStretch()
        config_layout.addLayout(conv_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.auto_post_checkbox = QCheckBox("Auto-post to Discord")
        self.auto_post_checkbox.setChecked(False)
        self.save_generated_checkbox = QCheckBox("Save generated devlogs")
        self.save_generated_checkbox.setChecked(True)
        options_layout.addWidget(self.auto_post_checkbox)
        options_layout.addWidget(self.save_generated_checkbox)
        options_layout.addStretch()
        config_layout.addLayout(options_layout)
        
        layout.addWidget(config_group)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("🚀 Generate DevLogs")
        self.stop_btn = QPushButton("⏹️ Stop Generation")
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status display
        self.status_display = QTextBrowser()
        self.status_display.setMaximumHeight(150)
        layout.addWidget(QLabel("Generation Status:"))
        layout.addWidget(self.status_display)
        
        # Connect signals
        self.generate_btn.clicked.connect(self._start_generation)
        self.stop_btn.clicked.connect(self._stop_generation)
        
        self.tab_widget.addTab(auto_widget, "🤖 Auto-Generation")

    def _create_generated_devlogs_tab(self):
        """Create the generated devlogs tab."""
        generated_widget = QWidget()
        layout = QVBoxLayout(generated_widget)
        
        # Title
        title_lbl = QLabel("📋 Generated DevLogs")
        title_lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_lbl)
        
        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Generated devlogs list
        self.generated_list = QListWidget()
        self.generated_list.itemClicked.connect(self._preview_generated_devlog)
        splitter.addWidget(self.generated_list)
        
        # Preview area
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_layout.addWidget(QLabel("DevLog Preview:"))
        self.preview_display = QTextBrowser()
        preview_layout.addWidget(self.preview_display)
        
        # Preview actions
        preview_btn_layout = QHBoxLayout()
        self.edit_generated_btn = QPushButton("✏️ Edit")
        self.save_generated_btn = QPushButton("💾 Save")
        self.post_generated_btn = QPushButton("🚀 Post to Discord")
        preview_btn_layout.addWidget(self.edit_generated_btn)
        preview_btn_layout.addWidget(self.save_generated_btn)
        preview_btn_layout.addWidget(self.post_generated_btn)
        preview_btn_layout.addStretch()
        preview_layout.addLayout(preview_btn_layout)
        
        splitter.addWidget(preview_frame)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        # Connect signals
        self.edit_generated_btn.clicked.connect(self._edit_generated_devlog)
        self.save_generated_btn.clicked.connect(self._save_generated_devlog)
        self.post_generated_btn.clicked.connect(self._post_generated_devlog)
        
        self.tab_widget.addTab(generated_widget, "📋 Generated")

    # ------------------------------------------------------------
    # Auto-Generation Methods
    # ------------------------------------------------------------
    def _start_generation(self):
        """Start the devlog generation process."""
        try:
            # Get conversations based on filter
            conversations = self._get_filtered_conversations()
            
            if not conversations:
                QMessageBox.warning(self, "No Conversations", "No conversations found matching the selected filter.")
                return
            
            # Get template type
            template_type = self.template_type_combo.currentText().lower().replace(' ', '_')
            
            # Create and start worker
            self.generator_worker = DevLogGeneratorWorker(conversations, template_type)
            self.generator_worker.progress_updated.connect(self._update_generation_progress)
            self.generator_worker.conversation_processed.connect(self._on_conversation_processed)
            self.generator_worker.generation_complete.connect(self._on_generation_complete)
            self.generator_worker.error_occurred.connect(self._on_generation_error)
            
            # Update UI
            self.generate_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(conversations))
            self.progress_bar.setValue(0)
            self.status_display.clear()
            self.status_display.append("Starting devlog generation...")
            
            # Start worker
            self.generator_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"Failed to start generation: {e}")
    
    def _stop_generation(self):
        """Stop the devlog generation process."""
        if self.generator_worker and self.generator_worker.isRunning():
            self.generator_worker.stop()
            self.generator_worker.wait()
        
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_display.append("Generation stopped by user.")
    
    def _get_filtered_conversations(self) -> List[Dict]:
        """Get conversations based on the selected filter."""
        try:
            all_conversations = self.memory_manager.get_conversations()
            
            filter_type = self.conv_filter_combo.currentText()
            
            if filter_type == "All Conversations":
                return all_conversations
            elif filter_type == "Development Focused":
                # Filter for development-related conversations
                dev_keywords = ['development', 'code', 'programming', 'software', 'api', 'database', 'system', 'architecture']
                return [
                    conv for conv in all_conversations
                    if any(keyword in conv.get('title', '').lower() or keyword in conv.get('content', '').lower() 
                           for keyword in dev_keywords)
                ]
            elif filter_type == "Recent (Last 7 days)":
                # Filter for recent conversations (simplified)
                return all_conversations[:10]  # Assume first 10 are recent
            elif filter_type == "Recent (Last 30 days)":
                return all_conversations[:30]  # Assume first 30 are recent
            elif filter_type == "High Message Count (>50)":
                # Filter for conversations with many messages
                return [
                    conv for conv in all_conversations
                    if conv.get('message_count', 0) > 50
                ]
            elif filter_type == "Contains Code":
                # Filter for conversations that likely contain code
                code_keywords = ['function', 'class', 'import', 'def ', 'const ', 'var ', 'let ', 'if ', 'for ', 'while ']
                return [
                    conv for conv in all_conversations
                    if any(keyword in conv.get('content', '').lower() for keyword in code_keywords)
                ]
            
            return all_conversations
            
        except Exception as e:
            logger.error(f"Error filtering conversations: {e}")
            return []
    
    def _update_generation_progress(self, message: str):
        """Update the generation progress display."""
        self.status_display.append(message)
        self.progress_bar.setValue(self.progress_bar.value() + 1)
    
    def _on_conversation_processed(self, data: Dict):
        """Handle when a conversation is processed."""
        conversation = data['conversation']
        devlog = data['devlog']
        
        self.status_display.append(f"✅ Generated devlog: {devlog['title']}")
        
        # Add to generated list
        self.generated_list.addItem(devlog['title'])
        
        # Save if enabled
        if self.save_generated_checkbox.isChecked():
            self._save_generated_devlog_to_file(devlog)
    
    def _on_generation_complete(self, devlogs: List[Dict]):
        """Handle when generation is complete."""
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.status_display.append(f"🎉 Generation complete! Generated {len(devlogs)} devlogs.")
        
        # Auto-post if enabled
        if self.auto_post_checkbox.isChecked():
            self._auto_post_devlogs(devlogs)
    
    def _on_generation_error(self, error: str):
        """Handle generation errors."""
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.status_display.append(f"❌ Error: {error}")
        QMessageBox.critical(self, "Generation Error", error)

    # ------------------------------------------------------------
    # Generated DevLog Methods
    # ------------------------------------------------------------
    def _preview_generated_devlog(self):
        """Preview the selected generated devlog."""
        # Implementation for previewing generated devlogs
        pass
    
    def _edit_generated_devlog(self):
        """Edit the selected generated devlog."""
        # Implementation for editing generated devlogs
        pass
    
    def _save_generated_devlog(self):
        """Save the selected generated devlog."""
        # Implementation for saving generated devlogs
        pass
    
    def _post_generated_devlog(self):
        """Post the selected generated devlog to Discord."""
        # Implementation for posting generated devlogs
        pass
    
    def _save_generated_devlog_to_file(self, devlog: Dict):
        """Save a generated devlog to file."""
        try:
            # Create output directory
            output_dir = Path("outputs/generated_devlogs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in devlog['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{timestamp}_{safe_title[:50]}.json"
            
            # Save devlog
            filepath = output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(devlog, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved generated devlog to: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving generated devlog: {e}")
    
    def _auto_post_devlogs(self, devlogs: List[Dict]):
        """Automatically post devlogs to Discord."""
        # Implementation for auto-posting devlogs
        pass

    # ------------------------------------------------------------
    # Manual DevLog Methods (existing)
    # ------------------------------------------------------------
    def _collect_tags(self) -> List[str]:
        text = self.tags_edit.text().strip()
        return [t.strip() for t in text.split(",") if t.strip()] if text else []

    def _handle_submit(self, post_to_discord: bool):
        title = self.title_edit.text().strip()
        desc = self.desc_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        if not (title and desc and content):
            QMessageBox.warning(self, "Validation", "Title, description, and content are required.")
            return

        post = self.tool.create_devlog(
            title=title,
            description=desc,
            content=content,
            tags=self._collect_tags(),
        )

        md_path = self.tool.save_local(post)

        ok = True
        if post_to_discord:
            embed = self.tool._build_embed(post)
            formatted = self.tool.format_for_discord(post)
            try:
                ok = asyncio.run(self.tool.post_to_discord(formatted, embed_data=embed))
            except RuntimeError:
                # running inside existing loop – fallback
                loop = asyncio.get_event_loop()
                ok = loop.create_task(self.tool.post_to_discord(formatted, embed_data=embed))
            except Exception as e:
                ok = False
                QMessageBox.critical(self, "Discord Error", str(e))

        self._refresh_list()
        self._reset_fields()
        msg = "DevLog saved and posted!" if (post_to_discord and ok) else "DevLog saved!"
        QMessageBox.information(self, "Success", msg + f"\nSaved to: {md_path}")

    def _reset_fields(self):
        self.title_edit.clear()
        self.desc_edit.clear()
        self.tags_edit.clear()
        self.content_edit.clear()

    def _refresh_list(self):
        self.list_widget.clear()
        for md_file in sorted(self.tool.output_dir.glob("*.md"), reverse=True):
            self.list_widget.addItem(md_file.name)

    def _open_selected_file(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        path = self.tool.output_dir / item.text()
        if not path.exists():
            QMessageBox.warning(self, "File Missing", "Cannot locate file on disk.")
            self._refresh_list()
            return
        # Ask the user where to open; fallback to default system opener
        QFileDialog.getOpenFileName(self, "Open DevLog", str(path), "Markdown (*.md)") 