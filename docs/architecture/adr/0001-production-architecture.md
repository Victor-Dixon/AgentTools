# ADR-0001: AgentTools Production Architecture

## Status

Accepted for stabilization.

## Context

AgentTools currently contains active runtime code, MCP server surfaces, web/API candidates, legacy tools, archives, and generated artifacts. The repo must be restored into a production-ready product without breaking existing behavior.

## Decision

AgentTools will use a layered architecture:

1. Domain layer
   - Pure business rules.
   - No filesystem, network, or framework dependency.
   - Owns agents, tasks, messages, memory contracts, consensus, work proof, and verification rules.

2. Application layer
   - Coordinates domain behavior.
   - Owns orchestration, routing, recovery, scoring flows, and runtime decisions.

3. Adapter layer
   - Exposes domain/application behavior through MCP servers, API routes, web UI, CLI, and integrations.

4. Legacy/archive layer
   - Historical tools and nested apps remain in place until classified and promoted or archived.

## Current Boundary Mapping

| Layer | Paths |
|---|---|
| Domain | `swarm_mcp/core/*.py` |
| Application | `swarm_mcp/core/coordinator.py`, `brain.py`, `memory.py`, `recovery.py`, `pattern_miner.py` |
| Adapters | `swarm_mcp/servers/`, `mcp_servers/`, `apps/api/`, `apps/web/`, `integration/` |
| Shared Contracts | `packages/shared/` |
| Archive / Legacy | `tools/`, `kanban-scheduler/`, optional module folders |

## Testing Strategy

- Characterization tests protect existing behavior.
- Domain tests define restored behavior.
- Adapter tests validate importability and contract wiring.
- Production gate prevents generated artifacts and broken validation.

## Refactor Constraint

No public import path should be broken without a compatibility shim and test coverage.

## Consequences

- Slower initial cleanup.
- Safer restoration.
- Clear path to promote legacy tools into the active product.
