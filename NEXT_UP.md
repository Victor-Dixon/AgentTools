# NEXT UP — PROJECT ROADMAP DASHBOARD (SSOT COMPANION)

**Updated:** 2026-03-21  
**Primary SSOT:** `MASTER_TASK_LOG.md`  
**Purpose of this file:** give humans a fast, accurate view of current phase, next actions, and exact agent asks.

---

## 1) Current Phase (Plain English)

**We are in:** **Phase 0A — Consolidation + Packaging Readiness**  
**We are not yet in:** Launch / Growth phases.

Reason: packaging-to-release chain is incomplete until SWARM-002/003/004 are finished.

---

## 2) Current Status Snapshot

- ✅ Core swarm modules and major MCP server surfaces exist.
- ✅ Testing foundation is present.
- ⚠️ PyPI release path is still blocked by account/token + publish + install verification tasks.
- ✅ Local branch situation is already consolidated to one branch: `work`.

---

## 3) Critical Path (Do In This Order)

1. **SWARM-002 (Account & Token)**
   - Create PyPI account
   - Create API token
   - Store token securely for CI/local publish flow

2. **SWARM-003 (Publish)**
   - Run package build
   - Publish with twine
   - Record exact command outputs in task log

3. **SWARM-004 (Verify Install)**
   - Test install in clean environment
   - Validate import + CLI sanity checks
   - Mark ready-for-launch-gate if successful

---

## 4) What We Should Ask the Agent Next (Ready-to-send prompts)

### Prompt A — SWARM-002
`Complete SWARM-002 now: create a PyPI setup checklist, document token creation/storage steps, and update MASTER_TASK_LOG.md with completion status and date.`

### Prompt B — SWARM-003
`Execute SWARM-003 now: run build + publish commands, capture outputs/errors, and update MASTER_TASK_LOG.md with exact results.`

### Prompt C — SWARM-004
`Execute SWARM-004 in a clean environment: install swarm-mcp from PyPI, verify import and CLI smoke test, then update MASTER_TASK_LOG.md and NEXT_UP.md.`

---

## 5) Definition of “Phase Complete” for 0A

Phase 0A is complete only when:
- [ ] SWARM-002 complete
- [ ] SWARM-003 complete
- [ ] SWARM-004 complete
- [ ] Launch checklist can be entered without blockers

---

## 6) Update Rule

After any critical-path task is completed, update:
1. `MASTER_TASK_LOG.md` (SSOT status first)
2. `NEXT_UP.md` (human dashboard second)
