# Discord Commander Runbook

Canonical home: `D:\agent-tools` (toolbelt). PyAutoGUI delivery delegates to `D:\Agent_Cellphone\src\services\agent_cell_phone.py`.

## Required environment variables

Document only — never commit values.

| Variable | Purpose |
|----------|---------|
| `DISCORD_BOT_TOKEN` | Bot token for inbound commands |
| `DISCORD_GUILD_ID` | Target guild |
| `DISCORD_WEBHOOK_URL` | Default outbound webhook |
| `DISCORD_WEBHOOK_AGENT_1` … `DISCORD_WEBHOOK_AGENT_8` | Per-agent outbound webhooks |
| `AGENT_CELLPHONE_ROOT` | Path to Agent_Cellphone repo (default `D:\Agent_Cellphone`) |
| `AGENT_GAS_LAYOUT_MODE` | Cursor layout (`8-agent`, `4-agent-1monitor`, etc.) |
| `DISCORD_COMMANDER_QUEUE_PATH` | Optional JSON queue file (default `data/message_queue.json`) |
| `DREAMVAULT_ROOT` | DreamVault path for D2A message templates (default `D:\DreamVault`) |
| `DISCORD_COMMANDER_USE_D2A_TEMPLATE` | Wrap `!message` with D2A agent reply policy (default `1`) |
| `DISCORD_COMMANDER_WEBHOOK_FALLBACK` | **Ignored for `!message`** — PyAutoGUI-only (legacy env kept at `0`) |

## Message templates (consolidated)

`!message` wraps operator text via DreamVault SSOT:

- Templates: `D:\DreamVault\runtime\messaging\templates\` (registry.yaml)
- Bridge: `template_bridge.py` → `render_d2a()` with `preferred_reply_format.txt`
- Agents see: Task / Actions Taken / Artifacts / Status reply contract
- Export for WeAreSwarm: `python runtime/scripts/export_messaging_templates_index_001.py`

Closeout cards use **discord_architect** webhooks — not the `!message` path.

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
| `start-queue` | Start JSON queue processor (PyAutoGUI drain loop) |
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

## Architecture (single source of truth)

```
Discord !message / CLI post
        │
        ▼
agent_message_sender.py
        │
        ├─► message_bus_bridge.py ──► DreamVault bus + inline PyAutoGUI
        │
        └─► pyautogui_transport.py ──► Agent_Cellphone/agent_cell_phone.py (Cursor paste)

outbound_router.py ──► Discord webhooks (CLI `post` + closeout only — NOT !message)

start-queue
        │
        ▼
message_queue_processor.py ──► pyautogui_transport.py
```

- **agent-tools**: Discord Commander CLI, bot, webhook router, queue store/processor
- **Agent_Cellphone**: PyAutoGUI coordinate delivery only (`agent_cell_phone.py` + `runtime/agent_comms/cursor_agent_coords.json`)
- **Removed/legacy**: duplicate queue modules under `Agent_Cellphone/src/services/` (consolidated into agent-tools)

## Operating !message to Cursor

1. Ensure Cursor agents are positioned per `cursor_agent_coords.json`
2. Set `AGENT_GAS_LAYOUT_MODE=8-agent` (or your layout)
3. Start bot: `python -m agent_tools.discord_commander start-bot`
4. Optional queue worker: `python -m agent_tools.discord_commander start-queue`
5. In Discord: `!message Agent-1 Check your inbox`

Delivery is **PyAutoGUI-only** for `!message`. Fail-closed if transport or coords are unavailable — no webhook fallback.

## Salvage manifest

See `data/salvage_manifests/discord_commander_salvage_manifest.md`.
