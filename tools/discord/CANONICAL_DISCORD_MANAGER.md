# Canonical Discord Manager

Canonical owner: `AgentTools/tools/discord/`

## Policy

AgentTools owns Discord integration code:
- webhook sending
- webhook creation / registration
- Discord bot adapters
- dashboard posting
- operator interaction surfaces

DreamVault consumes Discord services through scripts, environment variables, or AgentTools adapters.

## Non-Goals

DreamVault should not become the long-term owner of Discord integration logic.
DreamVault may keep lightweight reporting wrappers, but reusable Discord capability belongs here.

## Legacy Sources To Review

- `DreamVault/dreamvault/discord_webhook_sender.py`
- `DreamVault/dreamvault/discord_delivery_retry_queue.py`
- `DreamVault/dreamvault/discord_action_controls.py`
- `AgentTools/mcp_servers/discord_integration_server.py`
- `AgentTools/tools/discord/unified_discord.py`
- `AgentTools/tools_v2/categories/discord_webhook_tools.py`
- `Thea/src/dreamscape/core/discord/*`
- archived `discord_ops_manager` artifacts in DreamVault intelligence snapshots

## Promotion Rule

Do not delete legacy implementations until:
1. canonical adapter has tests,
2. call sites are migrated,
3. Discord smoke test passes,
4. migration report is written.
