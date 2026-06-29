# NEXT UP — SWARM MCP EXECUTION DASHBOARD

**Updated:** 2026-06-29 (post-release passdown)
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
**Release state:** v0.6.0 tagged; PyPI upload blocked on missing GitHub secret
**Blocking tasks:** SWARM-003 (publish), SWARM-004 (PyPI install verify)

Interpretation: M0 (Python gates) and M2 (MCP catalog) are complete. Package built and tagged; CI publish failed because `PYPI_API_TOKEN` is not set in `Victor-Dixon/AgentTools`.

---

## Inventory proof snapshot (evidence as of 2026-06-29)

- `swarm_mcp/servers/*.py` count: **5**
- CLI subcommands: **12**
- `mcp_servers/all_mcp_servers.json` entries: **23**; missing targets: **0**
- Package version: **0.6.0**; release tag: **v0.6.0**
- PyPI latest published: **0.5.0** (0.6.0 not yet live)
- Python tests: **72 passed, 1 skipped**
- npm audit: **2 moderate** (down from 7; `next`/`postcss` transitive)

---

## What we should focus on next (strict order)

1. **SWARM-003 — Unblock PyPI publish**
   - Add `PYPI_API_TOKEN` to GitHub repo secrets
   - Re-run failed publish job for tag `v0.6.0` (run `28408184056`)
   - Runbook: `docs/release/SWARM-003_PUBLISH_RUNBOOK.md`
2. **SWARM-004 — PyPI install verification**
   - `pip install swarm-mcp==0.6.0`
   - Verify `from swarm_mcp.cli import main` and `swarm status`
3. **SWARM-017 — Remaining npm audit** (non-blocking for Python release)
   - 2 moderate `next`/`postcss` — accept or force-upgrade when web ships

---

## Definition of done for this transition

- [x] SWARM-002 PyPI token runbook
- [x] SWARM-014 Python test gate
- [x] SWARM-015 import-healer coverage gate
- [x] SWARM-016 MCP catalog drift fixed
- [ ] SWARM-003 PyPI publish with evidence
- [ ] SWARM-004 clean PyPI install verification
- [ ] SWARM-017 npm audit resolved or accepted

---

## Agent passdown (2026-06-29 UTC)

**Branch/PR:** `master` — PR #6 squash-merged; PR #7 squash-merged; tag `v0.6.0` pushed

### Completed this session

| Task | Outcome |
|---|---|
| PR #6 | Squash-merged: SWARM-014/015/016 + passdown policy |
| PR #7 | Squash-merged: v0.6.0 bump, CI fix (`master`+`v*` tags), npm audit fix |
| SWARM-003 (partial) | Tag `v0.6.0` pushed; CI build/test **PASSED**; publish **FAILED** (empty `PYPI_API_TOKEN`) |
| SWARM-017 (partial) | `npm audit fix`: 7 vulns → 2 moderate |
| ROADMAP | M0 + M2 marked complete; M1 blocked on secret |

### Evidence

```bash
gh pr merge 6 --squash && gh pr merge 7 --squash
git tag v0.6.0 && git push origin v0.6.0
gh run watch 28408184056
```

```text
build-and-test: PASSED
publish-pypi: FAILED — TWINE_PASSWORD empty, HTTP 403 Forbidden
PyPI versions still: 0.5.0 latest (0.6.0 not published)
```

### Blockers

1. **`PYPI_API_TOKEN` not configured** in `Victor-Dixon/AgentTools` GitHub secrets (CI log shows empty password).
2. SWARM-004 cannot complete until 0.6.0 is live on PyPI.

### Next agent ask (copy/paste)

```text
Add PYPI_API_TOKEN to Victor-Dixon/AgentTools GitHub secrets, re-run the failed v0.6.0 publish job, record redacted twine output in docs/root/MASTER_TASK_LOG.md, then run SWARM-004:
  pip install swarm-mcp==0.6.0
  python -c "from swarm_mcp.cli import main"
  swarm status
Leave a new Agent passdown in NEXT_UP.md.
```

---

## Production Restoration Backlog

See `docs/architecture/adr/0001-production-architecture.md` — secondary to PyPI release path.
