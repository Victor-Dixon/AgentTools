# Codebase Recon & Closure-First Execution Plan

**Historical snapshot notice (reviewed 2026-05-17):** This document contains useful prior analysis, but several path claims are stale in the current checkout, including references to a present `kanban-scheduler/` directory and a nested `family-focus-board/` directory. Use `PROJECT_AUDIT_REPORT.md`, `PROJECT_STRUCTURE.md`, `MASTER_TASK_LIST.md`, `ROADMAP.md`, and `docs/root/MASTER_TASK_LOG.md` for current execution status.

## Executive Summary
The repository is operating as a mixed workspace rather than a single coherent product: it contains a Python `swarm_mcp` package, a TypeScript monorepo for Family Focus Board (`apps/api`, `apps/web`, `packages/shared`), a large standalone `kanban-scheduler` application, and a high-volume automation/tools surface (`tools/`, `mcp_servers/`). The current CI contract only executes Python tests and Python CLI checks, but the root package manager and active app scaffolding are Node workspace based, creating a governance split between what ships and what gets verified. The Family Focus Board stack appears closest to a product lane, but frontend and API tests/linting are mostly placeholder scripts and the UI is still scaffold-level. The Python swarm subsystem is functional in structure, but `pytest` fails in collection due to package path/dependency setup issues and therefore is not currently reliable as a merge gate. MCP server registration drifts from implementation: the JSON server catalog references non-existent `swarm_mcp.servers.*` modules for several tools. Tooling directories include both active and deprecated implementations, plus artifacts/odd files in root that indicate incomplete cleanup discipline. Overall, this repo is closer to a **tooling lab with product fragments** than a shippable product.

## Codebase Map

| Area | Purpose | Status |
|---|---|---|
| `swarm_mcp/` | Python package for multi-agent coordination primitives + MCP servers (`messaging`, `tasks`, `memory`, `control`, `tools`) | active |
| `mcp_servers/` | Additional MCP servers (DevOps, security, docs, analytics, deployment, etc.) plus server registry JSON | active but drifting |
| `apps/api/` | Fastify + Postgres backend for Family Focus Board MVP (boards/cards/timer/activity/inventory) | active |
| `apps/web/` | Next.js frontend for Family Focus Board; currently minimal scaffold page | experimental |
| `packages/shared/` | Shared TypeScript timer state machine logic and tests | active |
| `tools/` | Large consolidated + deprecated automation tool suite and CLI dispatcher | active + legacy mixed |
| `tools_v2/` | Newer adapter-driven tool architecture referenced across docs/deprecated scripts | experimental/transition |
| `tests/` | Python tests for swarm core and MCP server initialization | active but partially broken in env/setup |
| `kanban-scheduler/` | Separate full-stack app (Node/Express/React/Prisma), appears legacy parallel product line | legacy/parallel |
| `mod_deployment/`, `player_analytics/`, `backup_automation/`, `server_monitoring/`, `discord_integration/` | Domain-specific Python subsystems used by MCP servers | active but secondary |
| `family-focus-board/` | Empty directory shell despite naming overlap with root package identity | orphaned |

## Real Architecture
Primary architecture is **polyglot + multi-track**:

1. **Python swarm runtime path**
   - Package entry defined in `pyproject.toml` with CLI + MCP scripts pointing to `swarm_mcp.*`.
   - Runtime modules in `swarm_mcp/core/*` (coordination, consensus, conflict, work proof, etc.).
   - MCP transport endpoints in `swarm_mcp/servers/*` and additional standalone servers in `mcp_servers/*.py`.
   - Root CI (`.github/workflows/swarm_ci.yml`) validates this lane only.

2. **TypeScript product runtime path (Family Focus Board)**
   - Workspace root in `package.json` with `apps/*` and `packages/*`.
   - API entrypoint: `apps/api/src/server.ts` → registers DB/auth/routes/realtime.
   - Web entrypoint: `apps/web/app/page.tsx` (currently static MVP scaffold message).
   - Shared domain logic: `packages/shared/src/timer/stateMachine.ts` with passing tests.

3. **Tooling/runtime support path**
   - `tools/cli.py` shim → `tools/cli/main.py` routing to `tools.toolbelt` or unified dispatcher.
   - Registry-driven tool surface in `tools/toolbelt_registry.py`.
   - Large deprecated surface remains in `tools/deprecated/` and parallelized `tools_v2/`.

4. **Legacy parallel app path**
   - `kanban-scheduler/` has its own backend/frontend stack and package scripts, separate from the root workspace product lane.

## Critical Findings
1. **CI and repo runtime contracts diverge.** CI only runs Python tests + Python tool scans, while root workspace is Node monorepo with active API/web code; no CI job typechecks/tests those apps.
2. **MCP server registry contains broken module references.** `mcp_servers/all_mcp_servers.json` points to `swarm_mcp.servers.git_operations`, `code_quality`, `observability`, `testing`, but those modules are absent in `swarm_mcp/servers/`.
3. **Python test lane not reliably executable from clean environment.** `pytest tests -q` fails during collection with `ModuleNotFoundError: swarm_mcp` and missing `requests` dependency.
4. **Product test/lint gates are mostly placeholders.** `apps/api` and `apps/web` `test`/`lint` scripts echo placeholders rather than executing validation.
5. **Frontend is scaffold-level, not integrated with backend workflows.** `apps/web` home page explicitly says next steps are to connect API/render boards/timer.
6. **Legacy/deprecated code still impacts reliability scans.** Full compile sweep fails due to indentation errors in `tools/deprecated/*`, indicating cleanup incomplete even if isolated.
7. **Repository hygiene drift present.** Root contains malformed/stray files with command fragments, indicating partial script output checked in.
8. **Documentation-to-implementation drift exists across product intent.** Root README markets swarm framework, while `docs/mvp.md` and workspace structure indicate Family Focus Board product work.

