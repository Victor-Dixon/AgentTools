"""
Discord Embeds — promoted slice from Agent_Cellphone_V2 Commander.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def create_devlog_embed(devlog_data: dict[str, Any]) -> dict[str, Any]:
    colors = {
        "general": 0x3498DB,
        "cleanup": 0xE74C3C,
        "consolidation": 0x9B59B6,
        "coordination": 0x1ABC9C,
        "testing": 0xF39C12,
        "deployment": 0x27AE60,
    }
    return {
        "title": f"📋 {devlog_data.get('title', 'DevLog Update')}",
        "description": devlog_data.get("description", "")[:2000],
        "color": colors.get(devlog_data.get("category", "general"), 0x3498DB),
        "fields": [
            {"name": "Category", "value": devlog_data.get("category", "general").title(), "inline": True},
            {"name": "Agent", "value": devlog_data.get("agent", "Unknown"), "inline": True},
            {
                "name": "Timestamp",
                "value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": True,
            },
        ],
        "footer": {"text": "Dream.OS Discord Commander"},
    }


def create_agent_status_embed(agent_status: dict[str, Any]) -> dict[str, Any]:
    status_colors = {"active": 0x27AE60, "idle": 0xF39C12, "error": 0xE74C3C, "offline": 0x95A5A6}
    return {
        "title": f"🤖 Agent Status — {agent_status.get('agent_id', 'Unknown')}",
        "color": status_colors.get(agent_status.get("status", "unknown"), 0x3498DB),
        "fields": [
            {"name": "Status", "value": str(agent_status.get("status", "unknown")).title(), "inline": True},
            {"name": "Last Activity", "value": agent_status.get("last_activity", "Unknown"), "inline": True},
            {
                "name": "Timestamp",
                "value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": True,
            },
        ],
        "footer": {"text": "Dream.OS Status Monitor"},
    }


def create_coordination_embed(coordination_data: dict[str, Any]) -> dict[str, Any]:
    priority_colors = {"LOW": 0x95A5A6, "NORMAL": 0x3498DB, "HIGH": 0xF39C12, "CRITICAL": 0xE74C3C}
    return {
        "title": f"🐝 Swarm Coordination — {coordination_data.get('mission', 'Update')}",
        "color": priority_colors.get(coordination_data.get("priority", "NORMAL"), 0x3498DB),
        "fields": [
            {"name": "Mission", "value": coordination_data.get("mission", "Unknown"), "inline": True},
            {"name": "Priority", "value": coordination_data.get("priority", "NORMAL"), "inline": True},
            {"name": "Agents Involved", "value": str(coordination_data.get("agents", "All")), "inline": True},
        ],
        "footer": {"text": "Dream.OS Coordination"},
    }


def create_error_embed(error_data: dict[str, Any]) -> dict[str, Any]:
    severity_colors = {"critical": 0xE74C3C, "high": 0xF39C12, "medium": 0x3498DB, "low": 0x95A5A6}
    error_details = str(error_data.get("error", "No details"))[:500]
    return {
        "title": f"❌ Error — {error_data.get('title', 'Error')}",
        "description": str(error_data.get("description", ""))[:2000],
        "color": severity_colors.get(error_data.get("severity", "medium"), 0x3498DB),
        "fields": [
            {"name": "Severity", "value": str(error_data.get("severity", "medium")).title(), "inline": True},
            {"name": "Component", "value": error_data.get("component", "Unknown"), "inline": True},
            {"name": "Agent", "value": error_data.get("agent", "System"), "inline": True},
            {"name": "Error Details", "value": f"```\n{error_details}\n```", "inline": False},
        ],
        "footer": {"text": "Dream.OS Error Monitor"},
        "timestamp": error_data.get("timestamp"),
    }


__all__ = [
    "create_agent_status_embed",
    "create_coordination_embed",
    "create_devlog_embed",
    "create_error_embed",
]
