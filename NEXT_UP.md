# NEXT UP — SWARM MCP EXECUTION DASHBOARD

**Updated:** 2026-03-23  
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
**Blocking tasks:** SWARM-002, SWARM-003, SWARM-004

Interpretation: implementation exists and local package workflows exist, but external release verification is incomplete.

---

## Inventory proof snapshot (evidence as of 2026-03-23)

- `swarm_mcp/servers/*.py` count: **5** (`control.py`, `memory.py`, `messaging.py`, `tasks.py`, `tools.py`)
- CLI subcommands defined in `swarm_mcp/cli.py`: **12** (`status`, `send`, `inbox`, `search`, `learn`, `tasks`, `assign`, `vote`, `conflict`, `profile`, `prove`, `patterns`)
- Active local branch: **work**

These are evidence points, not goals.

---

## What we should focus on next (strict order)

1. **SWARM-002 — PyPI account/token readiness**
   - confirm account owner and token scope
   - document token storage path for CI/local publish
2. **SWARM-003 — Build and publish**
   - run `python -m build`
   - run `twine upload dist/*`
   - capture exact output in `MASTER_TASK_LOG.md`
3. **SWARM-004 — Fresh install verification**
   - in clean env: `pip install swarm-mcp`
   - verify import + minimal CLI smoke test

---

## Definition of done for this transition

This transition is complete only when all are true:
- [ ] SSOT has an accurate status statement (phase + blockers + release state)
- [ ] inventory proof snapshot is updated with dated, reproducible evidence
- [ ] SWARM-002 marked complete with concrete token setup record
- [ ] SWARM-003 marked complete with actual publish command output
- [ ] SWARM-004 marked complete with clean install/import verification output

