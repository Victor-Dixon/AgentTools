# AGENTS.md — Repository Operating Rules

<!-- DREAMOS_SHARED_CONTEXT_START -->
## Dream.OS shared context

For Dream.OS-managed work in this repository:
- Read the [canonical check-in instructions](https://github.com/Victor-Dixon/DreamVault/blob/master/runtime/docs/swarm_checkin_001.md) and the [shared swarm desk](https://github.com/Victor-Dixon/DreamVault/issues/228) before source edits.
- Post/update your own unique-session check-in with this repo, existing branch, full HEAD, exact write scope, evidence and next action. Resolve overlapping scopes before writing; update the same check-in at handoff/closeout and return its URL.
- [DreamVault](https://github.com/Victor-Dixon/DreamVault) holds shared governance/context; this repo's local instructions, PRD and task surfaces still govern project work. Read shared context through already-authorized access; do not copy the brain into this repo.
- Shared context grants no new repository, deployment, deletion, trading or client authority. Do not publish credentials, private client source, personal data or raw sensitive logs to the desk.
- If required brain access fails, report COORDINATION_BLOCKED with the actual error; continue safe read-only investigation for that managed lane. Do not fabricate a check-in or another session's acknowledgment.
- Standalone product use remains independent of Dream.OS/cloud access. This pointer applies when work is explicitly coordinated through Dream.OS; it does not enroll a service or activate an agent.

<!-- DREAMOS_SHARED_CONTEXT_END -->

## What this project even is

This repository maintains **SWARM MCP** (`swarm-mcp`), a Python package for multi-agent coordination workflows over MCP, and also contains secondary AgentTools/operator tooling plus a separate Family Focus Board TypeScript product lane.

Primary code surfaces:
- `swarm_mcp/core/` → coordination logic
- `swarm_mcp/servers/` → MCP server implementations
- `swarm_mcp/cli.py` → operational CLI
- `tests/` and `integration/` → verification

Secondary workspace surfaces:
- `mcp_servers/`, `tools/`, `tools_v2/` → local/operator MCP and automation tooling
- `apps/api/`, `apps/web/`, `packages/shared/` → Family Focus Board product lane
- `docs/architecture/DOMAIN_MODEL.md` → canonical domain model and documentation audit

## SSOT enforcement policy

- `docs/root/MASTER_TASK_LOG.md` is the single source of truth for project status.
- `NEXT_UP.md` mirrors SSOT for human-friendly execution focus.
- `docs/architecture/DOMAIN_MODEL.md` is the canonical repository domain model.
- Any task/status update must be reflected in `docs/root/MASTER_TASK_LOG.md` first, then `NEXT_UP.md`.
- If documents conflict, treat `docs/root/MASTER_TASK_LOG.md` as canonical and reconcile immediately.

## Agent passdown requirement (mandatory each session)

Every agent session that changes status, executes a critical-path task, or stops mid-task **must** end by updating `NEXT_UP.md` with a dated **Agent passdown** block.

Passdown must include:
1. **Date (UTC)** and **branch/PR** worked.
2. **Completed** — task IDs + one-line outcome each.
3. **Evidence** — exact commands run and summarized output.
4. **Blockers** — what stopped further progress and why.
5. **Next agent ask** — single copy/paste prompt for the next session.

Rules:
- Write verified SSOT evidence in `docs/root/MASTER_TASK_LOG.md`, then mirror the passdown in `NEXT_UP.md`.
- Remove or update stale/contradictory blocker lists in `NEXT_UP.md` when status changes.
- Do not leave a session with only code changes and no passdown.

## Documentation update guardrails

When editing project status docs:
1. Remove obsolete or contradictory claims.
2. Include concrete dates (`YYYY-MM-DD`).
3. Prefer evidence-backed inventory snapshots (commands and outputs).
4. Keep next actions constrained to the active critical path.
5. Mark unverifiable architecture, runtime topology, external integration status, or product intent as `Unknown` instead of inferring it.
6. Preserve the lane boundary: SWARM MCP tasks, AgentTools/operator tooling, and Family Focus Board cards/timers are related by repository location, not by a single shared domain model.

## Standard Repository Working Contract

1. Read `AGENTS.md`, `NEXT_UP.md`, `MASTER_TASK_LIST.md`, `MASTER_TASK_LOG.md`, any repo SSOT/state manifest, branch/HEAD, and relevant tests before editing.
2. Work one bounded lane with explicit **TARGET, ACTION, VERIFY, COMMIT**. Do not mix unrelated cleanup, features, migrations, or speculative rewrites.
3. Use Fast TDD: smallest acceptance test, smallest safe change, targeted verification, then broad verification.
4. When repo state changes, update `NEXT_UP.md` and `MASTER_TASK_LIST.md` in the same lane, plus the execution-state SSOT when present.
5. Append the repository's canonical master task log only after verification proves closure. Never record planned or merely implemented work as completed.
6. For non-trivial work, create/update `runtime/tasks/*.yaml` with objective, scope, acceptance, verification, holds, and next lane when supported.
7. Trust but verify: targeted tests, repo validators, `git diff --check`, and final status/diff review. PASS/COMPLETE/deployed/merged claims require evidence.
8. Salvage before destructive cleanup. Classify variants/donor material before delete/reset/rewrite; preserve canonical source unless evidence proves it stale.
9. End code or repo-structure work with a clean scoped commit. Planning-only work still requires synchronized task surfaces and verification.
10. Leave the next executable step in `NEXT_UP.md` with its verification gate so the next agent does not rediscover the lane.

### Canonical Planning Names

Fleet-standard root planning names are `NEXT_UP.md`, `MASTER_TASK_LIST.md`, and `MASTER_TASK_LOG.md`. Existing explicit repo SSOTs such as `docs/root/MASTER_TASK_LOG.md` remain authoritative until deliberately migrated; root compatibility files must not become competing authorities.
