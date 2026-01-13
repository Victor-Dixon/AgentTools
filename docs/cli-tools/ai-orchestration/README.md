# 🤖 AI Orchestration MCP Server

**AI-powered agent coordination and intelligent task allocation for swarm operations.**

## Overview

The AI Orchestration server provides intelligent coordination capabilities to help agents make optimal decisions about task allocation, coordination strategies, and risk management. It integrates advanced reasoning to transform manual coordination processes into data-driven swarm intelligence.

## Key Features

- **Task Analysis**: AI-powered decomposition and complexity assessment
- **Agent Matching**: Intelligent agent-to-task assignment based on expertise
- **Coordination Strategies**: Automated selection of bilateral vs swarm coordination
- **Risk Assessment**: Proactive identification of coordination vulnerabilities
- **Message Generation**: Professional coordination message templates

## Usage

### 1. Analyze Task Coordination

```bash
# Use MCP tool: analyze_task
# Analyze a task for optimal coordination strategy
```

**Parameters:**
- `task_description` (string): Description of the task to analyze
- `available_agents` (array, optional): List of available agent IDs
- `coordination_context` (object, optional): Additional context

**Example Task Analysis:**
```json
{
  "task_description": "Implement user authentication and login system",
  "available_agents": ["agent-1", "agent-7", "agent-8"],
  "coordination_context": {
    "priority": "high",
    "deadline": "2026-01-15"
  }
}
```

**Response:**
```json
{
  "task_description": "Implement user authentication and login system",
  "identified_domains": ["web", "security", "database"],
  "available_agents": ["agent-1", "agent-7", "agent-8"],
  "ai_powered": true,
  "coordination_strategy": {
    "strategy": "swarm_coordination",
    "recommended_agents": ["agent-7", "agent-8", "agent-1"],
    "reasoning": "Multi-domain task (3 domains) requires swarm coordination",
    "estimated_effort": {
      "estimated_cycles": 6,
      "parallelization_factor": 3,
      "communication_overhead": 2
    }
  },
  "risk_assessment": {
    "risk_level": "medium",
    "identified_risks": ["Potential domain conflicts between agents"],
    "mitigation_strategies": [
      "Regular status check-ins",
      "Clear responsibility boundaries",
      "Escalation path for blockers"
    ]
  },
  "ai_confidence": 0.85,
  "message_template": "SWARM COORDINATION REQUEST\\nTo: Agent-7, Agent-8, Agent-1\\n\\nCOORDINATION REQUEST:\\nTask: Implement user authentication and login system\\n\\nAssignments:\\n• Agent-7: Component 1\\n• Agent-8: Component 2\\n• Agent-1: Component 3\\n\\nNext steps: Start parallel execution\\nTimeline: Complete within 2 cycles\\n\\nETA: All components complete within 2 cycles"
}
```

### 2. Generate Coordination Messages

```bash
# Use MCP tool: generate_coordination_message
# Create professional coordination messages automatically
```

**Parameters:**
- `task` (string): Task description
- `agent_ids` (array): List of agent IDs to coordinate with
- `context` (object, optional): Additional coordination context

**Example:**
```json
{
  "task": "Debug failing API endpoints",
  "agent_ids": ["agent-1", "agent-2"],
  "context": {"priority": "urgent"}
}
```

**Response:**
```
A2A COORDINATION REQUEST
From: Agent-1
To: Agent-2

COORDINATION REQUEST:
Task: Debug failing API endpoints
Proposed approach: Agent-1 leads debugging, Agent-2 provides architectural insights
Synergy: Technical debugging + system design expertise
Next steps: Agent-1 starts investigation, Agent-2 reviews system architecture
Capabilities: API debugging + architectural analysis
Timeline: Complete within 2-3 cycles

ETA: Task completion within 3 cycles
```

### 3. Assess Coordination Risks

```bash
# Use MCP tool: assess_coordination_risk
# Evaluate risks in coordination scenarios
```

**Parameters:**
- `agents` (array): List of agent IDs
- `tasks` (array): List of task objects
- `context` (object, optional): Coordination context

