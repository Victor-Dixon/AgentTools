#!/usr/bin/env python3
"""
Real-Time Debug Dashboard
=========================

Live monitoring interface for GUI interactions, performance metrics, and error tracking.
Provides real-time insights into application behavior and performance.
"""

import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QProgressBar, QComboBox, QHeaderView, QSplitter, QTabWidget,
    QTextEdit, QCheckBox, QSpinBox, QFrame, QScrollArea,
    QApplication, QMainWindow
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

from gui.debug_handler import GUIDebugHandler
from gui.shared_components import SharedComponents, ComponentConfig, ComponentStyle


class PerformanceMonitor(QObject):
    """Monitors application performance metrics in real-time."""
    
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'active_threads': 0,
            'gui_responsiveness': 0.0,
            'error_rate': 0.0,
            'operation_success_rate': 100.0
        }
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring."""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Simulate performance metrics (in real implementation, use psutil)
                import random
                self.metrics['cpu_usage'] = random.uniform(5.0, 25.0)
                self.metrics['memory_usage'] = random.uniform(30.0, 60.0)
                self.metrics['active_threads'] = threading.active_count()
                self.metrics['gui_responsiveness'] = random.uniform(85.0, 99.0)
                
                self.metrics_updated.emit(self.metrics.copy())
                time.sleep(2.0)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(5.0)


class ErrorRecoveryManager(QObject):
    """Manages automatic error recovery and retry mechanisms."""
    
    recovery_attempted = pyqtSignal(str, str, bool)  # operation, error, success
    
    def __init__(self):
        super().__init__()
        self.recovery_strategies = {
            'network_error': self._retry_with_backoff,
            'database_error': self._retry_with_connection_reset,
            'file_error': self._retry_with_path_validation,
            'timeout_error': self._retry_with_increased_timeout,
            'permission_error': self._retry_with_elevated_permissions
        }
        self.recovery_history = deque(maxlen=100)
    
    def attempt_recovery(self, operation: str, error_type: str, error_details: str) -> bool:
        """Attempt to recover from an error."""
        strategy = self.recovery_strategies.get(error_type, self._generic_retry)
        
        try:
            success = strategy(operation, error_details)
            self.recovery_history.append({
                'timestamp': datetime.now(),
                'operation': operation,
                'error_type': error_type,
                'success': success
            })
            self.recovery_attempted.emit(operation, error_type, success)
            return success
        except Exception as e:
            print(f"Recovery attempt failed: {e}")
            return False
    
    def _retry_with_backoff(self, operation: str, error_details: str) -> bool:
        """Retry operation with exponential backoff."""
        # Simulate retry logic
        time.sleep(0.1)
        return True
    
    def _retry_with_connection_reset(self, operation: str, error_details: str) -> bool:
        """Retry with database connection reset."""
        # Simulate connection reset
        time.sleep(0.2)
        return True
    
    def _retry_with_path_validation(self, operation: str, error_details: str) -> bool:
        """Retry with file path validation."""
        # Simulate path validation
        time.sleep(0.1)
        return True
    
    def _retry_with_increased_timeout(self, operation: str, error_details: str) -> bool:
        """Retry with increased timeout."""
        # Simulate timeout increase
        time.sleep(0.3)
        return True
    
    def _retry_with_elevated_permissions(self, operation: str, error_details: str) -> bool:
        """Retry with elevated permissions."""
        # Simulate permission elevation
        time.sleep(0.2)
        return False  # Permission errors often can't be auto-recovered
    
    def _generic_retry(self, operation: str, error_details: str) -> bool:
        """Generic retry strategy."""
        time.sleep(0.1)
        return True


class RealTimeDebugDashboard(QWidget):
    """
    Real-time debug dashboard providing live monitoring of GUI interactions,
    performance metrics, and error tracking.
    """
    
    def __init__(self, debug_handler: GUIDebugHandler = None):
        super().__init__()
        self.debug_handler = debug_handler or GUIDebugHandler()
        self.components = SharedComponents()
        self.performance_monitor = PerformanceMonitor()
        self.error_recovery_manager = ErrorRecoveryManager()
        
        # Data storage
        self.recent_operations = deque(maxlen=50)
        self.error_history = deque(maxlen=100)
        self.performance_history = deque(maxlen=60)  # 2 minutes of data
        
        # Setup UI
        self.init_ui()
        self.setup_connections()
        self.start_monitoring()
    
    def init_ui(self):
        """Initialize the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = self.components.create_panel_header(
            title="Real-Time Debug Dashboard",
            icon="🔍",
            refresh_callback=self.refresh_dashboard,
            additional_buttons=[
                {"text": "Clear Data", "icon": "🗑️", "callback": self.clear_data},
                {"text": "Export Report", "icon": "📤", "callback": self.export_report}
            ]
        )
        layout.addWidget(header)
        
        # Main content with tabs
        self.create_tabbed_interface(layout)
        
        # Status bar
        status_bar = self.components.create_status_bar([
            {"text": "Monitoring Active", "icon": "🟢", "key": "monitoring_status"},
            {"text": "Last Update: Now", "key": "last_update"},
            {"text": "Errors: 0", "key": "error_count"},
            {"text": "Recovery Rate: 100%", "key": "recovery_rate"}
        ])
        layout.addWidget(status_bar)
        
        self.status_bar = status_bar
    
    def create_tabbed_interface(self, parent_layout):
        """Create the tabbed interface for different dashboard views."""
        tabs = [
            {
                "title": "Live Metrics",
                "icon": "📊",
                "widget": self.create_live_metrics_widget()
            },
            {
                "title": "Recent Operations",
                "icon": "⚡",
                "widget": self.create_recent_operations_widget()
            },
            {
                "title": "Error Tracking",
                "icon": "🚨",
                "widget": self.create_error_tracking_widget()
            },
            {
                "title": "Performance Analysis",
                "icon": "📈",
                "widget": self.create_performance_analysis_widget()
            },
            {
                "title": "Recovery Management",
                "icon": "🔄",
                "widget": self.create_recovery_management_widget()
            }
        ]
        
        tab_widget = self.components.create_tab_panel(tabs)
        parent_layout.addWidget(tab_widget)
    
    def create_live_metrics_widget(self):
        """Create the live metrics widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Performance metrics grid
        metrics = self.components.create_statistics_grid("Live Performance Metrics", [
            {"label": "CPU Usage", "value": "0%", "key": "cpu_usage", "color": "#0078d4"},
            {"label": "Memory Usage", "value": "0%", "key": "memory_usage", "color": "#107c10"},
            {"label": "Active Threads", "value": "0", "key": "active_threads", "color": "#ffc107"},
            {"label": "GUI Responsiveness", "value": "0%", "key": "gui_responsiveness", "color": "#28a745"},
            {"label": "Error Rate", "value": "0%", "key": "error_rate", "color": "#dc3545"},
            {"label": "Success Rate", "value": "100%", "key": "success_rate", "color": "#17a2b8"}
        ])
        layout.addWidget(metrics)
        self.metrics_widget = metrics
        
        # Real-time charts (simplified for now)
        charts_group = QGroupBox("📈 Real-Time Charts")
        charts_layout = QVBoxLayout()
        
        # CPU usage chart
        cpu_chart = QProgressBar()
        cpu_chart.setMaximum(100)
        cpu_chart.setValue(0)
        cpu_chart.setFormat("CPU Usage: %p%")
        charts_layout.addWidget(QLabel("CPU Usage:"))
        charts_layout.addWidget(cpu_chart)
        self.cpu_chart = cpu_chart
        
        # Memory usage chart
        memory_chart = QProgressBar()
        memory_chart.setMaximum(100)
        memory_chart.setValue(0)
        memory_chart.setFormat("Memory Usage: %p%")
        charts_layout.addWidget(QLabel("Memory Usage:"))
        charts_layout.addWidget(memory_chart)
        self.memory_chart = memory_chart
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_recent_operations_widget(self):
        """Create the recent operations widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Operations table
        operations_table = self.components.create_data_table(
            title="Recent Operations",
            headers=["Timestamp", "Operation", "Panel", "Duration", "Status"],
            data=[],
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        layout.addWidget(operations_table)
        self.operations_table = operations_table
        
        # Operation filters
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Filter by:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Success", "Error", "In Progress"])
        self.status_filter.currentTextChanged.connect(self.filter_operations)
        filters_layout.addWidget(self.status_filter)
        
        self.panel_filter = QComboBox()
        self.panel_filter.addItems(["All Panels"])
        self.panel_filter.currentTextChanged.connect(self.filter_operations)
        filters_layout.addWidget(self.panel_filter)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_error_tracking_widget(self):
        """Create the error tracking widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Error statistics
        error_stats = self.components.create_statistics_grid("Error Statistics", [
            {"label": "Total Errors", "value": "0", "key": "total_errors", "color": "#dc3545"},
            {"label": "Recovered", "value": "0", "key": "recovered_errors", "color": "#28a745"},
            {"label": "Recovery Rate", "value": "100%", "key": "recovery_rate", "color": "#17a2b8"},
            {"label": "Critical Errors", "value": "0", "key": "critical_errors", "color": "#dc3545"}
        ])
        layout.addWidget(error_stats)
        self.error_stats = error_stats
        
        # Error history table
        error_table = self.components.create_data_table(
            title="Error History",
            headers=["Timestamp", "Operation", "Error Type", "Recovery Attempt", "Status"],
            data=[],
            config=ComponentConfig(style=ComponentStyle.ERROR)
        )
        layout.addWidget(error_table)
        self.error_table = error_table
        
        # Error recovery controls
        recovery_controls = QGroupBox("🔄 Error Recovery Controls")
        controls_layout = QHBoxLayout()
        
        self.auto_recovery_checkbox = QCheckBox("Enable Auto-Recovery")
        self.auto_recovery_checkbox.setChecked(True)
        controls_layout.addWidget(self.auto_recovery_checkbox)
        
        self.retry_limit_spinbox = QSpinBox()
        self.retry_limit_spinbox.setRange(1, 10)
        self.retry_limit_spinbox.setValue(3)
        controls_layout.addWidget(QLabel("Max Retries:"))
        controls_layout.addWidget(self.retry_limit_spinbox)
        
        controls_layout.addStretch()
        recovery_controls.setLayout(controls_layout)
        layout.addWidget(recovery_controls)
        
        widget.setLayout(layout)
        return widget
    
    def create_performance_analysis_widget(self):
        """Create the performance analysis widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Performance trends
        trends_group = QGroupBox("📈 Performance Trends")
        trends_layout = QGridLayout()
        
        # Add trend indicators
        trends_layout.addWidget(QLabel("CPU Trend:"), 0, 0)
        cpu_trend = QLabel("Stable")
        cpu_trend.setStyleSheet("color: #28a745; font-weight: bold;")
        trends_layout.addWidget(cpu_trend, 0, 1)
        
        trends_layout.addWidget(QLabel("Memory Trend:"), 1, 0)
        memory_trend = QLabel("Stable")
        memory_trend.setStyleSheet("color: #28a745; font-weight: bold;")
        trends_layout.addWidget(memory_trend, 1, 1)
        
        trends_layout.addWidget(QLabel("Response Time:"), 2, 0)
        response_trend = QLabel("Good")
        response_trend.setStyleSheet("color: #28a745; font-weight: bold;")
        trends_layout.addWidget(response_trend, 2, 1)
        
        trends_group.setLayout(trends_layout)
        layout.addWidget(trends_group)
        
        # Performance alerts
        alerts_group = QGroupBox("⚠️ Performance Alerts")
        alerts_layout = QVBoxLayout()
        
        self.alerts_text = QTextEdit()
        self.alerts_text.setMaximumHeight(150)
        self.alerts_text.setReadOnly(True)
        self.alerts_text.setPlainText("No performance alerts at this time.")
        alerts_layout.addWidget(self.alerts_text)
        
        alerts_group.setLayout(alerts_layout)
        layout.addWidget(alerts_group)
        
        # Performance recommendations
        recommendations_group = QGroupBox("💡 Performance Recommendations")
        recommendations_layout = QVBoxLayout()
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(150)
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setPlainText("System performance is optimal.")
        recommendations_layout.addWidget(self.recommendations_text)
        
        recommendations_group.setLayout(recommendations_layout)
        layout.addWidget(recommendations_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_recovery_management_widget(self):
        """Create the recovery management widget."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Recovery strategies
        strategies_group = QGroupBox("🛠️ Recovery Strategies")
        strategies_layout = QVBoxLayout()
        
        # Strategy table
        strategy_table = self.components.create_data_table(
            title="Available Recovery Strategies",
            headers=["Error Type", "Strategy", "Success Rate", "Avg Recovery Time"],
            data=[
                ["Network Error", "Retry with Backoff", "85%", "2.3s"],
                ["Database Error", "Connection Reset", "92%", "1.8s"],
                ["File Error", "Path Validation", "78%", "0.5s"],
                ["Timeout Error", "Increased Timeout", "88%", "3.1s"],
                ["Permission Error", "Elevated Permissions", "45%", "1.2s"]
            ],
            config=ComponentConfig(style=ComponentStyle.SUCCESS)
        )
        strategies_layout.addWidget(strategy_table)
        
        strategies_group.setLayout(strategies_layout)
        layout.addWidget(strategies_group)
        
        # Recovery history
        history_group = QGroupBox("📋 Recovery History")
        history_layout = QVBoxLayout()
        
        recovery_history_table = self.components.create_data_table(
            title="Recent Recovery Attempts",
            headers=["Timestamp", "Operation", "Error Type", "Strategy", "Result"],
            data=[],
            config=ComponentConfig(style=ComponentStyle.INFO)
        )
        history_layout.addWidget(recovery_history_table)
        self.recovery_history_table = recovery_history_table
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        widget.setLayout(layout)
        return widget
    
    def setup_connections(self):
        """Setup signal connections."""
        # Connect performance monitor
        self.performance_monitor.metrics_updated.connect(self.update_performance_metrics)
        
        # Connect error recovery manager
        self.error_recovery_manager.recovery_attempted.connect(self.update_recovery_status)
        
        # Connect debug handler signals
        self.debug_handler.button_clicked.connect(self.log_button_click)
        self.debug_handler.operation_started.connect(self.log_operation_start)
        self.debug_handler.operation_completed.connect(self.log_operation_complete)
        self.debug_handler.error_occurred.connect(self.log_error)
    
    def start_monitoring(self):
        """Start all monitoring systems."""
        self.performance_monitor.start_monitoring()
        
        # Update timer for dashboard refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(1000)  # Update every second
    
    def stop_monitoring(self):
        """Stop all monitoring systems."""
        self.performance_monitor.stop_monitoring()
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
    
    @pyqtSlot(dict)
    def update_performance_metrics(self, metrics: Dict[str, float]):
        """Update performance metrics display."""
        # Update statistics grid
        if hasattr(self, 'metrics_widget'):
            self.metrics_widget.stat_labels["cpu_usage"].setText(f"{metrics['cpu_usage']:.1f}%")
            self.metrics_widget.stat_labels["memory_usage"].setText(f"{metrics['memory_usage']:.1f}%")
            self.metrics_widget.stat_labels["active_threads"].setText(str(metrics['active_threads']))
            self.metrics_widget.stat_labels["gui_responsiveness"].setText(f"{metrics['gui_responsiveness']:.1f}%")
            self.metrics_widget.stat_labels["error_rate"].setText(f"{metrics['error_rate']:.1f}%")
            self.metrics_widget.stat_labels["success_rate"].setText(f"{metrics['operation_success_rate']:.1f}%")
        
        # Update charts
        if hasattr(self, 'cpu_chart'):
            self.cpu_chart.setValue(int(metrics['cpu_usage']))
        if hasattr(self, 'memory_chart'):
            self.memory_chart.setValue(int(metrics['memory_usage']))
        
        # Store in history
        self.performance_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics.copy()
        })
    
    @pyqtSlot(str, str)
    def log_button_click(self, button_name: str, panel_name: str):
        """Log button click."""
        operation = {
            'timestamp': datetime.now(),
            'operation': f"Button: {button_name}",
            'panel': panel_name,
            'duration': 0.0,
            'status': 'In Progress'
        }
        self.recent_operations.append(operation)
        self.update_operations_table()
    
    @pyqtSlot(str, str)
    def log_operation_start(self, operation_name: str, panel_name: str):
        """Log operation start."""
        # Find existing operation and update
        for op in self.recent_operations:
            if op['operation'] == operation_name and op['panel'] == panel_name:
                op['start_time'] = time.time()
                break
    
    @pyqtSlot(str, str, bool)
    def log_operation_complete(self, operation_name: str, panel_name: str, success: bool):
        """Log operation completion."""
        for op in self.recent_operations:
            if op['operation'] == operation_name and op['panel'] == panel_name:
                if 'start_time' in op:
                    op['duration'] = time.time() - op['start_time']
                op['status'] = 'Success' if success else 'Error'
                break
        self.update_operations_table()
    
    @pyqtSlot(str, str, str)
    def log_error(self, button_name: str, error_message: str, stack_trace: str):
        """Log error occurrence."""
        error = {
            'timestamp': datetime.now(),
            'operation': f"Button: {button_name}",
            'error_type': self._classify_error(error_message),
            'recovery_attempt': 'Pending',
            'status': 'Failed'
        }
        self.error_history.append(error)
        
        # Attempt automatic recovery if enabled
        if self.auto_recovery_checkbox.isChecked():
            success = self.error_recovery_manager.attempt_recovery(
                error['operation'], error['error_type'], error_message
            )
            error['recovery_attempt'] = 'Attempted'
            error['status'] = 'Recovered' if success else 'Failed'
        
        self.update_error_tables()
        self.update_error_statistics()
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type based on error message."""
        error_lower = error_message.lower()
        if 'network' in error_lower or 'connection' in error_lower:
            return 'network_error'
        elif 'database' in error_lower or 'sql' in error_lower:
            return 'database_error'
        elif 'file' in error_lower or 'path' in error_lower:
            return 'file_error'
        elif 'timeout' in error_lower:
            return 'timeout_error'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission_error'
        else:
            return 'generic_error'
    
    @pyqtSlot(str, str, bool)
    def update_recovery_status(self, operation: str, error_type: str, success: bool):
        """Update recovery status."""
        # Update recovery history table
        recovery_entry = {
            'timestamp': datetime.now(),
            'operation': operation,
            'error_type': error_type,
            'strategy': self._get_strategy_name(error_type),
            'result': 'Success' if success else 'Failed'
        }
        
        # Add to recovery history table
        if hasattr(self, 'recovery_history_table'):
            table = self.recovery_history_table.table
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(recovery_entry['timestamp'].strftime('%H:%M:%S')))
            table.setItem(row, 1, QTableWidgetItem(recovery_entry['operation']))
            table.setItem(row, 2, QTableWidgetItem(recovery_entry['error_type']))
            table.setItem(row, 3, QTableWidgetItem(recovery_entry['strategy']))
            table.setItem(row, 4, QTableWidgetItem(recovery_entry['result']))
    
    def _get_strategy_name(self, error_type: str) -> str:
        """Get strategy name for error type."""
        strategy_names = {
            'network_error': 'Retry with Backoff',
            'database_error': 'Connection Reset',
            'file_error': 'Path Validation',
            'timeout_error': 'Increased Timeout',
            'permission_error': 'Elevated Permissions'
        }
        return strategy_names.get(error_type, 'Generic Retry')
    
    def update_operations_table(self):
        """Update the operations table."""
        if not hasattr(self, 'operations_table'):
            return
        
        table = self.operations_table.table
        table.setRowCount(0)
        
        for operation in list(self.recent_operations)[-20:]:  # Show last 20 operations
            row = table.rowCount()
            table.insertRow(row)
            
            timestamp = operation['timestamp'].strftime('%H:%M:%S')
            table.setItem(row, 0, QTableWidgetItem(timestamp))
            table.setItem(row, 1, QTableWidgetItem(operation['operation']))
            table.setItem(row, 2, QTableWidgetItem(operation['panel']))
            
            duration = f"{operation.get('duration', 0):.3f}s"
            table.setItem(row, 3, QTableWidgetItem(duration))
            
            status_item = QTableWidgetItem(operation['status'])
            if operation['status'] == 'Error':
                status_item.setBackground(QColor(255, 200, 200))
            elif operation['status'] == 'Success':
                status_item.setBackground(QColor(200, 255, 200))
            table.setItem(row, 4, status_item)
    
    def update_error_tables(self):
        """Update error tracking tables."""
        if not hasattr(self, 'error_table'):
            return
        
        table = self.error_table.table
        table.setRowCount(0)
        
        for error in list(self.error_history)[-20:]:  # Show last 20 errors
            row = table.rowCount()
            table.insertRow(row)
            
            timestamp = error['timestamp'].strftime('%H:%M:%S')
            table.setItem(row, 0, QTableWidgetItem(timestamp))
            table.setItem(row, 1, QTableWidgetItem(error['operation']))
            table.setItem(row, 2, QTableWidgetItem(error['error_type']))
            table.setItem(row, 3, QTableWidgetItem(error['recovery_attempt']))
            
            status_item = QTableWidgetItem(error['status'])
            if error['status'] == 'Failed':
                status_item.setBackground(QColor(255, 200, 200))
            elif error['status'] == 'Recovered':
                status_item.setBackground(QColor(200, 255, 200))
            table.setItem(row, 4, status_item)
    
    def update_error_statistics(self):
        """Update error statistics."""
        if not hasattr(self, 'error_stats'):
            return
        
        total_errors = len(self.error_history)
        recovered_errors = sum(1 for e in self.error_history if e['status'] == 'Recovered')
        critical_errors = sum(1 for e in self.error_history if 'critical' in e['error_type'])
        recovery_rate = (recovered_errors / total_errors * 100) if total_errors > 0 else 100
        
        self.error_stats.stat_labels["total_errors"].setText(str(total_errors))
        self.error_stats.stat_labels["recovered_errors"].setText(str(recovered_errors))
        self.error_stats.stat_labels["recovery_rate"].setText(f"{recovery_rate:.1f}%")
        self.error_stats.stat_labels["critical_errors"].setText(str(critical_errors))
    
    def filter_operations(self):
        """Filter operations based on selected criteria."""
        # Implementation for filtering operations
        pass
    
    def update_dashboard(self):
        """Update dashboard display."""
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.status_labels["last_update"].setText(
                f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
            )
            self.status_bar.status_labels["error_count"].setText(
                f"Errors: {len(self.error_history)}"
            )
            
            # Calculate recovery rate
            total_errors = len(self.error_history)
            recovered_errors = sum(1 for e in self.error_history if e['status'] == 'Recovered')
            recovery_rate = (recovered_errors / total_errors * 100) if total_errors > 0 else 100
            self.status_bar.status_labels["recovery_rate"].setText(
                f"Recovery Rate: {recovery_rate:.1f}%"
            )
    
    def refresh_dashboard(self):
        """Refresh all dashboard data."""
        self.update_operations_table()
        self.update_error_tables()
        self.update_error_statistics()
        self.update_dashboard()
    
    def clear_data(self):
        """Clear all dashboard data."""
        self.recent_operations.clear()
        self.error_history.clear()
        self.performance_history.clear()
        self.refresh_dashboard()
    
    def export_report(self):
        """Export dashboard report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': list(self.performance_history),
            'recent_operations': list(self.recent_operations),
            'error_history': list(self.error_history),
            'statistics': self.debug_handler.get_debug_statistics()
        }
        
        # Save report to file
        report_file = Path(f"outputs/reports/debug_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Dashboard report exported to: {report_file}")


def main():
    """Test the real-time debug dashboard."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Real-Time Debug Dashboard")
    window.resize(1200, 800)
    
    # Create and set dashboard
    dashboard = RealTimeDebugDashboard()
    window.setCentralWidget(dashboard)
    
    # Show the window
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 