# Building Agents for the Swarm 🏗️

This guide explains how to build AI agents that leverage the Swarm MCP ecosystem.

## 1. The Concept

The Swarm provides "Muscles" (Tools) and "Brain" (Memory) to your agents via the Model Context Protocol (MCP). Your agent is the "Pilot".

**Architecture:**
```
[Your Agent] <--> [MCP Protocol] <--> [Swarm Servers]
                                      ├── Messaging (Communicate)
                                      ├── Memory (Learn)
                                      ├── Tools (Act)
                                      └── Control (Coordinate)
```

## 2. Connecting to the Swarm

Your agent needs an MCP client. If you are using Cursor or Claude Desktop, this is built-in.

**Configuration (`mcp.json`):**
```json
{
  "mcpServers": {
    "swarm-tools": {
      "command": "swarm-tools-server"
    },
    "swarm-memory": {
      "command": "swarm-memory-server"
    },
    "swarm-messaging": {
      "command": "swarm-messaging-server"
    }
  }
}
```

## 3. Basic Workflows

### A. Assessing the Situation
Use the **Unified Monitor** to see what's happening.
```python
# Tool Call
run_monitor(category="all")
```

### B. Learning & Memory
Don't just run loops; learn from them.
```python
# Save a learning
share_learning(
    agent_id="Agent-X",
    title="Optimization Trick",
    content="Batching DB writes reduced latency by 50%."
)

# Recall later
search_knowledge(query="optimization")
```

### C. Coordination
Don't work alone. Use the **Consensus Engine** for big decisions.
```python
# Propose a change
vote_id = propose_vote(
    topic="Refactor Auth",
    description="Switching to JWT..."
)
```

## 4. Developing Custom Agents

You can use the `swarm_mcp` Python library to build standalone agents without a full MCP client.

```python
from swarm_mcp.core.messaging import get_queue

queue = get_queue()
queue.send("Captain", "I am ready.")
```

## 5. Best Practices

1.  **Check In**: Send a message to the `Captain` when you start.
2.  **Verify**: Use `run_verifier` after making changes.
3.  **Clean Up**: Use `run_cleanup` before signing off.

---
**Go forth and multiply.**
