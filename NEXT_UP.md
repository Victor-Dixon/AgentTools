# NEXT UP — AgentTools

**Updated:** 2026-08-11
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`

## Current priorities

### 1. Finish the existing release blocker

- `SWARM-003` — publish the intended `swarm-mcp` release with redacted CI evidence.
- `SWARM-004` — verify clean installation, import, and CLI behavior after publication.

### 2. Run the marketing capability audit

DreamVault has selected `inspect_social_media_manager_bridge_001` as the current marketing activation lane. AgentTools should support that lane as the reusable capability layer, not create a parallel social-media product.

Inspect the capabilities required by the verified bridge report and compare them against:

- current AgentTools integrations,
- capabilities already owned by `Victor-Dixon/socialmediamanager`,
- relevant API/MCP catalog candidates.

Classify every candidate as:

`EXISTING | DUPLICATE | PROMOTION_CANDIDATE | BLOCKED | REJECTED | UNKNOWN`

## Promotion gate

Before adding any API/MCP integration:

1. establish provenance and maintained source,
2. identify authentication and credential handling,
3. check platform terms/risk,
4. deduplicate against existing capabilities,
5. verify the narrow operation,
6. produce a promotion manifest,
7. add tests/evidence,
8. expose only the verified capability.

No bulk catalog ingestion.

## Acceptance target

AgentTools is ready for the marketing lane when the Social Media Manager bridge can name its required reusable capabilities and each one resolves to either an existing verified tool or a bounded promotion candidate.

## Guardrail

DreamVault owns governed task/context/approval state. `socialmediamanager` owns social execution workflows already implemented there. AgentTools owns reusable tool/integration capability only.

`NEXT_LANE=finish_release_blocker_then_marketing_capability_audit`
