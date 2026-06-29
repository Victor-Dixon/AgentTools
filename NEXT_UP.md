# NEXT UP — SWARM MCP EXECUTION DASHBOARD

**Updated:** 2026-06-29 (passdown refresh)
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Scope:** Packaging readiness first; workspace audit blockers tracked second.

---

## What this project even is

SWARM MCP is a Python package (`swarm-mcp`) for multi-agent coordination over MCP.
It includes:
- a CLI for agent coordination workflows,
- MCP server entry points in `swarm_mcp/servers/`,
- core coordination modules in `swarm_mcp/core/`.

This dashboard is the human-readable companion to the SSOT task log.

---

## Where we are now (accurate status)

**Current phase:** Phase 0A — Consolidation + Packaging Readiness
**Release state:** Not yet published to PyPI
**Blocking tasks:** SWARM-003, SWARM-004

Interpretation: Python CI gates (SWARM-014, SWARM-015) and MCP catalog integrity (SWARM-016) are restored. SWARM-003/004 remain open: PyPI name `swarm-mcp` already hosts a different package (`swarm_mcp.server` only); this repo's coordination CLI has not been published under that name yet.

---

## Inventory proof snapshot (evidence as of 2026-03-23)

- `swarm_mcp/servers/*.py` count: **5** (`control.py`, `memory.py`, `messaging.py`, `tasks.py`, `tools.py`)
- CLI subcommands defined in `swarm_mcp/cli.py`: **12** (`status`, `send`, `inbox`, `search`, `learn`, `tasks`, `assign`, `vote`, `conflict`, `profile`, `prove`, `patterns`)
- Historical 2026-03 local branch snapshot: **work**

These are evidence points, not goals.

### Audit refresh (evidence as of 2026-05-17)

- `swarm_mcp/servers/*.py` count remains **5**.
- CLI subcommand count remains **12**.
- Standalone `mcp_servers/*_server.py` count: **27**.
- `mcp_servers/all_mcp_servers.json` entries: **23**.
- Broken MCP catalog targets: **0** (repaired 2026-06-29; was 4 missing `swarm_mcp.servers.*` modules).
- Python test files under `tests/`: **20**.
- Tooling volume: `tools` **259** Python files, `tools_v2` **89** Python files.
- TypeScript workspace files: `apps` **24** files, `packages` **7** files.

### Reproducibility note

Inventory values are SSOT-backed and reproducible using the command block in `docs/root/MASTER_TASK_LOG.md` (same date: 2026-03-23), including exact output for server file count, CLI subcommand count, and branch state.

---

## What we should focus on next (strict order)

1. **SWARM-003 — Build and publish**
   - run `python -m build`
   - run `twine upload dist/*` (or tag-push to trigger CI publish job)
   - capture exact output in `docs/root/MASTER_TASK_LOG.md`
2. **SWARM-004 — Fresh install verification**
   - in clean env: `pip install swarm-mcp`
   - verify import + minimal CLI smoke test
3. **SWARM-017 — Resolve npm audit findings**
   - patch or otherwise remediate `next`, `fast-uri`, and `postcss` advisories before TS deployment

---

## Definition of done for this transition

This transition is complete only when all are true:
- [x] SSOT has an accurate status statement (phase + blockers + release state)
- [x] inventory proof snapshot is updated with dated, reproducible evidence
- [x] SWARM-002 marked complete with concrete token setup record
- [x] SWARM-014 Python test gate restored
- [x] SWARM-015 import-healer coverage gate restored
- [x] SWARM-016 MCP catalog drift fixed
- [ ] SWARM-003 marked complete with actual publish command output
- [ ] SWARM-004 marked complete with clean install/import verification output
- [ ] SWARM-017 npm audit findings resolved or explicitly accepted for non-production use

---

## Agent passdown (2026-06-29 UTC)

