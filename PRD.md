# PRD - AgentTools

## Vision
AgentTools is the Dream.OS operator control-plane and toolbelt layer.

It provides MCP server infrastructure, operator tooling, automation surfaces, integration bridges, repo orchestration, and governance-support utilities.

AgentTools is not the runtime swarm engine. It is the operational surface around Dream.OS.

## Core Responsibilities
- MCP server platform
- Operator tooling
- Repo automation
- CI/CD helpers
- Documentation generation
- Discord/Cursor/external integration bridges
- Durable automation utilities

## Canonical Boundaries
- AgentTools owns operator/control-plane tooling.
- DreamOS owns runtime/swarm execution.
- DreamVault owns governance, inventory, reports, and promotion manifests.

## Current Risks
- Legacy/deprecated tools mixed with active surfaces.
- Partial migration state in `tools_v2`.
- Some test gates depend on sibling canonical repos.

## Success Metrics
- Stable MCP server registry.
- Clear ownership boundaries.
- Passing local test gate.
- Promotion-ready reusable utilities.