## Shipping Blockers
| Blocker | Type | Why it blocks shipping |
|---|---|---|
| Broken CI coverage for active TS product lane | process/CI | API/web regressions can merge undetected |
| Python test collection/import failures | code+env | Claimed core runtime is not reproducibly testable |
| MCP registry pointing to missing modules | architecture/config | Server boot matrix is unreliable and misleading |
| Placeholder lint/test scripts in app packages | process | No enforceable code quality gates for app lane |
| Dual product tracks (`apps/*` vs `kanban-scheduler`) | scope/architecture | Fragmented execution, unclear SSOT for product direction |
| Deprecated code volume with syntax-invalid files | code hygiene | Increases noise and confidence loss in automation health checks |

## What To Kill / Freeze / Defer
- **Kill or archive root stray artifact files** (`itory && python -c `, `= sum(len(group.get('duplicates', [])) for group in batch['groups'])`) after confirming non-use.
- **Freeze `kanban-scheduler/` feature work** until a formal decision: either migrate needed capabilities into `apps/*` or archive it.
- **Freeze non-critical MCP server expansion** in `mcp_servers/` until server registry accuracy + boot checks are fixed.
- **Defer broad toolbelt growth** in `tools/`/`tools_v2/` until execution lane is stabilized around one SSOT runtime and CI gate set.

## What To Build Next
### Primary Lane: **Make Family Focus Board (`apps/api` + `apps/web` + `packages/shared`) the single shipping lane, with swarm/tooling treated as platform support**

Ordered execution targets:
1. **Establish SSOT runtime contract**: declare canonical product lane (`apps/*`) and classify `kanban-scheduler` + legacy directories as archived/frozen.
2. **Fix merge gates**: add CI jobs for `npm run typecheck`, workspace tests, and API/web lint checks (replace placeholder scripts with real commands).
3. **Close backend correctness loop**: add API integration tests around boards/cards/timer/activity flows and auth header contract.
4. **Ship minimal usable web workflow**: implement board read/create + basic card listing + timer state display wired to API/realtime.
5. **Repair MCP registry integrity**: either implement missing `swarm_mcp.servers.*` modules or repoint/remove stale entries in `all_mcp_servers.json`.
6. **Quarantine deprecated instability**: move syntax-broken deprecated scripts into archival path excluded from quality scans.

Why this order: it first restores trust in build/test contracts, then closes MVP workflow from backend to UI, then reduces operational drift from adjacent systems.

## 30-Day Execution Plan
### Week 1 — Contract & Gate Closure
- Decide and document product SSOT (apps lane) and archive policy for parallel lanes.
- Replace placeholder lint/test scripts in `apps/api` and `apps/web` with executable checks.
- Extend CI to run Node workspace checks alongside Python checks.
- **Closure target:** PR that makes CI fail on real app regressions.

### Week 2 — Backend Reliability Closure
- Add API tests for org bootstrap, board/list/card lifecycle, timer start/end, and activity logging.
- Add DB test bootstrap strategy and deterministic seed/migration test path.
- Resolve Python package import/dependency test failures for `swarm_mcp` to restore baseline confidence.
- **Closure target:** green automated test suite for backend + swarm core smoke path.

### Week 3 — MVP Usability Closure
- Implement minimal web flows: list boards, create board, view lists/cards, start/stop timer.
- Wire realtime room state consumption on frontend from socket events.
- Add one end-to-end happy-path test: create card → run timer → complete session.
- **Closure target:** demoable MVP loop with persisted data and timer telemetry.

### Week 4 — Drift Reduction Closure
- Reconcile `mcp_servers/all_mcp_servers.json` against actual modules with automated registry validation script in CI.
- Archive or isolate deprecated syntax-invalid scripts from active scans.
- Remove root stray artifacts and commit repository hygiene baseline.
- **Closure target:** deterministic server registry + clean repo hygiene report + no known false runtime entries.

## Evidence Appendix
- `README.md` — repo is presented as Swarm MCP framework narrative and package usage.
- `docs/mvp.md` — explicit Family Focus Board MVP scope and milestones.
- `package.json` — root npm workspaces define `apps/*` and `packages/*` as active TS monorepo.
- `.github/workflows/swarm_ci.yml` — CI currently runs only Python install/tests/security/import audit.
- `pyproject.toml` — Python package entrypoints and scripts for swarm servers.
- `apps/api/src/server.ts` — Fastify runtime entrypoint and plugin wiring.
- `apps/api/src/routes.ts` — substantial board/timer/inventory API implementation indicates real backend domain.
- `apps/web/app/page.tsx` — frontend remains scaffold with explicit “next steps” text.
- `apps/api/package.json` + `apps/web/package.json` — test/lint scripts are placeholders.
- `packages/shared/src/timer/stateMachine.test.ts` — only active TS test currently present and passing.
- `tests/test_mcp_servers.py` — Python tests assume module-executable MCP servers.
- `mcp_servers/all_mcp_servers.json` — includes missing module refs under `swarm_mcp.servers.*`.
- `swarm_mcp/servers/` directory listing — no `git_operations.py`, `code_quality.py`, `observability.py`, `testing.py`.
- `tools/cli.py` and `tools/cli/main.py` — active CLI shim + dispatcher architecture.
- `kanban-scheduler/package.json` and `kanban-scheduler/README.md` — separate legacy/parallel app surface.
- root files `itory && python -c ` and `= sum(len(group.get('duplicates', [])) for group in batch['groups'])` — malformed artifact files.
