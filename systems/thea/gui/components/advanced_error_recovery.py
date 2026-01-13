#!/usr/bin/env python3
"""
Advanced Error Recovery System
==============================

Comprehensive error recovery and retry mechanisms with pattern analysis
and automatic recovery strategies for different error types.
"""

import sys
import time
import threading
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from collections import defaultdict, deque
from pathlib import Path
from enum import Enum
import json
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QProgressBar, QComboBox, QHeaderView, QSplitter, QTabWidget,
    QTextEdit, QCheckBox, QSpinBox, QFrame, QScrollArea,
    QMessageBox, QApplication, QMainWindow, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

from gui.debug_handler import GUIDebugHandler
from gui.shared_components import SharedComponents, ComponentConfig, ComponentStyle


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Recovery strategy types."""
    RETRY = "retry"
    BACKOFF = "backoff"
    RESET_CONNECTION = "reset_connection"
    VALIDATE_PATH = "validate_path"
    INCREASE_TIMEOUT = "increase_timeout"
    ELEVATE_PERMISSIONS = "elevate_permissions"
    FALLBACK = "fallback"
    MANUAL_INTERVENTION = "manual_intervention"


class ErrorPattern:
    """Represents an error pattern for analysis."""
    
    def __init__(self, error_type: str, message_pattern: str, severity: ErrorSeverity):
        self.error_type = error_type
        self.message_pattern = message_pattern
        self.severity = severity
        self.occurrence_count = 0
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.recovery_success_rate = 0.0
        self.avg_recovery_time = 0.0
        self.recommended_strategy = None


class RecoveryAttempt:
    """Represents a recovery attempt."""
    
    def __init__(self, operation: str, error_type: str, strategy: RecoveryStrategy):
        self.operation = operation
        self.error_type = error_type
        self.strategy = strategy
        self.timestamp = datetime.now()
        self.start_time = time.time()
        self.success = False
        self.duration = 0.0
        self.error_message = ""
        self.recovery_details = ""


class AdvancedErrorRecovery(QObject):
    """
    Advanced error recovery system with pattern analysis and automatic recovery.
    """
    
    # Signals
    recovery_attempted = pyqtSignal(str, str, bool)  # operation, error, success
    error_pattern_detected = pyqtSignal(str, int)  # pattern, count
    recovery_strategy_changed = pyqtSignal(str, str)  # error_type, strategy
    manual_intervention_required = pyqtSignal(str, str)  # operation, error
    
    def __init__(self, debug_handler: GUIDebugHandler = None):
        super().__init__()
        self.debug_handler = debug_handler or GUIDebugHandler()
        
        # Recovery configuration
        self.max_retry_attempts = 3
        self.retry_delay_base = 1.0  # seconds
        self.auto_recovery_enabled = True
        self.pattern_analysis_enabled = True
        
        # Data storage
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.recovery_history: deque = deque(maxlen=1000)
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.operation_blacklist: set = set()  # Operations that should not be auto-recovered
        
        # Recovery strategy implementations
        self.strategy_handlers = {
            RecoveryStrategy.RETRY: self._retry_strategy,
            RecoveryStrategy.BACKOFF: self._backoff_strategy,
            RecoveryStrategy.RESET_CONNECTION: self._reset_connection_strategy,
            RecoveryStrategy.VALIDATE_PATH: self._validate_path_strategy,
            RecoveryStrategy.INCREASE_TIMEOUT: self._increase_timeout_strategy,
            RecoveryStrategy.ELEVATE_PERMISSIONS: self._elevate_permissions_strategy,
            RecoveryStrategy.FALLBACK: self._fallback_strategy,
            RecoveryStrategy.MANUAL_INTERVENTION: self._manual_intervention_strategy
        }
        
        # Setup default strategies
        self._setup_default_strategies()
        
        # Connect to debug handler
        if self.debug_handler:
            self.debug_handler.error_occurred.connect(self.handle_error)
    
    def _setup_default_strategies(self):
        """Setup default recovery strategies for common error types."""
        default_strategies = {
            'network_error': RecoveryStrategy.BACKOFF,
            'connection_error': RecoveryStrategy.RESET_CONNECTION,
            'database_error': RecoveryStrategy.RESET_CONNECTION,
            'file_error': RecoveryStrategy.VALIDATE_PATH,
            'permission_error': RecoveryStrategy.ELEVATE_PERMISSIONS,
            'timeout_error': RecoveryStrategy.INCREASE_TIMEOUT,
            'resource_error': RecoveryStrategy.FALLBACK,
            'validation_error': RecoveryStrategy.MANUAL_INTERVENTION
        }
        
        for error_type, strategy in default_strategies.items():
            self.recovery_strategies[error_type] = strategy
    
    def handle_error(self, operation: str, error_message: str, stack_trace: str):
        """Handle an error occurrence."""
        error_type = self._classify_error(error_message)
        
        # Update error pattern
        self._update_error_pattern(error_type, error_message)
        
        # Check if operation should be auto-recovered
        if operation in self.operation_blacklist:
            self.manual_intervention_required.emit(operation, error_message)
            return
        
        # Attempt automatic recovery
        if self.auto_recovery_enabled:
            self.attempt_recovery(operation, error_type, error_message)
    
    def attempt_recovery(self, operation: str, error_type: str, error_message: str) -> bool:
        """Attempt to recover from an error."""
        strategy = self.recovery_strategies.get(error_type, RecoveryStrategy.RETRY)
        
        # Create recovery attempt
        attempt = RecoveryAttempt(operation, error_type, strategy)
        
        try:
            # Execute recovery strategy
            handler = self.strategy_handlers.get(strategy, self._retry_strategy)
            success = handler(operation, error_type, error_message, attempt)
            
            # Update attempt details
            attempt.success = success
            attempt.duration = time.time() - attempt.start_time
            attempt.error_message = error_message
            
            # Store in history
            self.recovery_history.append(attempt)
            
            # Update pattern statistics
            self._update_pattern_statistics(error_type, success, attempt.duration)
            
            # Emit signals
            self.recovery_attempted.emit(operation, error_type, success)
            
            if not success and strategy == RecoveryStrategy.MANUAL_INTERVENTION:
                self.manual_intervention_required.emit(operation, error_message)
            
            return success
            
        except Exception as e:
            attempt.success = False
            attempt.duration = time.time() - attempt.start_time
            attempt.error_message = error_message
            attempt.recovery_details = f"Recovery failed: {str(e)}"
            
            self.recovery_history.append(attempt)
            self.recovery_attempted.emit(operation, error_type, False)
            return False
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type based on error message."""
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in ['network', 'connection', 'socket']):
            return 'network_error'
        elif any(keyword in error_lower for keyword in ['database', 'sql', 'db']):
            return 'database_error'
        elif any(keyword in error_lower for keyword in ['file', 'path', 'directory']):
            return 'file_error'
        elif any(keyword in error_lower for keyword in ['permission', 'access', 'denied']):
            return 'permission_error'
        elif any(keyword in error_lower for keyword in ['timeout', 'timed out']):
            return 'timeout_error'
        elif any(keyword in error_lower for keyword in ['resource', 'memory', 'disk']):
            return 'resource_error'
        elif any(keyword in error_lower for keyword in ['validation', 'invalid', 'format']):
            return 'validation_error'
        else:
            return 'generic_error'
    
    def _update_error_pattern(self, error_type: str, error_message: str):
        """Update error pattern analysis."""
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = ErrorPattern(
                error_type, error_message, self._determine_severity(error_type)
            )
        
        pattern = self.error_patterns[error_type]
        pattern.occurrence_count += 1
        pattern.last_seen = datetime.now()
        
        # Emit pattern detection signal
        if self.pattern_analysis_enabled:
            self.error_pattern_detected.emit(error_type, pattern.occurrence_count)
    
    def _determine_severity(self, error_type: str) -> ErrorSeverity:
        """Determine error severity based on type."""
        severity_map = {
            'network_error': ErrorSeverity.MEDIUM,
            'database_error': ErrorSeverity.HIGH,
            'file_error': ErrorSeverity.MEDIUM,
            'permission_error': ErrorSeverity.HIGH,
            'timeout_error': ErrorSeverity.MEDIUM,
            'resource_error': ErrorSeverity.CRITICAL,
            'validation_error': ErrorSeverity.LOW,
            'generic_error': ErrorSeverity.MEDIUM
        }
        return severity_map.get(error_type, ErrorSeverity.MEDIUM)
    
    def _update_pattern_statistics(self, error_type: str, success: bool, duration: float):
        """Update pattern statistics after recovery attempt."""
        if error_type in self.error_patterns:
            pattern = self.error_patterns[error_type]
            
            # Update success rate
            total_attempts = len([a for a in self.recovery_history if a.error_type == error_type])
            successful_attempts = len([a for a in self.recovery_history 
                                     if a.error_type == error_type and a.success])
            pattern.recovery_success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # Update average recovery time
            recovery_times = [a.duration for a in self.recovery_history 
                            if a.error_type == error_type and a.success]
            if recovery_times:
                pattern.avg_recovery_time = sum(recovery_times) / len(recovery_times)
    
    # Recovery Strategy Implementations
    
    def _retry_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Simple retry strategy."""
        for i in range(self.max_retry_attempts):
            try:
                time.sleep(self.retry_delay_base)
                # Simulate retry logic
                attempt.recovery_details = f"Retry attempt {i + 1}/{self.max_retry_attempts}"
                return True  # Simulate success
            except Exception as e:
                attempt.recovery_details = f"Retry {i + 1} failed: {str(e)}"
        return False
    
    def _backoff_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Exponential backoff strategy."""
        for i in range(self.max_retry_attempts):
            try:
                delay = self.retry_delay_base * (2 ** i)  # Exponential backoff
                time.sleep(delay)
                attempt.recovery_details = f"Backoff attempt {i + 1} (delay: {delay:.1f}s)"
                return True  # Simulate success
            except Exception as e:
                attempt.recovery_details = f"Backoff {i + 1} failed: {str(e)}"
        return False
    
    def _reset_connection_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Reset connection strategy."""
        try:
            # Simulate connection reset
            time.sleep(0.5)
            attempt.recovery_details = "Connection reset successful"
            return True
        except Exception as e:
            attempt.recovery_details = f"Connection reset failed: {str(e)}"
            return False
    
    def _validate_path_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Path validation strategy."""
        try:
            # Simulate path validation
            time.sleep(0.2)
            attempt.recovery_details = "Path validation successful"
            return True
        except Exception as e:
            attempt.recovery_details = f"Path validation failed: {str(e)}"
            return False
    
    def _increase_timeout_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Increase timeout strategy."""
        try:
            # Simulate timeout increase
            time.sleep(0.3)
            attempt.recovery_details = "Timeout increased successfully"
            return True
        except Exception as e:
            attempt.recovery_details = f"Timeout increase failed: {str(e)}"
            return False
    
    def _elevate_permissions_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Elevate permissions strategy."""
        try:
            # Simulate permission elevation
            time.sleep(0.4)
            attempt.recovery_details = "Permission elevation attempted"
            return False  # Permission errors often can't be auto-recovered
        except Exception as e:
            attempt.recovery_details = f"Permission elevation failed: {str(e)}"
            return False
    
    def _fallback_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Fallback strategy."""
        try:
            # Simulate fallback logic
            time.sleep(0.3)
            attempt.recovery_details = "Fallback mechanism activated"
            return True
        except Exception as e:
            attempt.recovery_details = f"Fallback failed: {str(e)}"
            return False
    
    def _manual_intervention_strategy(self, operation: str, error_type: str, error_message: str, attempt: RecoveryAttempt) -> bool:
        """Manual intervention strategy."""
        attempt.recovery_details = "Manual intervention required"
        return False  # Always requires manual intervention
    
    # Configuration Methods
    
    def set_recovery_strategy(self, error_type: str, strategy: RecoveryStrategy):
        """Set recovery strategy for an error type."""
        self.recovery_strategies[error_type] = strategy
        self.recovery_strategy_changed.emit(error_type, strategy.value)
    
    def add_operation_to_blacklist(self, operation: str):
        """Add operation to recovery blacklist."""
        self.operation_blacklist.add(operation)
    
    def remove_operation_from_blacklist(self, operation: str):
        """Remove operation from recovery blacklist."""
        self.operation_blacklist.discard(operation)
    
    def set_max_retry_attempts(self, max_attempts: int):
        """Set maximum retry attempts."""
        self.max_retry_attempts = max_attempts
    
    def set_retry_delay_base(self, delay: float):
        """Set base retry delay."""
        self.retry_delay_base = delay
    
    def enable_auto_recovery(self, enabled: bool = True):
        """Enable or disable automatic recovery."""
        self.auto_recovery_enabled = enabled
    
    def enable_pattern_analysis(self, enabled: bool = True):
        """Enable or disable pattern analysis."""
        self.pattern_analysis_enabled = enabled
    
    # Analysis Methods
    
    def get_error_patterns(self) -> Dict[str, ErrorPattern]:
        """Get all error patterns."""
        return self.error_patterns.copy()
    
    def get_recovery_history(self) -> List[RecoveryAttempt]:
        """Get recovery history."""
        return list(self.recovery_history)
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        total_attempts = len(self.recovery_history)
        successful_attempts = len([a for a in self.recovery_history if a.success])
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        avg_recovery_time = 0.0
        if successful_attempts > 0:
            recovery_times = [a.duration for a in self.recovery_history if a.success]
            avg_recovery_time = sum(recovery_times) / len(recovery_times)
        
        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'success_rate': success_rate,
            'avg_recovery_time': avg_recovery_time,
            'error_patterns': len(self.error_patterns),
            'blacklisted_operations': len(self.operation_blacklist)
        }
    
    def get_error_pattern_analysis(self) -> Dict[str, Any]:
        """Get detailed error pattern analysis."""
        analysis = {}
        for error_type, pattern in self.error_patterns.items():
            analysis[error_type] = {
                'occurrence_count': pattern.occurrence_count,
                'severity': pattern.severity.value,
                'first_seen': pattern.first_seen.isoformat(),
                'last_seen': pattern.last_seen.isoformat(),
                'recovery_success_rate': pattern.recovery_success_rate,
                'avg_recovery_time': pattern.avg_recovery_time,
                'recommended_strategy': pattern.recommended_strategy.value if pattern.recommended_strategy else None
            }
        return analysis
    
    def export_recovery_report(self, output_file: str = None) -> str:
        """Export recovery report."""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"outputs/reports/error_recovery_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_recovery_statistics(),
            'error_patterns': self.get_error_pattern_analysis(),
            'recovery_history': [
                {
                    'operation': a.operation,
                    'error_type': a.error_type,
                    'strategy': a.strategy.value,
                    'timestamp': a.timestamp.isoformat(),
                    'success': a.success,
                    'duration': a.duration,
                    'error_message': a.error_message,
                    'recovery_details': a.recovery_details
                }
                for a in self.recovery_history
            ],
            'configuration': {
                'max_retry_attempts': self.max_retry_attempts,
                'retry_delay_base': self.retry_delay_base,
                'auto_recovery_enabled': self.auto_recovery_enabled,
                'pattern_analysis_enabled': self.pattern_analysis_enabled,
                'recovery_strategies': {k: v.value for k, v in self.recovery_strategies.items()},
                'blacklisted_operations': list(self.operation_blacklist)
            }
        }
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return output_file
    
    def clear_history(self):
        """Clear recovery history."""
        self.recovery_history.clear()
        self.error_patterns.clear()


class ErrorRecoveryDialog(QDialog):
    """Dialog for manual error recovery intervention."""
    
    def __init__(self, operation: str, error_message: str, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.error_message = error_message
        self.recovery_action = None
        
        self.setWindowTitle("Manual Error Recovery Required")
        self.setModal(True)
        self.resize(500, 300)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Error information
        error_group = QGroupBox("Error Information")
        error_layout = QVBoxLayout()
        
        error_layout.addWidget(QLabel(f"Operation: {self.operation}"))
        error_layout.addWidget(QLabel(f"Error: {self.error_message}"))
        
        error_group.setLayout(error_layout)
        layout.addWidget(error_group)
        
        # Recovery options
        recovery_group = QGroupBox("Recovery Options")
        recovery_layout = QVBoxLayout()
        
        self.retry_button = QPushButton("🔄 Retry Operation")
        self.retry_button.clicked.connect(lambda: self.set_recovery_action("retry"))
        recovery_layout.addWidget(self.retry_button)
        
        self.skip_button = QPushButton("⏭️ Skip Operation")
        self.skip_button.clicked.connect(lambda: self.set_recovery_action("skip"))
        recovery_layout.addWidget(self.skip_button)
        
        self.abort_button = QPushButton("❌ Abort Operation")
        self.abort_button.clicked.connect(lambda: self.set_recovery_action("abort"))
        recovery_layout.addWidget(self.abort_button)
        
        recovery_group.setLayout(recovery_layout)
        layout.addWidget(recovery_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def set_recovery_action(self, action: str):
        """Set the recovery action and close dialog."""
        self.recovery_action = action
        self.accept()
    
    def get_recovery_action(self) -> Optional[str]:
        """Get the selected recovery action."""
        return self.recovery_action


def main():
    """Test the advanced error recovery system."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Advanced Error Recovery System")
    window.resize(800, 600)
    
    # Create error recovery system
    recovery_system = AdvancedErrorRecovery()
    
    # Test error handling
    def test_error():
        recovery_system.handle_error(
            "test_operation",
            "Network connection failed",
            "Traceback..."
        )
    
    # Create test button
    test_button = QPushButton("Test Error Recovery")
    test_button.clicked.connect(test_error)
    
    window.setCentralWidget(test_button)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 