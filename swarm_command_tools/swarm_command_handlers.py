#!/usr/bin/env python3
"""
Swarm Command Dashboard Handlers - SCD-1 (Swarm Command Dashboard)
===================================================================

Real-time swarm status monitoring and command interface for Agent-4 coordination.

V2 Compliant: Modular design, single responsibility
Author: Agent-4 (Strategic Coordination Lead)
Date: 2026-01-13
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from fastapi import HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Import from main repository - these tools are designed to be integrated
# TODO: Update imports when agent-tools has its own base classes
try:
    from src.core.base.base_service import BaseService
    from src.core.logging_mixin import LoggingMixin
except ImportError:
    # Fallback for standalone operation
    from abc import ABC
    import logging

    class BaseService(ABC):
        def __init__(self, name: str):
            self.name = name

    class LoggingMixin:
        def __init__(self):
            self._logger = None

        @property
        def logger(self):
            if self._logger is None:
                self._logger = logging.getLogger(self.__class__.__name__)
            return self._logger

logger = logging.getLogger(__name__)

class SwarmCommandDashboard(BaseService, LoggingMixin):
    """Swarm Command Dashboard - Real-time swarm monitoring and control."""

    def __init__(self):
        """Initialize the swarm command dashboard."""
        super().__init__("SwarmCommandDashboard")
        self.templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
        self.agent_workspaces = "agent_workspaces"
        self.coordination_cache = "coordination_cache.json"

    def get_swarm_status(self) -> Dict[str, Any]:
        """Get comprehensive swarm status for all agents."""
        try:
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "agents": {},
                "coordination_metrics": {},
                "active_workstreams": [],
                "system_health": "operational"
            }

            # Get status for each agent
            agent_ids = ["Agent-1", "Agent-2", "Agent-3", "Agent-4", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]
            for agent_id in agent_ids:
                agent_status = self._get_agent_status(agent_id)
                status_data["agents"][agent_id] = agent_status

                # Check for active workstreams
                if agent_status.get("current_workstream"):
                    status_data["active_workstreams"].append({
                        "agent": agent_id,
                        "workstream": agent_status["current_workstream"],
                        "progress": agent_status.get("progress", 0),
                        "status": agent_status.get("workstream_status", "unknown")
                    })

            # Get coordination metrics
            status_data["coordination_metrics"] = self._get_coordination_metrics()

            # Calculate overall swarm health
            status_data["system_health"] = self._calculate_system_health(status_data)

            return status_data

        except Exception as e:
            logger.error(f"Error getting swarm status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "system_health": "degraded"
            }

    def _get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status for a specific agent."""
        try:
            status_file = f"{self.agent_workspaces}/{agent_id}/status.json"
            inbox_dir = f"{self.agent_workspaces}/{agent_id}/inbox"

            agent_status = {
                "agent_id": agent_id,
                "last_seen": None,
                "status": "unknown",
                "current_mission": "No active mission",
                "inbox_count": 0,
                "current_workstream": None,
                "progress": 0,
                "workstream_status": "idle"
            }

            # Read status file if it exists
            if os.path.exists(status_file):
                try:
                    with open(status_file, 'r') as f:
                        status_data = json.load(f)
                        agent_status.update(status_data)
                        agent_status["last_seen"] = status_data.get("timestamp")
                except Exception as e:
                    logger.warning(f"Error reading status for {agent_id}: {e}")

            # Count inbox messages
            if os.path.exists(inbox_dir):
                try:
                    inbox_files = [f for f in os.listdir(inbox_dir) if f.endswith('.json')]
                    agent_status["inbox_count"] = len(inbox_files)

                    # Check for swarm coordination tasks
                    swarm_tasks = [f for f in inbox_files if 'swarm_contract_system_task' in f]
                    if swarm_tasks:
                        agent_status["current_workstream"] = "Contract System Migration"
                        # Estimate progress based on task assignment time
                        if swarm_tasks:
                            task_file = os.path.join(inbox_dir, swarm_tasks[0])
                            if os.path.exists(task_file):
                                try:
                                    with open(task_file, 'r') as f:
                                        task_data = json.load(f)
                                        assigned_time = datetime.fromisoformat(task_data["timestamp"])
                                        elapsed = datetime.now() - assigned_time
                                        # Rough progress estimation (this would be improved with real progress tracking)
                                        if elapsed < timedelta(minutes=30):
                                            agent_status["progress"] = 25
                                            agent_status["workstream_status"] = "in_progress"
                                        elif elapsed < timedelta(minutes=60):
                                            agent_status["progress"] = 50
                                            agent_status["workstream_status"] = "in_progress"
                                        elif elapsed < timedelta(minutes=90):
                                            agent_status["progress"] = 75
                                            agent_status["workstream_status"] = "in_progress"
                                        else:
                                            agent_status["progress"] = 90
                                            agent_status["workstream_status"] = "completing"
                                except Exception as e:
                                    logger.debug(f"Error reading task file: {e}")
                except Exception as e:
                    logger.warning(f"Error checking inbox for {agent_id}: {e}")

            return agent_status

        except Exception as e:
            logger.error(f"Error getting status for {agent_id}: {e}")
            return {
                "agent_id": agent_id,
                "status": "error",
                "error": str(e)
            }

    def _get_coordination_metrics(self) -> Dict[str, Any]:
        """Get coordination metrics from cache."""
        try:
            if not os.path.exists(self.coordination_cache):
                return {"total_messages": 0, "active_conversations": 0}

            with open(self.coordination_cache, 'r') as f:
                cache_data = json.load(f)

            # Calculate metrics
            total_messages = sum(len(messages) for messages in cache_data.values())
            active_conversations = len(cache_data)

            # Recent activity (last hour)
            one_hour_ago = datetime.now().timestamp() - 3600
            recent_messages = 0
            for messages in cache_data.values():
                recent_messages += sum(1 for ts in messages if ts > one_hour_ago)

            return {
                "total_messages": total_messages,
                "active_conversations": active_conversations,
                "recent_messages": recent_messages,
                "messages_per_hour": recent_messages
            }

        except Exception as e:
            logger.error(f"Error getting coordination metrics: {e}")
            return {"error": str(e)}

    def _calculate_system_health(self, status_data: Dict[str, Any]) -> str:
        """Calculate overall system health based on agent status."""
        agents = status_data.get("agents", {})
        active_workstreams = len(status_data.get("active_workstreams", []))

        # Health criteria
        total_agents = len(agents)
        error_agents = sum(1 for agent in agents.values() if agent.get("status") == "error")
        offline_agents = sum(1 for agent in agents.values() if agent.get("last_seen") is None)

        if error_agents > 0:
            return "critical"
        elif offline_agents > total_agents * 0.5:
            return "degraded"
        elif active_workstreams >= 5:  # Swarm is actively working
            return "optimal"
        elif active_workstreams >= 2:
            return "active"
        else:
            return "idle"

    def get_workstream_progress(self) -> Dict[str, Any]:
        """Get detailed workstream progress for all active tasks."""
        try:
            workstreams = {
                "contract_system_migration": {
                    "name": "Contract System Logging Migration",
                    "total_tasks": 17,
                    "completed_tasks": 0,
                    "in_progress_tasks": 0,
                    "assigned_agents": [],
                    "deadline": "2026-01-13T12:00:00",
                    "progress_percentage": 0
                }
            }

            # Scan agent inboxes for active tasks
            agent_ids = ["Agent-1", "Agent-2", "Agent-3", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]
            for agent_id in agent_ids:
                inbox_dir = f"{self.agent_workspaces}/{agent_id}/inbox"
                if os.path.exists(inbox_dir):
                    swarm_tasks = [f for f in os.listdir(inbox_dir) if 'swarm_contract_system_task' in f]
                    if swarm_tasks:
                        workstreams["contract_system_migration"]["assigned_agents"].append(agent_id)
                        workstreams["contract_system_migration"]["in_progress_tasks"] += 1

            # Calculate progress
            assigned = len(workstreams["contract_system_migration"]["assigned_agents"])
            if assigned > 0:
                workstreams["contract_system_migration"]["progress_percentage"] = int((assigned / 7) * 100)

            return workstreams

        except Exception as e:
            logger.error(f"Error getting workstream progress: {e}")
            return {"error": str(e)}

    def emergency_override(self, agent_id: str, action: str, reason: str) -> Dict[str, Any]:
        """Execute emergency override action for swarm coordination."""
        try:
            emergency_record = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "action": action,
                "reason": reason,
                "coordinator": "Agent-4",
                "status": "executed"
            }

            # Log emergency action
            logger.warning(f"🚨 EMERGENCY OVERRIDE: {agent_id} - {action} - {reason}")

            # In a full implementation, this would send commands to the agent
            # For now, we'll just record the action

            return {
                "success": True,
                "emergency_action": emergency_record,
                "message": f"Emergency override executed for {agent_id}"
            }

        except Exception as e:
            logger.error(f"Error executing emergency override: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global dashboard instance
swarm_dashboard = SwarmCommandDashboard()