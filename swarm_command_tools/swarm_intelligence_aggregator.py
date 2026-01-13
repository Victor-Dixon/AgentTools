#!/usr/bin/env python3
"""
Swarm Intelligence Aggregator (SIA-1) - Cross-Agent Knowledge Sharing Engine
=============================================================================

Collects, analyzes, and shares knowledge across the swarm to enable collective intelligence,
prevent duplicate work, and accelerate problem-solving.

V2 Compliant: Knowledge graph integration, pattern recognition
Author: Agent-4 (Strategic Coordination Lead)
Date: 2026-01-13
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import hashlib

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

@dataclass
class KnowledgePattern:
    """Represents a discovered knowledge pattern."""
    pattern_id: str
    pattern_type: str  # 'solution', 'problem', 'technique', 'best_practice'
    title: str
    description: str
    keywords: List[str]
    source_agents: List[str]
    occurrence_count: int
    first_discovered: datetime
    last_updated: datetime
    confidence_score: float  # 0.0 to 1.0
    related_patterns: List[str]
    implementations: List[Dict[str, Any]]

@dataclass
class AgentContribution:
    """Tracks an agent's knowledge contributions."""
    agent_id: str
    total_contributions: int
    pattern_discoveries: int
    solution_shares: int
    knowledge_quality_score: float
    specialization_areas: List[str]
    last_contribution: Optional[datetime]

@dataclass
class CollectiveInsight:
    """Represents collective swarm intelligence."""
    insight_id: str
    title: str
    description: str
    contributing_agents: List[str]
    confidence_level: float
    impact_assessment: str
    discovered_at: datetime
    validation_count: int

