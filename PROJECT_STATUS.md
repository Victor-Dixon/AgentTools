# PROJECT_STATUS: AgentTools

**Last reconciled:** 2026-08-24  
**Classification:** STANDARDIZATION_REQUIRED → STANDARDIZATION_IN_PROGRESS (NEXT_UP 7-question harden)  
**Default branch:** master  
**Open drafts at lane start:** PR #12 (revenue docs), PR #13 (marketing classification report) — neither touches planner trio

## Fleet contract checklist

| File | Status | Notes |
|---|---|---|
| AGENTS.md | Present | Root |
| PRD.md | Present | Not rewritten this lane |
| ROADMAP.md | Present | Not rewritten this lane |
| MASTER_TASK_LIST.md | Present | Strategic inventory; append STD note only |
| MASTER_TASK_LOG.md | Root pointer | Canonical SSOT: `docs/root/MASTER_TASK_LOG.md` |
| NEXT_UP.md | Hardened (this lane) | Single-lane 7-question contract |
| PROJECT_STATUS.md | Present (this lane) | This file |

## Active lane

Marketing/API/MCP promotion candidate verification — owned by draft PR #13 report artifact. See `NEXT_UP.md`.

## Branch hygiene classification (no deletes)

| Branch | Classification | Evidence |
|---|---|---|
| `master` | CANONICAL | Default branch |
| `main` | DIVERGED_REVIEW | ahead=24 behind=19 vs master |
| `audit/marketing-mcp-promotion-candidates-20260815` | ACTIVE_DRAFT_PR | PR #13; ahead=1 |
| `docs/swarm-mcp-commercialization-readiness-20260815` | ACTIVE_DRAFT_PR | PR #12; ahead=1 |
| `docs/fleet-planning-contract-v1` | STALE_BEHIND | ahead=0 behind=2 |
| `codex/populate-master_task_log.md-from-git-history` | STALE_BEHIND | ahead=0 behind=4 |
| `deploy/vps-swarm-commander` | DIVERGED_REVIEW | ahead=15 behind=52 |

Do not delete or force-push branches in this lane. Record only.

## Local workspace note

`D:\agent-tools` was dirty (ahead/behind on `main`) and was **not** used for mutation. Clean worktree from `origin/master` used instead.
