# NEXT UP — SWARM MCP EXECUTION DASHBOARD

**Updated:** 2026-07-03 (documentation/domain model audit validated)  
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`  
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`  
**Scope:** Packaging readiness first; workspace documentation/tooling blockers tracked second.

---

## What this project even is

SWARM MCP is a Python package (`swarm-mcp`) for multi-agent coordination over MCP.
It includes:
- core coordination modules in `swarm_mcp/core/`,
- a CLI for agent coordination workflows,
- MCP server entry points in `swarm_mcp/servers/`.

This repository also contains:
- AgentTools/operator tooling in `mcp_servers/`, `tools/`, and `tools_v2/`,
- a separate Family Focus Board TypeScript product lane in `apps/` and `packages/`.

This dashboard is the human-readable companion to the SSOT task log.

---

## Where we are now (accurate status)

**Current phase:** Phase 0A — Consolidation + Packaging Readiness  
**Release state:** v0.6.0 tagged; PyPI upload blocked on missing/unused GitHub secret configuration  
**Blocking tasks:** SWARM-003 (publish), SWARM-004 (PyPI install verify)  
**Documentation state:** SWARM-018 domain model/status synchronization validated on branch `cursor/domain-model-doc-audit-84b4` / PR #8

Interpretation: M0 (Python gates) and M2 (MCP catalog) are complete. Package built and tagged; CI publish failed because `PYPI_API_TOKEN` was not available to `TWINE_PASSWORD` in `Victor-Dixon/AgentTools`.

---

## Inventory proof snapshot

- `swarm_mcp/servers/*.py` count: **5**
- CLI subcommands: **12**
- `mcp_servers/all_mcp_servers.json` entries: **23**; missing targets: **0**
- Package version: **0.6.0**; release tag: **v0.6.0**
- PyPI latest published: **0.5.0** (0.6.0 not yet live)
- Python tests: **72 passed, 1 skipped** per 2026-06-29 SSOT evidence
- npm audit: **2 moderate** per 2026-06-29 SSOT evidence
- Canonical domain model: `docs/architecture/DOMAIN_MODEL.md`

---

## What we should focus on next (strict order)

1. **SWARM-003 — Unblock PyPI publish**
   - Add/configure `PYPI_API_TOKEN` in GitHub repo secrets.
   - Re-run failed publish job for tag `v0.6.0` (run `28408184056`) or re-trigger tag publish.
   - Runbook: `docs/release/SWARM-003_PUBLISH_RUNBOOK.md`.
2. **SWARM-004 — PyPI install verification**
   - `pip install swarm-mcp==0.6.0`
   - Verify `from swarm_mcp.cli import main` and `swarm status`.
3. **Documentation governance follow-through**
   - Keep `docs/architecture/DOMAIN_MODEL.md`, PRD, roadmap, task list, SSOT, and `NEXT_UP.md` synchronized.
   - Continue marking historical docs as non-canonical when touched.
4. **SWARM-017 — Remaining npm audit** (non-blocking for Python release)
   - 2 moderate `next`/`postcss` advisories remain accepted only while the TS lane is non-production.

---

## Definition of done for this transition

- [x] SWARM-002 PyPI token runbook (local credential/storage runbook; CI secret later disproven)
- [x] SWARM-014 Python test gate
- [x] SWARM-015 import-healer coverage gate
- [x] SWARM-016 MCP catalog drift fixed
- [x] SWARM-018 documentation/domain model audit implemented
- [x] SWARM-018 validation evidence recorded
- [ ] SWARM-003 PyPI publish with evidence
- [ ] SWARM-004 clean PyPI install verification
- [ ] SWARM-017 npm audit resolved or accepted for deployment target

---

## Agent passdown (2026-07-03 UTC)

**Branch/PR:** `cursor/domain-model-doc-audit-84b4` — PR #8

### Completed this session

| Task | Outcome |
|---|---|
| SWARM-018 | Added canonical domain model and synchronized active docs around SWARM MCP, AgentTools/operator tooling, and Family Focus Board boundaries. |
| SWARM-002/SWARM-003 docs | Reconciled token contradiction: local token runbook exists, but CI secret/configuration is not confirmed and blocked publish. |
| Historical docs | Added freshness/non-canonical notices to stale planning and audit docs. |
| Validation | Focused docs/catalog tests, full Python suite, import-healer coverage gate, and stale-claim scan completed. |

### Evidence

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest tests/test_docs_contract.py tests/test_project_artifact_contract.py tests/test_mcp_catalog.py -q
python3 -m pytest tests -q
python3 tools/swarm/tests/check_import_healer_coverage.py
targeted markdown stale-claim scan for old Python/MCP blocker phrases
```

```text
Dev dependency install succeeded; pytest was absent before install.
Focused docs/catalog tests: 9 passed in 0.05s.
Inventory check: 5 packaged servers, 12 CLI subcommands, 23 MCP catalog entries, 0 missing targets.
Full Python suite: 72 passed, 1 skipped in 2.21s.
Import healer coverage gate: 1 passed; coverage gate passed.
Stale-claim scan: remaining matches are historical-context lines only.
```

### Blockers

1. **`PYPI_API_TOKEN` not configured or not passed** in `Victor-Dixon/AgentTools` GitHub Actions; CI log showed empty `TWINE_PASSWORD`.
2. SWARM-004 cannot complete until `swarm-mcp==0.6.0` is live on PyPI.
3. Actual hosted GitHub repository description metadata still requires a write-capable repository metadata update; this branch updates the canonical description text in `docs/governance/github_description.md`.

### Next agent ask (copy/paste)

```text
SWARM-018 is complete on PR #8. Next, unblock SWARM-003:
  add/configure PYPI_API_TOKEN in GitHub secrets for Victor-Dixon/AgentTools,
  re-run the failed v0.6.0 publish job or re-trigger the v0.6.0 tag publish,
  record redacted publish output in docs/root/MASTER_TASK_LOG.md,
  then complete SWARM-004 clean install proof with pip install swarm-mcp==0.6.0, import smoke, and swarm status.
```

---

## Production Restoration Backlog

See `docs/architecture/adr/0001-production-architecture.md` and `docs/architecture/DOMAIN_MODEL.md` — secondary to PyPI release path.
