# MASTER_TASK_LIST

**Last updated:** 2026-07-03  
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`  
**Companion dashboard:** `NEXT_UP.md`  
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`

This task list mirrors the current execution state. Status values are `DONE`, `IN_PROGRESS`, `BLOCKED`, `TODO`, `PARTIAL`, and `UNKNOWN`.

---

## Global priorities

| Priority | Status | Task | Evidence / rationale |
|---|---|---|---|
| P0 | BLOCKED | Complete SWARM-003: publish `swarm-mcp==0.6.0` to PyPI and record redacted output. | Tag `v0.6.0` exists; CI publish failed with empty `TWINE_PASSWORD`. |
| P0 | BLOCKED | Complete SWARM-004: verify clean install/import/CLI smoke from PyPI. | Cannot complete until `0.6.0` is live on PyPI. |
| P0 | DONE | Restore declared Python test gate. | SSOT evidence: `python3 -m pytest tests -q` reported `72 passed, 1 skipped` on 2026-06-29. |
| P0 | DONE | Restore import-healer coverage gate. | SSOT evidence: coverage gate passed after reviewed baseline refresh on 2026-06-29. |
| P0 | DONE | Repair MCP catalog missing targets and add validation. | SSOT evidence: 23 catalog entries, 0 missing targets. |
| P0 | IN_PROGRESS | Keep domain/status documentation synchronized. | Canonical domain model added 2026-07-03; remaining historical docs need banners/classification as touched. |
| P1 | PARTIAL | Remediate npm vulnerabilities or document accepted risk. | SWARM-017 reduced vulnerabilities to 2 moderate; accepted only while TS lane is non-production. |
| P1 | TODO | Add Node workspace CI gates for typecheck, tests, audit, and real linting. | API/web lint and tests remain placeholders. |
| P1 | TODO | Classify standalone MCP servers as active, adapter-only, legacy, archive, or unknown. | `mcp_servers/` contains operator and uncertain game/community surfaces. |
| P1 | TODO | Classify legacy tool surfaces and disabled `tools_v2` adapters. | `docs/TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md` lists disabled entries; legacy scripts still need ownership status. |

---

## Project-by-project tasks

### 1. SWARM MCP Python package (`swarm_mcp/`)

| Status | Task | Owner lane | Notes |
|---|---|---|---|
| DONE | Core package structure exists with package metadata, exports, CLI, and 5 packaged MCP server entry points. | SWARM MCP | `pyproject.toml`, `swarm_mcp/__init__.py`, `swarm_mcp/cli.py`, `swarm_mcp/servers/`. |
| DONE | Core algorithms are implemented. | SWARM MCP | Coordinator, messaging, memory, brain, consensus, conflict, DNA, work proof, verification, recovery, task scoring, pattern miner. |
| DONE | Python test gate is green. | QA | `72 passed, 1 skipped` per 2026-06-29 SSOT evidence. |
| BLOCKED | Complete SWARM-003 PyPI publish. | Release | Requires `PYPI_API_TOKEN` GitHub secret/configuration and publish output captured in SSOT. |
| BLOCKED | Complete SWARM-004 clean PyPI install proof. | Release | Pending SWARM-003. |
| TODO | Add release checklist proving wheel contents, console scripts, MCP module execution, and README snippets. | Release | Prevents release docs from drifting from package behavior. |
| TODO | Decide/document canonical memory precedence. | Domain | `PackMemory`, `SwarmBrain`, and `swarm_brain/knowledge_base.json` coexist; precedence is Unknown. |

### 2. Packaged MCP servers (`swarm_mcp/servers/`)

| Status | Task | Notes |
|---|---|---|
| DONE | Packaged server files exist: `control.py`, `memory.py`, `messaging.py`, `tasks.py`, `tools.py`. | Matches `pyproject.toml` console scripts. |
| DONE | README MCP config lists all 5 packaged servers. | Current README includes `swarm-tools`. |
| TODO | Add smoke tests for every console script command, not only module initialization. | Complements existing tests. |
| TODO | Replace or document `swarm_mcp/servers/tools.py` dependency on legacy `tools.toolbelt_registry`. | It shells through legacy tooling when available. |

### 3. Standalone MCP server collection (`mcp_servers/`)

| Status | Task | Notes |
|---|---|---|
| DONE | Catalog missing targets repaired. | SWARM-016 evidence: 23 entries, 0 missing targets. |
| IN_PROGRESS | Maintain packaged-vs-standalone distinction. | Packaged servers ship with `swarm-mcp`; standalone servers are operator/local surfaces. |
| TODO | Classify each standalone server as `active`, `adapter-only`, `legacy`, `archive`, or `unknown`. | Highest priority: task manager, git ops, security scanner, CI/CD helper, docs generator, dependency management. |
| TODO | Reconcile task-manager docs/code with `docs/root/MASTER_TASK_LOG.md`. | Some task-log mutation assumptions remain risky. |

### 4. Tooling CLI and legacy tools (`tools/`)

| Status | Task | Notes |
|---|---|---|
| DONE | `tools/cli.py` shim and `tools/cli/main.py` dispatcher exist and are used by CI. | CI runs security scan and import audit through this path. |
| TODO | Make security scan findings actionable. | Fixture false positives and risk triage policy still need cleanup. |
| TODO | Fix or document import audit scope. | Historical output scanned 0 files under default `src/`; current behavior needs review. |
| TODO | Classify `tools/deprecated/` and other legacy scripts for archive/removal after confirming no active registry references. | Prevents legacy code from looking active. |

### 5. Toolbelt V2 (`tools_v2/`)

