# NEXT UP — AgentTools

**Updated:** 2026-08-11
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Strategic inventory:** `MASTER_TASK_LIST.md`
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`

This file is an immediate-action mirror, not a backlog or historical log. Status and evidence belong in the SSOT first.

## Immediate actions

1. **Verify reusable marketing/API/MCP promotion candidates.** Compare bridge requirements with AgentTools and `socialmediamanager`; classify each candidate and require provenance, auth/risk review, deduplication, a narrow verification, and a promotion manifest.
2. **Confirm CPC/cliprun helpers still match current phone/desktop lanes.** Identify current owners and consumers before changing helpers; intent and runtime use are `Unknown` until evidenced.
3. **Reconcile uncertain historical claims.** Work through the six `Needs verification` groups in the 2026-08-11 history reconstruction without converting commit subjects into deployment or test success.
4. **Verify integration boundaries.** Compare AgentTools with current Dream.OS core and projectscanner contracts while preserving AgentTools as the reusable capability layer.
5. **Decide branch policy.** Document whether branch `work` should receive a remote/upstream and how docs-only changes should be reviewed.

## Guardrails

- Do not bulk-import API or MCP catalogs.
- Do not store credentials in source, planning artifacts, reports, or prompts.
- Do not infer production operation from a merge, test file, runbook, tag, or deployment-labeled subject.
- Keep SWARM MCP, AgentTools/operator tooling, and Family Focus Board as separate repository lanes.

## Agent passdown — 2026-08-11 UTC

- **Branch/PR:** `work`; PR metadata creation required by the repository automation layer, with no push performed.
- **Completed:** `DOCS-PLAN-001` — populated the execution-history SSOT from the approved 13-section proposal; `DOCS-PLAN-002` — reorganized the strategic inventory by seven requested domains; `DOCS-PLAN-003` — reduced this mirror to five immediate actions.
- **Evidence:** `git diff --check` (pass); legacy filename/casing reference scan (no stale references); `test -f MASTER_TASK_LIST.md && test -f MASTER_TASK_LOG.md && test -f NEXT_UP.md` (pass); docs-only changed-path audit (pass).
- **Blockers:** Six historical groups remain `Needs verification`; CPC/cliprun ownership and current runtime use are `Unknown`; branch `work` has no configured upstream.
- **Next agent ask:** `Verify the marketing/API/MCP promotion candidates and CPC/cliprun ownership using current contracts, then record evidence in docs/root/MASTER_TASK_LOG.md before updating NEXT_UP.md.`
