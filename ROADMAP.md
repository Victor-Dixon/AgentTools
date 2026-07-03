# ROADMAP

**Last updated:** 2026-07-03  
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`  
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`  
**Roadmap scope:** SWARM MCP package release first, workspace stabilization second, product/tooling consolidation third.

---

## Current phase

### Phase 0A — Consolidation + Packaging Readiness (`IN_PROGRESS`)

The canonical release lane is **SWARM MCP** (`swarm-mcp`), a Python package for multi-agent coordination over MCP.

Primary release surfaces:

- `swarm_mcp/core/` — coordination domain and application services,
- `swarm_mcp/cli.py` — operator CLI,
- `swarm_mcp/servers/` — packaged MCP servers,
- `pyproject.toml` — package metadata and console scripts,
- `docs/root/MASTER_TASK_LOG.md` — execution SSOT.

Repository reality:

- **SWARM MCP** is the release-critical lane.
- **AgentTools/operator tooling** (`mcp_servers/`, `tools/`, `tools_v2/`) is active but secondary to the PyPI release.
- **Family Focus Board** (`apps/`, `packages/`) is a separate TypeScript product lane and should not block SWARM MCP release unless explicitly promoted.

---

## Milestones

### M0 — Restore deterministic Python gates (`COMPLETE` 2026-06-29)

**Goal:** A clean checkout can run the declared Python validation commands without hidden setup.

Completed evidence in SSOT:

- `python3 -m pip install -e ".[dev]"` succeeds.
- `python3 -m pytest tests -q` reported `72 passed, 1 skipped`.
- `python3 tools/swarm/tests/check_import_healer_coverage.py` passes after reviewed baseline refresh.

### M1 — Package release proof (`BLOCKED` — PyPI secret/configuration)

**Goal:** Complete SWARM-003 and SWARM-004.

Current state:

- Package version is `0.6.0`.
- Tag `v0.6.0` was pushed.
- CI build/test passed.
- PyPI publish failed because `TWINE_PASSWORD` was empty in the tag publish job.

Exit criteria:

- `python3 -m build` and `twine check` output captured in SSOT. Done locally.
- PyPI upload or GitHub tag publish output captured with secrets redacted. Blocked.
- Clean environment proves `pip install swarm-mcp==0.6.0`, import smoke, and `swarm status`. Pending publish.

### M2 — MCP and tool surface integrity (`COMPLETE` 2026-06-29)

**Goal:** Every active MCP catalog target resolves to an existing module/script.

Completed evidence in SSOT:

- `mcp_servers/all_mcp_servers.json` has 23 catalog entries.
- Catalog validation reports 0 missing targets.
- `tests/test_mcp_catalog.py` exists.
- Broken `tools_v2` registry entries are documented in `docs/TOOLS_V2_DISABLED_REGISTRY_ENTRIES.md`.

### M3 — Family Focus Board validation (`TODO`)

**Goal:** If the TypeScript workspace remains active, it has real quality gates and minimal product integration.

Exit criteria:

- API/web lint scripts run real linters.
- API has integration tests around org, board, list, card, timer, activity, inventory, and auth flows.
- Web reads/writes at least one board flow through the API.
- Shared timer state remains covered by Vitest.
- Deployment docs define `DATABASE_URL`, migrations, seed, and runtime ports.
- Remaining npm audit risk is remediated or explicitly accepted for the deployment target.

### M4 — Documentation and governance cleanup (`IN_PROGRESS` 2026-07-03)

**Goal:** Maintainers can identify the repository domain model, active product lanes, current status, completed work, remaining work, and next task without reading obsolete plans.

Completed in the 2026-07-03 documentation audit:

- Added canonical domain model: `docs/architecture/DOMAIN_MODEL.md`.
- Updated PRD to distinguish SWARM MCP, AgentTools/operator tooling, and Family Focus Board.
- Refreshed roadmap/task/dashboard documents to remove stale Python gate and MCP catalog blockers.
- Updated repository description guidance in `docs/governance/github_description.md`.

Remaining exit criteria:

- Classify or banner remaining historical docs that still look actionable.
- Reconcile task-log mutation code paths with `docs/root/MASTER_TASK_LOG.md` policy.
- Complete classification of standalone MCP servers and legacy tool scripts.

