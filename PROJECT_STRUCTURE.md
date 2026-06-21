# Project Structure

AgentTools is the Dream.OS canonical toolbelt repository.

## Primary Directories

| Path | Purpose |
|---|---|
| `tools/` | Operator tools, Discord utilities, repo intelligence helpers, and automation entrypoints |
| `swarm_mcp/` | MCP/server-side swarm tooling and work-proof primitives |
| `tests/` | Pytest verification suite for contracts, adapters, tools, docs, and migration boundaries |
| `docs/` | Governance notes, compatibility declarations, migration docs, and operator documentation |
| `examples/` | Demo/run proof examples |
| `.github/workflows/` | CI workflows |

## Repository Boundary

AgentTools owns toolbelt and integration surfaces. It adapts to DreamOS/DreamVault contracts but does not own canonical core runtime schemas.
