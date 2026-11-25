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


## Agent passdown — 2026-11-19 UTC

- Branch/PR: docs/control-plane-recovery-deferred-20261119, requested deferred draft.
- Completed: bounded recovery plan and task proposal; implementation NOT STARTED.
- Evidence: connected Control Plane call returned USER_NOT_LOGGED_IN; source entrypoint inspected. Working GitHub Architect queue/VPS path has deletion receipts.
- Blockers: actual deployed transport/auth/service failure remains unverified; recovery deliberately deferred.
- Next agent ask: Resume branch-debt cleanup through existing Architect/VPS path. Take AT-CONTROL-PLANE-RECOVERY-001 later; follow docs/operator/control_plane_recovery_20261119.md without expanding permissions.

## Agent passdown — 2026-11-25 UTC (Agent 1)

- Branch/PR: #38 and #41 merged; exact evidence in SSOT section “2026-11-25 — Agent 1 fleet capability recovery (V2)”.
- Completed: duplicate prevention and runner persistence source integration; 21 and 9 focused tests passed, no new advisory failures. Authenticated existing runner inventory executed with exit 0.
- Evidence: [CI #45710972438](https://github.com/Victor-Dixon/AgentTools/actions/runs/45710972438), [CI #45711742206](https://github.com/Victor-Dixon/AgentTools/actions/runs/45711742206), receipt `e0020116-93a2-4736-9a6e-d64cf4c6bf39`.
- Blockers: live repaired-collector acceptance needs authorized narrow operation; branch retirement needs preservation verification. No protected claim held.
- Next agent ask: consume [existing promotion handoff](https://github.com/Victor-Dixon/DreamVault/issues/228#issuecomment-7175853230); verify runtime without expanding authority; use existing Architect retirement gates. Preserve other active work and dispatcher authority.


## Agent passdown — 2026-11-25 UTC (Agent 4)

- #34/#37 merged; #42 source verified 3/3 at `67dec58e`, CI `45712309029`. See execution SSOT for evidence.
- Next: #42 merged; #49 compatibility implemented, required CI passed at e41c8895 (run 45715626639), advisory failed. Confirm targeted regression and integrate #49. Gateway activation independent; preserve existing holds and Agent1 passdown.


## Agent passdown — 2026-11-25 UTC (Agent 2)

- Local testing/quality recovery integrated through #55; exact evidence in execution SSOT section “2026-11-25 — Agent 2 testing and quality capability recovery”.
- Next: gateway owner consumes existing handoff at https://github.com/Victor-Dixon/DreamVault/issues/228#issuecomment-7177053801; preserve disabled mutation discovery until authorized workspace binding is verified. Actual JS analyzer backend acceptance remains open. No protected lease held.
