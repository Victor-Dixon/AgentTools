# MASTER_TASK_LIST

**Last updated:** 2026-05-17  
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`  
**Companion dashboard:** `NEXT_UP.md`  
**Audit deliverables:** `PROJECT_AUDIT_REPORT.md`, `PROJECT_STRUCTURE.md`, `ROADMAP.md`

This task list consolidates the current workspace audit into actionable work. Status values are:
`DONE`, `IN_PROGRESS`, `BLOCKED`, `TODO`, and `DEPRECATED`.

---

## Global priorities

| Priority | Status | Task | Evidence / rationale |
|---|---|---|---|
| P0 | BLOCKED | Publish and verify `swarm-mcp` externally: complete SWARM-003 and SWARM-004. | `docs/root/MASTER_TASK_LOG.md` still marks PyPI publish and clean install verification open. |
| P0 | BLOCKED | Restore Python CI parity by making `pip install -e ".[dev]" && python3 -m pytest tests -q` pass in a clean checkout. | Current run fails during collection because `tools_v2` imports `dotenv`, which is not in the `dev` extra. |
| P0 | BLOCKED | Fix import-healer coverage gate regression or refresh the baseline with documented justification. | `python3 tools/swarm/tests/check_import_healer_coverage.py` reports regressions vs `import_healer_coverage_baseline.json`. |
| P0 | TODO | Repair `mcp_servers/all_mcp_servers.json` so every catalog entry points to an existing module/script. | 4 entries reference missing `swarm_mcp.servers.git_operations`, `code_quality`, `observability`, and `testing`. |
| P0 | TODO | Remediate npm vulnerabilities with a reviewed dependency update. | `npm audit --audit-level=moderate` reports 3 vulnerabilities: `next`, `fast-uri`, `postcss`. |
| P1 | TODO | Add Node workspace CI gates for typecheck, tests, audit, and real linting. | Current GitHub workflow only runs Python checks; API/web lint and tests are placeholders. |
| P1 | TODO | Decide the product boundary between SWARM MCP, AgentTools, and Family Focus Board. | Root PRD/roadmap use AgentTools framing; README and SSOT use SWARM MCP; TS workspace is Family Focus Board. |
| P1 | TODO | Consolidate duplicate planning docs and retire shadow task artifacts. | Root and `docs/root` both contain `MASTER_TASK_*` files with different content. |
| P1 | TODO | Classify all standalone `mcp_servers` as keep, merge, archive, or delete-candidate. | 27 standalone server scripts sit beside the 5 packaged servers, with partial overlap. |
| P2 | TODO | Continue toolbelt V2 migration only after registry health is enforced by tests. | `docs/TOOL_SURFACES_AND_OVERLAP.md` records 91 entries, 87 registry count, and known failing adapters. |

---

## Project-by-project tasks

### 1. SWARM MCP Python package (`swarm_mcp/`)

| Status | Task | Owner lane | Notes |
|---|---|---|---|
| DONE | Core package structure exists with `pyproject.toml`, package exports, CLI, and 5 packaged MCP server entry points. | Package | Inventory: 23 Python files under `swarm_mcp/`; 5 server modules; 12 CLI subcommands. |
| DONE | Core algorithms are implemented: coordinator, messaging, memory, consensus, conflict detection, agent DNA, work proof, pattern miner, verification/recovery helpers. | Runtime | Covered by dedicated tests, but full suite currently blocked by dependency setup. |
| BLOCKED | Complete SWARM-003: build and publish `swarm-mcp` to PyPI; record exact output in SSOT. | Release | Requires maintainer token workflow already completed in SWARM-002. |
| BLOCKED | Complete SWARM-004: verify clean `pip install swarm-mcp`, import smoke, CLI smoke, and MCP server smoke from a fresh env. | Release | Cannot be considered complete until PyPI publish succeeds. |
| TODO | Add `python-dotenv` to the correct test/dev dependency path or isolate `tools_v2` imports from the package test collection. | QA | Current `tests/compat/test_agenttools_tool_adapter_characterization.py` imports `tools_v2`, which imports `dotenv`. |
| TODO | Ensure executable docs use `python3` or document environments where `python` is expected. | Dev setup | Cloud image has `python3` but no `python`; README examples use `python`. |
| TODO | Add a release checklist proving wheel contents, console scripts, MCP server module execution, and README snippets. | Release | Prevents release claims from drifting from package behavior. |

### 2. Packaged MCP servers (`swarm_mcp/servers/`)

| Status | Task | Notes |
|---|---|---|
| DONE | Packaged server files exist: `control.py`, `memory.py`, `messaging.py`, `tasks.py`, `tools.py`. | Matches `pyproject.toml` console scripts. |
| TODO | Add smoke tests for every console script command, not only module initialization. | Current tests use subprocess module execution for several servers. |
| TODO | Replace or document `swarm_mcp/servers/tools.py` dependency on legacy `tools.toolbelt_registry`. | It falls back to an empty registry on import failure and shells out to `tools.toolbelt`. |
| TODO | Update README MCP config to show all 5 packaged servers. | Root README previously omitted `swarm-tools`. |

### 3. Standalone MCP server collection (`mcp_servers/`)

| Status | Task | Notes |
|---|---|---|
| IN_PROGRESS | Maintain catalog of 27 standalone `*_server.py` files. | These are operational/tooling surfaces, not packaged PyPI servers. |
| BLOCKED | Fix 4 broken module references in `mcp_servers/all_mcp_servers.json`. | Broken entries point at missing `swarm_mcp.servers.*` modules. |
| TODO | Classify each standalone server as `active`, `adapter-only`, `legacy`, `archive`, or `delete-candidate`. | Highest priority: task manager, git ops, security scanner, CI/CD helper, docs generator, dependency management. |
| TODO | Update `mcp_servers/TASK_MANAGER_README.md` and related docs to reference `docs/root/MASTER_TASK_LOG.md`. | Several docs still claim `MASTER_TASK_LOG.md` lives at repo root. |
| TODO | Add a catalog validation test that imports/locates every configured server target. | This should become a CI gate before more MCP expansion. |

### 4. Tooling CLI and legacy tools (`tools/`)

| Status | Task | Notes |
|---|---|---|
| DONE | `tools/cli.py` shim and `tools/cli/main.py` dispatcher exist and are used by CI. | CI runs security scan and import audit through this path. |
| BLOCKED | Make security scan actionable by separating real findings from fixture false positives. | Current scan flags fixture `config.py` files as suspicious tracked files. |
| BLOCKED | Install or declare `pip-audit` if Python dependency audits remain part of the security gate. | Security scan skips Python audit because `pip-audit` is missing. |
| TODO | Fix import audit scope. | `PYTHONPATH=. python3 tools/cli.py --audit-imports` audited 0 Python files in `src/`, which is not useful for this repo. |
| TODO | Classify `tools/deprecated/` contents for archive/removal after confirming no active registry references. | Many TODO/stub markers and older scripts remain. |
| TODO | Keep generated command artifacts out of the repo or quarantine them under documented paths. | Import audit generated `quarantine/BROKEN_IMPORTS.md`; generated artifacts should not surprise maintainers. |

### 5. Toolbelt V2 (`tools_v2/`)

| Status | Task | Notes |
|---|---|---|
| IN_PROGRESS | Adapter/registry architecture exists with tests under `tools_v2/tests/`. | Not currently run by `.github/workflows/swarm_ci.yml`. |
| BLOCKED | Resolve dependency and import health before treating V2 as production-ready. | Root test suite fails on missing `dotenv`; registry docs list known failing entries. |
| TODO | Reconcile `tools_v2/README.md` claims with current registry reality. | README says production-ready and 23 tools; audit docs list a much larger registry with failing adapters. |
| TODO | Run `python3 -m pytest tools_v2/tests -q` in CI after dependency issues are fixed. | Prevents future registry regressions. |
| TODO | Reduce duplicate tool surfaces between `tools_v2`, `tools/`, and `mcp_servers`. | Use `docs/TOOL_SURFACES_AND_OVERLAP.md` as the starting map. |

### 6. Family Focus Board TypeScript workspace (`apps/`, `packages/`)

| Status | Task | Notes |
|---|---|---|
| IN_PROGRESS | Root npm workspace exists with `apps/api`, `apps/web`, and `packages/shared`. | Root package name is `family-focus-board`. |
| IN_PROGRESS | API has Fastify/Postgres routes for orgs, boards, lists, cards, focus rooms, sessions, activity, and inventory. | Needs integration tests and deployment docs. |
| IN_PROGRESS | Shared timer state machine exists and has Vitest tests. | `npm -ws run test` passes shared tests; API/web tests are placeholders. |
| TODO | Replace API/web placeholder tests with real unit/integration coverage. | Current scripts echo "(no api tests yet)" and "(no web tests yet)". |
| TODO | Add lint configuration for API/web/shared packages. | Current lint scripts are placeholders. |
| TODO | Wire web UI to API/realtime; current page is a scaffold message. | `apps/web/app/page.tsx` explicitly lists this as next work. |
| TODO | Add `.env.example` and deployment docs for `DATABASE_URL`, API host/port, migrations, and seed flow. | `apps/api/src/env.ts` requires `DATABASE_URL`. |
| BLOCKED | Resolve npm audit vulnerabilities before any production deployment. | `next`, transitive `fast-uri`, and `postcss` advisories are open. |

### 7. Documentation and planning artifacts

| Status | Task | Notes |
|---|---|---|
| DONE | Added/updated audit deliverables requested on 2026-05-17. | `MASTER_TASK_LIST.md`, `ROADMAP.md`, `PROJECT_STRUCTURE.md`, `PROJECT_AUDIT_REPORT.md`. |
| IN_PROGRESS | SSOT updated first, dashboard mirrored second. | `docs/root/MASTER_TASK_LOG.md` and `NEXT_UP.md` now include 2026-05-17 audit findings. |
| DONE | Convert root `MASTER_TASK_LOG.md` into a redirect-only compatibility pointer. | Completed 2026-05-17; canonical updates stay in `docs/root/MASTER_TASK_LOG.md`. |
| DONE | Replace `docs/root/MASTER_TASK_LIST.md` with a pointer to current audit deliverables. | Completed 2026-05-17 to remove stale metrics from 2025-12-26. |
| TODO | Reconcile `docs/CODEBASE_RECON_AND_EXECUTION_PLAN.md` and ADR references to absent `kanban-scheduler/` and `family-focus-board/` directories. | Current workspace has `apps/*` and `packages/*`, not nested app directories. |
| TODO | Mark historical docs with frozen dates when they are retained for context only. | Prevents old plans from being mistaken for active roadmap. |

### 8. CI/CD and release infrastructure

| Status | Task | Notes |
|---|---|---|
| DONE | GitHub Actions workflow exists for Python package tests, import-healer gate, security scan, import audit, and tag-based PyPI publish. | `.github/workflows/swarm_ci.yml`. |
| BLOCKED | CI likely fails on current dependency state. | Workflow installs `.[dev]`, then `pytest tests/ -v`; local equivalent fails on missing `dotenv`. |
| TODO | Add Node workflow steps: `npm ci`, `npm -ws run typecheck`, `npm -ws run test`, `npm audit --audit-level=moderate`. | Required if TS workspace remains active. |
| TODO | Add MCP catalog validation to CI. | Prevents missing module references. |
| TODO | Add package build/twine check before tag publish. | SWARM-003 should record exact output. |

---

## Blockers

1. **PyPI release not complete**: SWARM-003/004 remain open.
2. **Python test suite cannot collect under declared dev dependencies**: missing `dotenv`.
3. **Import-healer coverage gate reports regression** against committed baseline.
4. **MCP catalog has 4 broken targets**.
5. **Node dependency vulnerabilities are open**.
6. **API/web lack real tests/lint**.
7. **Documentation has multiple competing product narratives and duplicate task-log names**.

---

## Technical debt

- Duplicate tool capability surfaces across `swarm_mcp/servers`, `mcp_servers`, `tools`, and `tools_v2`.
- Stale docs with old metrics, missing paths, and outdated product assumptions.
- Fixture files trigger security scanner false positives.
- `tools_v2` import side effects make unrelated tests require optional dependencies.
- `tools/cli.py --audit-imports` scans a non-existent `src/` default for this repository.
- README and setup docs assume `python`, while this environment only provides `python3`.
- Root npm workspace and Python package coexist without a clearly documented ownership model.

---

## Bugs

| Status | Bug | Repro / evidence |
|---|---|---|
| BLOCKED | Full Python test collection fails on missing `dotenv`. | `python3 -m pytest tests -q`. |
| BLOCKED | Import-healer coverage gate fails. | `python3 tools/swarm/tests/check_import_healer_coverage.py`. |
| TODO | MCP catalog includes missing modules. | Inventory script found 4 missing `swarm_mcp.servers.*` targets. |
| TODO | Import audit reports success after scanning 0 files. | `PYTHONPATH=. python3 tools/cli.py --audit-imports`. |
| TODO | API/web test scripts do not test code. | `npm -ws run test` only executes Vitest in `packages/shared`. |

---

## Infrastructure tasks

- [BLOCKED] Install/declare Python dev dependencies needed by tests, or decouple optional tool surfaces.
- [TODO] Add Node CI for the active npm workspace.
- [TODO] Add dependency audit gates for Python (`pip-audit`) and Node (`npm audit`) with documented false-positive policy.
- [TODO] Add MCP catalog validation.
- [TODO] Add `.env.example` and deployment runbook for the API.
- [TODO] Ensure release scripts use paths available in clean environments.

---

## Documentation tasks

- [DONE] Produce 2026-05-17 audit deliverables.
- [IN_PROGRESS] Synchronize SSOT and `NEXT_UP.md` with audit findings.
- [DONE] Retire stale root `MASTER_TASK_LOG.md` shadow by converting it to a pointer.
- [DONE] Replace stale `docs/root/MASTER_TASK_LIST.md` with a pointer.
- [TODO] Update MCP server READMEs to use `docs/root/MASTER_TASK_LOG.md`.
- [TODO] Refresh README MCP config and CLI inventory.
- [TODO] Reconcile PRD/roadmap language: SWARM MCP package vs AgentTools platform vs Family Focus Board product.
- [TODO] Add deployment docs for PyPI release and TS app hosting.

---

## Security and performance issues

| Status | Area | Issue | Recommended action |
|---|---|---|---|
| BLOCKED | Node dependencies | 3 npm audit findings: `next`, `fast-uri`, `postcss`. | Run reviewed dependency updates and re-run typecheck/tests/audit. |
| TODO | Python dependencies | Security scan skips Python audit because `pip-audit` is missing. | Add `pip-audit` to dev/tooling deps or remove the claim from the gate. |
| TODO | Secrets | No obvious secrets found by scanner; fixture config false positives remain. | Add fixture allowlist or rename fixture files. |
| TODO | API security | API auth plugin and CORS posture need production review. | Add auth tests and deployment-specific CORS config. |
| TODO | Performance | Pattern mining, message persistence, and API DB queries have no load/perf gates. | Add targeted benchmarks after correctness gates pass. |

---

## Recommended execution order

1. Fix Python dev/test dependency gap and confirm `python3 -m pytest tests -q`.
2. Fix or intentionally refresh import-healer coverage baseline.
3. Repair MCP catalog missing targets and add catalog validation.
4. Complete SWARM-003 publish evidence and SWARM-004 clean install evidence.
5. Patch npm vulnerabilities and add Node CI gates.
6. Replace API/web placeholder tests and lint scripts.
7. Classify standalone MCP servers and `tools/deprecated` entries.
8. Reconcile product narrative and retire duplicate task-log shadows.
9. Wire Family Focus Board web UI to API/realtime if that product remains active.
10. Consolidate `tools_v2` registry and document the stable tool surface.
