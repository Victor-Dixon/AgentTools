# Discord Commander Salvage Manifest

**Promotion date:** 2026-06-10  
**Source:** `D:\Agent_Cellphone_V2_Repository`  
**Destination:** `D:\agent-tools`  
**Classification:** `discord_commander` → `canonical_toolbelt_home`

## Rationale

Discord Commander is a reusable Discord ↔ agent ops bridge, not core Agent Cellphone UI automation. PyAutoGUI transport stays in Agent Cellphone as an adapter boundary.

## Promoted files

| Destination | Source / lineage |
|-------------|------------------|
| `src/agent_tools/__init__.py` | New (toolbelt package root) |
| `src/agent_tools/discord_commander/__init__.py` | New |
| `src/agent_tools/discord_commander/__main__.py` | New (CLI entry) |
| `src/agent_tools/discord_commander/cli.py` | New (toolbelt CLI) |
| `src/agent_tools/discord_commander/config.py` | New (env schema) |
| `src/agent_tools/discord_commander/models.py` | Adapted from `src/discord_commander/discord_models.py` |
| `src/agent_tools/discord_commander/discord_service.py` | Adapted from `src/discord_commander/discord_service.py` |
| `src/agent_tools/discord_commander/outbound_router.py` | Built (salvage: `post_to_discord_router` not found in portfolio) |
| `src/agent_tools/discord_commander/inbound_dry_run.py` | Adapted from `scripts/health/discord_dry_run.py` |
| `src/agent_tools/discord_commander/outbound_dry_run.py` | Built (not present in source) |
| `src/agent_tools/discord_commander/status.py` | New |
| `src/agent_tools/discord_commander/queue_bridge.py` | New (PyAutoGUI adapter boundary) |
| `src/agent_tools/discord_commander/bot_runner_service.py` | Adapted from `src/discord_commander/bot_runner_service.py` |
| `src/agent_tools/discord_commander/unified_discord_bot.py` | Slim promotion from `src/discord_commander/unified_discord_bot.py` |
| `tools/discord_commander/post_to_discord_router.py` | Built (portfolio salvage missing) |
| `tools/discord_commander/run_unified_discord_bot_with_restart.py` | Adapted from `tools/run_unified_discord_bot_with_restart.py` |
| `tools/discord_commander/start_message_queue_processor.py` | Adapted from `tools/start_message_queue_processor.py` |
| `tools/discord_commander/start_discord_system.py` | Adapted from `tools/start_discord_system.py` |
| `scripts/health/discord_dry_run.py` | Adapted from `scripts/health/discord_dry_run.py` |
| `scripts/health/discord_outbound_dry_run.py` | Built |
| `docs/runbooks/discord_commander.md` | New runbook |
| `tests/test_discord_commander_toolbelt.py` | New tests |
| `data/salvage_manifests/discord_commander_salvage_manifest.md` | This file |

## Not promoted

- `.env`, cookies, tokens
- Full `src/discord_commander/` GUI surface (116 modules)
- `src/core/legacy_message_queue_processor.py` (remains in Agent Cellphone; referenced via adapter)
- Unrelated Dreamscape GUI code

## Verification

```powershell
cd D:\agent-tools
python -m pytest tests\test_discord_commander_toolbelt.py -q
python -m agent_tools.discord_commander --help
python -m agent_tools.discord_commander outbound-dry-run
python -m agent_tools.discord_commander post --agent Agent-1 --title "Dry Run" --message "DISCORD_COMMANDER_TOOLBELT=PASS" --dry-run
```
