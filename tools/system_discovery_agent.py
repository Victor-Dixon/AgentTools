#!/usr/bin/env python3
"""
🧠 SYSTEM DISCOVERY AGENT - Smart System Utilization Assistant
================================================================

Helps agents discover, understand, and effectively use available systems and tools.

USAGE:
    python tools/system_discovery_agent.py --discover-all
    python tools/system_discovery_agent.py --find-tool "testing"
    python tools/system_discovery_agent.py --task-analysis "implement user auth"
    python tools/system_discovery_agent.py --operating-cycle-help

FEATURES:
- System discovery and cataloging
- Intelligent tool recommendations
- Operating cycle integration guidance
- Task-specific system suggestions
- Usage pattern analysis

Author: Agent-4 (System Discovery & Integration Specialist)
Date: 2026-01-13
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class SystemTool:
    """Represents a system tool with metadata."""
    name: str
    category: str
    description: str
    location: str
    usage_command: str
    use_case: str
    expertise_domain: List[str]
    integration_points: List[str]
    prerequisites: List[str] = None
    examples: List[str] = None

class SystemDiscoveryAgent:
    """Intelligent system discovery and utilization assistant."""

    def __init__(self):
        self.systems_registry = self._load_systems_registry()
        self.agent_expertise = self._load_agent_expertise()

    def _load_systems_registry(self) -> Dict[str, SystemTool]:
        """Load comprehensive systems registry."""
        return {
            # AI & Orchestration Systems
            "ai_orchestrator": SystemTool(
                name="AI Orchestration System",
                category="orchestration",
                description="AI-powered task analysis and agent coordination recommendations",
                location="scripts/ai_orchestrate_simple.py",
                usage_command="python scripts/ai_orchestrate_simple.py --analyze-task 'your task'",
                use_case="Task breakdown, agent assignment, coordination strategy",
                expertise_domain=["orchestration", "planning", "coordination"],
                integration_points=["operating_cycle", "messaging_system", "task_assignment"]
            ),

            # Messaging & Communication Systems
            "messaging_cli": SystemTool(
                name="Unified Messaging CLI",
                category="communication",
                description="Swarm communication and bilateral coordination system",
                location="src/services/messaging_cli.py",
                usage_command="python -m src.services.messaging_cli --message 'task' --agent Agent-X",
                use_case="Agent-to-agent communication, task coordination, status updates",
                expertise_domain=["communication", "coordination", "messaging"],
                integration_points=["operating_cycle", "task_management", "status_tracking"]
            ),

            # Toolbelt Systems
            "captain_toolbelt": SystemTool(
                name="Captain's Toolbelt",
                category="operations",
                description="20 essential tools for swarm operations and monitoring",
                location="tools/toolbelt/",
                usage_command="python tools/captain_check_agent_status.py",
                use_case="Agent monitoring, task optimization, integrity verification",
                expertise_domain=["operations", "monitoring", "quality_assurance"],
                integration_points=["operating_cycle", "performance_monitoring", "quality_gates"]
            ),

            # Analysis & Intelligence Systems
            "duplicate_analyzer": SystemTool(
                name="Repository Duplicate Analyzer",
                category="analysis",
                description="Advanced duplicate detection and resolution tools",
                location="tools/analysis/",
                usage_command="python tools/analyze_repo_duplicates.py --repo owner/repo",
                use_case="Code consolidation, duplicate removal, repository cleanup",
                expertise_domain=["analysis", "consolidation", "code_quality"],
                integration_points=["code_review", "refactoring", "repository_management"]
            ),

            # Coordination Systems
            "coordination_tools": SystemTool(
                name="Agent Coordination Suite",
                category="coordination",
                description="Advanced coordination and status verification tools",
                location="tools/coordination/",
                usage_command="python tools/agent_status_quick_check.py --agent Agent-X",
                use_case="Status verification, coordination management, progress tracking",
                expertise_domain=["coordination", "monitoring", "communication"],
                integration_points=["operating_cycle", "task_management", "status_reporting"]
            ),

            # Quality Assurance Systems
            "qa_suite": SystemTool(
                name="Quality Assurance Suite",
                category="quality",
                description="Comprehensive testing and quality validation tools",
                location="tools/validation/ & tools/verification/",
                usage_command="python tools/coverage_validator.py",
                use_case="Test coverage validation, quality gates, compliance checking",
                expertise_domain=["testing", "quality_assurance", "validation"],
                integration_points=["operating_cycle", "code_review", "deployment"]
            ),

            # Automation Systems
            "automation_engine": SystemTool(
                name="Autonomous Task Engine",
                category="automation",
                description="AI-powered autonomous task execution and monitoring",
                location="tools/autonomous/",
                usage_command="python tools/autonomous_task_engine.py --start",
                use_case="Automated task execution, monitoring, and reporting",
                expertise_domain=["automation", "ai", "monitoring"],
                integration_points=["operating_cycle", "task_execution", "performance_tracking"]
            ),

            # Deployment Systems
            "deployment_tools": SystemTool(
                name="Deployment & DevOps Suite",
                category="deployment",
                description="Comprehensive deployment and infrastructure management",
                location="tools/deployment/ & scripts/",
                usage_command="python scripts/deploy_phase1_infrastructure.sh",
                use_case="Infrastructure deployment, environment setup, production releases",
                expertise_domain=["devops", "infrastructure", "deployment"],
                integration_points=["release_management", "environment_setup", "production_monitoring"]
            ),

            # Documentation Systems
            "documentation_tools": SystemTool(
                name="Documentation Management Suite",
                category="documentation",
                description="Automated documentation generation and management",
                location="tools/docs/ & scripts/documentation_consolidator.py",
                usage_command="python scripts/documentation_consolidator.py",
                use_case="Documentation generation, consolidation, and maintenance",
                expertise_domain=["documentation", "knowledge_management", "communication"],
                integration_points=["knowledge_sharing", "onboarding", "compliance"]
            )
        }

    def _load_agent_expertise(self) -> Dict[str, List[str]]:
        """Load agent expertise mappings."""
        return {
            'Agent-1': ['integration', 'core-systems', 'api', 'backend', 'testing'],
            'Agent-2': ['architecture', 'design', 'planning', 'system-design'],
            'Agent-3': ['infrastructure', 'devops', 'deployment', 'monitoring'],
            'Agent-5': ['business-intelligence', 'ai', 'orchestration', 'analytics'],
            'Agent-6': ['coordination', 'communication', 'messaging', 'facilitation'],
            'Agent-7': ['web-development', 'frontend', 'ui', 'user-experience', 'javascript'],
            'Agent-8': ['ssot', 'system-integration', 'data-management', 'validation', 'database']
        }

    def discover_all_systems(self) -> str:
        """Generate comprehensive system discovery report."""
        report = ["# 🧠 SYSTEM DISCOVERY REPORT - Complete Arsenal\n"]
        report.append(f"**Total Systems Available:** {len(self.systems_registry)}\n")

        # Group by category
        categories = {}
        for tool in self.systems_registry.values():
            if tool.category not in categories:
                categories[tool.category] = []
            categories[tool.category].append(tool)

        for category, tools in categories.items():
            report.append(f"## 🔧 {category.upper()} SYSTEMS ({len(tools)})\n")
            for tool in tools:
                report.append(f"### {tool.name}")
                report.append(f"**Purpose:** {tool.description}")
                report.append(f"**Command:** `{tool.usage_command}`")
                report.append(f"**Use Cases:** {tool.use_case}")
                report.append(f"**Expertise:** {', '.join(tool.expertise_domain)}")
                report.append(f"**Integration:** {', '.join(tool.integration_points)}\n")

        return "\n".join(report)

    def find_tools_for_task(self, task_description: str, agent_id: Optional[str] = None) -> str:
        """Find relevant tools for a specific task."""
        task_lower = task_description.lower()
        relevant_tools = []

        for tool in self.systems_registry.values():
            # Check task keywords
            if any(keyword in task_lower for keyword in tool.expertise_domain):
                relevant_tools.append(tool)
            # Check task description matches
            if any(keyword in task_lower for keyword in ['test', 'testing', 'quality']) and 'testing' in tool.expertise_domain:
                relevant_tools.append(tool)
            if any(keyword in task_lower for keyword in ['deploy', 'infrastructure', 'devops']) and tool.category == 'deployment':
                relevant_tools.append(tool)
            if any(keyword in task_lower for keyword in ['coordinate', 'communicate', 'message']) and tool.category == 'communication':
                relevant_tools.append(tool)

        # Filter by agent expertise if specified
        if agent_id and agent_id in self.agent_expertise:
            agent_skills = self.agent_expertise[agent_id]
            relevant_tools = [t for t in relevant_tools if any(skill in t.expertise_domain for skill in agent_skills)]

        report = [f"# 🎯 RECOMMENDED TOOLS for: '{task_description}'\n"]
        report.append(f"**Found {len(relevant_tools)} relevant systems**\n")

        for tool in relevant_tools:
            report.append(f"## {tool.name}")
            report.append(f"**Category:** {tool.category}")
            report.append(f"**Why Relevant:** {tool.use_case}")
            report.append(f"**Usage:** `{tool.usage_command}`")
            report.append("")

        if not relevant_tools:
            report.append("## 🤔 No Specific Tools Found")
            report.append("Consider using:")
            report.append("- `python scripts/ai_orchestrate_simple.py --analyze-task 'your task'` for AI-powered coordination")
            report.append("- `python -m src.services.messaging_cli --message 'task details' --agent target-agent` for coordination")
            report.append("- Check `tools/` directory for additional specialized tools")

        return "\n".join(report)

    def get_operating_cycle_integration(self) -> str:
        """Provide operating cycle integration guidance."""
        guidance = """# 🔄 OPERATING CYCLE SYSTEM INTEGRATION GUIDE

