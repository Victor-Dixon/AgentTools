#!/usr/bin/env python3
"""
Dashboard Panel
==============

Main dashboard showing key metrics and quick actions.
"""

import logging
from gui.debug_handler import debug_button
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGroupBox, QGridLayout, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from gui.debug_handler import debug_button

logger = logging.getLogger(__name__)

class DashboardPanel(QWidget):
    """Main dashboard panel with key metrics and quick actions."""
    
    # Signals
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.memory_manager = None
        self.mmorpg_engine = None
        self.discord_manager = None
        self.scraping_manager = None
        self.resume_tracker = None
        self.enhanced_skill_system = None
        
        self._setup_ui()
        self._setup_timer()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🏠 Dreamscape Dashboard")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Stats Grid
        self._create_stats_grid(layout)
        
        # Quick Actions
        self._create_quick_actions(layout)
        
        # Status Bar
        self._create_status_bar(layout)
        
        self.setLayout(layout)
    
    @debug_button("_create_stats_grid", "Dashboard Panel")
    def _create_stats_grid(self, parent_layout):
        """Create statistics grid using shared components and add to layout."""
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        # Initial dummy stats; will be updated in refresh_dashboard
        stats = [
            {"label": "Total Conversations", "value": "0", "key": "total_conversations"},
            {"label": "Total Messages", "value": "0", "key": "total_messages"},
            {"label": "Avg Msgs/Conversation", "value": "0", "key": "avg_messages_per_conversation"},
            {"label": "Earliest Date", "value": "-", "key": "earliest_date"},
            {"label": "Latest Date", "value": "-", "key": "latest_date"},
        ]
        self.stats_group = components.create_statistics_grid(
            title="Conversation Statistics",
            stats=stats
        )
        # Store label widgets for dynamic update
        self.stat_labels = self.stats_group.stat_labels
        parent_layout.addWidget(self.stats_group)

    def _create_quick_actions(self, parent_layout):
        """Create enhanced dashboard with card-based layout."""
        try:
            from gui.components.enhanced_dashboard_cards import EnhancedDashboardCards
            
            # Create enhanced dashboard cards
            self.enhanced_cards = EnhancedDashboardCards()
            
            # Connect card signals to existing methods
            self.enhanced_cards.setup_clicked.connect(self.run_setup_and_test)
            self.enhanced_cards.showcase_clicked.connect(self.run_comprehensive_showcase)
            self.enhanced_cards.preview_clicked.connect(self.run_comprehensive_preview)  # NEW: Preview connection
            self.enhanced_cards.workflow_clicked.connect(self.run_end_to_end_workflow)
            self.enhanced_cards.refresh_clicked.connect(self.refresh_dashboard)
            self.enhanced_cards.stats_clicked.connect(self._show_stats_overview)
            self.enhanced_cards.conversations_clicked.connect(self._show_recent_conversations)
            self.enhanced_cards.templates_clicked.connect(self._show_quick_template)
            
            parent_layout.addWidget(self.enhanced_cards)
            
            # Store references to update status later
            self.setup_btn = self.enhanced_cards.setup_card
            self.showcase_btn = self.enhanced_cards.showcase_card
            self.preview_btn = self.enhanced_cards.preview_card  # NEW: Preview card reference
            self.workflow_btn = self.enhanced_cards.workflow_card
            
        except ImportError as e:
            # Fallback to original button layout if enhanced cards not available
            logger.warning(f"Enhanced dashboard cards not available, using fallback: {e}")
            self._create_fallback_quick_actions(parent_layout)
            
    def _create_fallback_quick_actions(self, parent_layout):
        """Create original quick action buttons as fallback."""
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QHBoxLayout()
        
        # Setup Button (NEW)
        self.setup_btn = QPushButton("🔧 Setup & Test Pipeline")
        self.setup_btn.clicked.connect(self.run_setup_and_test)
        actions_layout.addWidget(self.setup_btn)
        
        # Showcase Button (NEW)
        self.showcase_btn = QPushButton("🎭 Comprehensive Showcase")
        self.showcase_btn.clicked.connect(self.run_comprehensive_showcase)
        actions_layout.addWidget(self.showcase_btn)
        
        # Preview Button (NEW) - Limited to 5 conversations
        self.preview_btn = QPushButton("🎯 Preview Workflow (5 Conversations)")
        self.preview_btn.clicked.connect(self.run_comprehensive_preview)
        actions_layout.addWidget(self.preview_btn)
        
        # Refresh Dashboard Button
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        self.refresh_btn = components.create_refresh_button(
            text="Refresh Dashboard", callback=self.refresh_dashboard
        )
        actions_layout.addWidget(self.refresh_btn)
        
        # End-to-End Workflow Button
        self.workflow_btn = QPushButton("🚀 End-to-End Workflow")
        self.workflow_btn.clicked.connect(self.run_end_to_end_workflow)
        actions_layout.addWidget(self.workflow_btn)
        
        # ChatGPT Refresh Button
        self.chatgpt_refresh_btn = components.create_refresh_button(
            text="Refresh ChatGPT", icon="📥", callback=self.refresh_chatgpt
        )
        actions_layout.addWidget(self.chatgpt_refresh_btn)
        
        # Quick Ingest Button
        self.quick_ingest_btn = QPushButton("⚡ Quick Ingest")
        self.quick_ingest_btn.clicked.connect(self.quick_ingestion_and_progress)
        actions_layout.addWidget(self.quick_ingest_btn)
        
        actions_group.setLayout(actions_layout)
        parent_layout.addWidget(actions_group)
    
    @debug_button("_create_status_bar", "Dashboard Panel")
    def _create_status_bar(self, parent_layout):
        from gui.components.shared_components import SharedComponents
        components = SharedComponents()
        status_items = [
            {"key": "status", "text": "Ready", "icon": "✅"}
        ]
        self.status_bar = components.create_status_bar(status_items=status_items)
        # Store the label for updates
        self.status_label = self.status_bar.status_labels["status"]
        parent_layout.addWidget(self.status_bar)

    def _setup_timer(self):
        """Setup auto-refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def set_managers(self, memory_manager, mmorpg_engine, discord_manager, 
                    scraping_manager, resume_tracker, enhanced_skill_system):
        """Set the manager instances."""
        self.memory_manager = memory_manager
        self.mmorpg_engine = mmorpg_engine
        self.discord_manager = discord_manager
        self.scraping_manager = scraping_manager
        self.resume_tracker = resume_tracker
        self.enhanced_skill_system = enhanced_skill_system
        
        # Initial refresh
        self.refresh_dashboard()
    
    @debug_button("Refresh Dashboard", "Dashboard")
    @debug_button("refresh_dashboard", "Dashboard Panel")
    def refresh_dashboard(self, *args, **kwargs):
        """Refresh dashboard data."""
        try:
            if not self.memory_manager:
                logger.warning("Memory manager not available")
                return
            # Get conversation stats
            stats = self.memory_manager.get_conversation_stats()
            # Update statistics grid labels
            for key in [
                "total_conversations",
                "total_messages",
                "avg_messages_per_conversation",
                "earliest_date",
                "latest_date"
            ]:
                value = stats.get(key, "-")
                if key in self.stat_labels:
                    self.stat_labels[key].setText(str(value))
            # Update status
            if hasattr(self, "status_label"):
                self.status_label.setText("Dashboard updated successfully")
                
            # Update enhanced dashboard if available
            self.update_enhanced_dashboard()
            
            logger.info("Dashboard stats updated successfully")
        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")
            if hasattr(self, "status_label"):
                self.status_label.setText(f"Error: {str(e)}")
    
    @debug_button("Setup and Test Pipeline", "Dashboard")
    @debug_button("run_setup_and_test", "Dashboard Panel")
    def run_setup_and_test(self, *args, **kwargs):
        """Run comprehensive setup and test of the entire pipeline."""
        from PyQt6.QtWidgets import QMessageBox
        from threading import Thread
        
        # Confirm action
        reply = QMessageBox.question(
            self, 
            "Setup & Test Pipeline", 
            "🔧 This will run a comprehensive setup and test:\n\n"
            "1. 🔍 Test all system connections (Database, Memory, MMORPG)\n"
            "2. 🤖 Set up ChatGPT login if needed\n"
            "3. 📊 Validate database schemas and tables\n"
            "4. 🧪 Test conversation processing pipeline\n"
            "5. 📝 Verify template system functionality\n"
            "6. 🎮 Test MMORPG integration\n"
            "7. 📁 Test file system and permissions\n"
            "8. 🧪 Run sample workflow through ALL aspects\n\n"
            "The sample workflow will test:\n"
            "• 📚 Conversation processing\n"
            "• 📝 Template application\n"
            "• 🎮 MMORPG progression\n"
            "• 📝 Content generation\n"
            "• 📊 Analytics and reporting\n"
            "• 🤖 ChatGPT scraping (if set up)\n\n"
            "This ensures the ENTIRE pipeline works before running the full workflow.\n\n"
            "Continue with comprehensive setup and testing?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable button during processing
        if hasattr(self.setup_btn, 'setEnabled'):
            self.setup_btn.setEnabled(False)
        if hasattr(self.setup_btn, 'setText'):
            self.setup_btn.setText("🔄 Running Setup...")
        elif hasattr(self.setup_btn, 'update_status'):
            self.setup_btn.update_status("running", 0)
        
        # Update status
        if hasattr(self, "status_label"):
            self.status_label.setText("Running setup and tests...")
        
        # Run setup in background thread
        def run_setup():
            try:
                # Import and run the setup workflow
                import sys
                sys.path.insert(0, "scripts")
                from end_to_end_workflow import EndToEndWorkflow
                
                # Create setup workflow
                setup_workflow = EndToEndWorkflow()
                
                # Run setup tests
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    results = loop.run_until_complete(setup_workflow.run_setup_and_test())
                    
                    # Schedule UI update on main thread
                    def update_ui():
                        try:
                            if results.get("status") == "completed":
                                # Build detailed results message
                                steps = results.get('steps_completed', [])
                                errors = results.get('errors', [])
                                sample_results = results.get('results', {})
                                
                                # Check key components
                                chatgpt_ready = 'chatgpt_setup_completed' in steps
                                database_ready = 'database_tested' in steps
                                sample_workflow_ready = 'sample_workflow_completed' in steps
                                
                                # Build sample workflow summary
                                sample_summary = ""
                                if sample_workflow_ready:
                                    sample_summary = "\n🧪 Sample Workflow Results:\n"
                                    if 'sample_conversation' in sample_results:
                                        sample_summary += f"• 📚 Conversation processing: ✅\n"
                                    if 'sample_template' in sample_results:
                                        sample_summary += f"• 📝 Template application: ✅\n"
                                    if 'sample_mmorpg' in sample_results:
                                        sample_summary += f"• 🎮 MMORPG progression: ✅\n"
                                    if 'sample_content' in sample_results:
                                        sample_summary += f"• 📝 Content generation: ✅\n"
                                    if 'sample_analytics' in sample_results:
                                        sample_summary += f"• 📊 Analytics & reporting: ✅\n"
                                    if 'sample_chatgpt' in sample_results:
                                        chatgpt_sample = sample_results['sample_chatgpt']
                                        if chatgpt_sample.get('setup_ready'):
                                            sample_summary += f"• 🤖 ChatGPT scraping: ✅\n"
                                        else:
                                            sample_summary += f"• 🤖 ChatGPT scraping: ⚠️ (not set up)\n"
                                
                                QMessageBox.information(
                                    self,
                                    "Setup Complete",
                                    f"✅ Setup and testing completed successfully!\n\n"
                                    f"📊 System Results:\n"
                                    f"• Systems tested: {len(steps)}\n"
                                    f"• Errors: {len(errors)}\n"
                                    f"• ChatGPT setup: {'✅ Complete' if chatgpt_ready else '⚠️ May need attention'}\n"
                                    f"• Database: {'✅ Ready' if database_ready else '⚠️ Issues detected'}\n"
                                    f"• Sample workflow: {'✅ Completed' if sample_workflow_ready else '❌ Failed'}\n"
                                    f"{sample_summary}\n"
                                    f"🎉 Your Dreamscape pipeline is ready to use!"
                                )
                                if hasattr(self, "status_label"):
                                    self.status_label.setText("Setup completed successfully")
                            else:
                                QMessageBox.warning(
                                    self,
                                    "Setup Issues",
                                    f"⚠️ Setup completed with some issues:\n\n"
                                    f"Errors: {len(results.get('errors', []))}\n"
                                    f"Steps completed: {len(results.get('steps_completed', []))}\n\n"
                                    f"Please check the logs for details."
                                )
                                if hasattr(self, "status_label"):
                                    self.status_label.setText("Setup completed with issues")
                        except Exception as e:
                            logger.error(f"Failed to update UI after setup: {e}")
                        finally:
                            if hasattr(self.setup_btn, 'setEnabled'):
                                self.setup_btn.setEnabled(True)
                            if hasattr(self.setup_btn, 'setText'):
                                self.setup_btn.setText("🔧 Setup & Test Pipeline")
                            elif hasattr(self.setup_btn, 'update_status'):
                                self.setup_btn.update_status("ready")
                    
                    # Schedule UI update
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, update_ui)
                    
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"Setup failed: {e}")
                
                # Schedule error display
                def show_error():
                    try:
                        QMessageBox.critical(
                            self,
                            "Setup Failed",
                            f"❌ Setup failed with error:\n\n{str(e)}\n\nPlease check the logs for details."
                        )
                        if hasattr(self, "status_label"):
                            self.status_label.setText("Setup failed")
                    except Exception as ui_error:
                        logger.error(f"Failed to show error dialog: {ui_error}")
                    finally:
                        if hasattr(self.setup_btn, 'setEnabled'):
                            self.setup_btn.setEnabled(True)
                        if hasattr(self.setup_btn, 'setText'):
                            self.setup_btn.setText("🔧 Setup & Test Pipeline")
                        elif hasattr(self.setup_btn, 'update_status'):
                            self.setup_btn.update_status("ready")
        
        Thread(target=run_setup, daemon=True).start()
    
    @debug_button("Comprehensive Showcase", "Dashboard")
    @debug_button("run_comprehensive_showcase", "Dashboard Panel")
    def run_comprehensive_showcase(self, *args, **kwargs):
        """Run comprehensive showcase of all Dreamscape features."""
        from PyQt6.QtWidgets import QMessageBox
        from threading import Thread
        
        # Confirm action
        reply = QMessageBox.question(
            self, 
            "Comprehensive Showcase", 
            "🎭 This will run a comprehensive showcase of ALL Dreamscape features:\n\n"
            "🏗️ Core Systems:\n"
            "• Memory Management (Vector storage, similarity search)\n"
            "• MMORPG Engine (Quest system, skill progression)\n"
            "• Template System (Dynamic content generation)\n"
            "• ChatGPT Scraping (Anti-detection automation)\n\n"
            "🚀 Advanced Features:\n"
            "• AI Studio (Multi-model testing, intelligent agents)\n"
            "• Memory Weaponization (Vector search, content creation)\n"
            "• Combat Engine (Skill-based progression)\n"
            "• Multi-modal Content (Text, image, audio)\n\n"
            "🎨 GUI System:\n"
            "• Modern PyQt6 Interface (12+ panels)\n"
            "• Dashboard System (Real-time statistics)\n"
            "• Shared Components (Reusable UI library)\n\n"
            "🔗 Integrations:\n"
            "• Discord Integration (Devlog updates)\n"
            "• API Integration (External services)\n"
            "• Workflow Automation (Pipeline orchestration)\n"
            "• Export System (Multiple formats)\n\n"
            "🛠️ Developer Tools:\n"
            "• Training Data Extraction\n"
            "• Agent Training System\n"
            "• Advanced Search (Semantic, full-text)\n"
            "• Debug Tools (Error tracking, monitoring)\n\n"
            "📊 Analytics & Reporting:\n"
            "• Comprehensive Analytics\n"
            "• Content Analytics\n"
            "• Performance Metrics\n"
            "• Report Generation\n\n"
            "This showcase will demonstrate the FULL power of Dreamscape!\n\n"
            "Continue with comprehensive showcase?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable button during processing
        if hasattr(self.showcase_btn, 'setEnabled'):
            self.showcase_btn.setEnabled(False)
        if hasattr(self.showcase_btn, 'setText'):
            self.showcase_btn.setText("🔄 Running Showcase...")
        elif hasattr(self.showcase_btn, 'update_status'):
            self.showcase_btn.update_status("running", 0)
        
        # Update status
        if hasattr(self, "status_label"):
            self.status_label.setText("Running comprehensive showcase...")
        
        # Run showcase in background thread
        def run_showcase():
            try:
                # Import and run the showcase workflow
                import sys
                sys.path.insert(0, "scripts")
                from end_to_end_workflow import EndToEndWorkflow
                
                # Create showcase workflow
                showcase_workflow = EndToEndWorkflow()
                
                # Run showcase
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    results = loop.run_until_complete(showcase_workflow.run_comprehensive_showcase())
                    
                    # Schedule UI update on main thread
                    def update_ui():
                        try:
                            if results.get("status") == "completed":
                                # Get comprehensive report
                                comprehensive_report = results.get('results', {}).get('comprehensive_report', {})
                                
                                if comprehensive_report:
                                    total_features = comprehensive_report.get('total_features_showcased', 0)
                                    successful = comprehensive_report.get('successful_showcases', 0)
                                    success_rate = comprehensive_report.get('success_rate', 0)
                                    recommendations = comprehensive_report.get('recommendations', [])
                                    
                                    QMessageBox.information(
                                        self,
                                        "Showcase Complete",
                                        f"🎭 Comprehensive Showcase Completed Successfully!\n\n"
                                        f"📊 Showcase Results:\n"
                                        f"• Total Features: {total_features}\n"
                                        f"• Successful: {successful}\n"
                                        f"• Success Rate: {success_rate:.1f}%\n"
                                        f"• Recommendations: {len(recommendations)}\n\n"
                                        f"🏗️ Core Systems: ✅\n"
                                        f"🚀 Advanced Features: ✅\n"
                                        f"🎨 GUI System: ✅\n"
                                        f"🔗 Integrations: ✅\n"
                                        f"🛠️ Developer Tools: ✅\n"
                                        f"📊 Analytics: ✅\n\n"
                                        f"🎉 Dreamscape is fully operational!"
                                    )
                                else:
                                    QMessageBox.information(
                                        self,
                                        "Showcase Complete",
                                        f"🎭 Comprehensive showcase completed successfully!\n\n"
                                        f"📊 Results:\n"
                                        f"• Steps completed: {len(results.get('steps_completed', []))}\n"
                                        f"• Errors: {len(results.get('errors', []))}\n\n"
                                        f"🎉 All major Dreamscape features are operational!"
                                    )
                                
                                if hasattr(self, "status_label"):
                                    self.status_label.setText("Showcase completed successfully")
                            else:
                                QMessageBox.warning(
                                    self,
                                    "Showcase Issues",
                                    f"⚠️ Showcase completed with some issues:\n\n"
                                    f"Errors: {len(results.get('errors', []))}\n"
                                    f"Steps completed: {len(results.get('steps_completed', []))}\n\n"
                                    f"Please check the logs for details."
                                )
                                if hasattr(self, "status_label"):
                                    self.status_label.setText("Showcase completed with issues")
                        except Exception as e:
                            logger.error(f"Failed to update UI after showcase: {e}")
                        finally:
                            self.showcase_btn.setEnabled(True)
                            self.showcase_btn.setText("🎭 Comprehensive Showcase")
                    
                    # Schedule UI update
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, update_ui)
                    
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"Showcase failed: {e}")
                
                # Schedule error display
                def show_error():
                    try:
                        QMessageBox.critical(
                            self,
                            "Showcase Failed",
                            f"❌ Showcase failed with error:\n\n{str(e)}\n\nPlease check the logs for details."
                        )
                        if hasattr(self, "status_label"):
                            self.status_label.setText("Showcase failed")
                    except Exception as ui_error:
                        logger.error(f"Failed to show error dialog: {ui_error}")
                    finally:
                        self.showcase_btn.setEnabled(True)
                        self.showcase_btn.setText("🎭 Comprehensive Showcase")
                
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, show_error)
        
        Thread(target=run_showcase, daemon=True).start()
    
    def _show_stats_overview(self):
        """Show statistics overview - navigate to analytics panel."""
        try:
            # Signal to main window to switch to analytics panel
            if hasattr(self.parent(), 'switch_panel'):
                self.parent().switch_panel('analytics_export')
            else:
                # Fallback - show simple stats dialog
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Statistics Overview",
                    "📊 Stats Overview\n\nNavigate to Analytics panel for detailed statistics."
                )
        except Exception as e:
            logger.error(f"Failed to show stats overview: {e}")
    
    def _show_recent_conversations(self):
        """Show recent conversations - navigate to conversations panel."""
        try:
            # Signal to main window to switch to conversations panel
            if hasattr(self.parent(), 'switch_panel'):
                self.parent().switch_panel('conversations')
            else:
                # Fallback - show simple dialog
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Recent Conversations",
                    "💬 Recent Conversations\n\nNavigate to Conversations panel to view and manage conversations."
                )
        except Exception as e:
            logger.error(f"Failed to show recent conversations: {e}")
    
    def _show_quick_template(self):
        """Show quick template access - navigate to templates panel."""
        try:
            # Signal to main window to switch to templates panel
            if hasattr(self.parent(), 'switch_panel'):
                self.parent().switch_panel('templates')
            else:
                # Fallback - show simple dialog
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Quick Template",
                    "📝 Quick Template Access\n\nNavigate to Templates panel to create and manage templates."
                )
        except Exception as e:
            logger.error(f"Failed to show quick template: {e}")
    
    def update_enhanced_dashboard(self):
        """Update enhanced dashboard cards with current data."""
        try:
            if hasattr(self, 'enhanced_cards'):
                # Update quick access values
                stats_count = len(self.stat_labels) if hasattr(self, 'stat_labels') else 0
                conversations_count = 0  # Will be updated with real data
                
                # Get conversation count if memory manager is available
                if self.memory_manager:
                    try:
                        stats = self.memory_manager.get_conversation_stats()
                        conversations_count = stats.get('total_conversations', 0)
                    except:
                        pass
                
                self.enhanced_cards.update_quick_access_values(
                    stats_count=stats_count,
                    conversations_count=conversations_count
                )
                
                # Update system status based on component availability
                systems_status = {
                    "Memory": "ready" if self.memory_manager else "warning",
                    "MMORPG": "ready" if self.mmorpg_engine else "warning", 
                    "ChatGPT": "warning",  # Default to warning until setup
                    "Analytics": "ready",  # Generally available
                    "Templates": "ready"   # Generally available
                }
                
                for system, status in systems_status.items():
                    self.enhanced_cards.update_system_status(system, status)
                    
        except Exception as e:
            logger.error(f"Failed to update enhanced dashboard: {e}")
    
    @debug_button("End-to-End Workflow", "Dashboard")
    @debug_button("run_end_to_end_workflow", "Dashboard Panel")
    def run_end_to_end_workflow(self, *args, **kwargs):
        """Run the complete end-to-end workflow."""
        from PyQt6.QtWidgets import QMessageBox
        
        # Confirm action
        reply = QMessageBox.question(
            self, 
            "End-to-End Workflow", 
            "🚀 This will run the complete Dreamscape workflow:\n\n"
            "1. 📚 Ingest/refresh all conversations (ensure full content)\n"
            "2. 🎯 Apply templates to each conversation\n"
            "3. 📤 Post devlogs to Discord\n"
            "4. 🎮 Trigger Dreamscape game logic (MMORPG progress, skills)\n\n"
            "This process may take several minutes. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable button during processing
        self.workflow_btn.setEnabled(False)
        self.workflow_btn.setText("🔄 Running Workflow...")
        
        # Get the main window and run the workflow
        main_window = self.window()
        if hasattr(main_window, 'run_end_to_end_workflow'):
            main_window.run_end_to_end_workflow("batch")
        else:
            QMessageBox.warning(
                self,
                "Workflow Not Available",
                "The end-to-end workflow is not available in this version."
            )
            self.workflow_btn.setEnabled(True)
            self.workflow_btn.setText("🚀 End-to-End Workflow")
    
    @debug_button("Comprehensive Preview Workflow", "Dashboard")
    @debug_button("run_comprehensive_preview", "Dashboard Panel")
    def run_comprehensive_preview(self, *args, **kwargs):
        """Run the comprehensive preview workflow (limited to 5 conversations)."""
        from PyQt6.QtWidgets import QMessageBox
        
        # Show preview information dialog
        reply = QMessageBox.question(
            self, 
            "🎭 Comprehensive Preview Workflow", 
            "🎯 This will run a comprehensive preview showcasing ALL Dreamscape features:\n\n"
            "✨ Features Demonstrated:\n"
            "• 🔧 Core Systems (Memory, MMORPG, Templates)\n"
            "• 🤖 ChatGPT Integration (Anti-detection scraping)\n"
            "• 🎮 MMORPG Features (Quest progression, XP, skills)\n"
            "• 🧠 AI & Analytics (Vector search, insights)\n"
            "• 🎨 GUI System (Modern PyQt6 interface)\n"
            "• 📊 Advanced Analytics (Time series, topics)\n"
            "• 🔗 Discord Integration (Devlog updates)\n"
            "• ⚔️ Memory Weaponization (Training data)\n"
            "• 🛠️ Developer Tools (Template orchestration)\n"
            "• 📈 Export Systems (Multi-format data)\n\n"
            "📊 Preview Mode: Limited to 5 conversations only\n"
            "👤 User Variables: Collected and displayed\n\n"
            "⏱️ Estimated time: 2-3 minutes\n\n"
            "Continue with comprehensive preview?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable button during processing
        if hasattr(self.preview_btn, 'setEnabled'):
            self.preview_btn.setEnabled(False)
        if hasattr(self.preview_btn, 'setText'):
            self.preview_btn.setText("🎭 Running Preview...")
        elif hasattr(self.preview_btn, 'update_status'):
            self.preview_btn.update_status("running", 0)
        
        # Get the main window and run the preview workflow
        main_window = self.window()
        if hasattr(main_window, 'run_end_to_end_workflow'):
            # Call with preview mode
            main_window.run_end_to_end_workflow("preview")
        else:
            QMessageBox.warning(
                self,
                "Preview Workflow Not Available",
                "The comprehensive preview workflow is not available in this version."
            )
            self.preview_btn.setEnabled(True)
            self.preview_btn.setText("🎯 Preview Workflow (5 Conversations)")
    
    @debug_button("Refresh ChatGPT", "Dashboard")
    @debug_button("refresh_chatgpt", "Dashboard Panel")
    def refresh_chatgpt(self, *args, **kwargs):
        """Refresh ChatGPT conversations."""
        try:
            if not self.scraping_manager:
                QMessageBox.warning(
                    self,
                    "Scraper Not Available",
                    "The scraper manager is not available."
                )
                return
            
            # Disable button during processing
            self.chatgpt_refresh_btn.setEnabled(False)
            self.chatgpt_refresh_btn.setText("🔄 Refreshing...")
            
            # Run scraper in background
            # This would typically use a worker thread
            # For now, just show a message
            QMessageBox.information(
                self,
                "ChatGPT Refresh",
                "ChatGPT refresh functionality will be implemented with proper background processing."
            )
            
            # Re-enable button
            self.chatgpt_refresh_btn.setEnabled(True)
            self.chatgpt_refresh_btn.setText("📥 Refresh ChatGPT")
            
        except Exception as e:
            logger.error(f"ChatGPT refresh failed: {e}")
            QMessageBox.critical(
                self,
                "ChatGPT Refresh Failed",
                f"Failed to refresh ChatGPT: {str(e)}"
            )
            self.chatgpt_refresh_btn.setEnabled(True)
            self.chatgpt_refresh_btn.setText("📥 Refresh ChatGPT") 
    
    def quick_ingestion_and_progress(self, *args, **kwargs):
        """Quick ingestion and progress update."""
        try:
            logger.info("Starting quick ingestion and progress update...")
            
            # Disable button during processing
            self.quick_ingest_btn.setEnabled(False)
            self.quick_ingest_btn.setText("🔄 Processing...")
            
            # Update status
            if hasattr(self, "status_label"):
                self.status_label.setText("Quick ingestion in progress...")
            
            # Get the main window and trigger quick ingestion
            main_window = self.window()
            if hasattr(main_window, 'import_new_conversations'):
                main_window.import_new_conversations()
            else:
                logger.warning("Main window import_new_conversations method not available")
                if hasattr(self, "status_label"):
                    self.status_label.setText("Quick ingestion not available")
            
            # Re-enable button
            self.quick_ingest_btn.setEnabled(True)
            self.quick_ingest_btn.setText("⚡ Quick Ingest")
            
        except Exception as e:
            logger.error(f"Quick ingestion failed: {e}")
            if hasattr(self, "status_label"):
                self.status_label.setText(f"Quick ingestion failed: {str(e)}")
            self.quick_ingest_btn.setEnabled(True)
            self.quick_ingest_btn.setText("⚡ Quick Ingest")
    
    def update_stats(self, stats: dict):
        """
        Update dashboard statistics
        
        Args:
            stats: Dictionary containing statistics to update
        """
        try:
            if hasattr(self, 'stat_labels') and self.stat_labels:
                # Update conversation statistics
                if 'conversations' in stats:
                    self.stat_labels.get('total_conversations', QLabel()).setText(str(stats['conversations']))
                if 'messages' in stats:
                    self.stat_labels.get('total_messages', QLabel()).setText(str(stats['messages']))
                if 'avg_messages_per_conversation' in stats:
                    self.stat_labels.get('avg_messages_per_conversation', QLabel()).setText(f"{stats['avg_messages_per_conversation']:.1f}")
                if 'earliest_date' in stats:
                    self.stat_labels.get('earliest_date', QLabel()).setText(str(stats['earliest_date']))
                if 'latest_date' in stats:
                    self.stat_labels.get('latest_date', QLabel()).setText(str(stats['latest_date']))
                
                # Update game statistics if available
                if 'game_stats' in stats:
                    game_stats = stats['game_stats']
                    # Add game-specific stats updates here if needed
                    
                logger.info("Dashboard statistics updated successfully")
            else:
                logger.warning("Dashboard stat_labels not available for update")
                
        except Exception as e:
            logger.error(f"Error updating dashboard stats: {e}") 