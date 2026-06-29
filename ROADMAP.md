# ROADMAP

**Last updated:** 2026-06-29
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Roadmap scope:** SWARM MCP package release first, workspace stabilization second, product/tooling consolidation third.

---

## Current phase

### Phase 0A — Consolidation + Packaging Readiness (`IN_PROGRESS`)

The canonical release lane is still **SWARM MCP** (`swarm-mcp`), a Python package with:

- core coordination logic in `swarm_mcp/core/`,
- operator CLI in `swarm_mcp/cli.py`,
- packaged MCP servers in `swarm_mcp/servers/`,
- release status tracked in `docs/root/MASTER_TASK_LOG.md`.

The 2026-05-17 audit adds an important constraint: this repository is also carrying a TypeScript Family Focus Board workspace and multiple tool/MCP surfaces. Those lanes should not block the PyPI release unless they are part of the package test/release contract.

---

## Upcoming milestones

### M0 — Restore deterministic gates (`COMPLETE` 2026-06-29)

**Goal:** A clean checkout can run the declared validation commands without hidden setup.

Dependencies:
- Python dev dependency path must include everything imported by `tests/`.
- Import-healer coverage baseline must match intended behavior.
- Node workspace dependencies must be installed via `npm ci` when Node gates are used.

Exit criteria:
- `pip install -e ".[dev]"` succeeds.
- `python3 -m pytest tests -q` passes.
- `python3 tools/swarm/tests/check_import_healer_coverage.py` passes or has a reviewed baseline update.
- `PYTHONPATH=. python3 tools/cli.py --security-scan` has no untriaged high-risk findings.
- `npm -ws run typecheck` passes after `npm ci`.
- `npm -ws run test` runs real tests for every active workspace or explicitly documents placeholder packages.

### M1 — Package release proof (`BLOCKED` — PyPI secret)

**Goal:** Complete SWARM-003 and SWARM-004.

Dependencies:
- M0 Python gates are green. ✅
- Maintainer PyPI token must be configured in GitHub secrets (`PYPI_API_TOKEN`). ❌ empty on tag `v0.6.0` publish attempt

Exit criteria:
- `python3 -m build` output captured in `docs/root/MASTER_TASK_LOG.md`. ✅
- `twine upload dist/*` or GitHub tag publish output captured with secrets redacted. ❌ 403 — missing token
- Clean environment proves `pip install swarm-mcp==0.6.0`, import smoke, CLI smoke. ⏳ pending publish

### M2 — MCP and tool surface integrity (`COMPLETE` 2026-06-29)

**Goal:** Every documented MCP/tool entry either works, is marked legacy, or is removed from active catalogs.

Dependencies:
- M0 test environment fixed.
- Product boundary decision recorded.

Exit criteria:
- `mcp_servers/all_mcp_servers.json` has no missing targets.
- Catalog validation test is in CI.
- `mcp_servers/` README classifies packaged vs standalone servers.
- `tools_v2` registry health test is added or failing entries are marked disabled with rationale.
- `tools/deprecated/` is excluded from active scans unless explicitly selected.

### M3 — Family Focus Board validation (`TODO`)

**Goal:** If the TS workspace remains active, it has real quality gates and minimal product integration.

Dependencies:
- Node dependency vulnerabilities resolved.
- CI includes Node gates.

Exit criteria:
- API/web lint scripts run real linters.
- API has integration tests around org, board, list, card, timer, activity, and auth flows.
- Web reads/writes at least one board flow through the API.
- Shared timer state remains covered by Vitest.
- Deployment docs define `DATABASE_URL`, migrations, seed, and runtime ports.

### M4 — Documentation and governance cleanup (`TODO`)

**Goal:** Maintainers can identify the active product and next task without reading obsolete plans.

Dependencies:
- M1/M2 decisions are complete.

Exit criteria:
- Root `MASTER_TASK_LOG.md` is a redirect-only stub or removed after references are fixed.
- `docs/root/MASTER_TASK_LIST.md` no longer contradicts the SSOT.
- PRD clearly labels AgentTools, SWARM MCP, and Family Focus Board relationships.
- Historical docs with stale path references are marked as archived snapshots.
- `PROJECT_STRUCTURE.md` and `PROJECT_AUDIT_REPORT.md` are refreshed after major architecture changes.

---

## Short-term initiatives

1. **Make Python gates green.**
   - Add/adjust test dependencies for `dotenv`.
   - Re-run full `tests/` suite.
   - Fix import-healer coverage regression.

2. **Repair release path.**
   - Build wheel/sdist.
   - Publish to PyPI.
   - Prove clean install.

3. **Fix MCP catalog drift.**
   - Replace missing `swarm_mcp.servers.*` catalog targets with existing `mcp_servers/*_server.py` targets or implement the missing packaged modules.
   - Add a catalog validation test.

4. **Patch Node security issues.**
   - Update vulnerable `next`/transitive packages with `npm audit fix` or reviewed manual upgrades.
   - Re-run typecheck/tests/audit.

5. **Remove documentation ambiguity.**
   - Keep `docs/root/MASTER_TASK_LOG.md` as SSOT.
   - Make root shadows and historical plans explicitly non-canonical.

---

## Long-term initiatives

1. **Toolbelt consolidation.**
   - Promote stable tools into one registry.
   - Convert legacy scripts to adapters only when actively used.
   - Archive unreferenced or duplicate tools.

2. **TS product maturity.**
   - Build Family Focus Board UI workflows.
   - Add API integration/e2e coverage.
   - Define deployment topology and observability.

3. **Operational MCP platform.**
   - Separate packaged public MCP servers from local/operator MCP servers.
   - Version catalogs and validate server boot in CI.
   - Add compatibility policy for external MCP clients.

4. **Documentation governance.**
   - Add doc freshness dates and canonical/non-canonical banners.
   - Add docs contract tests for required files and path references.
   - Keep `PROJECT_AUDIT_REPORT.md` updated after large migrations.

---

## Dependencies

| Dependency | Required by | Current risk |
|---|---|---|
| PyPI maintainer token | SWARM-003 publish | Completed per SSOT, but publish remains open. |
| Python dev dependencies | Tests, CI, release confidence | Missing `dotenv` in current dev test path. |
| Import-healer baseline | CI gate | Current coverage numbers are below baseline. |
| Node dependencies | TS typecheck/tests/audit | `npm ci` required; audit has vulnerabilities. |
| PostgreSQL / `DATABASE_URL` | `apps/api` runtime | No `.env.example` or deployment runbook in current docs. |
| MCP catalog accuracy | MCP client setup | 4 missing targets in catalog. |

---

## Risk areas

- **Release risk:** Package is implemented but not externally published or clean-install verified.
- **CI risk:** Declared workflow likely fails or misses important active surfaces.
- **Security risk:** npm advisories remain open; Python audit is skipped without `pip-audit`.
- **Architecture risk:** Multiple product narratives obscure priorities.
- **Maintenance risk:** Large legacy/deprecated tool volume increases false positives and duplicate fixes.
- **Documentation risk:** Stale historical docs still look actionable.

---

## Suggested sequencing

1. Restore Python gate determinism.
2. Complete PyPI publish and clean install proof.
3. Repair MCP catalog and package/server docs.
4. Add Node CI and remediate npm audit issues.
5. Replace placeholder API/web quality gates.
6. Decide product boundary and archive policy.
7. Consolidate tool registries and legacy scripts.
8. Refresh docs after each milestone, with SSOT first and `NEXT_UP.md` second.
