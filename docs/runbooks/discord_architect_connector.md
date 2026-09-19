# Discord Architect Connector — ChatGPT MCP path

**Status:** v0.1 scaffold (read-only + allowlisted smoke dry-run).  
**No live deployment / permission escalation without operator AUTHORIZE.**

## Reuse (do not fork)

| Layer | Path |
|-------|------|
| MCP stdio | `mcp_servers/dreamos_control_plane_server.py` (v0.5.0+) |
| MCP HTTP + OAuth | `mcp_servers/dreamos_control_plane_http_server.py` |
| OAuth scopes | `runtime/config/dreamos_oauth_scopes.yaml` (`dreamos-chatgpt-connector`) |
| Connector module | `src/agent_tools/discord_architect_connector/` |
| Channel allowlist SSOT | `D:\DreamVault\runtime\config\discord_router_channels.json` → `connector_allowlist` |
| D2A / !message | DreamVault `d2a_ingress_adapter` + message bus (unchanged) |
| Agent dispatch | MCP `dispatch_agent_message` → `send_agent_command` / Thea A2A bridge |

**DreamRelay:** not present in fleet roots — do not invent a second bus.

## Tools (connector)

| Tool | Scope | Default |
|------|-------|---------|
| `read_channels` | dreamos.read | config inventory |
| `read_messages` | dreamos.read | allowlisted only; `live=false` |
| `send_message_allowlisted` | dreamos.write | dry_run; smoke_test only |
| `dispatch_agent_message` | dreamos.write | alias → A2A bus |
| `get_agent_status` | dreamos.read | alias → fleet_status |
| `get_task_receipt` | dreamos.read | correlation_id receipts |
| `connector_security_contract` | dreamos.read | policy dump |

## Security defaults

1. Bot tokens / webhooks **server-side only** (`DISCORD_BOT_TOKEN` in host env / secrets files).
2. Send default **dry_run=true**; live requires `human_approved=true` **and** `DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1`.
3. Only routes in `connector_allowlist` (default: `smoke_test` / `#smoke-sessionz`).
4. Destructive Discord admin and PyAutoGUI live dispatch from ChatGPT remain **out of scope**.
5. Preserve `!message` routing, durable bus IDs, acks, inbox copies, timeouts, audit receipts.

## ChatGPT connection steps (exact)

1. Host tunnel/MCP with `dreamos_control_plane_http_server.py` (see readiness report `reports/dreamos_control_plane_mcp_readiness_20260826.json`).
2. Register ChatGPT connector client `dreamos-chatgpt-connector` with scopes `dreamos.read` (start) then `dreamos.write` only when needed.
3. Confirm OAuth redirect / tunnel URL from operator secrets (never paste tokens into ChatGPT).
4. In ChatGPT, enable the Dream.OS MCP connector and call `connector_security_contract` then `read_channels`.
5. Smoke: `send_message_allowlisted` with `dry_run=true` to `route_key=smoke_test`.
6. Live smoke (operator AUTHORIZE only): set `DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1`, call with `dry_run=false` + `human_approved=true`.

## Deployment contract

| Gate | Rule |
|------|------|
| PR1 | Code + unit tests only; no VPS fleet change |
| Live smoke | Operator AUTHORIZE + env gate |
| Broaden allowlist | Explicit human approval |
| Guild admin | Forbidden without separate AUTHORIZE lane |

## Verify

```powershell
cd D:\agent-tools
python -m pytest tests/test_discord_architect_connector_001.py tests/test_dreamos_control_plane_server_001.py -q
```
