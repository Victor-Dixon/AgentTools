# VPS Deploy Bridge

Guarded internal bridge for Dream.OS agents to request VPS uploads and deployments
without exposing root credentials or unrestricted SSH access.

## Security model

- Agents **never** see the VPS root password
- Agents **never** receive raw private SSH keys
- Agents create signed deploy request JSON artifacts only
- A local, operator-controlled runner validates and executes approved deploys
- Default mode is **dry-run** (planned commands only)
- Production execution requires `DREAMOS_DEPLOY_MODE=execute` **and** `"dry_run": false` in the request
- Every action writes a proof report under `reports/vps_deploy_bridge/<request_id>.json`

## Credential storage

SSH credentials live outside this repository:

- **Bitwarden** stores the VPS SSH private key and root password
- Export key path and connection details into your shell environment before execute mode
- Never commit keys, passwords, or `.env` files with real secrets

## Workflow

1. **Agent** writes a deploy request JSON (see `examples/deploy_request.example.json`)
2. **Operator** runs dry-run to review planned `scp`/`rsync`/`ssh` commands
3. **Operator** sets `"dry_run": false` after approval
4. **Operator** runs execute with environment variables loaded from Bitwarden exports

## Environment variables

Set these in your shell or operator session (not committed):

| Variable | Description |
|----------|-------------|
| `DREAMOS_VPS_HOST` | VPS hostname or IP |
| `DREAMOS_VPS_USER` | SSH user (non-root deploy user recommended) |
| `DREAMOS_VPS_SSH_KEY` | Path to SSH private key file |
| `DREAMOS_VPS_PORT` | SSH port (default `22`) |
| `DREAMOS_DEPLOY_MODE` | `dry_run` (default) or `execute` |

## Approved target prefixes

- `/opt/dreamos/`
- `/var/www/dreamos-sites/`
- `/tmp/dreamos-deploy/`

## Blocked write targets

- `/root/.ssh`, `/etc`, `/usr`, `/bin`, `/sbin`, `/var/lib`, `/home`

## Blocked command patterns

- `rm -rf /`, `mkfs`, `dd if=`, `shutdown`, `reboot`, `userdel`, `passwd`, `curl | sh`, `wget | sh`

## Service restart allowlist

- `swarm-commander`, `dreamos-brain`, `dreamos-dashboard`, `nginx`

## Commands

### Dry-run (default — safe review)

From the AgentTools repo root:

```bash
bash tools/vps_deploy_bridge/scripts/dry_run.sh tools/vps_deploy_bridge/examples/deploy_request.example.json
```

Or directly:

```bash
python tools/vps_deploy_bridge/vps_deploy_bridge.py tools/vps_deploy_bridge/examples/deploy_request.example.json
```

Expected verify line:

```
VERIFY=PASS_VPS_DEPLOY_BRIDGE_DRY_RUN
```

### Execute (operator only, after review)

1. Load credentials from Bitwarden into the environment:

```bash
export DREAMOS_VPS_HOST="your.vps.host"
export DREAMOS_VPS_USER="deploy"
export DREAMOS_VPS_SSH_KEY="$HOME/.ssh/dreamos_vps_deploy"
export DREAMOS_VPS_PORT="22"
```

2. Edit the request and set `"dry_run": false`

3. Run execute:

```bash
bash tools/vps_deploy_bridge/scripts/execute.sh path/to/approved_deploy_request.json
```

Expected verify line:

```
VERIFY=PASS_VPS_DEPLOY_BRIDGE_EXECUTED
```

## Deploy request fields

**Required:** `request_id`, `agent_id`, `repo`, `source_path`, `target_path`, `action`, `reason`, `created_at`, `dry_run`

**Actions:** `upload_file`, `upload_dir`, `run_command`, `restart_service`, `healthcheck`

**Optional:** `service_name`, `command`, `expected_verify`, `max_bytes`, `allowed_extensions`, `checksum_sha256`

Schema: `tools/vps_deploy_bridge/deploy_request.schema.json`

## Reports

Each run writes `reports/vps_deploy_bridge/<request_id>.json` with validation results,
planned commands, execution status, and verify line.

## Using with the VPS

Typical Dream.OS VPS layout:

- `/opt/dreamos/` — services (swarm-commander, dreamos-brain, configs)
- `/var/www/dreamos-sites/` — static sites
- `/tmp/dreamos-deploy/` — staging uploads before promotion

Agents propose changes; operators dry-run, review the report, then execute.
This keeps root credentials and unrestricted SSH out of agent context.
