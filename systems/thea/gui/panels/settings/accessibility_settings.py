#!/usr/bin/env python3
"""Accessibility Settings Panel Component."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox, QCheckBox
)
from PyQt6.QtCore import pyqtSignal

class AccessibilitySettingsWidget(QWidget):
    """Widget for accessibility configuration."""

    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        group = QGroupBox("Accessibility Options")
        form = QFormLayout(group)

        self.high_contrast = QCheckBox("Enable high contrast mode")
        self.high_contrast.toggled.connect(self._on_setting_changed)
        form.addRow(self.high_contrast)

        layout.addWidget(group)
        layout.addStretch()

    def _on_setting_changed(self):
        self.settings_changed.emit(self.get_settings())

    def get_settings(self) -> dict:
        return {
            'high_contrast': self.high_contrast.isChecked(),
        }

    def set_settings(self, settings: dict):
        if 'high_contrast' in settings:
            self.high_contrast.setChecked(settings['high_contrast'])
