# NEXT UP - AgentTools

**Last reconciled:** 2026-08-24  
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`  
**Strategic inventory:** `MASTER_TASK_LIST.md`  
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`

This file is the fleet-standard immediate execution queue (one primary lane). Status and evidence belong in the SSOT first.

## Highest-priority executable lane

### Verify reusable marketing/API/MCP promotion candidates

| Question | Answer |
|---|---|
| **Lane** | Classify marketing/API/MCP promotion candidates against AgentTools + `socialmediamanager` ownership: provenance, auth/risk, dedupe, narrow verification, promotion manifest. |
| **Why** | Immediate-action #1 from the 2026-08-11 planning pass; reusable capability must not bulk-import catalogs or claim social execution owned by `socialmediamanager`. |
| **Authority** | `MASTER_TASK_LIST.md` (Marketing capability audit); `docs/root/MASTER_TASK_LOG.md`; `docs/architecture/DOMAIN_MODEL.md`; `AGENTS.md`; draft PR #13 classification report. |
| **State** | Active via draft PR #13 (`audit/marketing-mcp-promotion-candidates-20260815`) which adds `_reports/promotion/marketing_api_mcp_candidate_classification_20260815.md`. Root NEXT_UP was a soft five-item list before this harden. |
| **Blockers** | Draft PR #13 is not merged; CPC/cliprun ownership remains `Unknown`; six historical groups remain `Needs verification` (do not convert commit subjects into success). |
| **Done evidence** | Classification table with EXISTING/DUPLICATE/PROMOTION_CANDIDATE/BLOCKED/REJECTED/UNKNOWN; evidence appended to `docs/root/MASTER_TASK_LOG.md`; PR #13 reviewed/merged or superseded with recorded decision; this NEXT_UP reconciled. |
| **Do-not-concurrent** | Do not open a parallel marketing-MCP classification rewrite while PR #13 owns the report artifact; do not bulk-import MCP/API catalogs; do not store credentials; do not claim production operation from merge/test/runbook subjects; keep SWARM MCP, AgentTools tooling, and Family Focus Board as separate lanes. |

## Queued (not concurrent)

2. Confirm CPC/cliprun helpers vs current phone/desktop lanes (owners/consumers `Unknown` until evidenced).  
3. Reconcile six `Needs verification` historical groups without inventing success claims.  
4. Verify integration boundaries vs Dream.OS core / projectscanner (AgentTools stays reusable capability layer).  
5. Decide branch policy for historical `work` / docs-only review (document only).

## Guardrails

- Do not bulk-import API or MCP catalogs.
- Do not store credentials in source, planning artifacts, reports, or prompts.
- Do not infer production operation from a merge, test file, runbook, tag, or deployment-labeled subject.
- Keep SWARM MCP, AgentTools/operator tooling, and Family Focus Board as separate repository lanes.

## Related open drafts (non-planner-file)

- PR #13 — marketing MCP promotion candidate classification (owns this lane's report)  
- PR #12 — SWARM MCP commercialization readiness gate (revenue docs only; not this lane)
