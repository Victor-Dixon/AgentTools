# PROJECT_STRUCTURE

**Last updated:** 2026-07-03
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`

This file documents the current repository layout, major service relationships, shared libraries, data flow, and infrastructure topology observed during the workspace audit. The canonical domain model lives in `docs/architecture/DOMAIN_MODEL.md`.

---

## Repository identity

This repository currently contains **multiple active and semi-active lanes**:

The `origin/master` version summarizes this repository as **AgentTools**, the Dream.OS canonical toolbelt repository. This audit preserves that boundary as the operator-tooling lane while also documenting the SWARM MCP package and Family Focus Board workspace that are present in this checkout.

1. **SWARM MCP** — Python package and public release lane.
2. **AgentTools/operator tooling** — local toolbelt, MCP helpers, migration/security/automation scripts.
3. **Family Focus Board** — TypeScript web/API/shared workspace.
4. **Legacy/archive/quarantine material** — deprecated scripts, historical plans, and extracted archive pointers.

The canonical project-status SSOT is `docs/root/MASTER_TASK_LOG.md`. Root-level planning files are convenience/audit deliverables unless they explicitly say otherwise.

---

## Top-level layout

| Path | Purpose | Current state |
|---|---|---|
| `swarm_mcp/` | Python package for multi-agent coordination over MCP. | Active, release-critical. |
| `swarm_mcp/core/` | Coordination primitives and domain/application logic. | Active. |
| `swarm_mcp/servers/` | Packaged MCP server modules exposed by `pyproject.toml` console scripts. | Active; 5 server modules. |
| `swarm_mcp/cli.py` | `swarm` operator CLI. | Active; 12 subcommands. |
| `tests/` | Python test suite for package, docs/contracts, MCP servers, and tool compatibility. | Active; SSOT evidence on 2026-06-29 reports `72 passed, 1 skipped`. |
| `integration/` | Example MCP host/server configs and integration bridge. | Secondary active. |
| `mcp_servers/` | Standalone MCP server scripts for local/operator workflows. | Active/secondary; catalog validation currently reports 0 missing targets. |
| `tools/` | Legacy and current automation scripts plus CLI dispatcher. | Mixed active and legacy. |
| `tools_v2/` | Adapter-driven toolbelt V2 registry and categories. | In-progress; not yet fully healthy. |
| `apps/api/` | Fastify/Postgres API for Family Focus Board. | Active scaffold/product lane; lacks tests. |
| `apps/web/` | Next.js web app for Family Focus Board. | Scaffold-level. |
| `packages/shared/` | Shared TypeScript types and timer state machine. | Active; has Vitest coverage. |
| `examples/` | Python package usage examples. | Support docs/examples. |
| `docs/` | Architecture, release, audit, roadmap, archive, and planning docs. | Mixed current and historical. |
| `docs/root/` | Historical root docs plus canonical `MASTER_TASK_LOG.md`. | SSOT file active; several sibling docs stale. |
| `.github/workflows/` | CI/CD workflows. | Python-only workflow plus tag-based PyPI publish. |
| `_ops/` | Operational reports. | Historical/support. |
| `package.json` | npm workspace root for Family Focus Board. | Active but not covered by CI. |
| `pyproject.toml` | Python package metadata, dependencies, scripts, test config. | Active release config. |

---

## Python package structure

```text
swarm_mcp/
├── __init__.py
├── cli.py
├── core/
│   ├── agent_dna.py
│   ├── brain.py
│   ├── conflict.py
│   ├── consensus.py
│   ├── coordinator.py
│   ├── memory.py
│   ├── messaging.py
│   ├── messaging_templates.py
│   ├── pattern_miner.py
│   ├── recovery.py
│   ├── task_scoring.py
│   ├── verification.py
│   └── work_proof.py
├── servers/
│   ├── control.py
│   ├── memory.py
│   ├── messaging.py
│   ├── tasks.py
│   └── tools.py
└── tools/
    └── __init__.py
