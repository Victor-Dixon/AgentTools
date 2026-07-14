# PRD - AgentTools

**Last updated:** 2026-07-14
**Status:** Active control-plane/toolbelt repository
**Primary SSOT:** `docs/root/MASTER_TASK_LOG.md`

## Purpose

AgentTools is the Dream.OS operator control-plane and toolbelt layer. It provides MCP server infrastructure, operator utilities, automation surfaces, integration bridges, repository orchestration helpers, verification tools, and governance-support utilities around Dream.OS.

AgentTools is not the Dream.OS runtime swarm engine and is not the canonical governance/reporting vault.

## Users

- Operators who need local toolbelt commands and operational automation.
- Agents that call MCP servers or tool adapters for coordination, verification, messaging, and control-plane work.
- Maintainers who classify active vs legacy tooling and prepare reusable utilities for promotion.

## Workflows

- Run the toolbelt through `D:\agent-tools\tools\toolbelt_cli.py`.
- Use `swarm_mcp/cli.py` for package-level coordination commands.
- Expose MCP server behavior through `swarm_mcp/servers/` and legacy/expanded servers in `mcp_servers/`.
- Use `tools_v2/` adapters for the migration path toward safer, registry-backed tool execution.
- Use `tests/`, `tools/consolidation/tests/`, `tools/swarm/tests/`, and `tools_v2/tests/` as the configured pytest surfaces.

## Requirements

- Keep `docs/root/MASTER_TASK_LOG.md` as the execution-status SSOT.
- Mirror only the highest-leverage active tasks in `NEXT_UP.md`.
- Preserve the boundary: AgentTools owns operator/control-plane tooling; DreamOS owns runtime/swarm execution; DreamVault owns governance inventory, reports, and promotion manifests.
- Do not promote legacy MCP/tool surfaces without active-vs-legacy classification and verification evidence.
- Do not treat root historical task lists as newer than the dated SSOT log.

## Current Capabilities

- `swarm_mcp/core/` contains coordination primitives for messaging, memory, consensus, conflict detection, task scoring, verification, work proof, recovery, and pattern mining.
- `swarm_mcp/servers/` contains 5 package MCP server entrypoints: `control.py`, `memory.py`, `messaging.py`, `tasks.py`, and `tools.py`.
- `swarm_mcp/cli.py` defines 12 CLI subcommands: `status`, `send`, `inbox`, `search`, `learn`, `tasks`, `assign`, `vote`, `conflict`, `profile`, `prove`, and `patterns`.
- `mcp_servers/` contains a broader legacy/expanded MCP server inventory that still requires classification before promotion.
- `tools/` and `tools_v2/` contain operational toolbelt utilities and adapter migration surfaces.
- `apps/api/`, `apps/web/`, and `packages/shared/` exist as product/control-plane surfaces.

## Partial Capabilities

- PyPI release remains incomplete until SWARM-003 and SWARM-004 have command-output evidence in the SSOT.
- Active vs legacy MCP server ownership is not fully classified.
- `tools_v2` migration is in progress and should remain test-first.
- Some gates depend on sibling canonical repositories or local environment setup.
- The repository currently has an existing dirty worktree unrelated to this documentation sync.

## Deferred Scope

- Runtime/swarm execution ownership that belongs in DreamOS.
- Governance reports, promotion manifests, and portfolio intelligence ownership that belongs in DreamVault.
- Destructive cleanup or removal of legacy tools without a classification manifest and verification.
- Publishing or release completion claims without PyPI/build/install evidence.

## Success Criteria

- `docs/root/MASTER_TASK_LOG.md` has dated, evidence-backed current status.
- `NEXT_UP.md` contains 3-7 active, concrete tasks mirrored from the SSOT.
- Active MCP/tool surfaces are classified with implementation paths and tests.
- `pytest -q` or the focused configured gates pass in the local environment.
- Documentation distinguishes package MCP surfaces from legacy/expanded MCP servers.

## Unresolved Decisions

- Which `mcp_servers/` files are keep, merge, archive, or delete.
- Which `tools_v2/` adapters become the canonical execution path for each tool category.
- Whether the package release path remains `swarm-mcp` only or includes broader AgentTools control-plane distribution.
- How to handle dirty-worktree operational reports during documentation-only repair passes.
