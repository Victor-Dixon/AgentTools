from enum import Enum

class RefreshType(Enum):
    """Types of refresh operations"""
    CONVERSATIONS = "conversations"
    ANALYTICS = "analytics"
    TEMPLATES = "templates"
    MEMORY = "memory"
    MMORPG = "mmorpg"
    SETTINGS = "settings"
    UI = "ui"
    ALL = "all"

class RefreshPriority(Enum):
    """Refresh priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4 