**Branch/PR:** `cursor/restore-python-ci-gates-5822` — [PR #6](https://github.com/Victor-Dixon/AgentTools/pull/6)

### Completed this session

| Task | Outcome |
|---|---|
| SWARM-014 | Python test gate restored (`72 passed, 1 skipped`) |
| SWARM-015 | Import-healer coverage gate restored |
| SWARM-016 | MCP catalog drift fixed; `tests/test_mcp_catalog.py` added |
| SWARM-003 (partial) | Local `python -m build` + `twine check` pass |
| SWARM-004 (partial) | Local wheel install smoke test passes; PyPI install exposes wrong artifact |

### Evidence

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest tests -q
python3 -m build && python3 -m twine check dist/*
python3 -m pip index versions swarm-mcp
python3 -m pip install --target /tmp/swarm-pypi-install --no-cache-dir swarm-mcp==0.1.0
```

```text
72 passed, 1 skipped in 2.05s
twine check: PASSED (wheel + sdist)
PyPI versions: 0.5.0, 0.4.0, 0.3.0, 0.2.1, 0.2.0, 0.1.0
PyPI entry point: swarm-mcp = swarm_mcp.server:main  (NOT this repo's swarm CLI)
```

### Blockers

1. **PyPI name collision:** `pip install swarm-mcp` installs a minimal `server.py` package, not this repo's `swarm_mcp.cli` + MCP servers.
2. **Version conflict:** This repo is `0.1.0`, but PyPI already has `0.1.0`–`0.5.0` for the other artifact.
3. **No local token:** `PYPI_API_TOKEN` not available in agent environment for upload.

### Next agent ask (copy/paste)

```text
Confirm PyPI ownership for swarm-mcp, bump version to >=0.6.0 in pyproject.toml if appropriate, publish with PYPI_API_TOKEN (or tag-push CI job), then complete SWARM-004 by verifying:
  pip install swarm-mcp==<new-version>
  python -c "from swarm_mcp.cli import main"
  swarm status
Record evidence in docs/root/MASTER_TASK_LOG.md and leave a new Agent passdown in NEXT_UP.md.
```

---

## Tooling stream update (mirrors SSOT, 2026-03-24 UTC)

### Completed now
- Coverage non-regression gate implemented for import healer stream via `tools/swarm/tests/check_import_healer_coverage.py` (stdlib trace-backed baseline comparison).
- Baseline recorded in `tools/swarm/tests/import_healer_coverage_baseline.json` for:
  - `tools/swarm/agents/import_healer.py` → 90.85%
  - `tools/swarm/tests/validate_import_healer.py` → 97.62%
  - `tools/swarm/tests/test_import_healer.py` → 100.00%
- CI now runs the gate in `.github/workflows/swarm_ci.yml`.
- Validation harness updated to run in-process so import healer execution is counted by coverage tooling.

### Commands run (2026-03-24 UTC)
- `python -m py_compile tools/swarm/agents/import_healer.py tools/swarm/tests/validate_import_healer.py tools/swarm/tests/test_import_healer.py`
- `python -m pytest -q tools/swarm/tests/test_import_healer.py`
- `python tools/swarm/tests/check_import_healer_coverage.py --write-baseline`
- `python tools/swarm/tests/check_import_healer_coverage.py` *(expected pass path)*
- `python tools/swarm/tests/check_import_healer_coverage.py --baseline-file /tmp/import_healer_coverage_strict.json` *(expected fail path)*

### Active blocker
- Pre-commit remains broken in this environment: `.git/hooks/pre-commit` targets `./node_modules/@fastify/pre-commit/hook`, but executable is missing; `pre-commit` CLI is not installed. Mitigation is explicit command checks until hook dependencies are restored.

---

## Workspace audit update (mirrors SSOT, 2026-05-17 UTC)

### Deliverables now available
- `MASTER_TASK_LIST.md`
- `ROADMAP.md`
- `PROJECT_STRUCTURE.md`
- `PROJECT_AUDIT_REPORT.md`

### Commands run after declared dependency installation
- `python3 -m pip install -e ".[dev]"`
- `npm ci`
- `python3 -m pytest tests -q` *(blocked: missing `dotenv`)*
- `python3 tools/swarm/tests/check_import_healer_coverage.py` *(blocked: coverage regression)*
- `PYTHONPATH=. python3 tools/cli.py --security-scan` *(needs triage: fixture false positives, skipped Python audit, npm findings)*
- `PYTHONPATH=. python3 tools/cli.py --audit-imports` *(weak pass: scanned 0 files in default `src/`)*
- `npm -ws run typecheck` *(pass)*
- `npm -ws run test` *(partial pass: shared Vitest passes; API/web placeholders)*
- `npm audit --audit-level=moderate` *(fail: 3 vulnerabilities)*

### Current highest-risk blockers (refreshed 2026-06-29)

1. PyPI publish strategy unresolved: existing `swarm-mcp` releases do not match this repository's package surface.
2. SWARM-004 cannot pass until the correct artifact is published to PyPI.
3. Node dependency audit fails (`npm audit --audit-level=moderate`).
4. API/web code lacks real tests and linting.
5. Pre-commit hook dependencies remain missing in some environments.

---

# Production Restoration Backlog

## Objective

Restore AgentTools into a production-ready Dream.OS toolbelt/MCP runtime using TDD and non-breaking architecture seams.

## Current Architecture Decision

See:

- `docs/architecture/DOMAIN_MODEL_DISCOVERY.md`
- `docs/architecture/CODE_INVENTORY.md`
- `docs/architecture/adr/0001-production-architecture.md`

## Active Product Spine

- `swarm_mcp/`
- `mcp_servers/`
- `apps/api/`
- `apps/web/`
- `packages/shared/`
- `tests/`
- `docs/`

## TDD Rule

No refactor without characterization tests.

## Next Workstream

### 1. Agent domain

- Discover `agent_dna.py` public behavior.
- Add tests for agent identity/capabilities.
- Extract pure domain object only if needed.

### 2. Message domain

- Discover `messaging.py` and `messaging_templates.py`.
- Add tests for message construction, routing fields, and validation.
- Define canonical message envelope.

### 3. Task domain

- Discover `task_scoring.py` and task server behavior.
- Add tests for scoring, priority, and assignment rules.
- Define task lifecycle states.

### 4. Work proof / verification

- Discover `work_proof.py` and `verification.py`.
- Add tests for proof claims, evidence, and pass/fail validation.
- Define completion contract.

### 5. MCP adapter consolidation

- Compare `swarm_mcp/servers/` and `mcp_servers/`.
- Mark each legacy MCP server as keep, merge, archive, or delete.
- Preserve compatibility imports until callers are migrated.

## Exit Criteria

- Production gate passes.
- Import boundary tests pass.
- Domain inventory is generated.
- Active vs legacy surfaces are documented.
- Next domain workstream has failing-first tests before implementation.
