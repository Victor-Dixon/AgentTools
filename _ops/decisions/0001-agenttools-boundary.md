# 0001 - AgentTools Canonical Boundary

## Decision
AgentTools is the canonical Dream.OS operator tooling and MCP integration layer.

It is not the runtime swarm engine.

## AgentTools Owns
- MCP servers
- operational tooling
- integration bridges
- repo automation
- CI/CD helpers
- Discord integrations
- documentation tooling
- utility orchestration

## AgentTools Does Not Own
- swarm runtime cognition
- transport FSM lifecycle
- autonomous execution kernel
- canonical governance inventory

## External Canonical Owners
| Concern | Canonical Repo |
|---|---|
| Runtime/swarm execution | DreamOS / Dream.os-Core |
| Governance/inventory | DreamVault |
| Operator/control-plane tooling | AgentTools |

## Consequence
Reusable operational tooling promotes into AgentTools. Runtime cognition promotes into DreamOS/Dream.os-Core.
