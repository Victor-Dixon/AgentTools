"""
Workflow Controller - GUI Workflow Management
===========================================

This controller handles all workflow execution and status management
for the GUI, separated from the main window for better organization.
"""

import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


class WorkflowController(QObject):
    """Controls workflow execution and status management for the GUI."""
    
    # Signals for workflow events
    workflow_started = pyqtSignal(str)  # workflow_name
    workflow_completed = pyqtSignal(str, dict)  # workflow_name, results
    workflow_failed = pyqtSignal(str, str)  # workflow_name, error
    workflow_progress = pyqtSignal(str, str)  # workflow_name, status
    
    def __init__(self, parent=None):
        """Initialize the workflow controller."""
        super().__init__(parent)
        self.main_window = parent
        self.active_workflows = {}
        self.workflow_history = []
        
    def run_end_to_end_workflow(self, mode: str = "batch"):
        """Run the complete end-to-end workflow for processing conversations."""
        from threading import Thread
        import asyncio
        
        workflow_name = f"end_to_end_{mode}"
        self.workflow_started.emit(workflow_name)
        
        def _run_workflow():
            try:
                # Import the refactored workflow
                import sys
                sys.path.insert(0, "scripts")
                from end_to_end_workflow_refactored import RefactoredEndToEndWorkflow

                # Create workflow instance
                workflow = RefactoredEndToEndWorkflow()
                
                # Run the workflow
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Run the appropriate workflow based on mode
                    if mode == "batch":
                        results = loop.run_until_complete(
                            workflow.run_conversation_analysis_workflow()
                        )
                    elif mode == "preview":
                        results = loop.run_until_complete(
                            workflow.run_comprehensive_showcase()
                        )
                    elif mode == "setup":
                        results = loop.run_until_complete(
                            workflow.run_setup_and_test()
                        )
                    elif mode == "testing":
                        results = loop.run_until_complete(
                            workflow.run_comprehensive_testing()
                        )
                    else:
                        results = loop.run_until_complete(
                            workflow.run_conversation_analysis_workflow()
                        )
                    
                    # Schedule UI updates on the main thread
                    def update_ui():
                        self._handle_workflow_success(workflow_name, mode, results)
                    
                    # Schedule UI update on main thread
                    QTimer.singleShot(0, update_ui)
                
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"End-to-end workflow failed: {e}")
                
                # Schedule error display on main thread
                def show_error():
                    self._handle_workflow_error(workflow_name, str(e))
                
                QTimer.singleShot(0, show_error)
        
        # Run workflow in background thread
        workflow_thread = Thread(target=_run_workflow, daemon=True)
        workflow_thread.start()
        
        # Track active workflow
        self.active_workflows[workflow_name] = {
            "thread": workflow_thread,
            "start_time": datetime.now(),
            "mode": mode
        }
    
    def _handle_workflow_success(self, workflow_name: str, mode: str, results: Dict[str, Any]):
        """Handle successful workflow completion."""
        try:
            # Remove from active workflows
            if workflow_name in self.active_workflows:
                workflow_info = self.active_workflows.pop(workflow_name)
                duration = datetime.now() - workflow_info["start_time"]
            else:
                duration = None
            
            # Add to history
            self.workflow_history.append({
                "name": workflow_name,
                "mode": mode,
                "status": "completed",
                "results": results,
                "duration": duration.total_seconds() if duration else None,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update status bar
            if self.main_window and hasattr(self.main_window, 'statusBar'):
                successful = 1 if results.get("status") == "completed" else 0
                total = 1
                
                self.main_window.statusBar().showMessage(
                    f"🎉 {workflow_name} completed: {successful}/{total} conversations processed",
                    10000,
                )
            
            # Show completion dialog with mode-specific content
            self._show_completion_dialog(workflow_name, mode, results)
            
            # Refresh dashboard if available
            if self.main_window and hasattr(self.main_window, 'refresh_dashboard_data'):
                self.main_window.refresh_dashboard_data()
            
            # Emit success signal
            self.workflow_completed.emit(workflow_name, results)
            
        except Exception as e:
            logger.error(f"Failed to handle workflow success: {e}")
    
    def _handle_workflow_error(self, workflow_name: str, error: str):
        """Handle workflow execution error."""
        try:
            # Remove from active workflows
            if workflow_name in self.active_workflows:
                workflow_info = self.active_workflows.pop(workflow_name)
                duration = datetime.now() - workflow_info["start_time"]
            else:
                duration = None
            
            # Add to history
            self.workflow_history.append({
                "name": workflow_name,
                "status": "failed",
                "error": error,
                "duration": duration.total_seconds() if duration else None,
                "timestamp": datetime.now().isoformat()
            })
            
            # Show error dialog
            if self.main_window:
                QMessageBox.critical(
                    self.main_window,
                    "Workflow Failed",
                    f"❌ {workflow_name} failed:\n\n{error}"
                )
            
            # Emit error signal
            self.workflow_failed.emit(workflow_name, error)
            
        except Exception as e:
            logger.error(f"Failed to handle workflow error: {e}")
    
    def _show_completion_dialog(self, workflow_name: str, mode: str, results: Dict[str, Any]):
        """Show workflow completion dialog."""
        if not self.main_window:
            return
        
        try:
            workflow_status = results.get("status", "unknown")
            
            if mode == "preview":
                # Handle preview workflow results
                data = results.get("data", {})
                features_showcased = len(data.get("features_showcased", []))
                user_variables = len(data.get("user_variables", {}))
                
                # Get comprehensive report for additional details
                report = data.get("comprehensive_report", {})
                success_rate = report.get("execution_summary", {}).get("success_rate", 0)
                system_health = report.get("setup_analysis", {}).get("system_health", "Good")
                setup_issues = len(data.get("user_variables", {}).get("setup_issues_resolved", []))
                
                message = f"🎉 Preview workflow completed!\n\n"
                message += f"📊 Preview Results:\n"
                message += f"• Status: {workflow_status}\n"
                message += f"• Features Showcased: {features_showcased}\n"
                message += f"• User Variables Collected: {user_variables}\n"
                message += f"• Success Rate: {success_rate:.1f}%\n"
                message += f"• Processing Mode: Preview (5 conversations max)\n\n"
                
                if setup_issues > 0:
                    message += f"🔧 Setup Assistance:\n"
                    message += f"• Auto-resolved {setup_issues} setup issues\n"
                    message += f"• System Health: {system_health}\n\n"
                
                message += f"🎭 All Dreamscape features have been demonstrated!\n"
                message += f"🔄 Refresh dashboard to see updated stats!"
                
                QMessageBox.information(
                    self.main_window,
                    "🎭 Comprehensive Preview Complete",
                    message,
                )
            else:
                # Handle regular workflow results
                data = results.get("data", {})
                steps_completed = len(data.get("steps_completed", []))
                errors = len(data.get("errors", []))
                
                QMessageBox.information(
                    self.main_window,
                    "End-to-End Workflow Complete",
                    f"🎉 Workflow completed!\n\n"
                    f"📊 Results:\n"
                    f"• Status: {workflow_status}\n"
                    f"• Steps completed: {steps_completed}\n"
                    f"• Errors: {errors}\n\n"
                    f"🔄 Refresh dashboard to see updated stats!",
                )
                
        except Exception as e:
            logger.error(f"Failed to show completion dialog: {e}")
            # Fallback simple dialog
            QMessageBox.information(
                self.main_window,
                "Workflow Complete",
                f"✅ {workflow_name} completed successfully!"
            )
    
    def get_active_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active workflows."""
        return self.active_workflows.copy()
    
    def get_workflow_history(self) -> list:
        """Get workflow execution history."""
        return self.workflow_history.copy()
    
    def cancel_active_workflows(self):
        """Cancel all active workflows."""
        for workflow_name, workflow_info in self.active_workflows.items():
            logger.info(f"Cancelling workflow: {workflow_name}")
            # Note: Thread cancellation is limited in Python
            # This mainly serves to clean up tracking
        
        self.active_workflows.clear()
    
    def run_setup_workflow(self):
        """Run the setup and test workflow."""
        self.run_end_to_end_workflow("setup")
    
    def run_preview_workflow(self):
        """Run the comprehensive preview workflow.""" 
        self.run_end_to_end_workflow("preview")
    
    def run_full_workflow(self):
        """Run the full conversation analysis workflow."""
        self.run_end_to_end_workflow("batch") 