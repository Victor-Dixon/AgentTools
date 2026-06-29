# NEXT UP — SWARM MCP EXECUTION DASHBOARD

**Updated:** 2026-06-29
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

Interpretation: Python CI gates (SWARM-014, SWARM-015) and MCP catalog integrity (SWARM-016) are restored. Remaining blockers are PyPI publish (SWARM-003) and clean-install verification from PyPI (SWARM-004).

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

## Operator handoff note (2026-06-29)

SWARM-014, SWARM-015, and SWARM-016 are complete. Python CI gates and MCP catalog validation pass. Local package build and wheel install smoke test succeeded. Proceed to SWARM-003/004 (PyPI publish + `pip install swarm-mcp` verification).

Evidence (2026-06-29):

```bash
python3 -m pytest tests -q
python3 -m build
python3 -m pip install --target /tmp/swarm-mcp-install dist/swarm_mcp-0.1.0-py3-none-any.whl
PYTHONPATH=/tmp/swarm-mcp-install python3 -m swarm_mcp.cli status
```

```text
72 passed, 1 skipped in 2.05s
Successfully built swarm_mcp-0.1.0.tar.gz and swarm_mcp-0.1.0-py3-none-any.whl
🐺 Swarm Status — 📊 1/1 agents ready
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

### Current highest-risk blockers
1. Python test gate fails under declared dev dependencies.
2. Import-healer coverage baseline no longer passes.
3. MCP catalog has missing targets.
4. Node dependency audit fails.
5. API/web code lacks real tests and linting.

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