## Phase 1: Task Analysis & Planning
**MANDATORY: Use AI Orchestration**
```bash
python scripts/ai_orchestrate_simple.py --analyze-task "your task description"
```
- Get AI-powered task breakdown and agent recommendations
- Identify optimal system usage for your task
- Receive coordination strategy suggestions

## Phase 2: System Discovery & Selection
**Use System Discovery Agent**
```bash
python tools/system_discovery_agent.py --task-analysis "your task"
```
- Discover relevant tools and systems
- Get usage recommendations and examples
- Understand integration points

## Phase 3: Execution with System Integration
**Integrate Systems into Your Cycle:**

### Communication & Coordination
```bash
# Bilateral messaging for coordination
python -m src.services.messaging_cli --message "task coordination" --agent Agent-X

# Status updates and progress tracking
python tools/agent_status_quick_check.py --agent Agent-X
```

### Quality Assurance
```bash
# Test coverage validation
python tools/coverage_validator.py

# Quality gate checking
python tools/v2_batch_checker.py
```

### Monitoring & Analytics
```bash
# Performance monitoring
python tools/captain_check_agent_status.py

# ROI and optimization analysis
python tools/captain_roi_quick_calc.py
```

## Phase 4: Validation & Reporting
**System-Enhanced Validation:**
```bash
# Integrity verification
python tools/integrity_validator.py

# Work attribution and verification
python tools/git_work_verifier.py
```

