# Domain Model Discovery

**Last reviewed:** 2026-07-03  
**Status:** Superseded by canonical model

The complete repository domain model now lives at:

- `docs/architecture/DOMAIN_MODEL.md`

This discovery stub is retained for compatibility with older references. Use the canonical model for:

- core domain and subdomains,
- major entities and value objects,
- services,
- relationships,
- data flow,
- user interactions,
- external integrations,
- feature-to-domain mapping,
- repository audit findings,
- unknowns.

Current verified lane split:

| Lane | Domain | Primary paths |
|---|---|---|
| SWARM MCP | Multi-agent AI coordination over MCP | `swarm_mcp/`, `tests/`, `integration/` |
| AgentTools/operator tooling | Local MCP servers, tool registries, repo automation | `mcp_servers/`, `tools/`, `tools_v2/` |
| Family Focus Board | Kanban plus shared Pomodoro/focus room product | `apps/api/`, `apps/web/`, `packages/shared/` |