| Status | Task | Notes |
|---|---|---|
| IN_PROGRESS | Adapter/registry architecture exists. | Registry, categories, lock file, and tests are present. |
| DONE | Broken active registry entries were moved/recorded as disabled. | See `docs/TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md`. |
| TODO | Reconcile `tools_v2/README.md` claims with current registry reality. | Keep tool counts and production-readiness language evidence-backed. |
| TODO | Add or confirm CI coverage for `tools_v2` registry health. | Prevents disabled entries from silently returning to active registry. |
| TODO | Reduce duplicate tool surfaces between `tools_v2`, `tools/`, and `mcp_servers`. | Use `docs/TOOL_SURFACES_AND_OVERLAP.md` and `DOMAIN_MODEL.md` as starting maps. |

### 6. Family Focus Board TypeScript workspace (`apps/`, `packages/`)

| Status | Task | Notes |
|---|---|---|
| IN_PROGRESS | Root npm workspace exists with `apps/api`, `apps/web`, and `packages/shared`. | Root package name is `family-focus-board`. |
| IN_PROGRESS | API has Fastify/Postgres routes for orgs, boards, lists, cards, focus rooms, sessions, activity, and inventory. | Needs integration tests and deployment docs. |
| DONE | Shared timer state machine exists and has Vitest tests. | `packages/shared/src/timer/stateMachine.ts`. |
| TODO | Replace API/web placeholder tests with real unit/integration coverage. | API/web tests are not confidence gates. |
| TODO | Add lint configuration for API/web/shared packages. | Current lint scripts need verification/replacement. |
| TODO | Wire web UI to API/realtime. | Web app is scaffold-level. |
| TODO | Add `.env.example` and deployment docs for `DATABASE_URL`, API host/port, migrations, and seed flow. | `apps/api` requires database configuration. |
| PARTIAL | Resolve npm audit vulnerabilities before production deployment. | 2 moderate issues remain accepted only while non-production. |

### 7. Documentation and planning artifacts

| Status | Task | Notes |
|---|---|---|
| DONE | Canonical domain model added. | `docs/architecture/DOMAIN_MODEL.md`, 2026-07-03. |
| DONE | PRD, roadmap, master task list, SSOT, dashboard, AGENTS, and GitHub description guidance synchronized for the domain audit. | 2026-07-03 documentation pass. |
| DONE | Root `MASTER_TASK_LOG.md` is a redirect-only compatibility pointer. | Canonical updates stay in `docs/root/MASTER_TASK_LOG.md`. |
| DONE | `docs/root/MASTER_TASK_LIST.md` is a pointer to current root task list and SSOT. | Prevents duplicate active lists. |
| IN_PROGRESS | Mark historical docs with frozen dates/non-canonical banners. | Continue as stale docs are touched. |
| TODO | Add docs contract tests for canonical domain/status docs if drift recurs. | Optional hardening. |

### 8. CI/CD and release infrastructure

| Status | Task | Notes |
|---|---|---|
| DONE | GitHub Actions workflow exists for Python tests, import-healer gate, security scan, import audit, and tag-based PyPI publish. | `.github/workflows/swarm_ci.yml`. |
| DONE | Python package/test CI path restored. | 2026-06-29 evidence. |
| BLOCKED | PyPI publish secret/configuration. | `TWINE_PASSWORD` was empty in failed publish job. |
| TODO | Add Node workflow steps: `npm ci`, `npm -ws run typecheck`, `npm -ws run test`, `npm audit --audit-level=moderate`. | Required if TS workspace remains active. |
| TODO | Review security/import audit behavior. | Ensure scans cover the intended files and dependencies. |

---

## Current blockers

1. **SWARM-003 PyPI publish:** `v0.6.0` publish failed because `PYPI_API_TOKEN` was not available to the job.
2. **SWARM-004 clean install proof:** blocked until `0.6.0` is published.
3. **TypeScript production readiness:** API/web test/lint/deploy docs and remaining npm audit risk are incomplete.
4. **Secondary surface classification:** standalone MCP servers and legacy tools still need active/legacy/unknown labels.

---

## Technical debt

- Duplicate tool capability surfaces across `swarm_mcp/servers`, `mcp_servers`, `tools`, and `tools_v2`.
- Parallel memory systems without documented precedence.
- Task-log mutation surfaces still need strict alignment with `docs/root/MASTER_TASK_LOG.md`.
- Stale historical docs still contain old metrics and path assumptions.
- API/web tests and lint scripts are placeholders.
- Live MCP deployment topology is Unknown.

---

## Bugs and drift

| Status | Issue | Repro / evidence |
|---|---|---|
| DONE | Full Python test collection failed on missing `dotenv`. | Fixed before 2026-06-29 test evidence. |
| DONE | Import-healer coverage gate failed against stale baseline. | Fixed before 2026-06-29 coverage evidence. |
| DONE | MCP catalog included missing modules. | Fixed in SWARM-016; 0 missing targets. |
| TODO | Import audit behavior may not cover intended repo paths. | Review `tools/cli.py --audit-imports` output. |
| TODO | API/web test scripts do not provide real coverage. | Replace placeholders with tests. |
| TODO | Some historical docs still look actionable. | Add banners or refresh content. |

---

## Recommended execution order

1. Configure `PYPI_API_TOKEN` and complete SWARM-003 publish.
2. Complete SWARM-004 clean install/import/CLI proof.
3. Keep SSOT and `NEXT_UP.md` synchronized with publish evidence.
4. Continue historical documentation banner/classification cleanup.
5. Patch or explicitly accept remaining npm audit risk before TS deployment.
6. Add real API/web tests and lint gates.
7. Classify standalone MCP servers and legacy tool entries.
8. Reconcile task-log mutation code paths with canonical SSOT.
