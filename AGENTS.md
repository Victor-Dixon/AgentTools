# AGENTS.md — Repository Operating Rules

## What this project even is

This repository maintains **SWARM MCP** (`swarm-mcp`), a Python package for multi-agent coordination workflows over MCP.

Primary code surfaces:
- `swarm_mcp/core/` → coordination logic
- `swarm_mcp/servers/` → MCP server implementations
- `swarm_mcp/cli.py` → operational CLI
- `tests/` and `integration/` → verification

## SSOT enforcement policy

- `docs/root/MASTER_TASK_LOG.md` is the single source of truth for project status.
- `NEXT_UP.md` mirrors SSOT for human-friendly execution focus.
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
- Write SSOT evidence in `docs/root/MASTER_TASK_LOG.md` first, then mirror the passdown in `NEXT_UP.md`.
- Remove or update stale/contradictory blocker lists in `NEXT_UP.md` when status changes.
- Do not leave a session with only code changes and no passdown.

## Documentation update guardrails

When editing project status docs:
1. Remove obsolete or contradictory claims.
2. Include concrete dates (`YYYY-MM-DD`).
3. Prefer evidence-backed inventory snapshots (commands and outputs).
4. Keep next actions constrained to the active critical path.

