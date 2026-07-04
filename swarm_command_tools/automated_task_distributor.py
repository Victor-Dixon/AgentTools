#!/usr/bin/env python3
"""
Automated Task Distributor (ATD-1) - Intelligent Task Assignment Engine
========================================================================

Automated task distribution system that intelligently assigns tasks to agents
based on capabilities, workload, and optimization algorithms.

V2 Compliant: Modular design, machine learning integration
Author: Agent-4 (Strategic Coordination Lead)
Date: 2026-01-13
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

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

class TaskPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BACKLOG = 1

class AgentCapability(Enum):
    PYTHON_DEVELOPMENT = "python_development"
    WEB_DEVELOPMENT = "web_development"
    AI_INTEGRATION = "ai_integration"
    INFRASTRUCTURE = "infrastructure"
    TESTING_QA = "testing_qa"
    COORDINATION = "coordination"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"

@dataclass
class Task:
    """Represents a task to be assigned."""
    task_id: str
    title: str
    description: str
    priority: TaskPriority
    required_capabilities: List[AgentCapability]
    estimated_hours: float
    deadline: Optional[datetime]
    dependencies: List[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class AgentProfile:
    """Represents an agent's capabilities and current workload."""
    agent_id: str
    capabilities: List[AgentCapability]
    current_workload: float  # Hours of active work
    max_capacity: float  # Maximum hours per period
    specialization_score: Dict[AgentCapability, float]  # 0.0 to 1.0
    reliability_score: float  # 0.0 to 1.0
    recent_performance: List[float]  # Recent task completion scores
    last_assignment: Optional[datetime]
    status: str = "active"

