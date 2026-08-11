# MASTER TASK LIST — AgentTools strategic inventory

**Last reconciled:** 2026-08-11
**Purpose:** Backlog and strategic inventory — what work exists
**Execution-status SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Immediate-action mirror:** `NEXT_UP.md`
**Domain-model SSOT:** `docs/architecture/DOMAIN_MODEL.md`

This file inventories work; it does not claim execution status. Record status and evidence in the execution SSOT first, then reflect no more than five immediate actions in `NEXT_UP.md`.

## Toolbelt/runtime helpers

- [ ] Inventory maintained helpers across `tools/`, `tools_v2/`, and operator surfaces; label ownership and supported entry points.
- [ ] Revalidate salvaged and scaffolded helpers before treating them as promoted runtime capabilities.
- [ ] Remove or quarantine generated/runtime artifacts only after provenance and consumer checks.
- [ ] Resolve or explicitly accept remaining npm audit risk before a TypeScript deployment.

## CPC/cliprun/operator workflow

- [ ] Confirm what CPC and cliprun mean in the current phone and desktop lanes; mark intent `Unknown` until an owner/evidence source confirms it.
- [ ] Map current phone/desktop entry points, configuration, credential boundaries, and failure recovery.
- [ ] Verify that helper contracts still match their current consumers before consolidation or promotion.
- [ ] Document a narrow smoke test for each retained operator workflow.

## MCP/API capability registry

- [ ] Inventory registry entries by purpose, provenance, authentication model, maintenance state, risk, and overlap.
- [ ] Validate every promoted MCP target and API wrapper through a narrow operation and recorded evidence.
- [ ] Require a promotion manifest; do not bulk-ingest discovery catalogs.
- [ ] Reconcile task-log mutation paths with the canonical `docs/root/MASTER_TASK_LOG.md` location.

## Marketing capability audit

- [ ] Compare the verified bridge requirements with existing AgentTools capabilities and `Victor-Dixon/socialmediamanager` ownership.
- [ ] Classify each candidate as `EXISTING | DUPLICATE | PROMOTION_CANDIDATE | BLOCKED | REJECTED | UNKNOWN`.
- [ ] Verify provenance, authentication, platform terms/risk, deduplication, and the narrow operation before promotion.
- [ ] Keep social execution in `socialmediamanager`; expose only reusable capability from AgentTools.

## Validation/testing

- [ ] Preserve Python test, import-healer coverage, and MCP catalog gates established for SWARM-014 through SWARM-016.
- [ ] Complete SWARM-003 with redacted publish evidence; do not infer success from a tag or runbook.
- [ ] Complete SWARM-004 with clean install, import, and CLI smoke evidence after publication.
- [ ] Add evidence-backed tests for each promoted helper or integration.

## Repo cleanup/planning

- [ ] Reconcile the six `Needs verification` history groups recorded in the execution SSOT.
- [ ] Decide and document the remote/upstream policy for local branch `work`.
- [ ] Keep this inventory, the execution SSOT, `NEXT_UP.md`, and the domain model aligned without duplicating roles.
- [ ] Review historical planning artifacts and label them non-canonical rather than silently treating them as current.

## Dream.OS integration boundaries

- [ ] Verify AgentTools boundaries against Dream.OS core and projectscanner using current repositories/contracts; otherwise record them as `Unknown`.
- [ ] Preserve ownership: DreamVault/Dream.OS owns governed task, context, and approval state; AgentTools owns reusable tools/integrations.
- [ ] Characterize message/task/work-proof schemas at adapter boundaries and avoid duplicating core orchestration.
- [ ] Record external runtime topology and deployment state as `Unknown` until directly evidenced.