---

## Short-term initiatives

1. **Unblock SWARM-003 PyPI publish.**
   - Add/configure `PYPI_API_TOKEN` for `Victor-Dixon/AgentTools`.
   - Re-run the failed `v0.6.0` publish job or re-trigger tag publish.
   - Record redacted output in `docs/root/MASTER_TASK_LOG.md`.

2. **Complete SWARM-004 clean install proof.**
   - Install `swarm-mcp==0.6.0` from PyPI after publish.
   - Verify import and CLI smoke.
   - Record output in SSOT and mirror `NEXT_UP.md`.

3. **Continue documentation governance.**
   - Keep `docs/architecture/DOMAIN_MODEL.md` current.
   - Add historical/non-canonical banners to older plans as they are touched.
   - Keep `docs/root/MASTER_TASK_LOG.md` first and `NEXT_UP.md` second for status changes.

4. **Patch or accept remaining TS dependency risk.**
   - Re-run Node checks after dependency changes.
   - Document accepted risk if Family Focus Board remains non-production.

5. **Classify secondary tool surfaces.**
   - Mark standalone MCP servers and legacy tools as active, adapter-only, legacy, archive, or unknown.
   - Keep disabled `tools_v2` adapters out of active registry until fixed.

---

## Long-term initiatives

1. **Toolbelt consolidation.**
   - Promote stable tools into one registry.
   - Convert legacy scripts to adapters only when actively used.
   - Archive or quarantine unreferenced duplicates after classification.

2. **Family Focus Board maturity.**
   - Build API-backed web workflows.
   - Add API integration/e2e coverage.
   - Define deployment topology and observability.

3. **Operational MCP platform.**
   - Keep packaged public MCP servers separate from local/operator MCP servers.
   - Version catalogs and validate server boot in CI.
   - Add compatibility policy for external MCP clients.

4. **Documentation governance.**
   - Keep freshness dates and canonical/non-canonical banners on planning docs.
   - Add docs contract tests for required domain/status docs if drift recurs.
   - Refresh audit reports after major architecture changes.

---

## Dependencies

| Dependency | Required by | Current risk |
|---|---|---|
| `PYPI_API_TOKEN` GitHub secret/configuration | SWARM-003 publish | Missing or not passed to tag publish job; CI log showed empty `TWINE_PASSWORD`. |
| PyPI `swarm-mcp` project ownership | SWARM-003 publish | Existing versions `0.1.0`-`0.5.0` do not expose this repo's current CLI; `0.6.0` must publish before clean proof. |
| Python dev dependencies | Tests, CI, release confidence | Green as of 2026-06-29 SSOT evidence. |
| Import-healer baseline | CI gate | Green as of 2026-06-29 SSOT evidence. |
| MCP catalog accuracy | MCP client setup | 0 missing targets as of 2026-06-29 SSOT evidence. |
| Node dependencies | TS typecheck/tests/audit | 2 moderate advisories remain; API/web tests and lint are placeholders. |
| PostgreSQL / `DATABASE_URL` | `apps/api` runtime | Required; deployment status and `.env.example` coverage incomplete. |

---

## Risk areas

- **Release risk:** `swarm-mcp==0.6.0` is implemented and tagged but not externally published or clean-install verified.
- **Documentation risk:** Some historical docs still contain stale claims; the active canonical set now points to SSOT and domain model.
- **Architecture risk:** Three lanes share one repository; contributors must avoid treating FFB cards, SWARM tasks, and AgentTools task logs as one model.
- **Maintenance risk:** Large legacy/deprecated tool volume increases false positives and duplicate fixes.
- **Security risk:** Remaining npm advisories are accepted only while the TS lane is non-production.
- **Runtime unknowns:** Live MCP/server deployment topology is not documented in this repository.

---

## Suggested sequencing

1. Complete SWARM-003 publish.
2. Complete SWARM-004 clean install proof.
3. Keep the domain model and SSOT synchronized after publish evidence changes.
4. Resolve or accept remaining npm audit risk before any TS deployment.
5. Replace API/web placeholder quality gates.
6. Classify standalone MCP servers and legacy tools.
7. Reconcile task-log mutation code with `docs/root/MASTER_TASK_LOG.md`.
