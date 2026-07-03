# PRD - Repository Product Definition

**Last reviewed:** 2026-07-03  
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`  
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`

This repository is a mixed workspace. The release-critical product lane is **SWARM MCP** (`swarm-mcp`), a Python package for multi-agent coordination over MCP. The same repository also contains an **AgentTools/operator tooling** lane and a separate **Family Focus Board** TypeScript product lane.

---

## 1. Product identity

### Primary lane: SWARM MCP

SWARM MCP is a Python package and MCP toolbelt for multi-agent AI coordination. It models agents, tasks, messages, memory, consensus, conflicts, work proofs, verification, pattern mining, and coordination control surfaces.

**Audience:** AI-agent operators, maintainers, and developers who need local coordination primitives exposed through Python APIs, a CLI, and MCP servers.

**Problem solved:** Multiple AI agents can duplicate work, lose context, make untracked decisions, or claim completion without evidence. SWARM MCP provides file-backed coordination primitives to reduce those failures.

### Secondary lane: AgentTools/operator tooling

AgentTools is the local operator tooling and MCP integration lane: standalone MCP servers, tool registries, repo automation, CI/security/docs helpers, Discord/operator bridges, and migration/salvage utilities.

**Audience:** Repository operators and agent maintainers.

**Problem solved:** Operators need reusable automation and MCP-accessible tools around the coordination package and repository maintenance work.

### Separate lane: Family Focus Board

Family Focus Board is a TypeScript Kanban plus shared Pomodoro/focus-room product under `apps/` and `packages/`.

**Audience:** Family/business users. Exact deployed user base is **Unknown** from this repository.

**Problem solved:** Work needs to be visible as cards, time needs to be protected through Pomodoro sessions, and focus-room state needs to be shared. Web integration is currently incomplete.

---

## 2. In scope

| Lane | In-scope surfaces |
|---|---|
| SWARM MCP | `swarm_mcp/core/`, `swarm_mcp/servers/`, `swarm_mcp/cli.py`, `pyproject.toml`, `tests/`, release docs |
| AgentTools/operator tooling | `mcp_servers/`, `tools/`, `tools_v2/`, CI/security/import/doc helpers, operator MCP catalogs |
| Family Focus Board | `apps/api/`, `apps/web/`, `packages/shared/`, `docs/mvp.md`, migrations and timer contracts |

---

## 3. Out of scope or unknown

- Hosted runtime topology for MCP servers: **Unknown**.
- Active production use of Discord, WordPress, mod/game-server, and player analytics tools: **Unknown**.
- External DreamOS/DreamVault runtime contracts beyond boundary docs in this repo: **Unknown**.
- Replacing implemented behavior as part of this audit: out of scope unless documentation is clearly wrong.

---

## 4. Major requirements derived from current implementation

### SWARM MCP

- Provide public Python exports for coordination primitives.
- Expose a `swarm` CLI with 12 documented subcommands.
- Expose five packaged MCP server entry points:
  - `swarm-messaging-server`
  - `swarm-memory-server`
  - `swarm-tasks-server`
  - `swarm-control-server`
  - `swarm-tools-server`
- Keep runtime package dependencies lightweight; optional/full tooling dependencies remain optional.
- Preserve file-backed operation for messages, memory, consensus, conflicts, proofs, and pattern storage.
- Publish and verify `swarm-mcp==0.6.0` before claiming release completion.

### AgentTools/operator tooling

- Keep `mcp_servers/all_mcp_servers.json` aligned with existing modules/scripts.
- Keep broken `tools_v2` adapters outside the active registry until they instantiate cleanly.
- Keep active/deprecated status visible for legacy tooling.
- Keep security/import/docs/CI helper docs aligned with current command behavior.

### Family Focus Board

- Model orgs, users, boards, lists, cards, focus rooms, Pomodoro sessions, activity logs, inventory categories, and inventory items.
- Use PostgreSQL migrations as the schema source.
- Use `packages/shared` timer state machine for room timer behavior.
- Add real API/web tests, linting, deployment docs, and web/API wiring before treating this as production-ready.

---

## 5. Success metrics

| Area | Success metric |
|---|---|
| SWARM MCP release | `swarm-mcp==0.6.0` publishes to PyPI and passes clean install/import/CLI smoke evidence in `docs/root/MASTER_TASK_LOG.md`. |
| SWARM MCP quality | `python3 -m pytest tests -q` and import-healer coverage gate pass in CI. |
| MCP catalog | Catalog validation reports 0 missing targets. |
| AgentTools/tooling | Active registry entries instantiate; disabled entries remain documented with rationale. |
| Documentation | `README.md`, `PRD.md`, `ROADMAP.md`, `MASTER_TASK_LIST.md`, `docs/root/MASTER_TASK_LOG.md`, `NEXT_UP.md`, `AGENTS.md`, and `docs/architecture/DOMAIN_MODEL.md` agree on identity, status, domain, and next work. |
| Family Focus Board | API/web tests and lint scripts become real gates; shared timer tests continue to pass; deployment requirements are documented. |

---

## 6. Current status

- SWARM MCP M0 Python gates and M2 MCP catalog integrity are complete per SSOT evidence.
- SWARM MCP M1 release proof is blocked because the `v0.6.0` publish job did not receive `PYPI_API_TOKEN`.
- SWARM-004 clean PyPI install verification remains blocked until `0.6.0` is live.
- SWARM-017 npm audit is partial: high severity issues were reduced; remaining moderate `next`/`postcss` risk is accepted only while the TS lane is non-production.
- Documentation/domain model synchronization was updated on 2026-07-03; remaining cleanup is classification of historical/legacy docs and tool surfaces.
