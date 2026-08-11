# MASTER TASK LIST — AgentTools

**Last reconciled:** 2026-08-11
**Canonical execution status:** `docs/root/MASTER_TASK_LOG.md`
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`
**Active handoff:** `NEXT_UP.md`

## Planning truth

The previous root task list contained January 2026 counts, version claims, agent assignments, and deadlines that no longer matched the repository. This file is now a concise actionable surface; historical detail remains available in Git history and project reports.

## Active

- [ ] Complete `SWARM-003`: publish the currently intended `swarm-mcp` release with redacted evidence.
- [ ] Complete `SWARM-004`: verify clean installation of the published release.
- [ ] Audit existing AgentTools integrations against the marketing capability needs discovered from DreamVault and `socialmediamanager`.
- [ ] Classify relevant API/MCP catalog candidates before promotion: purpose, provenance, auth model, maintenance state, risk, and overlap.
- [ ] Deduplicate candidates against capabilities already present in AgentTools and the Social Media Manager.
- [ ] Promote only narrow, verified, reusable capabilities with tests/evidence.
- [ ] Preserve the boundary: AgentTools provides reusable capabilities; DreamVault owns governed task/context/approval state.

## Marketing capability promotion lane

### Target

Support the evidence-backed marketing loop:

`DreamVault WorkReceipt -> approved content packet -> socialmediamanager execution -> publication evidence -> analytics signal`

### Rules

- External API/MCP lists are discovery inputs, not trusted dependencies.
- No bulk import of integrations.
- No credentials in source, task artifacts, reports, or prompts.
- Prefer existing capabilities over duplicate wrappers.
- Add a promotion manifest before admitting a new integration.
- Verify the narrow capability before exposing it to Dream.OS.

### Definition of done

- [ ] Existing relevant AgentTools capabilities inventoried.
- [ ] Candidate marketing integrations classified and deduplicated.
- [ ] At least one missing capability, if actually required, promoted through a verified manifest/test lane.
- [ ] No duplicate marketing integration added where `socialmediamanager` already owns execution.

## Existing release lane

- [ ] `SWARM-003` — publish with CI evidence.
- [ ] `SWARM-004` — clean install/import/CLI verification.
- [ ] `SWARM-017` — resolve or explicitly accept remaining npm audit risk for its deployment target.

## Governance

- [ ] Keep `docs/architecture/DOMAIN_MODEL.md`, `NEXT_UP.md`, and `docs/root/MASTER_TASK_LOG.md` synchronized when execution priorities change.
- [ ] Mark historical planning docs as non-canonical instead of maintaining competing task truths.
