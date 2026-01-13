#!/usr/bin/env python3
"""
AI Orchestration MCP Server
===========================

MCP server providing AI-powered agent coordination and task allocation.
Integrates with the swarm messaging system for intelligent coordination.

FEATURES:
- AI-powered task analysis and agent recommendations
- Intelligent coordination strategy selection
- Risk assessment and mitigation suggestions
- Message template generation for swarm coordination
- Real-time coordination intelligence

Author: Agent-5 (Infrastructure Automation Specialist)
Date: 2026-01-13
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Add main repo src to path for AI orchestration imports
import sys
main_repo_src = Path(__file__).parent.parent.parent / "Agent_Cellphone_V2_Repository" / "src"
if str(main_repo_src) not in sys.path:
    sys.path.insert(0, str(main_repo_src))

logger = logging.getLogger(__name__)

# Import AI orchestration components (with fallbacks)
try:
    from core.orchestration.ai_orchestrator_factory import create_smart_orchestrator
    from core.orchestration.registry import StepRegistry
    AI_AVAILABLE = True
except ImportError:
    logger.warning("AI orchestration components not available - using fallback mode")
    AI_AVAILABLE = False


class AIOrchestrationServer:
    """MCP server for AI-powered agent coordination."""

    def __init__(self):
        self.server = Server("ai-orchestration-server")
        self.orchestrator = None
        self.registry = None

        # Initialize components if available
        if AI_AVAILABLE:
            try:
                self.registry = StepRegistry()
                self.orchestrator = create_smart_orchestrator(self.registry, ['analyze'])
                logger.info("✅ AI orchestrator initialized in MCP server")
            except Exception as e:
                logger.warning(f"Failed to initialize AI orchestrator: {e}")

    async def handle_analyze_task(
        self,
        task_description: str,
        available_agents: Optional[List[str]] = None,
        coordination_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a task and provide AI-powered coordination recommendations.

        Args:
            task_description: Description of the task to analyze
            available_agents: List of available agent IDs (optional)
            coordination_context: Additional coordination context

        Returns:
            Analysis with recommendations
        """
        if not AI_AVAILABLE or not self.orchestrator:
            return self._fallback_task_analysis(task_description, available_agents)

        try:
            # Default agents if not specified
            if available_agents is None:
                available_agents = ['agent-1', 'agent-2', 'agent-3', 'agent-5', 'agent-6', 'agent-7', 'agent-8']

            # Create mock agent data with expertise mapping
            agent_expertise = {
                'agent-1': ['integration', 'core-systems', 'api', 'backend', 'testing'],
                'agent-2': ['architecture', 'design', 'planning', 'system-design'],
                'agent-3': ['infrastructure', 'devops', 'deployment', 'monitoring'],
                'agent-5': ['business-intelligence', 'ai', 'orchestration', 'analytics'],
                'agent-6': ['coordination', 'communication', 'messaging', 'facilitation'],
                'agent-7': ['web-development', 'frontend', 'ui', 'user-experience', 'javascript'],
                'agent-8': ['ssot', 'system-integration', 'data-management', 'validation', 'database']
            }

            agents = []
            for agent_id in available_agents:
                if agent_id in agent_expertise:
                    agents.append({
                        'id': agent_id,
                        'agent_id': agent_id,
                        'specialties': agent_expertise[agent_id],
                        'capacity': 5,  # Default capacity
                        'status': 'available'
                    })

            # Create coordination context
            coordination_payload = {
                'agents': agents,
                'tasks': [{
                    'id': 'current_task',
                    'task_id': 'current_task',
                    'description': task_description,
                    'priority': 3,
                    'estimated_complexity': 'medium',
                    'required_domains': self._extract_domains_from_task(task_description)
                }],
                'coordination_state': {
                    'phase': 'analysis',
                    'goal': 'Determine optimal coordination strategy'
                }
            }

            # Use AI orchestrator for analysis
            if hasattr(self.orchestrator, 'analyze_coordination_context'):
                try:
                    enhanced_payload = await self.orchestrator.analyze_coordination_context(coordination_payload)

                    if 'ai_insights' in enhanced_payload:
                        insights = enhanced_payload['ai_insights']
                        return {
                            'task_description': task_description,
                            'identified_domains': coordination_payload['tasks'][0]['required_domains'],
                            'available_agents': available_agents,
                            'ai_powered': True,
                            'coordination_strategy': insights.get('coordination_strategy', {}),
                            'risk_assessment': insights.get('risk_assessment', {}),
                            'ai_confidence': insights.get('ai_confidence', 0.5),
                            'message_template': self._generate_ai_message_template(insights, task_description)
                        }
                except Exception as e:
                    logger.warning(f"AI analysis failed, using fallback: {e}")

            # Fallback to basic analysis
            return self._fallback_task_analysis(task_description, available_agents)

        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            return self._fallback_task_analysis(task_description, available_agents)

    def _fallback_task_analysis(self, task_description: str, available_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fallback task analysis when AI is not available."""
        if available_agents is None:
            available_agents = ['agent-1', 'agent-2', 'agent-3', 'agent-5', 'agent-6', 'agent-7', 'agent-8']

        domains = self._extract_domains_from_task(task_description)

        # Simple heuristic-based strategy selection
        if len(domains) > 2:
            strategy = "swarm_coordination"
            agents = available_agents[:4]  # Max 4 for swarm
        elif len(domains) == 2:
            strategy = "bilateral_coordination"
            agents = available_agents[:2]
        else:
            strategy = "solo_execution"
            agents = available_agents[:1] if available_agents else []

        return {
            'task_description': task_description,
            'identified_domains': domains,
            'available_agents': available_agents,
            'ai_powered': False,
            'coordination_strategy': {
                'strategy': strategy,
                'recommended_agents': agents,
                'reasoning': f"Heuristic-based {strategy.replace('_', ' ')}"
            },
            'risk_assessment': {
                'risk_level': 'unknown',
                'identified_risks': ['AI analysis not available'],
                'mitigation_strategies': ['Manual review recommended']
            },
            'message_template': f"Task: {task_description}\\nRecommended approach: {strategy.replace('_', ' ')}"
        }

    def _extract_domains_from_task(self, task_description: str) -> List[str]:
        """Extract technical domains from task description."""
        domains = []
        desc_lower = task_description.lower()

        domain_patterns = {
            'ai': ['ai', 'machine learning', 'neural', 'gpt', 'llm', 'intelligence'],
            'web': ['web', 'frontend', 'ui', 'html', 'css', 'javascript', 'react', 'vue', 'user interface'],
            'api': ['api', 'backend', 'server', 'endpoint', 'rest', 'graphql', 'service'],
            'database': ['database', 'sql', 'data', 'schema', 'migration', 'storage'],
            'infrastructure': ['infrastructure', 'devops', 'deployment', 'docker', 'kubernetes', 'cloud'],
            'architecture': ['architecture', 'design', 'system', 'planning', 'structure'],
            'integration': ['integration', 'messaging', 'coordination', 'orchestration'],
            'testing': ['test', 'qa', 'validation', 'quality', 'debug'],
            'security': ['security', 'auth', 'authentication', 'authorization', 'login']
        }

        for domain, patterns in domain_patterns.items():
            if any(pattern in desc_lower for pattern in patterns):
                domains.append(domain)

        return domains if domains else ['general']

    def _generate_ai_message_template(self, insights: Dict[str, Any], task: str) -> str:
        """Generate coordination message template from AI insights."""
        strategy = insights.get('coordination_strategy', {})
        agents = strategy.get('recommended_agents', [])

        if not agents:
            return f"Task: {task}\\nAI Analysis: No specific agent recommendations available."

        if strategy.get('strategy') == 'solo_execution':
            return f"Task: {task}\\nAI recommends solo execution by {agents[0]}."

        elif len(agents) == 2:
            return f"""A2A COORDINATION REQUEST
From: Agent-{agents[0].split('-')[1]}
To: Agent-{agents[1].split('-')[1]}

COORDINATION REQUEST:
Task: {task}
Proposed approach: Agent-{agents[0].split('-')[1]} leads technical implementation, Agent-{agents[1].split('-')[1]} handles integration
Synergy: Combined expertise for complete solution
Next steps: Agent-{agents[0].split('-')[1]} starts implementation, Agent-{agents[1].split('-')[1]} prepares integration points
Capabilities: Technical implementation + system integration
Timeline: Complete within 2-3 cycles

ETA: Task completion within 3 cycles"""

        else:
            agent_nums = [a.split('-')[1] for a in agents]
            agent_list = ', '.join([f'Agent-{num}' for num in agent_nums])
            assignments = [f"Agent-{agent_nums[i]}: Component {i+1}" for i in range(len(agents))]

            return f"""SWARM COORDINATION REQUEST
To: {agent_list}

COORDINATION REQUEST:
Task: {task}

Assignments:
{chr(10).join(f'• {assignment}' for assignment in assignments)}

Next steps: Start parallel execution
Timeline: Complete within 2 cycles

ETA: All components complete within 2 cycles"""

    async def generate_coordination_message(
        self,
        task: str,
        agent_ids: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a complete coordination message for task and agents.

        Args:
            task: Task description
            agent_ids: List of agent IDs to coordinate with
            context: Additional coordination context

        Returns:
            Formatted coordination message
        """
        analysis = await self.handle_analyze_task(task, agent_ids, context)
        return analysis.get('message_template', f"Task: {task}\\nPlease coordinate execution.")

    async def assess_coordination_risk(
        self,
        agents: List[str],
        tasks: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess coordination risks for given agents and tasks.

        Args:
            agents: List of agent IDs
            tasks: List of task dictionaries
            context: Coordination context

        Returns:
            Risk assessment results
        """
        if not AI_AVAILABLE:
            return {
                'risk_level': 'unknown',
                'message': 'AI risk assessment not available',
                'recommendations': ['Manual risk review recommended']
            }

        # Simple risk assessment
        risks = []

        if len(tasks) > 3:
            risks.append("Multiple concurrent tasks may cause overload")

        if len(agents) > 4:
            risks.append("Large coordination group increases complexity")

        # Check for domain conflicts
        agent_domains = {}
        for agent in agents:
            # Mock domain mapping - in real implementation, this would come from agent profiles
            agent_domains[agent] = [f"domain_{i}" for i in range(len(agent) % 3 + 1)]

        overlapping_domains = set()
        for domains in agent_domains.values():
            overlapping_domains.update(domains)

        if len(overlapping_domains) < len(agents):
            risks.append("Potential domain conflicts between agents")

        risk_level = 'high' if len(risks) > 2 else 'medium' if risks else 'low'

        return {
            'risk_level': risk_level,
            'identified_risks': risks,
            'recommendations': [
                "Regular status check-ins",
                "Clear responsibility boundaries",
                "Escalation path for blockers"
            ] if risks else ["Coordination risk within acceptable parameters"],
            'agent_count': len(agents),
            'task_count': len(tasks)
        }


# Global server instance
server_instance = AIOrchestrationServer()


@server_instance.server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available AI orchestration tools."""
    return [
        types.Tool(
            name="analyze_task",
            description="Analyze a task and provide AI-powered coordination recommendations including optimal agent assignments, coordination strategies, and risk assessments",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the task to analyze"
                    },
                    "available_agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of available agent IDs (optional)",
                        "default": ["agent-1", "agent-2", "agent-3", "agent-5", "agent-6", "agent-7", "agent-8"]
                    },
                    "coordination_context": {
                        "type": "object",
                        "description": "Additional coordination context (optional)"
                    }
                },
                "required": ["task_description"]
            }
        ),
        types.Tool(
            name="generate_coordination_message",
            description="Generate a complete coordination message for task assignment and swarm coordination",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description"
                    },
                    "agent_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent IDs to coordinate with"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional coordination context (optional)"
                    }
                },
                "required": ["task", "agent_ids"]
            }
        ),
        types.Tool(
            name="assess_coordination_risk",
            description="Assess coordination risks for given agents and tasks, providing risk levels and mitigation strategies",
            inputSchema={
                "type": "object",
                "properties": {
                    "agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent IDs"
                    },
                    "tasks": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of task objects with properties like id, priority, dependencies"
                    },
                    "context": {
                        "type": "object",
                        "description": "Coordination context (optional)"
                    }
                },
                "required": ["agents", "tasks"]
            }
        )
    ]


@server_instance.server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool execution requests."""

    try:
        if name == "analyze_task":
            task_description = arguments["task_description"]
            available_agents = arguments.get("available_agents")
            coordination_context = arguments.get("coordination_context")

            result = await server_instance.handle_analyze_task(
                task_description, available_agents, coordination_context
            )

            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "generate_coordination_message":
            task = arguments["task"]
            agent_ids = arguments["agent_ids"]
            context = arguments.get("context")

            message = await server_instance.generate_coordination_message(task, agent_ids, context)

            return [types.TextContent(
                type="text",
                text=message
            )]

        elif name == "assess_coordination_risk":
            agents = arguments["agents"]
            tasks = arguments["tasks"]
            context = arguments.get("context")

            assessment = await server_instance.assess_coordination_risk(agents, tasks, context)

            return [types.TextContent(
                type="text",
                text=json.dumps(assessment, indent=2)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ai-orchestration-server",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())