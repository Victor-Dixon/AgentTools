# NEXT UP — SWARM MCP EXECUTION DASHBOARD

**Updated:** 2026-03-24
**Primary SSOT:** `MASTER_TASK_LOG.md`  
**Scope:** Packaging readiness only (Phase 0A)

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

Interpretation: implementation exists and local package workflows exist, but external release verification is incomplete.

---

## Inventory proof snapshot (evidence as of 2026-03-23)

- `swarm_mcp/servers/*.py` count: **5** (`control.py`, `memory.py`, `messaging.py`, `tasks.py`, `tools.py`)
- CLI subcommands defined in `swarm_mcp/cli.py`: **12** (`status`, `send`, `inbox`, `search`, `learn`, `tasks`, `assign`, `vote`, `conflict`, `profile`, `prove`, `patterns`)
- Active local branch: **work**

These are evidence points, not goals.

### Reproducibility note

Inventory values are SSOT-backed and reproducible using the command block in `MASTER_TASK_LOG.md` (same date: 2026-03-23), including exact output for server file count, CLI subcommand count, and branch state.

---

## What we should focus on next (strict order)

1. **SWARM-003 — Build and publish**
   - run `python -m build`
   - run `twine upload dist/*`
   - capture exact output in `MASTER_TASK_LOG.md`
2. **SWARM-004 — Fresh install verification**
   - in clean env: `pip install swarm-mcp`
   - verify import + minimal CLI smoke test

---

## Definition of done for this transition

This transition is complete only when all are true:
- [ ] SSOT has an accurate status statement (phase + blockers + release state)
- [ ] inventory proof snapshot is updated with dated, reproducible evidence
- [x] SWARM-002 marked complete with concrete token setup record
- [ ] SWARM-003 marked complete with actual publish command output
- [ ] SWARM-004 marked complete with clean install/import verification output

---

## Operator handoff note (2026-03-24)

SWARM-002 was completed on 2026-03-24 with redacted credential evidence recorded in SSOT. Proceed immediately to SWARM-003.

---

## Tooling stream update (mirrors SSOT, 2026-03-24 UTC)

### Completed now
- Import healer confidence hardening and safe rewrite gating shipped in `tools/swarm/agents/import_healer.py`.
- Local fixture-based validation added under `tools/swarm/tests/`.
- Recovery registry updated at `docs/recovery/recovery_registry.yaml` for new files.

### Commands run (2026-03-24 UTC)
- `python -m py_compile tools/swarm/agents/import_healer.py tools/swarm/tests/validate_import_healer.py tools/swarm/tests/test_import_healer.py`
- `python tools/swarm/tests/validate_import_healer.py`
- `python -m pytest -q tools/swarm/tests/test_import_healer.py`
- `python -m coverage run tools/swarm/tests/validate_import_healer.py` *(failed: module not installed)*

### Active blockers
- Coverage tooling is not installed in the current environment, so coverage non-regression could not be measured.
- No CI-enforced "coverage must not dip" threshold is currently wired for this tooling stream.
