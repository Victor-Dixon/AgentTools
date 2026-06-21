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

## Documentation update guardrails

When editing project status docs:
1. Remove obsolete or contradictory claims.
2. Include concrete dates (`YYYY-MM-DD`).
3. Prefer evidence-backed inventory snapshots (commands and outputs).
4. Keep next actions constrained to the active critical path.