```

### Package entry points

Defined in `pyproject.toml`:

- `swarm = swarm_mcp.cli:main`
- `swarm-messaging-server = swarm_mcp.servers.messaging:main`
- `swarm-memory-server = swarm_mcp.servers.memory:main`
- `swarm-tasks-server = swarm_mcp.servers.tasks:main`
- `swarm-control-server = swarm_mcp.servers.control:main`
- `swarm-tools-server = swarm_mcp.servers.tools:main`

### Core data flow

```text
Agent/operator
  -> swarm CLI or MCP client
  -> swarm_mcp.servers.* / swarm_mcp.cli
  -> swarm_mcp.core.* primitives
  -> file-backed state / git state / local workspace artifacts
  -> result back to agent/operator
```

The package is intentionally lightweight at runtime (`dependencies = []`), but tests currently import tooling code that requires optional dependencies.

---

## MCP service relationships

There are two MCP layers:

### Packaged/public MCP layer

Located in `swarm_mcp/servers/` and intended for the `swarm-mcp` Python package. These are release-critical.

| Server | Module | Role |
|---|---|---|
| Swarm messaging | `swarm_mcp.servers.messaging` | Send/broadcast agent messages. |
| Swarm memory | `swarm_mcp.servers.memory` | Shared memory/knowledge operations. |
| Swarm tasks | `swarm_mcp.servers.tasks` | Task queue and Stage 4 task tooling. |
| Swarm control | `swarm_mcp.servers.control` | Coordination/status/control operations. |
| Swarm tools | `swarm_mcp.servers.tools` | Adapter over legacy toolbelt commands. |

### Standalone/operator MCP layer

Located in `mcp_servers/`. These are local/operator automation surfaces, not currently packaged as `swarm-mcp` console scripts.

Observed script count: **27** `*_server.py` files.

Major categories:

- core operations: mission control, messaging, task manager, swarm brain;
- development/quality: refactoring, git operations, V2 compliance, testing, memory safety, code quality;
- infrastructure/monitoring: website manager/audit, observability, performance profiler;
- DevOps automation: dependency management, release management, CI/CD helper, environment setup, security scanner, docs generator, database operations;
- secondary/game/community surfaces: mod deployment, server monitoring, backup automation, Discord integration, player analytics.

Catalog status:

- `mcp_servers/all_mcp_servers.json` has 23 catalog entries.
- 2026-06-29 SSOT evidence reports 0 missing catalog targets after SWARM-016.

---

## Tooling structure

```text
tools/
├── cli.py
├── cli/
│   ├── main.py
│   ├── commands/
│   └── dispatchers/
├── analysis/
├── autonomous/
├── captain/
├── cleanup/
├── codemods/
├── communication/
├── consolidation/
├── debug/
├── deprecated/
├── devops/
├── discord/
├── github/
├── migration/
├── monitoring/
├── security/
├── swarm/
└── validation/
```

Key active paths:

- `tools/cli.py` — compatibility shim used by CI.
- `tools/cli/main.py` — dispatches between toolbelt flags and unified command dispatcher.
- `tools/swarm/agents/import_healer.py` — active import-healer stream.
- `tools/swarm/tests/check_import_healer_coverage.py` — active coverage non-regression gate.
- `tools/security/unified_security_scanner.py` — security scan invoked by CI.
- `tools/validation/audit_imports.py` — import audit invoked by CI, but current default scan scope is not useful for this repo.

Legacy/high-risk paths:

- `tools/deprecated/` — explicitly deprecated scripts.
- historical one-off scripts under several tool categories that are not CI-covered.

---

## Toolbelt V2 structure

```text
tools_v2/
├── core/
├── categories/
├── tests/
├── tool_registry.py
├── tool_registry.lock.json
└── toolbelt_core.py
```

Purpose:

- provide adapter-style tool execution;
- centralize tool specs and registry loading;
- bridge older toolbelt capabilities to a typed interface.

Current status:

- substantial implementation exists;
- tests exist under `tools_v2/tests/`;
- disabled registry entries are documented in `docs/TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md`;
- root Python test collection is green per 2026-06-29 SSOT evidence.

---

## TypeScript workspace structure

```text
apps/
├── api/
│   ├── migrations/
│   ├── package.json
│   └── src/
│       ├── activity.ts
│       ├── env.ts
│       ├── realtime.ts
│       ├── routes.ts
│       ├── server.ts
│       ├── db/
│       └── plugins/
└── web/
    ├── app/
    │   ├── globals.css
    │   ├── layout.tsx
    │   └── page.tsx
    ├── package.json
    └── tsconfig.json

