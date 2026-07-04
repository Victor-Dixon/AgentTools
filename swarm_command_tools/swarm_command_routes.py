#!/usr/bin/env python3
"""
Swarm Command Dashboard Routes - SCD-1 (Swarm Command Dashboard)
================================================================

FastAPI routes for the Swarm Command Dashboard - Real-time swarm monitoring and control interface.

V2 Compliant: Modular route design, integrated with existing FastAPI application
Author: Agent-4 (Strategic Coordination Lead)
Date: 2026-01-13
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from swarm_command_tools.swarm_command_handlers import swarm_dashboard

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/swarm", tags=["swarm-command"])

# Templates
templates = Jinja2Templates(directory="src/web/templates")

@router.get("/", response_class=HTMLResponse, summary="Swarm Command Dashboard")
async def swarm_command_dashboard(request: Request):
    """Main swarm command dashboard interface."""
    try:
        # Get current swarm status
        swarm_status = swarm_dashboard.get_swarm_status()
        workstream_progress = swarm_dashboard.get_workstream_progress()

        return templates.TemplateResponse(
            "swarm_dashboard.html",
            {
                "request": request,
                "swarm_status": swarm_status,
                "workstream_progress": workstream_progress,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error loading swarm dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.get("/api/status", summary="Get real-time swarm status")
async def get_swarm_status():
    """Get comprehensive real-time swarm status."""
    try:
        status = swarm_dashboard.get_swarm_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting swarm status: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/api/workstreams", summary="Get workstream progress")
async def get_workstream_progress():
    """Get detailed workstream progress information."""
    try:
        progress = swarm_dashboard.get_workstream_progress()
        return JSONResponse(content=progress)
    except Exception as e:
        logger.error(f"Error getting workstream progress: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/api/agent/{agent_id}", summary="Get specific agent status")
async def get_agent_status(agent_id: str):
    """Get detailed status for a specific agent."""
    try:
        agent_status = swarm_dashboard._get_agent_status(agent_id)
        return JSONResponse(content=agent_status)
    except Exception as e:
        logger.error(f"Error getting agent status for {agent_id}: {e}")
        return JSONResponse(
            content={"error": str(e), "agent_id": agent_id, "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.post("/api/emergency/{agent_id}", summary="Execute emergency override")
async def emergency_override(agent_id: str, action: str, reason: str):
    """Execute emergency override action for swarm coordination."""
    try:
        result = swarm_dashboard.emergency_override(agent_id, action, reason)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error executing emergency override for {agent_id}: {e}")
        return JSONResponse(
            content={"error": str(e), "agent_id": agent_id, "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/api/metrics", summary="Get coordination metrics")
async def get_coordination_metrics():
    """Get coordination performance metrics."""
    try:
        metrics = swarm_dashboard._get_coordination_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Error getting coordination metrics: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

# WebSocket endpoint for real-time updates (would need WebSocket support)
@router.get("/health", summary="Dashboard health check")
async def dashboard_health():
    """Health check endpoint for the swarm dashboard."""
    try:
        # Quick health check
        status = swarm_dashboard.get_swarm_status()
        health_status = {
            "status": "healthy" if status.get("system_health") != "critical" else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "system_health": status.get("system_health"),
            "active_agents": len([a for a in status.get("agents", {}).values() if a.get("status") != "error"]),
            "total_agents": len(status.get("agents", {}))
        }
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