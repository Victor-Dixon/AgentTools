"""Discord Commander toolbelt — Discord ↔ agent command bridge."""

from __future__ import annotations
# C2A_SELF_GAS_ROOT_DEFAULTS_041
# Canonical desktop roots for C2A/S2A hard onboard and self-gas routes.
import os as _c2a_self_gas_env_041
_c2a_self_gas_env_041.environ["DREAMVAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["DREAMOS_VAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["VAULT_ROOT"] = r"D:\DreamVault"
_c2a_self_gas_env_041.environ["AGENT_CELLPHONE_ROOT"] = r"D:\repos\Agent_Cellphone"
_c2a_self_gas_env_041.environ.setdefault("ALLOW_LIVE_CURSOR_INJECTION", "1")
_c2a_self_gas_env_041.environ.setdefault("DEFAULT_MODE", "pyautogui")
_c2a_self_gas_env_041.environ.setdefault("COORDINATE_MODE", "4-agent-1monitor")
_c2a_self_gas_env_041.environ.setdefault("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor")
_c2a_self_gas_env_041.environ.setdefault("DREAMOS_ALLOW_PYAUTOGUI_FAILSAFE_OVERRIDE", "1")

# D2A_AGENTTOOLS_BRIDGE_ENV_DEFAULTS_035
# Canonical visible-session D2A delivery defaults.
import os as _dreamos_d2a_env_035
_dreamos_d2a_env_035.environ["AGENT_CELLPHONE_ROOT"] = r"D:\repos\Agent_Cellphone"
_dreamos_d2a_env_035.environ.setdefault("ALLOW_LIVE_CURSOR_INJECTION", "1")
_dreamos_d2a_env_035.environ.setdefault("DEFAULT_MODE", "pyautogui")
_dreamos_d2a_env_035.environ.setdefault("COORDINATE_MODE", "4-agent-1monitor")
_dreamos_d2a_env_035.environ.setdefault("AGENT_GAS_LAYOUT_MODE", "4-agent-1monitor")
_dreamos_d2a_env_035.environ.setdefault("DREAMOS_ALLOW_PYAUTOGUI_FAILSAFE_OVERRIDE", "1")
_dreamos_d2a_env_035.environ.setdefault("PYTHONPATH", r"D:\agent-tools\src;D:\DreamVault\src")

from .discord_embeds import (
    create_agent_status_embed,
    create_coordination_embed,
    create_devlog_embed,
    create_error_embed,
)
from .utils.message_chunking import chunk_message, chunk_field_value

__all__ = [
    "__version__",
    "create_agent_status_embed",
    "create_coordination_embed",
    "create_devlog_embed",
    "create_error_embed",
    "chunk_message",
    "chunk_field_value",
]

__version__ = "0.2.0-slice"
