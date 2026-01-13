#!/usr/bin/env python3
"""
🐺 WE ARE SWARM - Two Agent Setup Example

Demonstrates basic multi-agent coordination with just two agents.
This is the minimal viable swarm - showing how agents can work together.

Usage:
    python examples/two_agent_setup.py
"""

import asyncio
from swarm_mcp.core.consensus import ConsensusEngine
from swarm_mcp.core.messaging import MessagingCoordinator
from swarm_mcp.core.agent_dna import AgentDNA


async def main():
    """Run a simple two-agent coordination example."""

    print("🐺 WE ARE SWARM - Two Agent Setup")
    print("=" * 50)

    # Initialize core components
    consensus = ConsensusEngine()
    messaging = MessagingCoordinator()
    dna_tracker = AgentDNA()

    # Define our two agents
    agents = {
        "agent_1": {
            "name": "Research Agent",
            "capabilities": ["web_search", "data_analysis", "pattern_recognition"],
            "specialty": "Information gathering and analysis"
        },
        "agent_2": {
            "name": "Execution Agent",
            "capabilities": ["code_generation", "testing", "deployment"],
            "specialty": "Implementation and execution"
        }
    }

    print("📊 Agents Initialized:")
    for agent_id, info in agents.items():
        print(f"  • {agent_id}: {info['name']} ({info['specialty']})")

    # Register agents in DNA tracker
    for agent_id, info in agents.items():
        dna_tracker.register_agent(agent_id, info)

    print("\n🧬 Agent DNA Profiles:")
    for agent_id in agents:
        profile = dna_tracker.get_profile(agent_id)
        print(f"  • {agent_id}: {len(profile.get('capabilities', []))} capabilities")

    # Simulate a coordination task
    task = {
        "id": "example_task_001",
        "description": "Research and implement a simple web scraper",
        "requirements": ["Python", "requests", "beautifulsoup4"],
        "deadline": "2026-01-15"
    }

    print(f"\n🎯 Task: {task['description']}")
    print(f"📋 Requirements: {', '.join(task['requirements'])}")

    # Agent 1 (Research) analyzes requirements
    print("\n🔍 Agent-1 (Research) analyzing requirements...")
    research_findings = {
        "libraries": ["requests==2.31.0", "beautifulsoup4==4.12.2"],
        "complexity": "Low",
        "estimated_time": "2 hours",
        "dependencies": ["lxml parser for better performance"]
    }

    # Agent 2 (Execution) proposes implementation
    print("⚙️ Agent-2 (Execution) proposing implementation...")
    implementation_plan = {
        "approach": "Create modular scraper with error handling",
        "components": ["HTTP client", "HTML parser", "Data extraction", "Error handling"],
        "testing": ["Unit tests", "Integration tests", "Error scenarios"]
    }

    # Consensus voting on approach
    print("\n🗳️ Consensus Voting:")
    vote_options = ["Modular approach with error handling", "Simple script approach", "Async implementation"]

    # Simulate votes
    votes = {
        "agent_1": vote_options[0],  # Prefers robust implementation
        "agent_2": vote_options[0],  # Agrees with research agent
    }

    consensus_result = consensus.vote("implementation_approach", votes, vote_options)
    print(f"  📊 Consensus: {consensus_result['winner']}")
    print(f"  ✅ Agreement: {consensus_result['agreement_percentage']}%")

    # Execute the agreed approach
    print("\n🚀 Implementation Starting...")
    print("  📝 Creating scraper module...")
    print("  🧪 Adding unit tests...")
    print("  📦 Packaging solution...")

    # Simulate successful completion
    print("\n✅ Task Completed Successfully!")
    print("  📊 Code: 45 lines")
    print("  🧪 Tests: 8 tests passing")
    print("  📈 Coverage: 95%")

    print("\n🎉 Two-Agent Coordination Complete!")
    print("The pack hunts together. Alone we are strong, together we are unstoppable.")


if __name__ == "__main__":
    asyncio.run(main())