packages/
└── shared/
    ├── package.json
    └── src/
        ├── index.ts
        ├── types.ts
        └── timer/
            ├── stateMachine.ts
            └── stateMachine.test.ts
```

### Family Focus Board data flow

```text
Browser / Next.js app
  -> apps/web
  -> HTTP + Socket.IO
  -> apps/api Fastify server
  -> auth/db plugins
  -> PostgreSQL via pg pool
  -> migrations under apps/api/migrations
  -> activity log + realtime board/timer events
  -> shared timer state from packages/shared
```

Current implementation notes:

- API has real route logic for org/bootstrap, boards, lists, cards, focus rooms, timer sessions, activity, and inventory.
- Web UI is currently scaffold-level and not yet connected to API/realtime.
- Shared timer state machine is implemented and covered by Vitest.
- API and web tests/lint scripts are placeholders.

---

## Documentation topology

| Path | Role | Status |
|---|---|---|
| `docs/root/MASTER_TASK_LOG.md` | Canonical project status SSOT. | Active. |
| `NEXT_UP.md` | Human-readable dashboard mirroring SSOT. | Active. |
| `MASTER_TASK_LIST.md` | Current audit-backed actionable task list. | Active deliverable. |
| `ROADMAP.md` | Current audit-backed roadmap. | Active deliverable. |
| `PROJECT_STRUCTURE.md` | Current structure documentation. | Active deliverable. |
| `PROJECT_AUDIT_REPORT.md` | 2026-05-17 audit report. | Historical snapshot; see SSOT/domain model for current status. |
| `PRD.md` | AgentTools product framing. | Needs reconciliation with SWARM MCP and Family Focus Board lanes. |
| `docs/mvp.md` | Family Focus Board MVP plan. | Active if TS product lane remains active. |
| `docs/architecture/adr/0001-production-architecture.md` | AgentTools architecture ADR. | Mostly useful, but references absent legacy paths. |
| `docs/CODEBASE_RECON_AND_EXECUTION_PLAN.md` | Earlier recon report. | Partially stale; references absent `kanban-scheduler/`. |
| `docs/ARCHIVE_POINTER.md` | External archive pointer. | Historical; includes surfaces now partially present in current tree. |

---

## Infrastructure topology

### Current CI/CD

`.github/workflows/swarm_ci.yml`:

- triggers on `master` and `main` pushes, PRs targeting `master` or `main`, `v*` tags, and manual dispatch;
- installs Python 3.10 and `pip install -e ".[dev]"`;
- runs `pytest tests/ -v`;
- runs import-healer coverage gate;
- runs `python tools/cli.py --security-scan`;
- runs `python tools/cli.py --audit-imports`;
- publishes to PyPI on tags beginning with `v`.

Gaps:

- no Node workspace install/typecheck/test/audit gate;
- import audit default scope and security scan triage still need review;
- PyPI publish job failed for tag `v0.6.0` because `TWINE_PASSWORD` was empty.

### Runtime/deployment assumptions

- Python package is intended to publish to PyPI as `swarm-mcp`.
- TS API requires `DATABASE_URL`.
- TS API listens on `API_HOST`/`API_PORT` or defaults to `0.0.0.0:3001`.
- Web app defaults to Next.js port 3000.
- No Dockerfile or docker-compose file is present in the current checkout.

---

## Active vs inactive summary

| Lane | Classification | Confidence |
|---|---|---|
| `swarm_mcp/` package | Active, release-critical | High |
| `tests/` package/docs contracts | Active, green per 2026-06-29 SSOT evidence | High |
| `swarm_mcp/servers/` packaged MCP | Active, release-critical | High |
| `mcp_servers/` standalone MCP | Active/secondary; catalog targets currently resolve | Medium-high |
| `tools/cli.py`, security/import audit, import healer | Active CI tooling | High |
| `tools_v2/` | In-progress migration surface | Medium-high |
| `apps/api` | Active TS product backend lane | Medium |
| `apps/web` | Scaffold/early active lane | Medium |
| `packages/shared` | Active TS shared library | High |
| `tools/deprecated/` | Deprecated/legacy | High |
| `docs/quarantine/` | Quarantine/historical repair area | High |
| archive pointer surfaces | Historical or external archive | Medium |