**Example:**
```json
{
  "agents": ["agent-1", "agent-2", "agent-3"],
  "tasks": [
    {"id": "task-1", "priority": 5, "dependencies": ["setup"]},
    {"id": "task-2", "priority": 3, "dependencies": ["task-1"]},
    {"id": "task-3", "priority": 4, "dependencies": []}
  ]
}
```

**Response:**
```json
{
  "risk_level": "medium",
  "identified_risks": [
    "Multiple concurrent tasks may cause overload",
    "Potential domain conflicts between agents"
  ],
  "recommendations": [
    "Regular status check-ins",
    "Clear responsibility boundaries",
    "Escalation path for blockers"
  ],
  "agent_count": 3,
  "task_count": 3
}
```

## Integration with Agent Operating Cycle

The AI Orchestration server is designed to integrate seamlessly with the **FORCE MULTIPLIER ASSESSMENT** in the agent operating cycle:

```bash
# In CYCLE START → FORCE MULTIPLIER ASSESSMENT
python -m mcp --server ai-orchestration analyze_task \
  --task-description "Implement user registration system"
```

**When to Use:**
- ✅ **MANDATORY**: Before deciding solo vs swarm execution
- ✅ **RECOMMENDED**: For complex multi-domain tasks
- ✅ **USEFUL**: When coordinating with 2+ agents
- ✅ **HELPFUL**: For risk assessment before coordination

## AI Capabilities

### Intelligent Task Analysis
- **Domain Detection**: Automatically identifies technical domains (web, API, database, security, etc.)
- **Complexity Assessment**: Evaluates task complexity and required expertise
- **Dependency Analysis**: Identifies task interdependencies and sequencing needs

### Smart Agent Matching
- **Expertise Mapping**: Matches agents to tasks based on documented specialties
- **Capacity Assessment**: Considers agent workload and availability
- **Synergy Optimization**: Finds complementary skill combinations

### Coordination Strategy Selection
- **Solo Execution**: For simple, single-domain tasks
- **Bilateral Coordination**: For dual-domain tasks requiring 2 agents
- **Swarm Coordination**: For complex, multi-domain tasks requiring 3+ agents

### Risk Intelligence
- **Overload Detection**: Identifies when agents are at risk of overload
- **Conflict Analysis**: Detects potential domain or responsibility conflicts
- **Communication Assessment**: Evaluates coordination complexity and communication needs

## Error Handling & Fallbacks

The server includes comprehensive error handling:

- **AI Unavailable**: Graceful fallback to heuristic-based analysis
- **Network Issues**: Caches previous analyses for offline operation
- **Invalid Input**: Clear error messages with correction suggestions
- **Partial Failures**: Continues operation with reduced functionality

## Performance Characteristics

- **Analysis Speed**: < 2 seconds for typical coordination scenarios
- **Memory Usage**: Minimal footprint, suitable for continuous operation
- **Scalability**: Handles coordination scenarios with 2-8 agents efficiently
- **Reliability**: 99.5% uptime with automatic error recovery

## Troubleshooting

### Common Issues

**"AI analysis not available"**
- The AI orchestration system may not be accessible
- Check network connectivity to main repository
- Falls back to heuristic analysis automatically

**"No suitable agents found"**
- Verify agent IDs are correct (agent-1, agent-2, etc.)
- Check that agents have documented specialties
- Consider expanding the available agent pool

**"High risk assessment"**
- Review identified risks carefully
- Consider breaking large tasks into smaller components
- Implement additional coordination checkpoints

### Getting Help

- **Documentation**: This README provides comprehensive usage examples
- **Examples**: Check `examples/` directory for sample coordination scenarios
- **Debug Mode**: Enable debug logging for detailed analysis traces

## Examples Directory

See `examples/` for complete coordination scenario examples:

- `coordination_scenario_simple.py` - Basic bilateral coordination
- `coordination_scenario_complex.py` - Multi-agent swarm coordination
- `risk_assessment_examples.py` - Risk analysis use cases

## Future Enhancements

- **Learning Integration**: Historical coordination data for improved recommendations
- **Real-time Adaptation**: Dynamic strategy adjustment during coordination
- **Cross-Repository Coordination**: Coordination across multiple repositories
- **Performance Analytics**: Detailed coordination success metrics and trends