"""
Settings Panel for Thea GUI
Manages application settings and configuration.
"""

import logging
from gui.debug_handler import debug_button
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict
import os

logger = logging.getLogger(__name__)

from gui.settings.general_settings import GeneralSettingsWidget
from gui.settings.api_settings import APISettingsWidget
from gui.settings.memory_settings import MemorySettingsWidget
from gui.settings.accessibility_settings import AccessibilitySettingsWidget
from dreamscape.core.settings_manager import settings_manager

class SettingsPanel(QWidget):
    """Panel for managing application settings."""
    
    # Signals
    settings_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {}
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        self.create_header(layout)
        
        # Settings tabs
        self.create_settings_tabs(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
    
    @debug_button("create_header", "Settings Panel")
    def create_header(self, layout):
        """Create panel header using shared components."""
        try:
            from gui.components.shared_components import SharedComponents
            
            components = SharedComponents()
            
            # Create header with title and icon (no emoji)
            header_widget = components.create_panel_header(
                title="Settings",
                icon="",
                refresh_callback=self.refresh_data
            )
            layout.addWidget(header_widget)
            
        except Exception as e:
            logger.error(f"Error creating panel header: {e}")
            # Fallback: create simple header (no emoji)
            header = QLabel("Settings")
            header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)

    @debug_button("refresh_data", "Settings Panel")
    def refresh_data(self):
        """Refresh settings data."""
        try:
            logger.info("Refreshing settings data")
            self.load_settings()
            logger.info("Settings data refresh completed")
        except Exception as e:
            logger.error(f"Error refreshing settings data: {e}")

    def create_settings_tabs(self, layout):
        """Create settings tabs."""
        try:
            # Create tab widget
            self.tab_widget = QTabWidget()
            
            # Add settings tabs
            self.general_settings = GeneralSettingsWidget()
            self.api_settings = APISettingsWidget()
            self.memory_settings = MemorySettingsWidget()
            self.accessibility_settings = AccessibilitySettingsWidget()
            
            self.tab_widget.addTab(self.general_settings, "General")
            self.tab_widget.addTab(self.api_settings, "API")
            self.tab_widget.addTab(self.memory_settings, "Memory")
            self.tab_widget.addTab(self.accessibility_settings, "Accessibility")
            
            layout.addWidget(self.tab_widget)
            
        except Exception as e:
            logger.error(f"Error creating settings tabs: {e}")
            # Fallback: create simple settings widget
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)
            fallback_label = QLabel("Settings not available")
            fallback_layout.addWidget(fallback_label)
            layout.addWidget(fallback_widget)

    def create_action_buttons(self, layout):
        """Create action buttons."""
        try:
            # Create button layout
            button_layout = QHBoxLayout()
            
            # Save button
            self.save_btn = QPushButton("Save Settings")
            self.save_btn.clicked.connect(self.save_settings)
            button_layout.addWidget(self.save_btn)
            
            # Reset button
            self.reset_btn = QPushButton("Reset to Defaults")
            self.reset_btn.clicked.connect(self.reset_settings)
            button_layout.addWidget(self.reset_btn)
            
            # Test Discord button
            self.test_discord_btn = QPushButton("Test Discord")
            self.test_discord_btn.clicked.connect(self.test_discord_connection)
            button_layout.addWidget(self.test_discord_btn)
            
            layout.addLayout(button_layout)
            
        except Exception as e:
            logger.error(f"Error creating action buttons: {e}")

    def _on_settings_changed(self):
        """Handle settings changes from child widgets."""
        # This could be used to track unsaved changes
        pass

    @debug_button("load_settings", "Settings Panel")
    def load_settings(self):
        """Load settings from configuration."""
        from dreamscape.core.settings_manager import settings_manager
        # Base defaults
        defaults = {
            'general': {
                'auto_save': True,
                'auto_refresh': True,
                'refresh_interval': 300,
                'theme': 'Light',
                'font_size': 12
            },
            'api': {
                'openai_key': '',
                'default_model': 'gpt-4o',
                'max_tokens': 2000,
                'headless_mode': True
            },
            'memory': {
                'db_path': 'dreamos_memory.db',
                'backup_enabled': True,
                'backup_interval': 7,
                'auto_index': True,
                'chunk_size': 1000,
                'max_chunks': 100
            },
            'discord': {
                'token': '',
                'enabled': False
            },
            'accessibility': {
                'high_contrast': False
            }
        }

        # Overlay saved flat settings
        saved_flat = settings_manager.get_all_settings()
        for cat, opts in defaults.items():
            for key in opts:
                if key in saved_flat:
                    opts[key] = saved_flat[key]

        self.settings = defaults
        self.apply_settings_to_ui()
    
    def apply_settings_to_ui(self):
        """Apply loaded settings to UI components."""
        try:
            if 'general' in self.settings:
                self.general_settings.set_settings(self.settings['general'])
            if 'api' in self.settings:
                self.api_settings.set_settings(self.settings['api'])
            if 'memory' in self.settings:
                self.memory_settings.set_settings(self.settings['memory'])
            if 'accessibility' in self.settings:
                self.accessibility_settings.set_settings(self.settings['accessibility'])
        except Exception as e:
            logger.error(f"Error applying settings to UI: {e}")
    
    @debug_button("save_settings", "Settings Panel")
    def save_settings(self):
        """Save current settings."""
        try:
            # Collect settings from all widgets
            self.settings = {
                'general': self.general_settings.get_settings(),
                'api': self.api_settings.get_settings(),
                'memory': self.memory_settings.get_settings(),
                'accessibility': self.accessibility_settings.get_settings()
            }
            
            # Persist general settings via shared settings_manager so they survive restarts
            from dreamscape.core.settings_manager import settings_manager

            # Flatten keys for persistence
            flat: dict[str, any] = {}
            for cat, opts in self.settings.items():
                flat.update(opts)

            settings_manager.update_settings(flat)
            
            # Emit signal with saved settings
            self.settings_saved.emit(self.settings)
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    @debug_button("reset_settings", "Settings Panel")
    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.load_settings()
    
    @debug_button("test_discord_connection", "Settings Panel")
    def test_discord_connection(self):
        """Test Discord bot connection."""
        # Get token from environment or settings
        token = os.getenv('DISCORD_BOT_TOKEN', '')
        if not token:
            QMessageBox.warning(self, "Warning", "No Discord bot token found in environment variables.")
            return
        
        try:
            import requests
            import json
            
            # Test Discord API connection
            headers = {
                'Authorization': f'Bot {token}',
                'Content-Type': 'application/json'
            }
            
            # Test 1: Get bot user info
            response = requests.get('https://discord.com/api/v10/users/@me', headers=headers, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                bot_name = bot_info.get('username', 'Unknown')
                bot_id = bot_info.get('id', 'Unknown')
                
                # Test 2: Get bot's guilds (servers)
                guilds_response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=headers, timeout=10)
                
                if guilds_response.status_code == 200:
                    guilds = guilds_response.json()
                    guild_count = len(guilds)
                    
                    # Show success message with bot info
                    message = f"Discord connection successful!\n\n"
                    message += f"Bot Name: {bot_name}\n"
                    message += f"Bot ID: {bot_id}\n"
                    message += f"Connected Servers: {guild_count}\n\n"
                    
                    if guilds:
                        message += "Connected to servers:\n"
                        for guild in guilds[:5]:  # Show first 5 servers
                            message += f"• {guild.get('name', 'Unknown')}\n"
                        if len(guilds) > 5:
                            message += f"... and {len(guilds) - 5} more"
                    
                    QMessageBox.information(self, "Connection Test", message)
                    
                else:
                    QMessageBox.warning(self, "Connection Test", 
                                      f"Bot token is valid but cannot access guilds.\n"
                                      f"Status: {guilds_response.status_code}\n"
                                      f"Make sure the bot has proper permissions.")
                    
            elif response.status_code == 401:
                QMessageBox.critical(self, "Connection Test", 
                                   "Invalid bot token.\n"
                                   "Please check your Discord bot token and try again.")
                
            elif response.status_code == 403:
                QMessageBox.critical(self, "Connection Test", 
                                   "Bot token lacks required permissions.\n"
                                   "Make sure the bot has the 'bot' scope enabled.")
                
            else:
                QMessageBox.critical(self, "Connection Test", 
                                   f"Connection failed.\n"
                                   f"Status: {response.status_code}\n"
                                   f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "Connection Test", 
                               "Connection timeout.\n"
                               "Please check your internet connection and try again.")
            
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Connection Test", 
                               "Network connection error.\n"
                               "Please check your internet connection and try again.")
            
        except ImportError:
            QMessageBox.warning(self, "Missing Dependency", 
                              "Discord connection test requires 'requests' library.\n"
                              "Install with: pip install requests")
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Test", 
                               f"Unexpected error during connection test:\n{str(e)}")
    
    def get_settings(self) -> Dict:
        """Get current settings."""
        return self.settings 