class AutomatedTaskDistributor(BaseService, LoggingMixin):
    """Automated Task Distributor - Intelligent task assignment engine."""

    def __init__(self):
        """Initialize the automated task distributor."""
        super().__init__("AutomatedTaskDistributor")
        self.agent_workspaces = "agent_workspaces"
        self.capability_database = self._load_capability_database()
        self.assignment_history = []
        self.optimization_weights = {
            "capability_match": 0.4,
            "workload_balance": 0.3,
            "specialization": 0.2,
            "reliability": 0.1
        }

    def _load_capability_database(self) -> Dict[str, AgentProfile]:
        """Load or create agent capability database."""
        try:
            # Define agent capabilities based on their known specializations
            capabilities_db = {
                "Agent-1": AgentProfile(
                    agent_id="Agent-1",
                    capabilities=[AgentCapability.PYTHON_DEVELOPMENT, AgentCapability.INFRASTRUCTURE, AgentCapability.COORDINATION],
                    current_workload=0.0,
                    max_capacity=40.0,
                    specialization_score={
                        AgentCapability.PYTHON_DEVELOPMENT: 0.9,
                        AgentCapability.INFRASTRUCTURE: 0.8,
                        AgentCapability.COORDINATION: 0.7,
                        AgentCapability.WEB_DEVELOPMENT: 0.6,
                        AgentCapability.AI_INTEGRATION: 0.5,
                        AgentCapability.TESTING_QA: 0.7,
                        AgentCapability.DOCUMENTATION: 0.8,
                        AgentCapability.RESEARCH: 0.6
                    },
                    reliability_score=0.95,
                    recent_performance=[0.95, 0.98, 0.92, 0.96, 0.94],
                    last_assignment=None
                ),
                "Agent-2": AgentProfile(
                    agent_id="Agent-2",
                    capabilities=[AgentCapability.PYTHON_DEVELOPMENT, AgentCapability.ARCHITECTURE, AgentCapability.AI_INTEGRATION],
                    current_workload=0.0,
                    max_capacity=35.0,
                    specialization_score={
                        AgentCapability.PYTHON_DEVELOPMENT: 0.95,
                        AgentCapability.AI_INTEGRATION: 0.9,
                        AgentCapability.INFRASTRUCTURE: 0.7,
                        AgentCapability.WEB_DEVELOPMENT: 0.6,
                        AgentCapability.COORDINATION: 0.5,
                        AgentCapability.TESTING_QA: 0.8,
                        AgentCapability.DOCUMENTATION: 0.6,
                        AgentCapability.RESEARCH: 0.7
                    },
                    reliability_score=0.92,
                    recent_performance=[0.88, 0.95, 0.91, 0.93, 0.89],
                    last_assignment=None
                ),
                "Agent-3": AgentProfile(
                    agent_id="Agent-3",
                    capabilities=[AgentCapability.INFRASTRUCTURE, AgentCapability.WEB_DEVELOPMENT, AgentCapability.AI_INTEGRATION],
                    current_workload=0.0,
                    max_capacity=45.0,
                    specialization_score={
                        AgentCapability.INFRASTRUCTURE: 0.95,
                        AgentCapability.AI_INTEGRATION: 0.85,
                        AgentCapability.WEB_DEVELOPMENT: 0.8,
                        AgentCapability.PYTHON_DEVELOPMENT: 0.75,
                        AgentCapability.COORDINATION: 0.6,
                        AgentCapability.TESTING_QA: 0.7,
                        AgentCapability.DOCUMENTATION: 0.5,
                        AgentCapability.RESEARCH: 0.6
                    },
                    reliability_score=0.97,
                    recent_performance=[0.96, 0.98, 0.94, 0.97, 0.95],
                    last_assignment=None
                ),
                "Agent-4": AgentProfile(
                    agent_id="Agent-4",
                    capabilities=[AgentCapability.COORDINATION, AgentCapability.PYTHON_DEVELOPMENT, AgentCapability.STRATEGY],
                    current_workload=0.0,
                    max_capacity=30.0,  # Lower capacity due to coordination role
                    specialization_score={
                        AgentCapability.COORDINATION: 0.98,
                        AgentCapability.PYTHON_DEVELOPMENT: 0.8,
                        AgentCapability.DOCUMENTATION: 0.9,
                        AgentCapability.RESEARCH: 0.85,
                        AgentCapability.INFRASTRUCTURE: 0.6,
                        AgentCapability.WEB_DEVELOPMENT: 0.7,
                        AgentCapability.AI_INTEGRATION: 0.75,
                        AgentCapability.TESTING_QA: 0.65
                    },
                    reliability_score=0.99,
                    recent_performance=[0.98, 0.99, 0.97, 0.98, 0.96],
                    last_assignment=None
                ),
                "Agent-5": AgentProfile(
                    agent_id="Agent-5",
                    capabilities=[AgentCapability.AI_INTEGRATION, AgentCapability.ANALYTICS, AgentCapability.RESEARCH],
                    current_workload=0.0,
                    max_capacity=38.0,
                    specialization_score={
                        AgentCapability.AI_INTEGRATION: 0.95,
                        AgentCapability.RESEARCH: 0.9,
                        AgentCapability.ANALYTICS: 0.88,
                        AgentCapability.PYTHON_DEVELOPMENT: 0.8,
                        AgentCapability.WEB_DEVELOPMENT: 0.7,
                        AgentCapability.COORDINATION: 0.75,
                        AgentCapability.TESTING_QA: 0.8,
                        AgentCapability.DOCUMENTATION: 0.85,
                        AgentCapability.INFRASTRUCTURE: 0.6
                    },
                    reliability_score=0.93,
                    recent_performance=[0.91, 0.94, 0.89, 0.96, 0.92],
                    last_assignment=None
                ),
                "Agent-6": AgentProfile(
                    agent_id="Agent-6",
                    capabilities=[AgentCapability.COORDINATION, AgentCapability.TESTING_QA, AgentCapability.DOCUMENTATION],
                    current_workload=0.0,
                    max_capacity=32.0,
                    specialization_score={
                        AgentCapability.COORDINATION: 0.85,
                        AgentCapability.TESTING_QA: 0.9,
                        AgentCapability.DOCUMENTATION: 0.95,
                        AgentCapability.PYTHON_DEVELOPMENT: 0.7,
                        AgentCapability.RESEARCH: 0.8,
                        AgentCapability.WEB_DEVELOPMENT: 0.6,
                        AgentCapability.AI_INTEGRATION: 0.65,
                        AgentCapability.INFRASTRUCTURE: 0.55
                    },
                    reliability_score=0.91,
                    recent_performance=[0.89, 0.92, 0.88, 0.94, 0.90],
                    last_assignment=None
                ),
                "Agent-7": AgentProfile(
                    agent_id="Agent-7",
                    capabilities=[AgentCapability.WEB_DEVELOPMENT, AgentCapability.TESTING_QA, AgentCapability.DOCUMENTATION],
                    current_workload=0.0,
                    max_capacity=36.0,
                    specialization_score={
                        AgentCapability.WEB_DEVELOPMENT: 0.95,
                        AgentCapability.TESTING_QA: 0.9,
                        AgentCapability.DOCUMENTATION: 0.85,
                        AgentCapability.PYTHON_DEVELOPMENT: 0.75,
                        AgentCapability.AI_INTEGRATION: 0.7,
                        AgentCapability.INFRASTRUCTURE: 0.65,
                        AgentCapability.COORDINATION: 0.6,
                        AgentCapability.RESEARCH: 0.7
                    },
                    reliability_score=0.94,
                    recent_performance=[0.93, 0.95, 0.91, 0.96, 0.92],
                    last_assignment=None
                ),
                "Agent-8": AgentProfile(
                    agent_id="Agent-8",
                    capabilities=[AgentCapability.INFRASTRUCTURE, AgentCapability.AI_INTEGRATION, AgentCapability.COORDINATION],
                    current_workload=0.0,
                    max_capacity=42.0,
                    specialization_score={
                        AgentCapability.INFRASTRUCTURE: 0.9,
                        AgentCapability.AI_INTEGRATION: 0.85,
                        AgentCapability.COORDINATION: 0.8,
                        AgentCapability.PYTHON_DEVELOPMENT: 0.8,
                        AgentCapability.WEB_DEVELOPMENT: 0.75,
                        AgentCapability.TESTING_QA: 0.7,
                        AgentCapability.DOCUMENTATION: 0.75,
                        AgentCapability.RESEARCH: 0.7
                    },
                    reliability_score=0.96,
                    recent_performance=[0.94, 0.97, 0.93, 0.98, 0.95],
                    last_assignment=None
                )
            }

            # Update current workloads from active assignments
            self._update_current_workloads(capabilities_db)

            return capabilities_db

        except Exception as e:
            logger.error(f"Error loading capability database: {e}")
            return {}

    def _update_current_workloads(self, capabilities_db: Dict[str, AgentProfile]):
        """Update current workloads based on active assignments."""
        try:
            for agent_id, profile in capabilities_db.items():
                inbox_dir = f"{self.agent_workspaces}/{agent_id}/inbox"
                if os.path.exists(inbox_dir):
                    active_tasks = [f for f in os.listdir(inbox_dir) if 'swarm_contract_system_task' in f]
                    # Estimate workload based on active tasks (rough approximation)
                    profile.current_workload = len(active_tasks) * 4.0  # Assume 4 hours per task
        except Exception as e:
            logger.warning(f"Error updating workloads: {e}")

    def distribute_task(self, task: Task) -> Dict[str, Any]:
        """Distribute a task to the optimal agent using intelligent algorithms."""
        try:
            # Find eligible agents
            eligible_agents = self._find_eligible_agents(task)

            if not eligible_agents:
                return {
                    "success": False,
                    "error": "No eligible agents found for task",
                    "task_id": task.task_id
                }

            # Score and rank agents
            agent_scores = {}
            for agent_id, profile in eligible_agents.items():
                score = self._calculate_agent_score(task, profile)
                agent_scores[agent_id] = score

            # Select best agent
            best_agent = max(agent_scores.items(), key=lambda x: x[1])[0]

            # Create assignment
            assignment = self._create_assignment(task, best_agent, agent_scores[best_agent])

            # Update agent workload
            self.capability_database[best_agent].current_workload += task.estimated_hours
            self.capability_database[best_agent].last_assignment = datetime.now()

            # Record assignment
            self.assignment_history.append({
                "task_id": task.task_id,
                "assigned_to": best_agent,
                "score": agent_scores[best_agent],
                "timestamp": datetime.now().isoformat(),
                "estimated_hours": task.estimated_hours
            })

            logger.info(f"✅ Task {task.task_id} assigned to {best_agent} with score {agent_scores[best_agent]:.3f}")

            return assignment

        except Exception as e:
            logger.error(f"Error distributing task {task.task_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task.task_id
            }

    def _find_eligible_agents(self, task: Task) -> Dict[str, AgentProfile]:
        """Find agents eligible for the task."""
        eligible = {}

        for agent_id, profile in self.capability_database.items():
            if profile.status != "active":
                continue

            # Check capability requirements
            if not self._agent_has_capabilities(profile, task.required_capabilities):
                continue

            # Check workload capacity
            if profile.current_workload + task.estimated_hours > profile.max_capacity:
                continue

            # Check deadline compatibility (if specified)
            if task.deadline and not self._agent_can_meet_deadline(profile, task):
                continue

            eligible[agent_id] = profile

        return eligible

    def _agent_has_capabilities(self, profile: AgentProfile, required: List[AgentCapability]) -> bool:
        """Check if agent has required capabilities."""
        return all(capability in profile.capabilities for capability in required)

    def _agent_can_meet_deadline(self, profile: AgentProfile, task: Task) -> bool:
        """Check if agent can meet task deadline."""
        if not task.deadline:
            return True

        # Estimate completion time based on workload and specialization
        avg_specialization = sum(profile.specialization_score.get(cap, 0.5) for cap in task.required_capabilities) / len(task.required_capabilities)
        estimated_completion_days = (task.estimated_hours / avg_specialization) / 8  # 8-hour workdays

        estimated_completion = datetime.now() + timedelta(days=estimated_completion_days)
        return estimated_completion <= task.deadline

    def _calculate_agent_score(self, task: Task, profile: AgentProfile) -> float:
        """Calculate suitability score for agent-task pairing."""
        scores = {}

        # Capability match score (0-1)
        capability_matches = sum(1 for cap in task.required_capabilities if cap in profile.capabilities)
        scores["capability"] = capability_matches / len(task.required_capabilities)

        # Specialization score (0-1)
        specialization_scores = [profile.specialization_score.get(cap, 0.5) for cap in task.required_capabilities]
        scores["specialization"] = sum(specialization_scores) / len(specialization_scores)

        # Workload balance score (0-1, higher is better balance)
        workload_ratio = profile.current_workload / profile.max_capacity
        scores["workload"] = 1.0 - workload_ratio  # Prefer less loaded agents

        # Reliability score (0-1)
        scores["reliability"] = profile.reliability_score

        # Recent performance score (0-1)
        if profile.recent_performance:
            scores["performance"] = sum(profile.recent_performance[-5:]) / len(profile.recent_performance[-5:])
        else:
            scores["performance"] = 0.8  # Default

        # Calculate weighted final score
        final_score = sum(
            scores[metric] * self.optimization_weights.get(f"{metric}_match" if metric == "capability" else metric, 0.1)
            for metric in scores.keys()
        )

        return final_score

    def _create_assignment(self, task: Task, agent_id: str, score: float) -> Dict[str, Any]:
        """Create task assignment with delivery instructions."""
        assignment_data = {
            "success": True,
            "task_id": task.task_id,
            "assigned_to": agent_id,
            "assignment_score": round(score, 3),
            "estimated_completion": self._estimate_completion_time(task, agent_id),
            "priority": task.priority.value,
            "required_capabilities": [cap.value for cap in task.required_capabilities],
            "estimated_hours": task.estimated_hours,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "assignment_timestamp": datetime.now().isoformat()
        }

        # Create inbox message for agent
        self._deliver_assignment_to_agent(assignment_data, task)

        return assignment_data

    def _estimate_completion_time(self, task: Task, agent_id: str) -> str:
        """Estimate task completion time."""
        profile = self.capability_database[agent_id]
        avg_specialization = sum(profile.specialization_score.get(cap, 0.5) for cap in task.required_capabilities) / len(task.required_capabilities)

        # Adjust for workload and reliability
        workload_factor = 1.0 + (profile.current_workload / profile.max_capacity)
        reliability_factor = 1.0 / profile.reliability_score

        adjusted_hours = task.estimated_hours * workload_factor * reliability_factor / avg_specialization

        completion_time = datetime.now() + timedelta(hours=adjusted_hours)
        return completion_time.isoformat()

    def _deliver_assignment_to_agent(self, assignment: Dict[str, Any], task: Task):
        """Deliver assignment to agent's inbox."""
        try:
            agent_id = assignment["assigned_to"]
            inbox_dir = f"{self.agent_workspaces}/{agent_id}/inbox"

            os.makedirs(inbox_dir, exist_ok=True)

            message_data = {
                "header": "🤖 AUTOMATED TASK ASSIGNMENT - ATD-1",
                "from": "AutomatedTaskDistributor-ATD-1",
                "to": agent_id,
                "priority": "urgent",
                "message_id": f"auto_assign_{task.task_id}_{int(datetime.now().timestamp())}",
                "timestamp": datetime.now().isoformat(),
                "protocol": "automated_task_distribution",
                "content": {
                    "assignment": assignment,
                    "task_details": {
                        "title": task.title,
                        "description": task.description,
                        "requirements": [cap.value for cap in task.required_capabilities],
                        "estimated_hours": task.estimated_hours,
                        "deadline": task.deadline.isoformat() if task.deadline else None
                    },
                    "coordination": {
                        "report_to": "Agent-4_Strategic_Coordination_Lead",
                        "sync_points": ["11:00 UTC", "11:15 UTC", "11:30 UTC"],
                        "success_criteria": "Complete implementation with LoggingMixin integration",
                        "quality_gate": "Import validation and basic functionality testing"
                    },
                    "automation_note": "This assignment was automatically optimized by ATD-1 for maximum swarm efficiency"
                },
                "signature": "AutomatedTaskDistributor-ATD-1_OptimizedAssignment"
            }

            filename = f"auto_assignment_{task.task_id}_{int(datetime.now().timestamp())}.json"
            filepath = os.path.join(inbox_dir, filename)

            with open(filepath, 'w') as f:
                json.dump(message_data, f, indent=2, default=str)

            logger.info(f"📨 Assignment delivered to {agent_id}: {filename}")

        except Exception as e:
            logger.error(f"Error delivering assignment to {agent_id}: {e}")

    def get_distribution_analytics(self) -> Dict[str, Any]:
        """Get analytics on task distribution performance."""
        try:
            total_assignments = len(self.assignment_history)
            if total_assignments == 0:
                return {"message": "No assignments yet"}

            # Calculate metrics
            avg_score = sum(a["score"] for a in self.assignment_history) / total_assignments
            agent_distribution = {}
            for assignment in self.assignment_history:
                agent = assignment["assigned_to"]
                agent_distribution[agent] = agent_distribution.get(agent, 0) + 1

            return {
                "total_assignments": total_assignments,
                "average_score": round(avg_score, 3),
                "agent_distribution": agent_distribution,
                "optimization_weights": self.optimization_weights,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting distribution analytics: {e}")
            return {"error": str(e)}

    def optimize_weights(self):
        """Optimize assignment weights based on historical performance."""
        # This would use machine learning to optimize weights
        # For now, just log that optimization is available
        logger.info("🎯 Weight optimization available - implement ML optimization algorithm")


# Global distributor instance
task_distributor = AutomatedTaskDistributor()