#!/usr/bin/env python3
"""
Automated Task Distributor Routes (ATD-1)
=========================================

FastAPI routes for the Automated Task Distributor - intelligent task assignment interface.

V2 Compliant: RESTful API design, integrated with existing application
Author: Agent-4 (Strategic Coordination Lead)
Date: 2026-01-13
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from swarm_command_tools.automated_task_distributor import task_distributor, Task, TaskPriority, AgentCapability

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/distribute", tags=["Task Distribution"])

class TaskPriorityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKLOG = "backlog"

class AgentCapabilityEnum(str, Enum):
    PYTHON_DEVELOPMENT = "python_development"
    WEB_DEVELOPMENT = "web_development"
    AI_INTEGRATION = "ai_integration"
    INFRASTRUCTURE = "infrastructure"
    TESTING_QA = "testing_qa"
    COORDINATION = "coordination"
    DOCUMENTATION = "documentation"
    RESEARCH = "research"

class TaskRequest(BaseModel):
    """Request model for task distribution."""
    task_id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: TaskPriorityEnum = Field(default=TaskPriorityEnum.MEDIUM, description="Task priority")
    required_capabilities: List[AgentCapabilityEnum] = Field(..., description="Required agent capabilities")
    estimated_hours: float = Field(..., gt=0, description="Estimated hours to complete")
    deadline: Optional[str] = Field(None, description="ISO format deadline (optional)")
    dependencies: Optional[List[str]] = Field(default=[], description="Task dependencies")

class DistributionResponse(BaseModel):
    """Response model for task distribution."""
    success: bool
    task_id: str
    assigned_to: Optional[str] = None
    assignment_score: Optional[float] = None
    estimated_completion: Optional[str] = None
    error: Optional[str] = None

@router.post("/task", response_model=DistributionResponse, summary="Distribute task automatically")
async def distribute_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Automatically distribute a task to the optimal agent."""
    try:
        # Convert request to Task object
        priority_map = {
            TaskPriorityEnum.CRITICAL: TaskPriority.CRITICAL,
            TaskPriorityEnum.HIGH: TaskPriority.HIGH,
            TaskPriorityEnum.MEDIUM: TaskPriority.MEDIUM,
            TaskPriorityEnum.LOW: TaskPriority.LOW,
            TaskPriorityEnum.BACKLOG: TaskPriority.BACKLOG
        }

        capability_map = {
            AgentCapabilityEnum.PYTHON_DEVELOPMENT: AgentCapability.PYTHON_DEVELOPMENT,
            AgentCapabilityEnum.WEB_DEVELOPMENT: AgentCapability.WEB_DEVELOPMENT,
            AgentCapabilityEnum.AI_INTEGRATION: AgentCapability.AI_INTEGRATION,
            AgentCapabilityEnum.INFRASTRUCTURE: AgentCapability.INFRASTRUCTURE,
            AgentCapabilityEnum.TESTING_QA: AgentCapability.TESTING_QA,
            AgentCapabilityEnum.COORDINATION: AgentCapability.COORDINATION,
            AgentCapabilityEnum.DOCUMENTATION: AgentCapability.DOCUMENTATION,
            AgentCapabilityEnum.RESEARCH: AgentCapability.RESEARCH
        }

        task = Task(
            task_id=task_request.task_id,
            title=task_request.title,
            description=task_request.description,
            priority=priority_map[task_request.priority],
            required_capabilities=[capability_map[cap] for cap in task_request.required_capabilities],
            estimated_hours=task_request.estimated_hours,
            deadline=datetime.fromisoformat(task_request.deadline) if task_request.deadline else None,
            dependencies=task_request.dependencies or []
        )

        # Distribute task (this may take some time, so we use background tasks for heavy processing)
        result = task_distributor.distribute_task(task)

        return DistributionResponse(**result)

    except Exception as e:
        logger.error(f"Error distributing task: {e}")
        raise HTTPException(status_code=500, detail=f"Task distribution failed: {str(e)}")

@router.get("/analytics", summary="Get distribution analytics")
async def get_distribution_analytics():
    """Get analytics on task distribution performance."""
    try:
        analytics = task_distributor.get_distribution_analytics()
        return JSONResponse(content=analytics)
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/agents", summary="Get agent capabilities and status")
async def get_agent_capabilities():
    """Get current agent capabilities and workload status."""
    try:
        agents_data = {}
        for agent_id, profile in task_distributor.capability_database.items():
            agents_data[agent_id] = {
                "capabilities": [cap.value for cap in profile.capabilities],
                "current_workload": profile.current_workload,
                "max_capacity": profile.max_capacity,
                "workload_percentage": round((profile.current_workload / profile.max_capacity) * 100, 1),
                "reliability_score": profile.reliability_score,
                "status": profile.status,
                "specialization_scores": {cap.value: score for cap, score in profile.specialization_score.items()}
            }

        return JSONResponse(content={
            "agents": agents_data,
            "total_agents": len(agents_data),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting agent capabilities: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.post("/optimize", summary="Optimize distribution weights")
async def optimize_distribution_weights():
    """Trigger optimization of distribution algorithm weights."""
    try:
        # Run optimization in background
        task_distributor.optimize_weights()

        return JSONResponse(content={
            "message": "Optimization triggered",
            "current_weights": task_distributor.optimization_weights,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error optimizing weights: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/history", summary="Get assignment history")
async def get_assignment_history(limit: int = 50):
    """Get recent assignment history."""
    try:
        history = task_distributor.assignment_history[-limit:] if task_distributor.assignment_history else []

        return JSONResponse(content={
            "assignments": history,
            "total_assignments": len(task_distributor.assignment_history),
            "returned_count": len(history),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting assignment history: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/health", summary="Task distributor health check")
async def distributor_health():
    """Health check for the automated task distributor."""
    try:
        agent_count = len(task_distributor.capability_database)
        total_assignments = len(task_distributor.assignment_history)

        health_status = {
            "status": "healthy",
            "agent_database_size": agent_count,
            "total_assignments": total_assignments,
            "optimization_weights": task_distributor.optimization_weights,
            "timestamp": datetime.now().isoformat()
        }

        # Check if we have minimum viable agents
        if agent_count < 3:
            health_status["status"] = "degraded"
            health_status["warning"] = "Low agent count may affect distribution quality"

        return JSONResponse(content=health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status_code=503
        )