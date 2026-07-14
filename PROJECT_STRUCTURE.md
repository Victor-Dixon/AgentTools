# Project Structure

**Last updated:** 2026-07-14

AgentTools is the Dream.OS canonical operator/control-plane toolbelt repository.

## Canonical Source Directories

| Path | Purpose | Status |
|---|---|---|
| `swarm_mcp/core/` | Package coordination primitives: messaging, memory, consensus, conflict detection, task scoring, verification, work proof, recovery, patterns | VERIFIED |
| `swarm_mcp/servers/` | Package MCP server entrypoints (`control`, `memory`, `messaging`, `tasks`, `tools`) | VERIFIED |
| `swarm_mcp/cli.py` | Package CLI with 12 subcommands | VERIFIED |
| `mcp_servers/` | Broader legacy/expanded MCP server inventory; 29 Python server files observed excluding `__init__.py` | PARTIAL |
| `tools/` | Operator utilities, Discord helpers, repo intelligence helpers, and automation entrypoints | VERIFIED |
| `tools_v2/` | Adapter/registry migration surface for safer toolbelt execution | PARTIAL |
| `apps/api/`, `apps/web/`, `packages/shared/` | Product/control-plane application surfaces | PARTIAL |

## Runtime Entrypoints

| Path | Purpose |
|---|---|
| `tools/toolbelt_cli.py` | Canonical local toolbelt operation entrypoint |
| `swarm_mcp/cli.py` | Package CLI |
| `start_swarm.py` | Local coordination startup script |
| `mcp_servers/*_server.py` | Legacy/expanded MCP server scripts |

## Tests

Configured in `pytest.ini`:

- `tests/`
- `tools/consolidation/tests/`
- `tools/swarm/tests/`
- `tools_v2/tests/`

## Configuration

| Path | Purpose |
|---|---|
| `pyproject.toml` | Python package/build metadata |
| `package.json`, `package-lock.json`, `tsconfig.base.json` | Node/TypeScript support surfaces |
| `config/` | Local configuration data |
| `.github/workflows/` | CI workflows |

## Documentation and Planning

| Path | Purpose |
|---|---|
| `docs/root/MASTER_TASK_LOG.md` | Status/task SSOT |
| `NEXT_UP.md` | Human-readable active focus mirror |
| `PRD.md` | Product requirements and boundaries |
| `PROJECT_STRUCTURE.md` | Repository structure map |
| `docs/architecture/` | Architecture/domain discovery and ADRs |
| `MASTER_TASK_LIST.md` | Historical task ledger plus current projection notes |

## Task Artifacts and Reports

| Path | Purpose |
|---|---|
| `runtime/tasks/` | Runtime task YAML artifacts |
| `runtime/reports/` | Operational reports and closeouts |
| `reports/` | Durable report artifacts |
| `data/` | Local operational data |

## Deprecated or Needs Classification

- `mcp_servers/` contains useful expanded servers but needs keep/merge/archive/delete classification against `swarm_mcp/servers/`.
- `tools_archive/`, `tools_backup/`, and `quarantine/` are not active canonical tool surfaces without an explicit promotion manifest.
- Historical launch claims in older root docs must be reconciled against `docs/root/MASTER_TASK_LOG.md` before reuse.