class SwarmIntelligenceAggregator(BaseService, LoggingMixin):
    """Swarm Intelligence Aggregator - Collective knowledge engine."""

    def __init__(self):
        """Initialize the swarm intelligence aggregator."""
        super().__init__("SwarmIntelligenceAggregator")
        self.knowledge_base_file = "swarm_intelligence_knowledge.json"
        self.agent_workspaces = "agent_workspaces"
        self.knowledge_patterns: Dict[str, KnowledgePattern] = {}
        self.agent_contributions: Dict[str, AgentContribution] = {}
        self.collective_insights: List[CollectiveInsight] = []
        self.pattern_extraction_rules = self._load_pattern_rules()

        # Load existing knowledge
        self._load_knowledge_base()

    def _load_pattern_rules(self) -> Dict[str, Any]:
        """Load pattern extraction and recognition rules."""
        return {
            "solution_patterns": [
                r"solved.*by.*using",
                r"fixed.*with.*approach",
                r"resolved.*using.*method",
                r"implemented.*solution",
                r"successful.*implementation"
            ],
            "problem_patterns": [
                r"encountered.*issue",
                r"faced.*problem",
                r"blocked.*by.*error",
                r"difficulty.*with",
                r"challenge.*in.*area"
            ],
            "technique_patterns": [
                r"using.*technique",
                r"applied.*method",
                r"leveraged.*approach",
                r"utilized.*pattern",
                r"implemented.*strategy"
            ],
            "best_practice_patterns": [
                r"best.*practice",
                r"recommended.*approach",
                r"standard.*method",
                r"optimal.*solution",
                r"proven.*technique"
            ]
        }

    def _load_knowledge_base(self):
        """Load existing knowledge base from disk."""
        try:
            if os.path.exists(self.knowledge_base_file):
                with open(self.knowledge_base_file, 'r') as f:
                    data = json.load(f)

                # Load patterns
                for pattern_data in data.get("patterns", []):
                    pattern = KnowledgePattern(**pattern_data)
                    self.knowledge_patterns[pattern.pattern_id] = pattern

                # Load contributions
                for contrib_data in data.get("contributions", []):
                    contrib = AgentContribution(**contrib_data)
                    self.agent_contributions[contrib.agent_id] = contrib

                # Load insights
                for insight_data in data.get("insights", []):
                    insight = CollectiveInsight(**insight_data)
                    self.collective_insights.append(insight)

                logger.info(f"📚 Loaded {len(self.knowledge_patterns)} patterns, {len(self.agent_contributions)} contributions, {len(self.collective_insights)} insights")

        except Exception as e:
            logger.warning(f"Error loading knowledge base: {e}")

    def _save_knowledge_base(self):
        """Save knowledge base to disk."""
        try:
            data = {
                "patterns": [asdict(p) for p in self.knowledge_patterns.values()],
                "contributions": [asdict(c) for c in self.agent_contributions.values()],
                "insights": [asdict(i) for i in self.collective_insights],
                "last_updated": datetime.now().isoformat()
            }

            with open(self.knowledge_base_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")

    def scan_agent_activities(self) -> Dict[str, Any]:
        """Scan all agent activities for new knowledge patterns."""
        try:
            new_patterns_found = 0
            activities_processed = 0

            # Scan each agent's devlog and activities
            agent_ids = ["Agent-1", "Agent-2", "Agent-3", "Agent-4", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]

            for agent_id in agent_ids:
                patterns_from_agent = self._scan_agent_knowledge(agent_id)
                new_patterns_found += len(patterns_from_agent)
                activities_processed += 1

                # Update agent contributions
                if agent_id not in self.agent_contributions:
                    self.agent_contributions[agent_id] = AgentContribution(
                        agent_id=agent_id,
                        total_contributions=0,
                        pattern_discoveries=0,
                        solution_shares=0,
                        knowledge_quality_score=0.8,
                        specialization_areas=[],
                        last_contribution=None
                    )

                self.agent_contributions[agent_id].total_contributions += len(patterns_from_agent)
                self.agent_contributions[agent_id].last_contribution = datetime.now()

            # Save updated knowledge base
            self._save_knowledge_base()

            return {
                "success": True,
                "new_patterns_found": new_patterns_found,
                "activities_processed": activities_processed,
                "total_patterns": len(self.knowledge_patterns),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scanning agent activities: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _scan_agent_knowledge(self, agent_id: str) -> List[KnowledgePattern]:
        """Scan a specific agent's knowledge sources."""
        new_patterns = []

        try:
            # Scan devlog
            devlog_path = f"website_data/agent_activity/{agent_id}_latest_devlog.md"
            if os.path.exists(devlog_path):
                with open(devlog_path, 'r') as f:
                    content = f.read()
                    patterns = self._extract_patterns_from_text(content, agent_id)
                    new_patterns.extend(patterns)

            # Scan recent status updates
            status_path = f"{self.agent_workspaces}/{agent_id}/status.json"
            if os.path.exists(status_path):
                try:
                    with open(status_path, 'r') as f:
                        status_data = json.load(f)
                        if "current_mission" in status_data:
                            patterns = self._extract_patterns_from_text(status_data["current_mission"], agent_id)
                            new_patterns.extend(patterns)
                except Exception as e:
                    logger.debug(f"Error scanning status for {agent_id}: {e}")

            # Deduplicate and validate patterns
            unique_patterns = self._deduplicate_patterns(new_patterns)

            # Add to knowledge base
            for pattern in unique_patterns:
                if pattern.pattern_id not in self.knowledge_patterns:
                    self.knowledge_patterns[pattern.pattern_id] = pattern
                    self.agent_contributions[agent_id].pattern_discoveries += 1

        except Exception as e:
            logger.warning(f"Error scanning knowledge for {agent_id}: {e}")

        return new_patterns

    def _extract_patterns_from_text(self, text: str, agent_id: str) -> List[KnowledgePattern]:
        """Extract knowledge patterns from text content."""
        patterns = []
        text_lower = text.lower()

        for pattern_type, regexes in self.pattern_extraction_rules.items():
            for regex in regexes:
                matches = re.finditer(regex, text_lower, re.IGNORECASE)
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]

                    # Create pattern
                    pattern_id = hashlib.md5(f"{pattern_type}_{match.group()}_{agent_id}".encode()).hexdigest()[:16]

                    # Check if this pattern already exists
                    if pattern_id in self.knowledge_patterns:
                        # Update existing pattern
                        existing = self.knowledge_patterns[pattern_id]
                        if agent_id not in existing.source_agents:
                            existing.source_agents.append(agent_id)
                        existing.occurrence_count += 1
                        existing.last_updated = datetime.now()
                        existing.confidence_score = min(1.0, existing.confidence_score + 0.1)
                    else:
                        # Create new pattern
                        pattern = KnowledgePattern(
                            pattern_id=pattern_id,
                            pattern_type=pattern_type.replace("_patterns", ""),
                            title=f"Pattern from {agent_id}: {match.group()[:50]}...",
                            description=context.strip(),
                            keywords=self._extract_keywords(context),
                            source_agents=[agent_id],
                            occurrence_count=1,
                            first_discovered=datetime.now(),
                            last_updated=datetime.now(),
                            confidence_score=0.6,
                            related_patterns=[],
                            implementations=[]
                        )
                        patterns.append(pattern)

        return patterns

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b\w{4,}\b', text.lower())
        # Remove common stop words
        stop_words = {'with', 'from', 'that', 'this', 'have', 'been', 'were', 'when', 'where', 'what', 'which', 'their', 'there', 'these', 'those'}
        keywords = [word for word in words if word not in stop_words]
        # Return top 5 most common
        return [word for word, _ in Counter(keywords).most_common(5)]

    def _deduplicate_patterns(self, patterns: List[KnowledgePattern]) -> List[KnowledgePattern]:
        """Remove duplicate patterns."""
        seen = set()
        unique = []

        for pattern in patterns:
            # Create a signature for deduplication
            signature = (pattern.pattern_type, tuple(sorted(pattern.keywords)))
            if signature not in seen:
                seen.add(signature)
                unique.append(pattern)

        return unique

    def search_knowledge(self, query: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Search the knowledge base for relevant patterns."""
        try:
            query_lower = query.lower()
            results = []

            for pattern in self.knowledge_patterns.values():
                # Skip if filtering by agent and pattern doesn't include them
                if agent_id and agent_id not in pattern.source_agents:
                    continue

                # Check if query matches title, description, or keywords
                searchable_text = f"{pattern.title} {pattern.description} {' '.join(pattern.keywords)}".lower()

                if query_lower in searchable_text:
                    results.append({
                        "pattern_id": pattern.pattern_id,
                        "type": pattern.pattern_type,
                        "title": pattern.title,
                        "description": pattern.description[:200] + "..." if len(pattern.description) > 200 else pattern.description,
                        "source_agents": pattern.source_agents,
                        "confidence": pattern.confidence_score,
                        "last_updated": pattern.last_updated.isoformat()
                    })

            # Sort by confidence and recency
            results.sort(key=lambda x: (x["confidence"], x.get("last_updated", "")), reverse=True)

            return {
                "success": True,
                "query": query,
                "results": results[:10],  # Top 10 results
                "total_found": len(results),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

    def get_swarm_insights(self) -> Dict[str, Any]:
        """Generate collective insights from swarm knowledge."""
        try:
            insights = []

            # Analyze pattern clusters
            pattern_clusters = self._analyze_pattern_clusters()
            for cluster in pattern_clusters:
                if cluster["confidence"] > 0.7:  # High confidence insights only
                    insight = CollectiveInsight(
                        insight_id=hashlib.md5(f"insight_{cluster['theme']}".encode()).hexdigest()[:16],
                        title=f"Swarm Insight: {cluster['theme']}",
                        description=cluster["description"],
                        contributing_agents=list(set(cluster["agents"])),
                        confidence_level=cluster["confidence"],
                        impact_assessment=cluster["impact"],
                        discovered_at=datetime.now(),
                        validation_count=cluster["validation_count"]
                    )
                    insights.append(insight)

            # Update collective insights
            self.collective_insights = insights

            return {
                "success": True,
                "insights_generated": len(insights),
                "total_patterns_analyzed": len(self.knowledge_patterns),
                "insights": [asdict(i) for i in insights],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating swarm insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _analyze_pattern_clusters(self) -> List[Dict[str, Any]]:
        """Analyze patterns to find clusters and insights."""
        clusters = []

        # Group patterns by keywords
        keyword_groups = defaultdict(list)
        for pattern in self.knowledge_patterns.values():
            for keyword in pattern.keywords:
                keyword_groups[keyword].append(pattern)

        # Find significant clusters
        for keyword, patterns in keyword_groups.items():
            if len(patterns) >= 3:  # At least 3 patterns for a cluster
                cluster_agents = list(set(agent for pattern in patterns for agent in pattern.source_agents))
                avg_confidence = sum(p.confidence_score for p in patterns) / len(patterns)

                # Determine cluster theme and impact
                if keyword in ["logging", "loggingmixin", "error", "debug"]:
                    theme = "Error Handling & Logging Standardization"
                    impact = "High - Improves system observability and debugging"
                elif keyword in ["task", "assignment", "coordination"]:
                    theme = "Task Coordination Optimization"
                    impact = "High - Accelerates parallel processing"
                elif keyword in ["integration", "api", "service"]:
                    theme = "Service Integration Patterns"
                    impact = "Medium - Improves system interoperability"
                else:
                    theme = f"Knowledge Cluster: {keyword}"
                    impact = "Medium - General optimization opportunity"

                clusters.append({
                    "theme": theme,
                    "keyword": keyword,
                    "pattern_count": len(patterns),
                    "agents": cluster_agents,
                    "confidence": avg_confidence,
                    "description": f"Swarm has collectively identified {len(patterns)} patterns related to {keyword}, involving {len(cluster_agents)} agents.",
                    "impact": impact,
                    "validation_count": len(patterns)
                })

        return sorted(clusters, key=lambda x: x["confidence"] * x["pattern_count"], reverse=True)

    def get_agent_knowledge_profile(self, agent_id: str) -> Dict[str, Any]:
        """Get knowledge profile for a specific agent."""
        try:
            if agent_id not in self.agent_contributions:
                return {
                    "success": False,
                    "error": f"No knowledge profile found for {agent_id}"
                }

            contribution = self.agent_contributions[agent_id]

            # Get patterns contributed by this agent
            agent_patterns = [
                asdict(pattern) for pattern in self.knowledge_patterns.values()
                if agent_id in pattern.source_agents
            ]

            # Calculate specialization areas
            keyword_counts = Counter()
            for pattern in agent_patterns:
                keyword_counts.update(pattern["keywords"])

            top_specializations = [kw for kw, _ in keyword_counts.most_common(5)]

            return {
                "success": True,
                "agent_id": agent_id,
                "contribution_summary": {
                    "total_contributions": contribution.total_contributions,
                    "pattern_discoveries": contribution.pattern_discoveries,
                    "solution_shares": contribution.solution_shares,
                    "knowledge_quality_score": contribution.knowledge_quality_score,
                    "specialization_areas": top_specializations
                },
                "patterns_contributed": len(agent_patterns),
                "recent_patterns": agent_patterns[-5:],  # Last 5 patterns
                "collaboration_score": len(set(p["source_agents"] for p in agent_patterns if len(p["source_agents"]) > 1)) / max(1, len(agent_patterns)),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting knowledge profile for {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }

    def get_swarm_knowledge_stats(self) -> Dict[str, Any]:
        """Get overall swarm knowledge statistics."""
        try:
            total_patterns = len(self.knowledge_patterns)
            total_contributions = sum(c.total_contributions for c in self.agent_contributions.values())
            active_contributors = sum(1 for c in self.agent_contributions.values() if c.total_contributions > 0)

            # Pattern type distribution
            pattern_types = Counter(p.pattern_type for p in self.knowledge_patterns.values())

            # Most active contributors
            top_contributors = sorted(
                self.agent_contributions.items(),
                key=lambda x: x[1].total_contributions,
                reverse=True
            )[:5]

            return {
                "success": True,
                "overall_stats": {
                    "total_patterns": total_patterns,
                    "total_contributions": total_contributions,
                    "active_contributors": active_contributors,
                    "collective_insights": len(self.collective_insights),
                    "average_patterns_per_agent": total_patterns / max(1, active_contributors)
                },
                "pattern_distribution": dict(pattern_types),
                "top_contributors": [
                    {
                        "agent_id": agent_id,
                        "contributions": contrib.total_contributions,
                        "quality_score": contrib.knowledge_quality_score
                    }
                    for agent_id, contrib in top_contributors
                ],
                "knowledge_growth": self._calculate_knowledge_growth(),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting swarm knowledge stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _calculate_knowledge_growth(self) -> Dict[str, Any]:
        """Calculate knowledge growth trends."""
        try:
            # Simple growth calculation (could be enhanced with time series analysis)
            recent_patterns = sum(1 for p in self.knowledge_patterns.values()
                                if (datetime.now() - p.first_discovered) < timedelta(days=7))

            return {
                "patterns_this_week": recent_patterns,
                "growth_rate": recent_patterns / max(1, len(self.knowledge_patterns)) if self.knowledge_patterns else 0,
                "trend": "growing" if recent_patterns > 5 else "stable"
            }

        except Exception as e:
            return {"error": str(e)}


# Global aggregator instance
intelligence_aggregator = SwarmIntelligenceAggregator()