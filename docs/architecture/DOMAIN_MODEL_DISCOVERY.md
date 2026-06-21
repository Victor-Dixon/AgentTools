# AgentTools Domain Model Discovery

## Product Thesis

AgentTools is the Dream.OS toolbelt and MCP runtime for coordinating agents, tasks, messages, tools, memory, verification, consensus, and operational control surfaces.

## Candidate Domains

| Domain | Current Code Surface | Responsibility |
|---|---|---|
| Agent | `swarm_mcp/core/agent_dna.py` | Agent identity, traits, capabilities |
| Task | `swarm_mcp/core/task_scoring.py`, `swarm_mcp/servers/tasks.py` | Task scoring, routing, lifecycle |
| Message | `swarm_mcp/core/messaging.py`, `swarm_mcp/core/messaging_templates.py`, `swarm_mcp/servers/messaging.py` | Agent communication and routing |
| Memory | `swarm_mcp/core/memory.py`, `swarm_mcp/servers/memory.py`, `swarm_brain/knowledge_base.json` | Persistent knowledge and retrieval |
| Consensus | `swarm_mcp/core/consensus.py`, `swarm_mcp/core/conflict.py` | Voting, disagreement, conflict resolution |
| Work Proof | `swarm_mcp/core/work_proof.py`, `swarm_mcp/core/verification.py` | Evidence, validation, completion proof |
| Coordinator | `swarm_mcp/core/coordinator.py`, `start_swarm.py` | Runtime orchestration |
| Tool Registry | `swarm_mcp/servers/tools.py`, `tools_v2/`, `mcp_servers/` | Tool exposure and execution surface |
| API/UI | `apps/api/`, `apps/web/`, `packages/shared/` | Product control plane |

## Architecture Principle

Keep current modules stable. Add tests and seams before moving code.

## Refactor Policy

1. Characterize existing behavior first.
2. Add domain-level tests.
3. Extract pure functions/classes only after tests exist.
4. Preserve public imports.
5. Do not delete legacy surfaces until mapped.
6. Commit every closed seam separately.