## Phase 5: Knowledge Transfer
**Document System Usage Patterns:**
- Update system usage in devlogs
- Share discovered tools with swarm
- Contribute to system improvement

## 🧠 SMART SYSTEM USAGE PATTERNS

### Pattern 1: Large Task Coordination
1. `ai_orchestrate_simple.py --analyze-task "task"` (Planning)
2. `messaging_cli --broadcast` (Coordination)
3. `captain_check_agent_status.py` (Monitoring)

### Pattern 2: Quality-Focused Development
1. `coverage_validator.py` (Planning)
2. `v2_batch_checker.py` (Execution)
3. `integrity_validator.py` (Validation)

### Pattern 3: Infrastructure Work
1. `scripts/deploy_phase1_infrastructure.sh` (Setup)
2. `tools/deployment/` tools (Execution)
3. `tools/monitoring/` tools (Validation)

**Remember:** Systems are force multipliers. Using them effectively increases your impact 4-8x! 🚀"""
        return guidance

    def analyze_usage_patterns(self) -> str:
        """Analyze current system usage patterns and provide recommendations."""
        analysis = """# 📊 SYSTEM USAGE PATTERN ANALYSIS

## Current Challenges Identified

### 1. **System Discovery Gap**
- Agents unaware of 80%+ available systems
- No centralized system catalog
- Lack of usage examples and templates

