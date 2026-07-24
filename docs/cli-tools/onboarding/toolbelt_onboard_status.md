# Toolbelt `--onboard-status`

Show onboarding / rehydration readiness for an agent without mutating workspace state.

## Canonical command

```bash
python -m tools.toolbelt --onboard-status --agent Agent-2
```

Equivalent legacy dispatcher:

```bash
python -m tools.toolbelt.cli.onboarding_cli onboard:status --agent Agent-2
```

## What it prints

- Expected `agent_workspaces/<agent>/status.json` path
- Expected `agent_workspaces/<agent>/inbox/` path
- A `jq` inspection hint
- The canonical toolbelt flag form for copy/paste

Exit `0` when `--agent` is valid (`Agent-1` .. `Agent-8`). Invalid agent IDs raise / fail closed.

## Related flags

| Flag | Purpose |
|------|---------|
| `--onboard-status` | Readiness paths only (this doc) |
| `--onboard-soft` | Soft S2A rehydrate (non-destructive) |
| `--onboard-hard` | Destructive reset — requires `--yes` |

## Tests

```bash
cd D:/agent-tools
# If pytest hangs on plugin autoload, set:
#   set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -q -k onboard --override-ini="addopts=" --override-ini="testpaths=tests"
```

Focused module: `tests/test_toolbelt_onboard_status_001.py`

## Implementation

- Registry: `tools/toolbelt_registry.py` → `onboard-status`
- CLI: `tools/toolbelt/cli/onboarding_cli.py` → `cmd_status`
- Executor: `tools/toolbelt/executors/onboarding_executor.py` → `_onboarding_status` / `format_onboarding_status_lines`
