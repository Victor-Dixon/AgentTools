# PR #27 — Discord Architect Connector salvage

## Source

- Open source PR: #27
- Source branch: `feat/discord-architect-connector-v0`
- Source head inspected: `56a0dd6b1235d80d3002c09d8b70013cfc5c1b4c`
- Compare vs `master` at salvage start: 53 commits ahead, 0 behind, 8 files in the GitHub file diff

## Why the proposed change was not mergeable as-is

PR #27's file diff had already been narrowed to connector paths, but the branch still carried 53 unrelated historical commits (S2A, MCP conversion, VPS deploy, Commander, THEA-A2A). That history is not the connector change.

Exact-head advisory CI also failed collection on Python 3.10:

- `ImportError: cannot import name 'UTC' from 'datetime'`
- the same import error while loading `dreamos_control_plane_server`

Required `build-and-test` passed because it did not collect the new connector tests.

Owner review also required that client-supplied `human_approved=true` must not count as trusted authorization, and that the live-send env gate stay off.

## Reconciliation result

`UNIQUE_WORK_PROVEN=true` for the Discord Architect Connector module, the Dream.OS control-plane MCP facade that exposes it, the runbook, and the connector/control-plane tests.

Replacement branch `cursor/pr27-discord-architect-connector-cfa1` reconstructs that unique work on current `master` without merging stale history.

## Collision / secret scan

- No existing `src/agent_tools/discord_architect_connector/` on `master` (add).
- No existing `mcp_servers/dreamos_control_plane_server.py` on `master` (add).
- Existing BusMessage tripwire would have treated the new `dreamos*` filenames as an adapter; the tripwire now ignores `tests/` and `mcp_servers/` facades instead of shipping a competing schema snapshot.
- Connector responses redact/omit tokens; unit tests assert token strings do not leak.

## Terminal disposition

Replacement PR #29 merged to `master` at `2026-09-20T15:50:56Z` as `f53c706f`. Source PR #27 is closed. Remote `feat/discord-architect-connector-v0` is deleted. No VPS deploy, Discord live send, or bot-permission expansion is authorized by this salvage.
