# NEXT UP — AgentTools

**Updated:** 2026-09-20
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Strategic inventory:** `MASTER_TASK_LIST.md`
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`

This file is an immediate-action mirror, not a backlog or historical log. Status and evidence belong in the SSOT first.

## Immediate actions

1. **Finish PR #27 retirement after #29 merges.** Close superseded PR #27 and retire `feat/discord-architect-connector-v0` under governed branch cleanup. Do not merge the 53-commit historical stack.
2. **Keep the Discord Architect Connector live-send gate off.** No VPS deploy, Discord live send, or bot-permission expansion. HTTP/OAuth reachability remains `Unknown` until independently evidenced.
3. **Verify reusable marketing/API/MCP promotion candidates.** Compare bridge requirements with AgentTools and `socialmediamanager`; classify each candidate and require provenance, auth/risk review, deduplication, a narrow verification, and a promotion manifest.
4. **Confirm CPC/cliprun helpers still match current phone/desktop lanes.** Identify current owners and consumers before changing helpers; intent and runtime use are `Unknown` until evidenced.
5. **Reconcile uncertain historical claims.** Work through the six `Needs verification` groups in the 2026-08-11 history reconstruction without converting commit subjects into deployment or test success.

## Guardrails

- Do not bulk-import API or MCP catalogs.
- Do not store credentials in source, planning artifacts, reports, or prompts.
- Do not infer production operation from a merge, test file, runbook, tag, or deployment-labeled subject.
- Keep SWARM MCP, AgentTools/operator tooling, and Family Focus Board as separate repository lanes.
- Client-supplied `human_approved=true` is not trusted authorization for Discord live send.

## Agent passdown — 2026-09-20 UTC

- **Branch/PR:** `cursor/pr27-discord-architect-connector-cfa1`; replacement PR #29; source PR #27 left intact for evidence.
- **Completed:** Reconstruct PR #27 Discord Architect Connector on current master; repair Python 3.10 collection and untrusted client `human_approved`; required `build-and-test` passed on exact head `33776e8b`.
- **Evidence:** local `python -m pytest` required set `82 passed, 2 skipped`; GitHub Actions `35520691882` `build-and-test` PASS (`82 passed, 2 skipped`); advisory FAIL on pre-existing legacy tests, not connector collection.
- **Blockers:** Live Discord send / HTTP-OAuth / VPS remain unauthorized or `Unknown`. Advisory full suite still fails historically. Merge of #29 and retirement of `feat/discord-architect-connector-v0` may still be in progress at passdown write time.
- **Next agent ask:** `If PR #29 is merged, close PR #27 and retire feat/discord-architect-connector-v0 with default/protected/open-PR guards. Do not enable DISCORD_CONNECTOR_ALLOW_LIVE_SEND. Then continue the marketing/API/MCP promotion-candidate audit.`
