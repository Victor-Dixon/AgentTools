# Discord Architect Connector — ChatGPT MCP path

**Status:** v0.1 scaffold (read-only + allowlisted smoke dry-run).  
**No live deployment / permission escalation without operator AUTHORIZE.**

## Reuse (do not fork)

| Layer | Path |
|-------|------|
| MCP stdio | `mcp_servers/dreamos_control_plane_server.py` |
| Connector module | `src/agent_tools/discord_architect_connector/` |
| Channel allowlist SSOT | `$DREAMVAULT_ROOT/runtime/config/discord_router_channels.json` → `connector_allowlist` (override with `DISCORD_ROUTER_CONFIG`) |
| D2A / !message | DreamVault `d2a_ingress_adapter` + message bus (unchanged) |
| Agent dispatch | MCP `dispatch_agent_message` → `send_agent_command` / Thea A2A bridge |

HTTP/OAuth reachability, live guild authorization, and VPS hosting are **Unknown** until independently evidenced. This lane does not invent a second bus.

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
2. Send default **dry_run=true**. A client-supplied `human_approved=true` is **not** trusted authorization.
3. Live send requires server-side `DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1` (default **off**).
4. Only routes in `connector_allowlist` (default: `smoke_test`).
5. Destructive Discord admin and PyAutoGUI live dispatch from ChatGPT remain **out of scope**.
6. Preserve `!message` routing, durable bus IDs, acks, inbox copies, timeouts, audit receipts.

## ChatGPT connection steps (exact)

1. Host the stdio MCP server `mcp_servers/dreamos_control_plane_server.py`. HTTP/OAuth tunnel status is **Unknown** until evidenced.
2. Confirm OAuth redirect / tunnel URL from operator secrets (never paste tokens into ChatGPT).
3. Call `connector_security_contract` then `read_channels`.
4. Smoke: `send_message_allowlisted` with `dry_run=true` to `route_key=smoke_test`.
5. Live smoke remains **blocked** unless an operator sets `DISCORD_CONNECTOR_ALLOW_LIVE_SEND=1` on the server.

## Deployment contract

| Gate | Rule |
|------|------|
| PR | Code + unit tests only; no VPS fleet change |
| Live smoke | Operator AUTHORIZE + server-side env gate |
| Broaden allowlist | Explicit human approval |
| Guild admin | Forbidden without separate AUTHORIZE lane |

## Verify

```bash
python -m pytest tests/test_discord_architect_connector_001.py tests/test_dreamos_control_plane_server_001.py tests/compat/test_agenttools_bus_message_adapter_contract.py -q
```
