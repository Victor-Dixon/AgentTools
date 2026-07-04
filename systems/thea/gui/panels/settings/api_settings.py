#!/usr/bin/env python3
"""
API Settings Panel Component
Handles OpenAI and ChatGPT configuration.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QSpinBox, QComboBox, QCheckBox, QLabel
)
from PyQt6.QtCore import pyqtSignal

class APISettingsWidget(QWidget):
    """Widget for API configuration settings."""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the API settings UI."""
        layout = QVBoxLayout(self)
        
        # OpenAI settings
        openai_group = QGroupBox("OpenAI Configuration")
        openai_layout = QFormLayout(openai_group)
        
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setPlaceholderText("Enter your OpenAI API key")
        self.openai_key.textChanged.connect(self._on_setting_changed)
        openai_layout.addRow("API Key:", self.openai_key)
        
        self.default_model = QComboBox()
        self.default_model.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"])
        self.default_model.setCurrentText("gpt-4o")
        self.default_model.currentTextChanged.connect(self._on_setting_changed)
        openai_layout.addRow("Default model:", self.default_model)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 8000)
        self.max_tokens.setValue(2000)
        self.max_tokens.valueChanged.connect(self._on_setting_changed)
        openai_layout.addRow("Max tokens:", self.max_tokens)
        
        layout.addWidget(openai_group)
        
        # ChatGPT settings
        chatgpt_group = QGroupBox("ChatGPT Scraper")
        chatgpt_layout = QFormLayout(chatgpt_group)
        
        # Add info label about environment variables
        info_label = QLabel("Note: ChatGPT credentials are loaded from environment variables (CHATGPT_USERNAME, CHATGPT_PASSWORD)")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        chatgpt_layout.addRow(info_label)
        
        self.chatgpt_username = QLineEdit()
        self.chatgpt_username.setPlaceholderText("ChatGPT username/email (from CHATGPT_USERNAME env var)")
        self.chatgpt_username.setReadOnly(True)
        self.chatgpt_username.setStyleSheet("background-color: #f0f0f0;")
        chatgpt_layout.addRow("Username:", self.chatgpt_username)
        
        self.chatgpt_password = QLineEdit()
        self.chatgpt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.chatgpt_password.setPlaceholderText("ChatGPT password (from CHATGPT_PASSWORD env var)")
        self.chatgpt_password.setReadOnly(True)
        self.chatgpt_password.setStyleSheet("background-color: #f0f0f0;")
        chatgpt_layout.addRow("Password:", self.chatgpt_password)
        
        self.headless_mode = QCheckBox("Run browser in headless mode")
        self.headless_mode.setChecked(True)
        self.headless_mode.toggled.connect(self._on_setting_changed)
        chatgpt_layout.addRow("Headless mode:", self.headless_mode)
        
        layout.addWidget(chatgpt_group)
        layout.addStretch()
        
        # Load environment variables
        self._load_env_credentials()
    
    def _load_env_credentials(self):
        """Load credentials from environment variables."""
        username = os.getenv('CHATGPT_USERNAME', '')
        password = os.getenv('CHATGPT_PASSWORD', '')
        
        if username:
            self.chatgpt_username.setText(username)
            self.chatgpt_username.setToolTip(f"Loaded from CHATGPT_USERNAME environment variable")
        else:
            self.chatgpt_username.setText("")
            self.chatgpt_username.setToolTip("CHATGPT_USERNAME environment variable not set")
        
        if password:
            self.chatgpt_password.setText("••••••••")  # Show dots instead of actual password
            self.chatgpt_password.setToolTip("Password loaded from CHATGPT_PASSWORD environment variable")
        else:
            self.chatgpt_password.setText("")
            self.chatgpt_password.setToolTip("CHATGPT_PASSWORD environment variable not set")
    
    def _on_setting_changed(self):
        """Emit signal when settings change."""
        self.settings_changed.emit(self.get_settings())
    
    def get_settings(self) -> dict:
        """Get current API settings."""
        return {
            'openai_key': self.openai_key.text(),
            'default_model': self.default_model.currentText(),
            'max_tokens': self.max_tokens.value(),
            'headless_mode': self.headless_mode.isChecked()
        }
    
    def set_settings(self, settings: dict):
        """Set API settings from dictionary."""
        if 'openai_key' in settings:
            self.openai_key.setText(settings['openai_key'])
        if 'default_model' in settings:
            self.default_model.setCurrentText(settings['default_model'])
        if 'max_tokens' in settings:
            self.max_tokens.setValue(settings['max_tokens'])
        if 'headless_mode' in settings:
            self.headless_mode.setChecked(settings['headless_mode'])
        
        # Reload environment credentials
        self._load_env_credentials() 