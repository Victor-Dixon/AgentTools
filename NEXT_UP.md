# NEXT UP — AgentTools

**Updated:** 2026-09-20
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`
**Strategic inventory:** `MASTER_TASK_LIST.md`
**Canonical domain model:** `docs/architecture/DOMAIN_MODEL.md`

This file is an immediate-action mirror, not a backlog or historical log. Status and evidence belong in the SSOT first.

## Immediate actions

1. **Keep the Discord Architect Connector live-send gate off.** No VPS deploy, Discord live send, or bot-permission expansion. HTTP/OAuth reachability remains `Unknown` until independently evidenced.
2. **Verify reusable marketing/API/MCP promotion candidates.** Compare bridge requirements with AgentTools and `socialmediamanager`; classify each candidate and require provenance, auth/risk review, deduplication, a narrow verification, and a promotion manifest.
3. **Confirm CPC/cliprun helpers still match current phone/desktop lanes.** Identify current owners and consumers before changing helpers; intent and runtime use are `Unknown` until evidenced.
4. **Reconcile uncertain historical claims.** Work through the six `Needs verification` groups in the 2026-08-11 history reconstruction without converting commit subjects into deployment or test success.
5. **Decide branch policy.** Document whether local branch `work` should receive a remote/upstream and how docs-only changes should be reviewed.

## Guardrails

- Do not bulk-import API or MCP catalogs.
- Do not store credentials in source, planning artifacts, reports, or prompts.
- Do not infer production operation from a merge, test file, runbook, tag, or deployment-labeled subject.
- Keep SWARM MCP, AgentTools/operator tooling, and Family Focus Board as separate repository lanes.
- Client-supplied `human_approved=true` is not trusted authorization for Discord live send.

## Agent passdown — 2026-09-20 UTC

- **Branch/PR:** replacement PR #29 merged to `master` as `f53c706f`; superseded PR #27 closed; `feat/discord-architect-connector-v0` deleted.
- **Completed:** Reconstruct PR #27 Discord Architect Connector on current master; repair Python 3.10 collection and untrusted client `human_approved`; required `build-and-test` passed on exact head `33776e8b`; merge #29; retire source PR/branch.
- **Evidence:** local `python -m pytest` required set `82 passed, 2 skipped`; GitHub Actions `35520691882` `build-and-test` PASS (`82 passed, 2 skipped`); advisory FAIL on pre-existing legacy tests, not connector collection; `gh pr view 29` state=MERGED; `git push origin --delete feat/discord-architect-connector-v0` succeeded.
- **Blockers:** Live Discord send / HTTP-OAuth / VPS remain unauthorized or `Unknown`. Advisory full suite still fails historically. Open PR #28 (`feat/devlog-poster-mobile-20260919`) is unrelated and was not retired.
- **Next agent ask:** `Do not enable DISCORD_CONNECTOR_ALLOW_LIVE_SEND. Continue the marketing/API/MCP promotion-candidate audit using current contracts, then record evidence in docs/root/MASTER_TASK_LOG.md before updating NEXT_UP.md.`
