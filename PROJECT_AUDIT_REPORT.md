# PROJECT_AUDIT_REPORT

**Audit date:** 2026-05-17  
**Audited workspace:** `/workspace`  
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`  
**Related deliverables:** `MASTER_TASK_LIST.md`, `ROADMAP.md`, `PROJECT_STRUCTURE.md`

---

## Executive summary

This workspace is a **mixed polyglot repository**. The clearest release-critical product is **SWARM MCP**, a Python package for multi-agent coordination over MCP. It has implemented core modules, CLI commands, packaged MCP server modules, tests, package metadata, and CI configuration. However, it is not release-complete: PyPI publish and clean-install verification remain open, and the current test gate is blocked by dependency/config drift.

The repository also contains a substantial **AgentTools/operator tooling** layer (`tools/`, `tools_v2/`, `mcp_servers/`) and a **Family Focus Board** TypeScript workspace (`apps/api`, `apps/web`, `packages/shared`). Those lanes have useful code but are not aligned with the Python-only CI contract and are inconsistently represented across planning docs.

Overall health is **moderate but unstable**: implementation exists in several lanes, but release confidence is reduced by broken gates, stale documentation, duplicate task-log artifacts, catalog drift, and unremediated dependency vulnerabilities.

---

## Overall health scorecard

| Area | Health | Completion estimate | Notes |
|---|---:|---:|---|
| SWARM MCP Python package | Yellow | 80% | Core/package exists; release proof and clean install remain incomplete. |
| Packaged MCP servers | Yellow | 75% | 5 servers exist; more smoke/console-script tests needed. |
| Standalone `mcp_servers` | Yellow/red | 60% | 27 scripts; catalog has 4 missing targets and docs need classification. |
| Legacy/current `tools` CLI | Yellow | 65% | CI uses it, but security/import audit behavior needs cleanup. |
| Toolbelt V2 | Yellow/red | 55% | Architecture exists; registry/import health not production-stable. |
| Family Focus Board API | Yellow | 60% | Substantial Fastify/Postgres routes; no real tests/lint/deployment docs. |
| Family Focus Board Web | Red/yellow | 25% | Scaffold page only; not connected to API/realtime. |
| Shared TS package | Green/yellow | 80% | Timer state machine and Vitest tests pass. |
| CI/CD | Yellow/red | 50% | Python-only and currently blocked; no Node CI. |
| Documentation/planning | Yellow/red | 55% | Current audit docs exist, but historical docs and duplicates remain. |

Estimated overall workspace completion: **62%** for a governed multi-lane workspace.  
Estimated SWARM MCP package release completion: **80%** before PyPI verification; **not launch-complete**.

---

## Project inventory

### Active projects

| Project | Path(s) | Purpose | Stack | State |
|---|---|---|---|---|
| SWARM MCP package | `swarm_mcp/`, `pyproject.toml`, `tests/` | Multi-agent coordination package and MCP support. | Python 3.10+, hatchling, pytest. | Active, release-critical. |
| Packaged MCP servers | `swarm_mcp/servers/` | Public MCP entry points shipped with package. | Python JSON-RPC style MCP loops. | Active; needs deeper smoke tests. |
| Operator CLI/toolbelt | `tools/cli.py`, `tools/cli/`, `tools/toolbelt*` | Local automation CLI used by CI and MCP tools server. | Python. | Active but noisy. |
| Import healer stream | `tools/swarm/agents/`, `tools/swarm/tests/` | Import repair tooling and coverage gate. | Python, coverage/pytest. | Active but coverage gate currently failing. |
| Standalone MCP servers | `mcp_servers/` | Local/operator MCP automation servers. | Python scripts. | Active/secondary with catalog drift. |
| Toolbelt V2 | `tools_v2/` | Adapter-driven tool registry and categories. | Python. | In-progress; registry/import issues. |
| Family Focus Board API | `apps/api/` | Kanban/focus-room backend. | Fastify, PostgreSQL, Socket.IO, Zod, TypeScript. | Active scaffold; no real tests. |
| Family Focus Board Web | `apps/web/` | Frontend for family board/timer product. | Next.js 16, React 19, Tailwind. | Scaffold-level. |
| Shared TS contracts | `packages/shared/` | Timer state machine and shared types. | TypeScript, Vitest. | Active and tested. |

### Inactive, legacy, or uncertain projects

| Surface | Path(s) | Classification | Rationale |
|---|---|---|---|
| Deprecated tools | `tools/deprecated/` | DEPRECATED | Explicit directory name; many stubs/TODOs. |
| Quarantined Python | `docs/quarantine/broken_python/` | Quarantine/historical | Intended for broken/repair artifacts, not active runtime. |
| External archive pointer | `docs/ARCHIVE_POINTER.md` | Historical | Points to archive outside canonical checkout. |
| Game/server/community MCP surfaces | `mcp_servers/mod_*`, `server_monitoring`, `backup_automation`, `discord_integration`, `player_analytics`; `tools_v2/categories/mod_deployment_tools.py` | Uncertain/secondary | Present in code, but archive pointer also lists these domains as archived; needs classification. |
| Earlier recon docs | `docs/CODEBASE_RECON_AND_EXECUTION_PLAN.md`, `_ops/reports/root_docs_audit.md` | Partially stale | Useful history, but references absent paths or older layout. |
| Root task-log shadow | `MASTER_TASK_LOG.md` | Compatibility pointer | Converted on 2026-05-17; canonical updates belong in `docs/root/MASTER_TASK_LOG.md`. |
| `docs/root/MASTER_TASK_LIST.md` | Superseded pointer | Replaced on 2026-05-17; current actionable tasks live in root `MASTER_TASK_LIST.md`. |

---

## Implementation progress

### SWARM MCP

Implemented:

- package metadata and console scripts;
- 12 CLI subcommands: `status`, `send`, `inbox`, `search`, `learn`, `tasks`, `assign`, `vote`, `conflict`, `profile`, `prove`, `patterns`;
- 5 packaged MCP server modules: `control.py`, `memory.py`, `messaging.py`, `tasks.py`, `tools.py`;
- core coordination modules and public exports;
- tests for core behavior, docs contracts, MCP servers, and compatibility surfaces;
- GitHub Actions workflow for Python tests and PyPI tag publish.

Incomplete:

- PyPI publish (`SWARM-003`);
- clean install verification (`SWARM-004`);
- full Python test pass under declared dev dependencies;
- release docs with captured command output;
- packaged MCP console-script smoke tests.

### AgentTools / local tooling

Implemented:

- CLI shim and dispatcher;
- security scanner;
- import auditor;
- import healer coverage gate;
- many analysis, validation, migration, and monitoring scripts;
- tool inventories and surface audits.

Incomplete:

- consistent active/deprecated classification;
- useful import audit default scope;
- `pip-audit` dependency if Python security audit remains claimed;
- false-positive policy for fixture files;
- consolidation of duplicate logic across `tools`, `tools_v2`, and `mcp_servers`.

### Toolbelt V2

Implemented:

- registry, lock file, core/facade/spec modules;
- numerous categories and adapter-like tools;
- unit/smoke tests under `tools_v2/tests`.

Incomplete:

- registry health consistency;
- optional dependency isolation;
- CI coverage;
- README claims aligned with actual tool count and failing entries;
- migration plan from legacy toolbelt to V2.

### Family Focus Board

Implemented:

- npm workspace root;
- API server with Fastify, DB/auth plugins, realtime, migrations, routes;
- board/list/card/timer/activity/inventory API functionality;
- shared timer state machine and tests;
- minimal Next.js app scaffold.

Incomplete:

- API integration tests;
- web/API lint configuration;
- web-to-API integration;
- e2e flow;
- deployment docs and `.env.example`;
- npm vulnerability remediation.

---

## Verification results

Commands were run on 2026-05-17 after installing declared dependencies with `python3 -m pip install -e ".[dev]"` and `npm ci`.

| Check | Result | Notes |
|---|---|---|
| Inventory script | PASS | Confirmed 5 packaged servers, 12 CLI subcommands, 27 standalone MCP server scripts, 23 catalog entries, and 4 missing catalog targets. |
| `python3 -m pytest tests -q` | FAIL | Collection fails: `ModuleNotFoundError: No module named 'dotenv'` from `tools_v2/categories/communication_tools.py`. |
| `python3 tools/swarm/tests/check_import_healer_coverage.py` | FAIL | Coverage regressions vs baseline for import healer, validator, and test file. |
| `PYTHONPATH=. python3 tools/cli.py --security-scan` | FAIL/needs triage | No obvious secrets found; flags 2 fixture `config.py` files; skips Python audit because `pip-audit` missing; reports npm vulnerabilities. |
| `PYTHONPATH=. python3 tools/cli.py --audit-imports` | PASS but weak | Audits 0 Python files in `src/`; output is not meaningful for this repo. |
| `npm -ws run typecheck` after `npm ci` | PASS | All TypeScript workspaces typecheck. |
| `npm -ws run test` after `npm ci` | PARTIAL PASS | API/web tests are placeholders; shared Vitest suite passes 1 file / 3 tests. |
| `npm audit --audit-level=moderate` | FAIL | 3 vulnerabilities: 1 moderate, 2 high. |

Environment setup notes:

- The cloud image provides `python3` but not `python`.
- Python console scripts installed to `/home/ubuntu/.local/bin`, which is not on `PATH`.
- Node dependencies are absent until `npm ci` is run.

---

## Critical issues

1. **Release is not complete.** SWARM-003 and SWARM-004 remain open.
2. **Python test suite fails under declared dev dependencies.** Missing `dotenv` breaks test collection.
3. **Import-healer coverage gate currently fails.** CI confidence is blocked until this is fixed or justified.
4. **MCP catalog contains broken targets.** Four `swarm_mcp.servers.*` entries do not exist.
5. **npm audit has high-severity advisories.** `next`, `fast-uri`, and `postcss` need remediation before production.
6. **Node workspace is not represented in CI.** TypeScript code can regress without CI feedback.
7. **API/web tests and lint scripts are placeholders.** Product confidence is low outside shared timer logic.
8. **Documentation has conflicting product narratives.** SWARM MCP, AgentTools, and Family Focus Board are all represented as primary in different docs.
9. **Duplicate task-log artifacts created ambiguity.** Root `MASTER_TASK_LOG.md` is now a pointer, but remaining docs/tooling references still need cleanup.
10. **Security/import audit commands need tuning.** One scans fixture names as suspicious; the other scans 0 files.

---

## Missing components

### Package/release

- PyPI release evidence.
- Clean install verification.
- `CHANGELOG.md` or release notes for v0.1.0.
- Console-script smoke tests.
- Build artifact verification.

### CI/testing

- Passing Python test suite under CI dependency set.
- Node workspace CI.
- API integration tests.
- Web component/page tests.
- e2e happy path.
- MCP catalog validation test.
- Tools V2 registry health test.

### Documentation

- `.env.example` for API.
- API deployment guide.
- MCP packaged-vs-standalone distinction.
- Product boundary decision.
- Archive/deprecation policy.
- Updated contributing setup for actual remote and `python3`/PATH notes.

### Security/performance

- npm vulnerability remediation.
- Python dependency audit installation/config.
- Production CORS/auth review for API.
- Performance/load tests for message queues, pattern mining, and API routes.

---

## Duplicate, outdated, or abandoned work

| Item | Type | Recommendation |
|---|---|---|
| Root `MASTER_TASK_LOG.md` vs `docs/root/MASTER_TASK_LOG.md` | Duplicate/shadow | Root file converted to redirect-only pointer on 2026-05-17; finish updating references. |
| Root `MASTER_TASK_LIST.md` vs `docs/root/MASTER_TASK_LIST.md` | Duplicate/shadow | Root file is current audit deliverable; `docs/root` copy converted to pointer on 2026-05-17. |
| `mcp_servers` vs `swarm_mcp/servers` | Overlapping MCP surfaces | Document packaged vs standalone; add catalog tests; merge only intentionally. |
| `tools` vs `tools_v2` | Duplicate tool capability surfaces | Freeze V2 expansion until registry health is green; migrate high-value tools deliberately. |
| `docs/CODEBASE_RECON_AND_EXECUTION_PLAN.md` | Outdated doc | Mark as historical or refresh; it references absent `kanban-scheduler/`. |
| `docs/ARCHIVE_POINTER.md` | Potentially confusing archive note | Clarify that some listed domains still have current files in this checkout. |
| `tools/deprecated/` | Legacy code | Keep isolated; archive/delete after registry reference audit. |

---

## Code quality review

### Unused dependencies

No full unused-dependency analysis was run. Observed dependency concerns:

- `python-dotenv` is needed by test-imported `tools_v2` code but is only listed under `full`, not `dev`.
- `pip-audit` is used by the security scanner but not declared in `dev`.
- Node dependencies include vulnerable versions or vulnerable transitive packages.

### Duplicate logic

Likely duplicates:

- security scanning in `tools/security`, `mcp_servers/security_scanner_server.py`, and `tools_v2/categories/security_audit_tools.py`;
- testing/coverage tooling across `tools`, `mcp_servers/testing_server.py`, and `tools_v2/categories/testing_tools.py`;
- messaging/task functionality across `swarm_mcp/core`, `swarm_mcp/servers`, `mcp_servers`, and `tools_v2/categories/message_*`.

### Inconsistent patterns

- Some tools use registry/adapters; others are standalone scripts.
- MCP servers are split between package modules and script files.
- Docs use both root and `docs/root` task-log paths.
- TS packages use npm workspace scripts, but CI ignores them.

### Missing tests

- API route integration tests.
- Web app tests.
- MCP catalog validation.
- Tools V2 registry health.
- Console-script smoke tests.
- Security scan false-positive tests.

### Security concerns

- npm vulnerabilities.
- Python dependency audit skipped.
- Production auth/CORS behavior requires review.
- No obvious hardcoded secrets were found by the current scanner.

### Performance bottlenecks

Potential unmeasured areas:

- file-backed coordination state under concurrent agent use;
- pattern mining over large event histories;
- API DB route query behavior under larger boards;
- MCP server subprocess/tool execution overhead.

### Environment/config issues

- `python` command is unavailable in this environment; docs/scripts often use `python`.
- `/home/ubuntu/.local/bin` is not on `PATH` after pip user install.
- `DATABASE_URL` is required but no `.env.example` was observed.
- Node checks require `npm ci`.

---

## Architecture review

### Scalability

SWARM MCP is currently file/local-state oriented and suitable for lightweight coordination. It needs concurrency, locking, and persistence decisions before high-volume multi-agent use. Family Focus Board uses PostgreSQL and realtime events, which is a stronger production foundation, but lacks tests and deployment topology.

### Modularity

`swarm_mcp/core` is reasonably modular. Tooling is less modular because capabilities are repeated across standalone scripts, registries, and MCP adapters. The TypeScript workspace is cleanly split into API/web/shared packages.

### Separation of concerns

The biggest issue is repository-level separation, not individual modules. Product, package, local tooling, and archive surfaces coexist without a single current boundary document.

### API consistency

The API routes use Zod validation and Fastify conventions. MCP APIs are less consistent because packaged and standalone servers differ in module style and registration.

### Naming conventions

Naming is inconsistent across products:

- package: `swarm-mcp`;
- repo/product docs: SWARM MCP, WE ARE SWARM, AgentTools, Dream.OS;
- npm workspace: `family-focus-board`;
- package scopes: `@ffb/*`.

### Monorepo organization

The repo behaves like a monorepo but does not yet have monorepo governance. It needs clear lanes, CI per lane, and archive policy.

### CI/CD readiness

CI exists but is incomplete:

- Python path likely fails under current dependency state;
- Node path is absent;
- PyPI publish exists but has no recorded successful release evidence;
- security/import audits need reliability improvements.

---

## Refactor recommendations

1. **Separate release-critical package tests from optional toolbelt imports.**
   - Avoid making `swarm-mcp` release depend on every local tool category.

2. **Create an MCP catalog validator.**
   - Validate every configured module/script target exists and can initialize.

3. **Define canonical tool registry ownership.**
   - Pick `tools_v2` or legacy registry as the future; mark the other compatibility-only.

4. **Move deprecated scripts out of active scan paths.**
   - Keep compatibility shims only where tests prove active use.

5. **Convert docs shadows into pointers.**
   - Reduce duplicate `MASTER_TASK_*` content.

6. **Make the TypeScript lane self-validating.**
   - Add lint/test/build gates before adding more features.

---

## Quick wins

1. Add `python-dotenv` to the `dev` extra or avoid importing dotenv during test collection.
2. Add `pip-audit` to the security tooling dependency path.
3. Fix the 4 MCP catalog entries.
4. Add `swarm-tools` to README MCP config.
5. Finish updating remaining docs/tooling that still mention root `MASTER_TASK_LOG.md`.
6. Add `.env.example` for `apps/api`.
7. Add Node CI commands after `npm ci`.
8. Rename/allowlist fixture `config.py` files in the security scanner.
9. Update docs that say task log lives at repo root.
10. Add a real API health/route integration test.

---

## Suggested archival/deletion candidates

Do not delete until references are checked.

| Candidate | Recommendation |
|---|---|
| `tools/deprecated/` scripts with no registry references | Archive or delete after inventory. |
| Root `MASTER_TASK_LOG.md` | Keep as pointer until all consumers are updated; eventual deletion only after compatibility review. |
| `docs/root/MASTER_TASK_LIST.md` | Keep as pointer unless a generated SSOT-derived list replaces it. |
| Historical recon reports with stale paths | Keep under historical archive with clear banner. |
| Standalone MCP servers for archived domains | Freeze or archive if not actively used. |
| Generated `quarantine/BROKEN_IMPORTS.md` artifacts | Keep generated outputs out of source unless intentionally documented. |

---

## Top 10 highest priority actions

1. Fix Python test dependency/import failure (`dotenv`) and prove `python3 -m pytest tests -q`.
2. Fix or intentionally refresh import-healer coverage baseline.
3. Repair `mcp_servers/all_mcp_servers.json` missing targets and add catalog validation.
4. Complete SWARM-003 PyPI publish with captured output.
5. Complete SWARM-004 clean install/import/CLI/MCP verification.
6. Remediate npm vulnerabilities and re-run audit.
7. Add Node workspace CI for typecheck/tests/audit.
8. Replace API/web placeholder tests and lint scripts with real checks.
9. Decide and document product boundaries among SWARM MCP, AgentTools, and Family Focus Board.
10. Retire duplicate/stale task-log/task-list docs after references are fixed.

---

## Biggest technical risks

1. **False release confidence** from implemented code without PyPI/clean-install proof.
2. **CI blind spots** across TypeScript and optional tooling surfaces.
3. **Security exposure** from vulnerable Node dependencies and skipped Python audits.
4. **MCP runtime drift** from catalog entries that do not resolve.
5. **Scope fragmentation** across package, tooling, and product lanes.
6. **Documentation drift** causing agents/humans to update the wrong SSOT.
7. **Legacy code drag** from deprecated scripts still visible to scans and readers.

---

## Recommended next sprint

Focus on **gate restoration and release proof**, not feature expansion.

Sprint goals:

1. Make Python package tests collect and pass under declared dev dependencies.
2. Restore import-healer coverage gate.
3. Fix MCP catalog target drift.
4. Complete PyPI publish and clean install verification.
5. Patch npm vulnerabilities and add a minimal Node CI job.
6. Convert root/doc shadow task artifacts into pointers or explicitly mark them non-canonical.

Definition of done:

- All commands listed in `NEXT_UP.md` pass or have documented, accepted exceptions.
- `docs/root/MASTER_TASK_LOG.md` has dated evidence for release tasks.
- `PROJECT_AUDIT_REPORT.md` is updated if any risk classification changes.

---

## Suggested cleanup/refactor plan

### Step 1 — Stabilize gates

- Fix dependency declarations.
- Fix coverage baseline.
- Add catalog validation.
- Add Node CI.

### Step 2 — Clarify boundaries

- Document which lane is release-critical.
- Classify `mcp_servers` and `tools/deprecated`.
- Label historical docs.

### Step 3 — Consolidate surfaces

- Merge duplicated tool capabilities into one registry where useful.
- Keep compatibility shims tested.
- Remove unreferenced dead scripts after audit.

### Step 4 — Mature product lanes

- Finish SWARM MCP release.
- Add Family Focus Board API/web test coverage if that product stays active.
- Add deployment docs and operational checks.

---

## Estimated completion percentage per project

| Project | Estimated completion | Confidence |
|---|---:|---|
| SWARM MCP package | 80% | High |
| Packaged MCP servers | 75% | High |
| Standalone MCP servers | 60% | Medium |
| Tools CLI / legacy tooling | 65% | Medium |
| Toolbelt V2 | 55% | Medium |
| Family Focus Board API | 60% | Medium |
| Family Focus Board Web | 25% | High |
| Family Focus Board shared package | 80% | High |
| CI/CD | 50% | High |
| Documentation/planning | 55% before this audit, 70% for current deliverables after this audit | Medium |
