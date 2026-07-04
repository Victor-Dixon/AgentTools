#!/usr/bin/env python3
"""
Swarm Intelligence Aggregator Routes (SIA-1)
============================================

FastAPI routes for the Swarm Intelligence Aggregator - cross-agent knowledge sharing interface.

V2 Compliant: RESTful API design, integrated with existing application
Author: Agent-4 (Strategic Coordination Lead)
Date: 2026-01-13
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from swarm_command_tools.swarm_intelligence_aggregator import intelligence_aggregator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/intelligence", tags=["Knowledge Aggregation"])

class KnowledgeSearchRequest(BaseModel):
    """Request model for knowledge search."""
    query: str
    agent_filter: Optional[str] = None
    pattern_type: Optional[str] = None
    limit: int = 10

@router.post("/scan", summary="Scan agent activities for new knowledge")
async def scan_agent_activities(background_tasks: BackgroundTasks):
    """Scan all agent activities and extract new knowledge patterns."""
    try:
        # Run scan in background since it may be time-intensive
        background_tasks.add_task(intelligence_aggregator.scan_agent_activities)

        return JSONResponse(content={
            "message": "Knowledge scan initiated in background",
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error initiating knowledge scan: {e}")
        raise HTTPException(status_code=500, detail=f"Scan initiation failed: {str(e)}")

@router.post("/search", summary="Search swarm knowledge base")
async def search_knowledge(search_request: KnowledgeSearchRequest):
    """Search the collective swarm knowledge base."""
    try:
        results = intelligence_aggregator.search_knowledge(
            query=search_request.query,
            agent_id=search_request.agent_filter
        )

        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        return JSONResponse(
            content={"error": str(e), "query": search_request.query, "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/insights", summary="Get collective swarm insights")
async def get_swarm_insights():
    """Generate and retrieve collective swarm intelligence insights."""
    try:
        insights = intelligence_aggregator.get_swarm_insights()
        return JSONResponse(content=insights)
    except Exception as e:
        logger.error(f"Error getting swarm insights: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/agent/{agent_id}", summary="Get agent knowledge profile")
async def get_agent_knowledge_profile(agent_id: str):
    """Get detailed knowledge contribution profile for a specific agent."""
    try:
        profile = intelligence_aggregator.get_agent_knowledge_profile(agent_id)

        if not profile.get("success", False):
            raise HTTPException(status_code=404, detail=profile.get("error", "Profile not found"))

        return JSONResponse(content=profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge profile for {agent_id}: {e}")
        return JSONResponse(
            content={"error": str(e), "agent_id": agent_id, "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/stats", summary="Get swarm knowledge statistics")
async def get_swarm_knowledge_stats():
    """Get comprehensive statistics about swarm knowledge and contributions."""
    try:
        stats = intelligence_aggregator.get_swarm_knowledge_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/patterns", summary="Get knowledge patterns")
async def get_knowledge_patterns(
    pattern_type: Optional[str] = None,
    agent_filter: Optional[str] = None,
    limit: int = Query(50, description="Maximum number of patterns to return")
):
    """Get knowledge patterns with optional filtering."""
    try:
        patterns = []

        for pattern_id, pattern in intelligence_aggregator.knowledge_patterns.items():
            # Apply filters
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            if agent_filter and agent_filter not in pattern.source_agents:
                continue

            patterns.append({
                "pattern_id": pattern.pattern_id,
                "type": pattern.pattern_type,
                "title": pattern.title,
                "description": pattern.description,
                "keywords": pattern.keywords,
                "source_agents": pattern.source_agents,
                "occurrence_count": pattern.occurrence_count,
                "confidence_score": pattern.confidence_score,
                "first_discovered": pattern.first_discovered.isoformat(),
                "last_updated": pattern.last_updated.isoformat()
            })

        # Sort by confidence and recency
        patterns.sort(key=lambda x: (x["confidence_score"], x["last_updated"]), reverse=True)

        return JSONResponse(content={
            "patterns": patterns[:limit],
            "total_found": len(patterns),
            "returned_count": min(limit, len(patterns)),
            "filters_applied": {
                "pattern_type": pattern_type,
                "agent_filter": agent_filter
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting knowledge patterns: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/contributions", summary="Get agent contribution rankings")
async def get_agent_contributions():
    """Get ranking of agent knowledge contributions."""
    try:
        contributions = []

        for agent_id, contrib in intelligence_aggregator.agent_contributions.items():
            contributions.append({
                "agent_id": agent_id,
                "total_contributions": contrib.total_contributions,
                "pattern_discoveries": contrib.pattern_discoveries,
                "solution_shares": contrib.solution_shares,
                "knowledge_quality_score": contrib.knowledge_quality_score,
                "specialization_areas": contrib.specialization_areas,
                "last_contribution": contrib.last_contribution.isoformat() if contrib.last_contribution else None
            })

        # Sort by total contributions
        contributions.sort(key=lambda x: x["total_contributions"], reverse=True)

        return JSONResponse(content={
            "contributions": contributions,
            "total_contributors": len(contributions),
            "most_active_agent": contributions[0]["agent_id"] if contributions else None,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting agent contributions: {e}")
        return JSONResponse(
            content={"error": str(e), "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.post("/pattern/{pattern_id}/validate", summary="Validate knowledge pattern")
async def validate_knowledge_pattern(pattern_id: str, agent_id: str):
    """Validate and increase confidence of a knowledge pattern."""
    try:
        if pattern_id not in intelligence_aggregator.knowledge_patterns:
            raise HTTPException(status_code=404, detail=f"Pattern {pattern_id} not found")

        pattern = intelligence_aggregator.knowledge_patterns[pattern_id]

        # Increase confidence score
        pattern.confidence_score = min(1.0, pattern.confidence_score + 0.1)
        pattern.last_updated = datetime.now()

        # Track validation
        if "validations" not in pattern.__dict__:
            pattern.validations = []
        pattern.validations.append({
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        })

        # Save updated knowledge
        intelligence_aggregator._save_knowledge_base()

        return JSONResponse(content={
            "success": True,
            "pattern_id": pattern_id,
            "new_confidence": pattern.confidence_score,
            "validated_by": agent_id,
            "timestamp": datetime.now().isoformat()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating pattern {pattern_id}: {e}")
        return JSONResponse(
            content={"error": str(e), "pattern_id": pattern_id, "timestamp": datetime.now().isoformat()},
            status_code=500
        )

@router.get("/health", summary="Intelligence aggregator health check")
async def aggregator_health():
    """Health check for the swarm intelligence aggregator."""
    try:
        pattern_count = len(intelligence_aggregator.knowledge_patterns)
        contributor_count = len(intelligence_aggregator.agent_contributions)
        insight_count = len(intelligence_aggregator.collective_insights)

        health_status = {
            "status": "healthy",
            "knowledge_patterns": pattern_count,
            "active_contributors": contributor_count,
            "collective_insights": insight_count,
            "knowledge_base_size": os.path.getsize("swarm_intelligence_knowledge.json") if os.path.exists("swarm_intelligence_knowledge.json") else 0,
            "timestamp": datetime.now().isoformat()
        }

        # Health criteria
        if pattern_count < 10:
            health_status["status"] = "initializing"
            health_status["message"] = "Building initial knowledge base"
        elif contributor_count < 3:
            health_status["status"] = "limited"
            health_status["message"] = "Low contributor engagement"

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