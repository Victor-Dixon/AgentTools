# Discord Commander Runbook

Canonical home: `D:\agent-tools` (toolbelt). PyAutoGUI lane transport remains in `D:\Agent_Cellphone_V2_Repository`.

## Required environment variables

Document only — never commit values.

| Variable | Purpose |
|----------|---------|
| `DISCORD_BOT_TOKEN` | Bot token for inbound commands |
| `DISCORD_GUILD_ID` | Target guild |
| `DISCORD_WEBHOOK_URL` | Default outbound webhook |
| `DISCORD_WEBHOOK_AGENT_1` … `DISCORD_WEBHOOK_AGENT_8` | Per-agent outbound webhooks |

## CLI

```powershell
cd D:\agent-tools
$env:PYTHONPATH = "src"
python -m agent_tools.discord_commander --help
```

### Commands

| Command | Description |
|---------|-------------|
| `inbound-dry-run` | Validate bot token (no posts) |
| `outbound-dry-run` | Validate webhook config (no secrets printed) |
| `post` | Post embed to agent webhook (`--dry-run`, `--message-file`) |
| `start-bot` | Start unified Discord bot |
| `start-queue` | Start queue processor (PyAutoGUI adapter) |
| `status` | Show masked configuration status |

## Health checks

```powershell
python scripts/health/discord_dry_run.py
python scripts/health/discord_outbound_dry_run.py
```

## Examples

```powershell
python -m agent_tools.discord_commander outbound-dry-run
python -m agent_tools.discord_commander post --agent Agent-1 --title "Update" --message "Hello" --dry-run
python -m agent_tools.discord_commander status
```

## Architecture

- **agent-tools**: CLI, outbound router, health checks, slim bot
- **Agent_Cellphone_V2_Repository**: PyAutoGUI transport, lane injection (adapter boundary via `queue_bridge.py`)

## Salvage manifest

See `data/salvage_manifests/discord_commander_salvage_manifest.md`.