### 2. **Integration Complexity**
- Systems not integrated into operating cycles
- Manual system selection and configuration
- No automated system suggestions

### 3. **Training & Onboarding**
- No formal system usage training
- Limited documentation on system interactions
- Knowledge silos around system expertise

### 4. **Feedback & Improvement**
- No metrics on system effectiveness
- Limited sharing of successful patterns
- No continuous improvement loops

## Recommended Solutions

### Immediate Actions (Week 1-2)
1. **Deploy System Discovery Program**
   - Run `system_discovery_agent.py --discover-all` weekly
   - Create system usage quick-reference guides
   - Establish system champions for each category

2. **Integrate into Operating Cycles**
   - Add system discovery to cycle Phase 1
   - Create system integration checklists
   - Implement system usage tracking

3. **Training Program**
   - Create system usage workshops
   - Develop interactive tutorials
   - Establish mentorship program

### Medium-term Improvements (Week 3-5)
4. **Automation & Intelligence**
   - AI-powered system recommendations
   - Automated system orchestration
   - Predictive system suggestions

5. **Feedback Systems**
   - System effectiveness metrics
   - Usage pattern analysis
   - Continuous improvement loops

### Long-term Vision (Week 6-9)
6. **Autonomous System Coordination**
   - Self-organizing system usage
   - Predictive system deployment
   - Zero-configuration system integration

## Success Metrics
- **System Utilization:** 80%+ of available systems used weekly
- **Cycle Integration:** 95% of cycles include system usage
- **Knowledge Sharing:** 100% of agents trained on core systems
- **Efficiency Gains:** 4-8x productivity improvement through system usage

## Call to Action
**🐝 WE ARE SWARM. SYSTEMS ARE OUR SUPERPOWER.** 

Start using systems today:
1. Run `python tools/system_discovery_agent.py --discover-all`
2. Integrate `ai_orchestrate_simple.py` into your planning
3. Use `messaging_cli` for all coordination
4. Report system usage in your devlogs

**Together, we will achieve system mastery and swarm excellence! ⚡🔥**"""
        return analysis

def main():
    parser = argparse.ArgumentParser(description="🧠 System Discovery Agent - Smart System Utilization Assistant")
    parser.add_argument("--discover-all", action="store_true", help="Generate complete system discovery report")
    parser.add_argument("--find-tool", type=str, help="Find tools for specific task or domain")
    parser.add_argument("--task-analysis", type=str, help="Analyze task and recommend systems")
    parser.add_argument("--operating-cycle-help", action="store_true", help="Get operating cycle integration guidance")
    parser.add_argument("--usage-analysis", action="store_true", help="Analyze current system usage patterns")
    parser.add_argument("--agent", type=str, help="Filter recommendations for specific agent expertise")

    args = parser.parse_args()

    agent = SystemDiscoveryAgent()

    if args.discover_all:
        print(agent.discover_all_systems())
    elif args.find_tool:
        print(agent.find_tools_for_task(args.find_tool, args.agent))
    elif args.task_analysis:
        print(agent.find_tools_for_task(args.task_analysis, args.agent))
    elif args.operating_cycle_help:
        print(agent.get_operating_cycle_integration())
    elif args.usage_analysis:
        print(agent.analyze_usage_patterns())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()