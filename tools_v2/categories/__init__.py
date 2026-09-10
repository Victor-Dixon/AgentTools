"""Lazy namespace for AgentTools v2 tool categories.

Importing one registry adapter must not import every optional category and its
third-party dependencies. Category modules remain available through normal
attribute/module imports and are loaded only when requested.
"""

from __future__ import annotations

import importlib

_MODULES = (
    "agent_activity_tools",
    "agent_ops_tools",
    "analysis_tools",
    "autonomous_workflow_tools",
    "bi_tools",
    "captain_coordination_tools",
    "captain_tools",
    "captain_tools_advanced",
    "captain_tools_architecture",
    "captain_tools_coordination",
    "captain_tools_core",
    "captain_tools_extension",
    "captain_tools_messaging",
    "captain_tools_monitoring",
    "captain_tools_utilities",
    "captain_tools_validation",
    "communication_tools",
    "compliance_tools",
    "config_tools",
    "coordination_tools",
    "dashboard_tools",
    "debate_tools",
    "discord_profile_tools",
    "discord_tools",
    "discord_webhook_tools",
    "docs_tools",
    "github_consolidation_tools",
    "health_tools",
    "import_fix_tools",
    "infrastructure_audit_tools",
    "infrastructure_tools",
    "infrastructure_utility_tools",
    "infrastructure_workspace_tools",
    "integration_tools",
    "intelligent_mission_advisor",
    "intelligent_mission_advisor_adapter",
    "intelligent_mission_advisor_analysis",
    "intelligent_mission_advisor_guidance",
    "memory_safety_adapters",
    "memory_safety_tools",
    "message_analytics_tools",
    "message_history_tools",
    "message_task_tools",
    "messaging_tools",
    "mission_calculator",
    "observability_tools",
    "onboarding_tools",
    "oss_tools",
    "proposal_tools",
    "queue_monitor_tools",
    "refactoring_tools",
    "repo_tools",
    "session_tools",
    "ssot_validation_tools",
    "swarm_brain_tools",
    "swarm_consciousness",
    "swarm_mission_control",
    "swarm_state_reader",
    "system_tools",
    "test_generation_tools",
    "testing_tools",
    "v2_tools",
    "validation_tools",
    "vector_tools",
    "web_tools",
    "workflow_tools",
)

__all__ = list(_MODULES)


def __getattr__(name: str):
    """Load a category module only when it is actually requested."""
    if name in _MODULES:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
