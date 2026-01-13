"""
Voice Modeling Panel - Refactored Modular Version
=================================================

A streamlined version of voice_modeling_panel.py (~900 lines) using the
AIStudioBase and DataPanelBase for voice model management.
"""

import logging
from PyQt6.QtWidgets import QTabWidget
from typing import Dict, Any

from gui.base.ai_studio_base import AIStudioBase
from gui.base.data_panel_base import DataPanelBase

logger = logging.getLogger(__name__)


class VoiceModelingPanelRefactored(AIStudioBase, DataPanelBase):
    """Refactored Voice Modeling Panel using base classes."""

    def __init__(self):
        AIStudioBase.__init__(self, title="🗣️ Voice Modeling", description="Voice profile creation and training")
        DataPanelBase.__init__(self, title="Voice Data", description="Training data for voices")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_training_tab("Voice Training"), "Training")
        self.tab_widget.addTab(self.create_data_tab("Voice Data"), "Data")
        self.tab_widget.addTab(self.create_chat_tab("Voice Testing"), "Testing")
        self.layout().addWidget(self.tab_widget)

    def get_panel_summary(self) -> Dict[str, Any]:
        return {
            "voices": len(self.ai_models),
            "records": len(self.data_records),
        }
