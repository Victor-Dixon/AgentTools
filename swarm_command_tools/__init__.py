"""
Swarm Command Tools - Agent-4 Strategic Coordination Tools
==========================================================

This package contains the AI-powered swarm coordination tools for Agent-4:

- Swarm Command Dashboard (SCD-1): Real-time swarm monitoring
- Automated Task Distributor (ATD-1): AI-powered task assignment
- Swarm Intelligence Aggregator (SIA-1): Cross-agent knowledge sharing

These tools transform Agent-4 from overwhelmed coordinator to empowered quarterback.

Author: Agent-4 (Strategic Coordination Lead)
Date: 2026-01-13
"""

__version__ = "1.0.0"
__author__ = "Agent-4 Strategic Coordination Lead"

# Import main components for easy access
from .swarm_command_handlers import swarm_dashboard
from .automated_task_distributor import task_distributor
from .swarm_intelligence_aggregator import intelligence_aggregator

__all__ = [
    "swarm_dashboard",
    "task_distributor",
    "intelligence_aggregator"
]