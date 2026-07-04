# Swarm Commander — VPS headless deployment

Deploy the **slim Discord Commander** (`src/agent_tools/discord_commander/`) as the first always-on Dream.OS service on Ubuntu 24.04.

- **No GUI** — PyAutoGUI / Agent_Cellphone lanes are adapter-only (`queue_bridge.py`), not baseline deps
- **No raw repo imports** — clone `Agent-Tools` only
- **Outbound default** — `!message` routes through `outbound_router` → per-agent webhooks
- **Secrets** — live values only in `/opt/dreamos/secrets/swarm-commander.env` (never committed)

## Minimal runtime surface

| Path | Purpose |
|------|---------|
| `src/agent_tools/discord_commander/` | Slim bot, messaging, outbound router, CLI |
| `deploy/vps/swarm-commander/` | VPS install, systemd, healthcheck |
| `tests/test_discord_commander_toolbelt.py` | Contract tests |
| `pyproject.toml` | Optional extras: `discord`, `full` (PyAutoGUI) |

Headless startup loads **no PyAutoGUI**. `send_agent_message()` falls through to webhook router when no transport adapter is bound.

## Prerequisites

- Ubuntu 24.04, Python 3.12+, Docker optional (not required for Commander)
- Discord bot with **Message Content Intent** enabled (Discord Developer Portal → Bot → Privileged Gateway Intents)
- Bitwarden / operator secrets (see below)

### Required Bitwarden secrets

| Secret | Env var |
|--------|---------|
| Bot token | `DISCORD_BOT_TOKEN` |
| Default webhook (fallback) | `DISCORD_WEBHOOK_URL` |
| Per-agent webhooks | `DISCORD_WEBHOOK_AGENT_1` … `DISCORD_WEBHOOK_AGENT_8` |
| Guild ID (slash sync + bot validation) | `DISCORD_GUILD_ID` |

Template: `deploy/vps/swarm-commander/.env.example` (placeholders only).

Optional: `DREAMVAULT_ROOT=/opt/dreamos/DreamVault` for `!swarm-status` / `/fleet-audit`.

## VPS install

```bash
sudo useradd -r -m -s /bin/bash dreamos || true
sudo mkdir -p /opt/dreamos/repos /opt/dreamos/secrets
sudo chown -R dreamos:dreamos /opt/dreamos

sudo -u dreamos git clone https://github.com/Victor-Dixon/Agent-Tools.git /opt/dreamos/repos/agent-tools
cd /opt/dreamos/repos/agent-tools
chmod +x deploy/vps/swarm-commander/scripts/*.sh

# Copy and fill secrets (Bitwarden) — include DISCORD_GUILD_ID
sudo cp deploy/vps/swarm-commander/.env.example /opt/dreamos/secrets/swarm-commander.env
sudo chmod 600 /opt/dreamos/secrets/swarm-commander.env
sudo nano /opt/dreamos/secrets/swarm-commander.env

bash deploy/vps/swarm-commander/scripts/install.sh
```

**Exact install command (from repo root):**

```bash
bash deploy/vps/swarm-commander/scripts/install.sh
```

**Exact healthcheck:**

```bash
bash deploy/vps/swarm-commander/scripts/healthcheck.sh
```

## systemd

```bash
sudo systemctl start swarm-commander
sudo systemctl status swarm-commander
sudo journalctl -u swarm-commander -f --no-pager
```

Unit file: `deploy/vps/swarm-commander/systemd/swarm-commander.service`  
Env file: `/opt/dreamos/secrets/swarm-commander.env`

## Start / stop (manual)

```bash
bash deploy/vps/swarm-commander/scripts/start.sh
bash deploy/vps/swarm-commander/scripts/stop.sh
```

## Test `!message`

1. Start bot (systemd or `start.sh`)
2. In Discord (Message Content Intent enabled):

   ```text
   !message Agent-1 Check your inbox
   ```

3. Agent ID forms accepted: `Agent-1`, `agent-3`, `3`

**Expected failure (no webhook):**

```text
Failed to send message to Agent-1: No webhook configured for Agent-1
```

CLI equivalent (dry-run):

```bash
cd /opt/dreamos/repos/agent-tools
source /opt/dreamos/secrets/swarm-commander.env
export PYTHONPATH=src
.venv/bin/python -m agent_tools.discord_commander post \
  --agent Agent-1 --title Test --message "Check your inbox" --dry-run
```

Without webhooks, outbound dry-run reports `WEBHOOK_MISSING`.

## Local dev tests

```bash
cd agent-tools
python -m venv .venv
.venv/bin/pip install -r deploy/vps/swarm-commander/requirements-headless.txt pytest
.venv/bin/pip install -e ".[discord]" 2>/dev/null || true
PYTHONPATH=src .venv/bin/pytest -q tests/test_discord_commander_toolbelt.py tests/test_vps_swarm_commander_deploy.py
```

## Production notes

- Enable **Message Content Intent** or prefix commands (`!message`) will not receive content
- PyAutoGUI queue processor is **optional** — `python -m agent_tools.discord_commander start-queue` only when Agent_Cellphone adapter is installed
- Do not commit `.env` — only `.env.example` with empty placeholders
